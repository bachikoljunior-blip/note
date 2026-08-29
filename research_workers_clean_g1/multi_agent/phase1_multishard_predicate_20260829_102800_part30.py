from itertools import product
from collections import Counter
import json

KINDS = ["TOPOLOGY_ONLY", "INSERT_EXISTING", "INSERT_NEW_AFTER_SPLIT", "SHARD_RECREATE_ABA"]
PHASE = ["BEFORE_FINAL_CHECK", "AFTER_FINAL_CHECK"]
BOOL = [False, True]
SPANS = [1, 2, 3]


def scenarios():
    out = []
    for span, kind, phase, vector_atomic, descriptor_invalidate, incarnation, root_covers, root_visible, cert_complete, registry_complete, takeover, response_loss in product(
        SPANS, KINDS, PHASE, BOOL, BOOL, BOOL, BOOL, BOOL, BOOL, BOOL, BOOL, BOOL
    ):
        out.append({
            "span": span,
            "kind": kind,
            "phase": phase,
            "vector_atomic": vector_atomic,
            "descriptor_invalidate": descriptor_invalidate,
            "incarnation": incarnation,
            "root_covers": root_covers,
            "root_visible": root_visible,
            "cert_complete": cert_complete,
            "registry_complete": registry_complete,
            "takeover": takeover,
            "response_loss": response_loss,
        })
    return out


def conflict(s):
    return s["kind"] != "TOPOLOGY_ONLY"


def evaluate(s, strategy):
    is_conflict = conflict(s)
    duplicate = False

    if strategy == "initial_scan_shards":
        blocked = False
        if is_conflict and s["phase"] == "BEFORE_FINAL_CHECK":
            if s["kind"] == "INSERT_EXISTING":
                blocked = True
            elif s["kind"] == "INSERT_NEW_AFTER_SPLIT":
                blocked = s["descriptor_invalidate"]
            elif s["kind"] == "SHARD_RECREATE_ABA":
                blocked = s["incarnation"]
        activated = not blocked
        duplicate = activated and (s["takeover"] or s["response_loss"])

    elif strategy == "canonical_shard_vector":
        if not is_conflict:
            activated = True
        elif s["phase"] == "BEFORE_FINAL_CHECK":
            blocked = s["kind"] != "SHARD_RECREATE_ABA" or s["incarnation"]
            activated = not blocked
        else:
            if not s["vector_atomic"]:
                activated = True
            elif s["kind"] == "INSERT_EXISTING":
                activated = False
            elif s["kind"] == "INSERT_NEW_AFTER_SPLIT":
                activated = not s["descriptor_invalidate"]
            elif s["kind"] == "SHARD_RECREATE_ABA":
                activated = not s["incarnation"]

    elif strategy == "root_range_generation":
        blocked = s["root_covers"] and s["root_visible"]
        activated = not blocked

    elif strategy == "shard_intent_root_certificate":
        permit = s["root_covers"] and s["root_visible"] and s["cert_complete"]
        activated = permit and not is_conflict

    elif strategy == "serial_predicate_reservation":
        activated = not is_conflict

    elif strategy == "staging_complete_integrator":
        activated = not (is_conflict and s["registry_complete"])

    else:
        raise ValueError(strategy)

    unsafe = is_conflict and activated
    return {
        "unsafe": bool(unsafe),
        "duplicate": bool(duplicate),
        "progress": int(activated),
        "false_exclusion": int((not is_conflict) and not activated),
        "serialized_conflict": int(strategy == "serial_predicate_reservation" and is_conflict),
        "wasted_staging": int(strategy == "staging_complete_integrator" and is_conflict and s["registry_complete"]),
    }


def summarize(rows, strategy):
    c = Counter()
    for s in rows:
        for k, v in evaluate(s, strategy).items():
            c[k] += int(v)
    return dict(c)


def main():
    rows = scenarios()
    strategies = [
        "initial_scan_shards",
        "canonical_shard_vector",
        "root_range_generation",
        "shard_intent_root_certificate",
        "serial_predicate_reservation",
        "staging_complete_integrator",
    ]
    result = {
        "schema_version": 1,
        "scenario_count": len(rows),
        "interpretation": {
            "scope": "Finite physical-shard-membership drift lattice; counts are synthetic mechanism cases, not production failure rates.",
            "safety_definition": "A conflicting insertion or shard incarnation change after a predicate snapshot must not be authorized from a stale physical shard set.",
        },
        "strategies": {st: summarize(rows, st) for st in strategies},
        "slices": {},
    }

    split_new_after = [s for s in rows if s["kind"] == "INSERT_NEW_AFTER_SPLIT" and s["phase"] == "AFTER_FINAL_CHECK" and not s["descriptor_invalidate"]]
    vector_strong = [s for s in rows if conflict(s) and s["phase"] == "AFTER_FINAL_CHECK" and s["vector_atomic"] and s["descriptor_invalidate"] and s["incarnation"]]
    vector_nonatomic = [s for s in rows if conflict(s) and s["phase"] == "AFTER_FINAL_CHECK" and not s["vector_atomic"]]
    root_strong = [s for s in rows if s["root_covers"] and s["root_visible"]]
    root_weak_conflict = [s for s in rows if conflict(s) and (not s["root_covers"] or not s["root_visible"])]
    aba_strong = [s for s in rows if s["kind"] == "SHARD_RECREATE_ABA" and s["phase"] == "AFTER_FINAL_CHECK" and s["vector_atomic"] and s["incarnation"]]
    aba_weak = [s for s in rows if s["kind"] == "SHARD_RECREATE_ABA" and s["phase"] == "AFTER_FINAL_CHECK" and s["vector_atomic"] and not s["incarnation"]]
    staging_complete = [s for s in rows if s["registry_complete"]]
    staging_incomplete_conflict = [s for s in rows if conflict(s) and not s["registry_complete"]]

    result["slices"] = {
        "new_shard_after_final_check_without_parent_descriptor_invalidation": {
            "count": len(split_new_after),
            "initial_scan_unsafe": summarize(split_new_after, "initial_scan_shards")["unsafe"],
            "canonical_vector_unsafe": summarize(split_new_after, "canonical_shard_vector")["unsafe"],
        },
        "atomic_descriptor_vector_strong_slice": {"count": len(vector_strong), "unsafe": summarize(vector_strong, "canonical_shard_vector")["unsafe"]},
        "non_atomic_vector_after_final_check": {"count": len(vector_nonatomic), "unsafe": summarize(vector_nonatomic, "canonical_shard_vector")["unsafe"]},
        "root_generation_authoritative_slice": {"count": len(root_strong), "unsafe": summarize(root_strong, "root_range_generation")["unsafe"], "false_exclusion": summarize(root_strong, "root_range_generation")["false_exclusion"]},
        "root_generation_missing_or_lagged_conflict": {"count": len(root_weak_conflict), "unsafe": summarize(root_weak_conflict, "root_range_generation")["unsafe"]},
        "shard_recreate_atomic_vector_incarnation_sensitive": {"count": len(aba_strong), "unsafe": summarize(aba_strong, "canonical_shard_vector")["unsafe"]},
        "shard_recreate_atomic_vector_without_incarnation": {"count": len(aba_weak), "unsafe": summarize(aba_weak, "canonical_shard_vector")["unsafe"]},
        "staging_complete_registry": {"count": len(staging_complete), "unsafe": summarize(staging_complete, "staging_complete_integrator")["unsafe"], "wasted_staging": summarize(staging_complete, "staging_complete_integrator")["wasted_staging"]},
        "staging_incomplete_registry_conflict": {"count": len(staging_incomplete_conflict), "unsafe": summarize(staging_incomplete_conflict, "staging_complete_integrator")["unsafe"]},
    }

    assert result["slices"]["new_shard_after_final_check_without_parent_descriptor_invalidation"]["canonical_vector_unsafe"] == len(split_new_after)
    assert result["slices"]["atomic_descriptor_vector_strong_slice"]["unsafe"] == 0
    assert result["slices"]["non_atomic_vector_after_final_check"]["unsafe"] == len(vector_nonatomic)
    assert result["slices"]["root_generation_authoritative_slice"]["unsafe"] == 0
    assert result["slices"]["root_generation_missing_or_lagged_conflict"]["unsafe"] == len(root_weak_conflict)
    assert result["slices"]["shard_recreate_atomic_vector_incarnation_sensitive"]["unsafe"] == 0
    assert result["strategies"]["serial_predicate_reservation"]["unsafe"] == 0
    assert result["slices"]["staging_complete_registry"]["unsafe"] == 0

    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
