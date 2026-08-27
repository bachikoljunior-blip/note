from __future__ import annotations
from dataclasses import dataclass, field
from hashlib import sha256
import json, math
from typing import Any, Iterable


def _canon(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def encode_frame(event: dict[str, Any]) -> bytes:
    body = _canon(event)
    return f"{len(body):08x}:{sha256(body).hexdigest()}:".encode("ascii") + body + b"\n"


def decode_valid_prefix(blob: bytes) -> tuple[list[dict[str, Any]], int, str]:
    events: list[dict[str, Any]] = []
    pos = 0
    while pos < len(blob):
        start = pos
        if len(blob) - pos < 74:
            return events, start, "partial_header"
        try:
            n = int(blob[pos:pos+8].decode("ascii"), 16)
        except Exception:
            return events, start, "bad_length"
        pos += 8
        if blob[pos:pos+1] != b":":
            return events, start, "bad_header_sep"
        pos += 1
        digest = blob[pos:pos+64]
        pos += 64
        if blob[pos:pos+1] != b":":
            return events, start, "bad_digest_sep"
        pos += 1
        if len(blob) - pos < n + 1:
            return events, start, "partial_body"
        body = blob[pos:pos+n]
        pos += n
        if blob[pos:pos+1] != b"\n":
            return events, start, "missing_newline"
        pos += 1
        if sha256(body).hexdigest().encode("ascii") != digest:
            return events, start, "checksum_mismatch"
        try:
            event = json.loads(body.decode("utf-8"))
        except Exception:
            return events, start, "bad_json"
        events.append(event)
    return events, pos, "clean_eof"


def event_digest(event: dict[str, Any]) -> str:
    return sha256(_canon(event)).hexdigest()


@dataclass
class ActiveBlock:
    block_id: str
    slot_ids: tuple[str, ...]
    admitted_at: float
    deadline: float
    b_cap: int
    accepted: dict[str, tuple[float, float]] = field(default_factory=dict)

    @property
    def planned_size(self) -> int:
        return len(self.slot_ids)

    def summary(self) -> dict[str, Any]:
        vals = [self.accepted[s][0] if s in self.accepted else 1.0 for s in self.slot_ids]
        return {
            "block_id": self.block_id,
            "planned_size": self.planned_size,
            "completed_canonical": len(self.accepted),
            "missing_or_failed": self.planned_size - len(self.accepted),
            "block_score": sum(vals) / self.planned_size,
            "exposure_weight": self.planned_size / self.b_cap,
        }


class JournalProtocolError(RuntimeError):
    pass


class AtomicDualChannelJournal:
    """Replay-only scientific state machine.

    Durable scientific truth is the framed append-only event stream. Numerical
    e-process caches are disposable and must be reconstructed from closed_rows.

    Required write order:
      1. ADMIT must be durably acknowledged before any slot work is launched.
      2. SLOT is accepted scientifically only after its complete frame is durable.
      3. CLOSE is the sole durable commit marker for a block. Both replay channels
         are rebuilt from the one deduplicated closed row; no separate channel
         append is durable scientific state.

    The framing model fail-closes a torn final append by accepting only the valid
    checksummed prefix. It does not claim protection from arbitrary corruption of
    already-durable earlier bytes or storage that violates append ordering/fsync.
    """

    def __init__(self) -> None:
        self.active: ActiveBlock | None = None
        self.closed_rows: list[dict[str, Any]] = []
        self.closed_by_block: dict[str, dict[str, Any]] = {}
        self.seen_event_digest: dict[str, str] = {}
        self.anomalies: list[dict[str, Any]] = []

    @staticmethod
    def admit_event(block_id: str, slot_ids: Iterable[str], admitted_at: float, deadline: float, b_cap: int) -> dict[str, Any]:
        ids = tuple(str(x) for x in slot_ids)
        if not ids or len(set(ids)) != len(ids):
            raise ValueError("nonempty unique slots required")
        if not math.isfinite(admitted_at) or not math.isfinite(deadline) or deadline < admitted_at:
            raise ValueError("invalid times")
        if int(b_cap) < len(ids):
            raise ValueError("b_cap too small")
        return {
            "schema_version": 1, "kind": "ADMIT", "event_id": f"admit:{block_id}",
            "block_id": str(block_id), "slot_ids": list(ids), "admitted_at": float(admitted_at),
            "deadline": float(deadline), "b_cap": int(b_cap),
        }

    @staticmethod
    def slot_event(block_id: str, slot_id: str, score: float, observed_at: float) -> dict[str, Any]:
        y = float(score)
        if not math.isfinite(y) or y < 0 or y > 1:
            raise ValueError("score must lie in [0,1]")
        return {
            "schema_version": 1, "kind": "SLOT", "event_id": f"slot:{block_id}:{slot_id}",
            "block_id": str(block_id), "slot_id": str(slot_id), "score": y, "observed_at": float(observed_at),
        }

    @staticmethod
    def close_event(block_id: str, closed_at: float) -> dict[str, Any]:
        return {
            "schema_version": 1, "kind": "CLOSE", "event_id": f"close:{block_id}",
            "block_id": str(block_id), "closed_at": float(closed_at),
        }

    def _dedupe(self, event: dict[str, Any]) -> str:
        eid = str(event["event_id"])
        digest = event_digest(event)
        old = self.seen_event_digest.get(eid)
        if old is None:
            self.seen_event_digest[eid] = digest
            return "new"
        if old == digest:
            return "duplicate"
        self.anomalies.append({"type": "event_id_conflict", "event_id": eid})
        return "conflict"

    def apply(self, event: dict[str, Any]) -> str:
        status = self._dedupe(event)
        if status == "duplicate":
            return "duplicate_ignored"
        if status == "conflict":
            return "conflict_ignored"
        kind = event.get("kind")
        bid = str(event.get("block_id"))

        if kind == "ADMIT":
            if bid in self.closed_by_block:
                self.anomalies.append({"type": "admit_after_close", "block_id": bid})
                return "admit_after_close_ignored"
            if self.active is not None:
                self.anomalies.append({"type": "admit_while_active", "block_id": bid})
                return "admit_while_active_ignored"
            ids = tuple(str(x) for x in event["slot_ids"])
            if not ids or len(set(ids)) != len(ids) or int(event["b_cap"]) < len(ids):
                raise JournalProtocolError("invalid admitted plan")
            self.active = ActiveBlock(bid, ids, float(event["admitted_at"]), float(event["deadline"]), int(event["b_cap"]))
            return "admitted"

        if kind == "SLOT":
            if bid in self.closed_by_block:
                self.anomalies.append({"type": "slot_after_close", "block_id": bid, "slot_id": event["slot_id"]})
                return "slot_after_close_ignored"
            if self.active is None or self.active.block_id != bid:
                self.anomalies.append({"type": "slot_without_active", "block_id": bid, "slot_id": event["slot_id"]})
                return "slot_without_active_ignored"
            sid = str(event["slot_id"])
            if sid not in self.active.slot_ids:
                self.anomalies.append({"type": "slot_not_admitted", "block_id": bid, "slot_id": sid})
                return "slot_not_admitted_ignored"
            if sid in self.active.accepted:
                self.anomalies.append({"type": "slot_overwrite", "block_id": bid, "slot_id": sid})
                return "slot_overwrite_ignored"
            observed_at = float(event["observed_at"])
            if observed_at > self.active.deadline:
                self.anomalies.append({"type": "slot_after_deadline", "block_id": bid, "slot_id": sid})
                return "slot_after_deadline_ignored"
            y = float(event["score"])
            if not math.isfinite(y) or y < 0 or y > 1:
                raise JournalProtocolError("invalid slot score")
            self.active.accepted[sid] = (y, observed_at)
            return "slot_accepted"

        if kind == "CLOSE":
            if bid in self.closed_by_block:
                return "close_duplicate_semantic_ignored"
            if self.active is None or self.active.block_id != bid:
                self.anomalies.append({"type": "close_without_active", "block_id": bid})
                return "close_without_active_ignored"
            closed_at = float(event["closed_at"])
            if closed_at < self.active.deadline:
                self.anomalies.append({"type": "early_close", "block_id": bid})
                return "early_close_ignored"
            row = self.active.summary()
            self.closed_rows.append(row)
            self.closed_by_block[bid] = row
            self.active = None
            return "closed"

        raise JournalProtocolError(f"unknown kind {kind!r}")

    @classmethod
    def recover(cls, blob: bytes) -> tuple["AtomicDualChannelJournal", int, str]:
        events, valid_len, tail_status = decode_valid_prefix(blob)
        state = cls()
        for event in events:
            state.apply(event)
        return state, valid_len, tail_status

    def deterministic_recovery_close(self, recovered_at: float) -> dict[str, Any] | None:
        if self.active is None or recovered_at < self.active.deadline:
            return None
        return self.close_event(self.active.block_id, max(float(recovered_at), self.active.deadline))

    def replay_channels(self) -> tuple[list[tuple[float, float]], list[tuple[float, float]]]:
        process = [(1.0, row["block_score"]) for row in self.closed_rows]
        exposure = [(row["exposure_weight"], row["block_score"]) for row in self.closed_rows]
        return process, exposure
