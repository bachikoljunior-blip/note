"""Research prototype: exact predictable-weight upper confidence endpoint.

Contract:
  * Y_i in [0,1]
  * 0 < w_i <= 1 and w_i is fixed before Y_i is observed
  * target m_t = sum_i w_i E[Y_i|F_{i-1}] / sum_i w_i

For fixed lambda > 0, a_i = 1-exp(-lambda w_i). The denominator envelope is

  D_max(m) = max prod_i (1-a_i mu_i)
             s.t. 0<=mu_i<=1, sum_i w_i mu_i = W m.

The KKT solution is mu_i = clip(1/a_i-c/w_i, 0, 1). This implementation
precomputes the exact breakpoint segments so each log D_max query is O(log n)
after O(n log n) setup for each lambda. It intentionally fails closed on weight,
score, alpha, or mixture-contract violations.
"""

from __future__ import annotations

from bisect import bisect_left
from dataclasses import dataclass
from math import exp, expm1, isfinite, log
from typing import Iterable, Sequence


@dataclass(frozen=True)
class _Segment:
    left: float
    right: float
    C: float
    K: int
    B: float
    s_left: float
    s_right: float


class WeightedEnvelopeComponent:
    def __init__(self, weights: Sequence[float], lam: float) -> None:
        if not isfinite(lam) or lam <= 0:
            raise ValueError("lambda must be finite and > 0")
        self.weights = tuple(float(x) for x in weights)
        if not self.weights:
            raise ValueError("weights must be nonempty")
        if any((not isfinite(w)) or w <= 0 or w > 1 for w in self.weights):
            raise ValueError("each predictable weight must satisfy 0 < w <= 1")
        self.lam = float(lam)
        self.W = sum(self.weights)

        a = tuple(-expm1(-self.lam * w) for w in self.weights)
        A = tuple(1.0 / x for x in a)
        lower = tuple(w * (1.0 - ai) / ai for w, ai in zip(self.weights, a))
        upper = tuple(w / ai for w, ai in zip(self.weights, a))

        events: list[tuple[float, int, int]] = []
        for i, x in enumerate(lower):
            events.append((x, 0, i))  # leaves mu=1 and enters interior
        for i, x in enumerate(upper):
            events.append((x, 1, i))  # leaves interior and enters mu=0
        events.sort(key=lambda z: z[0])

        groups: list[tuple[float, list[tuple[int, int]]]] = []
        j = 0
        while j < len(events):
            x = events[j][0]
            items: list[tuple[int, int]] = []
            while j < len(events) and events[j][0] == x:
                items.append((events[j][1], events[j][2]))
                j += 1
            groups.append((x, items))

        # On any open segment, S(c)=C-K*c and log D_max(c)=B+K*log(c).
        C = self.W
        K = 0
        B = sum(log(1.0 - ai) for ai in a)
        segments: list[_Segment] = []
        for gi, (x, items) in enumerate(groups):
            for typ, i in items:
                if typ == 0:
                    C += lower[i]
                    K += 1
                    B += log(a[i] / self.weights[i]) - log(1.0 - a[i])
                else:
                    C -= self.weights[i] * A[i]
                    K -= 1
                    B -= log(a[i] / self.weights[i])
            if gi + 1 < len(groups):
                nx = groups[gi + 1][0]
                if K > 0 and nx > x:
                    sl = C - K * x
                    sr = C - K * nx
                    segments.append(_Segment(x, nx, C, K, B, sl, sr))

        if not segments:
            raise RuntimeError("failed to construct water-filling segments")
        self._segments = tuple(segments)
        self._neg_s_right = tuple(-s.s_right for s in self._segments)

    def log_dmax(self, m: float) -> float:
        m = float(m)
        if not isfinite(m) or m < 0 or m > 1:
            raise ValueError("m must be in [0,1]")
        if m == 0:
            return 0.0
        if m == 1:
            return -self.lam * self.W

        target = m * self.W
        idx = bisect_left(self._neg_s_right, -target)
        if idx >= len(self._segments):
            idx = len(self._segments) - 1
        seg = self._segments[idx]
        tol = 1e-10 * max(1.0, self.W)
        if not (seg.s_left + tol >= target >= seg.s_right - tol):
            # Fail closed rather than silently using the wrong segment.
            found = None
            for q in range(max(0, idx - 2), min(len(self._segments), idx + 3)):
                sq = self._segments[q]
                if sq.s_left + tol >= target >= sq.s_right - tol:
                    found = sq
                    break
            if found is None:
                raise ArithmeticError("water-filling segment lookup lost monotonicity")
            seg = found

        c = (seg.C - target) / seg.K
        c = min(max(c, seg.left), seg.right)
        if c <= 0:
            raise ArithmeticError("nonpositive water-filling multiplier")
        return seg.B + seg.K * log(c)


def _logsumexp(xs: Iterable[float]) -> float:
    vals = tuple(float(x) for x in xs)
    if not vals:
        raise ValueError("empty log-sum-exp")
    m = max(vals)
    return m + log(sum(exp(x - m) for x in vals))


class ExactWeightedUpperCS:
    def __init__(
        self,
        weights: Sequence[float],
        lambdas: Sequence[float],
        mixture_weights: Sequence[float],
    ) -> None:
        self.weights = tuple(float(x) for x in weights)
        if len(lambdas) != len(mixture_weights) or not lambdas:
            raise ValueError("lambdas and mixture_weights must be nonempty and aligned")
        ps = tuple(float(x) for x in mixture_weights)
        if any((not isfinite(p)) or p <= 0 for p in ps):
            raise ValueError("mixture weights must be finite and > 0")
        total = sum(ps)
        self.ps = tuple(p / total for p in ps)
        self.lambdas = tuple(float(x) for x in lambdas)
        self.components = tuple(
            WeightedEnvelopeComponent(self.weights, lam) for lam in self.lambdas
        )

    def log_e(self, scores: Sequence[float], m: float) -> float:
        if len(scores) != len(self.weights):
            raise ValueError("scores and weights must align")
        ys = tuple(float(y) for y in scores)
        if any((not isfinite(y)) or y < 0 or y > 1 for y in ys):
            raise ValueError("each score must lie in [0,1]")
        S = sum(w * y for w, y in zip(self.weights, ys))
        return _logsumexp(
            log(p) - lam * S - comp.log_dmax(m)
            for p, lam, comp in zip(self.ps, self.lambdas, self.components)
        )

    def upper_endpoint(self, scores: Sequence[float], alpha: float = 0.05, iterations: int = 64) -> float:
        if not isfinite(alpha) or not (0 < alpha < 1):
            raise ValueError("alpha must be in (0,1)")
        if iterations < 20:
            raise ValueError("iterations too small for fail-closed endpoint inversion")
        threshold = log(1.0 / alpha)
        if self.log_e(scores, 1.0) < threshold:
            return 1.0
        lo, hi = 0.0, 1.0
        for _ in range(iterations):
            mid = (lo + hi) / 2.0
            if self.log_e(scores, mid) >= threshold:
                hi = mid
            else:
                lo = mid
        return hi


DEFAULT_LAMBDAS = (0.47, 1.06, 1.87, 3.37, 7.4)
DEFAULT_MIXTURE = (0.20164302, 0.13134027, 0.23178294, 0.19559454, 0.23963933)
