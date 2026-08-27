"""Durable fail-closed block journal with deterministic confidence-sequence replay.

This wrapper deliberately persists scientific state, not implementation caches:
1. one active pre-admitted planned-slot block, and
2. an ordered journal of closed {predictable_weight, block_score} summaries.

On recovery the outer confidence-sequence implementation is rebuilt by replaying the
closed journal in order. This avoids treating cache/storage format as scientific state.
A recovery at or after a frozen active-block deadline closes that block fail-closed.

`cs_factory()` must return an object supporting append(weight, score) and may expose
any additional query methods required by the caller.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from math import isfinite
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
            raise ValueError("nonempty unique slot ids required")
        if not isfinite(admitted_at) or not isfinite(deadline) or deadline < admitted_at:
            raise ValueError("invalid frozen times")
        if int(b_cap) < len(ids):
            raise ValueError("B_cap must cover planned size")
        return cls(str(block_id), ids, float(admitted_at), float(deadline), int(b_cap))

    @property
    def planned_size(self) -> int:
        return len(self.slot_ids)

    @property
    def predictable_weight(self) -> float:
        return self.planned_size / self.b_cap

    def record_canonical(self, slot_id: str, score: float, observed_at: float) -> tuple[bool, str]:
        sid = str(slot_id)
        if self.closed:
            return False, "closed"
        if sid not in self.slot_ids:
            return False, "not_admitted"
        if sid in self.accepted:
            return False, "already_accepted"
        if not isfinite(observed_at):
            raise ValueError("observed_at must be finite")
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
        if not isfinite(closed_at) or closed_at < self.deadline:
            raise ValueError("cannot fail-close before deadline")
        self.closed = True
        self.closed_at = float(closed_at)
        return self.summary()

    def summary(self) -> dict[str, Any]:
        if not self.closed or self.closed_at is None:
            raise ValueError("block not closed")
        vals = {sid: self.accepted[sid][0] if sid in self.accepted else 1.0 for sid in self.slot_ids}
        return {
            "block_id": self.block_id,
            "planned_size": self.planned_size,
            "missing_or_failed": self.planned_size - len(self.accepted),
            "block_score": sum(vals.values()) / self.planned_size,
            "predictable_weight": self.predictable_weight,
        }

    def to_state(self) -> dict[str, Any]:
        return {
            "block_id": self.block_id,
            "slot_ids": list(self.slot_ids),
            "admitted_at": self.admitted_at,
            "deadline": self.deadline,
            "b_cap": self.b_cap,
            "accepted": {sid: {"score": y, "observed_at": t} for sid, (y, t) in self.accepted.items()},
            "closed": self.closed,
            "closed_at": self.closed_at,
        }

    @classmethod
    def from_state(cls, state: dict[str, Any]) -> "PlannedSlotBlock":
        block = cls.admit(state["block_id"], state["slot_ids"], float(state["admitted_at"]), float(state["deadline"]), int(state["b_cap"]))
        for sid, row in state.get("accepted", {}).items():
            ok, reason = block.record_canonical(sid, float(row["score"]), float(row["observed_at"]))
            if not ok:
                raise ValueError(f"invalid restored accepted slot {sid}: {reason}")
        if state.get("closed", False):
            block.close(float(state["closed_at"]))
        return block


class DurableReliabilityMonitor:
    def __init__(self, cs_factory: Callable[[], Any], b_cap: int) -> None:
        self._cs_factory = cs_factory
        self.b_cap = int(b_cap)
        self.closed: list[dict[str, Any]] = []
        self.active: PlannedSlotBlock | None = None
        self.cs = cs_factory()

    def admit(self, block_id: str, slot_ids: Iterable[str], admitted_at: float, deadline: float) -> None:
        if self.active is not None:
            raise ValueError("an active block already exists")
        self.active = PlannedSlotBlock.admit(block_id, slot_ids, admitted_at, deadline, self.b_cap)

    def record_canonical(self, slot_id: str, score: float, observed_at: float) -> tuple[bool, str]:
        if self.active is None:
            return False, "no_active"
        return self.active.record_canonical(slot_id, score, observed_at)

    def close_active(self, closed_at: float) -> dict[str, Any]:
        if self.active is None:
            raise ValueError("no active block")
        summary = self.active.close(closed_at)
        self.cs.append(summary["predictable_weight"], summary["block_score"])
        self.closed.append(summary)
        self.active = None
        return summary

    def durable_state(self) -> dict[str, Any]:
        return {
            "schema_version": 1,
            "b_cap": self.b_cap,
            "closed": list(self.closed),
            "active": self.active.to_state() if self.active is not None else None,
        }

    @classmethod
    def recover(cls, cs_factory: Callable[[], Any], state: dict[str, Any], recovered_at: float | None = None) -> "DurableReliabilityMonitor":
        monitor = cls(cs_factory, int(state["b_cap"]))
        for row in state.get("closed", []):
            monitor.cs.append(float(row["predictable_weight"]), float(row["block_score"]))
            monitor.closed.append(dict(row))
        if state.get("active") is not None:
            monitor.active = PlannedSlotBlock.from_state(state["active"])
            if recovered_at is not None and recovered_at >= monitor.active.deadline:
                monitor.close_active(recovered_at)
        return monitor
