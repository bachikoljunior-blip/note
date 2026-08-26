"""Role-local synthetic correlation-aware promotion ablation.

Not an external empirical claim. Reproduces the C54/C56 16-cell archive family
under a fixed 1,200 evaluator-call budget.

Modes:
  same      - repeat evaluator A after timeout.
  naive     - switch to B and multiply A/B likelihood ratios as if independent.
  discount  - switch to B but multiply B log-LR by (1 - cross_mix).
  separate  - keep B evidence separate; require B confirmation, otherwise abstain.

The final metric `effective_info_nats_per_call` is an explicit mechanistic proxy,
not exact mutual information. It uses equal-prior Jeffreys information per judge,
discounts repeated A/B calls by (1-rho), and discounts the first B call by
(1-cross_mix), because cross_mix couples only the first A/B verdict in this
generator.
"""
import math
import numpy as np


def bern_kl(p, q):
    eps = 1e-12
    p = min(max(p, eps), 1 - eps)
    q = min(max(q, eps), 1 - eps)
    return p * math.log(p / q) + (1 - p) * math.log((1 - p) / (1 - q))


def info_unit(q_fa, q_fr):
    p1, p0 = 1 - q_fr, q_fa
    return 0.5 * (bern_kl(p1, p0) + bern_kl(p0, p1))


def cell_beta_params(i):
    return 2.0 + 0.35 * (i % 4), 2.6 + 0.25 * (i // 4)


def sample_proposal(rng, incumbent, cell):
    a, b = cell_beta_params(cell)
    if rng.random() < 0.55:
        return float(rng.beta(a, b))
    return float(np.clip(incumbent + rng.normal(0.04, 0.18), 0, 1))


def loglr_increment(verdict, q_fa, q_fr):
    p1, p0 = 1 - q_fr, q_fa
    return math.log((p1 / p0) if verdict else ((1 - p1) / (1 - p0)))


def correlated_first_pair(rng, p_a, p_b, cross_mix):
    if rng.random() < cross_mix:
        u = rng.random()
        return bool(u < p_a), bool(u < p_b)
    return bool(rng.random() < p_a), bool(rng.random() < p_b)


class Challenger:
    __slots__ = (
        "q", "a_first", "a_locked", "b_first", "b_locked",
        "logA", "logB", "logCombined", "n_a", "n_b"
    )

    def __init__(self, q, a_first, a_locked, b_first, b_locked, inc_a):
        self.q = q
        self.a_first = a_first
        self.a_locked = a_locked
        self.b_first = b_first
        self.b_locked = b_locked
        self.logA = inc_a
        self.logB = 0.0
        self.logCombined = inc_a
        self.n_a = 1
        self.n_b = 0


def verdict_a(rng, ch, q_fa, q_fr, true_better):
    if ch.a_locked:
        return ch.a_first
    p = (1 - q_fr) if true_better else q_fa
    return bool(rng.random() < p)


def verdict_b(rng, ch, q_fa, q_fr, true_better):
    if ch.b_locked:
        return ch.b_first
    p = (1 - q_fr) if true_better else q_fa
    return bool(rng.random() < p)


def run(seed, qfa_a, qfr_a, qfa_b, qfr_b, cross_mix, mode="naive",
        rho_a=0.6, rho_b=0.6, alpha=0.20, cap_a=3, cap_b=4,
        revisit_rate=0.50, reservoir_cap=4, budget=1200, n_cells=16):
    rng = np.random.default_rng(seed)
    incumbents = np.array(
        [rng.beta(*cell_beta_params(i)) for i in range(n_cells)], dtype=float
    )
    active = [None] * n_cells
    standby = [[] for _ in range(n_cells)]

    evals = proposals = false_prom = true_prom = total_prom = 0
    b_calls = b_first_calls = b_repeat_calls = a_repeat_calls = abstentions = 0

    threshold = math.log(1 / alpha)
    reject = -threshold
    discount = max(0.0, 1.0 - cross_mix)
    info_a = info_unit(qfa_a, qfr_a)
    info_b = info_unit(qfa_b, qfr_b)

    def decide(ch, cell, evidence):
        nonlocal false_prom, true_prom, total_prom
        if evidence >= threshold:
            total_prom += 1
            better_now = ch.q > incumbents[cell]
            true_prom += int(better_now)
            false_prom += int(not better_now)
            incumbents[cell] = ch.q
            standby[cell].clear()
            return 1
        if evidence <= reject:
            return -1
        return 0

    while evals < budget:
        cell = int(rng.integers(0, n_cells))
        ch = active[cell]

        if ch is not None:
            better = ch.q > incumbents[cell]
            v = verdict_a(rng, ch, qfa_a, qfr_a, better)
            d = loglr_increment(v, qfa_a, qfr_a)
            ch.n_a += 1
            a_repeat_calls += 1
            evals += 1
            ch.logA += d
            ch.logCombined += d

            z = decide(ch, cell, ch.logA if mode == "separate" else ch.logCombined)
            if z:
                active[cell] = None
            elif ch.n_a >= cap_a:
                standby[cell].append(ch)
                standby[cell].sort(key=lambda x: x.logA, reverse=True)
                standby[cell] = standby[cell][:reservoir_cap]
                active[cell] = None
            continue

        if standby[cell] and rng.random() < revisit_rate:
            ch = standby[cell].pop(0)
            better = ch.q > incumbents[cell]
            evals += 1

            if mode == "same":
                v = verdict_a(rng, ch, qfa_a, qfr_a, better)
                d = loglr_increment(v, qfa_a, qfr_a)
                ch.n_a += 1
                a_repeat_calls += 1
                ch.logA += d
                ch.logCombined += d
                z = decide(ch, cell, ch.logCombined)
                if not z:
                    standby[cell].append(ch)
                    standby[cell].sort(key=lambda x: x.logCombined, reverse=True)
                    standby[cell] = standby[cell][:reservoir_cap]
                continue

            v = verdict_b(rng, ch, qfa_b, qfr_b, better)
            d = loglr_increment(v, qfa_b, qfr_b)
            ch.n_b += 1
            b_calls += 1
            if ch.n_b == 1:
                b_first_calls += 1
            else:
                b_repeat_calls += 1
            ch.logB += d

            if mode == "naive":
                ch.logCombined += d
                z = decide(ch, cell, ch.logCombined)
                if not z:
                    standby[cell].append(ch)
                    standby[cell].sort(key=lambda x: x.logCombined, reverse=True)
                    standby[cell] = standby[cell][:reservoir_cap]

            elif mode == "discount":
                evidence = ch.logA + discount * ch.logB
                z = decide(ch, cell, evidence)
                if not z:
                    standby[cell].append(ch)
                    standby[cell].sort(
                        key=lambda x: x.logA + discount * x.logB, reverse=True
                    )
                    standby[cell] = standby[cell][:reservoir_cap]

            elif mode == "separate":
                if ch.logB >= threshold and ch.logA > 0:
                    z = decide(ch, cell, threshold)
                elif ch.logB <= reject or ch.logA <= reject:
                    z = -1
                elif ch.n_b >= cap_b:
                    abstentions += 1
                    z = 2
                else:
                    z = 0
                if z == 0:
                    standby[cell].append(ch)
                    standby[cell].sort(key=lambda x: x.logB, reverse=True)
                    standby[cell] = standby[cell][:reservoir_cap]
            else:
                raise ValueError(mode)
            continue

        x = sample_proposal(rng, incumbents[cell], cell)
        proposals += 1
        better = x > incumbents[cell]
        p_a = (1 - qfr_a) if better else qfa_a
        p_b = (1 - qfr_b) if better else qfa_b
        a_first, b_first = correlated_first_pair(rng, p_a, p_b, cross_mix)
        a_locked = bool(rng.random() < rho_a)
        b_locked = bool(rng.random() < rho_b)
        evals += 1

        inc_a = loglr_increment(a_first, qfa_a, qfr_a)
        ch = Challenger(x, a_first, a_locked, b_first, b_locked, inc_a)
        if decide(ch, cell, inc_a) == 0:
            active[cell] = ch

    effective_info = (
        proposals * info_a
        + a_repeat_calls * (1 - rho_a) * info_a
        + b_first_calls * (1 - cross_mix) * info_b
        + b_repeat_calls * (1 - rho_b) * info_b
    )

    return {
        "quality": float(incumbents.mean()),
        "false_promotion_fraction": false_prom / max(total_prom, 1),
        "proposals": proposals,
        "b_calls": b_calls,
        "b_first_calls": b_first_calls,
        "b_repeat_calls": b_repeat_calls,
        "a_repeat_calls": a_repeat_calls,
        "abstentions": abstentions,
        "effective_info_nats_proxy": effective_info,
        "effective_info_nats_per_call": effective_info / evals,
    }


def summarize(rows):
    return {k: float(np.mean([r[k] for r in rows])) for k in rows[0]}


def paired_ci(a, b, key):
    d = np.array([x[key] - y[key] for x, y in zip(a, b)])
    return float(d.mean()), float(1.96 * d.std(ddof=1) / math.sqrt(len(d)))


def block(qfa_a, qfr_a, qfa_b, qfr_b, cross_mix, reps, base_seed):
    modes = ["same", "naive", "discount", "separate"]
    out = {m: [] for m in modes}
    for r in range(reps):
        seed = base_seed + int(cross_mix * 1000) * 100_000 + r
        for mode in modes:
            out[mode].append(
                run(seed, qfa_a, qfr_a, qfa_b, qfr_b, cross_mix, mode=mode)
            )
    return out


def print_block(name, qfa_a, qfr_a, qfa_b, qfr_b, reps, base):
    for cross_mix in (0.0, 0.5, 1.0):
        out = block(
            qfa_a, qfr_a, qfa_b, qfr_b, cross_mix, reps, base
        )
        print(name, "cross_mix=", cross_mix)
        for mode in ("same", "naive", "discount", "separate"):
            s = summarize(out[mode])
            if mode == "same":
                print(mode, s)
            else:
                print(
                    mode,
                    s,
                    "quality_delta_vs_same=", paired_ci(out[mode], out["same"], "quality"),
                    "fp_delta_vs_same=",
                    paired_ci(out[mode], out["same"], "false_promotion_fraction"),
                )


if __name__ == "__main__":
    print_block("symmetric", 0.40, 0.40, 0.40, 0.40, 150, 910_000_000)
    print_block("asymmetric", 0.40, 0.20, 0.20, 0.20, 150, 1_010_000_000)
