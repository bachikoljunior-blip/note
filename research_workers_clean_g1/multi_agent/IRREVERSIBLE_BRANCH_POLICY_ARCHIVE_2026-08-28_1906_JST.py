#!/usr/bin/env python3
"""
Exact mechanism lattice for repair-policy portfolios under one unresolved
writer to an irreversible branch.

This is deliberately synthetic. Balanced-world proportions are mechanism
counts, not provider incident rates.

Graph: A -> {B, C}; C is irreversible.
Current effect snapshots are dependency-consistent when observed, but an old
in-flight write to C can later complete after a fresh snapshot. The planner
may forward-complete, rollback reversible effects, block, or wait for the old
writer and then re-plan.

The genome is:
  no_inflight_mode in {min, forward, rollback}
  inflight_mode in {block, forward, current_min, wait_min}

Capabilities:
  retry A/B/C (certified same-intent effect-producing action)
  compensate A/B
C cannot be compensated.

Action budget counts additional wait/retry/compensate mutations after the
initial fresh snapshot. A final proof read is assumed mandatory and common to
all terminal claims, so it is not charged in this comparative budget.

Safety objective accepts exactly one of:
  forward terminal = {A,B,C}
  rollback terminal = {}
"""

from itertools import product
from collections import defaultdict
import json

NODES = ("A", "B", "C")

CURRENT_STATES = []
for cur in (frozenset(), frozenset({"A"}), frozenset({"A","B"})):
    for inflight in ("none", "will_absent", "will_present"):
        CURRENT_STATES.append((cur, inflight))
for cur in (frozenset({"A","C"}), frozenset({"A","B","C"})):
    CURRENT_STATES.append((cur, "none"))

CAP_KEYS = ("rA","rB","rC","cA","cB")
NO_INFLIGHT_MODES = ("min","forward","rollback")
INFLIGHT_MODES = ("block","forward","current_min","wait_min")

def best_path(cur, caps, budget, mode):
    options = []

    missing = [n for n in NODES if n not in cur]
    if all(caps["r"+n] for n in missing):
        cost = len(missing)
        if cost <= budget:
            options.append(("forward", cost, "C" in missing))

    if "C" not in cur:
        present_reversible = [n for n in ("A","B") if n in cur]
        if all(caps["c"+n] for n in present_reversible):
            cost = len(present_reversible)
            if cost <= budget:
                options.append(("rollback", cost, False))

    if not options:
        return None
    if mode == "forward":
        fw = [x for x in options if x[0] == "forward"]
        return min(fw, key=lambda x: x[1]) if fw else None
    if mode == "rollback":
        rb = [x for x in options if x[0] == "rollback"]
        return min(rb, key=lambda x: x[1]) if rb else None
    # minimize mutations; ties prefer rollback to avoid a new irreversible C.
    return min(options, key=lambda x: (x[1], 0 if x[0] == "rollback" else 1))

def evaluate_genome(no_inflight_mode, inflight_mode, budget):
    s = defaultdict(float)
    unsafe_reasons = defaultdict(int)

    for cur, inflight in CURRENT_STATES:
        for values in product((False, True), repeat=len(CAP_KEYS)):
            caps = dict(zip(CAP_KEYS, values))
            s["worlds"] += 1

            action = None
            extra_wait = 0
            plan_cur = cur
            inflight_after = inflight

            if inflight == "none":
                action = best_path(cur, caps, budget, no_inflight_mode)
            else:
                if inflight_mode == "block":
                    action = None
                elif inflight_mode == "forward":
                    action = best_path(cur, caps, budget, "forward")
                elif inflight_mode == "current_min":
                    action = best_path(cur, caps, budget, "min")
                elif inflight_mode == "wait_min":
                    if budget >= 1:
                        extra_wait = 1
                        settled = set(cur)
                        if inflight == "will_present":
                            settled.add("C")
                        plan_cur = frozenset(settled)
                        inflight_after = "none"
                        action = best_path(plan_cur, caps, budget - 1, "min")
                else:
                    raise ValueError(inflight_mode)

            if action is None:
                continue

            kind, mutations, issued_c = action
            s["terminal"] += 1
            s["actions"] += mutations + extra_wait
            s["issued_irreversible_c_retry"] += int(issued_c)

            final = set(plan_cur)
            if kind == "forward":
                final.update(NODES)
            else:
                final.difference_update(("A","B"))

            # If the planner did not wait, the old writer can complete later.
            if inflight_after == "will_present":
                final.add("C")

            safe = ((kind == "forward" and final == set(NODES)) or
                    (kind == "rollback" and final == set()))
            if not safe:
                s["unsafe"] += 1
                if kind == "rollback" and inflight_after == "will_present":
                    unsafe_reasons["late_irreversible_writer_after_rollback"] += 1
                else:
                    unsafe_reasons["other"] += 1

    worlds = int(s["worlds"])
    terminal = int(s["terminal"])
    return {
        "genome": {
            "no_inflight_mode": no_inflight_mode,
            "inflight_mode": inflight_mode,
        },
        "budget": budget,
        "worlds": worlds,
        "terminal": terminal,
        "coverage": terminal / worlds,
        "unsafe_terminal": int(s["unsafe"]),
        "unsafe_rate_given_terminal": (s["unsafe"] / terminal) if terminal else None,
        "expected_incremental_actions_per_world": s["actions"] / worlds,
        "mean_incremental_actions_given_terminal": (s["actions"] / terminal) if terminal else None,
        "issued_irreversible_c_retry_per_world": s["issued_irreversible_c_retry"] / worlds,
        "issued_irreversible_c_retry_rate_given_terminal":
            (s["issued_irreversible_c_retry"] / terminal) if terminal else None,
        "unsafe_reasons": dict(unsafe_reasons),
    }

def pareto_front(rows):
    # Among safe genomes: maximize coverage, minimize expected actions,
    # minimize irreversible-C retry exposure.
    safe = [r for r in rows if r["unsafe_terminal"] == 0]
    front = []
    for r in safe:
        dominated = False
        for q in safe:
            if q is r:
                continue
            weak = (
                q["coverage"] >= r["coverage"]
                and q["expected_incremental_actions_per_world"] <= r["expected_incremental_actions_per_world"]
                and q["issued_irreversible_c_retry_per_world"] <= r["issued_irreversible_c_retry_per_world"]
            )
            strict = (
                q["coverage"] > r["coverage"]
                or q["expected_incremental_actions_per_world"] < r["expected_incremental_actions_per_world"]
                or q["issued_irreversible_c_retry_per_world"] < r["issued_irreversible_c_retry_per_world"]
            )
            if weak and strict:
                dominated = True
                break
        if not dominated:
            front.append(r)
    return front

all_results = {}
for budget in (0,1,2,3,4):
    rows = [
        evaluate_genome(nm, im, budget)
        for nm in NO_INFLIGHT_MODES
        for im in INFLIGHT_MODES
    ]
    all_results[str(budget)] = {
        "rows": rows,
        "pareto_front": pareto_front(rows),
    }

# Named policies for compact comparison.
named = {
    "current_min": ("min", "current_min"),
    "quiescence_gate": ("min", "block"),
    "wait_then_min": ("min", "wait_min"),
    "forward_guard": ("min", "forward"),
    "always_forward": ("forward", "forward"),
    "always_rollback": ("rollback", "current_min"),
}
named_results = {
    name: {
        str(b): evaluate_genome(genome[0], genome[1], b)
        for b in (0,1,2,3,4)
    }
    for name, genome in named.items()
}

# Exact invariants.
assert all(
    named_results[p][str(b)]["unsafe_terminal"] == 0
    for p in ("quiescence_gate","wait_then_min","forward_guard","always_forward")
    for b in (0,1,2,3,4)
)
assert named_results["current_min"]["2"]["unsafe_terminal"] == 52
assert named_results["current_min"]["2"]["unsafe_reasons"] == {
    "late_irreversible_writer_after_rollback": 52
}
assert named_results["wait_then_min"]["2"]["terminal"] == 232
assert named_results["forward_guard"]["2"]["terminal"] == 168
assert named_results["quiescence_gate"]["2"]["terminal"] == 120

# Safe-policy coverage must not decrease when action budget increases.
for p in ("quiescence_gate","wait_then_min","forward_guard","always_forward"):
    cov = [named_results[p][str(b)]["coverage"] for b in (0,1,2,3,4)]
    assert all(a <= b + 1e-15 for a,b in zip(cov, cov[1:]))

out = {
    "study": "irreversible_branch_reconciliation_policy_archive",
    "scope": {
        "graph": "A -> {B,C}; C irreversible",
        "world_count_per_budget": 11 * (2**5),
        "current_state_cases": len(CURRENT_STATES),
        "capability_vectors": 2**5,
        "balanced_synthetic": True,
        "incident_rate_estimate": False,
        "budget_definition": "additional wait/retry/compensate actions after one fresh snapshot; mandatory final proof read not charged",
    },
    "named_results": named_results,
    "all_policy_genomes": all_results,
}
print(json.dumps(out, indent=2, sort_keys=True))
