"""Dual-channel fail-closed reliability monitor for a conjunctive safety gate.

Each CLOSED block contributes the same fail-closed block score to two channels:
- equal-process channel: predictable weight 1;
- planned-exposure channel: predictable weight planned_size / B_cap.

The release decision is an intersection-union test: at a frozen alpha, BOTH channel
e-processes at their unsafe tolerances must cross 1/alpha. No alpha split is required
for this one AND decision. If numerical simultaneous confidence bounds are separately
reported, that is a different contract and requires an explicit joint-coverage rule.

The wrapper persists an ordered scientific journal and replays it into fresh CS objects;
root caches are intentionally not durable scientific state.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from math import isfinite, log
from typing import Any, Callable, Iterable


@dataclass
class PlannedSlotBlock:
    block_id: str
    slot_ids: tuple[str, ...]
    admitted_at: float
    deadline: float
    b_cap: int
    accepted: dict[str, tuple[float, float]] = field(default_factory=dict)
    closed: bool = False
    closed_at: float | None = None

    @classmethod
    def admit(cls, block_id: str, slot_ids: Iterable[str], admitted_at: float, deadline: float, b_cap: int) -> "PlannedSlotBlock":
        ids = tuple(str(x) for x in slot_ids)
        if not ids or len(set(ids)) != len(ids):
            raise ValueError("nonempty unique slots required")
        if not isfinite(admitted_at) or not isfinite(deadline) or deadline < admitted_at:
            raise ValueError("invalid frozen times")
        if int(b_cap) < len(ids):
            raise ValueError("B_cap must cover planned size")
        return cls(str(block_id), ids, float(admitted_at), float(deadline), int(b_cap))

    @property
    def planned_size(self) -> int:
        return len(self.slot_ids)

    def record_canonical(self, slot_id: str, score: float, observed_at: float) -> tuple[bool, str]:
        sid = str(slot_id)
        if self.closed:
            return False, "closed"
        if sid not in self.slot_ids:
            return False, "not_admitted"
        if sid in self.accepted:
            return False, "already_accepted"
        if observed_at > self.deadline:
            return False, "after_deadline"
        y = float(score)
        if not isfinite(y) or y < 0 or y > 1:
            raise ValueError("score must lie in [0,1]")
        self.accepted[sid] = (y, float(observed_at))
        return True, "accepted"

    def close(self, closed_at: float) -> dict[str, Any]:
        if self.closed:
            return self.summary()
        if closed_at < self.deadline:
            raise ValueError("cannot close before frozen deadline")
        self.closed = True
        self.closed_at = float(closed_at)
        return self.summary()

    def summary(self) -> dict[str, Any]:
        if not self.closed:
            raise ValueError("block not closed")
        vals = [self.accepted[sid][0] if sid in self.accepted else 1.0 for sid in self.slot_ids]
        return {
            "block_id": self.block_id,
            "planned_size": self.planned_size,
            "completed_canonical": len(self.accepted),
            "missing_or_failed": self.planned_size - len(self.accepted),
            "block_score": sum(vals) / self.planned_size,
            "exposure_weight": self.planned_size / self.b_cap,
        }

    def to_state(self) -> dict[str, Any]:
        return {
            "block_id": self.block_id,
            "slot_ids": list(self.slot_ids),
            "admitted_at": self.admitted_at,
            "deadline": self.deadline,
            "b_cap": self.b_cap,
            "accepted": {sid: {"score": y, "observed_at": t} for sid, (y, t) in self.accepted.items()},
        }

    @classmethod
    def from_state(cls, state: dict[str, Any]) -> "PlannedSlotBlock":
        block = cls.admit(state["block_id"], state["slot_ids"], state["admitted_at"], state["deadline"], state["b_cap"])
        for sid, row in state.get("accepted", {}).items():
            ok, reason = block.record_canonical(sid, row["score"], row["observed_at"])
            if not ok:
                raise ValueError(f"invalid restored slot {sid}: {reason}")
        return block


class DualChannelReliabilityMonitor:
    def __init__(self, cs_factory: Callable[[], Any], b_cap: int, tau_process: float, tau_exposure: float, alpha: float = 0.05) -> None:
        if not 0 < alpha < 1:
            raise ValueError("alpha must lie in (0,1)")
        self._cs_factory = cs_factory
        self.b_cap = int(b_cap)
        self.tau_process = float(tau_process)
        self.tau_exposure = float(tau_exposure)
        self.alpha = float(alpha)
        self.process_cs = cs_factory()
        self.exposure_cs = cs_factory()
        self.closed: list[dict[str, Any]] = []
        self.active: PlannedSlotBlock | None = None

    def admit(self, block_id: str, slot_ids: Iterable[str], admitted_at: float, deadline: float) -> None:
        if self.active is not None:
            raise ValueError("active block exists")
        self.active = PlannedSlotBlock.admit(block_id, slot_ids, admitted_at, deadline, self.b_cap)

    def record_canonical(self, slot_id: str, score: float, observed_at: float) -> tuple[bool, str]:
        if self.active is None:
            return False, "no_active"
        return self.active.record_canonical(slot_id, score, observed_at)

    def close_active(self, closed_at: float) -> dict[str, Any]:
        if self.active is None:
            raise ValueError("no active block")
        row = self.active.close(closed_at)
        self.process_cs.append(1.0, row["block_score"])
        self.exposure_cs.append(row["exposure_weight"], row["block_score"])
        self.closed.append(row)
        self.active = None
        return row

    def joint_safe(self) -> bool:
        if not self.closed:
            return False
        threshold = log(1.0 / self.alpha)
        return (
            self.process_cs.log_e(self.tau_process) >= threshold
            and self.exposure_cs.log_e(self.tau_exposure) >= threshold
        )

    def durable_state(self) -> dict[str, Any]:
        return {
            "schema_version": 1,
            "b_cap": self.b_cap,
            "tau_process": self.tau_process,
            "tau_exposure": self.tau_exposure,
            "alpha": self.alpha,
            "closed": list(self.closed),
            "active": self.active.to_state() if self.active is not None else None,
        }

    @classmethod
    def recover(cls, cs_factory: Callable[[], Any], state: dict[str, Any], recovered_at: float | None = None) -> "DualChannelReliabilityMonitor":
        monitor = cls(cs_factory, state["b_cap"], state["tau_process"], state["tau_exposure"], state["alpha"])
        for row in state.get("closed", []):
            monitor.process_cs.append(1.0, row["block_score"])
            monitor.exposure_cs.append(row["exposure_weight"], row["block_score"])
            monitor.closed.append(dict(row))
        if state.get("active") is not None:
            monitor.active = PlannedSlotBlock.from_state(state["active"])
            if recovered_at is not None and recovered_at >= monitor.active.deadline:
                monitor.close_active(recovered_at)
        return monitor
