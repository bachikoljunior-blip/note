"""Exact-production-V3 predictable-weight K guard and hybrid reporting budget.

This supersedes ``v3_same_history_K_guard_2026-08-28.py``.  The superseded
prototype accidentally used ``a=lambda*w`` and a different denominator term.
Production V3 actually uses

    a_i = 1 - exp(-lambda*w_i)

and its exact water-filling denominator is the one implemented by
``weighted_average_incremental_lsm_v3_warm_root_2026-08-27.py``.

This file duplicates only that score-free predictable-weight denominator
geometry so the guard can be evaluated before revealing the current score.
It does not alter the V3 score process, mixture, or selector.

Scope: same-history numerical reporting only when the true running channel
means lie in the declared safe domain [0, mu0], weights are fixed before the
current score and satisfy 0<w<=1, and K_cap/risk split were predeclared.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from math import exp, expm1, isfinite, log, log1p
from typing import Iterable, Sequence

DEFAULT_LAMBDAS = (0.47, 1.06, 1.87, 3.37, 7.4)


def c_of_k(k: float) -> tuple[float, int]:
    if not isfinite(k) or k < 1.0:
        raise ValueError("K must be finite and >=1")
    return min(
        ((10.0 / i) * (1.0 + (i - 1.0) / ((10.0 - i) * k)), i)
        for i in range(1, 10)
    )


def selector_error_multiplier(k: float) -> float:
    c, _ = c_of_k(k)
    return 2.0 / c


def _weights(weights: Iterable[float]) -> tuple[float, ...]:
    ws = tuple(float(w) for w in weights)
    if not ws:
        raise ValueError("weight history must be nonempty")
    if any((not isfinite(w)) or w <= 0.0 or w > 1.0 for w in ws):
        raise ValueError("production V3 predictable weights require 0<w<=1")
    return ws


def _group(ws: Sequence[float]) -> tuple[tuple[float, int], ...]:
    counts: dict[float, int] = {}
    for w in ws:
        counts[w] = counts.get(w, 0) + 1
    return tuple(sorted(counts.items()))


def production_v3_log_dmax(weights: Iterable[float], lam: float, mean: float) -> float:
    """Exact production-V3 log denominator from predictable weights only.

    This is an algebraic grouped-weight implementation of the same envelope as
    ``StreamingWeightedEnvelopeComponent.log_dmax`` in the persisted production
    V3 core.  For each weight, V3 defines a=1-exp(-lambda*w), lower=w(1-a)/a,
    upper=w/a.  The root c solves the weighted water-fill score
    sum length([c,inf) intersect [lower,upper]) = mean*sum(w).
    """
    ws = _weights(weights)
    if not isfinite(lam) or lam <= 0.0:
        raise ValueError("lambda must be finite and >0")
    if not isfinite(mean) or mean < 0.0 or mean > 1.0:
        raise ValueError("mean must lie in [0,1]")
    if mean == 0.0:
        return 0.0

    rows = []
    total_w = 0.0
    for w, n in _group(ws):
        a = -expm1(-lam * w)
        lower = w * (1.0 - a) / a
        upper = w / a
        lconst = log(a / w)
        sat = log1p(-a)
        rows.append((w, n, lower, upper, lconst, sat))
        total_w += n * w

    if mean == 1.0:
        return -lam * total_w

    target = mean * total_w
    lo = min(row[2] for row in rows)
    hi = max(row[3] for row in rows)

    def score(c: float) -> float:
        s = 0.0
        for _w, n, lower, upper, _lc, _sat in rows:
            if c < lower:
                s += n * (upper - lower)
            elif c < upper:
                s += n * (upper - c)
        return s

    for _ in range(180):
        mid = (lo + hi) / 2.0
        if score(mid) > target:
            lo = mid
        else:
            hi = mid
    c = (lo + hi) / 2.0

    log_d = 0.0
    for _w, n, lower, upper, lconst, sat in rows:
        if c < upper:
            log_d += n * lconst
        if c < lower:
            log_d += n * (-lconst + sat)
        elif c < upper:
            log_d += n * log(c)
    return log_d


def safe_domain_u(
    weights: Iterable[float],
    *,
    mu0: float = 0.05,
    lambdas: Sequence[float] = DEFAULT_LAMBDAS,
) -> float:
    ws = _weights(weights)
    if not (0.0 < mu0 < 1.0):
        raise ValueError("mu0 must lie in (0,1)")
    if not lambdas:
        raise ValueError("lambda family must be nonempty")
    return max(
        1.0,
        *(exp(-production_v3_log_dmax(ws, float(lam), mu0)) for lam in lambdas),
    )


def two_channel_k(
    weights_1: Iterable[float],
    weights_2: Iterable[float],
    *,
    mu0: float = 0.05,
    lambdas: Sequence[float] = DEFAULT_LAMBDAS,
) -> tuple[float, float, float]:
    u1 = safe_domain_u(weights_1, mu0=mu0, lambdas=lambdas)
    u2 = safe_domain_u(weights_2, mu0=mu0, lambdas=lambdas)
    return max(u1, u2), u1, u2


@dataclass(frozen=True)
class HybridBudget:
    delta_global: float
    k_cap: float
    same_history_nominal_alpha: float
    same_history_error_multiplier: float
    same_history_lifetime_spend_bound: float
    fresh_confirm_alpha: float

    def as_dict(self) -> dict:
        return asdict(self)


def make_hybrid_budget(
    *,
    delta_global: float,
    k_cap: float,
    same_history_nominal_alpha: float,
) -> HybridBudget:
    if not 0.0 < delta_global < 1.0:
        raise ValueError("delta_global must lie in (0,1)")
    if not 0.0 < same_history_nominal_alpha < 1.0:
        raise ValueError("same_history_nominal_alpha must lie in (0,1)")
    m = selector_error_multiplier(k_cap)
    same_spend = m * same_history_nominal_alpha
    fresh = delta_global - same_spend
    if fresh <= 0.0:
        raise ValueError("same-history phase exhausts lifetime reporting budget")
    return HybridBudget(
        delta_global,
        k_cap,
        same_history_nominal_alpha,
        m,
        same_spend,
        fresh,
    )


@dataclass
class GuardState:
    budget: HybridBudget
    mu0: float = 0.05
    lambdas: Sequence[float] = DEFAULT_LAMBDAS
    mode: str = "SAME_HISTORY"
    handoff_prefix: int | None = None

    def update(
        self,
        prefix: int,
        weights_1: Iterable[float],
        weights_2: Iterable[float],
    ) -> dict:
        """Evaluate the guard BEFORE releasing a numerical report at prefix."""
        if prefix <= 0:
            raise ValueError("prefix must be positive")
        k, u1, u2 = two_channel_k(
            weights_1, weights_2, mu0=self.mu0, lambdas=self.lambdas
        )
        if self.mode == "SAME_HISTORY" and k > self.budget.k_cap:
            self.mode = "FRESH_CONFIRM"
            self.handoff_prefix = prefix
        return {
            "prefix": prefix,
            "mode": self.mode,
            "K": k,
            "U1": u1,
            "U2": u2,
            "mu0": self.mu0,
            "declared_safe_domain": [0.0, self.mu0],
            "budget": self.budget.as_dict(),
            "same_history_numeric_reporting_allowed": self.mode == "SAME_HISTORY",
            "fresh_confirm_required": self.mode == "FRESH_CONFIRM",
            "fresh_confirm_must_start_after_prefix": self.handoff_prefix,
            "latched_handoff": True,
            "risk_accounting_rule": (
                "same_history_error <= m(K_cap)*delta_same; "
                "fresh conditional error <= delta_fresh; union <= delta_global"
            ),
        }


def equal_nominal_alpha_for_two_phases(delta_global: float, k_cap: float) -> float:
    m = selector_error_multiplier(k_cap)
    return delta_global / (1.0 + m)


__all__ = [
    "DEFAULT_LAMBDAS",
    "HybridBudget",
    "GuardState",
    "c_of_k",
    "selector_error_multiplier",
    "production_v3_log_dmax",
    "safe_domain_u",
    "two_channel_k",
    "make_hybrid_budget",
    "equal_nominal_alpha_for_two_phases",
]
