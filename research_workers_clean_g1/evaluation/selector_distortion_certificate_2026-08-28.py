"""Selector-specific same-history numeric-coverage certificate for the V3 two-channel reporter.

This helper does not alter the production V3 statistical family. It records the
algebraic sufficient condition derived from the exact nine-split minimax selector
and the V3 denominator geometry.

If E1_t(theta1), E2_t(theta2) are valid e-processes at the two true fixed
parameters and the target-to-true evidence distortion obeys

    1/K <= (E2(mu0)/E2(theta2)) / (E1(mu0)/E1(theta1)) <= K

for every reporting time, then selected-pair numeric miscoverage is bounded by

    P(any selected-pair miscoverage) <= 2*delta/c(K)

where

    c(K) = min_{i=1,...,9} 10/i * (1 + (i-1)/((10-i)*K)).

The channel-2 expression is the same after i -> 10-i. In particular K<=5
implies c(K)>=2 and hence the bound is <=delta. No channel independence is
required; the proof uses the average of the two true-parameter e-processes.

For V3, E(mu0)/E(theta) is a positive-mixture weighted average of component
ratios d_lambda(theta)/d_lambda(mu0), so deterministic component minima/maxima
provide a score-independent bound on K for a fixed predictable weight history.
"""

from __future__ import annotations

from math import exp, log
from typing import Iterable, Sequence

DEFAULT_LAMBDAS = (0.47, 1.06, 1.87, 3.37, 7.4)


def c_of_k(k: float) -> tuple[float, int]:
    if k < 1:
        raise ValueError("K must be >=1")
    vals = []
    for i in range(1, 10):
        companion = 0.0 if i == 1 else (i - 1) / ((10 - i) * k)
        vals.append((10.0 / i * (1.0 + companion), i))
    return min(vals)


def error_multiplier(k: float) -> float:
    """Returns the coefficient m in error <= m*delta."""
    c, _ = c_of_k(k)
    return 2.0 / c


def _log_dmax_grouped(
    groups: Sequence[tuple[int, float]], lam: float, mean: float, iterations: int = 80
) -> float:
    """Exact-envelope water filling for repeated predictable weights.

    groups contains (count, weight) pairs. This is a compact numerical audit
    helper for the existing V3 denominator, not a replacement implementation.
    """
    if not 0 <= mean <= 1:
        raise ValueError("mean must lie in [0,1]")
    clean = [(int(n), float(w)) for n, w in groups if n > 0]
    if not clean:
        raise ValueError("at least one observation is required")
    total_w = sum(n * w for n, w in clean)
    if mean == 0:
        return 0.0
    if mean == 1:
        return -lam * total_w
    params = []
    for n, w in clean:
        a = 1.0 - exp(-lam * w)
        params.append((n, w, a))
    lo = 0.0
    hi = max(w / a for _, w, a in params)
    target = mean * total_w
    for _ in range(iterations):
        c = (lo + hi) / 2.0
        weighted_mean_sum = 0.0
        for n, w, a in params:
            mu = 1.0 / a - c / w
            if mu < 0.0:
                mu = 0.0
            elif mu > 1.0:
                mu = 1.0
            weighted_mean_sum += n * w * mu
        if weighted_mean_sum > target:
            lo = c
        else:
            hi = c
    c = (lo + hi) / 2.0
    out = 0.0
    for n, w, a in params:
        mu = 1.0 / a - c / w
        if mu < 0.0:
            mu = 0.0
        elif mu > 1.0:
            mu = 1.0
        out += n * log(1.0 - a * mu)
    return out


def component_ratio_bounds(
    groups: Sequence[tuple[int, float]], theta: float, mu0: float = 0.05,
    lambdas: Iterable[float] = DEFAULT_LAMBDAS,
) -> tuple[float, float]:
    ratios = []
    for lam in lambdas:
        # E(mu0)/E(theta) component ratio = d(theta)/d(mu0).
        ratios.append(
            exp(_log_dmax_grouped(groups, lam, theta) - _log_dmax_grouped(groups, lam, mu0))
        )
    return min(ratios), max(ratios)


def two_channel_k(
    groups1: Sequence[tuple[int, float]],
    groups2: Sequence[tuple[int, float]],
    theta1: float,
    theta2: float,
    mu0: float = 0.05,
) -> float:
    l1, u1 = component_ratio_bounds(groups1, theta1, mu0)
    l2, u2 = component_ratio_bounds(groups2, theta2, mu0)
    return max(u2 / l1, u1 / l2)


def common_mean_prefix_audit(max_n: int = 40, mu0: float = 0.05, grid_points: int = 21) -> dict:
    """Numerical scope audit used by the checkpoint.

    Channel 1 uses equal process weights. Channel 2 alternates .25,1 starting
    with .25. This is only a finite theta-grid audit, not a continuum proof.
    """
    worst = (-1.0, None, None)
    for n in range(1, max_n + 1):
        n_quarter = (n + 1) // 2
        n_one = n // 2
        g1 = ((n, 1.0),)
        g2 = ((n_one, 1.0), (n_quarter, 0.25))
        for j in range(grid_points):
            theta = mu0 * j / (grid_points - 1)
            k = two_channel_k(g1, g2, theta, theta, mu0)
            if k > worst[0]:
                worst = (k, n, theta)
    return {"max_K": worst[0], "at_n": worst[1], "at_theta": worst[2]}


if __name__ == "__main__":
    print("K table")
    for k in (1, 1.5, 2, 3, 4, 5, 10):
        c, i = c_of_k(k)
        print(k, c, i, error_multiplier(k))
    print("common mean prefix audit", common_mean_prefix_audit())
