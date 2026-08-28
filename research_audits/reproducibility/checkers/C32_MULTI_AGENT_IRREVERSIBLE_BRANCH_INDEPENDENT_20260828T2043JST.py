#!/usr/bin/env python3
"""Independent reproduction of C32 irreversible-branch policy counts.
Does not import or execute the clean worker implementation.
"""
from collections import defaultdict
from itertools import product
import json

NODES = ("A", "B", "C")
CAP_KEYS = ("rA", "rB", "rC", "cA", "cB")
CURRENT = []
for cur in (frozenset(), frozenset({"A"}), frozenset({"A","B"})):
    for inflight in ("none", "will_absent", "will_present"):
        CURRENT.append((cur, inflight))
for cur in (frozenset({"A","C"}), frozenset({"A","B","C"})):
    CURRENT.append((cur, "none"))

def choose(cur, caps, budget, mode):
    choices = []
    missing = [n for n in NODES if n not in cur]
    if all(caps["r"+n] for n in missing) and len(missing) <= budget:
        choices.append(("forward", len(missing), "C" in missing))
    if "C" not in cur:
        rev = [n for n in ("A","B") if n in cur]
        if all(caps["c"+n] for n in rev) and len(rev) <= budget:
            choices.append(("rollback", len(rev), False))
    if not choices:
        return None
    if mode == "forward":
        f = [x for x in choices if x[0] == "forward"]
        return min(f, key=lambda x:x[1]) if f else None
    if mode == "rollback":
        r = [x for x in choices if x[0] == "rollback"]
        return min(r, key=lambda x:x[1]) if r else None
    return min(choices, key=lambda x:(x[1], 0 if x[0] == "rollback" else 1))

def run(no_inflight_mode, inflight_mode, budget):
    s = defaultdict(float)
    reasons = defaultdict(int)
    for cur, inflight in CURRENT:
        for values in product((False, True), repeat=len(CAP_KEYS)):
            caps = dict(zip(CAP_KEYS, values))
            s["worlds"] += 1
            plan_cur, inflight_after, wait = cur, inflight, 0
            if inflight == "none":
                action = choose(cur, caps, budget, no_inflight_mode)
            elif inflight_mode == "block":
                action = None
            elif inflight_mode == "forward":
                action = choose(cur, caps, budget, "forward")
            elif inflight_mode == "current_min":
                action = choose(cur, caps, budget, "min")
            elif inflight_mode == "wait_min":
                action = None
                if budget >= 1:
                    wait = 1
                    settled = set(cur)
                    if inflight == "will_present":
                        settled.add("C")
                    plan_cur, inflight_after = frozenset(settled), "none"
                    action = choose(plan_cur, caps, budget - 1, "min")
            else:
                raise ValueError(inflight_mode)
            if action is None:
                continue
            kind, mutations, issued_c = action
            s["terminal"] += 1
            s["actions"] += mutations + wait
            s["issued_c"] += int(issued_c)
            final = set(plan_cur)
            if kind == "forward":
                final.update(NODES)
            else:
                final.difference_update(("A","B"))
            if inflight_after == "will_present":
                final.add("C")
            safe = (kind == "forward" and final == set(NODES)) or (kind == "rollback" and not final)
            if not safe:
                s["unsafe"] += 1
                reasons["late_irreversible_writer_after_rollback" if kind == "rollback" and inflight_after == "will_present" else "other"] += 1
    w, t = int(s["worlds"]), int(s["terminal"])
    return {
        "worlds": w,
        "terminal": t,
        "coverage": t / w,
        "unsafe_terminal": int(s["unsafe"]),
        "unsafe_rate_given_terminal": s["unsafe"] / t if t else None,
        "expected_incremental_actions_per_world": s["actions"] / w,
        "issued_irreversible_c_retry_per_world": s["issued_c"] / w,
        "unsafe_reasons": dict(reasons),
    }

POLICIES = {
    "current_min": ("min", "current_min"),
    "quiescence_gate": ("min", "block"),
    "wait_then_min": ("min", "wait_min"),
    "forward_guard": ("min", "forward"),
    "always_forward": ("forward", "forward"),
}
out = {name:{str(b):run(*genome, b) for b in (1,2,3)} for name,genome in POLICIES.items()}
assert out["current_min"]["2"]["terminal"] == 264
assert out["current_min"]["2"]["unsafe_terminal"] == 52
assert out["current_min"]["2"]["unsafe_reasons"] == {"late_irreversible_writer_after_rollback": 52}
assert out["quiescence_gate"]["2"]["terminal"] == 120 and out["quiescence_gate"]["2"]["unsafe_terminal"] == 0
assert out["forward_guard"]["2"]["terminal"] == 168 and out["forward_guard"]["2"]["unsafe_terminal"] == 0
assert out["wait_then_min"]["2"]["terminal"] == 232 and out["wait_then_min"]["2"]["unsafe_terminal"] == 0
assert out["wait_then_min"]["3"]["terminal"] == 248 and out["wait_then_min"]["3"]["unsafe_terminal"] == 0
print(json.dumps({"independent": True, "worker_imported": False, "selected_results": out}, indent=2, sort_keys=True))
