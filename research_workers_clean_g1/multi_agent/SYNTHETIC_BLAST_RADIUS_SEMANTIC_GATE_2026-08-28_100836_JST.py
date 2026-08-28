#!/usr/bin/env python3
"""Deterministic mechanism study for blast-radius-sensitive semantic correction.

This script reproduces the synthetic calculations checkpointed by the CLEAN
multi_agent role on 2026-08-28. It is not a production threshold estimator.

Model:
  p_help = P(candidate verifier B helps | current verifier A is wrong,
             same construct and calibration slice)
  p_harm = P(B harms | A is correct, same construct and slice)
  pi     = prevalence that A is wrong in the slice
  H      = destructive-harm multiplier (blast radius / irreversibility proxy)
  cost   = normalized extra-call / promotion cost

Expected utility:
    U = pi * p_help - (1-pi) * H * p_harm - cost

Two decision rules are compared:
  1) plug-in posterior-mean utility under independent Jeffreys priors;
  2) conservative 95% equal-tailed bound:
       U_LB = pi * LCB95(p_help)
              - (1-pi) * H * UCB95(p_harm)
              - cost
     and destructive promotion is allowed only if U_LB > 0.

Dependencies: numpy, scipy.
"""

from __future__ import annotations

import json
import numpy as np
from scipy.stats import beta

SEED = 20260828
PI = 0.25
COST = 0.01
ALPHA = 0.05


def jeffreys_bounds(k: int, n: int, alpha: float = ALPHA):
    a = k + 0.5
    b = n - k + 0.5
    return (
        float(beta.ppf(alpha / 2, a, b)),
        float(beta.ppf(1 - alpha / 2, a, b)),
        a / (a + b),
    )


def conservative_utility_lb(
    helpful: int,
    n_help: int,
    harmful: int,
    n_harm: int,
    harm_multiplier: float,
    pi: float = PI,
    cost: float = COST,
    alpha: float = ALPHA,
):
    l_help, _, _ = jeffreys_bounds(helpful, n_help, alpha)
    _, u_harm, _ = jeffreys_bounds(harmful, n_harm, alpha)
    return pi * l_help - (1 - pi) * harm_multiplier * u_harm - cost


def support_threshold(
    harm_multiplier: float,
    p_help: float = 0.65,
    p_harm: float = 0.03,
    max_n: int = 20000,
):
    true_utility = PI * p_help - (1 - PI) * harm_multiplier * p_harm - COST
    if true_utility <= 0:
        return {
            "harm_multiplier": harm_multiplier,
            "true_utility": true_utility,
            "first_certifying_n": None,
            "reason": "negative_or_zero_asymptotic_utility",
        }
    for n in range(1, max_n + 1):
        helpful = round(p_help * n)
        harmful = round(p_harm * n)
        u_lb = conservative_utility_lb(
            helpful, n, harmful, n, harm_multiplier
        )
        if u_lb > 0:
            return {
                "harm_multiplier": harm_multiplier,
                "true_utility": true_utility,
                "first_certifying_n": n,
                "helpful_count": helpful,
                "harmful_count": harmful,
                "utility_lower_bound": u_lb,
            }
    return {
        "harm_multiplier": harm_multiplier,
        "true_utility": true_utility,
        "first_certifying_n": None,
        "reason": f"not_certified_by_n_{max_n}",
    }


def monte_carlo_grid(seed: int = SEED, reps: int = 300):
    rng = np.random.default_rng(seed)
    phelps = np.linspace(0.4, 0.8, 9)
    pharms = np.linspace(0.0, 0.15, 16)
    grid = np.array([(ph, pm) for ph in phelps for pm in pharms], float)

    out = []
    for H in [1, 4, 10]:
        for n in [20, 50, 100, 500]:
            ph = grid[:, 0][:, None]
            pm = grid[:, 1][:, None]
            true_u = PI * ph[:, 0] - (1 - PI) * pm[:, 0] * H - COST

            kh = rng.binomial(n, ph, size=(len(grid), reps))
            km = rng.binomial(n, pm, size=(len(grid), reps))

            mean_help = (kh + 0.5) / (n + 1)
            mean_harm = (km + 0.5) / (n + 1)
            plug = (PI * mean_help - (1 - PI) * mean_harm * H - COST) > 0

            lhelp = beta.ppf(0.025, kh + 0.5, n - kh + 0.5)
            uharm = beta.ppf(0.975, km + 0.5, n - km + 0.5)
            conservative = (
                PI * lhelp - (1 - PI) * uharm * H - COST
            ) > 0

            positive = true_u > 0
            negative = ~positive
            out.append(
                {
                    "H": H,
                    "n": n,
                    "plug_unsafe": float(plug[negative].mean()),
                    "plug_power": float(plug[positive].mean()),
                    "lcb_unsafe": float(conservative[negative].mean()),
                    "lcb_power": float(conservative[positive].mean()),
                    "npos_parameter_points": int(positive.sum()),
                    "nneg_parameter_points": int(negative.sum()),
                    "replications_per_parameter_point": reps,
                }
            )
    return out


def main():
    result = {
        "schema_version": 1,
        "study": "blast_radius_sensitive_semantic_correction_gate",
        "seed": SEED,
        "parameters": {
            "pi": PI,
            "cost": COST,
            "alpha": ALPHA,
            "support_example_p_help": 0.65,
            "support_example_p_harm": 0.03,
        },
        "support_thresholds": [
            support_threshold(H) for H in [0.25, 1, 2, 4, 6, 10]
        ],
        "monte_carlo": monte_carlo_grid(),
        "scope_note": (
            "Synthetic mechanism study only. H, prevalence, costs, support "
            "thresholds, and grid-level error rates are not production constants."
        ),
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
