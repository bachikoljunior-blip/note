#!/usr/bin/env python3
"""Finite stress model for Phase-1 multi_agent Part 31.

Equal-weight synthetic mechanism lattice; counts are not production rates.
No network or external service is required to execute this script.
"""
from itertools import product
from collections import defaultdict
import json

CLAIMS = {
    "L0": {0},
    "L1": {1},
    "L2": {2},
    "L3": {3},
    "SPAN01": {0, 1},
    "SPAN12": {1, 2},
}

EVENTS = []
for i in range(4):
    EVENTS.append((f"content_L{i}", {i}, "content", True))
for i in range(4):
    EVENTS.append((f"split_topology_L{i}", {i}, "topology", False))
for i in range(4):
    EVENTS.append((f"split_conflict_L{i}", {i}, "topology", True))
for a, b in [(0, 1), (1, 2), (2, 3)]:
    EVENTS.append((f"merge_topology_L{a}L{b}", {a, b}, "topology", False))
for a, b in [(0, 1), (1, 2), (2, 3)]:
    EVENTS.append((f"merge_conflict_L{a}L{b}", {a, b}, "topology", True))

MECHANISMS = [
    "global_root",
    "fixed_partition",
    "adaptive_lineage",
    "root_leaf",
    "interval_lock",
    "staging_integrator",
]

def evaluate(mech, claim_set, event_set, event_class, changes_truth, timing,
             root_visible, lineage_invalidation, tombstone, multi_atomic,
             registry_complete, durable_id, response_loss, takeover):
    width = len(claim_set)
    overlap = bool(claim_set & event_set)
    semantic_conflict = overlap and changes_truth
    after = timing == "after_check"
    blocked = False
    unsafe = False
    proof_width = 0
    hotspot_touch = 0
    staged_waste = 0

    if mech == "global_root":
        proof_width = 1
        hotspot_touch = 1
        if after and root_visible:
            blocked = True
        if after and semantic_conflict and not root_visible:
            unsafe = True

    elif mech == "fixed_partition":
        proof_width = width
        hotspot_touch = 1 if 0 in claim_set else 0
        if after and semantic_conflict:
            if width == 1 or multi_atomic:
                blocked = True
            else:
                unsafe = True

    elif mech == "adaptive_lineage":
        proof_width = width
        hotspot_touch = 1 if 0 in claim_set else 0
        if after:
            if event_class == "content":
                if semantic_conflict:
                    if width == 1 or multi_atomic:
                        blocked = True
                    else:
                        unsafe = True
            else:
                topo_fenced = lineage_invalidation and tombstone
                if overlap and topo_fenced:
                    if width == 1 or multi_atomic:
                        blocked = True
                    elif changes_truth:
                        unsafe = True
                elif semantic_conflict and not topo_fenced:
                    unsafe = True

    elif mech == "root_leaf":
        proof_width = width + 1
        hotspot_touch = 1
        if after:
            if event_class == "content":
                if semantic_conflict:
                    if width == 1 or multi_atomic:
                        blocked = True
                    else:
                        unsafe = True
            else:
                if root_visible:
                    blocked = True
                elif semantic_conflict:
                    unsafe = True

    elif mech == "interval_lock":
        proof_width = 1
        hotspot_touch = 1
        if after and semantic_conflict:
            blocked = True

    elif mech == "staging_integrator":
        proof_width = 1 if registry_complete else 0
        hotspot_touch = 1
        if after and semantic_conflict:
            staged_waste = 1
            if registry_complete:
                blocked = True
            else:
                unsafe = True

    grant = not blocked
    false_exclusion = blocked and not semantic_conflict
    ambiguous = (response_loss or takeover) and grant
    duplicate_retry = ambiguous and not durable_id
    recovery_reads = 0
    if ambiguous and durable_id:
        recovery_reads = {
            "global_root": 1,
            "fixed_partition": width,
            "adaptive_lineage": width,
            "root_leaf": width + 1,
            "interval_lock": 1,
            "staging_integrator": 2,
        }[mech]

    return {
        "blocked": int(blocked),
        "unsafe": int(unsafe),
        "false_exclusion": int(false_exclusion),
        "grant": int(grant),
        "proof_width": proof_width,
        "hotspot_touch": hotspot_touch,
        "staged_waste": staged_waste,
        "duplicate_retry": int(duplicate_retry),
        "recovery_reads": recovery_reads,
        "semantic_conflict": int(semantic_conflict),
        "overlap": int(overlap),
        "after": int(after),
    }

def build_rows():
    rows = []
    for cname, cset in CLAIMS.items():
        for ename, eset, eclass, truth in EVENTS:
            for timing in ["before_check", "after_check"]:
                for flags in product([False, True], repeat=8):
                    (root_visible, lineage_invalidation, tombstone, multi_atomic,
                     registry_complete, durable_id, response_loss, takeover) = flags
                    base = {
                        "claim": cname,
                        "event": ename,
                        "event_class": eclass,
                        "changes_truth": truth,
                        "timing": timing,
                        "root_visible": root_visible,
                        "lineage_invalidation": lineage_invalidation,
                        "tombstone": tombstone,
                        "multi_atomic": multi_atomic,
                        "registry_complete": registry_complete,
                        "durable_id": durable_id,
                        "response_loss": response_loss,
                        "takeover": takeover,
                    }
                    for mech in MECHANISMS:
                        rows.append({**base, "mech": mech, **evaluate(
                            mech, cset, eset, eclass, truth, timing, *flags
                        )})
    return rows

def subset(rows, **conds):
    out = []
    for r in rows:
        ok = True
        for key, val in conds.items():
            if r[key] != val:
                ok = False
                break
        if ok:
            out.append(r)
    return out

def aggregate(rows):
    by = {}
    for mech in MECHANISMS:
        x = [r for r in rows if r["mech"] == mech]
        by[mech] = {
            "n": len(x),
            "unsafe": sum(r["unsafe"] for r in x),
            "false_exclusion": sum(r["false_exclusion"] for r in x),
            "blocked": sum(r["blocked"] for r in x),
            "grants": sum(r["grant"] for r in x),
            "duplicate_retry": sum(r["duplicate_retry"] for r in x),
            "mean_proof_width": sum(r["proof_width"] for r in x) / len(x),
            "hotspot_touch": sum(r["hotspot_touch"] for r in x),
            "staged_waste": sum(r["staged_waste"] for r in x),
            "recovery_reads": sum(r["recovery_reads"] for r in x),
        }
    return by

def main():
    rows = build_rows()
    scenario_count = len(rows) // len(MECHANISMS)

    common = subset(
        rows,
        root_visible=True,
        lineage_invalidation=True,
        tombstone=True,
        multi_atomic=True,
        registry_complete=True,
        durable_id=True,
        response_loss=False,
        takeover=False,
    )

    result = {
        "schema_version": 1,
        "scenario_count": scenario_count,
        "strategy_evaluations": len(rows),
        "common_strong_semantic_slice": aggregate(common),
        "negative_controls": {},
        "note": "Equal-weight finite synthetic mechanism counts; not production rates.",
    }

    neg = {}
    neg["adaptive_topology_conflict_after_check"] = {}
    for lin, tomb in [(True, True), (True, False), (False, True), (False, False)]:
        x = subset(rows, mech="adaptive_lineage", root_visible=True,
                   registry_complete=True, durable_id=True,
                   response_loss=False, takeover=False, multi_atomic=True,
                   timing="after_check", event_class="topology",
                   lineage_invalidation=lin, tombstone=tomb)
        x = [r for r in x if r["semantic_conflict"]]
        neg["adaptive_topology_conflict_after_check"][f"lineage_{lin}_tombstone_{tomb}"] = {
            "n": len(x),
            "unsafe": sum(r["unsafe"] for r in x),
            "blocked": sum(r["blocked"] for r in x),
        }

    neg["fixed_partition_spanning_conflict_after_check"] = {}
    for atom in [True, False]:
        x = subset(rows, mech="fixed_partition", root_visible=True,
                   lineage_invalidation=True, tombstone=True,
                   registry_complete=True, durable_id=True,
                   response_loss=False, takeover=False, multi_atomic=atom,
                   timing="after_check")
        x = [r for r in x if r["semantic_conflict"] and r["proof_width"] > 1]
        neg["fixed_partition_spanning_conflict_after_check"][f"multi_atomic_{atom}"] = {
            "n": len(x),
            "unsafe": sum(r["unsafe"] for r in x),
            "blocked": sum(r["blocked"] for r in x),
        }

    neg["root_leaf_topology_conflict_after_check"] = {}
    for visible in [True, False]:
        x = subset(rows, mech="root_leaf", root_visible=visible,
                   lineage_invalidation=True, tombstone=True,
                   multi_atomic=True, registry_complete=True, durable_id=True,
                   response_loss=False, takeover=False,
                   timing="after_check", event_class="topology")
        x = [r for r in x if r["semantic_conflict"]]
        neg["root_leaf_topology_conflict_after_check"][f"root_visible_{visible}"] = {
            "n": len(x),
            "unsafe": sum(r["unsafe"] for r in x),
            "blocked": sum(r["blocked"] for r in x),
        }

    neg["staging_conflict_after_check"] = {}
    for complete in [True, False]:
        x = subset(rows, mech="staging_integrator", root_visible=True,
                   lineage_invalidation=True, tombstone=True, multi_atomic=True,
                   registry_complete=complete, durable_id=True,
                   response_loss=False, takeover=False, timing="after_check")
        x = [r for r in x if r["semantic_conflict"]]
        neg["staging_conflict_after_check"][f"registry_complete_{complete}"] = {
            "n": len(x),
            "unsafe": sum(r["unsafe"] for r in x),
            "blocked": sum(r["blocked"] for r in x),
            "staged_waste": sum(r["staged_waste"] for r in x),
        }

    neg["after_check_nonconflict_false_exclusion"] = {}
    for mech in MECHANISMS:
        x = [r for r in common if r["mech"] == mech
             and r["timing"] == "after_check" and not r["semantic_conflict"]]
        neg["after_check_nonconflict_false_exclusion"][mech] = {
            "n": len(x),
            "false_exclusion": sum(r["false_exclusion"] for r in x),
        }

    neg["response_loss_without_durable_transition_id"] = {}
    for mech in MECHANISMS:
        neg["response_loss_without_durable_transition_id"][mech] = {}
        for did in [True, False]:
            x = subset(rows, mech=mech, root_visible=True,
                       lineage_invalidation=True, tombstone=True,
                       multi_atomic=True, registry_complete=True,
                       durable_id=did, response_loss=True, takeover=False)
            neg["response_loss_without_durable_transition_id"][mech][f"durable_id_{did}"] = {
                "n": len(x),
                "grants": sum(r["grant"] for r in x),
                "duplicate_retry_possible": sum(r["duplicate_retry"] for r in x),
                "recovery_reads": sum(r["recovery_reads"] for r in x),
            }

    result["negative_controls"] = neg
    print(json.dumps(result, indent=2, sort_keys=True))

if __name__ == "__main__":
    main()
