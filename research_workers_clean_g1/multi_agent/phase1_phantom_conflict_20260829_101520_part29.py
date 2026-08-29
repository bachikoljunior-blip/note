from itertools import product
from collections import Counter
import json

INSERT = ["NEW_KEY", "DELETE_RECREATE"]
PATH = ["INDEXED", "BYPASS"]
BOOL = [False, True]


def scenarios():
    out = []
    for ins, overlap, path, global_visible, range_visible, shard_complete, append_visible, append_incarnation, known_incarnation, registry_complete, takeover, response_loss, ambiguous_commit in product(
        INSERT, BOOL, PATH, BOOL, BOOL, BOOL, BOOL, BOOL, BOOL, BOOL, BOOL, BOOL, BOOL
    ):
        out.append({
            "insertion": ins,
            "overlap": overlap,
            "path": path,
            "global_visible": global_visible,
            "range_visible": range_visible,
            "shard_complete": shard_complete,
            "append_visible": append_visible,
            "append_incarnation": append_incarnation,
            "known_incarnation": known_incarnation,
            "registry_complete": registry_complete,
            "takeover": takeover,
            "response_loss": response_loss,
            "ambiguous_commit": ambiguous_commit,
        })
    return out


def invalidated(s, strategy):
    conflict = s["overlap"]
    if strategy == "per_known_key_cas":
        return conflict and s["insertion"] == "DELETE_RECREATE" and s["known_incarnation"]
    if strategy == "global_coupling_epoch":
        return s["path"] == "INDEXED" and s["global_visible"]
    if strategy == "range_index_epoch":
        return conflict and s["path"] == "INDEXED" and s["range_visible"] and s["shard_complete"]
    if strategy == "append_conflict_generation":
        covered = s["path"] == "INDEXED" and s["append_visible"]
        if s["insertion"] == "DELETE_RECREATE":
            covered = covered and s["append_incarnation"]
        return covered
    if strategy == "serial_predicate_reservation":
        return conflict
    if strategy == "staging_fenced_integrator":
        return conflict and s["registry_complete"]
    raise ValueError(strategy)


def evaluate(s, strategy):
    conflict = s["overlap"]
    inv = invalidated(s, strategy)
    activated = not inv
    unsafe = conflict and activated
    duplicate = False
    if activated and strategy == "per_known_key_cas":
        duplicate = s["takeover"] or s["response_loss"] or s["ambiguous_commit"]
    return {
        "unsafe": bool(unsafe),
        "duplicate": bool(duplicate),
        "progress": int(activated),
        "false_exclusion": int(inv and not conflict),
        "wasted_staging": int(strategy == "staging_fenced_integrator" and inv),
        "serialized_conflict": int(strategy == "serial_predicate_reservation" and conflict),
    }


def summarize(rows, strategy):
    c = Counter()
    for s in rows:
        r = evaluate(s, strategy)
        for k, v in r.items():
            c[k] += int(v)
    return dict(c)


def main():
    rows = scenarios()
    strategies = [
        "per_known_key_cas",
        "global_coupling_epoch",
        "range_index_epoch",
        "append_conflict_generation",
        "serial_predicate_reservation",
        "staging_fenced_integrator",
    ]
    result = {
        "schema_version": 1,
        "scenario_count": len(rows),
        "interpretation": {
            "scope": "Finite two-insertion-mode synthetic phantom-conflict lattice; counts are not production failure rates.",
            "safety_definition": "A new overlapping effect key must not gain conflicting authority after a claimant validated a snapshot that omitted it.",
        },
        "strategies": {st: summarize(rows, st) for st in strategies},
        "slices": {},
    }

    phantom_new = [s for s in rows if s["insertion"] == "NEW_KEY" and s["overlap"]]
    recreate_known_strong = [s for s in rows if s["insertion"] == "DELETE_RECREATE" and s["overlap"] and s["known_incarnation"]]
    global_strong = [s for s in rows if s["path"] == "INDEXED" and s["global_visible"]]
    global_bypass = [s for s in rows if s["path"] == "BYPASS"]
    range_strong = [s for s in rows if s["overlap"] and s["path"] == "INDEXED" and s["range_visible"] and s["shard_complete"]]
    range_lag = [s for s in rows if s["overlap"] and s["path"] == "INDEXED" and (not s["range_visible"] or not s["shard_complete"])]
    append_strong = [s for s in rows if s["path"] == "INDEXED" and s["append_visible"] and (s["insertion"] == "NEW_KEY" or s["append_incarnation"])]
    append_aba = [s for s in rows if s["insertion"] == "DELETE_RECREATE" and s["overlap"] and s["path"] == "INDEXED" and s["append_visible"] and not s["append_incarnation"]]
    staging_complete = [s for s in rows if s["registry_complete"]]
    staging_incomplete_conflict = [s for s in rows if s["overlap"] and not s["registry_complete"]]
    nonoverlap_indexed_visible = [s for s in rows if not s["overlap"] and s["path"] == "INDEXED" and s["global_visible"]]

    result["slices"] = {
        "new_key_phantom_vs_known_key_cas": {"count": len(phantom_new), "unsafe": summarize(phantom_new, "per_known_key_cas")["unsafe"], "duplicate": summarize(phantom_new, "per_known_key_cas")["duplicate"]},
        "delete_recreate_incarnation_sensitive_known_key": {"count": len(recreate_known_strong), "unsafe": summarize(recreate_known_strong, "per_known_key_cas")["unsafe"]},
        "global_epoch_authoritative_indexed_slice": {"count": len(global_strong), "unsafe": summarize(global_strong, "global_coupling_epoch")["unsafe"], "false_exclusion": summarize(global_strong, "global_coupling_epoch")["false_exclusion"]},
        "global_epoch_bypass_slice": {"count": len(global_bypass), "unsafe": summarize(global_bypass, "global_coupling_epoch")["unsafe"]},
        "range_epoch_complete_slice": {"count": len(range_strong), "unsafe": summarize(range_strong, "range_index_epoch")["unsafe"]},
        "range_epoch_lag_or_partial_shard": {"count": len(range_lag), "unsafe": summarize(range_lag, "range_index_epoch")["unsafe"]},
        "append_generation_complete_slice": {"count": len(append_strong), "unsafe": summarize(append_strong, "append_conflict_generation")["unsafe"], "false_exclusion": summarize(append_strong, "append_conflict_generation")["false_exclusion"]},
        "append_generation_recreate_without_incarnation": {"count": len(append_aba), "unsafe": summarize(append_aba, "append_conflict_generation")["unsafe"]},
        "staging_complete_registry": {"count": len(staging_complete), "unsafe": summarize(staging_complete, "staging_fenced_integrator")["unsafe"], "wasted_staging": summarize(staging_complete, "staging_fenced_integrator")["wasted_staging"]},
        "staging_incomplete_registry_conflict": {"count": len(staging_incomplete_conflict), "unsafe": summarize(staging_incomplete_conflict, "staging_fenced_integrator")["unsafe"]},
        "nonoverlap_global_false_exclusion": {"count": len(nonoverlap_indexed_visible), "global_false_exclusion": summarize(nonoverlap_indexed_visible, "global_coupling_epoch")["false_exclusion"], "range_false_exclusion": summarize(nonoverlap_indexed_visible, "range_index_epoch")["false_exclusion"]},
    }

    assert result["slices"]["new_key_phantom_vs_known_key_cas"]["unsafe"] == len(phantom_new)
    assert result["slices"]["delete_recreate_incarnation_sensitive_known_key"]["unsafe"] == 0
    assert result["slices"]["global_epoch_authoritative_indexed_slice"]["unsafe"] == 0
    assert result["slices"]["range_epoch_complete_slice"]["unsafe"] == 0
    assert result["slices"]["range_epoch_lag_or_partial_shard"]["unsafe"] == len(range_lag)
    assert result["strategies"]["serial_predicate_reservation"]["unsafe"] == 0
    assert result["slices"]["staging_complete_registry"]["unsafe"] == 0

    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
