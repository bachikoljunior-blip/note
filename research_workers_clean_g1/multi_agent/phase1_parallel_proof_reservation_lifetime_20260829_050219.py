#!/usr/bin/env python3
"""Finite synthetic stress test for proposal proof/version drift and reservation lifetime during two-fragment recovery."""
from itertools import product
from collections import Counter, defaultdict
import json

CHANGE = ["none", "before_reserve", "after_reserve_before_A", "between_A_B"]
EXPIRY = ["never", "before_A", "between_A_B"]
TAKEOVER = ["none", "before_A", "between_A_B"]
REACQUIRE = [False, True]
IRREV_A = [False, True]
LATE_OLD = [False, True]
POLICIES = ["precheck_once", "reserve_then_final_revalidate", "per_fragment_fence", "immutable_stage_current_integrator"]

def current_at(change, time):
    if change == "none": return True
    threshold = {"before_reserve": 1, "after_reserve_before_A": 2, "between_A_B": 3}[change]
    return time < threshold

def reservation_valid(expiry, time):
    if expiry == "never": return True
    threshold = {"before_A": 2, "between_A_B": 3}[expiry]
    return time < threshold

def old_epoch_current(takeover, time):
    if takeover == "none": return True
    threshold = {"before_A": 2, "between_A_B": 3}[takeover]
    return time < threshold

def execute_effect(r, label, time, parent_change, proof_change, expiry, takeover,
                   check_current, check_reservation, check_epoch, allow_reacquire, reacquire, direct_worker=True):
    curr = current_at(parent_change, time) and current_at(proof_change, time)
    resv = reservation_valid(expiry, time); epoch = old_epoch_current(takeover, time)
    if check_current:
        r["checks"] += 1
        if not curr: r["blocked_stale_proof"] += 1; return False
    if check_epoch:
        r["checks"] += 1
        if not epoch: r["blocked_stale_epoch"] += 1; return False
    if check_reservation:
        r["checks"] += 1
        if not resv:
            if allow_reacquire and reacquire and curr:
                r["reacquire"] += 1; r["actions"] += 1; resv = True
            else:
                r["blocked_expired_reservation"] += 1; return False
    r["actions"] += 1; r[label + "_applied"] += 1
    if not curr: r["stale_proposal_effect"] += 1
    if not resv: r["effect_without_reservation"] += 1
    if direct_worker and not epoch: r["stale_worker_effect"] += 1
    return True

def evaluate(policy, parent_change, proof_change, expiry, takeover, reacquire, irrev_a, late_old):
    r = Counter(); curr_reserve = current_at(parent_change, 1.5) and current_at(proof_change, 1.5)
    if policy == "precheck_once":
        r["checks"] += 1
        if not curr_reserve: r["blocked_stale_proof"] += 1; return r
        r["reservation_acquired"] += 1; r["actions"] += 1
        A = execute_effect(r, "A", 2, parent_change, proof_change, expiry, takeover, False, False, False, False, reacquire)
        B = execute_effect(r, "B", 3, parent_change, proof_change, expiry, takeover, False, False, False, False, reacquire)
    elif policy == "reserve_then_final_revalidate":
        if not curr_reserve: r["blocked_stale_proof"] += 1; return r
        r["reservation_acquired"] += 1; r["actions"] += 1; r["checks"] += 1
        if not (current_at(parent_change, 2) and current_at(proof_change, 2)):
            r["blocked_stale_proof"] += 1; r["reservation_leak"] += 1; return r
        if not reservation_valid(expiry, 2):
            r["blocked_expired_reservation"] += 1; r["reservation_leak"] += 1; return r
        A = execute_effect(r, "A", 2, parent_change, proof_change, expiry, takeover, False, False, False, False, reacquire)
        B = execute_effect(r, "B", 3, parent_change, proof_change, expiry, takeover, False, False, False, False, reacquire)
    elif policy == "per_fragment_fence":
        if not curr_reserve: r["blocked_stale_proof"] += 1; return r
        r["reservation_acquired"] += 1; r["actions"] += 1
        A = execute_effect(r, "A", 2, parent_change, proof_change, expiry, takeover, True, True, True, False, reacquire)
        B = execute_effect(r, "B", 3, parent_change, proof_change, expiry, takeover, True, True, True, False, reacquire) if A else False
    elif policy == "immutable_stage_current_integrator":
        r["stage_A"] += 1; r["stage_B"] += 1
        if not curr_reserve:
            if reacquire and current_at(parent_change, 2) and current_at(proof_change, 2):
                r["reservation_acquired"] += 1; r["actions"] += 1
            else:
                r["blocked_stale_proof"] += 1; return r
        else:
            r["reservation_acquired"] += 1; r["actions"] += 1
        A = execute_effect(r, "A", 2, parent_change, proof_change, expiry, "none", True, True, False, True, reacquire, False)
        B = execute_effect(r, "B", 3, parent_change, proof_change, expiry, "none", True, True, False, True, reacquire, False) if A else False
        if late_old and takeover != "none": r["late_old_stage_ignored"] += 1
    else: raise ValueError(policy)
    if late_old and takeover != "none" and policy in ("precheck_once", "reserve_then_final_revalidate"):
        r["late_old_direct_effect"] += 1; r["stale_worker_effect"] += 1
        if r["A_applied"] or r["B_applied"]: r["duplicate_authoritative_effect"] += 1
    if r["A_applied"] and r["B_applied"]: r["candidate_complete"] += 1
    if r["A_applied"] and not r["B_applied"] and irrev_a: r["partial_irreversible_exposure"] += 1
    r["unsafe"] = int(bool(r["stale_proposal_effect"] or r["effect_without_reservation"] or r["stale_worker_effect"] or r["duplicate_authoritative_effect"]))
    if r["candidate_complete"] and not r["unsafe"]: r["safe_complete"] += 1
    return r

def main():
    totals = {p: Counter() for p in POLICIES}; slices = defaultdict(Counter); n = 0
    for pc, qc, ex, to, re, irr, late in product(CHANGE, CHANGE, EXPIRY, TAKEOVER, REACQUIRE, IRREV_A, LATE_OLD):
        n += 1; results = {p: evaluate(p, pc, qc, ex, to, re, irr, late) for p in POLICIES}
        for p, r in results.items():
            totals[p]["scenarios"] += 1
            for k, v in r.items(): totals[p][k] += v
            for metric, name in [
                ("unsafe", "unsafe_scenarios"), ("safe_complete", "safe_complete_scenarios"),
                ("reservation_leak", "reservation_leak_scenarios"), ("partial_irreversible_exposure", "partial_irreversible_scenarios"),
                ("duplicate_authoritative_effect", "duplicate_effect_scenarios"), ("stale_proposal_effect", "stale_proposal_effect_scenarios"),
                ("stale_worker_effect", "stale_worker_effect_scenarios")
            ]: totals[p][name] += int(bool(r[metric]))
        def add_slice(name):
            s = slices[name]; s["scenarios"] += 1
            for p, r in results.items():
                s[p + "_unsafe"] += int(r["unsafe"]); s[p + "_safe_complete"] += int(r["safe_complete"])
                s[p + "_partial_irrev"] += int(r["partial_irreversible_exposure"])
        if pc == "between_A_B" or qc == "between_A_B": add_slice("version_or_proof_changes_between_fragments")
        if ex == "between_A_B": add_slice("reservation_expires_between_fragments")
        if to == "between_A_B": add_slice("integrator_takeover_between_fragments")
        if late and to != "none": add_slice("late_old_fragment_after_takeover")
        if irr and (pc == "between_A_B" or qc == "between_A_B" or ex == "between_A_B"): add_slice("partial_irreversible_risk")
    out = {"model": {"scenario_count": n, "equal_weight_synthetic": True, "empirical_rate_claim": False,
                     "parent_change": CHANGE, "proof_digest_change": CHANGE, "reservation_expiry": EXPIRY,
                     "integrator_takeover": TAKEOVER, "reservation_reacquire": REACQUIRE,
                     "fragment_A_irreversible": IRREV_A, "late_old_fragment": LATE_OLD},
           "policies": {}, "slices": {k: dict(v) for k, v in slices.items()},
           "scope_limits": [
               "Finite synthetic mechanism lattice only; counts are not production failure rates.",
               "A reservation is an exact modeled exclusive-effect authority while valid; expiry removes that authority.",
               "Per-fragment fencing can safely block B after A was validly issued; this can still leave partial irreversible exposure and is not atomic all-or-nothing execution.",
               "Immutable staging prevents stale leaf workers from directly issuing authoritative effects; current integrator publication remains subject to current proof/reservation gates.",
               "Reacquire is a strong capability only when parent/proof remain current; conflict probability is outside this leaf."
           ]}
    for p, c in totals.items():
        d = dict(c); d["safe_complete_coverage"] = c["safe_complete_scenarios"] / n; d["unsafe_rate"] = c["unsafe_scenarios"] / n
        d["avg_actions"] = c["actions"] / n; d["avg_checks"] = c["checks"] / n; out["policies"][p] = d
    print(json.dumps(out, indent=2, sort_keys=True))

if __name__ == "__main__": main()
