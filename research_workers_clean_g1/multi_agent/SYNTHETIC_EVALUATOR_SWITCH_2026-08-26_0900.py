"""C54 role-local synthetic evaluator-switch ablation.

Not an external empirical claim. Requires numpy. Reproduces the same synthetic
archive family as C52, with evaluator A used for the active gate and either the
same evaluator or evaluator B used for timeout revisits under a fixed 1,200-call
budget. Cross-evaluator dependence is a mixture of shared-vs-independent
uniform draws, which preserves each evaluator's marginal pass probability.
"""

import math
import numpy as np


def cell_beta_params(i):
    return 2.0 + 0.35 * (i % 4), 2.6 + 0.25 * (i // 4)


def sample_proposal(rng, incumbent, cell):
    a, b = cell_beta_params(cell)
    if rng.random() < 0.55:
        return float(rng.beta(a, b))
    return float(np.clip(incumbent + rng.normal(0.04, 0.18), 0, 1))


def lr_update(e, verdict, q_fa, q_fr):
    p1 = 1 - q_fr
    p0 = q_fa
    if verdict:
        return e * (p1 / p0)
    return e * ((1 - p1) / (1 - p0))


def correlated_first_pair(rng, p_a, p_b, cross_mix):
    # With probability cross_mix, both judges threshold the same U; otherwise
    # they use independent U values. Marginals remain p_a and p_b exactly.
    if rng.random() < cross_mix:
        u = rng.random()
        return bool(u < p_a), bool(u < p_b)
    return bool(rng.random() < p_a), bool(rng.random() < p_b)


class Challenger:
    __slots__ = (
        "q", "true_better", "a_first", "a_locked", "b_first", "b_locked",
        "e", "n_a", "n_b"
    )

    def __init__(self, q, true_better, a_first, a_locked, b_first, b_locked, e):
        self.q = q
        self.true_better = true_better
        self.a_first = a_first
        self.a_locked = a_locked
        self.b_first = b_first
        self.b_locked = b_locked
        self.e = e
        self.n_a = 1
        self.n_b = 0


def verdict_a(rng, ch, q_fa, q_fr):
    if ch.a_locked:
        return ch.a_first
    p = (1 - q_fr) if ch.true_better else q_fa
    return bool(rng.random() < p)


def verdict_b(rng, ch, q_fa, q_fr):
    if ch.b_locked:
        return ch.b_first
    p = (1 - q_fr) if ch.true_better else q_fa
    return bool(rng.random() < p)


def run(seed, qfa_a, qfr_a, qfa_b, qfr_b, cross_mix,
        mode="switch", rho_a=0.6, rho_b=0.6, alpha=0.20, cap_a=3,
        revisit_rate=0.50, reservoir_cap=4, budget=1200, n_cells=16):
    rng = np.random.default_rng(seed)
    incumbents = np.array([
        rng.beta(*cell_beta_params(i)) for i in range(n_cells)
    ], dtype=float)
    active = [None] * n_cells
    standby = [[] for _ in range(n_cells)]
    evals = proposals = false_prom = true_prom = total_prom = 0
    revisit_calls = b_calls = a_revisit_calls = 0

    while evals < budget:
        c = int(rng.integers(0, n_cells))
        ch = active[c]

        if ch is not None:
            v = verdict_a(rng, ch, qfa_a, qfr_a)
            ch.n_a += 1
            evals += 1
            ch.e = lr_update(ch.e, v, qfa_a, qfr_a)
            if ch.e >= 1 / alpha:
                total_prom += 1
                true_prom += int(ch.q > incumbents[c])
                false_prom += int(ch.q <= incumbents[c])
                incumbents[c] = ch.q
                active[c] = None
                standby[c].clear()
            elif ch.e <= alpha:
                active[c] = None
            elif ch.n_a >= cap_a:
                standby[c].append(ch)
                standby[c].sort(key=lambda z: z.e, reverse=True)
                standby[c] = standby[c][:reservoir_cap]
                active[c] = None
            continue

        if standby[c] and rng.random() < revisit_rate:
            ch = standby[c].pop(0)
            revisit_calls += 1
            evals += 1
            if mode == "switch":
                v = verdict_b(rng, ch, qfa_b, qfr_b)
                ch.n_b += 1
                b_calls += 1
                ch.e = lr_update(ch.e, v, qfa_b, qfr_b)
            else:
                v = verdict_a(rng, ch, qfa_a, qfr_a)
                ch.n_a += 1
                a_revisit_calls += 1
                ch.e = lr_update(ch.e, v, qfa_a, qfr_a)
            if ch.e >= 1 / alpha:
                total_prom += 1
                true_prom += int(ch.q > incumbents[c])
                false_prom += int(ch.q <= incumbents[c])
                incumbents[c] = ch.q
                standby[c].clear()
            elif ch.e > alpha:
                standby[c].append(ch)
                standby[c].sort(key=lambda z: z.e, reverse=True)
                standby[c] = standby[c][:reservoir_cap]
            continue

        x = sample_proposal(rng, incumbents[c], c)
        proposals += 1
        better = x > incumbents[c]
        p_a = (1 - qfr_a) if better else qfa_a
        p_b = (1 - qfr_b) if better else qfa_b
        a_first, b_first = correlated_first_pair(rng, p_a, p_b, cross_mix)
        a_locked = bool(rng.random() < rho_a)
        b_locked = bool(rng.random() < rho_b)
        evals += 1
        e = lr_update(1.0, a_first, qfa_a, qfr_a)
        ch = Challenger(x, better, a_first, a_locked, b_first, b_locked, e)
        if e >= 1 / alpha:
            total_prom += 1
            true_prom += int(better)
            false_prom += int(not better)
            incumbents[c] = x
            standby[c].clear()
        elif e <= alpha:
            pass
        else:
            active[c] = ch

    return {
        "quality": float(incumbents.mean()),
        "proposals": proposals,
        "false_promotion_fraction": false_prom / max(total_prom, 1),
        "false_promotions": false_prom,
        "true_promotions": true_prom,
        "revisit_calls": revisit_calls,
        "b_calls": b_calls,
        "a_revisit_calls": a_revisit_calls,
    }


def summarize(rs):
    return {k: float(np.mean([r[k] for r in rs])) for k in rs[0]}


def paired_ci(a, b, key="quality"):
    d = np.array([x[key] - y[key] for x, y in zip(a, b)])
    return float(d.mean()), float(1.96 * d.std(ddof=1) / math.sqrt(len(d)))


def symmetric_sweep(reps=150):
    crosses = [0.0, 0.25, 0.50, 0.75, 1.0]
    for qb in [0.40, 0.35, 0.30, 0.25, 0.20]:
        same = []
        for r in range(reps):
            seed = 170_000_000 + int(qb * 1000) * 10_000 + r
            same.append(run(seed, 0.40, 0.40, qb, qb, 0.0, mode="same"))
        print("qB", qb, "same", summarize(same))
        for cross in crosses:
            sw = []
            for r in range(reps):
                seed = 170_000_000 + int(qb * 1000) * 10_000 + r
                sw.append(run(seed, 0.40, 0.40, qb, qb, cross, mode="switch"))
            print(" cross", cross, summarize(sw), "quality_delta", paired_ci(sw, same))


def asymmetric_high_power(reps=500):
    # High false-admission / lower false-rejection A; B improves q_FA only.
    for cross in [0.0, 1.0]:
        same, sw = [], []
        for r in range(reps):
            seed = 190_000_000 + int(cross * 10) * 1_000_000 + r
            same.append(run(seed, 0.40, 0.20, 0.20, 0.20, 0.0, mode="same"))
            sw.append(run(seed, 0.40, 0.20, 0.20, 0.20, cross, mode="switch"))
        print("asym cross", cross, "same", summarize(same), "switch", summarize(sw),
              "quality_delta", paired_ci(sw, same),
              "fp_delta", paired_ci(sw, same, "false_promotion_fraction"))


if __name__ == "__main__":
    symmetric_sweep()
    asymmetric_high_power()
