#!/usr/bin/env python3
import json
import math
import platform
import random
import statistics
import sys
import time
from collections import deque

import networkx as nx

PROTOCOL_BLOB = "4572296bdc1f9a285bc63a9155649167bd36eca6"
RANDOM_ORDER_SEED = 880401
CLAUSE_SEED = 880503
MAX_NODES = 2_000_000
MAX_SECONDS = 45.0

FAMILIES = [
    {"id": "path18", "kind": "path_graph", "n": 18},
    {"id": "binary_tree15", "kind": "balanced_binary_tree", "n": 15},
    {"id": "grid4x4", "kind": "grid_2d", "rows": 4, "cols": 4, "n": 16},
    {"id": "cubic18_s880301", "kind": "random_3_regular", "n": 18, "seed": 880301},
    {"id": "cubic18_s880319", "kind": "random_3_regular", "n": 18, "seed": 880319},
]
ORDERS = [
    "natural",
    "reverse_natural",
    "reverse_cuthill_mckee",
    "greedy_vertex_separation",
    "best_of_16_seeded_random_by_vertex_separation",
]
SCHEDULES = [
    "lexicographic_incremental",
    "seeded_random_incremental",
    "balanced_pairwise",
]


def stable_seed(text, base):
    h = base
    for ch in text.encode("utf-8"):
        h = ((h * 131) ^ ch) & 0xFFFFFFFF
    return h


def build_graph(spec):
    if spec["kind"] == "path_graph":
        return nx.path_graph(spec["n"])
    if spec["kind"] == "balanced_binary_tree":
        # 15 nodes exactly: height 3 full binary tree.
        g = nx.balanced_tree(2, 3)
        assert g.number_of_nodes() == spec["n"]
        return g
    if spec["kind"] == "grid_2d":
        raw = nx.grid_2d_graph(spec["rows"], spec["cols"])
        mapping = {v: i for i, v in enumerate(sorted(raw.nodes()))}
        return nx.relabel_nodes(raw, mapping)
    if spec["kind"] == "random_3_regular":
        return nx.random_regular_graph(3, spec["n"], seed=spec["seed"])
    raise ValueError(spec)


def frontier_size(g, prefix):
    p = set(prefix)
    return sum(1 for u in p if any(v not in p for v in g.neighbors(u)))


def vertex_separation_width(g, order):
    prefix = []
    best = 0
    for v in order[:-1]:
        prefix.append(v)
        best = max(best, frontier_size(g, prefix))
    return best


def greedy_vs_order(g):
    remaining = set(g.nodes())
    prefix = []
    while remaining:
        scored = []
        for v in sorted(remaining):
            candidate = prefix + [v]
            scored.append((frontier_size(g, candidate), g.degree[v], v))
        _, _, pick = min(scored)
        prefix.append(pick)
        remaining.remove(pick)
    return prefix


def order_for(g, family_id, name):
    nodes = sorted(g.nodes())
    if name == "natural":
        return nodes
    if name == "reverse_natural":
        return list(reversed(nodes))
    if name == "reverse_cuthill_mckee":
        return list(nx.utils.reverse_cuthill_mckee_ordering(g))
    if name == "greedy_vertex_separation":
        return greedy_vs_order(g)
    if name == "best_of_16_seeded_random_by_vertex_separation":
        rng = random.Random(stable_seed(family_id, RANDOM_ORDER_SEED))
        candidates = []
        for _ in range(16):
            o = nodes[:]
            rng.shuffle(o)
            candidates.append((vertex_separation_width(g, o), o))
        return min(candidates, key=lambda x: (x[0], x[1]))[1]
    raise ValueError(name)


class GuardedOut(RuntimeError):
    pass


class ROBDD:
    def __init__(self, n):
        self.n = n
        self.nodes = [None, None]
        self.unique = {}
        self.apply_cache = {}
        self.clause_cache = {}
        self.rank_cache = {}
        self.apply_calls = 0
        self.apply_hits = 0
        self.start = time.perf_counter()

    def guard(self):
        if len(self.nodes) - 2 > MAX_NODES:
            raise GuardedOut("max_allocated_nodes")
        if time.perf_counter() - self.start > MAX_SECONDS:
            raise GuardedOut("max_compile_seconds")

    def varpos(self, u):
        return self.n if u <= 1 else self.nodes[u][0]

    def mk(self, var, lo, hi):
        if lo == hi:
            return lo
        key = (var, lo, hi)
        out = self.unique.get(key)
        if out is not None:
            return out
        self.guard()
        out = len(self.nodes)
        self.nodes.append(key)
        self.unique[key] = out
        return out

    def clause2(self, a, b):
        key = tuple(sorted((a, b)))
        out = self.clause_cache.get(key)
        if out is not None:
            return out
        x, y = key
        if x == y:
            out = self.mk(x, 0, 1)
        else:
            # x OR y under position order x < y.
            y_node = self.mk(y, 0, 1)
            out = self.mk(x, y_node, 1)
        self.clause_cache[key] = out
        return out

    def and_(self, u, v):
        self.apply_calls += 1
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
        hit = self.apply_cache.get(key)
        if hit is not None:
            self.apply_hits += 1
            return hit
        self.guard()
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

    def reachable_nodes(self, roots):
        if isinstance(roots, int):
            roots = [roots]
        seen = set()
        stack = list(roots)
        while stack:
            u = stack.pop()
            if u <= 1 or u in seen:
                continue
            seen.add(u)
            _, lo, hi = self.nodes[u]
            stack.append(lo)
            stack.append(hi)
        return len(seen)

    def _rank(self, u, level):
        key = (u, level)
        hit = self.rank_cache.get(key)
        if hit is not None:
            return hit
        if u == 0:
            out = (0,) * (self.n - level + 1)
        elif u == 1:
            out = tuple(math.comb(self.n - level, k) for k in range(self.n - level + 1))
        else:
            var, lo, hi = self.nodes[u]
            plo = self._rank(lo, var + 1)
            phi = self._rank(hi, var + 1)
            branch = [0] * (self.n - var + 1)
            for k, x in enumerate(plo):
                branch[k] += x
            for k, x in enumerate(phi):
                branch[k + 1] += x
            gap = var - level
            if gap:
                acc = [0] * (self.n - level + 1)
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

    def eval(self, root, pos_bits):
        u = root
        while u > 1:
            var, lo, hi = self.nodes[u]
            u = hi if ((pos_bits >> var) & 1) else lo
        return int(u == 1)


def relabeled_edges(g, order):
    pos = {v: i for i, v in enumerate(order)}
    edges = []
    for u, v in g.edges():
        a, b = sorted((pos[u], pos[v]))
        edges.append((a, b))
    return sorted(edges), pos


def direct_cnf_value(g, assignment_original_bits):
    for u, v in g.edges():
        if not ((assignment_original_bits >> u) & 1) and not ((assignment_original_bits >> v) & 1):
            return 0
    return 1


def original_to_position_bits(bits, order):
    out = 0
    for p, v in enumerate(order):
        if (bits >> v) & 1:
            out |= 1 << p
    return out


def compile_cell(g, family_id, order_name, order, schedule):
    edges, _ = relabeled_edges(g, order)
    mgr = ROBDD(g.number_of_nodes())
    peak_reachable = 0
    peak_forest = 0
    guarded = None
    t0 = time.perf_counter()
    root = None
    try:
        if schedule in ("lexicographic_incremental", "seeded_random_incremental"):
            seq = edges[:]
            if schedule == "seeded_random_incremental":
                rng = random.Random(stable_seed(family_id + ":" + order_name, CLAUSE_SEED))
                rng.shuffle(seq)
            root = 1
            for a, b in seq:
                root = mgr.and_(root, mgr.clause2(a, b))
                peak_reachable = max(peak_reachable, mgr.reachable_nodes(root))
        elif schedule == "balanced_pairwise":
            forest = [mgr.clause2(a, b) for a, b in edges]
            peak_forest = max(peak_forest, mgr.reachable_nodes(forest)) if forest else 0
            if not forest:
                root = 1
            else:
                while len(forest) > 1:
                    nxt = []
                    for i in range(0, len(forest), 2):
                        if i + 1 == len(forest):
                            nxt.append(forest[i])
                        else:
                            nxt.append(mgr.and_(forest[i], forest[i + 1]))
                    forest = nxt
                    peak_forest = max(peak_forest, mgr.reachable_nodes(forest))
                root = forest[0]
        else:
            raise ValueError(schedule)
    except GuardedOut as e:
        guarded = str(e)
    compile_ms = 1000 * (time.perf_counter() - t0)

    row = {
        "family": family_id,
        "n": g.number_of_nodes(),
        "edges": g.number_of_edges(),
        "order": order_name,
        "order_vertices": order,
        "order_vertex_separation_width": vertex_separation_width(g, order),
        "schedule": schedule,
        "guarded_out": guarded,
        "compile_wall_clock_ms": compile_ms,
        "apply_recursive_calls": mgr.apply_calls,
        "apply_cache_hits": mgr.apply_hits,
        "unique_node_allocations": len(mgr.nodes) - 2,
        "final_allocated_nonterminal_nodes": len(mgr.nodes) - 2,
        "peak_reachable_nodes_during_incremental_schedule": peak_reachable if schedule != "balanced_pairwise" else None,
        "peak_forest_reachable_nodes": peak_forest if schedule == "balanced_pairwise" else None,
    }
    if guarded or root is None:
        return row

    row["final_reachable_nonterminal_nodes"] = mgr.reachable_nodes(root)
    tr = time.perf_counter()
    rank = mgr.rank_counts(root)
    row["rank_count_wall_clock_ms"] = 1000 * (time.perf_counter() - tr)
    row["rank_cache_states"] = len(mgr.rank_cache)
    row["exact_rank_count_vector"] = rank

    # Correctness check. n<=18 in this protocol, so exhaustive check is required.
    mismatches = 0
    limit = 1 << g.number_of_nodes()
    for bits in range(limit):
        want = direct_cnf_value(g, bits)
        got = mgr.eval(root, original_to_position_bits(bits, order))
        if want != got:
            mismatches += 1
            if mismatches >= 10:
                break
    row["assignment_checks"] = limit if mismatches == 0 else None
    row["assignment_mismatches"] = mismatches
    return row


def rankdata(xs):
    indexed = sorted(enumerate(xs), key=lambda kv: kv[1])
    ranks = [0.0] * len(xs)
    i = 0
    while i < len(indexed):
        j = i + 1
        while j < len(indexed) and indexed[j][1] == indexed[i][1]:
            j += 1
        r = (i + j - 1) / 2 + 1
        for k in range(i, j):
            ranks[indexed[k][0]] = r
        i = j
    return ranks


def pearson(xs, ys):
    if len(xs) < 2:
        return None
    mx, my = statistics.mean(xs), statistics.mean(ys)
    dx = [x - mx for x in xs]
    dy = [y - my for y in ys]
    den = math.sqrt(sum(x*x for x in dx) * sum(y*y for y in dy))
    return None if den == 0 else sum(a*b for a, b in zip(dx, dy)) / den


def main():
    cells = []
    orders_summary = []
    family_rank_reference = {}
    family_rank_mismatches = {}

    for spec in FAMILIES:
        g = build_graph(spec)
        seen_orders = {}
        for order_name in ORDERS:
            order = order_for(g, spec["id"], order_name)
            seen_orders[order_name] = order
            orders_summary.append({
                "family": spec["id"],
                "order": order_name,
                "vertex_separation_width": vertex_separation_width(g, order),
                "vertices": order,
            })
            for schedule in SCHEDULES:
                row = compile_cell(g, spec["id"], order_name, order, schedule)
                cells.append(row)
                rank = row.get("exact_rank_count_vector")
                if rank is not None:
                    if spec["id"] not in family_rank_reference:
                        family_rank_reference[spec["id"]] = rank
                    elif family_rank_reference[spec["id"]] != rank:
                        family_rank_mismatches[spec["id"]] = family_rank_mismatches.get(spec["id"], 0) + 1

    valid = [r for r in cells if not r.get("guarded_out") and r.get("assignment_mismatches") == 0]
    correctness = {
        "guarded_cells": sum(bool(r.get("guarded_out")) for r in cells),
        "assignment_mismatch_cells": sum((r.get("assignment_mismatches") or 0) > 0 for r in cells),
        "rank_vector_mismatch_families": family_rank_mismatches,
        "passed": not family_rank_mismatches and all((r.get("assignment_mismatches") or 0) == 0 for r in cells if not r.get("guarded_out")),
    }

    # Compare final representation vs order width on one canonical schedule per order.
    canon = [r for r in valid if r["schedule"] == "balanced_pairwise"]
    widths = [r["order_vertex_separation_width"] for r in canon]
    log_nodes = [math.log2(max(1, r["final_reachable_nonterminal_nodes"])) for r in canon]
    rho = pearson(rankdata(widths), rankdata(log_nodes)) if canon else None

    schedule_ratios = []
    by_key = {}
    for r in valid:
        by_key.setdefault((r["family"], r["order"]), {})[r["schedule"]] = r
    for key, d in by_key.items():
        if all(s in d for s in SCHEDULES):
            lex = d["lexicographic_incremental"]
            bal = d["balanced_pairwise"]
            rnd = d["seeded_random_incremental"]
            schedule_ratios.append({
                "family": key[0],
                "order": key[1],
                "balanced_vs_lex_allocated_ratio": bal["final_allocated_nonterminal_nodes"] / max(1, lex["final_allocated_nonterminal_nodes"]),
                "random_vs_lex_allocated_ratio": rnd["final_allocated_nonterminal_nodes"] / max(1, lex["final_allocated_nonterminal_nodes"]),
                "balanced_vs_lex_apply_calls_ratio": bal["apply_recursive_calls"] / max(1, lex["apply_recursive_calls"]),
                "random_vs_lex_apply_calls_ratio": rnd["apply_recursive_calls"] / max(1, lex["apply_recursive_calls"]),
                "final_live_nodes_equal": len({lex["final_reachable_nonterminal_nodes"], bal["final_reachable_nonterminal_nodes"], rnd["final_reachable_nonterminal_nodes"]}) == 1,
            })

    family_summary = {}
    for spec in FAMILIES:
        rows = [r for r in valid if r["family"] == spec["id"] and r["schedule"] == "balanced_pairwise"]
        if rows:
            family_summary[spec["id"]] = {
                "n": rows[0]["n"],
                "edges": rows[0]["edges"],
                "min_vertex_separation_width": min(r["order_vertex_separation_width"] for r in rows),
                "max_vertex_separation_width": max(r["order_vertex_separation_width"] for r in rows),
                "min_final_live_nodes": min(r["final_reachable_nonterminal_nodes"] for r in rows),
                "max_final_live_nodes": max(r["final_reachable_nonterminal_nodes"] for r in rows),
                "best_order_by_final_live_nodes": min(rows, key=lambda r: (r["final_reachable_nonterminal_nodes"], r["order"]))["order"],
            }

    out = {
        "schema": "coalition_boundary_width_pathology_v0_results",
        "protocol_blob": PROTOCOL_BLOB,
        "environment": {"python": sys.version.split()[0], "platform": platform.platform(), "networkx": nx.__version__},
        "correctness": correctness,
        "aggregate": {
            "cells": len(cells),
            "valid_cells": len(valid),
            "spearman_vertex_separation_vs_log2_final_live_nodes": rho,
            "median_balanced_vs_lex_allocated_ratio": statistics.median(x["balanced_vs_lex_allocated_ratio"] for x in schedule_ratios) if schedule_ratios else None,
            "median_balanced_vs_lex_apply_calls_ratio": statistics.median(x["balanced_vs_lex_apply_calls_ratio"] for x in schedule_ratios) if schedule_ratios else None,
            "all_schedule_final_live_nodes_equal": all(x["final_live_nodes_equal"] for x in schedule_ratios),
        },
        "family_summary": family_summary,
        "orders": orders_summary,
        "schedule_ratios": schedule_ratios,
        "cells": cells,
        "scope": "Exact only for the preregistered positive monotone 2-CNF graph instances and tested fixed orders/schedules. Random cubic graphs are not certified expanders. Timing and allocation are implementation/environment specific. This v0 does not implement CUDD dynamic reordering or an alternative TDD/d-DNNF representation.",
    }
    print(json.dumps(out, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
