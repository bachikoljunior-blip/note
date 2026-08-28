#!/usr/bin/env python3
"""Finite synthetic replay-surface registry / witness-GC stress model.

Equal-weight mechanism lattice, not a production failure-rate estimate.
"""
from itertools import product
from collections import Counter
import json

EVENTS = [
    "none",
    "add_before", "add_after",
    "extend_before", "extend_after",
    "redrive_before", "redrive_after",
]
POLICIES = [
    "unversioned_max",
    "snapshot_digest",
    "epoch_fence_at_gc",
    "epoch_fence_retirement_barrier",
    "permanent_compact_witness",
]

def scenarios():
    for event, elapsed, clock_safe, latent, reuse, gc_race, action in product(
        EVENTS, [False, True], [False, True], [False, True],
        [False, True], [False, True], ["result", "effect"]
    ):
        before = event.endswith("_before")
        after = event.endswith("_after")
        drift = event != "none"
        yield {
            "event": event,
            "elapsed": elapsed,
            "clock_safe": clock_safe,
            "latent": latent,
            "reuse": reuse,
            "gc_race": gc_race,
            "action": action,
            "before": before,
            "after": after,
            "drift": drift,
            "quiescent_at_gc": elapsed and clock_safe and not before,
        }

def evaluate(s, policy):
    if policy == "unversioned_max":
        full_gc = s["elapsed"]
        uid_precondition = False
        retirement_barrier = False
        compact = False
    elif policy == "snapshot_digest":
        full_gc = s["elapsed"]
        uid_precondition = True
        retirement_barrier = False
        compact = False
    elif policy == "epoch_fence_at_gc":
        full_gc = s["elapsed"] and s["clock_safe"] and not s["before"]
        uid_precondition = True
        retirement_barrier = False
        compact = False
    elif policy == "epoch_fence_retirement_barrier":
        full_gc = s["elapsed"] and s["clock_safe"] and not s["before"]
        uid_precondition = True
        retirement_barrier = True
        compact = False
    elif policy == "permanent_compact_witness":
        full_gc = False
        uid_precondition = True
        retirement_barrier = True
        compact = True
    else:
        raise ValueError(policy)

    new_witness_delete = (
        full_gc and not uid_precondition and s["gc_race"] and s["reuse"]
    )
    false_quiescence_at_gc = full_gc and not s["quiescent_at_gc"]
    future_resurrection = full_gc and s["after"] and not retirement_barrier
    stale_after_gc = (
        full_gc
        and s["latent"]
        and (not s["quiescent_at_gc"] or future_resurrection)
    )
    unsafe = new_witness_delete or stale_after_gc

    bulky_reclaimed = full_gc or compact
    compact_retained = compact or (retirement_barrier and full_gc)
    full_witness_retained = not bulky_reclaimed
    safe_full_delete = full_gc and not unsafe

    return {
        "full_gc": full_gc,
        "false_quiescence_at_gc": false_quiescence_at_gc,
        "future_resurrection": future_resurrection,
        "stale_after_gc": stale_after_gc,
        "new_witness_delete": new_witness_delete,
        "unsafe": unsafe,
        "safe_full_delete": safe_full_delete,
        "bulky_reclaimed": bulky_reclaimed,
        "compact_retained": compact_retained,
        "full_witness_retained": full_witness_retained,
    }

def aggregate(rows):
    out = {}
    for p in POLICIES:
        c = Counter()
        for s in rows:
            for k, v in evaluate(s, p).items():
                if v:
                    c[k] += 1
        out[p] = dict(sorted(c.items()))
    return out

def subset(rows, pred):
    xs = [s for s in rows if pred(s)]
    return {"n": len(xs), "policies": aggregate(xs)}

def main():
    rows = list(scenarios())
    assert len(rows) == 448
    result = {
        "model": "dynamic_replay_surface_registry_witness_gc",
        "scenario_count": len(rows),
        "equal_weight_synthetic": True,
        "policies": aggregate(rows),
        "slices": {
            "after_gc_drift_elapsed_clock_safe_latent": subset(
                rows, lambda s: s["after"] and s["elapsed"] and s["clock_safe"] and s["latent"]
            ),
            "before_gc_drift_elapsed_clock_safe_latent": subset(
                rows, lambda s: s["before"] and s["elapsed"] and s["clock_safe"] and s["latent"]
            ),
            "no_drift_elapsed_clock_safe": subset(
                rows, lambda s: s["event"] == "none" and s["elapsed"] and s["clock_safe"]
            ),
            "unversioned_gc_aba_reusable": subset(
                rows, lambda s: s["elapsed"] and s["gc_race"] and s["reuse"]
            ),
            "clock_unsafe_elapsed_no_drift_latent": subset(
                rows, lambda s: s["event"] == "none" and s["elapsed"] and not s["clock_safe"] and s["latent"]
            ),
        },
    }
    p = result["policies"]
    assert p["unversioned_max"]["full_gc"] == 224
    assert p["unversioned_max"]["unsafe"] == 134
    assert p["unversioned_max"]["new_witness_delete"] == 56
    assert p["snapshot_digest"]["unsafe"] == 104
    assert p["epoch_fence_at_gc"]["full_gc"] == 64
    assert p["epoch_fence_at_gc"]["unsafe"] == 24
    assert p["epoch_fence_retirement_barrier"]["full_gc"] == 64
    assert p["epoch_fence_retirement_barrier"].get("unsafe", 0) == 0
    assert p["permanent_compact_witness"]["bulky_reclaimed"] == 448
    assert p["permanent_compact_witness"].get("unsafe", 0) == 0
    after = result["slices"]["after_gc_drift_elapsed_clock_safe_latent"]["policies"]
    assert after["epoch_fence_at_gc"]["unsafe"] == 24
    assert after["epoch_fence_retirement_barrier"].get("unsafe", 0) == 0
    print(json.dumps(result, indent=2, sort_keys=True))

if __name__ == "__main__":
    main()
