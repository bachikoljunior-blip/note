#!/usr/bin/env python3
"""Finite synthetic stress test for concurrent/out-of-order effect evidence reducers.
Counts are mechanism counts, not empirical rates.
"""
from itertools import product
from collections import Counter, defaultdict
import json

LIFECYCLES = {
    "success": (["PENDING", "SUCCEEDED"], "SUCCEEDED"),
    "late_failed": (["SUCCEEDED", "FAILED"], "FAILED"),
    "reversed": (["SUCCEEDED", "REVERSED"], "REVERSED"),
    "pending": (["PENDING"], "PENDING"),
    "accepted_then_success": (["ACCEPTED", "SUCCEEDED"], "SUCCEEDED"),
    "accepted_then_failed": (["ACCEPTED", "FAILED"], "FAILED"),
}
STALE_STATES = [None, "SUCCEEDED", "FAILED", "REVERSED"]
DELIVERY_PATTERNS = ["split_ordered", "split_reverse", "duplicate_both", "a_partial_b_full", "a_stale_b_current", "local_vs_provider"]
TIMESTAMP_MODES = ["ordered", "tie_seconds", "stale_newer"]
STATUS_AVAILABLE = [False, True]
A_STALE_EPOCH = [False, True]
COMMIT_ORDERS = ["A_then_B", "B_then_A"]
POLICIES = ["root_lww", "timestamp_lww", "naive_enum", "event_set_unfenced", "fenced_source_reducer"]
RANK = {"UNKNOWN": 0, "PENDING": 1, "ACCEPTED": 2, "SUCCEEDED": 3, "FAILED": 4, "REVERSED": 5}
TERMINAL = {"SUCCEEDED", "FAILED", "REVERSED"}


def make_events(lifecycle, stale_state, ts_mode):
    states, truth = LIFECYCLES[lifecycle]
    cur = []
    for i, state in enumerate(states):
        source = "local_acceptance" if state == "ACCEPTED" else "provider_event"
        ts = 100 + i
        cur.append({"event_id": f"X2-e{i+1}", "object_id": "X2", "state": state, "source": source, "ts": ts, "seq": i+1})
    stale = None
    if stale_state:
        stale = {"event_id": "X1-old", "object_id": "X1", "state": stale_state, "source": "provider_event", "ts": 99, "seq": 9}
    if ts_mode == "tie_seconds":
        for e in cur:
            e["ts"] = 100
        if stale:
            stale["ts"] = 100
    elif ts_mode == "stale_newer" and stale:
        stale["ts"] = 200
    return cur, stale, truth


def deliveries(cur, stale, pattern):
    first, second = cur[0], cur[-1]
    if pattern == "split_ordered":
        A, B = [first] + ([stale] if stale else []), [second]
    elif pattern == "split_reverse":
        A, B = [second] + ([stale] if stale else []), [first]
    elif pattern == "duplicate_both":
        A, B = list(cur) + ([stale] if stale else []), list(cur)
    elif pattern == "a_partial_b_full":
        A, B = [first] + ([stale] if stale else []), list(cur)
    elif pattern == "a_stale_b_current":
        A, B = ([stale] if stale else [first]), list(cur)
    elif pattern == "local_vs_provider":
        local = [e for e in cur if e["source"] == "local_acceptance"]
        A = (local if local else [first]) + ([stale] if stale else [])
        B = [e for e in cur if e["source"] == "provider_event"] or [second]
    else:
        raise ValueError(pattern)
    return A, B


def event_trigger_count(events):
    return sum(1 for e in events if e["state"] in ("FAILED", "REVERSED"))


def strong_reduce(events, status_available, truth):
    unique = {e["event_id"]: e for e in events}
    cur = [e for e in unique.values() if e["object_id"] == "X2"]
    provider_terminal = {e["state"] for e in cur if e["source"] == "provider_event" and e["state"] in TERMINAL}
    provider_nonterminal = {e["state"] for e in cur if e["source"] == "provider_event" and e["state"] not in TERMINAL}
    lookups = 0
    if len(provider_terminal) == 1:
        return next(iter(provider_terminal)), "X2", lookups
    if len(provider_terminal) > 1:
        if status_available:
            return truth, "X2", 1
        return "UNKNOWN", "X2", lookups
    if "PENDING" in provider_nonterminal:
        return "PENDING", "X2", lookups
    return "UNKNOWN", None, lookups


def score_output(state, object_id, truth):
    r = Counter()
    r["terminal"] = int(state in TERMINAL)
    r["correct_terminal"] = int(state == truth and truth in TERMINAL)
    r["false_terminal"] = int(state in TERMINAL and state != truth)
    r["missed_failure_or_reversal"] = int(truth in ("FAILED", "REVERSED") and state == "SUCCEEDED")
    r["stale_evidence_accepted"] = int(object_id == "X1")
    r["unresolved"] = int(state not in TERMINAL)
    return r


def eval_root_lww(A, B, order, truth):
    chosen = (B[-1] if B else None) if order == "A_then_B" else (A[-1] if A else None)
    r = score_output(chosen["state"] if chosen else "UNKNOWN", chosen["object_id"] if chosen else None, truth)
    triggers = event_trigger_count(A) + event_trigger_count(B)
    r["duplicate_comp_trigger"] = int(triggers > 1)
    r["comp_trigger_count"] = triggers
    return r


def eval_timestamp_lww(A, B, order, truth):
    stream = (A + B) if order == "A_then_B" else (B + A)
    chosen = None
    for e in stream:
        if chosen is None or e["ts"] >= chosen["ts"]:
            chosen = e
    r = score_output(chosen["state"] if chosen else "UNKNOWN", chosen["object_id"] if chosen else None, truth)
    triggers = event_trigger_count(stream)
    r["duplicate_comp_trigger"] = int(triggers > 1)
    r["comp_trigger_count"] = triggers
    return r


def eval_naive_enum(A, B, truth):
    events = A + B
    chosen = max(events, key=lambda e: RANK[e["state"]]) if events else None
    r = score_output(chosen["state"] if chosen else "UNKNOWN", chosen["object_id"] if chosen else None, truth)
    r["duplicate_comp_trigger"] = 0
    r["comp_trigger_count"] = int(chosen is not None and chosen["state"] in ("FAILED", "REVERSED"))
    return r


def eval_event_set_unfenced(A, B, order, status_available, truth):
    sA, oA, qA = strong_reduce(A, status_available, truth)
    sB, oB, qB = strong_reduce(B, status_available, truth)
    state, oid = (sB, oB) if order == "A_then_B" else (sA, oA)
    r = score_output(state, oid, truth)
    r["status_lookups"] = qA + qB
    triggers = int(sA in ("FAILED", "REVERSED")) + int(sB in ("FAILED", "REVERSED"))
    r["comp_trigger_count"] = triggers
    r["duplicate_comp_trigger"] = int(triggers > 1)
    return r


def eval_fenced(A, B, a_stale_epoch, status_available, truth):
    union = {e["event_id"]: e for e in (A + B)}
    state, oid, lookups = strong_reduce(list(union.values()), status_available, truth)
    r = score_output(state, oid, truth)
    r["status_lookups"] = lookups
    r["unique_event_count"] = len(union)
    r["raw_delivery_count"] = len(A) + len(B)
    r["deduped_delivery_count"] = len(A) + len(B) - len(union)
    r["stale_reducer_write_blocked"] = int(a_stale_epoch)
    r["comp_trigger_count"] = int(state in ("FAILED", "REVERSED"))
    r["duplicate_comp_trigger"] = 0
    return r


def main():
    totals = {p: Counter() for p in POLICIES}
    slices = defaultdict(Counter)
    n = 0
    for lifecycle, stale_state, pattern, ts_mode, status_available, a_stale_epoch, order in product(
        LIFECYCLES, STALE_STATES, DELIVERY_PATTERNS, TIMESTAMP_MODES, STATUS_AVAILABLE, A_STALE_EPOCH, COMMIT_ORDERS
    ):
        cur, stale, truth = make_events(lifecycle, stale_state, ts_mode)
        A, B = deliveries(cur, stale, pattern)
        results = {
            "root_lww": eval_root_lww(A, B, order, truth),
            "timestamp_lww": eval_timestamp_lww(A, B, order, truth),
            "naive_enum": eval_naive_enum(A, B, truth),
            "event_set_unfenced": eval_event_set_unfenced(A, B, order, status_available, truth),
            "fenced_source_reducer": eval_fenced(A, B, a_stale_epoch, status_available, truth),
        }
        n += 1
        for p, r in results.items():
            totals[p]["scenarios"] += 1
            for k, v in r.items():
                totals[p][k] += v
            if r["false_terminal"]: totals[p]["false_terminal_scenarios"] += 1
            if r["correct_terminal"]: totals[p]["correct_terminal_scenarios"] += 1
            if r["stale_evidence_accepted"]: totals[p]["stale_evidence_scenarios"] += 1
            if r["missed_failure_or_reversal"]: totals[p]["missed_failure_or_reversal_scenarios"] += 1
            if r["duplicate_comp_trigger"]: totals[p]["duplicate_comp_trigger_scenarios"] += 1
            if r["unresolved"]: totals[p]["unresolved_scenarios"] += 1

        if lifecycle in ("late_failed", "reversed") and ts_mode == "tie_seconds":
            slices["tie_timestamp_late_terminal"]["scenarios"] += 1
            for p, r in results.items():
                slices["tie_timestamp_late_terminal"][p + "_false_terminal"] += int(r["false_terminal"])
                slices["tie_timestamp_late_terminal"][p + "_missed"] += int(r["missed_failure_or_reversal"])
        if stale_state in ("FAILED", "REVERSED") and lifecycle == "success":
            slices["stale_prior_attempt_vs_current_success"]["scenarios"] += 1
            for p, r in results.items():
                slices["stale_prior_attempt_vs_current_success"][p + "_false_terminal"] += int(r["false_terminal"])
                slices["stale_prior_attempt_vs_current_success"][p + "_stale_evidence"] += int(r["stale_evidence_accepted"])
        if pattern == "duplicate_both":
            slices["duplicate_delivery"]["scenarios"] += 1
            for p, r in results.items():
                slices["duplicate_delivery"][p + "_duplicate_comp_trigger"] += int(r["duplicate_comp_trigger"])
        if a_stale_epoch and order == "B_then_A":
            slices["stale_reducer_commits_last"]["scenarios"] += 1
            for p, r in results.items():
                slices["stale_reducer_commits_last"][p + "_false_terminal"] += int(r["false_terminal"])

    out = {
        "model": {
            "equal_weight_synthetic": True,
            "empirical_rate_claim": False,
            "scenario_count": n,
            "lifecycle_count": len(LIFECYCLES),
            "stale_state_count": len(STALE_STATES),
            "delivery_pattern_count": len(DELIVERY_PATTERNS),
            "timestamp_mode_count": len(TIMESTAMP_MODES),
            "status_availability_count": len(STATUS_AVAILABLE),
            "reducer_epoch_cases": len(A_STALE_EPOCH),
            "commit_order_count": len(COMMIT_ORDERS)
        },
        "policies": {},
        "slices": {k: dict(v) for k, v in slices.items()},
        "scope_limits": [
            "Finite mechanism lattice only; not production failure rates.",
            "The strong reducer is given the current object identity X2 by the terminality certificate; prior-attempt X1 events are not authoritative for X2.",
            "When conflicting authoritative terminal states exist, the strong reducer uses a modeled authoritative current-status lookup if available; otherwise it stays nonterminal.",
            "Provider-specific transition semantics are deliberately not generalized into one enum ordering."
        ]
    }
    for p, c in totals.items():
        d = dict(c)
        d["correct_terminal_coverage"] = c["correct_terminal_scenarios"] / n
        d["false_terminal_rate"] = c["false_terminal_scenarios"] / n
        d["duplicate_comp_trigger_rate"] = c["duplicate_comp_trigger_scenarios"] / n
        out["policies"][p] = d
    print(json.dumps(out, indent=2, sort_keys=True))

if __name__ == "__main__":
    main()
