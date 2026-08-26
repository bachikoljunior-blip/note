"""Synthetic two-layer provenance / rollback sweep for the clean multi-agent role.

Frozen semantic tuple for the research that produced this script:
- note main SHA: a0c1b503671cd3f285705334d868508426825ec3
- sanitized root control revision: 11
- role config revision: 6
- role config blob: 9a3edbe40ee5cbf3a94fe3206606aa58841c955c

This is a mechanism harness, not a production estimate. It extends the earlier
provenance sweep by dropping runtime-observed edges at every DAG layer and adding a
static potential-dependency layer with independently controlled recall and false
positive rate. It measures edge recall separately from transitive descendant-set
recall. A post-replay assertion policy is included only as a synthetic upper-bound
study: its assertion coverage is a parameter, not a claim that a production system
has oracle access to stale descendants.
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


def sample_dependency_maps(parents, nodes, rng, observed_recall, static_recall, static_fp):
    true_edges = {(p, c) for c, ps in parents.items() for p in ps}
    observed = {e for e in true_edges if rng.random() < observed_recall}
    static = {e for e in true_edges if rng.random() < static_recall}
    index = {n: i for i, n in enumerate(nodes)}
    for a in nodes:
        for b in nodes:
            if index[a] < index[b] and b not in ("S", "U") and (a, b) not in true_edges:
                if rng.random() < static_fp:
                    static.add((a, b))
    return true_edges, observed, static


def verifier(active, true, rng, p):
    if active != true:
        if rng.random() >= p.tpr:
            return False, None
        proposed = true if rng.random() < p.corr_acc else true + (1 if rng.random() < 0.5 else -1)
        return True, proposed
    if rng.random() >= p.fpr:
        return False, None
    return True, true + (1 if rng.random() < 0.5 else -1)


def run(seed, fanout=3, depth=3, observed_recall=0.85, static_recall=0.9,
        static_fp=0.05, policy="enlarged_union", assertion_recall=1.0, p=P()):
    rng = random.Random(seed)
    parents, funcs, nodes, children = make_dag(fanout, depth)
    true_desc = descendants(children, "S")
    topo = [n for n in nodes if n not in ("S", "U")]

    true_s, true_u = rng.randint(5, 15), rng.randint(3, 12)
    active_s = (
        true_s + (2 if rng.random() < 0.5 else -2)
        if rng.random() < p.p_source_corrupt else true_s
    )
    vals = {"S": active_s, "U": true_u}
    source_version = {"S": 0, "U": None}
    calls = 0.0

    # Late correction: materialize the whole graph before boundary verification.
    for n in topo:
        vals[n] = mc(funcs[n], [vals[x] for x in parents[n]], rng, p)
        calls += p.model_cost
        source_version[n] = 0 if n in true_desc else None

    flag, proposal = verifier(active_s, true_s, rng, p)
    calls += p.verifier_cost
    replaced = False
    if flag and proposal is not None:
        active_s = proposal
        vals["S"] = active_s
        source_version["S"] = 1
        replaced = True

    true_edges, observed, static = sample_dependency_maps(
        parents, nodes, rng, observed_recall, static_recall, static_fp
    )
    observed_desc = reach_from_edges(observed, "S")
    union_desc = reach_from_edges(observed | static, "S")

    if not replaced:
        replay = set()
    elif policy in ("local_observed", "assert_fail_closed"):
        replay = observed_desc
    elif policy in ("enlarged_union", "union_assert_fail_closed"):
        replay = observed_desc | union_desc
    elif policy == "whole_redraw":
        replay = set(topo)
    else:
        raise ValueError(policy)

    for n in topo:
        if n in replay:
            vals[n] = mc(funcs[n], [vals[x] for x in parents[n]], rng, p)
            calls += p.model_cost
            source_version[n] = 1 if n in true_desc else None

    stale_nodes = {
        n for n in true_desc
        if replaced and source_version.get(n) != source_version["S"]
    }
    detected_stale = False
    if replaced and policy in ("assert_fail_closed", "union_assert_fail_closed") and stale_nodes:
        # Synthetic coverage model for a post-replay proof/check. This is NOT oracle evidence.
        detected_stale = any(rng.random() < assertion_recall for _ in stale_nodes)
        if detected_stale:
            for n in topo:
                vals[n] = mc(funcs[n], [vals[x] for x in parents[n]], rng, p)
                calls += p.model_cost
                source_version[n] = 1 if n in true_desc else None
            stale_nodes = set()

    truth = {"S": true_s, "U": true_u}
    for n in topo:
        truth[n] = funcs[n](*[truth[x] for x in parents[n]])

    def rec_prec(pred):
        recall = len(pred & true_desc) / len(true_desc)
        precision = len(pred & true_desc) / len(pred) if pred else 1.0
        return recall, precision

    obs_dr, obs_dp = rec_prec(observed_desc)
    union_dr, union_dp = rec_prec(union_desc)
    return {
        "correct": vals["D"] == truth["D"],
        "calls": calls,
        "source_restored": active_s == true_s,
        "stale": bool(stale_nodes),
        "stale_fraction": len(stale_nodes) / len(true_desc) if replaced else 0.0,
        "replay_fraction": len(replay) / len(topo) if replaced else 0.0,
        "observed_edge_recall": len(observed & true_edges) / len(true_edges),
        "union_edge_recall": len((observed | static) & true_edges) / len(true_edges),
        "observed_descendant_recall": obs_dr,
        "observed_descendant_precision": obs_dp,
        "union_descendant_recall": union_dr,
        "union_descendant_precision": union_dp,
        "detected_stale": detected_stale,
    }


def aggregate(n=20_000, **kwargs):
    rows = [run(i, **kwargs) for i in range(n)]
    out = {k: statistics.mean(r[k] for r in rows) for k in rows[0]}
    out["correct_per_100k_calls"] = out["correct"] / out["calls"] * 100_000
    return out


def main():
    print("Two-layer provenance key conditions, fanout=3 depth=3")
    conditions = [
        (0.70, 0.90, 0.05),
        (0.85, 0.70, 0.20),
        (0.85, 0.90, 0.05),
        (0.85, 1.00, 0.20),
        (0.95, 0.90, 0.05),
    ]
    for observed_recall, static_recall, static_fp in conditions:
        for policy in ("local_observed", "enlarged_union", "whole_redraw"):
            print(observed_recall, static_recall, static_fp, policy,
                  aggregate(n=20_000, observed_recall=observed_recall,
                            static_recall=static_recall, static_fp=static_fp,
                            policy=policy))

    print("\nStatic false-positive sweep with perfect static recall")
    for static_fp in (0.0, 0.02, 0.05, 0.10, 0.20, 0.40, 0.80):
        print(static_fp, aggregate(n=10_000, observed_recall=0.85,
                                   static_recall=1.0, static_fp=static_fp,
                                   policy="enlarged_union"))

    print("\nPost-replay assertion diagnostic")
    for observed_recall in (0.70, 0.85, 0.95):
        for assertion_recall in (0.50, 0.80, 1.00):
            for policy in ("local_observed", "assert_fail_closed", "whole_redraw"):
                print(observed_recall, assertion_recall, policy,
                      aggregate(n=5_000, observed_recall=observed_recall,
                                static_recall=0.0, static_fp=0.0,
                                policy=policy, assertion_recall=assertion_recall))


if __name__ == "__main__":
    main()
