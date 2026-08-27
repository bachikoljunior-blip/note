"""Lifetime-safe V3 numerical reporting: same-history K guard -> fresh confirm.

This module binds three already-derived contracts:
1. production V3 e-process / weighted upper-CS implementation;
2. the exact nine-split minimax selector for same-history reporting;
3. the corrected production-V3 predictable-weight K guard.

Critical ordering contract
--------------------------
Call ``admit(exposure_weight)`` BEFORE the current block score is observable.
The admission fixes the predictable weight, advances an immutable weight-prefix
hash chain, and checks K.  Only then may ``observe(token, block_score)`` be
called.  A score supplied without a matching admission is rejected.

If K first exceeds the predeclared K_cap at prefix t, the handoff is latched at
t before that score is used by either reporting phase.  The score at t is
quarantined for numerical reporting.  Fresh-confirm streams begin empty and
consume rows t+1, t+2, ... only.  Their alpha split is frozen from pre-handoff
history and the residual lifetime alpha.  No alpha reset occurs.

This file is evaluation research code, not a production deployment claim.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
from importlib.util import module_from_spec, spec_from_file_location
import json
from math import exp, isfinite, log
from pathlib import Path
import sys
from typing import Any, Sequence


def _load_sibling(filename: str, module_name: str) -> Any:
    p = Path(__file__).resolve().with_name(filename)
    s = spec_from_file_location(module_name, p)
    if s is None or s.loader is None:
        raise ImportError(p)
    m = module_from_spec(s)
    sys.modules[module_name] = m
    s.loader.exec_module(m)
    return m


_V3 = _load_sibling(
    "weighted_average_incremental_lsm_v3_warm_root_2026-08-27.py",
    "_evaluation_hybrid_v3_prod",
)
_G = _load_sibling(
    "v3_same_history_K_guard_2026-08-28_v2.py",
    "_evaluation_hybrid_k_guard",
)


def _new_stream() -> Any:
    return _V3.IncrementalExactWeightedUpperCS(_V3.DEFAULT_LAMBDAS, _V3.DEFAULT_MIXTURE)


def _grid(delta: float) -> tuple[tuple[float, float], ...]:
    if not isfinite(delta) or not (0.0 < delta < 1.0):
        raise ValueError("delta must lie in (0,1)")
    return tuple((i * delta / 10.0, (10 - i) * delta / 10.0) for i in range(1, 10))


def _minimax_split(log_e_equal: float, log_e_exposure: float, delta: float) -> tuple[int, float, float]:
    candidates = []
    for i, (ae, ax) in enumerate(_grid(delta), start=1):
        residual = max(log(1.0 / ae) - log_e_equal, log(1.0 / ax) - log_e_exposure)
        candidates.append((residual, abs(ae - ax), i, ae, ax))
    _r, _bal, i, ae, ax = min(candidates)
    return i, ae, ax


def _weight_chain(prev_hex: str, prefix: int, exposure_weight: float) -> str:
    body = json.dumps(
        {"prev": prev_hex, "prefix": prefix, "equal_weight": 1.0, "exposure_weight": exposure_weight},
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(body).hexdigest()


@dataclass(frozen=True)
class AdmissionToken:
    prefix: int
    exposure_weight: float
    weight_prefix_digest: str
    mode: str
    handoff_prefix: int | None
    score_may_enter_same_history: bool
    score_may_enter_fresh: bool


@dataclass(frozen=True)
class FrozenFreshAllocation:
    frozen_at_prefix: int
    source_weight_prefix_digest: str
    grid_index: int
    alpha_equal: float
    alpha_exposure: float
    target_mu: float
    delta_fresh: float
    source_log_e_equal: float
    source_log_e_exposure: float

    def assert_valid(self) -> None:
        if self.frozen_at_prefix < 1:
            raise ValueError("handoff prefix must be positive")
        if self.alpha_equal <= 0 or self.alpha_exposure <= 0:
            raise ValueError("fresh channel alphas must be positive")
        if self.alpha_equal + self.alpha_exposure > self.delta_fresh + 1e-15:
            raise ValueError("fresh allocation exceeds residual alpha")


class KGuardHybridReporter:
    def __init__(
        self,
        *,
        target_mu: float = 0.05,
        delta_global: float = 0.05,
        k_cap: float = 5.0,
        delta_same: float = 0.025,
    ) -> None:
        if not 0.0 < target_mu < 1.0:
            raise ValueError("target_mu must lie in (0,1)")
        self.target_mu = float(target_mu)
        self.budget = _G.make_hybrid_budget(
            delta_global=delta_global,
            k_cap=k_cap,
            same_history_nominal_alpha=delta_same,
        )
        self.guard = _G.GuardState(self.budget, mu0=self.target_mu)
        self.same_equal = _new_stream()
        self.same_exposure = _new_stream()
        self.fresh_equal: Any | None = None
        self.fresh_exposure: Any | None = None
        self.fresh_allocation: FrozenFreshAllocation | None = None
        self.same_rows = 0
        self.fresh_rows = 0
        self.quarantined_handoff_rows = 0
        self.prefix = 0
        self._weights_equal: list[float] = []
        self._weights_exposure: list[float] = []
        self._weight_digest = "0" * 64
        self._pending: AdmissionToken | None = None

    def _freeze_fresh_allocation(self, handoff_prefix: int, digest: str) -> None:
        if self.fresh_allocation is not None:
            return
        if self.same_rows == 0:
            le = lx = 0.0
        else:
            le = self.same_equal.log_e(self.target_mu)
            lx = self.same_exposure.log_e(self.target_mu)
        i, ae, ax = _minimax_split(le, lx, self.budget.fresh_confirm_alpha)
        frozen = FrozenFreshAllocation(
            frozen_at_prefix=handoff_prefix,
            source_weight_prefix_digest=digest,
            grid_index=i,
            alpha_equal=ae,
            alpha_exposure=ax,
            target_mu=self.target_mu,
            delta_fresh=self.budget.fresh_confirm_alpha,
            source_log_e_equal=le,
            source_log_e_exposure=lx,
        )
        frozen.assert_valid()
        self.fresh_allocation = frozen
        self.fresh_equal = _new_stream()
        self.fresh_exposure = _new_stream()

    def admit(self, exposure_weight: float) -> AdmissionToken:
        """Admit a predictable weight before observing the current score."""
        if self._pending is not None:
            raise RuntimeError("previous admission has not been observed")
        w = float(exposure_weight)
        if not isfinite(w) or w <= 0.0 or w > 1.0:
            raise ValueError("exposure_weight must satisfy 0<w<=1")
        self.prefix += 1
        self._weights_equal.append(1.0)
        self._weights_exposure.append(w)
        self._weight_digest = _weight_chain(self._weight_digest, self.prefix, w)

        prior_mode = self.guard.mode
        cert = self.guard.update(self.prefix, self._weights_equal, self._weights_exposure)
        if prior_mode == "SAME_HISTORY" and cert["mode"] == "FRESH_CONFIRM":
            self._freeze_fresh_allocation(self.prefix, self._weight_digest)

        token = AdmissionToken(
            prefix=self.prefix,
            exposure_weight=w,
            weight_prefix_digest=self._weight_digest,
            mode=cert["mode"],
            handoff_prefix=self.guard.handoff_prefix,
            score_may_enter_same_history=(cert["mode"] == "SAME_HISTORY"),
            score_may_enter_fresh=(
                cert["mode"] == "FRESH_CONFIRM"
                and self.guard.handoff_prefix is not None
                and self.prefix > self.guard.handoff_prefix
            ),
        )
        self._pending = token
        return token

    def observe(self, token: AdmissionToken, block_score: float) -> dict[str, Any]:
        """Consume one score only under the exact matching prior admission."""
        if self._pending is None or token != self._pending:
            raise ValueError("score does not match the unique pending admission")
        y = float(block_score)
        if not isfinite(y) or y < 0.0 or y > 1.0:
            raise ValueError("block_score must lie in [0,1]")
        if token.weight_prefix_digest != self._weight_digest or token.prefix != self.prefix:
            raise ValueError("admission token/prefix digest mismatch")

        self._pending = None
        if token.score_may_enter_same_history:
            self.same_equal.append(1.0, y)
            self.same_exposure.append(token.exposure_weight, y)
            self.same_rows += 1
            return self._same_snapshot(token)

        if token.score_may_enter_fresh:
            assert self.fresh_allocation is not None
            assert self.fresh_equal is not None and self.fresh_exposure is not None
            self.fresh_equal.append(1.0, y)
            self.fresh_exposure.append(token.exposure_weight, y)
            self.fresh_rows += 1
            return self._fresh_snapshot(token)

        # The first guard-failing row is deliberately in neither certificate.
        self.quarantined_handoff_rows += 1
        return {
            "prefix": token.prefix,
            "mode": "FRESH_CONFIRM",
            "handoff_row_quarantined": True,
            "numeric_report_available": False,
            "weight_prefix_digest": token.weight_prefix_digest,
            "fresh_allocation": asdict(self.fresh_allocation) if self.fresh_allocation else None,
            "budget": self.budget.as_dict(),
        }

    def _same_snapshot(self, token: AdmissionToken) -> dict[str, Any]:
        le = self.same_equal.log_e(self.target_mu)
        lx = self.same_exposure.log_e(self.target_mu)
        i, ae, ax = _minimax_split(le, lx, self.budget.same_history_nominal_alpha)
        return {
            "prefix": token.prefix,
            "mode": "SAME_HISTORY",
            "numeric_report_available": True,
            "weight_prefix_digest": token.weight_prefix_digest,
            "K": _G.two_channel_k(
                self._weights_equal,
                self._weights_exposure,
                mu0=self.target_mu,
            )[0],
            "grid_index": i,
            "alpha_equal": ae,
            "alpha_exposure": ax,
            "upper_equal": self.same_equal.upper_endpoint(alpha=ae),
            "upper_exposure": self.same_exposure.upper_endpoint(alpha=ax),
            "target_log_e_equal": le,
            "target_log_e_exposure": lx,
            "same_rows": self.same_rows,
            "budget": self.budget.as_dict(),
        }

    def _fresh_snapshot(self, token: AdmissionToken) -> dict[str, Any]:
        assert self.fresh_allocation is not None
        assert self.fresh_equal is not None and self.fresh_exposure is not None
        f = self.fresh_allocation
        return {
            "prefix": token.prefix,
            "mode": "FRESH_CONFIRM",
            "numeric_report_available": True,
            "weight_prefix_digest": token.weight_prefix_digest,
            "handoff_prefix": f.frozen_at_prefix,
            "fresh_rows": self.fresh_rows,
            "frozen_allocation": asdict(f),
            "upper_equal": self.fresh_equal.upper_endpoint(alpha=f.alpha_equal),
            "upper_exposure": self.fresh_exposure.upper_endpoint(alpha=f.alpha_exposure),
            "target_log_e_equal": self.fresh_equal.log_e(self.target_mu),
            "target_log_e_exposure": self.fresh_exposure.log_e(self.target_mu),
            "budget": self.budget.as_dict(),
        }

    def state(self) -> dict[str, Any]:
        return {
            "prefix": self.prefix,
            "mode": self.guard.mode,
            "handoff_prefix": self.guard.handoff_prefix,
            "weight_prefix_digest": self._weight_digest,
            "same_rows": self.same_rows,
            "fresh_rows": self.fresh_rows,
            "quarantined_handoff_rows": self.quarantined_handoff_rows,
            "pending_admission": asdict(self._pending) if self._pending else None,
            "fresh_allocation": asdict(self.fresh_allocation) if self.fresh_allocation else None,
            "budget": self.budget.as_dict(),
        }


__all__ = [
    "AdmissionToken",
    "FrozenFreshAllocation",
    "KGuardHybridReporter",
]
