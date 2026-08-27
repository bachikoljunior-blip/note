"""Two distinct reliability contracts over the same immutable closed-block history.

Contract A -- decision-only intersection-union test (IUT)
---------------------------------------------------------
The existing release gate is preserved exactly: each channel gets alpha_decision and
release is allowed only when BOTH channel e-processes cross 1/alpha_decision.  This
single AND decision tests the union null "equal-process unsafe OR planned-exposure
unsafe" and therefore does not split alpha across the two component tests.

Contract B -- simultaneous numeric upper-bound reporting
--------------------------------------------------------
If two numerical upper confidence bounds are displayed with a joint coverage claim,
that is a different contract.  This wrapper precommits alpha_report_equal and
alpha_report_exposure with sum <= alpha_joint_report.  A union bound then gives joint
coverage at least 1 - (alpha_report_equal + alpha_report_exposure), with no channel
independence assumption.

All four streams ingest exactly the same canonical closed rows.  The wrapper keeps no
scientific state beyond those immutable rows; recovery should reconstruct all streams
from the journal-derived rows so replay/live divergence is detectable.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
import json
from math import isfinite, log
from typing import Any, Callable, Iterable, Mapping


@dataclass(frozen=True)
class DualChannelReportingContract:
    alpha_decision: float = 0.05
    alpha_joint_report: float = 0.05
    alpha_report_equal: float = 0.025
    alpha_report_exposure: float = 0.025
    tau_equal: float = 0.01
    tau_exposure: float = 0.01

    def __post_init__(self) -> None:
        vals = (
            self.alpha_decision,
            self.alpha_joint_report,
            self.alpha_report_equal,
            self.alpha_report_exposure,
        )
        if any((not isfinite(x)) or x <= 0 or x >= 1 for x in vals):
            raise ValueError("all alpha values must lie strictly in (0,1)")
        if self.alpha_report_equal + self.alpha_report_exposure > self.alpha_joint_report + 1e-15:
            raise ValueError("reporting alpha allocation exceeds precommitted joint alpha")
        if any((not isfinite(x)) or x < 0 or x > 1 for x in (self.tau_equal, self.tau_exposure)):
            raise ValueError("unsafe tolerances must lie in [0,1]")


class SimultaneousDualChannelReporter:
    """Run decision-IUT and simultaneous-reporting contracts over identical rows.

    `stream_factory(alpha)` must return a fresh stream implementing:
      * append(weight: float, score: float)
      * log_e(mu0: float) -> float
      * upper_endpoint() -> float

    The stream implementation defines the statistical estimand and e/CS family.  This
    wrapper only enforces contract separation, alpha allocation, row identity, and
    deterministic replay.  In particular it does not silently convert one estimand
    into another.
    """

    def __init__(
        self,
        stream_factory: Callable[[float], Any],
        contract: DualChannelReportingContract | None = None,
    ) -> None:
        self.stream_factory = stream_factory
        self.contract = contract or DualChannelReportingContract()
        c = self.contract
        self.decision_equal = stream_factory(c.alpha_decision)
        self.decision_exposure = stream_factory(c.alpha_decision)
        self.report_equal = stream_factory(c.alpha_report_equal)
        self.report_exposure = stream_factory(c.alpha_report_exposure)
        self.closed_rows: list[dict[str, Any]] = []
        self._rows_hasher = sha256()

    @staticmethod
    def _canonicalize_row(row: Mapping[str, Any]) -> dict[str, Any]:
        if "block_score" not in row or "exposure_weight" not in row:
            raise ValueError("closed row requires block_score and exposure_weight")
        score = float(row["block_score"])
        w = float(row["exposure_weight"])
        if not isfinite(score) or score < 0 or score > 1:
            raise ValueError("block_score must lie in [0,1]")
        if not isfinite(w) or w < 0 or w > 1:
            raise ValueError("exposure_weight must lie in [0,1]")
        out: dict[str, Any] = {}
        for key in (
            "block_id",
            "planned_size",
            "completed_canonical",
            "missing_or_failed",
        ):
            if key in row:
                out[key] = row[key]
        out["block_score"] = score
        out["exposure_weight"] = w
        return out

    def append_closed_row(self, row: Mapping[str, Any]) -> None:
        r = self._canonicalize_row(row)
        score = r["block_score"]
        w = r["exposure_weight"]
        self.decision_equal.append(1.0, score)
        self.decision_exposure.append(w, score)
        self.report_equal.append(1.0, score)
        self.report_exposure.append(w, score)
        self.closed_rows.append(r)
        line = json.dumps(r, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8") + b"\n"
        self._rows_hasher.update(line)

    def extend_closed_rows(self, rows: Iterable[Mapping[str, Any]]) -> None:
        for row in rows:
            self.append_closed_row(row)

    def rows_digest(self) -> str:
        return self._rows_hasher.hexdigest()

    def snapshot(self) -> dict[str, Any]:
        c = self.contract
        log_threshold = log(1.0 / c.alpha_decision)
        loge_eq = float(self.decision_equal.log_e(c.tau_equal))
        loge_exp = float(self.decision_exposure.log_e(c.tau_exposure))
        ub_eq_marg = float(self.decision_equal.upper_endpoint())
        ub_exp_marg = float(self.decision_exposure.upper_endpoint())
        ub_eq_joint = float(self.report_equal.upper_endpoint())
        ub_exp_joint = float(self.report_exposure.upper_endpoint())
        joint_safe_decision = bool(loge_eq >= log_threshold and loge_exp >= log_threshold)
        simultaneous_report_safe = bool(ub_eq_joint <= c.tau_equal and ub_exp_joint <= c.tau_exposure)
        allocated = c.alpha_report_equal + c.alpha_report_exposure
        return {
            "schema_version": 1,
            "row_count": len(self.closed_rows),
            "rows_digest": self.rows_digest(),
            "decision_contract": {
                "name": "intersection_union_decision",
                "alpha_per_channel": c.alpha_decision,
                "log_e_threshold_per_channel": log_threshold,
                "equal_log_e": loge_eq,
                "exposure_log_e": loge_exp,
                "joint_safe_decision": joint_safe_decision,
                "note": "Single AND decision; no alpha split is required for the union unsafe null.",
            },
            "marginal_numeric_bounds": {
                "alpha_per_channel": c.alpha_decision,
                "equal_upper": ub_eq_marg,
                "exposure_upper": ub_exp_marg,
            },
            "simultaneous_reporting_contract": {
                "name": "simultaneous_numeric_upper_bounds",
                "alpha_joint_budget": c.alpha_joint_report,
                "alpha_equal": c.alpha_report_equal,
                "alpha_exposure": c.alpha_report_exposure,
                "allocated_alpha": allocated,
                "joint_coverage_lower_bound": 1.0 - allocated,
                "independence_assumed": False,
                "equal_upper": ub_eq_joint,
                "exposure_upper": ub_exp_joint,
                "equal_upper_widening_vs_marginal": ub_eq_joint - ub_eq_marg,
                "exposure_upper_widening_vs_marginal": ub_exp_joint - ub_exp_marg,
                "simultaneous_report_safe": simultaneous_report_safe,
                "note": "Stricter reporting contract, not a correction to the valid decision-only IUT.",
            },
            "tolerances": {"equal": c.tau_equal, "exposure": c.tau_exposure},
        }

    @classmethod
    def replay(
        cls,
        stream_factory: Callable[[float], Any],
        rows: Iterable[Mapping[str, Any]],
        contract: DualChannelReportingContract | None = None,
    ) -> "SimultaneousDualChannelReporter":
        obj = cls(stream_factory, contract)
        obj.extend_closed_rows(rows)
        return obj

    def durable_contract(self) -> dict[str, Any]:
        return {
            "schema_version": 1,
            "contract": asdict(self.contract),
            "closed_rows": list(self.closed_rows),
            "rows_digest": self.rows_digest(),
            "recovery_rule": "rebuild all four streams from the same canonical immutable closed rows",
        }
