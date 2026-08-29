from itertools import product
from collections import Counter
import json

SLOT_AXES = {
    "attempts": [1, 2, 4],
    "crash": [False, True],
    "takeover": [False, True],
    "late_old_effect": [False, True],
    "recreate": [False, True],
    "incarnation_sensitive": [False, True],
    "response_lost": [False, True],
}
SLOT_STRATEGIES = [
    "no_role_slot",
    "role_slot_no_effect_fence",
    "role_slot_epoch_fence",
    "role_slot_reusable_id_reset",
]

def slot_eval(strategy, s):
    o = Counter()
    attempts = s["attempts"]
    takeover = s["crash"] and s["takeover"]
    late = takeover and s["late_old_effect"]
    if strategy == "no_role_slot":
        o["max_admitted"] += attempts
        if attempts > 1:
            o["duplicate_concurrent"] += 1
    elif strategy == "role_slot_no_effect_fence":
        o["max_admitted"] += 1
        o["blocked_overlap"] += max(0, attempts - 1)
        if late:
            o["unsafe_old_effect"] += 1
        if s["response_lost"]:
            o["reconciled"] += 1
    elif strategy == "role_slot_epoch_fence":
        o["max_admitted"] += 1
        o["blocked_overlap"] += max(0, attempts - 1)
        if late and s["recreate"] and not s["incarnation_sensitive"]:
            o["unsafe_old_effect"] += 1
        if takeover:
            o["takeover_epoch"] += 1
        if s["response_lost"]:
            o["reconciled"] += 1
    elif strategy == "role_slot_reusable_id_reset":
        o["max_admitted"] += 1
        o["blocked_overlap"] += max(0, attempts - 1)
        if late and s["recreate"]:
            o["unsafe_old_effect"] += 1
    return o

STARVATION_AXES = {
    "initial_inflight": [0, 1, 4, 10],
    "replacement_rounds": [0, 2, 8, 32],
    "retry_budget": [1, 4, 8, 16, 32],
    "response_lost": [False, True],
}
STARVATION_STRATEGIES = [
    "role_slots_only",
    "role_slots_plus_shared_ticket",
    "global_root_admission",
    "no_admission_control",
]

def starvation_eval(strategy, s):
    o = Counter()
    initial = s["initial_inflight"]
    replacements = s["replacement_rounds"]
    budget = s["retry_budget"]
    if strategy == "role_slots_only":
        conflicts = initial + replacements
        if budget > conflicts:
            o["terminal"] += 1
            o["retries"] += conflicts
            if s["response_lost"]:
                o["reconciled"] += 1
        else:
            o["starved_or_retry_exhausted"] += 1
            o["retries"] += budget
        o["instantaneous_bound"] += initial
    elif strategy == "role_slots_plus_shared_ticket":
        conflicts = initial
        o["deferred_replacements"] += replacements
        if budget > conflicts:
            o["terminal"] += 1
            o["retries"] += conflicts
            if s["response_lost"]:
                o["reconciled"] += 1
        else:
            o["retry_exhausted"] += 1
            o["retries"] += budget
    elif strategy == "global_root_admission":
        o["global_hotspot_touches"] += initial + replacements + 1
        o["deferred_replacements"] += replacements
        o["terminal"] += 1
        if s["response_lost"]:
            o["reconciled"] += 1
    elif strategy == "no_admission_control":
        conflicts = initial + replacements
        if budget > conflicts:
            o["terminal"] += 1
        else:
            o["starved_or_retry_exhausted"] += 1
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
    slot_scenarios, slot_aggregate = aggregate(SLOT_AXES, SLOT_STRATEGIES, slot_eval)
    starvation_scenarios, starvation_aggregate = aggregate(STARVATION_AXES, STARVATION_STRATEGIES, starvation_eval)
    return {
        "role_slot_model": {
            "scenario_count": len(slot_scenarios),
            "strategy_evaluations": len(slot_scenarios) * len(SLOT_STRATEGIES),
            "axes": SLOT_AXES,
            "aggregate": slot_aggregate,
            "incarnation_sensitive_strong_slice": {
                "scenarios": 96,
                "unsafe_old_effect": 0,
                "blocked_overlap_events": 128,
                "takeover_epoch_events": 24,
            },
        },
        "wide_starvation_model": {
            "scenario_count": len(starvation_scenarios),
            "strategy_evaluations": len(starvation_scenarios) * len(STARVATION_STRATEGIES),
            "axes": STARVATION_AXES,
            "aggregate": starvation_aggregate,
        },
        "boundary": {
            "instantaneous_bound": "One incarnation/epoch-fenced slot per role can bound simultaneously admitted operations to one per role only if every authoritative effect is required to validate that slot and each role serializes its local operation queue.",
            "starvation": "A finite instantaneous bound alone does not stop an infinite sequence of replacement operations from preempting a wide branch publication. A persistent shared admission gate or a global per-admission authority is additionally required to stop new arrivals.",
            "current_clean_policy": "This multi_agent role may read/write only own role-local state plus sanitized root/public sources. Other-role slots or a dynamic shared ticket are not currently an admissible CLEAN semantic-input/write surface, so the shared-gate half of the finite-starvation proof is not deployable by this role under current control.",
        },
    }

if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
