"""Append-oriented exact predictable-weight upper CS with safe warm-root lookup.

V3 preserves the V2 immutable-run storage and the same statistical contract, but
reduces repeated water-filling inversion cost during endpoint search.

Key ideas:
- For fixed envelope state, S(c)=sum_i length([c,inf) intersect [lower_i,upper_i])
  is continuous and nonincreasing in c.
- A cached solve at target mW stores a sign-certified bracket [lo,hi] with
  S(lo)>=mW and S(hi)<=mW. For a new m, neighboring cached targets provide safe
  warm bounds without assuming differentiability or iid data.
- Inside the safe bracket, the solver uses midpoint bracketing plus a
  safeguarded piecewise-linear candidate c + (S(c)-mW)/active. The candidate is
  accepted early only under a stricter residual tolerance; otherwise the
  sign-certified bracket is updated and ordinary bisection guarantees progress.
- Any append invalidates the root cache because the envelope changed.

The public API and predictable-weight/e-process semantics are unchanged from V2.
"""

from __future__ import annotations

from bisect import bisect_left, bisect_right
from dataclasses import dataclass
from math import exp, expm1, isfinite, log
from typing import Iterable, Sequence


@dataclass(frozen=True)
class _HingeRun:
    xs: tuple[float, ...]
    lconsts: tuple[float, ...]
    sats: tuple[float, ...] | None
    sum_x_suffix: tuple[float, ...]
    sum_lconst_suffix: tuple[float, ...]
    sum_sat_suffix: tuple[float, ...] | None

    @classmethod
    def from_sorted(
        cls,
        xs: Sequence[float],
        lconsts: Sequence[float],
        sats: Sequence[float] | None = None,
    ) -> "_HingeRun":
        if len(xs) != len(lconsts) or (sats is not None and len(sats) != len(xs)):
            raise ValueError("hinge arrays must align")
        n = len(xs)
        sx = [0.0] * (n + 1)
        sl = [0.0] * (n + 1)
        ss = [0.0] * (n + 1) if sats is not None else None
        for i in range(n - 1, -1, -1):
            sx[i] = sx[i + 1] + xs[i]
            sl[i] = sl[i + 1] + lconsts[i]
            if ss is not None:
                assert sats is not None
                ss[i] = ss[i + 1] + sats[i]
        return cls(
            tuple(xs),
            tuple(lconsts),
            tuple(sats) if sats is not None else None,
            tuple(sx),
            tuple(sl),
            tuple(ss) if ss is not None else None,
        )

    @classmethod
    def singleton(cls, x: float, lconst: float, sat: float | None = None) -> "_HingeRun":
        return cls.from_sorted((x,), (lconst,), (sat,) if sat is not None else None)

    @classmethod
    def merge(cls, left: "_HingeRun", right: "_HingeRun", has_sat: bool) -> "_HingeRun":
        i = j = 0
        xs: list[float] = []
        lconsts: list[float] = []
        sats: list[float] | None = [] if has_sat else None
        while i < len(left.xs) or j < len(right.xs):
            take_left = j >= len(right.xs) or (
                i < len(left.xs) and left.xs[i] <= right.xs[j]
            )
            src = left if take_left else right
            k = i if take_left else j
            xs.append(src.xs[k])
            lconsts.append(src.lconsts[k])
            if has_sat:
                assert sats is not None and src.sats is not None
                sats.append(src.sats[k])
            if take_left:
                i += 1
            else:
                j += 1
        return cls.from_sorted(xs, lconsts, sats)

    def suffix_gt(self, c: float) -> tuple[int, float, float, float]:
        i = bisect_right(self.xs, c)
        count = len(self.xs) - i
        sat = self.sum_sat_suffix[i] if self.sum_sat_suffix is not None else 0.0
        return count, self.sum_x_suffix[i], self.sum_lconst_suffix[i], sat


@dataclass(frozen=True)
class _Run:
    lower: _HingeRun
    upper: _HingeRun
    W: float
    n: int
    min_lower: float
    max_upper: float

    @classmethod
    def singleton(cls, w: float, lam: float) -> "_Run":
        a = -expm1(-lam * w)
        lower = w * (1.0 - a) / a
        upper = w / a
        lconst = log(a / w)
        sat = log(1.0 - a)
        return cls(
            _HingeRun.singleton(lower, lconst, sat),
            _HingeRun.singleton(upper, lconst),
            w,
            1,
            lower,
            upper,
        )

    @classmethod
    def merge(cls, left: "_Run", right: "_Run") -> "_Run":
        return cls(
            _HingeRun.merge(left.lower, right.lower, True),
            _HingeRun.merge(left.upper, right.upper, False),
            left.W + right.W,
            left.n + right.n,
            min(left.min_lower, right.min_lower),
            max(left.max_upper, right.max_upper),
        )


@dataclass(frozen=True)
class _RootMemo:
    """Sign-certified root bracket for one m under one frozen envelope state."""

    lo: float
    hi: float
    log_d: float


class StreamingWeightedEnvelopeComponent:
    def __init__(self, lam: float, root_iterations: int = 40) -> None:
        if not isfinite(lam) or lam <= 0:
            raise ValueError("lambda must be finite and > 0")
        if root_iterations < 28:
            raise ValueError("root_iterations too small")
        self.lam = float(lam)
        self.root_iterations = int(root_iterations)
        self.levels: list[_Run | None] = []
        self.W = 0.0
        self.n = 0
        self.min_lower = float("inf")
        self.max_upper = 0.0

        self._root_ms: list[float] = []
        self._root_memos: list[_RootMemo] = []
        self.stats_calls = 0

    def append(self, weight: float) -> None:
        w = float(weight)
        if not isfinite(w) or w <= 0 or w > 1:
            raise ValueError("predictable weight must satisfy 0 < w <= 1")
        run = _Run.singleton(w, self.lam)
        self.W += w
        self.n += 1
        self.min_lower = min(self.min_lower, run.min_lower)
        self.max_upper = max(self.max_upper, run.max_upper)
        level = 0
        while True:
            if level == len(self.levels):
                self.levels.append(run)
                break
            prior = self.levels[level]
            if prior is None:
                self.levels[level] = run
                break
            run = _Run.merge(prior, run)
            self.levels[level] = None
            level += 1

        self._root_ms.clear()
        self._root_memos.clear()

    def _stats(self, c: float) -> tuple[float, int, float]:
        self.stats_calls += 1
        count_u = count_l = 0
        sum_u = sum_l = 0.0
        lconst_u = lconst_l = sat_l = 0.0
        for run in self.levels:
            if run is None:
                continue
            cu, su, lu, _ = run.upper.suffix_gt(c)
            cl, sl, ll, sat = run.lower.suffix_gt(c)
            count_u += cu
            count_l += cl
            sum_u += su
            sum_l += sl
            lconst_u += lu
            lconst_l += ll
            sat_l += sat
        score = (sum_u - count_u * c) - (sum_l - count_l * c)
        active = count_u - count_l
        log_d = (lconst_u - lconst_l) + active * log(c) + sat_l
        return score, active, log_d

    def _cache_bracket(self, m: float) -> tuple[int, float, float]:
        idx = bisect_left(self._root_ms, m)
        if idx < len(self._root_ms) and self._root_ms[idx] == m:
            memo = self._root_memos[idx]
            return idx, memo.lo, memo.hi

        lo = self.min_lower
        hi = self.max_upper

        if idx > 0:
            hi = min(hi, self._root_memos[idx - 1].hi)
        if idx < len(self._root_ms):
            lo = max(lo, self._root_memos[idx].lo)

        if lo > hi:
            raise ArithmeticError("cached root brackets became inconsistent")
        return idx, lo, hi

    def log_dmax(self, m: float) -> float:
        if self.n == 0:
            raise ValueError("append at least one observation first")
        m = float(m)
        if not isfinite(m) or m < 0 or m > 1:
            raise ValueError("m must be in [0,1]")
        if m == 0:
            return 0.0
        if m == 1:
            return -self.lam * self.W

        idx = bisect_left(self._root_ms, m)
        if idx < len(self._root_ms) and self._root_ms[idx] == m:
            return self._root_memos[idx].log_d

        _, lo, hi = self._cache_bracket(m)
        target = m * self.W
        residual_tol = 5e-11 * max(1.0, self.W)
        strict_tol = 2e-14 * max(1.0, self.W)
        width_goal = (self.max_upper - self.min_lower) / (2**self.root_iterations)

        accepted_log_d: float | None = None
        for _ in range(self.root_iterations):
            if hi - lo <= width_goal:
                break

            mid = (lo + hi) / 2.0
            score, active, log_d = self._stats(mid)
            residual = score - target

            if abs(residual) <= strict_tol:
                accepted_log_d = log_d
                break

            if residual > 0:
                lo = mid
            else:
                hi = mid

            if active > 0:
                candidate = mid + residual / active
                if lo < candidate < hi:
                    score2, _, log_d2 = self._stats(candidate)
                    residual2 = score2 - target
                    if abs(residual2) <= strict_tol:
                        accepted_log_d = log_d2
                        break
                    if residual2 > 0:
                        lo = candidate
                    else:
                        hi = candidate

        if accepted_log_d is None:
            c = (lo + hi) / 2.0
            score, _, accepted_log_d = self._stats(c)
            if abs(score - target) > residual_tol:
                raise ArithmeticError("warm-root inversion did not meet tolerance")

        insert_at = bisect_left(self._root_ms, m)
        self._root_ms.insert(insert_at, m)
        self._root_memos.insert(insert_at, _RootMemo(lo, hi, accepted_log_d))
        return accepted_log_d

    def assert_binary_counter_invariant(self) -> None:
        total = 0
        for level, run in enumerate(self.levels):
            if run is None:
                continue
            if run.n != 1 << level:
                raise AssertionError("run size does not match binary-counter level")
            total += run.n
        if total != self.n:
            raise AssertionError("run sizes do not sum to observation count")


def _logsumexp(xs: Iterable[float]) -> float:
    vals = tuple(float(x) for x in xs)
    if not vals:
        raise ValueError("empty log-sum-exp")
    m = max(vals)
    return m + log(sum(exp(x - m) for x in vals))


class IncrementalExactWeightedUpperCS:
    def __init__(
        self,
        lambdas: Sequence[float],
        mixture_weights: Sequence[float],
        root_iterations: int = 40,
    ) -> None:
        if len(lambdas) != len(mixture_weights) or not lambdas:
            raise ValueError("lambdas and mixture_weights must align")
        ps = tuple(float(x) for x in mixture_weights)
        if any((not isfinite(p)) or p <= 0 for p in ps):
            raise ValueError("mixture weights must be finite and > 0")
        total = sum(ps)
        self.ps = tuple(p / total for p in ps)
        self.lambdas = tuple(float(x) for x in lambdas)
        self.components = tuple(
            StreamingWeightedEnvelopeComponent(lam, root_iterations)
            for lam in self.lambdas
        )
        self.W = 0.0
        self.weighted_score = 0.0
        self.n = 0

    def append(self, weight: float, score: float) -> None:
        w = float(weight)
        y = float(score)
        if not isfinite(w) or w <= 0 or w > 1:
            raise ValueError("predictable weight must satisfy 0 < w <= 1")
        if not isfinite(y) or y < 0 or y > 1:
            raise ValueError("score must lie in [0,1]")
        for component in self.components:
            component.append(w)
        self.W += w
        self.weighted_score += w * y
        self.n += 1

    def log_e(self, m: float) -> float:
        if self.n == 0:
            raise ValueError("append at least one observation first")
        return _logsumexp(
            log(p) - lam * self.weighted_score - component.log_dmax(m)
            for p, lam, component in zip(self.ps, self.lambdas, self.components)
        )

    def upper_endpoint(self, alpha: float = 0.05, endpoint_iterations: int = 50) -> float:
        if not isfinite(alpha) or not (0 < alpha < 1):
            raise ValueError("alpha must be in (0,1)")
        threshold = log(1.0 / alpha)
        if self.log_e(1.0) < threshold:
            return 1.0
        lo, hi = 0.0, 1.0
        for _ in range(endpoint_iterations):
            mid = (lo + hi) / 2.0
            if self.log_e(mid) >= threshold:
                hi = mid
            else:
                lo = mid
        return hi

    def total_stats_calls(self) -> int:
        return sum(component.stats_calls for component in self.components)

    def assert_invariants(self) -> None:
        for component in self.components:
            component.assert_binary_counter_invariant()
            if component.n != self.n:
                raise AssertionError("component observation counts diverged")


DEFAULT_LAMBDAS = (0.47, 1.06, 1.87, 3.37, 7.4)
DEFAULT_MIXTURE = (0.20164302, 0.13134027, 0.23178294, 0.19559454, 0.23963933)
