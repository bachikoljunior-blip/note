#!/usr/bin/env python3
"""Finite rollback-domain witness lattice for Phase-1 multi_agent Part 51.

All enumerated scenarios are worlds in which a later authority state advanced/revoked
an old artifact, then some subset of repository/local witnesses was rewound or lost.
The model asks whether each candidate blocks the revoked old artifact.

This is a mechanism lattice, not a production failure-rate estimate.
"""
from itertools import product
import json

DIMS = [
    "main_rewound",
    "receipt_ref_rewound",
    "secondary_ref_rewound",
    "role_memory_lost",
    "prompt_has_monotonic_floor",
    "later_object_present",
    "independent_ref_domain",
    "external_history_attestation",
    "current_protection_strict",
    "authority_name_reused",
]

STRATEGIES = [
    "current_main_only",
    "same_repo_receipt_chain",
    "known_sha_object_probe",
    "multi_ref_same_repo",
    "independent_ref_witness",
    "prompt_monotonic_floor",
    "current_branch_protection_fact",
    "external_history_attestation_oracle",
    "fail_closed_no_witness",
]

def blocks_revoked(strategy, x):
    if strategy == "current_main_only":
        return not x["main_rewound"]
    if strategy == "same_repo_receipt_chain":
        return not x["receipt_ref_rewound"]
    if strategy == "known_sha_object_probe":
        # An unreachable object is useful only if its later SHA survives somewhere the
        # worker can name. Object existence by itself is not an enumerable witness here.
        return (not x["role_memory_lost"]) and x["later_object_present"]
    if strategy == "multi_ref_same_repo":
        return (not x["main_rewound"]) or (not x["secondary_ref_rewound"])
    if strategy == "independent_ref_witness":
        return x["independent_ref_domain"] and (not x["secondary_ref_rewound"])
    if strategy == "prompt_monotonic_floor":
        return x["prompt_has_monotonic_floor"]
    if strategy == "current_branch_protection_fact":
        # A current protection setting contains no historical head/version floor.
        # It cannot distinguish "never advanced" from "advanced, rule bypassed/changed,
        # rewound, then rule restored".
        return False
    if strategy == "external_history_attestation_oracle":
        return x["external_history_attestation"]
    if strategy == "fail_closed_no_witness":
        return True
    raise KeyError(strategy)

def main():
    scenarios = [dict(zip(DIMS, bits)) for bits in product([False, True], repeat=len(DIMS))]
    summary = {}
    for strategy in STRATEGIES:
        blocked = sum(blocks_revoked(strategy, x) for x in scenarios)
        summary[strategy] = {
            "scenario_count": len(scenarios),
            "blocks_revoked": blocked,
            "unsafe_old_acceptance": len(scenarios) - blocked,
        }

    hard = [
        x for x in scenarios
        if x["main_rewound"]
        and x["receipt_ref_rewound"]
        and x["secondary_ref_rewound"]
        and x["role_memory_lost"]
        and not x["prompt_has_monotonic_floor"]
        and not x["external_history_attestation"]
    ]
    hard_summary = {}
    for strategy in STRATEGIES:
        blocked = sum(blocks_revoked(strategy, x) for x in hard)
        hard_summary[strategy] = {
            "scenario_count": len(hard),
            "blocks_revoked": blocked,
            "unsafe_old_acceptance": len(hard) - blocked,
        }

    out = {
        "schema_version": 1,
        "scope": "advanced_then_revoked world with rollback/loss witness combinations",
        "scenario_count": len(scenarios),
        "strategy_evaluations": len(scenarios) * len(STRATEGIES),
        "dimensions": DIMS,
        "summary": summary,
        "hard_indistinguishable_slice_definition": {
            "main_rewound": True,
            "receipt_ref_rewound": True,
            "secondary_ref_rewound": True,
            "role_memory_lost": True,
            "prompt_has_monotonic_floor": False,
            "external_history_attestation": False,
            "free_dimensions": [
                "later_object_present",
                "independent_ref_domain",
                "current_protection_strict",
                "authority_name_reused",
            ],
        },
        "hard_indistinguishable_slice": hard_summary,
        "clean_acceptance_note": (
            "external_history_attestation_oracle is an oracle baseline only, not an accepted "
            "Phase-1 dependency; fail_closed_no_witness is the only strategy safe in the hard "
            "slice without a surviving witness, but it sacrifices availability."
        ),
    }
    print(json.dumps(out, indent=2, sort_keys=True))

if __name__ == "__main__":
    main()
