#!/usr/bin/env python3
"""Finite synthetic stress test for objective-first recovery archives and conflict-gated parallel fragments."""
from itertools import product
from collections import Counter, defaultdict
import json

OBJECTIVES = ["all_forward", "all_rollback", "atomic_all_or_nothing", "mixed_permitted", "manual_permitted"]
BEHAVIORS = ["F", "R", "M"]
FEAS_MASKS = list(range(8))
CURRENT_MASKS = list(range(8))
COST_ORDERS = [
    ("F", "R", "M"), ("F", "M", "R"), ("R", "F", "M"),
    ("R", "M", "F"), ("M", "F", "R"), ("M", "R", "F")
]
COMPOSABLE = [False, True]
OVERLAP = ["disjoint", "shared"]
RESERVATION = [False, True]
LAT_PROFILES = {
    "parallel_wins": {"F": 6, "R": 7, "M": 8, "FR": 4},
    "mixed_wins": {"F": 6, "R": 7, "M": 2, "FR": 4},
    "forward_wins": {"F": 2, "R": 7, "M": 6, "FR": 4},
}
POLICIES = [
    "scalar_cheapest_only", "objective_first_archive", "early_crosscritique",
    "fragment_parallel_fenced", "neg_parallel_unfenced"
]

def allowed(obj, b):
    if obj == "all_forward": return b == "F"
    if obj == "all_rollback": return b == "R"
    if obj == "atomic_all_or_nothing": return b in ("F", "R")
    return b in ("F", "R", "M")

def bits(mask):
    return {b for i, b in enumerate(BEHAVIORS) if mask & (1 << i)}

def cheapest(candidates, order):
    for b in order:
        if b in candidates: return b
    return None

def eval_behavior(b, obj, feas, current, latency):
    r = Counter()
    if b is None:
        r["blocked"] = 1; return r
    r["chosen"] = 1; r["latency"] = latency[b]
    if b not in feas:
        r["infeasible_selected"] = 1; r["unsafe"] = 1; return r
    if b not in current:
        r["stale_proof_accept"] = 1; r["unsafe"] = 1
    if not allowed(obj, b):
        r["objective_violation"] = 1; r["unsafe"] = 1
    if not r["unsafe"]:
        r["safe_terminal"] = 1; r["behavior_" + b] = 1
    return r

def scalar_only(obj, feas, current, order, lat):
    return eval_behavior(cheapest(feas, order), obj, feas, current, lat)

def objective_first(obj, feas, current, order, lat):
    candidates = feas & current & {b for b in BEHAVIORS if allowed(obj, b)}
    return eval_behavior(cheapest(candidates, order), obj, feas, current, lat)

def early_crosscritique(obj, feas, current, order, lat):
    # Synthetic negative mechanism: collapse to one cheapest feasible proposal before objective/current proof.
    retained = cheapest(feas, order); r = Counter()
    if retained is None:
        r["blocked"] = 1; return r
    r["retained"] = 1; r["latency"] = lat[retained]
    if retained not in current or not allowed(obj, retained):
        r["blocked"] = 1
        valid = feas & current & {b for b in BEHAVIORS if allowed(obj, b)}
        r["valid_objective_lost"] = int(bool(valid - {retained}))
        return r
    r["safe_terminal"] = 1; r["behavior_" + retained] = 1
    return r

def parallel_policy(obj, feas, current, order, lat, composable, overlap, reservation, fenced):
    base = objective_first(obj, feas, current, order, lat)
    if not base["safe_terminal"]:
        return base
    candidate = {"F", "R"} <= (feas & current)
    objective_allows = allowed(obj, "F") and allowed(obj, "R")
    faster = lat["FR"] < base["latency"]
    if candidate and objective_allows and composable and faster:
        if fenced and overlap == "shared" and not reservation:
            base["parallel_denied_conflict"] = 1; return base
        r = Counter()
        r["parallel_used"] = 1; r["latency"] = lat["FR"]; r["behavior_FR_parallel"] = 1
        if not fenced and overlap == "shared" and not reservation:
            r["duplicate_authoritative_effect"] = 1; r["unsafe"] = 1; return r
        r["safe_terminal"] = 1; return r
    return base

def main():
    totals = {p: Counter() for p in POLICIES}; slices = defaultdict(Counter); n = 0
    for obj, fm, cm, order, comp, ov, res, lp in product(
        OBJECTIVES, FEAS_MASKS, CURRENT_MASKS, COST_ORDERS, COMPOSABLE, OVERLAP, RESERVATION, LAT_PROFILES
    ):
        feas, current, lat = bits(fm), bits(cm), LAT_PROFILES[lp]; n += 1
        results = {
            "scalar_cheapest_only": scalar_only(obj, feas, current, order, lat),
            "objective_first_archive": objective_first(obj, feas, current, order, lat),
            "early_crosscritique": early_crosscritique(obj, feas, current, order, lat),
            "fragment_parallel_fenced": parallel_policy(obj, feas, current, order, lat, comp, ov, res, True),
            "neg_parallel_unfenced": parallel_policy(obj, feas, current, order, lat, comp, ov, res, False),
        }
        base = results["objective_first_archive"]
        beneficial = ({"F", "R"} <= (feas & current) and allowed(obj, "F") and allowed(obj, "R") and
                      comp and base["safe_terminal"] and lat["FR"] < base["latency"])
        if beneficial:
            slices["beneficial_parallel_candidate"]["scenarios"] += 1
            if ov == "shared" and not res:
                slices["shared_key_parallel_without_reservation"]["scenarios"] += 1
        if len(feas & current) >= 2:
            slices["multi_current_proposals"]["scenarios"] += 1
        if results["early_crosscritique"]["valid_objective_lost"]:
            slices["early_critique_loses_valid_objective"]["scenarios"] += 1
        for p, r in results.items():
            totals[p]["scenarios"] += 1
            for k, v in r.items(): totals[p][k] += v
            for metric, name in [
                ("safe_terminal", "safe_terminal_scenarios"), ("unsafe", "unsafe_scenarios"),
                ("parallel_used", "parallel_used_scenarios"), ("duplicate_authoritative_effect", "duplicate_effect_scenarios"),
                ("stale_proof_accept", "stale_proof_accept_scenarios"), ("objective_violation", "objective_violation_scenarios"),
                ("valid_objective_lost", "valid_objective_lost_scenarios")
            ]:
                totals[p][name] += int(bool(r[metric]))
            if r["safe_terminal"]: totals[p]["safe_latency_sum"] += r["latency"]
    out = {
        "model": {"scenario_count": n, "equal_weight_synthetic": True, "empirical_rate_claim": False,
                  "objectives": OBJECTIVES, "behaviors": BEHAVIORS, "cost_order_count": len(COST_ORDERS),
                  "latency_profiles": LAT_PROFILES, "effect_key_overlap": OVERLAP, "reservation": RESERVATION,
                  "fragments_composable": COMPOSABLE},
        "policies": {}, "slices": {k: dict(v) for k, v in slices.items()},
        "scope_limits": [
            "Finite synthetic mechanism lattice only; counts are not empirical multi-agent failure rates.",
            "early_crosscritique is a deliberate diversity-collapse negative mechanism, not a claim that critique in general is harmful.",
            "Objective compatibility is an explicit contract; mixed behavior is not substituted for all-forward/all-rollback objectives.",
            "FR parallel composition is allowed only for a modeled composable fragment pair and is beneficial only when its latency profile is strictly faster than the chosen whole proposal.",
            "Shared exclusive effect keys require a reservation/fence before parallel fragments can issue authoritative effects."
        ]
    }
    for p, c in totals.items():
        d = dict(c); d["safe_terminal_coverage"] = c["safe_terminal_scenarios"] / n; d["unsafe_rate"] = c["unsafe_scenarios"] / n
        d["avg_safe_latency"] = c["safe_latency_sum"] / c["safe_terminal_scenarios"] if c["safe_terminal_scenarios"] else None
        out["policies"][p] = d
    print(json.dumps(out, indent=2, sort_keys=True))

if __name__ == "__main__": main()
