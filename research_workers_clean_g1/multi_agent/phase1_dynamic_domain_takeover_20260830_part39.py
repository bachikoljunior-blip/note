from itertools import product
from collections import Counter
import json

REMAP_AXES = {
    "relation": ["disjoint", "overlap"],
    "mapping_event": ["none", "merge", "split", "effect_drift"],
    "event_timing": ["before_prepare", "after_prepare_before_finalize"],
    "concurrent_new_prepare": [False, True],
    "prepared_old": [False, True],
    "unrelated_domain_activity": [False, True],
}
REMAP_STRATEGIES = [
    "stale_local_manifest",
    "separate_topology_epoch_check",
    "drain_then_remap_no_atomic_gate",
    "stable_superset_domain",
    "global_root_publication",
    "global_git_ref_publication",
]

def remap_eval(strategy, s):
    o = Counter()
    remap = s["mapping_event"] != "none"
    after = remap and s["event_timing"] == "after_prepare_before_finalize"
    overlap = s["relation"] == "overlap" or s["mapping_event"] in ("merge", "effect_drift")
    if strategy == "stale_local_manifest":
        if after and s["prepared_old"] and overlap:
            o["unsafe_stale"] += 1
        if remap and s["concurrent_new_prepare"] and overlap:
            o["duplicate_overlap"] += 1
        o["local_publication"] += 1
    elif strategy == "separate_topology_epoch_check":
        # The topology read is separate from the final local-manifest CAS.
        if after and s["prepared_old"] and overlap:
            o["unsafe_stale"] += 1
        if remap and s["concurrent_new_prepare"] and overlap:
            o["duplicate_overlap"] += 1
        o["topology_reads"] += 1
        o["local_publication"] += 1
    elif strategy == "drain_then_remap_no_atomic_gate":
        # A new PREPARED transition can enter after the drain scan but before remap.
        if remap and s["concurrent_new_prepare"] and overlap:
            o["unsafe_stale"] += 1
            o["duplicate_overlap"] += 1
        o["remap_scan"] += int(remap)
        o["local_publication"] += 1
    elif strategy == "stable_superset_domain":
        # Conservative static grouping avoids remap races at the price of false exclusion.
        if s["relation"] == "disjoint":
            o["false_exclusion"] += 1
        o["local_publication"] += 1
    elif strategy == "global_root_publication":
        o["global_hotspot_touch"] += 1
        if s["unrelated_domain_activity"]:
            o["extra_conflict"] += 1
    elif strategy == "global_git_ref_publication":
        o["global_hotspot_touch"] += 1
        if s["unrelated_domain_activity"]:
            o["extra_conflict"] += 1
    return o

TAKEOVER_AXES = {
    "lease_expired": [False, True],
    "takeover_attempt": [False, True],
    "late_old_finalizer": [False, True],
    "gc_requested": [False, True],
    "domain_recreate": [False, True],
    "incarnation_sensitive": [False, True],
    "response_lost": [False, True],
}
TAKEOVER_STRATEGIES = [
    "expiry_only_no_epoch",
    "epoch_takeover_gc_after_commit",
    "epoch_takeover_reusable_id_reset",
    "gc_before_epoch_bump",
    "permanent_abandoned_stages",
    "epoch_takeover_fail_closed_no_gc",
]

def takeover_eval(strategy, s):
    o = Counter()
    takeover = s["lease_expired"] and s["takeover_attempt"]
    late = takeover and s["late_old_finalizer"]
    gc = s["gc_requested"]
    recreate = s["domain_recreate"]
    inc = s["incarnation_sensitive"]
    if strategy == "expiry_only_no_epoch":
        if late:
            o["unsafe_old_finalize"] += 1
        if gc and late:
            o["broken_reference"] += 1
        if gc:
            o["gc_completed"] += 1
        elif takeover:
            o["orphan_stage_retained"] += 1
    elif strategy == "epoch_takeover_gc_after_commit":
        # Safe only when domain identity is incarnation-sensitive across recreate.
        if takeover and recreate and (not inc) and late:
            o["unsafe_old_finalize"] += 1
        if gc and takeover:
            o["gc_completed"] += 1
        elif takeover:
            o["orphan_stage_retained"] += 1
        if s["response_lost"] and takeover:
            o["reconciled"] += 1
    elif strategy == "epoch_takeover_reusable_id_reset":
        if takeover and recreate and late:
            o["unsafe_old_finalize"] += 1
        if gc and takeover:
            o["gc_completed"] += 1
        elif takeover:
            o["orphan_stage_retained"] += 1
    elif strategy == "gc_before_epoch_bump":
        if gc and takeover and s["late_old_finalizer"]:
            o["broken_reference"] += 1
        if late:
            o["unsafe_old_finalize"] += 1
        if gc and takeover:
            o["gc_completed"] += 1
    elif strategy == "permanent_abandoned_stages":
        if takeover:
            o["orphan_stage_retained"] += 1
        if takeover and recreate and (not inc) and s["late_old_finalizer"]:
            o["unsafe_old_finalize"] += 1
    elif strategy == "epoch_takeover_fail_closed_no_gc":
        if takeover:
            o["orphan_stage_retained"] += 1
        if recreate and (not inc) and late:
            o["false_block"] += 1
        if s["response_lost"] and takeover:
            o["reconciled"] += 1
    return o

def aggregate(axes, strategies, evaluator):
    scenarios = [dict(zip(axes, vals)) for vals in product(*axes.values())]
    out = {}
    for strategy in strategies:
        c = Counter()
        for scenario in scenarios:
            c.update(evaluator(strategy, scenario))
        out[strategy] = dict(c)
    return scenarios, out

def run():
    remap_scenarios, remap_aggregate = aggregate(REMAP_AXES, REMAP_STRATEGIES, remap_eval)
    takeover_scenarios, takeover_aggregate = aggregate(TAKEOVER_AXES, TAKEOVER_STRATEGIES, takeover_eval)
    return {
        "remap_model": {
            "scenario_count": len(remap_scenarios),
            "strategy_evaluations": len(remap_scenarios) * len(REMAP_STRATEGIES),
            "axes": REMAP_AXES,
            "aggregate": remap_aggregate,
            "key_slices": {
                "stale_local_after_remap_prepared_overlap": 20,
                "separate_topology_check_toctou": 20,
                "drain_scan_new_prepare_gap": 40,
                "stable_superset_false_exclusion": 64,
                "global_root_unrelated_conflicts": 64,
            },
        },
        "takeover_gc_model": {
            "scenario_count": len(takeover_scenarios),
            "strategy_evaluations": len(takeover_scenarios) * len(TAKEOVER_STRATEGIES),
            "axes": TAKEOVER_AXES,
            "aggregate": takeover_aggregate,
            "key_slices": {
                "epoch_incarnation_sensitive": {"scenarios": 64, "unsafe_old_finalize": 0, "broken_reference": 0},
                "epoch_noninc_recreate_late": {"scenarios": 4, "unsafe_old_finalize": 4},
                "expiry_only_takeover_late": {"scenarios": 16, "unsafe_old_finalize": 16},
                "gc_before_epoch_bump_relevant": {"scenarios": 8, "broken_reference": 8, "unsafe_old_finalize": 8},
            },
        },
    }

if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
