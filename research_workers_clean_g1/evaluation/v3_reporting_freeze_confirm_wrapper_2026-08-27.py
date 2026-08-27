"""Selection-aware V3 reporting via pilot freeze + fresh confirmation.

Statistical contract:
- The allocation split may depend arbitrarily on the CLOSED pilot prefix.
- The chosen split and pilot digest are frozen before any reporting row is consumed.
- Reporting V3 streams start empty and consume only CLOSED rows strictly after the
  frozen pilot prefix. Pilot evidence is never replayed into the certificate.
- Conditional e-validity of post-pilot rows plus alpha_equal+alpha_exposure<=delta
  gives classical selected-pair simultaneous coverage without a K-way grid penalty.

This module does not change the production V3 e-process family.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
from importlib.util import module_from_spec, spec_from_file_location
import json
from math import log
from pathlib import Path
import sys
from typing import Any, Iterable, Sequence


def _load_sibling(filename: str, module_name: str) -> Any:
    p = Path(__file__).resolve().with_name(filename)
    s = spec_from_file_location(module_name, p)
    if s is None or s.loader is None:
        raise ImportError(p)
    m = module_from_spec(s); sys.modules[module_name] = m; s.loader.exec_module(m); return m


_A = _load_sibling("v3_simultaneous_reporting_adapter_2026-08-27.py", "_evaluation_freeze_v3")
DEFAULT_GRID = tuple((i / 1000.0, 0.05 - i / 1000.0) for i in range(5, 50, 5))


def _canon(rows: Sequence[dict[str, Any]]) -> bytes:
    return json.dumps(list(rows), sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def rows_digest(rows: Sequence[dict[str, Any]]) -> str:
    return hashlib.sha256(_canon(rows)).hexdigest()


def _append_row(stream: Any, row: dict[str, Any], channel: str) -> None:
    if channel == "equal_process":
        w = 1.0
    elif channel == "planned_exposure":
        w = float(row["exposure_weight"])
    else:
        raise ValueError(channel)
    stream.append(w, float(row["block_score"]))


@dataclass(frozen=True)
class FrozenAllocation:
    pilot_row_count: int
    pilot_digest: str
    grid_index: int
    alpha_equal: float
    alpha_exposure: float
    target_mu: float
    pilot_log_e_equal: float
    pilot_log_e_exposure: float
    selection_rule: str = "minimax_remaining_log_threshold"

    def assert_valid(self, joint_alpha: float = 0.05) -> None:
        if self.pilot_row_count < 1:
            raise ValueError("pilot must contain at least one CLOSED row")
        if not (0 < self.alpha_equal < 1 and 0 < self.alpha_exposure < 1):
            raise ValueError("channel alphas must be in (0,1)")
        if self.alpha_equal + self.alpha_exposure > joint_alpha + 1e-15:
            raise ValueError("selected pair exceeds joint alpha")
        if not (0 < self.target_mu < 1):
            raise ValueError("target_mu must be in (0,1)")


def freeze_allocation(
    pilot_rows: Sequence[dict[str, Any]],
    grid: Sequence[tuple[float, float]] = DEFAULT_GRID,
    target_mu: float = 0.05,
) -> FrozenAllocation:
    if not pilot_rows:
        raise ValueError("pilot_rows cannot be empty")
    pe = _A.production_v3_stream_factory(0.05)
    px = _A.production_v3_stream_factory(0.05)
    for row in pilot_rows:
        _append_row(pe, row, "equal_process")
        _append_row(px, row, "planned_exposure")
    le = pe.log_e(target_mu); lx = px.log_e(target_mu)
    scores: list[tuple[float, float, int]] = []
    for i, (ae, ax) in enumerate(grid):
        if ae <= 0 or ax <= 0 or ae + ax > 0.05 + 1e-15:
            raise ValueError(f"invalid grid pair {i}: {(ae, ax)}")
        residual = max(log(1.0 / ae) - le, log(1.0 / ax) - lx)
        # Stable second key prefers balanced allocation on exact residual ties.
        scores.append((residual, abs(ae - ax), i))
    _, _, k = min(scores)
    ae, ax = grid[k]
    frozen = FrozenAllocation(
        pilot_row_count=len(pilot_rows),
        pilot_digest=rows_digest(pilot_rows),
        grid_index=k,
        alpha_equal=float(ae),
        alpha_exposure=float(ax),
        target_mu=float(target_mu),
        pilot_log_e_equal=float(le),
        pilot_log_e_exposure=float(lx),
    )
    frozen.assert_valid()
    return frozen


class FreshConfirmReporter:
    def __init__(self, frozen: FrozenAllocation) -> None:
        frozen.assert_valid()
        self.frozen = frozen
        self.equal = _A.production_v3_stream_factory(frozen.alpha_equal)
        self.exposure = _A.production_v3_stream_factory(frozen.alpha_exposure)
        self.postpilot_rows = 0

    def append(self, row: dict[str, Any]) -> None:
        _append_row(self.equal, row, "equal_process")
        _append_row(self.exposure, row, "planned_exposure")
        self.postpilot_rows += 1

    def resolved(self) -> bool:
        if self.postpilot_rows == 0:
            return False
        m = self.frozen.target_mu
        return (
            self.equal.log_e(m) >= log(1.0 / self.frozen.alpha_equal)
            and self.exposure.log_e(m) >= log(1.0 / self.frozen.alpha_exposure)
        )

    def snapshot(self) -> dict[str, Any]:
        if self.postpilot_rows == 0:
            return {
                "postpilot_rows": 0,
                "resolved": False,
                "upper_equal": 1.0,
                "upper_exposure": 1.0,
            }
        return {
            "postpilot_rows": self.postpilot_rows,
            "resolved": self.resolved(),
            "log_e_equal": self.equal.log_e(self.frozen.target_mu),
            "log_e_exposure": self.exposure.log_e(self.frozen.target_mu),
            "upper_equal": self.equal.upper_endpoint(),
            "upper_exposure": self.exposure.upper_endpoint(),
        }


def replay_fresh(rows: Sequence[dict[str, Any]], frozen: FrozenAllocation) -> FreshConfirmReporter:
    if len(rows) < frozen.pilot_row_count:
        raise ValueError("row history shorter than frozen pilot")
    pilot = rows[: frozen.pilot_row_count]
    if rows_digest(pilot) != frozen.pilot_digest:
        raise ValueError("pilot prefix digest mismatch")
    reporter = FreshConfirmReporter(frozen)
    for row in rows[frozen.pilot_row_count :]:
        reporter.append(row)
    return reporter


def first_fresh_resolution(
    rows: Sequence[dict[str, Any]], frozen: FrozenAllocation
) -> int | None:
    if rows_digest(rows[: frozen.pilot_row_count]) != frozen.pilot_digest:
        raise ValueError("pilot prefix digest mismatch")
    reporter = FreshConfirmReporter(frozen)
    for i, row in enumerate(rows[frozen.pilot_row_count :], start=frozen.pilot_row_count + 1):
        reporter.append(row)
        if reporter.resolved():
            return i
    return None
