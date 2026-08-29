#!/usr/bin/env python3
"""Phase-1 multi_agent Part 35 finite model.

Cancellation-tombstone compaction under stable repository authority, plus an
explicit same-domain complete-rewind indistinguishability proof obligation.
Equal-weight synthetic counts; not production rates. No network required.
"""
from itertools import product
import json

WIDTHS = [1, 2, 3]
FLOOR_STATES = ["none", "partial", "full"]
STRATEGIES = [
    "permanent_tombstone",
    "gc_after_clean_no_floor",
    "per_cell_floor_gc",
    "terminal_index",
    "generation_watermark",
    "fail_closed_no_gc",
]


def evaluate(strategy, width, floor_state, stale_restore, cell_recreate,
             incarnation_sensitive, key_reuse, key_incarnation_sensitive,
             gc_attempt):
    unsafe = false_block = gc_done = 0
    all_floored = floor_state == "full" or (width == 1 and floor_state == "partial")

    if strategy in ("permanent_tombstone", "fail_closed_no_gc"):
        pass

    elif strategy == "gc_after_clean_no_floor":
        if gc_attempt:
            gc_done = 1
            if stale_restore:
                unsafe = 1
            if cell_recreate and not incarnation_sensitive:
                unsafe = 1

    elif strategy == "per_cell_floor_gc":
        if gc_attempt and all_floored:
            gc_done = 1
            if cell_recreate and not incarnation_sensitive:
                unsafe = 1

    elif strategy == "terminal_index":
        if gc_attempt:
            gc_done = 1  # bulky reservation record removed; terminal index entry remains
        if key_reuse and not key_incarnation_sensitive:
            false_block = 1

    elif strategy == "generation_watermark":
        if gc_attempt:
            gc_done = 1
        if key_reuse and not key_incarnation_sensitive:
            false_block = 1
        if cell_recreate and not incarnation_sensitive:
            unsafe = 1

    return {"unsafe": unsafe, "false_block": false_block, "gc_done": gc_done}


def build_rows():
    rows = []
    for vals in product(
        WIDTHS, FLOOR_STATES, [False, True], [False, True],
        [False, True], [False, True], [False, True], [False, True]
    ):
        width, floor_state, stale_restore, cell_recreate, incarnation_sensitive, key_reuse, key_incarnation_sensitive, gc_attempt = vals
        for strategy in STRATEGIES:
            rows.append({
                "width": width, "floor_state": floor_state,
                "stale_restore": stale_restore, "cell_recreate": cell_recreate,
                "incarnation_sensitive": incarnation_sensitive,
                "key_reuse": key_reuse,
                "key_incarnation_sensitive": key_incarnation_sensitive,
                "gc_attempt": gc_attempt, "strategy": strategy,
                **evaluate(strategy, *vals),
            })
    return rows


def aggregate(rows):
    out = {}
    for strategy in STRATEGIES:
        x = [r for r in rows if r["strategy"] == strategy]
        out[strategy] = {
            "n": len(x),
            "unsafe": sum(r["unsafe"] for r in x),
            "false_block": sum(r["false_block"] for r in x),
            "gc_done": sum(r["gc_done"] for r in x),
        }
    return out


def indistinguishability_pair():
    # World A: repository legitimately remains at byte state S = GRANTED(g1).
    # World B: repository reached CANCELLED(g1), then a complete authority-domain
    # rewind restored every allowed persistent witness to the exact same bytes S.
    # A stateless deterministic role reading only current same-domain state sees S in both.
    observation_A = "S:GRANTED(g1)"
    observation_B = "S:GRANTED(g1)"
    assert observation_A == observation_B
    return {
        "world_A": "never_cancelled; current bytes S=GRANTED(g1)",
        "world_B": "cancelled_then_complete_same_domain_rewind; current bytes S=GRANTED(g1)",
        "observations_identical": True,
        "consequence": "Any deterministic decision on allowed current bytes is identical in A and B. Admit preserves liveness in A but re-admits stale authority in B; reject preserves B safety but false-blocks A. A surviving anti-rollback assumption/witness outside the rewound state is necessary to distinguish them."
    }


def main():
    rows = build_rows()
    strong = [r for r in rows if r["incarnation_sensitive"] and r["key_incarnation_sensitive"]]
    print(json.dumps({
        "scenario_count": len(rows) // len(STRATEGIES),
        "strategy_evaluations": len(rows),
        "strong_incarnation_slice": aggregate(strong),
        "complete_rewind_pair": indistinguishability_pair(),
        "note": "Equal-weight finite synthetic mechanism counts; not production rates."
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
