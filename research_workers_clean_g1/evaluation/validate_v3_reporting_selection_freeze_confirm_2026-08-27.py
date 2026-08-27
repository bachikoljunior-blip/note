"""Clean evaluation-only validation for post-selection reporting alpha allocation.

No O/downstream/other-worker inputs. This script checks:
1) an exact two-channel counterexample to same-history alpha reallocation;
2) the algebraic relation between e-BY FCR and strict two-bound SoS;
3) a synthetic null e-process stress comparing naive same-history selection,
   uniform all-pairs insurance, and a predictable freeze-and-confirm reset.
"""
from __future__ import annotations
import json
import math
import numpy as np

JOINT_ALPHA = 0.05
K = 9


def exact_counterexample():
    # Each E_i is a valid e-value: E_i=1/.045 with probability .045, else 0.
    # Select (.045,.005) when E1 is high, else (.005,.045) when E2 is high.
    # If either e-value is high, the selected report misses in at least one channel.
    p = 0.045
    return {
        "single_channel_e_mean": p * (1.0 / p),
        "selected_pair_miscoverage": 1.0 - (1.0 - p) ** 2,
        "nominal_joint_alpha": JOINT_ALPHA,
    }


def eby_sos_algebra():
    # With exactly two selected intervals, FCR=E[V]/2.
    # P(V>=1) <= E[V] <= 2*FCR, so strict SoS error <= delta follows
    # from FCR q<=delta/2. e-BY over 2K candidate intervals then uses
    # per-selected-interval alpha q*|S|/(2K)=delta/(2K), identical to
    # equal all-interval union insurance.
    q = JOINT_ALPHA / 2.0
    per_interval = q * 2.0 / (2.0 * K)
    return {
        "required_fcr_for_sos": q,
        "eby_per_selected_interval_alpha": per_interval,
        "uniform_union_per_interval_alpha": JOINT_ALPHA / (2.0 * K),
    }


def simulate(seed=20260827, n=200_000, horizon=200, pilot=40):
    rng = np.random.default_rng(seed)
    logp, logm = math.log(1.5), math.log(0.5)  # fair-sign e-factor mean = 1
    lw1 = np.zeros(n); lw2 = np.zeros(n)
    mx1 = np.zeros(n); mx2 = np.zeros(n)
    post1 = np.zeros(n); post2 = np.zeros(n)
    pmx1 = np.zeros(n); pmx2 = np.zeros(n)
    mx1_tau = mx2_tau = None

    for t in range(1, horizon + 1):
        inc1 = np.where(rng.random(n) < 0.5, logp, logm)
        inc2 = np.where(rng.random(n) < 0.5, logp, logm)
        lw1 += inc1; lw2 += inc2
        mx1 = np.maximum(mx1, lw1); mx2 = np.maximum(mx2, lw2)
        if t == pilot:
            mx1_tau = mx1.copy(); mx2_tau = mx2.copy()
        if t > pilot:
            post1 += inc1; post2 += inc2
            pmx1 = np.maximum(pmx1, post1); pmx2 = np.maximum(pmx2, post2)

    # Same finite allocation grid extremes as the 9-split V3 stress.
    # Give .045 to whichever channel had larger pilot running-max evidence.
    a1 = np.where(mx1_tau >= mx2_tau, 0.045, 0.005)
    a2 = JOINT_ALPHA - a1
    th1 = np.log(1.0 / a1); th2 = np.log(1.0 / a2)

    naive = np.mean((mx1 >= th1) | (mx2 >= th2))
    # Freeze allocation at pilot and restart reporting evidence from 1.
    freeze = np.mean((pmx1 >= th1) | (pmx2 >= th2))
    # Uniform pair insurance pi=1/K; same-history evidence is allowed because
    # all K candidate pairs are protected simultaneously.
    insured = np.mean((mx1 >= th1 + math.log(K)) | (mx2 >= th2 + math.log(K)))

    return {
        "seed": seed,
        "n": n,
        "horizon": horizon,
        "pilot": pilot,
        "naive_same_history_rate": float(naive),
        "freeze_confirm_rate": float(freeze),
        "uniform_all_pairs_insured_rate": float(insured),
    }


if __name__ == "__main__":
    out = {
        "exact_counterexample": exact_counterexample(),
        "eby_sos_algebra": eby_sos_algebra(),
        "synthetic_null_stress": simulate(),
    }
    print(json.dumps(out, indent=2, sort_keys=True))
