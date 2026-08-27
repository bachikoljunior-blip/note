#!/usr/bin/env python3
"""Preregistered incremental upper-Shapley boundary holdout.

Protocol:
  research_workers_clean_g1/reasoning/experiments/
  coalition_incremental_boundary_holdout_v0_protocol.json

For fixed player i in a monotone simple game, the exact upper-Shapley
completion depends on:
  * maximal observed zeroes on the upper b-slice v(T ∪ {i});
  * minimal observed ones on the lower a-slice v(T).

A new non-dominated boundary point replaces weaker antichain members, but its
new CNF clause subsumes the removed clauses. Therefore a persistent ROBDD can
be updated by conjoining only the new stronger clause; old physical nodes are
immutable and may remain shared. Cardinality polynomials are memoized per
immutable ROBDD node/level.

The holdout compares every effective incremental update against a full rebuild
from the current reduced boundary. Runtime results are implementation- and
environment-specific; correctness is the primary preregistered endpoint.
"""
import json
import math
import platform
import random
import statistics
import sys
import time

N_VALUES = [10, 14, 18]
SEEDS = [730001, 730019, 730043, 730079]
BUDGETS = {10: 500, 14: 900, 18: 1300}
PROTOCOL_BLOB = "39a53bdf7e5e1ff258b4473f39a07d36fa1d008d"

def reduce_maximal(masks):
    out = []
    for s in sorted(set(masks), key=lambda x: (-x.bit_count(), -x)):
        if any((s & ~t) == 0 for t in out):
            continue
        out.append(s)
    return out

def reduce_minimal(masks):
    out = []
    for s in sorted(set(masks), key=lambda x: (x.bit_count(), x)):
        if any((t & ~s) == 0 for t in out):
            continue
        out.append(s)
    return out

def update_maximal(boundary, z):
    if any((z & ~t) == 0 for t in boundary):
        return list(boundary), False
    return [t for t in boundary if not ((t & ~z) == 0)] + [z], True

def update_minimal(boundary, a):
    if any((t & ~a) == 0 for t in boundary):
        return list(boundary), False
    return [t for t in boundary if not ((a & ~t) == 0)] + [a], True

def gen_supports(n, rng, count):
    sizes = tuple(range(1, min(n, 6) + 1))
    supports = []
    tries = 0
    while len(supports) < count and tries < 10000:
        tries += 1
        k = rng.choice(sizes)
        mask = sum(1 << j for j in rng.sample(range(n), k))
        if any((t & ~mask) == 0 for t in supports):
            continue
        supports = [t for t in supports if not ((mask & ~t) == 0)]
        if mask not in supports:
            supports.append(mask)
    return supports

def value_support(mask, supports):
    return int(any((mask & s) == s for s in supports))

def localizer(n, player):
    others = [j for j in range(n) if j != player]
    loc = {j: k for k, j in enumerate(others)}
    def local(mask):
        z = 0
        for j in others:
            if mask & (1 << j):
                z |= 1 << loc[j]
        return z
    return local

class ROBDD:
    def __init__(self, m):
        self.m = m
        self.order = list(range(m))
        self.pos = {v: v for v in range(m)}
        self.nodes = [None, None]  # 0=false, 1=true
        self.unique = {}
        self.apply_cache = {}
        self.clause_cache = {}
        self.rank_cache = {}
        self.rank_cache_misses = 0

    def varpos(self, u):
        return self.m if u <= 1 else self.nodes[u][0]

    def mk(self, var, lo, hi):
        if lo == hi:
            return lo
        key = (var, lo, hi)
        if key in self.unique:
            return self.unique[key]
        u = len(self.nodes)
        self.nodes.append(key)
        self.unique[key] = u
        return u

    def clause(self, vars_set, positive):
        key = (tuple(sorted(vars_set)), positive)
        if key in self.clause_cache:
            return self.clause_cache[key]
        u = 0
        for v in sorted(vars_set, reverse=True):
            u = self.mk(v, u, 1) if positive else self.mk(v, 1, u)
        self.clause_cache[key] = u
        return u

    def and_(self, u, v):
        if u == 0 or v == 0:
            return 0
        if u == 1:
            return v
        if v == 1:
            return u
        if u == v:
            return u
        if u > v:
            u, v = v, u
        key = (u, v)
        if key in self.apply_cache:
            return self.apply_cache[key]
        p = min(self.varpos(u), self.varpos(v))
        if self.varpos(u) == p:
            _, ulo, uhi = self.nodes[u]
        else:
            ulo = uhi = u
        if self.varpos(v) == p:
            _, vlo, vhi = self.nodes[v]
        else:
            vlo = vhi = v
        out = self.mk(p, self.and_(ulo, vlo), self.and_(uhi, vhi))
        self.apply_cache[key] = out
        return out

    def _rank(self, u, level):
        key = (u, level)
        if key in self.rank_cache:
            return self.rank_cache[key]
        self.rank_cache_misses += 1
        if u == 0:
            out = (0,) * (self.m - level + 1)
        elif u == 1:
            out = tuple(math.comb(self.m - level, k)
                        for k in range(self.m - level + 1))
        else:
            var, lo, hi = self.nodes[u]
            plo = self._rank(lo, var + 1)
            phi = self._rank(hi, var + 1)
            branch = [0] * (self.m - var + 1)
            for k, x in enumerate(plo):
                branch[k] += x
            for k, x in enumerate(phi):
                branch[k + 1] += x
            gap = var - level
            if gap:
                acc = [0] * (self.m - level + 1)
                for a in range(gap + 1):
                    ca = math.comb(gap, a)
                    for b, cb in enumerate(branch):
                        acc[a + b] += ca * cb
                out = tuple(acc)
            else:
                out = tuple(branch)
        self.rank_cache[key] = out
        return out

    def rank_counts(self, root):
        return list(self._rank(root, 0))

    def reachable_nodes(self, root):
        seen = set()
        def dfs(u):
            if u <= 1 or u in seen:
                return
            seen.add(u)
            _, lo, hi = self.nodes[u]
            dfs(lo)
            dfs(hi)
        dfs(root)
        return len(seen)

def fresh_rebuild(m, b0, a1):
    mgr = ROBDD(m)
    root = 1
    full = (1 << m) - 1
    for z in b0:
        cm = full ^ z
        if cm == 0:
            root = 0
        else:
            root = mgr.and_(
                root, mgr.clause({j for j in range(m) if (cm >> j) & 1}, True)
            )
    for a in a1:
        if a == 0:
            root = 0
        else:
            root = mgr.and_(
                root, mgr.clause({j for j in range(m) if (a >> j) & 1}, False)
            )
    return mgr, root

def p95(xs):
    return sorted(xs)[int(0.95 * (len(xs) - 1))] if xs else 0.0

def run_cell(n, seed, observation_budget):
    game_rng = random.Random(seed)
    supports = gen_supports(n, game_rng, max(3, n // 3))
    player = seed % n
    obs_rng = random.Random(seed + 1000003 * n)
    stream = obs_rng.sample(range(1 << n), observation_budget)

    m = n - 1
    local = localizer(n, player)
    bit = 1 << player
    full = (1 << m) - 1
    mgr = ROBDD(m)
    root = 1
    b0, a1, all_b0, all_a1 = [], [], [], []

    incr_times = []
    rebuild_times = []
    new_rank_states = []
    reachable = []
    mismatches = 0
    effective = 0

    for mask in stream:
        val = value_support(mask, supports)
        changed = False
        t0 = time.perf_counter()

        if (mask & bit) and val == 0:
            z = local(mask & ~bit)
            all_b0.append(z)
            b0, changed = update_maximal(b0, z)
            if changed:
                cm = full ^ z
                root = 0 if cm == 0 else mgr.and_(
                    root,
                    mgr.clause({j for j in range(m) if (cm >> j) & 1}, True),
                )
        elif not (mask & bit) and val == 1:
            a = local(mask)
            all_a1.append(a)
            a1, changed = update_minimal(a1, a)
            if changed:
                root = 0 if a == 0 else mgr.and_(
                    root,
                    mgr.clause({j for j in range(m) if (a >> j) & 1}, False),
                )

        if not changed:
            continue

        effective += 1
        if set(b0) != set(reduce_maximal(all_b0)):
            mismatches += 1
        if set(a1) != set(reduce_minimal(all_a1)):
            mismatches += 1

        before = mgr.rank_cache_misses
        inc_counts = mgr.rank_counts(root)
        new_rank_states.append(mgr.rank_cache_misses - before)
        incr_times.append(time.perf_counter() - t0)
        reachable.append(mgr.reachable_nodes(root))

        t1 = time.perf_counter()
        fresh_mgr, fresh_root = fresh_rebuild(m, b0, a1)
        fresh_counts = fresh_mgr.rank_counts(fresh_root)
        rebuild_times.append(time.perf_counter() - t1)
        if inc_counts != fresh_counts:
            mismatches += 1

    return {
        "n": n,
        "seed": seed,
        "observation_budget": observation_budget,
        "player": player,
        "minimal_supports": [
            [j for j in range(n) if (s >> j) & 1] for s in supports
        ],
        "effective_updates": effective,
        "correctness_mismatches": mismatches,
        "final_maximal_upper_zeroes": len(b0),
        "final_minimal_lower_ones": len(a1),
        "median_incremental_ms": 1000 * statistics.median(incr_times),
        "p95_incremental_ms": 1000 * p95(incr_times),
        "median_rebuild_ms": 1000 * statistics.median(rebuild_times),
        "p95_rebuild_ms": 1000 * p95(rebuild_times),
        "total_incremental_s": sum(incr_times),
        "total_rebuild_s": sum(rebuild_times),
        "speedup_total": sum(rebuild_times) / sum(incr_times),
        "median_new_rank_cache_states": statistics.median(new_rank_states),
        "median_reachable_nodes": statistics.median(reachable),
        "final_manager_nodes_ever_allocated": len(mgr.nodes) - 2,
        "final_rank_cache_entries": len(mgr.rank_cache),
    }

def main():
    cells = []
    for n in N_VALUES:
        for seed in SEEDS:
            cells.append(run_cell(n, seed, BUDGETS[n]))

    aggregate = {}
    for n in N_VALUES:
        rows = [r for r in cells if r["n"] == n]
        aggregate[str(n)] = {
            "cells": len(rows),
            "total_effective_updates": sum(r["effective_updates"] for r in rows),
            "correctness_mismatches": sum(r["correctness_mismatches"] for r in rows),
            "median_of_cell_median_incremental_ms":
                statistics.median(r["median_incremental_ms"] for r in rows),
            "median_of_cell_median_rebuild_ms":
                statistics.median(r["median_rebuild_ms"] for r in rows),
            "median_total_speedup":
                statistics.median(r["speedup_total"] for r in rows),
            "min_total_speedup": min(r["speedup_total"] for r in rows),
            "max_total_speedup": max(r["speedup_total"] for r in rows),
            "median_new_rank_cache_states":
                statistics.median(r["median_new_rank_cache_states"] for r in rows),
            "median_reachable_nodes":
                statistics.median(r["median_reachable_nodes"] for r in rows),
        }

    out = {
        "schema": "coalition_incremental_boundary_holdout_v0_results",
        "protocol_blob": PROTOCOL_BLOB,
        "environment": {
            "python": sys.version.split()[0],
            "platform": platform.platform(),
        },
        "correctness": {
            "total_effective_updates": sum(r["effective_updates"] for r in cells),
            "total_mismatches": sum(r["correctness_mismatches"] for r in cells),
            "passed": all(r["correctness_mismatches"] == 0 for r in cells),
        },
        "aggregate_by_n": aggregate,
        "cells": cells,
        "scope": (
            "Runtime ratios are descriptive for this Python implementation/environment. "
            "Exactness is established only for the preregistered generated monotone-game "
            "observation streams. No polynomial-scaling or real-proof-utility claim."
        ),
    }
    print(json.dumps(out, indent=2, sort_keys=True))

if __name__ == "__main__":
    main()
