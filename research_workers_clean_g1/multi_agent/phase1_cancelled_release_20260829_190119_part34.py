#!/usr/bin/env python3
"""Phase-1 multi_agent Part 34 finite model.

Cancellation tombstone vs eager/per-cell cleanup after a reservation has won
GRANTED -> CANCELLED. Equal-weight synthetic counts; not production rates.
No network required.
"""
from itertools import product
import json

CLAIMS = {
    "L0": {0}, "L1": {1}, "L2": {2},
    "SPAN01": {0, 1}, "SPAN12": {1, 2}, "SPAN012": {0, 1, 2},
}
RELEASE_STATES = ["none", "partial", "full"]
TOMBSTONE_STATES = ["CURRENT_CANCELLED", "MISSING", "ROLLED_BACK_GRANTED"]
MECHANISMS = [
    "block_stale", "eager_release", "per_cell_cancel",
    "lazy_tombstone", "missing_is_free", "staging_integrator",
]


def released_cells(state):
    if state == "none": return set()
    if state == "partial": return {0}
    return {0, 1, 2}


def evaluate(mech, claimset, release, tomb, aba, incarnation_sensitive,
             late_old, registry_complete):
    released = released_cells(release)
    stale = set(claimset) - released
    unsafe = progress = blocked = false_block = reclaim_reads = old_effect = 0

    if mech == "block_stale":
        if stale:
            blocked = false_block = 1
        else:
            progress = 1
        if tomb == "ROLLED_BACK_GRANTED" and late_old:
            unsafe = old_effect = 1

    elif mech == "eager_release":
        if stale:
            blocked = false_block = 1
        else:
            progress = 1
        if tomb == "ROLLED_BACK_GRANTED" and late_old:
            unsafe = old_effect = 1
        if aba and not incarnation_sensitive and released & set(claimset):
            unsafe = 1

    elif mech == "per_cell_cancel":
        marked = released
        if set(claimset).issubset(marked):
            progress = 1
        else:
            blocked = false_block = 1
        if tomb == "ROLLED_BACK_GRANTED" and late_old and not incarnation_sensitive:
            unsafe = old_effect = 1
        if aba and not incarnation_sensitive and marked & set(claimset):
            unsafe = 1

    elif mech == "lazy_tombstone":
        reclaim_reads = len(stale)
        if tomb == "CURRENT_CANCELLED":
            progress = 1
            if aba and not incarnation_sensitive:
                unsafe = 1
        elif tomb == "MISSING":
            blocked = false_block = 1
        else:
            blocked = 1
            if late_old:
                unsafe = old_effect = 1

    elif mech == "missing_is_free":
        reclaim_reads = len(stale)
        if tomb in ("CURRENT_CANCELLED", "MISSING"):
            progress = 1
            if tomb == "MISSING" and stale:
                unsafe = 1
            if aba and not incarnation_sensitive:
                unsafe = 1
        else:
            blocked = 1
            if late_old:
                unsafe = old_effect = 1

    elif mech == "staging_integrator":
        reclaim_reads = 1
        if registry_complete:
            if tomb == "CURRENT_CANCELLED":
                progress = 1
            else:
                blocked = 1
                false_block = int(tomb == "MISSING")
                if tomb == "ROLLED_BACK_GRANTED" and late_old:
                    unsafe = old_effect = 1
        else:
            progress = 1
            if tomb != "CURRENT_CANCELLED" or (aba and not incarnation_sensitive):
                unsafe = 1

    return {
        "unsafe": unsafe, "progress": progress, "blocked": blocked,
        "false_block": false_block, "reclaim_reads": reclaim_reads,
        "old_effect": old_effect,
    }


def build_rows():
    rows = []
    for cname, cset in CLAIMS.items():
        for vals in product(
            RELEASE_STATES, TOMBSTONE_STATES,
            [False, True], [False, True], [False, True], [False, True]
        ):
            release, tomb, aba, incarnation_sensitive, late_old, registry_complete = vals
            for mech in MECHANISMS:
                rows.append({
                    "claim": cname, "release": release, "tomb": tomb,
                    "aba": aba, "incarnation_sensitive": incarnation_sensitive,
                    "late_old": late_old, "registry_complete": registry_complete,
                    "mech": mech,
                    **evaluate(mech, cset, *vals),
                })
    return rows


def recovery_rows():
    rows = []
    for release, interruption, durable_tombstone, deterministic_new_id, stale_exists in product(
        RELEASE_STATES, ["crash", "response_loss", "rate_limit"],
        [False, True], [False, True], [False, True]
    ):
        resumable = orphan = self_conflict = checkpoint = 0
        if interruption == "rate_limit": checkpoint = 1
        if stale_exists:
            if not durable_tombstone:
                orphan = 1
            elif interruption == "response_loss" and not deterministic_new_id:
                self_conflict = 1
            elif deterministic_new_id:
                resumable = 1
            else:
                self_conflict = 1
        else:
            resumable = 1
        rows.append({
            "release": release, "interruption": interruption,
            "durable_tombstone": durable_tombstone,
            "deterministic_new_id": deterministic_new_id,
            "stale_exists": stale_exists,
            "resumable": resumable, "orphan": orphan,
            "self_conflict": self_conflict, "checkpoint": checkpoint,
        })
    return rows


def aggregate(rows):
    out = {}
    for mech in MECHANISMS:
        x = [r for r in rows if r["mech"] == mech]
        out[mech] = {"n": len(x)}
        for k in ["unsafe", "progress", "blocked", "false_block", "reclaim_reads", "old_effect"]:
            out[mech][k] = sum(r[k] for r in x)
    return out


def main():
    rows = build_rows()
    recovery = recovery_rows()
    strong = [r for r in rows if r["tomb"] == "CURRENT_CANCELLED" and r["incarnation_sensitive"] and r["registry_complete"]]
    print(json.dumps({
        "scenario_count": len(rows) // len(MECHANISMS),
        "strategy_evaluations": len(rows),
        "recovery_scenario_count": len(recovery),
        "current_tombstone_strong_slice": aggregate(strong),
        "note": "Equal-weight finite synthetic mechanism counts; not production rates."
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
