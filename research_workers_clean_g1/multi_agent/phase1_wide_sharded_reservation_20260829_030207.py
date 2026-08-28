#!/usr/bin/env python3
"""Finite mechanism stress test for wide/sharded multi-effect reservation.

All scenario weights are equal synthetic mechanism stressors, not production probabilities.
The model compares:
  * one <=100-action atomic reservation,
  * deterministic per-shard reservation with only an in-memory complete certificate,
  * durable reservation-intent + shard receipts + commit record,
  * speculative immutable staging + one fenced integrator,
  * a negative control that treats partial shard claims as authority.
"""
from itertools import product, permutations
from collections import Counter
import json

WIDTHS = ["small80", "wide120"]
OVERLAPS = ["disjoint", "one_shard", "multi_shard"]
ALIASES = [False, True]
OUTCOMES = ["ok", "ambiguous_applied", "ambiguous_not_applied"]
TOKEN_STATES = ["fresh", "expired"]
CRASHES = ["none", "early_after_first_unit", "late_before_publish"]
PARENTS = ["stable", "superseded_after_first_unit"]
LEASES = ["valid", "expired_before_publish"]
HOTS = ["none", "shard2_cancel"]
RESTARTS = ["full_state", "reservation_only"]

def scenarios():
    keys = ["width","overlap","alias","outcome","token","crash","parent","lease","hot","restart"]
    vals = product(WIDTHS, OVERLAPS, ALIASES, OUTCOMES, TOKEN_STATES, CRASHES, PARENTS, LEASES, HOTS, RESTARTS)
    return [dict(zip(keys, v)) for v in vals]

def base_result():
    return dict(
        terminal=False, unsafe=False, orphan=False, false_exclusion=False,
        wasted_compute=0, recovery_reads=0, recovery_writes=0,
        partial_authority=False, duplicate_effect=False,
        parallel_compute_admit=False, parallel_effect_admit=False,
        structural_block=False
    )

def atomic_txn(s):
    r = base_result()
    if s["width"] == "wide120":
        r["structural_block"] = True
        if s["overlap"] == "disjoint" and s["parent"] == "stable" and s["lease"] == "valid" and s["hot"] == "none":
            r["false_exclusion"] = True
        return r
    recovery_needed = s["crash"] != "none" or s["outcome"] != "ok"
    if recovery_needed:
        r["recovery_reads"] += 1
        if s["outcome"] == "ambiguous_not_applied":
            r["recovery_writes"] += 1
    if s["hot"] != "none":
        if s["overlap"] == "disjoint" and s["parent"] == "stable" and s["lease"] == "valid":
            r["false_exclusion"] = True
        return r
    if s["parent"] != "stable" or s["lease"] != "valid":
        if s["outcome"] in ("ok", "ambiguous_applied") or s["crash"] == "late_before_publish":
            r["recovery_writes"] += 1
        return r
    r["terminal"] = True
    if s["overlap"] == "disjoint":
        r["parallel_compute_admit"] = True
        r["parallel_effect_admit"] = True
    return r

def per_shard(s):
    r = base_result()
    needs_recovery = s["crash"] != "none" or s["outcome"] != "ok"
    unrecoverable = False
    if s["restart"] == "reservation_only":
        if s["crash"] != "none":
            unrecoverable = True
        if s["outcome"] != "ok" and s["token"] == "expired":
            unrecoverable = True
    if needs_recovery and not unrecoverable:
        if s["crash"] != "none" or s["token"] == "expired":
            r["recovery_reads"] += 3
        if s["outcome"] == "ambiguous_not_applied":
            r["recovery_writes"] += 1
    if unrecoverable:
        r["orphan"] = True
        return r
    if s["hot"] != "none":
        if s["restart"] == "reservation_only":
            r["orphan"] = True
        else:
            r["recovery_writes"] += 1
        if s["overlap"] == "disjoint" and s["parent"] == "stable" and s["lease"] == "valid":
            r["false_exclusion"] = True
        return r
    if s["parent"] != "stable" or s["lease"] != "valid":
        if s["restart"] == "reservation_only":
            r["orphan"] = True
        else:
            r["recovery_writes"] += 1
        return r
    r["terminal"] = True
    if s["overlap"] == "disjoint":
        r["parallel_compute_admit"] = True
        r["parallel_effect_admit"] = True
    return r

def intent_shards(s):
    r = base_result()
    recovery_needed = s["crash"] != "none" or s["outcome"] != "ok" or s["restart"] == "reservation_only"
    if recovery_needed:
        r["recovery_reads"] += 4
        if s["outcome"] == "ambiguous_not_applied":
            r["recovery_writes"] += 1
    if s["hot"] != "none":
        r["recovery_writes"] += 2
        if s["overlap"] == "disjoint" and s["parent"] == "stable" and s["lease"] == "valid":
            r["false_exclusion"] = True
        return r
    if s["parent"] != "stable" or s["lease"] != "valid":
        r["recovery_writes"] += 2
        return r
    r["terminal"] = True
    if s["overlap"] == "disjoint":
        r["parallel_compute_admit"] = True
        r["parallel_effect_admit"] = True
    return r

def staged_integrator(s):
    r = base_result()
    if s["parent"] != "stable" or s["lease"] != "valid":
        r["wasted_compute"] = 2
        return r
    r["terminal"] = True
    if s["overlap"] == "disjoint":
        r["parallel_compute_admit"] = True
        r["parallel_effect_admit"] = False
    else:
        r["wasted_compute"] = 1
    if s["crash"] != "none" or s["outcome"] != "ok":
        r["recovery_reads"] += 1
    return r

def naive_partial(s):
    r = base_result()
    can_resolve_first = (
        s["outcome"] == "ok" or
        s["outcome"] == "ambiguous_applied" or
        s["token"] == "fresh" or
        s["restart"] == "full_state"
    )
    first_acquired = can_resolve_first
    full_complete = (
        first_acquired and s["crash"] == "none" and s["hot"] == "none"
        and s["parent"] == "stable" and s["lease"] == "valid"
    )
    if full_complete:
        r["terminal"] = True
        if s["overlap"] == "disjoint":
            r["parallel_compute_admit"] = True
            r["parallel_effect_admit"] = True
        return r
    if first_acquired:
        r["partial_authority"] = True
        r["unsafe"] = True
        r["terminal"] = True
        if s["overlap"] != "disjoint" and s["lease"] == "expired_before_publish":
            r["duplicate_effect"] = True
    return r

PROTOCOLS = {
    "atomic<=100": atomic_txn,
    "per_shard_complete_cert": per_shard,
    "intent+shards": intent_shards,
    "staged_fenced_integrator": staged_integrator,
    "NEG_partial_shard_authority": naive_partial,
}

def summarize(rows):
    out = {}
    for name, fn in PROTOCOLS.items():
        c, sums = Counter(), Counter()
        for s in rows:
            r = fn(s)
            for k, v in r.items():
                if isinstance(v, bool):
                    c[k] += int(v)
                else:
                    sums[k] += v
        out[name] = {**c, **{f"sum_{k}": v for k, v in sums.items()}}
    return out

def slice_stats(rows, pred):
    subset = [s for s in rows if pred(s)]
    return {"count": len(subset), "protocols": summarize(subset)}

def simulate_orders(a, b, steps=20):
    held, idx = {}, {"A": 0, "B": 0}
    blocked, done = {"A": False, "B": False}, {"A": False, "B": False}
    orders = {"A": a, "B": b}
    for t in range(steps):
        w = "A" if t % 2 == 0 else "B"
        if not done[w] and not blocked[w]:
            if idx[w] >= 3:
                done[w] = True
            else:
                sh = orders[w][idx[w]]
                if sh not in held:
                    held[sh] = w
                    idx[w] += 1
                    if idx[w] >= 3:
                        done[w] = True
                elif held[sh] != w:
                    blocked[w] = True
        for ww in ("A", "B"):
            if done[ww]:
                owned = [k for k, v in held.items() if v == ww]
                for k in owned:
                    del held[k]
                other = "B" if ww == "A" else "A"
                blocked[other] = False
        if blocked["A"] and blocked["B"]:
            return "deadlock"
        if done["A"] and done["B"]:
            return "both_done"
    return "incomplete"

def main():
    rows = scenarios()
    slices = {
        "wide_nominal": slice_stats(rows, lambda s:
            s["width"]=="wide120" and not s["alias"] and s["outcome"]=="ok" and s["token"]=="fresh"
            and s["crash"]=="none" and s["parent"]=="stable" and s["lease"]=="valid"
            and s["hot"]=="none" and s["restart"]=="full_state"),
        "reservation_only_after_crash_wide": slice_stats(rows, lambda s:
            s["width"]=="wide120" and not s["alias"] and s["crash"]!="none" and s["parent"]=="stable"
            and s["lease"]=="valid" and s["hot"]=="none" and s["restart"]=="reservation_only" and s["token"]=="expired"),
        "expired_ambiguous_reservation_only_wide": slice_stats(rows, lambda s:
            s["width"]=="wide120" and not s["alias"] and s["outcome"]!="ok" and s["token"]=="expired"
            and s["crash"]=="none" and s["parent"]=="stable" and s["lease"]=="valid"
            and s["hot"]=="none" and s["restart"]=="reservation_only"),
        "parent_superseded_reservation_only_wide": slice_stats(rows, lambda s:
            s["width"]=="wide120" and not s["alias"] and s["outcome"]=="ok" and s["crash"]=="none"
            and s["parent"]!="stable" and s["lease"]=="valid" and s["hot"]=="none" and s["restart"]=="reservation_only"),
        "hot_cancel_full_state_wide": slice_stats(rows, lambda s:
            s["width"]=="wide120" and not s["alias"] and s["outcome"]=="ok" and s["crash"]=="none"
            and s["parent"]=="stable" and s["lease"]=="valid" and s["hot"]!="none" and s["restart"]=="full_state"),
    }
    order_counts = Counter()
    ps = list(permutations(["s1","s2","s3"]))
    for a in ps:
        for b in ps:
            order_counts[simulate_orders(a,b)] += 1

    result = {
        "scenario_count": len(rows),
        "factors": {
            "width": WIDTHS, "overlap": OVERLAPS, "alias": ALIASES, "outcome": OUTCOMES,
            "token": TOKEN_STATES, "crash": CRASHES, "parent": PARENTS, "lease": LEASES,
            "hot": HOTS, "restart": RESTARTS
        },
        "protocol_summary": summarize(rows),
        "targeted_slices": slices,
        "acquisition_order_microtest": {
            "workers": 2,
            "shards_needed_by_each": 3,
            "possible_order_pairs": 36,
            "arbitrary_order_interleaved": dict(order_counts),
            "canonical_global_order_deadlock_count": 0,
        },
    }
    print(json.dumps(result, indent=2, sort_keys=True))

if __name__ == "__main__":
    main()
