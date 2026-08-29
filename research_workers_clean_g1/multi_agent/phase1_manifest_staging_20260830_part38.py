from itertools import product
from collections import Counter
import json

AXES = {
    "relation": ["disjoint", "overlap"],
    "authority_event": ["none", "cancel", "supersede"],
    "unrelated_advance": [False, True],
    "response_lost": [False, True],
    "gc_race": [False, True],
    "crash_before_finalize": [False, True],
    "reader_mode": ["manifest", "direct_fixed"],
}
STRATEGIES = [
    "prepared_conflict_domain_manifest",
    "staging_no_prepared_gc_guard",
    "per_task_prepared_manifest",
    "fixed_paths_then_manifest",
    "global_git_ref_ancestry",
    "fail_closed_serial",
]
METRICS = ["terminal", "reader_contract_miss", "pending", "reconciled", "broken_reference", "duplicate_conflict", "unsafe_partial", "unsafe_stale", "extra_conflict", "false_block", "serialized_disjoint"]

def evaluate(strategy, s):
    o = {k: 0 for k in METRICS}
    authority_changed = s["authority_event"] != "none"
    if strategy == "prepared_conflict_domain_manifest":
        if authority_changed or s["crash_before_finalize"]:
            o["pending"] = 1
        else:
            o["terminal"] = 1
            if s["response_lost"]:
                o["reconciled"] = 1
            if s["reader_mode"] == "direct_fixed":
                o["reader_contract_miss"] = 1
    elif strategy == "staging_no_prepared_gc_guard":
        if authority_changed or s["crash_before_finalize"]:
            o["pending"] = 1
        else:
            o["terminal"] = 1
            if s["gc_race"]:
                o["broken_reference"] = 1
            if s["response_lost"]:
                o["reconciled"] = 1
            if s["reader_mode"] == "direct_fixed":
                o["reader_contract_miss"] = 1
    elif strategy == "per_task_prepared_manifest":
        if authority_changed or s["crash_before_finalize"]:
            o["pending"] = 1
        else:
            o["terminal"] = 1
            if s["relation"] == "overlap":
                o["duplicate_conflict"] = 1
            if s["response_lost"]:
                o["reconciled"] = 1
            if s["reader_mode"] == "direct_fixed":
                o["reader_contract_miss"] = 1
    elif strategy == "fixed_paths_then_manifest":
        if authority_changed:
            o["unsafe_stale"] = 1
        if s["crash_before_finalize"]:
            o["unsafe_partial"] = 1
            o["pending"] = 1
        elif authority_changed:
            o["pending"] = 1
        else:
            o["terminal"] = 1
            if s["response_lost"]:
                o["reconciled"] = 1
        if s["reader_mode"] == "direct_fixed":
            o["unsafe_partial"] = 1
    elif strategy == "global_git_ref_ancestry":
        preadvance = authority_changed or s["unrelated_advance"]
        if s["crash_before_finalize"] or preadvance:
            o["pending"] = 1
            if s["unrelated_advance"] and not authority_changed and not s["crash_before_finalize"]:
                o["extra_conflict"] = 1
        else:
            o["terminal"] = 1
            if s["response_lost"]:
                o["reconciled"] = 1
    elif strategy == "fail_closed_serial":
        if authority_changed or s["crash_before_finalize"] or s["response_lost"]:
            o["pending"] = 1
            if s["response_lost"] and not authority_changed and not s["crash_before_finalize"]:
                o["false_block"] = 1
        else:
            o["terminal"] = 1
        if s["relation"] == "disjoint":
            o["serialized_disjoint"] = 1
    return o

def run():
    scenarios = [dict(zip(AXES, vals)) for vals in product(*AXES.values())]
    aggregate = {}
    for strategy in STRATEGIES:
        c = Counter()
        for s in scenarios:
            c.update(evaluate(strategy, s))
        aggregate[strategy] = dict(c)
    return {
        "scenario_count": len(scenarios),
        "strategy_evaluations": len(scenarios) * len(STRATEGIES),
        "axes": AXES,
        "aggregate": aggregate,
        "interpretation": {
            "prepared_manifest": "A PREPARED manifest CAS before staging gives GC a durable live root and fences cancel/takeover with the same current-blob authority. Final APPLIED CAS is response-loss-reconcilable by transition identity.",
            "gc": "Writing stages before any PREPARED/live reference leaves a deletion race; final publication can point at missing stage data.",
            "overlap": "A per-task manifest does not serialize two tasks that overlap the same authoritative effect; the manifest key must be a stable conflict-domain key, not a display/task identity.",
            "reader_contract": "Manifest-gated atomic visibility only applies to readers that dereference the manifest. Direct fixed-path consumers remain a separate parity child.",
            "global_ref": "Branch-ref publication preserves direct-path atomic visibility but conflicts on unrelated branch advances.",
            "scope_limit": "Static conflict-domain mapping is assumed here; dynamic remapping/topology mutation is deferred. Complete same-domain rewind remains unresolved from Part 36."
        }
    }

if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
