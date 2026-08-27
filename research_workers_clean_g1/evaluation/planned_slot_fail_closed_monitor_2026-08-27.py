"""Fail-closed planned-slot interruption monitor for evaluation reliability.

Scientific contract:
- Freeze block size, slot identities, deadline, and B_cap before current-block outcomes.
- Canonical results observed by the frozen deadline contribute bounded score in [0,1].
- Every pre-admitted slot without an accepted canonical result at close contributes 1.
- A late retry cannot replace a failed/missing planned slot unless that retry policy was part
  of the frozen estimand before admission.
- Predictable exposure weight is planned_size / B_cap, never realized completed count.

This module is an endpoint/state-machine implementation. Statistical validity of the
outer bounded confidence sequence is a separate contract.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from math import isfinite
from typing import Any, Iterable


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
    def admit(
        cls,
        block_id: str,
        slot_ids: Iterable[str],
        admitted_at: float,
        deadline: float,
        b_cap: int,
    ) -> "PlannedSlotBlock":
        ids = tuple(str(x) for x in slot_ids)
        if not ids:
            raise ValueError("at least one slot is required")
        if len(set(ids)) != len(ids):
            raise ValueError("slot ids must be unique")
        if not isfinite(admitted_at) or not isfinite(deadline) or deadline < admitted_at:
            raise ValueError("invalid admission/deadline")
        if int(b_cap) < len(ids):
            raise ValueError("B_cap must be >= planned size")
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
            raise ValueError("fail-closed finalization cannot precede the frozen deadline")
        self.closed = True
        self.closed_at = float(closed_at)
        return self.summary()

    def summary(self) -> dict[str, Any]:
        if not self.closed or self.closed_at is None:
            raise ValueError("block is not closed")
        scores = {
            sid: self.accepted[sid][0] if sid in self.accepted else 1.0
            for sid in self.slot_ids
        }
        return {
            "block_id": self.block_id,
            "planned_size": self.planned_size,
            "completed_canonical": len(self.accepted),
            "missing_or_failed": self.planned_size - len(self.accepted),
            "block_score": sum(scores.values()) / self.planned_size,
            "predictable_weight": self.predictable_weight,
            "slot_scores": scores,
            "admitted_at": self.admitted_at,
            "deadline": self.deadline,
            "closed_at": self.closed_at,
        }

    def to_state(self) -> dict[str, Any]:
        return {
            "schema_version": 1,
            "block_id": self.block_id,
            "slot_ids": list(self.slot_ids),
            "admitted_at": self.admitted_at,
            "deadline": self.deadline,
            "b_cap": self.b_cap,
            "accepted": {
                sid: {"score": score, "observed_at": observed_at}
                for sid, (score, observed_at) in self.accepted.items()
            },
            "closed": self.closed,
            "closed_at": self.closed_at,
        }

    @classmethod
    def from_state(cls, state: dict[str, Any]) -> "PlannedSlotBlock":
        block = cls.admit(
            state["block_id"],
            state["slot_ids"],
            float(state["admitted_at"]),
            float(state["deadline"]),
            int(state["b_cap"]),
        )
        accepted = state.get("accepted", {})
        for sid, row in accepted.items():
            ok, reason = block.record_canonical(sid, float(row["score"]), float(row["observed_at"]))
            if not ok:
                raise ValueError(f"invalid restored accepted slot {sid}: {reason}")
        if bool(state.get("closed", False)):
            closed_at = state.get("closed_at")
            if closed_at is None:
                raise ValueError("closed state lacks closed_at")
            block.close(float(closed_at))
        return block


def recover_and_close(state: dict[str, Any], recovered_at: float) -> dict[str, Any]:
    """Recover a persisted block and finalize it if its frozen deadline has passed."""
    block = PlannedSlotBlock.from_state(state)
    if block.closed:
        return block.summary()
    if recovered_at < block.deadline:
        raise ValueError("deadline has not passed; block remains live")
    return block.close(recovered_at)
