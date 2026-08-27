#!/usr/bin/env python3
"""Deterministic mechanism study for rollback provenance complementarity.

Scope: synthetic DAG mechanism study only. Numbers are not deployment thresholds.
All randomness is seeded from SHA-256; Python's process-local hash() is never used.
"""

import hashlib
import numpy as np

SURFACES = [
    "handoff", "shared_memory", "conditional_routing",
    "dynamic_tool", "reducer", "custom_wrapper",
]
SURFACE_P = np.array([0.22, 0.18, 0.18, 0.14, 0.16, 0.12])
RUNTIME_RECALL = {
    "handoff": 0.99,
    "shared_memory": 0.95,
    "conditional_routing": 0.78,
    "dynamic_tool": 0.62,
    "reducer": 0.98,
    "custom_wrapper": 0.45,
}
G = 1800
N = 28


def seed_int(*parts):
    b = "|".join(map(str, parts)).encode()
    return int.from_bytes(hashlib.sha256(b).digest()[:8], "big") % (2**63 - 1)


def descendants(n, edges, source):
    adj = [[] for _ in range(n)]
    for e in edges:
        adj[e[0]].append(e[1])
    seen, stack = set(), [source]
    while stack:
        x = stack.pop()
        for y in adj[x]:
            if y not in seen:
                seen.add(y)
                stack.append(y)
    return seen


def gen_graph(gid, n=N, edge_p=0.11):
    rng = np.random.default_rng(seed_int("dag", gid))
    edges = []
    for i in range(n):
        for j in range(i + 1, n):
            p = edge_p * (1.4 if j - i <= 4 else 0.75)
            if rng.random() < p:
                edges.append((i, j, str(rng.choice(SURFACES, p=SURFACE_P))))
    for i in range(0, n - 1, 4):
        j = min(n - 1, i + 1)
        if not any(a == i and b == j for a, b, _ in edges):
            edges.append((i, j, str(rng.choice(SURFACES, p=SURFACE_P))))
    candidates = [i for i in range(n - 1) if descendants(n, edges, i)]
    source = int(rng.choice(candidates))
    true_desc = descendants(n, edges, source)
    rr = np.random.default_rng(seed_int("runtime", gid))
    runtime = [e for e in edges if rr.random() < RUNTIME_RECALL[e[2]]]
    true_pairs = {(a, b) for a, b, _ in edges}
    nonedges = [
        (a, b) for a in range(n) for b in range(a + 1, n)
        if (a, b) not in true_pairs
    ]
    return gid, n, edges, source, true_desc, runtime, nonedges


GRAPHS = [gen_graph(g) for g in range(G)]
RT_RATE = sum(len(g[5]) for g in GRAPHS) / sum(len(g[2]) for g in GRAPHS)


def static_conditional(n, edges, runtime, nonedges, gid, target, q_miss, fp):
    # q_miss = P(static captures edge | runtime missed it).
    # p_hit is solved so marginal static recall remains approximately target.
    p_hit = (target - (1 - RT_RATE) * q_miss) / RT_RATE
    p_hit = min(1.0, max(0.0, p_hit))
    rt_pairs = {(a, b) for a, b, _ in runtime}
    rng = np.random.default_rng(seed_int("static", gid, target, q_miss, fp))
    out = []
    for e in edges:
        p = p_hit if (e[0], e[1]) in rt_pairs else q_miss
        if rng.random() < p:
            out.append(e)
    mask = rng.random(len(nonedges)) < fp
    out.extend((a, b, "static_fp") for (a, b), m in zip(nonedges, mask) if m)
    return out, p_hit


def eval_union(target, q_miss, fp):
    recovered = total_cost = true_captured = true_total = 0
    complement_hits = complement_total = missing_nodes = extra_nodes = 0
    p_hit_last = None
    for gid, n, edges, source, true_desc, runtime, nonedges in GRAPHS:
        static, p_hit = static_conditional(
            n, edges, runtime, nonedges, gid, target, q_miss, fp
        )
        p_hit_last = p_hit
        true_pairs = {(a, b) for a, b, _ in edges}
        rt_pairs = {(a, b) for a, b, _ in runtime}
        st_true = {(a, b) for a, b, s in static if s != "static_fp"}
        true_captured += len(st_true & true_pairs)
        true_total += len(true_pairs)
        rt_missed = true_pairs - rt_pairs
        complement_total += len(rt_missed)
        complement_hits += len(rt_missed & st_true)

        replay = descendants(n, runtime + static, source)
        missing = true_desc - replay
        extra = replay - true_desc
        recovered += int(not missing)
        total_cost += 1 + len(replay)
        missing_nodes += len(missing)
        extra_nodes += len(extra)
    return {
        "target": target,
        "q_miss": q_miss,
        "p_hit": p_hit_last,
        "fp": fp,
        "static_edge_recall": true_captured / true_total,
        "complement_on_runtime_miss": complement_hits / complement_total,
        "recovery": recovered / G,
        "mean_cost": total_cost / G,
        "correct_per_100k": recovered / total_cost * 100000,
        "mean_missing": missing_nodes / G,
        "mean_extra": extra_nodes / G,
    }


def eval_baseline(kind):
    recovered = total_cost = 0
    for gid, n, edges, source, true_desc, runtime, nonedges in GRAPHS:
        if kind == "local":
            replay = descendants(n, runtime, source)
        elif kind == "whole":
            replay = set(range(n))
            replay.discard(source)
        else:
            raise ValueError(kind)
        recovered += int(not (true_desc - replay))
        total_cost += 1 + len(replay)
    return {
        "recovery": recovered / G,
        "mean_cost": total_cost / G,
        "correct_per_100k": recovered / total_cost * 100000,
    }


if __name__ == "__main__":
    print("runtime marginal edge recall", RT_RATE)
    print("local", eval_baseline("local"))
    print("whole", eval_baseline("whole"))
    cases = [
        (0.90, 0.45), (0.90, 0.90), (0.90, 1.00),
        (0.95, 0.72), (0.95, 0.95), (0.95, 1.00),
        (0.98, 0.89), (0.98, 0.98), (0.98, 1.00),
    ]
    for fp in (0.02, 0.10):
        print("\nFP", fp)
        for target, q in cases:
            print(eval_union(target, q, fp))
