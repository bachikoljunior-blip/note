from itertools import product
from collections import Counter
import json

NODES = (0, 1, 2)
EDGE_NODES = {"AB": (0, 1), "BC": (1, 2)}
PLAN_GRAPHS = [
    frozenset(),
    frozenset({"AB"}),
    frozenset({"BC"}),
    frozenset({"AB", "BC"}),
]
BOOL = [False, True]
VER_MODES = ["BOTH", "LEFT_ONLY", "RIGHT_ONLY", "NONE"]
ORIGINS = ["EDGE_WRITE", "CONTRACT_DRIFT"]

def components(edges):
    adj = {i: set() for i in NODES}
    for e in edges:
        a, b = EDGE_NODES[e]
        adj[a].add(b)
        adj[b].add(a)
    seen = set()
    out = []
    for n in NODES:
        if n in seen:
            continue
        stack = [n]
        comp = set()
        while stack:
            x = stack.pop()
            if x in seen:
                continue
            seen.add(x)
            comp.add(x)
            stack.extend(adj[x] - seen)
        out.append(frozenset(comp))
    return out

def toggle(edges, edge):
    out = set(edges)
    if edge in out:
        out.remove(edge)
    else:
        out.add(edge)
    return frozenset(out)

def scenarios():
    rows = []
    for plan in PLAN_GRAPHS:
        # No-mutation controls; irrelevant fields normalized.
        for retired_mask, takeover, response_loss, transfer in product(range(1, 8), BOOL, BOOL, BOOL):
            rows.append({
                "plan": sorted(plan),
                "mutation": "NONE",
                "origin": "NONE",
                "epoch_visible": False,
                "epoch_covers_contract": False,
                "ver_mode": "NONE",
                "retired_mask": retired_mask,
                "takeover": takeover,
                "response_loss": response_loss,
                "transfer": transfer,
            })
        for edge, origin, epoch_visible, epoch_covers_contract, ver_mode, retired_mask, takeover, response_loss, transfer in product(
            EDGE_NODES, ORIGINS, BOOL, BOOL, VER_MODES, range(1, 8), BOOL, BOOL, BOOL
        ):
            rows.append({
                "plan": sorted(plan),
                "mutation": edge,
                "origin": origin,
                "epoch_visible": epoch_visible,
                "epoch_covers_contract": epoch_covers_contract,
                "ver_mode": ver_mode,
                "retired_mask": retired_mask,
                "takeover": takeover,
                "response_loss": response_loss,
                "transfer": transfer,
            })
    return rows

def plan_edges(s):
    return frozenset(s["plan"])

def current_edges(s):
    p = plan_edges(s)
    return p if s["mutation"] == "NONE" else toggle(p, s["mutation"])

def retired_set(s):
    return {i for i in NODES if s["retired_mask"] & (1 << i)}

def epoch_changed(s):
    if s["mutation"] == "NONE":
        return False
    if s["origin"] == "EDGE_WRITE":
        return s["epoch_visible"]
    if s["origin"] == "CONTRACT_DRIFT":
        return s["epoch_visible"] and s["epoch_covers_contract"]
    return False

def version_changed_nodes(s):
    if s["mutation"] == "NONE":
        return set()
    a, b = EDGE_NODES[s["mutation"]]
    if s["ver_mode"] == "BOTH":
        return {a, b}
    if s["ver_mode"] == "LEFT_ONLY":
        return {a}
    if s["ver_mode"] == "RIGHT_ONLY":
        return {b}
    return set()

def unsafe_mixed(activated, edges):
    for e in edges:
        a, b = EDGE_NODES[e]
        if (a in activated) ^ (b in activated):
            return True
    return False

def activate_components(edges, retired, blocked_nodes=None):
    blocked_nodes = blocked_nodes or set()
    out = set()
    for comp in components(edges):
        if comp & blocked_nodes:
            continue
        if comp <= retired:
            out |= set(comp)
    return out

def evaluate(s, strategy):
    p = plan_edges(s)
    c = current_edges(s)
    retired = retired_set(s)
    duplicate = False

    if strategy == "stale_plan_component":
        activated = activate_components(p, retired)
        duplicate = bool(activated and (s["takeover"] or s["response_loss"]))

    elif strategy == "per_resource_no_epoch":
        activated = set(retired)
        duplicate = bool(activated and (s["takeover"] or s["response_loss"]))

    elif strategy == "precheck_epoch_only":
        # Grammar places mutation after the precheck and before activation.
        activated = activate_components(p, retired)
        duplicate = bool(activated and (s["takeover"] or s["response_loss"]))

    elif strategy == "global_epoch_activation_recheck":
        activated = set() if epoch_changed(s) else activate_components(p, retired)

    elif strategy == "per_effect_version_recheck":
        activated = activate_components(p, retired, version_changed_nodes(s))

    elif strategy == "vector_barrier":
        activated = set(NODES) if retired == set(NODES) else set()

    elif strategy == "atomic_current_component_transfer":
        activated = activate_components(c, retired) if s["transfer"] else set()

    else:
        raise ValueError(strategy)

    return {
        "unsafe": unsafe_mixed(activated, c),
        "duplicate": duplicate,
        "terminal": activated == set(NODES),
        "progress": len(activated),
    }

def summarize(rows, strategy):
    out = Counter()
    for s in rows:
        r = evaluate(s, strategy)
        out["unsafe"] += int(r["unsafe"])
        out["duplicate"] += int(r["duplicate"])
        out["terminal"] += int(r["terminal"])
        out["progress_units"] += r["progress"]
    return dict(out)

def is_add(s):
    return s["mutation"] != "NONE" and s["mutation"] not in plan_edges(s)

def is_remove(s):
    return s["mutation"] != "NONE" and s["mutation"] in plan_edges(s)

def agg(rows, strategy):
    return summarize(rows, strategy)

def main():
    rows = scenarios()
    strategies = [
        "stale_plan_component",
        "per_resource_no_epoch",
        "precheck_epoch_only",
        "global_epoch_activation_recheck",
        "per_effect_version_recheck",
        "vector_barrier",
        "atomic_current_component_transfer",
    ]
    result = {
        "schema_version": 1,
        "scenario_count": len(rows),
        "interpretation": {
            "scope": "Three-resource finite synthetic graph-drift lattice over AB/BC coupling edges; counts are not production failure rates.",
            "safety_definition": "No current coupling edge may connect one activated g2 resource to one not-yet-activated resource.",
        },
        "strategies": {st: summarize(rows, st) for st in strategies},
        "slices": {},
    }

    add_hazard = [
        s for s in rows
        if is_add(s) and evaluate(s, "stale_plan_component")["unsafe"]
    ]
    strong_epoch = [
        s for s in rows
        if s["mutation"] == "NONE" or epoch_changed(s)
    ]
    lagged_edge = [
        s for s in rows
        if s["origin"] == "EDGE_WRITE" and s["mutation"] != "NONE" and not s["epoch_visible"]
    ]
    uncovered_contract = [
        s for s in rows
        if s["origin"] == "CONTRACT_DRIFT" and s["mutation"] != "NONE" and not s["epoch_covers_contract"]
    ]
    strong_versions = [
        s for s in rows
        if s["mutation"] == "NONE" or s["ver_mode"] == "BOTH"
    ]
    partial_versions = [
        s for s in rows
        if s["mutation"] != "NONE" and s["ver_mode"] != "BOTH"
    ]
    removal_strong_epoch = [
        s for s in rows if is_remove(s) and epoch_changed(s)
    ]
    removal_strong_versions = [
        s for s in rows if is_remove(s) and s["ver_mode"] == "BOTH"
    ]
    removal_transfer = [
        s for s in rows if is_remove(s) and s["transfer"]
    ]

    result["slices"] = {
        "edge_addition_stale_plan_hazard": {
            "count": len(add_hazard),
            "stale_plan_unsafe": agg(add_hazard, "stale_plan_component")["unsafe"],
            "vector_unsafe": agg(add_hazard, "vector_barrier")["unsafe"],
            "atomic_transfer_unsafe": agg(add_hazard, "atomic_current_component_transfer")["unsafe"],
        },
        "global_epoch_strong_authority_slice": {
            "count": len(strong_epoch),
            "unsafe": agg(strong_epoch, "global_epoch_activation_recheck")["unsafe"],
        },
        "global_epoch_lagged_edge_write": {
            "count": len(lagged_edge),
            "unsafe": agg(lagged_edge, "global_epoch_activation_recheck")["unsafe"],
        },
        "graph_epoch_does_not_cover_contract_drift": {
            "count": len(uncovered_contract),
            "unsafe": agg(uncovered_contract, "global_epoch_activation_recheck")["unsafe"],
        },
        "per_effect_versions_both_endpoints_atomic": {
            "count": len(strong_versions),
            "unsafe": agg(strong_versions, "per_effect_version_recheck")["unsafe"],
        },
        "per_effect_versions_partial_or_missing": {
            "count": len(partial_versions),
            "unsafe": agg(partial_versions, "per_effect_version_recheck")["unsafe"],
        },
        "edge_removal_liveness": {
            "global_strong_count": len(removal_strong_epoch),
            "global_strong_progress_units": agg(removal_strong_epoch, "global_epoch_activation_recheck")["progress_units"],
            "per_effect_strong_count": len(removal_strong_versions),
            "per_effect_strong_progress_units": agg(removal_strong_versions, "per_effect_version_recheck")["progress_units"],
            "atomic_transfer_count": len(removal_transfer),
            "atomic_transfer_progress_units": agg(removal_transfer, "atomic_current_component_transfer")["progress_units"],
        },
    }

    assert result["slices"]["global_epoch_strong_authority_slice"]["unsafe"] == 0
    assert result["slices"]["per_effect_versions_both_endpoints_atomic"]["unsafe"] == 0
    assert result["strategies"]["vector_barrier"]["unsafe"] == 0
    assert result["strategies"]["atomic_current_component_transfer"]["unsafe"] == 0
    assert result["slices"]["edge_addition_stale_plan_hazard"]["stale_plan_unsafe"] == len(add_hazard)

    print(json.dumps(result, indent=2, sort_keys=True))

if __name__ == "__main__":
    main()
