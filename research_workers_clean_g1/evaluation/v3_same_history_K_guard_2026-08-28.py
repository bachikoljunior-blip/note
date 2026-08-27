"""Predictable-weight K guard and lifetime-safe hybrid reporting budget for V3.

This helper is role-local evaluation research code.  It does not alter the V3
score process, lambda mixture, or selector.  It consumes only pre-outcome
predictable weight histories plus a predeclared safe parameter domain
``theta_j in [0, mu0]``.

For each channel j, V3 denominator geometry implies

    q_j = E_j(mu0) / E_j(theta_j) in [1, U_j]

uniformly over theta_j in [0, mu0], with

    U_j = max_lambda 1 / d_{j,lambda}(mu0).

Hence cross-channel distortion is bounded by K = max(U_1, U_2).  For the exact
nine-split minimax selector, same-history selected numerical miscoverage at
nominal joint level delta_same is at most

    m(K_cap) * delta_same,  m(K)=2/c(K),
    c(K)=min_{i=1..9} 10/i * (1 + (i-1)/((10-i)K)),

provided K_t <= K_cap at every same-history reporting prefix.

A lifetime-safe handoff to fresh confirmation can therefore preallocate

    delta_fresh <= delta_global - m(K_cap)*delta_same.

The handoff is latched: after the first K-guard failure, same-history numerical
reporting never resumes within that reporting lifetime.  Fresh confirmation
must start from post-handoff rows only.  This avoids treating the second phase
as if the first phase had spent zero reporting risk.

Scope: the K guard certifies only the declared safe domain theta_j <= mu0 and
requires strictly positive, finite, predictable weights.  It does not infer
predictability from data and must not accept score-dependent realized weights.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from math import exp, isfinite, log
from typing import Iterable, Sequence

DEFAULT_LAMBDAS = (0.47, 1.06, 1.87, 3.37, 7.4)


def c_of_k(k: float) -> tuple[float, int]:
    if not isfinite(k) or k < 1.0:
        raise ValueError("K must be finite and >= 1")
    vals = []
    for i in range(1, 10):
        c_i = (10.0 / i) * (1.0 + (i - 1.0) / ((10.0 - i) * k))
        vals.append((c_i, i))
    return min(vals)


def selector_error_multiplier(k: float) -> float:
    c, _ = c_of_k(k)
    return 2.0 / c


def _validate_weights(weights: Iterable[float]) -> tuple[float, ...]:
    out = tuple(float(w) for w in weights)
    if not out:
        raise ValueError("weight history must be nonempty")
    if any((not isfinite(w)) or w <= 0.0 for w in out):
        raise ValueError("all weights must be finite and strictly positive")
    return out


def _group_weights(weights: Sequence[float]) -> tuple[tuple[float, int], ...]:
    counts: dict[float, int] = {}
    for w in weights:
        counts[w] = counts.get(w, 0) + 1
    return tuple(sorted(counts.items()))


def _solve_c(grouped: Sequence[tuple[float, int]], lam: float, mean: float) -> float:
    """Solve sum_i w_i * clip(1/a_i-c/w_i,0,1) = mean*sum_i w_i.

    For V3's Bernoulli-style denominator a_i = lam*w_i.  The resulting
    water-filling solution is exact up to scalar bisection tolerance and uses
    only the predictable weights.
    """
    if not (0.0 <= mean <= 1.0):
        raise ValueError("mean must lie in [0,1]")
    if not isfinite(lam) or lam <= 0.0:
        raise ValueError("lambda must be finite and positive")

    total_weight = sum(w * n for w, n in grouped)
    target = mean * total_weight

    def weighted_sum(c: float) -> float:
        s = 0.0
        for w, n in grouped:
            a = lam * w
            mu = 1.0 / a - c / w
            if mu <= 0.0:
                mu = 0.0
            elif mu >= 1.0:
                mu = 1.0
            s += n * w * mu
        return s

    # Any sufficiently negative c clips all mu_i to one; sufficiently positive
    # c clips all to zero.  These explicit data-dependent bounds are mechanical
    # functions of predictable weights only.
    lo = min(w * (1.0 / (lam * w) - 1.0) for w, _ in grouped) - max(w for w, _ in grouped) - 1.0
    hi = max(w * (1.0 / (lam * w)) for w, _ in grouped) + max(w for w, _ in grouped) + 1.0
    if weighted_sum(lo) < target or weighted_sum(hi) > target:
        raise RuntimeError("failed to bracket water-filling root")

    for _ in range(180):
        mid = (lo + hi) / 2.0
        if weighted_sum(mid) > target:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2.0


def _log_dmax(weights: Sequence[float], lam: float, mean: float) -> float:
    """Exact V3-style log denominator envelope for one lambda and mean."""
    ws = _validate_weights(weights)
    grouped = _group_weights(ws)
    c = _solve_c(grouped, lam, mean)
    out = 0.0
    for w, n in grouped:
        a = lam * w
        mu = 1.0 / a - c / w
        if mu <= 0.0:
            mu = 0.0
        elif mu >= 1.0:
            mu = 1.0
        term = 1.0 + a * (mu - mean)
        if term <= 0.0 or not isfinite(term):
            raise RuntimeError("nonpositive/nonfinite denominator term")
        out += n * log(term)
    return out


def safe_domain_u(
    weights: Iterable[float],
    *,
    mu0: float = 0.05,
    lambdas: Sequence[float] = DEFAULT_LAMBDAS,
) -> float:
    """Return U=max_lambda 1/d_lambda(mu0) for theta in [0,mu0]."""
    ws = _validate_weights(weights)
    if not (0.0 < mu0 < 1.0):
        raise ValueError("mu0 must lie strictly in (0,1)")
    if not lambdas:
        raise ValueError("lambda family must be nonempty")
    u = 1.0
    for lam in lambdas:
        log_d = _log_dmax(ws, float(lam), mu0)
        candidate = exp(-log_d)
        if candidate > u:
            u = candidate
    if not isfinite(u) or u < 1.0:
        raise RuntimeError("invalid distortion bound")
    return u


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
    if not (0.0 < delta_global < 1.0):
        raise ValueError("delta_global must lie in (0,1)")
    if not (0.0 < same_history_nominal_alpha < 1.0):
        raise ValueError("same_history_nominal_alpha must lie in (0,1)")
    m = selector_error_multiplier(k_cap)
    same_spend = m * same_history_nominal_alpha
    fresh = delta_global - same_spend
    if fresh <= 0.0:
        raise ValueError("same-history phase exhausts or exceeds lifetime reporting budget")
    return HybridBudget(
        delta_global=delta_global,
        k_cap=k_cap,
        same_history_nominal_alpha=same_history_nominal_alpha,
        same_history_error_multiplier=m,
        same_history_lifetime_spend_bound=same_spend,
        fresh_confirm_alpha=fresh,
    )


@dataclass
class GuardState:
    """Irreversible same-history -> fresh-confirm state machine.

    ``update`` must be called before any numerical report at the corresponding
    prefix.  The weight histories supplied to it must have been fixed before
    observing the score at that prefix.
    """

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
        if prefix <= 0:
            raise ValueError("prefix must be positive")
        k, u1, u2 = two_channel_k(
            weights_1, weights_2, mu0=self.mu0, lambdas=self.lambdas
        )
        if self.mode == "SAME_HISTORY" and k > self.budget.k_cap:
            self.mode = "FRESH_CONFIRM"
            self.handoff_prefix = prefix
        cert = {
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
                "same_history_error <= m(K_cap)*delta_same; fresh phase conditional "
                "error <= delta_fresh; union <= delta_global"
            ),
        }
        return cert


def equal_nominal_alpha_for_two_phases(delta_global: float, k_cap: float) -> float:
    """a satisfying m(K_cap)*a + a = delta_global."""
    m = selector_error_multiplier(k_cap)
    return delta_global / (1.0 + m)


__all__ = [
    "DEFAULT_LAMBDAS",
    "HybridBudget",
    "GuardState",
    "c_of_k",
    "selector_error_multiplier",
    "safe_domain_u",
    "two_channel_k",
    "make_hybrid_budget",
    "equal_nominal_alpha_for_two_phases",
]
