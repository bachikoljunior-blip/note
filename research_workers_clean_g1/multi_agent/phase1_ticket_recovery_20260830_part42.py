from itertools import product
from collections import Counter
import json

RECOVERY_AXES = {
    "declared_bound": [None, 4, 10],
    "actual_inflight": [0, 2, 4, 10, 20],
    "retry_budget": [4, 8, 16, 32],
    "interruptions": [0, 1, 2, 4],
    "recovery_budget": [0, 1, 2, 4],
    "late_old_owner": [False, True],
    "response_lost": [False, True],
}
RECOVERY_STRATEGIES = [
    "wallclock_auto_release",
    "epoch_recovery_no_declared_bound",
    "epoch_recovery_declared_bound",
    "global_root_every_admission",
    "permanent_failclosed_ticket",
]

def recovery_eval(strategy, s):
    o = Counter()
    interruptions = s["interruptions"]
    recovery_budget = s["recovery_budget"]
    actual = s["actual_inflight"]
    retry_budget = s["retry_budget"]
    bound = s["declared_bound"]

    if strategy == "wallclock_auto_release":
        if interruptions > 0:
            o["local_auto_unblock"] += 1
            if s["late_old_owner"]:
                o["unsafe_old_owner"] += 1
        if interruptions == 0 and retry_budget > actual:
            o["terminal"] += 1
            if s["response_lost"]:
                o["reconciled"] += 1
        else:
            o["pending_or_ambiguous"] += 1

    elif strategy == "epoch_recovery_no_declared_bound":
        if recovery_budget >= interruptions and retry_budget > actual + interruptions:
            o["terminal"] += 1
            if s["response_lost"]:
                o["reconciled"] += 1
        else:
            o["pending"] += 1
        o["finite_starvation_bound_unproven"] += 1

    elif strategy == "epoch_recovery_declared_bound":
        if bound is None:
            o["no_bound_contract"] += 1
            o["pending"] += 1
        elif actual > bound:
            o["bound_violated"] += 1
            o["pending"] += 1
        elif recovery_budget < interruptions:
            o["recovery_budget_exhausted"] += 1
            o["pending"] += 1
        elif retry_budget <= actual + interruptions:
            o["retry_budget_exhausted"] += 1
            o["pending"] += 1
        else:
            o["terminal"] += 1
            o["finite_starvation_bound_proven"] += 1
            if interruptions > 0:
                o["recovery_epoch_transitions"] += interruptions
            if s["response_lost"]:
                o["reconciled"] += 1

    elif strategy == "global_root_every_admission":
        o["global_hotspot_touches"] += actual + 1
        if recovery_budget >= interruptions:
            o["terminal"] += 1
            if interruptions > 0:
                o["recovery_epoch_transitions"] += interruptions
            if s["response_lost"]:
                o["reconciled"] += 1
        else:
            o["pending"] += 1

    elif strategy == "permanent_failclosed_ticket":
        if interruptions > 0:
            o["indefinite_exclusion"] += 1
            o["pending"] += 1
        elif retry_budget > actual:
            o["terminal"] += 1
        else:
            o["pending"] += 1
    return o

COMPACTION_AXES = {
    "terminal": ["released", "applied"],
    "old_refs_clean": [False, True],
    "retirement_witness": [False, True],
    "stale_restore": [False, True],
    "key_recreate": [False, True],
    "incarnation_sensitive": [False, True],
    "gc_requested": [False, True],
}
COMPACTION_STRATEGIES = [
    "cleanup_only_gc",
    "incarnation_retirement_floor",
    "logical_name_floor",
    "permanent_ticket_tombstone",
]

def compaction_eval(strategy, s):
    o = Counter()
    if strategy == "cleanup_only_gc":
        if s["gc_requested"] and s["old_refs_clean"]:
            o["gc_completed"] += 1
            if s["stale_restore"]:
                o["unsafe_restore"] += 1
        elif s["gc_requested"]:
            o["gc_blocked"] += 1
    elif strategy == "incarnation_retirement_floor":
        if s["gc_requested"] and s["retirement_witness"] and s["incarnation_sensitive"]:
            o["gc_completed"] += 1
        elif s["gc_requested"]:
            o["gc_blocked"] += 1
        if s["key_recreate"] and not s["incarnation_sensitive"] and s["retirement_witness"]:
            o["false_block_if_name_floor_used"] += 1
    elif strategy == "logical_name_floor":
        if s["gc_requested"] and s["retirement_witness"]:
            o["gc_completed"] += 1
            if s["key_recreate"]:
                o["false_block_new_incarnation"] += 1
        elif s["gc_requested"]:
            o["gc_blocked"] += 1
    elif strategy == "permanent_ticket_tombstone":
        if s["gc_requested"]:
            o["gc_blocked"] += 1
        o["retained_tombstone"] += 1
    return o

def aggregate(axes, strategies, evaluator):
    scenarios = [dict(zip(axes, values)) for values in product(*axes.values())]
    out = {}
    for strategy in strategies:
        c = Counter()
        for scenario in scenarios:
            c.update(evaluator(strategy, scenario))
        out[strategy] = dict(c)
    return scenarios, out

def run():
    recovery_scenarios, recovery_aggregate = aggregate(RECOVERY_AXES, RECOVERY_STRATEGIES, recovery_eval)
    compaction_scenarios, compaction_aggregate = aggregate(COMPACTION_AXES, COMPACTION_STRATEGIES, compaction_eval)
    return {
        "recovery_model": {
            "scenario_count": len(recovery_scenarios),
            "strategy_evaluations": len(recovery_scenarios) * len(RECOVERY_STRATEGIES),
            "axes": RECOVERY_AXES,
            "aggregate": recovery_aggregate,
            "key_slices": {
                "wallclock_expired_late_old_owner": {"scenarios": 1440, "unsafe_old_owner": 1440},
                "declared_bound_10_actual_at_most_10": {"scenarios": 1024, "terminal_with_proven_finite_bound": 500, "pending_due_budget_or_recovery": 524},
            }
        },
        "ticket_compaction_model": {
            "scenario_count": len(compaction_scenarios),
            "strategy_evaluations": len(compaction_scenarios) * len(COMPACTION_STRATEGIES),
            "axes": COMPACTION_AXES,
            "aggregate": compaction_aggregate,
        },
        "scope": "Declared max_inflight is an explicit protocol contract, not inferred from the number of configured roles. Complete same-domain rewind remains excluded; retirement floors are scoped to incarnation-sensitive ticket/conflict-domain identities."
    }

if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
