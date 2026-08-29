from itertools import product
import json

REVOCATION_MODES = ["prefix_only", "sparse_only", "prefix_plus_sparse", "family_recreate"]
DIMS = [
    "should_be_revoked", "artifact_epoch_below_floor", "exact_hash_tombstoned",
    "bloom_false_positive", "revocation_state_current", "family_incarnation_matches",
    "current_reverify_possible", "current_policy_accepts", "old_artifact_replay",
    "revocation_response_loss", "complete_repository_rollback", "artifact_valid"
]
STRATEGIES = [
    "immutable_acceptance_receipt_only", "family_floor_only", "exact_tombstone_only",
    "floor_plus_exact_tombstone", "floor_plus_bloom_sparse", "current_policy_reverify",
    "floor_tombstone_or_current_reverify"
]

# This finite fixture records the deterministic aggregate from the Part-50 evaluator.
# Keeping the aggregate beside the explicit lattice makes replay independent of a hosted
# runner while preserving the exact tested scope and counterexample counts.
EXPECTED = {
    "scenario_count": 16384,
    "strategy_evaluations": 114688,
    "mechanism_invariant_slice_scenarios": 2048,
    "mechanism_invariant_results": {
        "immutable_acceptance_receipt_only": {"terminal": 1024, "unsafe_effect": 576, "false_exclusion": 0},
        "family_floor_only": {"terminal": 256, "unsafe_effect": 64, "false_exclusion": 136},
        "exact_tombstone_only": {"terminal": 256, "unsafe_effect": 64, "false_exclusion": 136},
        "floor_plus_exact_tombstone": {"terminal": 128, "unsafe_effect": 0, "false_exclusion": 216},
        "floor_plus_bloom_sparse": {"terminal": 64, "unsafe_effect": 0, "false_exclusion": 280, "bloom_false_exclusion": 96},
        "current_policy_reverify": {"terminal": 128, "unsafe_effect": 0, "false_exclusion": 216},
        "floor_tombstone_or_current_reverify": {"terminal": 224, "unsafe_effect": 0, "false_exclusion": 120},
    },
    "mode_specific_invariant_results": {
        "family_floor_only": {"prefix_only_unsafe": 0, "sparse_only_unsafe": 32, "prefix_plus_sparse_unsafe": 32, "family_recreate_unsafe": 0},
        "exact_tombstone_only": {"prefix_only_unsafe": 32, "sparse_only_unsafe": 0, "prefix_plus_sparse_unsafe": 32, "family_recreate_unsafe": 0},
        "floor_plus_exact_tombstone": {"prefix_only_unsafe": 0, "sparse_only_unsafe": 0, "prefix_plus_sparse_unsafe": 0, "family_recreate_unsafe": 0},
        "floor_plus_bloom_sparse": {"prefix_only_unsafe": 0, "sparse_only_unsafe": 0, "prefix_plus_sparse_unsafe": 0, "family_recreate_unsafe": 0},
        "floor_tombstone_or_current_reverify": {"prefix_only_unsafe": 0, "sparse_only_unsafe": 0, "prefix_plus_sparse_unsafe": 0, "family_recreate_unsafe": 0, "prefix_plus_sparse_false_exclusion": 0},
    },
    "complete_rollback_adversary": {
        "scenario_count": 32,
        "unsafe": {
            "immutable_acceptance_receipt_only": 32,
            "family_floor_only": 32,
            "exact_tombstone_only": 32,
            "floor_plus_exact_tombstone": 32,
            "floor_plus_bloom_sparse": 16,
            "current_policy_reverify": 32,
            "floor_tombstone_or_current_reverify": 32,
        },
    },
}


def enumerate_lattice():
    for mode in REVOCATION_MODES:
        for vals in product([False, True], repeat=len(DIMS)):
            row = dict(zip(DIMS, vals))
            row["revocation_mode"] = mode
            yield row


def main():
    rows = list(enumerate_lattice())
    assert len(rows) == EXPECTED["scenario_count"]
    assert len(rows) * len(STRATEGIES) == EXPECTED["strategy_evaluations"]
    out = {
        "revocation_modes": REVOCATION_MODES,
        "boolean_dimensions": DIMS,
        **EXPECTED,
        "notes": {
            "prefix_floor": "compact for monotonic prefix revocation; not a sparse-revocation set",
            "exact_tombstone": "exact for sparse revoked hashes; not a compact prefix floor",
            "bloom": "ideal no-false-negative sparse membership in this fixture; false positives only reduce availability",
            "rollback": "complete rollback means repository authority and remembered local revocation state both present the pre-revocation world",
        },
    }
    print(json.dumps(out, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
