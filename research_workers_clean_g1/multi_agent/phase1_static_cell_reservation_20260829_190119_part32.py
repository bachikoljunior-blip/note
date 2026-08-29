#!/usr/bin/env python3
"""Phase-1 multi_agent Part 32 finite model.

Static logical authority cells + ordered multi-cell reservation.
Equal-weight synthetic counts; not production rates. No network required.
"""
from itertools import product
from collections import defaultdict
import json

CLAIMS = {
    "L0": (0,),
    "L1": (1,),
    "L2": (2,),
    "SPAN01": (0, 1),
    "SPAN12": (1, 2),
    "SPAN012": (0, 1, 2),
}
TIMINGS = ["before_acquire", "after_first", "after_all_before_commit", "after_commit"]
MECHANISMS = ["global_root", "ancestor_only", "ordered_weak", "ordered_strong", "interval_lock", "staging_integrator"]


def auth_node(claim):
    s = set(claim)
    if len(s) == 1:
        return f"L{next(iter(s))}"
    if s.issubset({0, 1}):
        return "P01"
    return "ROOT"


def evaluate(mech, A, B, timing, parent_supersede, parent_fence,
             same_gen_expiry, canonical_order, registry_complete):
    A, B = set(A), set(B)
    overlap = bool(A & B)
    disjoint = not overlap
    blocked = False
    unsafe = False
    false_exclusion = False
    deadlock = 0
    staged_waste = 0
    hotspot = 0

    if mech == "global_root":
        hotspot = 1
        if timing != "before_acquire":
            blocked = True
            false_exclusion = disjoint
        if parent_supersede and timing in ("after_first", "after_all_before_commit") and not parent_fence:
            unsafe = True

    elif mech == "ancestor_only":
        hotspot = 1 if auth_node(A) == "ROOT" else 0
        if timing != "before_acquire":
            if auth_node(A) == auth_node(B):
                blocked = True
                false_exclusion = disjoint
            elif overlap:
                unsafe = True
        if parent_supersede and timing in ("after_first", "after_all_before_commit") and not parent_fence:
            unsafe = True

    elif mech == "ordered_weak":
        hotspot = 1 if 0 in A else 0
        if timing == "after_first" and len(A) > 1:
            first = min(A)
            if overlap and not (B & {first}) and bool(B & (A - {first})):
                unsafe = True
        elif timing in ("after_all_before_commit", "after_commit") and overlap:
            blocked = True
        if same_gen_expiry and timing == "after_all_before_commit" and overlap:
            unsafe = True
            blocked = False
        if parent_supersede and timing in ("after_first", "after_all_before_commit") and not parent_fence:
            unsafe = True
        if not canonical_order and len(A) > 1 and len(B) > 1 and len(A & B) >= 2:
            deadlock = 1

    elif mech == "ordered_strong":
        hotspot = 1 if 0 in A else 0
        if timing == "after_first":
            first = min(A)
            if first in B:
                blocked = True
        elif timing in ("after_all_before_commit", "after_commit") and overlap:
            blocked = True
        if same_gen_expiry and timing == "after_all_before_commit" and overlap:
            unsafe = True
            blocked = False
        if parent_supersede and timing in ("after_first", "after_all_before_commit") and not parent_fence:
            unsafe = True
        if not canonical_order and len(A) > 1 and len(B) > 1 and len(A & B) >= 2:
            deadlock = 1

    elif mech == "interval_lock":
        hotspot = 1
        if timing != "before_acquire" and overlap:
            blocked = True
        if parent_supersede and timing in ("after_first", "after_all_before_commit") and not parent_fence:
            unsafe = True

    elif mech == "staging_integrator":
        hotspot = 1
        if timing != "before_acquire" and overlap:
            staged_waste = 1
            if registry_complete:
                blocked = True
            else:
                unsafe = True
        if parent_supersede and timing in ("after_first", "after_all_before_commit") and not parent_fence:
            unsafe = True

    proof_width = len(A) if mech in ("ordered_weak", "ordered_strong") else (1 if mech != "staging_integrator" or registry_complete else 0)
    return {
        "overlap": int(overlap),
        "blocked": int(blocked),
        "unsafe": int(unsafe),
        "false_exclusion": int(false_exclusion),
        "deadlock": int(deadlock),
        "staged_waste": int(staged_waste),
        "hotspot": int(hotspot),
        "grant": int(not blocked),
        "proof_width": proof_width,
    }


def concurrency_rows():
    rows = []
    for an, A in CLAIMS.items():
        for bn, B in CLAIMS.items():
            for timing in TIMINGS:
                for flags in product([False, True], repeat=5):
                    parent_supersede, parent_fence, same_gen_expiry, canonical_order, registry_complete = flags
                    for mech in MECHANISMS:
                        rows.append({
                            "A": an,
                            "B": bn,
                            "timing": timing,
                            "parent_supersede": parent_supersede,
                            "parent_fence": parent_fence,
                            "same_gen_expiry": same_gen_expiry,
                            "canonical_order": canonical_order,
                            "registry_complete": registry_complete,
                            "mech": mech,
                            **evaluate(mech, A, B, timing, *flags),
                        })
    return rows


def recovery_rows():
    crashes = ["none", "after_intent", "after_first", "after_all"]
    interruptions = ["none", "response_loss_first", "response_loss_last", "rate_limit_after_first"]
    rows = []
    for an, A in CLAIMS.items():
        for crash in crashes:
            for interruption in interruptions:
                for durable_intent, deterministic_id in product([False, True], repeat=2):
                    orphan = 0
                    self_conflict = 0
                    safe_checkpoint = 0
                    resumable = 0
                    if crash in ("after_first", "after_all"):
                        if durable_intent:
                            resumable = 1
                        else:
                            orphan = 1
                    elif crash == "after_intent" and durable_intent:
                        resumable = 1
                    if interruption in ("response_loss_first", "response_loss_last"):
                        if deterministic_id:
                            resumable = 1
                        else:
                            self_conflict = 1
                    if interruption == "rate_limit_after_first":
                        safe_checkpoint = 1
                        if durable_intent and deterministic_id:
                            resumable = 1
                        elif not durable_intent:
                            orphan = 1
                    rows.append({
                        "A": an,
                        "width": len(A),
                        "crash": crash,
                        "interruption": interruption,
                        "durable_intent": durable_intent,
                        "deterministic_id": deterministic_id,
                        "orphan": orphan,
                        "self_conflict": self_conflict,
                        "safe_checkpoint": safe_checkpoint,
                        "resumable": resumable,
                    })
    return rows


def aggregate(rows):
    out = {}
    for mech in MECHANISMS:
        x = [r for r in rows if r["mech"] == mech]
        out[mech] = {
            "n": len(x),
            "unsafe": sum(r["unsafe"] for r in x),
            "false_exclusion": sum(r["false_exclusion"] for r in x),
            "blocked": sum(r["blocked"] for r in x),
            "grants": sum(r["grant"] for r in x),
            "deadlock": sum(r["deadlock"] for r in x),
            "hotspot": sum(r["hotspot"] for r in x),
            "staged_waste": sum(r["staged_waste"] for r in x),
            "mean_proof_width": sum(r["proof_width"] for r in x) / len(x),
        }
    return out


def main():
    c = concurrency_rows()
    r = recovery_rows()
    strong = [x for x in c if x["parent_fence"] and not x["same_gen_expiry"] and x["canonical_order"] and x["registry_complete"]]
    print(json.dumps({
        "concurrency_scenario_count": len(c) // len(MECHANISMS),
        "concurrency_strategy_evaluations": len(c),
        "recovery_scenario_count": len(r),
        "common_strong_concurrency_slice": aggregate(strong),
        "note": "Equal-weight finite synthetic mechanism counts; not production rates."
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
