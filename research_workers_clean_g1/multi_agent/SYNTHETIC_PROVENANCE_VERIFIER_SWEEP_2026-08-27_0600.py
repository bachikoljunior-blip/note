"""Synthetic provenance/recovery sweep for multi-agent state repair.

This reproduces the 2026-08-27 ~06:00 JST exploratory extension of
SYNTHETIC_DEPENDENCY_ROLLBACK_2026-08-27_0503.py.

Frozen semantic tuple:
- note main SHA: 5d284a097cbc5ff6d630847b1218c8b1bce4c83f
- control revision: 9
- config revision: 6
- role config blob: 9a3edbe40ee5cbf3a94fe3206606aa58841c955c

All numerical parameters are synthetic controls, not estimates of any production
model or verifier. The "conservative_inferred" policy is intentionally an optimistic
static-potential-dependency fallback: it has perfect recall over the true S-dependent
first-level branches and may additionally redraw independent C. It is not an
inference oracle claimed to be available in practice.
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
    shared_error: float = 0.60
    second_tpr: float = 0.90
    second_fpr: float = 0.04
    second_corr_acc: float = 0.96
    model_cost: float = 1.0
    verifier_cost: float = 0.25


def perturb(v, rng):
    return v + (1 if rng.random() < 0.5 else -1)


def mc(func, args, rng, p):
    t = func(*args)
    return t if rng.random() < p.p_model_correct else perturb(t, rng)


def make_dag(fanout, depth):
    parents = {}
    funcs = {}
    leaves = []
    for b in range(fanout):
        prev = "S"
        for d in range(depth):
            n = f"x{b}_{d}"
            parents[n] = [prev]
            inc = b + d + 1
            funcs[n] = (lambda inc: (lambda x: x + inc))(inc)
            prev = n
        leaves.append(prev)
    parents["C"] = ["U"]
    funcs["C"] = lambda u: 2 * u - 1
    parents["D"] = leaves + ["C"]
    funcs["D"] = lambda *xs: sum(xs)
    return parents, funcs, leaves


def verifier_one(active, true, rng, p, mode="independent", latent_shared=False):
    # Same-context/correlated mode: a shared source-level narrative failure can make
    # the verifier accept the same wrong source rather than producing independent evidence.
    if mode == "correlated" and latent_shared:
        if active != true and rng.random() < p.shared_error:
            return False, None
    if active != true:
        if rng.random() >= p.tpr:
            return False, None
        if rng.random() < p.corr_acc:
            return True, true
        return True, true + (1 if rng.random() < 0.5 else -1)
    if rng.random() >= p.fpr:
        return False, None
    return True, true + (1 if rng.random() < 0.5 else -1)


def verifier_two(active, true, rng, p):
    # Heterogeneous/independent confirmation model.
    if active != true:
        if rng.random() >= p.second_tpr:
            return False, None
        if rng.random() < p.second_corr_acc:
            return True, true
        return True, true + (1 if rng.random() < 0.5 else -1)
    if rng.random() >= p.second_fpr:
        return False, None
    return True, true + (1 if rng.random() < 0.5 else -1)


def run(seed, fanout=3, depth=3, miss=0.0, policy="local_observed",
        vmode="independent", p=P(), inferred_fp=0.5):
    rng = random.Random(seed)
    _, funcs, _ = make_dag(fanout, depth)
    true_s = rng.randint(5, 15)
    true_u = rng.randint(3, 12)
    active_s = (
        true_s + (2 if rng.random() < 0.5 else -2)
        if rng.random() < p.p_source_corrupt else true_s
    )
    latent_shared = active_s != true_s

    vals = {"S": active_s, "U": true_u}
    versions = {"S": 0}
    observed_parents = {}
    calls = 0.0

    # Materialize first-level S-dependent work plus an independent C before verification.
    for b in range(fanout):
        n = f"x{b}_0"
        vals[n] = mc(funcs[n], [vals["S"]], rng, p)
        calls += p.model_cost
        versions[n] = 0
        observed_parents[n] = [] if rng.random() < miss else ["S"]
    vals["C"] = mc(funcs["C"], [true_u], rng, p)
    calls += p.model_cost
    observed_parents["C"] = ["U"]

    flag1, prop1 = verifier_one(active_s, true_s, rng, p, vmode, latent_shared)
    calls += p.verifier_cost
    replace = False
    proposal = None

    if policy == "annotation":
        proposal = prop1 if flag1 else None
    elif policy == "provisional_confirm":
        # Destructive replace only when two verifier paths agree exactly.
        if flag1 and prop1 is not None:
            flag2, prop2 = verifier_two(active_s, true_s, rng, p)
            calls += p.verifier_cost
            if flag2 and prop2 == prop1:
                active_s = prop1
                replace = True
            else:
                proposal = prop1
    else:
        if flag1 and prop1 is not None:
            active_s = prop1
            replace = True

    if replace:
        vals["S"] = active_s
        versions["S"] = 1

    true_affected = {f"x{b}_0" for b in range(fanout)}
    replay = set()
    if replace:
        if policy == "whole_redraw":
            replay |= true_affected | {"C"}
        elif policy == "conservative_inferred":
            # Optimistic static fallback: full recall for possible S-dependent first-level
            # branches, plus a tunable false-positive redraw of independent C.
            replay |= true_affected
            if rng.random() < inferred_fp:
                replay.add("C")
        elif policy in ("local_observed", "provisional_confirm"):
            for n in true_affected:
                if "S" in observed_parents.get(n, []):
                    replay.add(n)
        elif policy == "hard_no_replay":
            pass

    for n in list(replay):
        if n == "C":
            vals[n] = mc(funcs[n], [true_u], rng, p)
            calls += p.model_cost
        else:
            vals[n] = mc(funcs[n], [vals["S"]], rng, p)
            calls += p.model_cost
            versions[n] = versions["S"]

    for d in range(1, depth):
        for b in range(fanout):
            n = f"x{b}_{d}"
            par = f"x{b}_{d-1}"
            vals[n] = mc(funcs[n], [vals[par]], rng, p)
            calls += p.model_cost
            observed_parents[n] = [] if rng.random() < miss else [par]
            versions[n] = versions.get(par, 0)

    if policy == "annotation" and proposal is not None and rng.random() < 0.75:
        # Annotation can trigger an expensive branch reconstruction without mutating canonical S.
        for b in range(fanout):
            prev = proposal
            for d in range(depth):
                n = f"x{b}_{d}"
                vals[n] = mc(funcs[n], [prev], rng, p)
                calls += p.model_cost
                prev = vals[n]

    leafvals = [vals[f"x{b}_{depth - 1}"] for b in range(fanout)]
    vals["D"] = mc(funcs["D"], leafvals + [vals["C"]], rng, p)
    calls += p.model_cost

    true_leaves = []
    for b in range(fanout):
        x = true_s
        for d in range(depth):
            x = funcs[f"x{b}_{d}"](x)
        true_leaves.append(x)
    target = funcs["D"](*(true_leaves + [funcs["C"](true_u)]))

    stale = replace and any(
        versions.get(f"x{b}_0", 0) != versions["S"] for b in range(fanout)
    )
    return {
        "correct": vals["D"] == target,
        "calls": calls,
        "stale": stale,
        "source": active_s == true_s,
        "replay": len(replay),
    }


def agg(n=20_000, **kw):
    rows = [run(i, **kw) for i in range(n)]
    out = {k: statistics.mean(r[k] for r in rows) for k in rows[0]}
    out["correct_per_100k"] = out["correct"] / out["calls"] * 100_000
    return out


def main():
    print("Missing observed-edge sweep; fanout=3 depth=3")
    for miss in (0.0, 0.05, 0.10, 0.20, 0.40):
        for policy in ("local_observed", "conservative_inferred", "whole_redraw"):
            print(miss, policy, agg(n=10_000, miss=miss, policy=policy))

    print("\nFanout/depth; miss=0; local vs whole")
    for fanout in (1, 2, 4, 8):
        for depth in (1, 2, 4):
            a = agg(n=5_000, fanout=fanout, depth=depth, miss=0.0, policy="local_observed")
            w = agg(n=5_000, fanout=fanout, depth=depth, miss=0.0, policy="whole_redraw")
            print(fanout, depth, a["correct_per_100k"], w["correct_per_100k"])

    print("\nVerifier information-set sweep; fanout=3 depth=3 miss=.05")
    for mode in ("independent", "correlated"):
        for policy in ("annotation", "local_observed", "provisional_confirm", "whole_redraw"):
            print(mode, policy, agg(n=20_000, miss=.05, policy=policy, vmode=mode))


if __name__ == "__main__":
    main()
