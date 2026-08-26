"""Matched-budget synthetic recovery harness for multi-agent state repair.

Frozen semantic tuple:
- note main SHA: 57b44c6166ffc99fc3232b32dffa07376768c008
- control revision: 10
- config revision: 6
- role config blob: 9a3edbe40ee5cbf3a94fe3206606aa58841c955c

The harness has two roots, S and independent U. A reads S, B reads A, C reads U,
and D reads B+C. A verifier checks S after A/C materialize. Recovery policies:
annotation-only, hard canonical replacement without replay, observed dependency-closed
replay, whole redraw, plus an inferred-dense diagnostic that treats every earlier step
as a dependency. The total-budget comparison reports correct endpoints per fixed call
and token budget, so cheaper policies process more tasks rather than receiving free
extra work.
"""
from __future__ import annotations

from dataclasses import dataclass
import random
from collections import defaultdict


@dataclass
class Params:
    p_source_corrupt: float = 0.35
    p_model_correct: float = 0.97
    verifier_tpr: float = 0.88
    verifier_fpr: float = 0.05
    correction_accuracy_when_wrong: float = 0.94
    false_positive_bad_replacement: float = 0.90
    annotation_heed: float = 0.75
    repeat_corr: float = 0.60
    model_tokens: int = 1000
    verifier_tokens: int = 250


def fA(s): return 2 * s + 1

def fB(a): return a + 5

def fC(u): return 3 * u - 2

def fD(b, c): return b - c


def perturb(v, rng):
    return v + (1 if rng.random() < 0.5 else -1)


def model_call(func, args, rng, p):
    truth = func(*args)
    return truth if rng.random() < p.p_model_correct else perturb(truth, rng)


def verifier(active_s, true_s, rng, p, prev=None, same_version=False):
    if prev is not None and same_version and rng.random() < p.repeat_corr:
        return prev
    if active_s != true_s:
        if rng.random() >= p.verifier_tpr:
            return False, None
        if rng.random() < p.correction_accuracy_when_wrong:
            return True, true_s
        proposal = active_s if rng.random() < 0.5 else true_s + (2 if rng.random() < 0.5 else -2)
        if proposal == true_s:
            proposal += 1
        return True, proposal
    if rng.random() >= p.verifier_fpr:
        return False, None
    if rng.random() < p.false_positive_bad_replacement:
        return True, true_s + (1 if rng.random() < 0.5 else -1)
    return True, true_s


def run_task(policy, seed, p=Params()):
    rng = random.Random(seed)
    true_s = rng.randint(5, 15)
    true_u = rng.randint(3, 12)
    target = fD(fB(fA(true_s)), fC(true_u))
    active_s = true_s + (2 if rng.random() < 0.5 else -2) if rng.random() < p.p_source_corrupt else true_s
    source_version = 0
    calls = model_calls = verifier_calls = tokens = 0
    latency_steps = 0

    # A and C are independent and can be parallel.
    a = model_call(fA, (active_s,), rng, p)
    c = model_call(fC, (true_u,), rng, p)
    a_version = source_version
    calls += 2; model_calls += 2; tokens += 2 * p.model_tokens; latency_steps += 1

    v1 = verifier(active_s, true_s, rng, p)
    flag1, proposal = v1
    calls += 1; verifier_calls += 1; tokens += p.verifier_tokens; latency_steps += 1
    correction_applied = False

    if policy == "annotation":
        if flag1 and proposal is not None and rng.random() < p.annotation_heed:
            b = model_call(lambda s: fB(fA(s)), (proposal,), rng, p)
            b_version = ("annotation", proposal)
        else:
            b = model_call(fB, (a,), rng, p)
            b_version = a_version
        calls += 1; model_calls += 1; tokens += p.model_tokens; latency_steps += 1

    elif policy == "hard_no_replay":
        if flag1 and proposal is not None:
            active_s = proposal; source_version += 1; correction_applied = True
        b = model_call(fB, (a,), rng, p)
        b_version = a_version
        calls += 1; model_calls += 1; tokens += p.model_tokens; latency_steps += 1

    elif policy == "local_replay":
        if flag1 and proposal is not None:
            active_s = proposal; source_version += 1; correction_applied = True
            a = model_call(fA, (active_s,), rng, p)
            a_version = source_version
            calls += 1; model_calls += 1; tokens += p.model_tokens; latency_steps += 1
        b = model_call(fB, (a,), rng, p)
        b_version = a_version
        calls += 1; model_calls += 1; tokens += p.model_tokens; latency_steps += 1

    elif policy in ("whole_redraw", "local_inferred_dense"):
        if flag1 and proposal is not None:
            active_s = proposal; source_version += 1; correction_applied = True
            # whole redraw, or full-context inferred dependency closure, replays C too.
            a = model_call(fA, (active_s,), rng, p)
            c = model_call(fC, (true_u,), rng, p)
            a_version = source_version
            calls += 2; model_calls += 2; tokens += 2 * p.model_tokens; latency_steps += 1
        b = model_call(fB, (a,), rng, p)
        b_version = a_version
        calls += 1; model_calls += 1; tokens += p.model_tokens; latency_steps += 1
    else:
        raise ValueError(policy)

    d = model_call(fD, (b, c), rng, p)
    calls += 1; model_calls += 1; tokens += p.model_tokens; latency_steps += 1

    same_version = not correction_applied
    v2 = verifier(active_s, true_s, rng, p, prev=v1, same_version=same_version)
    flag2, _ = v2
    calls += 1; verifier_calls += 1; tokens += p.verifier_tokens; latency_steps += 1

    stale = correction_applied and isinstance(b_version, int) and b_version != source_version
    return {
        "endpoint_correct": d == target,
        "source_restored": active_s == true_s,
        "validated_wrong": (not flag2) and d != target,
        "repeat_intervention": bool(flag1 and flag2 and same_version),
        "calls": calls,
        "tokens": tokens,
        "latency_steps": latency_steps,
        "stale_descendant": stale,
    }


def aggregate(policy, n=50_000, p=Params()):
    rows = [run_task(policy, i, p) for i in range(n)]
    out = {}
    for key in rows[0]:
        out[key] = sum(float(r[key]) for r in rows) / n
    out["correct_per_100k_calls"] = out["endpoint_correct"] / out["calls"] * 100_000
    out["correct_per_1m_tokens"] = out["endpoint_correct"] / out["tokens"] * 1_000_000
    return out


def main():
    policies = ["annotation", "hard_no_replay", "local_replay", "whole_redraw", "local_inferred_dense"]
    for pol in policies:
        print(pol, aggregate(pol))

    print("\nCorrection-accuracy sweep (throughput comparison)")
    for q in [0.50, 0.62, 0.74, 0.86, 0.92, 0.98]:
        p = Params(verifier_tpr=0.85, verifier_fpr=0.08,
                   correction_accuracy_when_wrong=q, repeat_corr=0.60)
        a = aggregate("annotation", n=20_000, p=p)
        l = aggregate("local_replay", n=20_000, p=p)
        print(q, a["correct_per_100k_calls"], l["correct_per_100k_calls"])

    print("\nFalse-positive sweep")
    for fpr in [0.00, 0.05, 0.10, 0.15, 0.20]:
        p = Params(verifier_tpr=0.88, verifier_fpr=fpr,
                   correction_accuracy_when_wrong=0.94, repeat_corr=0.60)
        a = aggregate("annotation", n=20_000, p=p)
        l = aggregate("local_replay", n=20_000, p=p)
        print(fpr, a["correct_per_100k_calls"], l["correct_per_100k_calls"], l["source_restored"])


if __name__ == "__main__":
    main()
