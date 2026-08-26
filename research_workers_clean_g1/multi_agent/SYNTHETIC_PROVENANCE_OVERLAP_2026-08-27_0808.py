"""Synthetic provenance-overlap sweep for the clean multi-agent role.

Frozen semantic tuple:
- note main SHA: 64b03acca1c5d9290975fe82a252d4f0ab2aa235
- sanitized root control revision: 11
- role config revision: 6
- role config blob: 9a3edbe40ee5cbf3a94fe3206606aa58841c955c

Mechanism study only. The key manipulation holds runtime-observed edge recall and
static-map marginal edge recall fixed while varying how often the static map catches
an edge specifically when runtime provenance missed it. This separates marginal
coverage from complementary coverage / correlated blind spots.
"""
from __future__ import annotations
from dataclasses import dataclass
import random
import statistics


@dataclass
class P:
    p_source_corrupt: float = 0.35
    p_model_correct: float = 0.97
    tpr: float = 0.88
    fpr: float = 0.05
    corr_acc: float = 0.94
    model_cost: float = 1.0
    verifier_cost: float = 0.25


def perturb(v, rng):
    return v + (1 if rng.random() < 0.5 else -1)


def mc(func, args, rng, p):
    target = func(*args)
    return target if rng.random() < p.p_model_correct else perturb(target, rng)


def make_dag(fanout=3, depth=3):
    parents, funcs, leaves = {}, {}, []
    nodes = ["S", "U"]
    for b in range(fanout):
        prev = "S"
        for d in range(depth):
            n = f"x{b}_{d}"
            parents[n] = [prev]
            inc = b + d + 1
            funcs[n] = (lambda inc: (lambda x: x + inc))(inc)
            prev = n
            nodes.append(n)
        leaves.append(prev)
    parents["C"] = ["U"]
    funcs["C"] = lambda u: 2 * u - 1
    nodes.append("C")
    parents["D"] = leaves + ["C"]
    funcs["D"] = lambda *xs: sum(xs)
    nodes.append("D")
    children = {n: [] for n in nodes}
    for child, pars in parents.items():
        for par in pars:
            children.setdefault(par, []).append(child)
    return parents, funcs, nodes, children


def descendants(children, source):
    out, stack = set(), [source]
    while stack:
        u = stack.pop()
        for v in children.get(u, []):
            if v not in out:
                out.add(v)
                stack.append(v)
    return out


def reach_from_edges(edges, source):
    child = {}
    for a, b in edges:
        child.setdefault(a, []).append(b)
    return descendants(child, source)


def verifier(active, true, rng, p):
    if active != true:
        if rng.random() >= p.tpr:
            return False, None
        proposed = true if rng.random() < p.corr_acc else true + (1 if rng.random() < 0.5 else -1)
        return True, proposed
    if rng.random() >= p.fpr:
        return False, None
    return True, true + (1 if rng.random() < 0.5 else -1)


def sample_maps(parents, nodes, rng, observed_recall, static_marginal_recall,
                static_fp, q_static_given_observed_miss):
    """Hold P(static edge)=static_marginal_recall fixed while changing overlap.

    q_static_given_observed_miss is the important complement quantity:
    P(static captures edge | runtime observed map missed edge).
    P(static captures | runtime captured) is solved to preserve the same marginal.
    """
    true_edges = {(p, c) for c, ps in parents.items() for p in ps}
    q = q_static_given_observed_miss
    p_seen = (static_marginal_recall - (1 - observed_recall) * q) / observed_recall
    if not 0 <= p_seen <= 1:
        raise ValueError((observed_recall, static_marginal_recall, q, p_seen))
    observed, static = set(), set()
    for edge in true_edges:
        seen = rng.random() < observed_recall
        if seen:
            observed.add(edge)
        if rng.random() < (p_seen if seen else q):
            static.add(edge)

    index = {n: i for i, n in enumerate(nodes)}
    for a in nodes:
        for b in nodes:
            if index[a] < index[b] and b not in ("S", "U") and (a, b) not in true_edges:
                if rng.random() < static_fp:
                    static.add((a, b))
    return true_edges, observed, static, p_seen


def run(seed, q, policy, fanout=3, depth=3, observed_recall=0.85,
        static_marginal_recall=0.90, static_fp=0.05, p=P()):
    rng = random.Random(seed)
    parents, funcs, nodes, children = make_dag(fanout, depth)
    true_desc = descendants(children, "S")
    topo = [n for n in nodes if n not in ("S", "U")]

    true_s, true_u = rng.randint(5, 15), rng.randint(3, 12)
    active_s = true_s + (2 if rng.random() < 0.5 else -2) if rng.random() < p.p_source_corrupt else true_s
    vals = {"S": active_s, "U": true_u}
    versions = {"S": 0, "U": None}
    calls = 0.0
    for n in topo:
        vals[n] = mc(funcs[n], [vals[x] for x in parents[n]], rng, p)
        calls += p.model_cost
        versions[n] = 0 if n in true_desc else None

    flag, proposal = verifier(active_s, true_s, rng, p)
    calls += p.verifier_cost
    replaced = False
    if flag and proposal is not None:
        vals["S"] = proposal
        versions["S"] = 1
        replaced = True

    true_edges, observed, static, p_seen = sample_maps(
        parents, nodes, rng, observed_recall, static_marginal_recall,
        static_fp, q
    )
    union = observed | static
    union_desc = reach_from_edges(union, "S")
    if not replaced:
        replay = set()
    elif policy == "union":
        replay = union_desc
    elif policy == "whole":
        replay = set(topo)
    else:
        raise ValueError(policy)

    for n in topo:
        if n in replay:
            vals[n] = mc(funcs[n], [vals[x] for x in parents[n]], rng, p)
            calls += p.model_cost
            versions[n] = 1 if n in true_desc else None

    stale = bool({n for n in true_desc if replaced and versions.get(n) != versions["S"]})
    truth = {"S": true_s, "U": true_u}
    for n in topo:
        truth[n] = funcs[n](*[truth[x] for x in parents[n]])

    return {
        "correct": vals["D"] == truth["D"],
        "calls": calls,
        "stale": stale,
        "union_edge_recall": len(union & true_edges) / len(true_edges),
        "union_descendant_recall": len(union_desc & true_desc) / len(true_desc),
        "union_replay_fraction": len(union_desc) / len(topo),
        "p_static_given_observed_hit": p_seen,
    }


def aggregate(q, policy, n=6000):
    rows = [run(i, q, policy) for i in range(n)]
    correct = statistics.mean(r["correct"] for r in rows)
    calls = statistics.mean(r["calls"] for r in rows)
    return {
        "correct": correct,
        "calls": calls,
        "correct_per_100k_calls": correct / calls * 100000,
        "stale_run_rate": statistics.mean(r["stale"] for r in rows),
        "union_edge_recall": statistics.mean(r["union_edge_recall"] for r in rows),
        "union_descendant_recall": statistics.mean(r["union_descendant_recall"] for r in rows),
        "union_replay_fraction": statistics.mean(r["union_replay_fraction"] for r in rows),
        "p_static_given_observed_hit": rows[0]["p_static_given_observed_hit"],
    }


def main():
    # For observed=.85 and static marginal=.90, q=1/3 is the strongest feasible
    # positive overlap of capture / correlated misses (P(static|observed-hit)=1).
    for q in (1/3, 0.5, 0.7, 0.9, 1.0):
        print("q_static_given_observed_miss", q)
        print(" union", aggregate(q, "union"))
        print(" whole", aggregate(q, "whole"))


if __name__ == "__main__":
    main()
