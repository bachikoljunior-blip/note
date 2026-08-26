"""Role-local synthetic judge-dependence ablation for clean_g1 multi_agent.

Not an external empirical claim. Fixed family: 16 archive cells, 1,200 evaluator
calls, rho_A=rho_B=0.6, active A cap=3, reversible standby reservoir cap=4,
revisit rate=0.5, alpha=0.20 unless overridden.

Important generator detail preserved from the predecessor implementation:
`b_latent` is correlated with A's first verdict, but the first *observed* B verdict
uses that latent only when B is locked. If B is unlocked, every observed B call is
fresh. Thus the effective first-observed-A/B coupling is rho_B * cross_mix, not
cross_mix itself.

Modes:
  same      repeat A after timeout
  naive     switch to B and add marginal log likelihood ratios
  discount  predecessor scalar discount (1-cross_mix) on B evidence
  separate  independent B confirmation with cap
  pair      correct only the first observed A/B joint likelihood; keep later
            repeat evidence marginal/naive
  lock      exact history likelihood for within-evaluator lock dependence while
            intentionally assuming cross-evaluator independence
  joint     exact history likelihood under the implemented generator including
            within-evaluator locks and cross-evaluator first-latent coupling
"""
import math
import numpy as np


def bp(v, p):
    return p if v else 1 - p


def pair_prob(a, b, pa, pb, c):
    ind = bp(a, pa) * bp(b, pb)
    if a and b:
        com = min(pa, pb)
    elif a and not b:
        com = max(pa - pb, 0.0)
    elif (not a) and b:
        com = max(pb - pa, 0.0)
    else:
        com = 1.0 - max(pa, pb)
    return (1 - c) * ind + c * com


def llr(v, qfa, qfr):
    p1, p0 = 1 - qfr, qfa
    return math.log((p1 / p0) if v else ((1 - p1) / (1 - p0)))


def params(i):
    return 2.0 + 0.35 * (i % 4), 2.6 + 0.25 * (i // 4)


def proposal(rng, incumbent, cell):
    a, b = params(cell)
    if rng.random() < 0.55:
        return float(rng.beta(a, b))
    x = incumbent + rng.normal(0.04, 0.18)
    return float(min(1.0, max(0.0, x)))


def first_pair(rng, pa, pb, c):
    if rng.random() < c:
        u = rng.random()
        return bool(u < pa), bool(u < pb)
    return bool(rng.random() < pa), bool(rng.random() < pb)


class Ch:
    __slots__ = (
        "q", "a1", "a_lock", "b_latent", "b_lock", "log_a", "log_b",
        "log_combined", "n_a", "n_b", "a_n", "a_ones", "a_all_first",
        "b_n", "b_ones", "b_all_first", "pair_adjust"
    )

    def __init__(self, q, a1, a_lock, b_latent, b_lock, first_a_llr):
        self.q = q
        self.a1 = a1
        self.a_lock = a_lock
        self.b_latent = b_latent
        self.b_lock = b_lock
        self.log_a = first_a_llr
        self.log_b = 0.0
        self.log_combined = first_a_llr
        self.n_a = 1
        self.n_b = 0
        self.a_n = 1
        self.a_ones = int(a1)
        self.a_all_first = True
        self.b_n = 0
        self.b_ones = 0
        self.b_all_first = True
        self.pair_adjust = 0.0


def count_prob(n, ones, p):
    return (p ** ones) * ((1 - p) ** (n - ones))


def history_llr(ch, qfa_a, qfr_a, qfa_b, qfr_b, cross_mix, rho_a, rho_b):
    vals = []
    for truth in (1, 0):
        pa = (1 - qfr_a) if truth else qfa_a
        pb = (1 - qfr_b) if truth else qfa_b
        a_rep_n = ch.a_n - 1
        a_rep_ones = ch.a_ones - int(ch.a1)
        a_factor = rho_a * (1.0 if ch.a_all_first else 0.0) + (1 - rho_a) * count_prob(a_rep_n, a_rep_ones, pa)
        b_sum = 0.0
        for b_latent in (False, True):
            p_first = pair_prob(ch.a1, b_latent, pa, pb, cross_mix)
            if ch.b_n == 0:
                b_factor = 1.0
            elif ch.b_all_first:
                first_observed_b = bool(ch.b_ones == ch.b_n)
                lock_like = 1.0 if first_observed_b == b_latent else 0.0
                b_factor = rho_b * lock_like + (1 - rho_b) * count_prob(ch.b_n, ch.b_ones, pb)
            else:
                b_factor = (1 - rho_b) * count_prob(ch.b_n, ch.b_ones, pb)
            b_sum += p_first * b_factor
        vals.append(max(a_factor * b_sum, 1e-300))
    return math.log(vals[0] / vals[1])


def observed_pair_llr(a, b, qfa_a, qfr_a, qfa_b, qfr_b, cross_mix, rho_b):
    vals = []
    for truth in (1, 0):
        pa = (1 - qfr_a) if truth else qfa_a
        pb = (1 - qfr_b) if truth else qfa_b
        p = rho_b * pair_prob(a, b, pa, pb, cross_mix) + (1 - rho_b) * bp(a, pa) * bp(b, pb)
        vals.append(max(p, 1e-300))
    return math.log(vals[0] / vals[1])


def verdict_a(rng, ch, qfa, qfr, better):
    if ch.a_lock:
        return ch.a1
    return bool(rng.random() < ((1 - qfr) if better else qfa))


def verdict_b(rng, ch, qfa, qfr, better):
    if ch.b_lock:
        return ch.b_latent
    return bool(rng.random() < ((1 - qfr) if better else qfa))


def run(seed, errors, cross_mix, mode, budget=1200, n_cells=16, rho_a=0.6, rho_b=0.6,
        alpha=0.20, cap_a=3, cap_b=4, revisit=0.50, reservoir_cap=4):
    qfa_a, qfr_a, qfa_b, qfr_b = errors
    rng = np.random.default_rng(seed)
    incumbents = np.array([rng.beta(*params(i)) for i in range(n_cells)], dtype=float)
    active = [None] * n_cells
    standby = [[] for _ in range(n_cells)]
    evals = proposals = false_prom = total_prom = b_calls = abstentions = 0
    threshold = math.log(1 / alpha)
    reject = -threshold
    discount = max(0.0, 1.0 - cross_mix)

    def evidence(ch):
        if mode in ("same", "naive"):
            return ch.log_combined
        if mode == "discount":
            return ch.log_a + discount * ch.log_b
        if mode == "separate":
            return ch.log_b
        if mode == "pair":
            return ch.log_combined + ch.pair_adjust
        if mode == "lock":
            return history_llr(ch, qfa_a, qfr_a, qfa_b, qfr_b, 0.0, rho_a, rho_b)
        if mode == "joint":
            return history_llr(ch, qfa_a, qfr_a, qfa_b, qfr_b, cross_mix, rho_a, rho_b)
        raise ValueError(mode)

    def decide(ch, cell, ev):
        nonlocal false_prom, total_prom
        if ev >= threshold:
            total_prom += 1
            false_prom += int(not (ch.q > incumbents[cell]))
            incumbents[cell] = ch.q
            standby[cell].clear()
            return 1
        if ev <= reject:
            return -1
        return 0

    while evals < budget:
        cell = int(rng.integers(0, n_cells))
        ch = active[cell]
        if ch is not None:
            better = ch.q > incumbents[cell]
            v = verdict_a(rng, ch, qfa_a, qfr_a, better)
            d = llr(v, qfa_a, qfr_a)
            ch.n_a += 1
            ch.log_a += d
            ch.log_combined += d
            ch.a_n += 1
            ch.a_ones += int(v)
            ch.a_all_first = ch.a_all_first and (v == ch.a1)
            evals += 1
            ev = evidence(ch) if mode in ("pair", "lock", "joint") else (ch.log_a if mode == "separate" else ch.log_combined)
            z = decide(ch, cell, ev)
            if z:
                active[cell] = None
            elif ch.n_a >= cap_a:
                standby[cell].append(ch)
                standby[cell].sort(key=evidence, reverse=True)
                standby[cell] = standby[cell][:reservoir_cap]
                active[cell] = None
            continue

        if standby[cell] and rng.random() < revisit:
            ch = standby[cell].pop(0)
            better = ch.q > incumbents[cell]
            evals += 1
            if mode == "same":
                v = verdict_a(rng, ch, qfa_a, qfr_a, better)
                d = llr(v, qfa_a, qfr_a)
                ch.n_a += 1
                ch.log_a += d
                ch.log_combined += d
                ch.a_n += 1
                ch.a_ones += int(v)
                ch.a_all_first = ch.a_all_first and (v == ch.a1)
                z = decide(ch, cell, ch.log_combined)
            else:
                v = verdict_b(rng, ch, qfa_b, qfr_b, better)
                d = llr(v, qfa_b, qfr_b)
                ch.n_b += 1
                ch.log_b += d
                ch.log_combined += d
                ch.b_n += 1
                ch.b_ones += int(v)
                if ch.b_n == 1:
                    ch.b_all_first = True
                else:
                    prev_n = ch.b_n - 1
                    prev_ones = ch.b_ones - int(v)
                    prior_first = True if prev_ones == prev_n else (False if prev_ones == 0 else None)
                    ch.b_all_first = ch.b_all_first and prior_first is not None and (v == prior_first)
                b_calls += 1
                if mode == "pair" and ch.n_b == 1:
                    ch.pair_adjust = observed_pair_llr(ch.a1, v, qfa_a, qfr_a, qfa_b, qfr_b, cross_mix, rho_b) - llr(ch.a1, qfa_a, qfr_a) - d
                if mode == "separate":
                    if ch.log_b >= threshold and ch.log_a > 0:
                        z = decide(ch, cell, threshold)
                    elif ch.log_b <= reject or ch.log_a <= reject:
                        z = -1
                    elif ch.n_b >= cap_b:
                        abstentions += 1
                        z = 2
                    else:
                        z = 0
                else:
                    z = decide(ch, cell, evidence(ch))
            if z == 0:
                standby[cell].append(ch)
                standby[cell].sort(key=evidence, reverse=True)
                standby[cell] = standby[cell][:reservoir_cap]
            continue

        x = proposal(rng, incumbents[cell], cell)
        proposals += 1
        better = x > incumbents[cell]
        pa = (1 - qfr_a) if better else qfa_a
        pb = (1 - qfr_b) if better else qfa_b
        a1, b_latent = first_pair(rng, pa, pb, cross_mix)
        a_lock = bool(rng.random() < rho_a)
        b_lock = bool(rng.random() < rho_b)
        evals += 1
        ch = Ch(x, a1, a_lock, b_latent, b_lock, llr(a1, qfa_a, qfr_a))
        ev = evidence(ch) if mode in ("lock", "joint") else ch.log_a
        if decide(ch, cell, ev) == 0:
            active[cell] = ch

    return {
        "quality": float(incumbents.mean()),
        "false_promotion_fraction": false_prom / max(total_prom, 1),
        "proposals": proposals,
        "b_calls": b_calls,
        "promotions": total_prom,
        "abstentions": abstentions,
    }


def summarize(errors, cross_mix, reps=100, base_seed=1_510_000_000, alpha=0.20):
    modes = ("same", "naive", "discount", "separate", "pair", "lock", "joint")
    out = {m: [] for m in modes}
    for r in range(reps):
        seed = base_seed + int(cross_mix * 1000) * 100_000 + r
        for m in modes:
            out[m].append(run(seed, errors, cross_mix, m, alpha=alpha))
    base = np.array([x["quality"] for x in out["same"]])
    rows = {}
    for m in modes:
        q = np.array([x["quality"] for x in out[m]])
        fp = np.array([x["false_promotion_fraction"] for x in out[m]])
        d = q - base
        rows[m] = {
            "quality": float(q.mean()),
            "false_promotion_fraction": float(fp.mean()),
            "proposals": float(np.mean([x["proposals"] for x in out[m]])),
            "b_calls": float(np.mean([x["b_calls"] for x in out[m]])),
            "promotions": float(np.mean([x["promotions"] for x in out[m]])),
            "paired_quality_delta_vs_same": float(d.mean()),
            "paired_quality_95pct_halfwidth": float(0.0 if m == "same" else 1.96 * d.std(ddof=1) / math.sqrt(reps)),
        }
    return rows


if __name__ == "__main__":
    for name, errors, seed in (
        ("symmetric", (0.40, 0.40, 0.40, 0.40), 1_510_000_000),
        ("asymmetric", (0.40, 0.20, 0.20, 0.20), 1_610_000_000),
    ):
        for c in (0.0, 0.5, 1.0):
            print(name, c, summarize(errors, c, reps=100, base_seed=seed))
