#!/usr/bin/env python3
from itertools import product
from collections import Counter, defaultdict
import json

HISTORIES = [
    "NEVER_V4",
    "V4_CONFIRMED_THEN_ROLLBACK",
    "V4_AMBIG_APPLIED_THEN_ROLLBACK",
    "V4_AMBIG_NOT_APPLIED",
]
REF_STATES = ["CURRENT", "FORCE_REWOUND", "DELETE_RECREATE", "DIVERGENT_SIBLING"]
VERSION_SURFACES = ["V4_VISIBLE", "V4_OBJECT_HIDDEN", "V4_LOST"]
LATEST_STATES = ["CURRENT", "STALE", "MISSING"]
SHA_STATES = ["PRESERVED_IN_CURRENT_REPO", "LOST_WITH_ROLLBACK"]
ALT_REFS = ["V4_PINNED", "REWOUND_V3", "MISSING"]
DEDUPE_STATES = ["VALID", "EXPIRED"]
TRANSPORT_STATES = ["AVAILABLE", "RATE_LIMITED"]

POLICIES = [
    "current_pointer_only",
    "same_branch_append_only",
    "same_domain_sha_chain",
    "same_repo_alt_ref",
    "combined_same_repo",
    "same_object_tombstone",
    "fail_closed_without_monotonic_proof",
    "protected_monotonic_floor",
]

def scenario(vals):
    s = dict(zip(
        ["history", "ref_state", "version_surface", "latest_state",
         "sha_state", "alt_ref", "dedupe", "transport"], vals))
    true_floor = 4 if s["history"] in (
        "V4_CONFIRMED_THEN_ROLLBACK",
        "V4_AMBIG_APPLIED_THEN_ROLLBACK",
    ) else 3
    s["true_floor"] = true_floor
    s["main_gen"] = 4 if true_floor == 4 and s["ref_state"] == "CURRENT" else 3
    s["visible_v4"] = true_floor == 4 and s["version_surface"] == "V4_VISIBLE"
    s["known_v4_sha"] = (
        true_floor == 4
        and s["sha_state"] == "PRESERVED_IN_CURRENT_REPO"
        and s["version_surface"] != "V4_LOST"
    )
    s["alt_ref_v4"] = true_floor == 4 and s["alt_ref"] == "V4_PINNED"
    if s["latest_state"] == "MISSING":
        s["latest_gen"] = None
    elif s["latest_state"] == "CURRENT":
        s["latest_gen"] = s["main_gen"]
    else:
        s["latest_gen"] = max(2, s["main_gen"] - 1)
    return s

def observation(s):
    # What a stateless recovery worker can actually observe from current repository state.
    return (
        s["main_gen"],
        s["visible_v4"],
        s["known_v4_sha"],
        s["alt_ref_v4"],
        s["latest_gen"],
        s["dedupe"],
        s["transport"],
    )

def decision(policy, s):
    if s["transport"] == "RATE_LIMITED":
        return "CHECKPOINT"
    if policy == "protected_monotonic_floor":
        return "ACCEPT_G3" if s["true_floor"] <= 3 else "REJECT_G3"
    if policy == "fail_closed_without_monotonic_proof":
        return "REJECT_G3"

    observed = s["main_gen"]
    if policy in ("current_pointer_only", "same_object_tombstone"):
        pass
    elif policy == "same_branch_append_only":
        if s["visible_v4"]:
            observed = 4
    elif policy == "same_domain_sha_chain":
        if s["known_v4_sha"]:
            observed = 4
    elif policy == "same_repo_alt_ref":
        if s["alt_ref_v4"]:
            observed = 4
    elif policy == "combined_same_repo":
        if s["visible_v4"] or s["known_v4_sha"] or s["alt_ref_v4"]:
            observed = 4
    else:
        raise ValueError(policy)
    return "ACCEPT_G3" if observed <= 3 else "REJECT_G3"

def main():
    scenarios = [
        scenario(v) for v in product(
            HISTORIES, REF_STATES, VERSION_SURFACES, LATEST_STATES,
            SHA_STATES, ALT_REFS, DEDUPE_STATES, TRANSPORT_STATES
        )
    ]

    policy_metrics = {}
    for policy in POLICIES:
        c = Counter()
        for s in scenarios:
            d = decision(policy, s)
            c["total"] += 1
            if d == "CHECKPOINT":
                c["checkpoint"] += 1
                continue
            if d == "ACCEPT_G3":
                c["accepted"] += 1
                if s["true_floor"] == 4:
                    c["unsafe_old_accept"] += 1
                    if s["dedupe"] == "EXPIRED":
                        c["duplicate_external_effect"] += 1
                else:
                    c["legit_accept"] += 1
            else:
                c["rejected"] += 1
                if s["true_floor"] == 3:
                    c["false_block"] += 1
                else:
                    c["safe_reject"] += 1
        policy_metrics[policy] = dict(c)

    full_erasure = [
        s for s in scenarios
        if s["transport"] == "AVAILABLE"
        and s["true_floor"] == 4
        and s["main_gen"] == 3
        and not s["visible_v4"]
        and not s["known_v4_sha"]
        and not s["alt_ref_v4"]
    ]

    full_erasure_metrics = {}
    for policy in POLICIES:
        c = Counter()
        for s in full_erasure:
            d = decision(policy, s)
            c[d] += 1
            if d == "ACCEPT_G3":
                c["unsafe"] += 1
        full_erasure_metrics[policy] = dict(c)

    groups = defaultdict(list)
    for s in scenarios:
        groups[observation(s)].append(s)
    mixed_floor_observations = []
    for obs, members in groups.items():
        floors = sorted({m["true_floor"] for m in members})
        if floors == [3, 4]:
            mixed_floor_observations.append({
                "observation": obs,
                "member_count": len(members),
            })

    result = {
        "scenario_count": len(scenarios),
        "available_transport_count": sum(s["transport"] == "AVAILABLE" for s in scenarios),
        "rate_limited_count": sum(s["transport"] == "RATE_LIMITED" for s in scenarios),
        "policy_metrics": policy_metrics,
        "full_same_domain_erasure": {
            "scenario_count": len(full_erasure),
            "observation_class_count": len({observation(s) for s in full_erasure}),
            "policy_metrics": full_erasure_metrics,
        },
        "observational_indistinguishability": {
            "all_observation_classes": len(groups),
            "classes_containing_both_true_floor_3_and_4": len(mixed_floor_observations),
            "members_in_mixed_classes": sum(x["member_count"] for x in mixed_floor_observations),
            "claim": (
                "For any deterministic recovery rule whose inputs are restricted to the current "
                "same-domain observation tuple, histories in the same mixed class force the same "
                "decision. Accepting g3 preserves liveness for true-floor-3 members but is unsafe "
                "for rolled-back true-floor-4 members; rejecting g3 is safe for the latter but "
                "false-blocks the former."
            ),
        },
        "protected_boundary": {
            "minimum_generic_effect": (
                "Provide a monotonic authority/freshness witness outside the rollback domain, "
                "or prevent authority-ref rewind/delete/recreate with protected policy whose "
                "bypass/removal authority is itself outside the worker-controlled rollback domain."
            ),
            "chat_capable_predecessors_complete_in_model": True,
            "classification": "downstream_verification_required",
        },
    }
    print(json.dumps(result, indent=2, sort_keys=True))

if __name__ == "__main__":
    main()
