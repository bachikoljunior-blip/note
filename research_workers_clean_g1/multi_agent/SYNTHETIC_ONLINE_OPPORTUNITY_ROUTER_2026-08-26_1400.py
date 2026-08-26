"""Role-local synthetic ablation for clean_g1 multi_agent, 2026-08-26 14:00 JST.

Not an external empirical claim. Core family: 16 cells, 1,200 evaluator-call
budget, proposal mixture from the predecessor synthetic line, rho_A=rho_B=.6,
three A calls then up to four B calls. The candidate decision is prior-aware
expected archive-quality loss. B is routed by its one-step expected value of
information (EVSI).

Policies:
  value   call B whenever EVSI_B > 0
  oracle  call B iff EVSI_B exceeds a deterministic 64-sample state-conditioned
          fresh A-only proposal value estimate (simulator-side oracle baseline)
  learned call B iff EVSI_B exceeds a strictly online cell x incumbent-bin
          estimate learned only from past completed A-only proposal pipelines

The selected online estimator has 10 incumbent bins, cell x bin local means,
zero-mean shrinkage, and O(1) update/inference. Optional ``ctrl_cost`` charges a
synthetic evaluator-call equivalent per inference/update; this exchange rate is
not physically calibrated.
"""
from __future__ import annotations
import math
import numpy as np

N_CELLS = 16
INC_GRID = np.round(np.linspace(0, 1, 101), 2)


def params(cell):
    return 2.0 + 0.35 * (cell % 4), 2.6 + 0.25 * (cell // 4)


def proposal(rng, inc, cell):
    a, b = params(cell)
    if rng.random() < 0.55:
        return float(rng.beta(a, b))
    return float(np.clip(inc + rng.normal(0.04, 0.18), 0, 1))


# Simulator-known proposal prior/magnitude table. This was already oracle-known
# in the predecessor utility controller; only the opportunity estimate is learned.
PRIOR = {}
for cell in range(N_CELLS):
    a, b = params(cell)
    for gi, inc in enumerate(INC_GRID):
        rng = np.random.default_rng(7_000_000 + cell * 10_000 + gi)
        n = 1600
        mix = rng.random(n) < 0.55
        xs = np.empty(n)
        xs[mix] = rng.beta(a, b, int(mix.sum()))
        xs[~mix] = np.clip(inc + rng.normal(0.04, 0.18, int((~mix).sum())), 0, 1)
        d = xs - inc
        pos, neg = d[d > 0], -d[d <= 0]
        PRIOR[(cell, gi)] = (
            max(1e-4, min(1 - 1e-4, float((d > 0).mean()))),
            float(pos.mean()) if len(pos) else 1e-6,
            float(neg.mean()) if len(neg) else 1e-6,
        )


def prior_stats(cell, inc):
    return PRIOR[(cell, int(np.clip(round(float(inc) * 100), 0, 100)))]


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


LIKES = {}
def build_likes(errors, cross, rho_a=.6, rho_b=.6):
    key = (tuple(errors), cross, rho_a, rho_b)
    if key in LIKES:
        return LIKES[key]
    qfa_a, qfr_a, qfa_b, qfr_b = errors
    tab = {}
    for truth in (0, 1):
        pa = (1 - qfr_a) if truth else qfa_a
        pb = (1 - qfr_b) if truth else qfa_b
        for ai in range(8):
            ah = tuple(bool((ai >> k) & 1) for k in range(3))
            a1, arep = ah[0], ah[1:]
            allsame = all(v == a1 for v in arep)
            af = rho_a * float(allsame) + (1 - rho_a) * bp(arep[0], pa) * bp(arep[1], pa)
            bhists = [()]
            for n in range(1, 5):
                bhists += [tuple(bool((bi >> k) & 1) for k in range(n)) for bi in range(2 ** n)]
            for bh in bhists:
                total = 0.0
                for blat in (False, True):
                    pfirst = pair_prob(a1, blat, pa, pb, cross)
                    if not bh:
                        bf = 1.0
                    else:
                        allb = all(v == bh[0] for v in bh)
                        fresh = 1.0
                        for v in bh:
                            fresh *= bp(v, pb)
                        bf = rho_b * float(allb and bh[0] == blat) + (1 - rho_b) * fresh
                    total += pfirst * bf
                tab[(truth, ah, bh)] = max(af * total, 1e-300)
    LIKES[key] = tab
    return tab


def posterior(prior, ah, bh, tab):
    l1, l0 = tab[(1, ah, bh)], tab[(0, ah, bh)]
    return prior * l1 / (prior * l1 + (1 - prior) * l0)


def decision(prior, mup, mun, ah, bh, tab):
    p = posterior(prior, ah, bh, tab)
    return ((1 - p) * mun < p * mup), p


def b_evsi(prior, mup, mun, ah, bh, tab):
    p = posterior(prior, ah, bh, tab)
    cur = min((1 - p) * mun, p * mup)
    l1, l0 = tab[(1, ah, bh)], tab[(0, ah, bh)]
    after = 0.0
    for v in (False, True):
        bh2 = bh + (v,)
        l1v, l0v = tab[(1, ah, bh2)], tab[(0, ah, bh2)]
        pv = p * (l1v / l1) + (1 - p) * (l0v / l0)
        p2 = prior * l1v / (prior * l1v + (1 - prior) * l0v)
        after += pv * min((1 - p2) * mun, p2 * mup)
    return max(0.0, cur - after)


def latents(rng, better, errors, cross, rho_a=.6, rho_b=.6):
    qfa_a, qfr_a, qfa_b, qfr_b = errors
    pa = (1 - qfr_a) if better else qfa_a
    pb = (1 - qfr_b) if better else qfa_b
    if rng.random() < cross:
        u = rng.random(); a1, blat = u < pa, u < pb
    else:
        a1, blat = rng.random() < pa, rng.random() < pb
    return bool(a1), bool(blat), rng.random() < rho_a, rng.random() < rho_b, pa, pb


def a_history(rng, lat):
    a1, _, alock, _, pa, _ = lat
    return (a1, a1 if alock else bool(rng.random() < pa), a1 if alock else bool(rng.random() < pa))


def b_verdict(rng, lat):
    _, blat, _, block, _, pb = lat
    return blat if block else bool(rng.random() < pb)


class OnlineOpportunity:
    """10 incumbent bins plus cell x bin local shrinkage; zero prior."""
    def __init__(self):
        self.bn = np.zeros(10, int); self.bs = np.zeros(10)
        self.cbn = np.zeros((N_CELLS, 10), int); self.cbs = np.zeros((N_CELLS, 10))
        self.pred_count = self.update_count = 0
        self.records = []

    @staticmethod
    def bi(inc):
        return min(9, int(float(inc) * 10))

    def predict(self, cell, inc):
        self.pred_count += 1
        b = self.bi(inc)
        bm = self.bs[b] / (self.bn[b] + 5.0)
        v = (self.cbs[cell, b] + 8.0 * bm) / (self.cbn[cell, b] + 8.0)
        return float(np.clip(v, 0.0, 0.10))

    def update(self, cell, inc, y, pred):
        self.update_count += 1
        b = self.bi(inc)
        self.records.append((b, pred, y))
        self.bn[b] += 1; self.bs[b] += y
        self.cbn[cell, b] += 1; self.cbs[cell, b] += y


ORACLE = {}
def oracle64(cell, inc, errors, cross, tab):
    gi = int(np.clip(round(float(inc) * 100), 0, 100))
    key = (cell, gi, tuple(errors), cross)
    if key in ORACLE:
        return ORACLE[key]
    incq = gi / 100
    rng = np.random.default_rng(8_100_000 + cell * 50_000 + gi * 31 + int(cross * 100) * 777 + int(sum(errors) * 1000))
    vals = []
    for _ in range(64):
        q = proposal(rng, incq, cell)
        better = q > incq
        prior, mup, mun = prior_stats(cell, incq)
        lat = latents(rng, better, errors, cross)
        ah = a_history(rng, lat)
        promote, _ = decision(prior, mup, mun, ah, (), tab)
        vals.append((q - incq) / 3 if promote else 0.0)
    ORACLE[key] = max(0.0, float(np.mean(vals)))
    return ORACLE[key]


def run(seed, errors, cross, mode, budget=1200, ctrl_cost=0.0):
    rng = np.random.default_rng(seed)
    tab = build_likes(errors, cross)
    incs = np.array([rng.beta(*params(i)) for i in range(N_CELLS)], float)
    learner = OnlineOpportunity()
    spent = 0.0; proposals = b_calls = promotions = false_prom = false_rej = aonly = 0

    while spent + 3 <= budget:
        cell = int(rng.integers(0, N_CELLS)); inc0 = float(incs[cell])
        q = proposal(rng, inc0, cell); proposals += 1; better = q > inc0
        prior, mup, mun = prior_stats(cell, inc0)
        lat = latents(rng, better, errors, cross); ah = a_history(rng, lat); spent += 3
        bh = (); pred = None
        if mode == "learned":
            pred = learner.predict(cell, inc0); spent += ctrl_cost
        used_b = False
        while len(bh) < 4 and spent + 1 <= budget:
            ev = b_evsi(prior, mup, mun, ah, bh, tab)
            if mode == "value": threshold = 0.0
            elif mode == "oracle": threshold = oracle64(cell, inc0, errors, cross, tab)
            elif mode == "learned": threshold = pred
            else: threshold = float("inf")
            if ev <= threshold + 1e-12:
                break
            bh += (b_verdict(rng, lat),); spent += 1; b_calls += 1; used_b = True

        promote, _ = decision(prior, mup, mun, ah, bh, tab)
        old = incs[cell]
        if promote:
            promotions += 1; false_prom += int(not better); incs[cell] = q
        else:
            false_rej += int(better)
        gain = float(incs[cell] - old)
        if not used_b:
            aonly += 1
            if mode == "learned":
                learner.update(cell, inc0, gain / 3.0, pred); spent += ctrl_cost

    return {
        "quality": float(incs.mean()), "proposals": proposals, "b_calls": b_calls,
        "false_promotion_fraction": false_prom / max(promotions, 1),
        "false_rejection_fraction": false_rej / max(proposals - promotions, 1),
        "aonly": aonly, "spent": spent,
        "predictor_ops": learner.pred_count + learner.update_count,
        "calibration_records": learner.records,
    }


def paired_summary(errors, cross, reps=300, base_seed=3_900_000_000):
    modes = ("value", "oracle", "learned")
    xs = {m: [] for m in modes}
    for r in range(reps):
        seed = base_seed + r + int(cross * 100_000)
        for m in modes:
            xs[m].append(run(seed, errors, cross, m))
    oq = np.array([z["quality"] for z in xs["oracle"]])
    vq = np.array([z["quality"] for z in xs["value"]])
    out = {}
    for m in modes:
        q = np.array([z["quality"] for z in xs[m]])
        out[m] = {
            "quality": float(q.mean()),
            "delta_vs_oracle": float((q - oq).mean()),
            "halfwidth95_vs_oracle": float(0 if m == "oracle" else 1.96 * (q - oq).std(ddof=1) / math.sqrt(reps)),
            "delta_vs_value": float((q - vq).mean()),
            "halfwidth95_vs_value": float(0 if m == "value" else 1.96 * (q - vq).std(ddof=1) / math.sqrt(reps)),
            "b_calls": float(np.mean([z["b_calls"] for z in xs[m]])),
            "proposals": float(np.mean([z["proposals"] for z in xs[m]])),
        }
    return out


if __name__ == "__main__":
    for name, errors, base in (
        ("asymmetric", (.40, .20, .20, .20), 3_900_000_000),
        ("symmetric", (.40, .40, .40, .40), 4_000_000_000),
    ):
        for cross in (0.0, 0.5, 1.0):
            print(name, cross, paired_summary(errors, cross, reps=300, base_seed=base + int(cross * 1_000_000)))
