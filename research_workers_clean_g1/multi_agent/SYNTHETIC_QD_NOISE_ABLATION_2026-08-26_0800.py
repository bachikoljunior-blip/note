"""Reproduce C52 synthetic archive-decision-noise ablation.

Role-local synthetic experiment only. Absolute values are not external empirical claims.
Requires numpy; pandas is optional for formatting.
"""

import math
import itertools
import numpy as np


def cell_beta_params(i):
    return 2.0 + 0.35 * (i % 4), 2.6 + 0.25 * (i // 4)


def sample_proposal(rng, incumbent, cell):
    a, b = cell_beta_params(cell)
    if rng.random() < 0.55:
        return float(rng.beta(a, b))
    return float(np.clip(incumbent + rng.normal(0.04, 0.18), 0, 1))


class Challenger:
    __slots__ = ("q", "true_better", "first_verdict", "locked", "e", "n")

    def __init__(self, q, true_better, first_verdict, locked, e, n=1):
        self.q = q
        self.true_better = true_better
        self.first_verdict = first_verdict
        self.locked = locked
        self.e = e
        self.n = n


def verdict_for(rng, ch, q_fa, q_fr):
    if ch.locked:
        return ch.first_verdict
    p = (1 - q_fr) if ch.true_better else q_fa
    return bool(rng.random() < p)


def lr_update(e, verdict, q_fa, q_fr):
    p1 = 1 - q_fr
    p0 = q_fa
    if verdict:
        return e * (p1 / p0)
    return e * ((1 - p1) / (1 - p0))


def run_sequential(seed, q_fa, q_fr, rho, alpha, cap, timeout_mode,
                   budget=1200, n_cells=16, standby_rate=0.25,
                   standby_cap=4):
    rng = np.random.default_rng(seed)
    incumbents = np.array(
        [rng.beta(*cell_beta_params(i)) for i in range(n_cells)], dtype=float
    )
    active = [None] * n_cells
    standby = [[] for _ in range(n_cells)]
    proposals = true_prom = false_prom = total_prom = evals = 0
    standby_revisits = 0

    while evals < budget:
        c = int(rng.integers(0, n_cells))
        ch = active[c]

        if ch is not None:
            v = verdict_for(rng, ch, q_fa, q_fr)
            ch.n += 1
            evals += 1
            ch.e = lr_update(ch.e, v, q_fa, q_fr)
            if ch.e >= 1 / alpha:
                total_prom += 1
                if ch.q > incumbents[c]:
                    true_prom += 1
                else:
                    false_prom += 1
                incumbents[c] = ch.q
                active[c] = None
                if timeout_mode == "standby":
                    standby[c].clear()
            elif ch.e <= alpha:
                active[c] = None
            elif ch.n >= cap:
                if timeout_mode == "standby":
                    standby[c].append(ch)
                    standby[c].sort(key=lambda x: x.e, reverse=True)
                    standby[c] = standby[c][:standby_cap]
                active[c] = None
            continue

        if timeout_mode == "standby" and standby[c] and rng.random() < standby_rate:
            ch = standby[c].pop(0)
            v = verdict_for(rng, ch, q_fa, q_fr)
            ch.n += 1
            evals += 1
            standby_revisits += 1
            ch.e = lr_update(ch.e, v, q_fa, q_fr)
            if ch.e >= 1 / alpha:
                total_prom += 1
                if ch.q > incumbents[c]:
                    true_prom += 1
                else:
                    false_prom += 1
                incumbents[c] = ch.q
                standby[c].clear()
            elif ch.e > alpha:
                standby[c].append(ch)
                standby[c].sort(key=lambda x: x.e, reverse=True)
            continue

        x = sample_proposal(rng, incumbents[c], c)
        proposals += 1
        true_better = x > incumbents[c]
        locked = bool(rng.random() < rho)
        p = (1 - q_fr) if true_better else q_fa
        first = bool(rng.random() < p)
        evals += 1
        e = lr_update(1.0, first, q_fa, q_fr)
        ch = Challenger(x, true_better, first, locked, e, 1)

        if e >= 1 / alpha:
            total_prom += 1
            if true_better:
                true_prom += 1
            else:
                false_prom += 1
            incumbents[c] = x
            if timeout_mode == "standby":
                standby[c].clear()
        elif e <= alpha:
            pass
        elif cap <= 1:
            if timeout_mode == "standby":
                standby[c].append(ch)
                standby[c].sort(key=lambda z: z.e, reverse=True)
                standby[c] = standby[c][:standby_cap]
        else:
            active[c] = ch

    return {
        "quality": float(incumbents.mean()),
        "proposals": proposals,
        "true_promotions": true_prom,
        "false_promotions": false_prom,
        "false_promotion_fraction": false_prom / max(total_prom, 1),
        "standby_revisits": standby_revisits,
    }


def run_one_shot(seed, q_fa, q_fr, budget=1200, n_cells=16):
    rng = np.random.default_rng(seed)
    incumbents = np.array(
        [rng.beta(*cell_beta_params(i)) for i in range(n_cells)], dtype=float
    )
    false_prom = total_prom = 0
    for _ in range(budget):
        c = int(rng.integers(0, n_cells))
        x = sample_proposal(rng, incumbents[c], c)
        better = x > incumbents[c]
        p = (1 - q_fr) if better else q_fa
        if rng.random() < p:
            total_prom += 1
            if not better:
                false_prom += 1
            incumbents[c] = x
    return {
        "quality": float(incumbents.mean()),
        "proposals": budget,
        "false_promotion_fraction": false_prom / max(total_prom, 1),
    }


def run_provisional(seed, q_fa, q_fr, rho, budget=1200, n_cells=16):
    rng = np.random.default_rng(seed)
    incumbents = np.array(
        [rng.beta(*cell_beta_params(i)) for i in range(n_cells)], dtype=float
    )
    pending = [None] * n_cells
    evals = proposals = false_prom = total_prom = 0
    while evals < budget:
        c = int(rng.integers(0, n_cells))
        ch = pending[c]
        if ch is not None:
            v = verdict_for(rng, ch, q_fa, q_fr)
            evals += 1
            if v:
                total_prom += 1
                if ch.q <= incumbents[c]:
                    false_prom += 1
                incumbents[c] = ch.q
            pending[c] = None
            continue
        x = sample_proposal(rng, incumbents[c], c)
        proposals += 1
        better = x > incumbents[c]
        locked = bool(rng.random() < rho)
        p = (1 - q_fr) if better else q_fa
        first = bool(rng.random() < p)
        evals += 1
        if first:
            pending[c] = Challenger(x, better, first, locked, 1.0, 1)
    return {
        "quality": float(incumbents.mean()),
        "proposals": proposals,
        "false_promotion_fraction": false_prom / max(total_prom, 1),
    }


def summarize(results):
    keys = results[0].keys()
    return {k: float(np.mean([r[k] for r in results])) for k in keys}


def coarse_grid(reps=100):
    out = []
    for rho, q, alpha, cap, mode in itertools.product(
        [0.0, 0.6], [0.30, 0.35, 0.40], [0.05, 0.10, 0.20],
        [3, 4, 6], ["discard", "standby"]
    ):
        rs = []
        for r in range(reps):
            seed = (10_000_000 + int(rho * 10) * 1_000_000 +
                    int(q * 100) * 10_000 + int(alpha * 100) * 100 +
                    cap * 10 + r)
            rs.append(run_sequential(seed, q, q, rho, alpha, cap, mode))
        row = summarize(rs)
        row.update(dict(rho=rho, q=q, alpha=alpha, cap=cap, mode=mode))
        out.append(row)
    return out


def paired_q40(reps=200):
    q = 0.40
    for rho in [0.0, 0.6]:
        policies = {
            "one": [], "provisional": [],
            "strict_discard": [], "strict_standby": [],
            "relaxed_discard": [], "relaxed_standby": [],
        }
        for r in range(reps):
            seed = 40_000_000 + int(rho * 10) * 1_000_000 + r
            policies["one"].append(run_one_shot(seed, q, q))
            policies["provisional"].append(run_provisional(seed, q, q, rho))
            policies["strict_discard"].append(run_sequential(seed, q, q, rho, 0.10, 6, "discard"))
            policies["strict_standby"].append(run_sequential(seed, q, q, rho, 0.10, 6, "standby"))
            policies["relaxed_discard"].append(run_sequential(seed, q, q, rho, 0.30, 6, "discard"))
            policies["relaxed_standby"].append(run_sequential(seed, q, q, rho, 0.30, 6, "standby"))
        print("rho=", rho)
        for name, rs in policies.items():
            s = summarize(rs)
            print(name, s)
        ref = np.array([x["quality"] for x in policies["relaxed_standby"]])
        for name in ["one", "provisional", "strict_discard", "strict_standby", "relaxed_discard"]:
            x = np.array([z["quality"] for z in policies[name]])
            d = ref - x
            half = 1.96 * d.std(ddof=1) / math.sqrt(reps)
            print("relaxed_standby -", name, float(d.mean()), "+/-", float(half))


if __name__ == "__main__":
    paired_q40()
