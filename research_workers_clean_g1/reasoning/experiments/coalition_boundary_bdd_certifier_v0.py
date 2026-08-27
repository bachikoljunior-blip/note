#!/usr/bin/env python3
"""Exploratory exact upper-Shapley certifier using boundary antichains + BDD-style DP.

For monotone v and fixed player i, write a(T)=v(T), b(T)=v(T∪{i}).
The maximum Shapley contribution over all monotone completions consistent with
point observations is attained by the pointwise-minimum feasible a and
pointwise-maximum feasible b. Therefore only:
  - maximal observed zeroes on the b-slice, and
  - minimal observed ones on the a-slice
matter.

The uncertain pivotal family is
  R_i = B_{n-1} \ (down(B0_max) ∪ up(A1_min)),
and
  phi_i^max = (1/n) * sum_k |R_i ∩ C(n-1,k)| / C(n-1,k).

R_i is a CNF:
  for Z in B0_max: OR_{j∉Z} x_j
  for A in A1_min: OR_{j∈A} ¬x_j
so exact cardinality counts can be computed by a reduced BDD-like memoized DP
without materializing the full 2^n closure graph.

This file reproduces:
1) parity against the explicit maximum-closure/max-flow formulation,
2) an indicative n=10 runtime benchmark,
3) sparse-observation scaling through n=28.

The experiment is exploratory, not preregistered.
"""
import json, math, platform, random, statistics, sys, time
from functools import lru_cache

import scipy
from scipy.sparse import dok_matrix
from scipy.sparse.csgraph import maximum_flow

def gen_monotone_game(n, rng):
    candidates = set()
    for _ in range(rng.randint(1, max(2, 2 * n))):
        k = rng.randint(0, n)
        candidates.add(sum(1 << j for j in rng.sample(range(n), k)))
    supports = []
    for s in sorted(candidates, key=lambda x: (x.bit_count(), x)):
        if not any((t & ~s) == 0 for t in supports):
            supports.append(s)
    values = [int(any((m & s) == s for s in supports)) for m in range(1 << n)]
    return supports, values

def gen_game_from_supports(n, rng, count=5, sizes=(2, 3, 4)):
    supports = []
    tries = 0
    while len(supports) < count and tries < 10000:
        tries += 1
        k = rng.choice([s for s in sizes if s <= n])
        mask = sum(1 << j for j in rng.sample(range(n), k))
        if any((t & ~mask) == 0 for t in supports):
            continue
        supports = [t for t in supports if not (mask & ~t) == 0]
        if mask not in supports:
            supports.append(mask)
    return supports

def value_from_supports(mask, supports):
    return int(any((mask & s) == s for s in supports))

def objective_coeff(n, player):
    coeff = [0] * (1 << n)
    bit = 1 << player
    for mask in range(1 << n):
        if mask & bit:
            continue
        k = mask.bit_count()
        w = math.factorial(k) * math.factorial(n - k - 1)
        coeff[mask] -= w
        coeff[mask | bit] += w
    return coeff

def flow_upper(n, values, sampled, player):
    nodes = 1 << n
    scale = math.factorial(n)
    src, snk = nodes, nodes + 1
    inf = 10 * scale
    coeff = objective_coeff(n, player)
    cap = dok_matrix((nodes + 2, nodes + 2), dtype=int)
    positive = 0
    for node, w in enumerate(coeff):
        if w > 0:
            cap[src, node] = w
            positive += w
        elif w < 0:
            cap[node, snk] = -w
    for mask in range(nodes):
        for j in range(n):
            if not mask & (1 << j):
                cap[mask, mask | (1 << j)] = inf
    for mask in sampled:
        if values[mask]:
            cap[src, mask] = int(cap[src, mask]) + inf
        else:
            cap[mask, snk] = int(cap[mask, snk]) + inf
    flow = maximum_flow(cap.tocsr(), src, snk)
    return float((positive - flow.flow_value) / scale)

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

def boundary_from_sample(n, value_get, sampled, player):
    others = [j for j in range(n) if j != player]
    loc = {j: k for k, j in enumerate(others)}
    full = (1 << (n - 1)) - 1
    def localize(mask):
        z = 0
        for j in others:
            if mask & (1 << j):
                z |= 1 << loc[j]
        return z
    bit = 1 << player
    b0 = [localize(m & ~bit) for m in sampled if (m & bit) and value_get(m) == 0]
    a1 = [localize(m) for m in sampled if not (m & bit) and value_get(m) == 1]
    b0 = reduce_maximal(b0)
    a1 = reduce_minimal(a1)
    positive_clauses = [full ^ z for z in b0]
    negative_clauses = list(a1)
    return positive_clauses, negative_clauses, b0, a1

def bdd_rank_counts(m, positive_clauses, negative_clauses):
    if any(c == 0 for c in positive_clauses) or any(c == 0 for c in negative_clauses):
        return [0] * (m + 1), 1
    freq = [0] * m
    for clause in list(positive_clauses) + list(negative_clauses):
        for j in range(m):
            if clause >> j & 1:
                freq[j] += 1
    order = sorted(range(m), key=lambda j: (-freq[j], j))
    inv = {old: new for new, old in enumerate(order)}
    def remap(clause):
        x = 0
        for old in range(m):
            if clause >> old & 1:
                x |= 1 << inv[old]
        return x
    p0 = tuple(sorted(remap(c) for c in set(positive_clauses)))
    n0 = tuple(sorted(remap(c) for c in set(negative_clauses)))
    state_count = 0

    @lru_cache(None)
    def rec(idx, pclauses, nclauses):
        nonlocal state_count
        state_count += 1
        if idx == m:
            return (1,) if not pclauses and not nclauses else (0,)
        bit = 1 << idx
        branches = []
        for val in (0, 1):
            bad = False
            pnext = []
            for clause in pclauses:
                if clause & bit:
                    if val == 1:
                        continue
                    clause = clause & ~bit
                    if clause == 0:
                        bad = True
                        break
                pnext.append(clause)
            if bad:
                branches.append(None)
                continue
            nnext = []
            for clause in nclauses:
                if clause & bit:
                    if val == 0:
                        continue
                    clause = clause & ~bit
                    if clause == 0:
                        bad = True
                        break
                nnext.append(clause)
            if bad:
                branches.append(None)
                continue
            branches.append(rec(
                idx + 1,
                tuple(sorted(set(pnext))),
                tuple(sorted(set(nnext))),
            ))
        counts = [0] * (m - idx + 1)
        if branches[0] is not None:
            for k, v in enumerate(branches[0]):
                counts[k] += v
        if branches[1] is not None:
            for k, v in enumerate(branches[1]):
                counts[k + 1] += v
        return tuple(counts)

    counts = list(rec(0, p0, n0))
    return counts, state_count

def boundary_bdd_upper(n, value_get, sampled, player):
    pos, neg, b0, a1 = boundary_from_sample(n, value_get, sampled, player)
    counts, states = bdd_rank_counts(n - 1, pos, neg)
    upper = sum(
        count / (n * math.comb(n - 1, k))
        for k, count in enumerate(counts)
    )
    return float(upper), states, len(pos), len(neg), counts

def closed_enum_upper(n, value_get, sampled, player):
    _, _, b0, a1 = boundary_from_sample(n, value_get, sampled, player)
    total = 0.0
    m = n - 1
    for coalition in range(1 << m):
        if any((coalition & ~z) == 0 for z in b0):
            continue
        if any((a & ~coalition) == 0 for a in a1):
            continue
        total += 1 / (n * math.comb(m, coalition.bit_count()))
    return float(total)

def main():
    out = {
        "schema": "coalition_boundary_bdd_certifier_v0_results",
        "run_kind": "exploratory_not_preregistered",
        "environment": {
            "python": sys.version.split()[0],
            "scipy": scipy.__version__,
            "platform": platform.platform(),
        },
    }

    parity = {
        "cases": 0,
        "max_abs_diff_flow_vs_bdd": 0.0,
        "max_abs_diff_flow_vs_closed": 0.0,
    }
    for n in range(3, 9):
        for seed in range(12):
            rng = random.Random(1234 + n * 100 + seed)
            _, values = gen_monotone_game(n, rng)
            total = 1 << n
            for _ in range(5):
                budget = rng.randint(0, total)
                sampled = set(rng.sample(range(total), budget))
                for player in rng.sample(range(n), min(3, n)):
                    flow = flow_upper(n, values, sampled, player)
                    bdd, *_ = boundary_bdd_upper(
                        n, lambda m, v=values: v[m], sampled, player
                    )
                    enum = closed_enum_upper(
                        n, lambda m, v=values: v[m], sampled, player
                    )
                    parity["cases"] += 1
                    parity["max_abs_diff_flow_vs_bdd"] = max(
                        parity["max_abs_diff_flow_vs_bdd"], abs(flow - bdd)
                    )
                    parity["max_abs_diff_flow_vs_closed"] = max(
                        parity["max_abs_diff_flow_vs_closed"], abs(flow - enum)
                    )
    out["parity"] = parity

    n = 10
    supports = [[0,1],[2,3],[4,5],[6,7],[0,2,4,6,8,9]]
    support_masks = [sum(1 << i for i in s) for s in supports]
    values = [
        int(any((m & s) == s for s in support_masks))
        for m in range(1 << n)
    ]
    rng = random.Random(20260828)
    benchmark = {}
    for budget in [128, 256, 512, 768, 896]:
        rows = []
        for rep in range(20):
            sampled = set(rng.sample(range(1 << n), budget))
            player = 8 if rep % 2 == 0 else 9
            t = time.perf_counter()
            flow = flow_upper(n, values, sampled, player)
            flow_s = time.perf_counter() - t
            t = time.perf_counter()
            enum = closed_enum_upper(n, lambda m, v=values: v[m], sampled, player)
            enum_s = time.perf_counter() - t
            t = time.perf_counter()
            bdd, states, pcount, ncount, _ = boundary_bdd_upper(
                n, lambda m, v=values: v[m], sampled, player
            )
            bdd_s = time.perf_counter() - t
            assert abs(flow - enum) < 1e-12 and abs(flow - bdd) < 1e-12
            rows.append({
                "flow_s": flow_s,
                "enum_s": enum_s,
                "bdd_s": bdd_s,
                "bdd_states": states,
                "positive_boundary_clauses": pcount,
                "negative_boundary_clauses": ncount,
            })
        benchmark[str(budget)] = {
            "repetitions": len(rows),
            "median_flow_ms": 1000 * statistics.median(r["flow_s"] for r in rows),
            "median_closed_enum_ms": 1000 * statistics.median(r["enum_s"] for r in rows),
            "median_boundary_bdd_ms": 1000 * statistics.median(r["bdd_s"] for r in rows),
            "median_bdd_states": statistics.median(r["bdd_states"] for r in rows),
            "median_positive_boundary_clauses": statistics.median(
                r["positive_boundary_clauses"] for r in rows
            ),
            "median_negative_boundary_clauses": statistics.median(
                r["negative_boundary_clauses"] for r in rows
            ),
        }
    out["n10_benchmark"] = benchmark

    scaling = []
    for n in [12,14,16,18,20,22,24,26,28]:
        rng = random.Random(9100 + n)
        supports = gen_game_from_supports(n, rng)
        budget = 2000
        sampled = rng.sample(range(1 << n), budget)
        values = {m: value_from_supports(m, supports) for m in sampled}
        t = time.perf_counter()
        upper, states, pcount, ncount, _ = boundary_bdd_upper(
            n, lambda m, d=values: d[m], sampled, n - 1
        )
        elapsed = time.perf_counter() - t
        scaling.append({
            "n": n,
            "sampled_coalitions": budget,
            "minimal_support_count": len(supports),
            "positive_boundary_clauses": pcount,
            "negative_boundary_clauses": ncount,
            "bdd_states": states,
            "elapsed_s": elapsed,
            "upper": upper,
            "explicit_boolean_lattice_vertices": 1 << n,
        })
    out["scaling"] = scaling
    print(json.dumps(out, indent=2, sort_keys=True))

if __name__ == "__main__":
    main()
