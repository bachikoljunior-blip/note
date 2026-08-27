"""Durable pre-score K-guard admission over the existing ADMIT/SLOT/CLOSE journal.

This adapter makes the numerical-reporting admission a property of durable
operation order rather than caller convention.

Scientific ordering contract
----------------------------
1. ``prepare_admit`` replays only the durable journal, performs the K-guard
   admission on a fresh reporter reconstructed from that journal, and embeds
   the resulting admission token into the ADMIT frame.
2. The caller MUST durably append/fsync the returned ADMIT frame before
   launching any slot whose score can affect that block. If persistence is
   uncertain, the in-memory preview is discarded and state is recovered from
   the journal; no slot may be launched from the speculative preview.
3. SLOT evidence is unchanged and is scientific only after its complete frame
   is durable.
4. ``prepare_close`` replays from the durable prefix, deterministically computes
   the fail-closed block score, consumes the one pending admission, and embeds
   the numerical-reporting snapshot in the CLOSE frame. The caller MUST durably
   append/fsync CLOSE before exposing that numerical report externally.
5. Recovery replays every persisted reporting admission/observation and rejects
   any token, weight-prefix, handoff, or snapshot mismatch. The first K-failing
   row therefore remains quarantined across crash/restart and cannot enter
   either same-history or fresh confirmation.

The adapter intentionally does not create a second durable numerical state.
The append-only journal remains scientific truth; reporter caches are rebuilt
from it. It binds the exact sibling modules below so historical replay cannot
silently change statistical semantics.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path
import sys
from typing import Any, Callable

ATOMIC_FILENAME = "atomic_dual_channel_journal_2026-08-27T2107_JST.py"
ATOMIC_BLOB = "36540f1e8d0b47d4c678f091da87e90c385ef6f7"
REPORTER_FILENAME = "v3_k_guard_hybrid_reporter_2026-08-28.py"
REPORTER_BLOB = "66a3f0744deb3ba5c5ee52a2e29f683fa8e94987"
V3_FILENAME = "weighted_average_incremental_lsm_v3_warm_root_2026-08-27.py"
V3_BLOB = "54159990956368010b3445909f8bd8e8f569ecb7"
K_GUARD_FILENAME = "v3_same_history_K_guard_2026-08-28_v2.py"
K_GUARD_BLOB = "6f4a5ef2340730b5de493ad46ec21650486689f4"
SCHEMA_VERSION = 1


def _canon(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _digest(obj: Any) -> str:
    return sha256(_canon(obj)).hexdigest()


def _load_sibling(filename: str, module_name: str) -> Any:
    p = Path(__file__).resolve().with_name(filename)
    s = spec_from_file_location(module_name, p)
    if s is None or s.loader is None:
        raise ImportError(p)
    m = module_from_spec(s)
    sys.modules[module_name] = m
    s.loader.exec_module(m)
    return m


def _default_atomic() -> Any:
    return _load_sibling(ATOMIC_FILENAME, "_evaluation_durable_hybrid_atomic")


def _default_reporter_factory() -> Callable[[], Any]:
    m = _load_sibling(REPORTER_FILENAME, "_evaluation_durable_hybrid_reporter")
    return m.KGuardHybridReporter


def _binding() -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "atomic": {"filename": ATOMIC_FILENAME, "blob": ATOMIC_BLOB},
        "reporter": {"filename": REPORTER_FILENAME, "blob": REPORTER_BLOB},
        "v3": {"filename": V3_FILENAME, "blob": V3_BLOB},
        "k_guard": {"filename": K_GUARD_FILENAME, "blob": K_GUARD_BLOB},
    }


class DurableHybridProtocolError(RuntimeError):
    pass


@dataclass
class DurableHybridState:
    base: Any
    reporter: Any
    pending_token: Any | None
    latest_snapshot: dict[str, Any] | None
    valid_len: int
    tail_status: str
    reporting_rows: int

    def state(self) -> dict[str, Any]:
        return {
            "base_closed_rows": len(self.base.closed_rows),
            "base_active_block": self.base.active.block_id if self.base.active is not None else None,
            "reporter": self.reporter.state(),
            "pending_token": asdict(self.pending_token) if self.pending_token is not None else None,
            "latest_snapshot": self.latest_snapshot,
            "valid_len": self.valid_len,
            "tail_status": self.tail_status,
            "reporting_rows": self.reporting_rows,
        }


def _check_binding(event: dict[str, Any]) -> None:
    got = event.get("reporting_binding")
    if got != _binding():
        raise DurableHybridProtocolError("reporting module binding mismatch")


def _token_dict(token: Any) -> dict[str, Any]:
    return asdict(token)


def _token_from_event(event: dict[str, Any]) -> dict[str, Any]:
    token = event.get("reporting_admission")
    if not isinstance(token, dict):
        raise DurableHybridProtocolError("missing durable reporting admission")
    if event.get("reporting_admission_digest") != _digest(token):
        raise DurableHybridProtocolError("reporting admission digest mismatch")
    return token


def _snapshot_from_event(event: dict[str, Any]) -> dict[str, Any]:
    snap = event.get("reporting_observation")
    if not isinstance(snap, dict):
        raise DurableHybridProtocolError("missing durable reporting observation")
    if event.get("reporting_observation_digest") != _digest(snap):
        raise DurableHybridProtocolError("reporting observation digest mismatch")
    return snap


def recover(
    blob: bytes,
    *,
    atomic_module: Any | None = None,
    reporter_factory: Callable[[], Any] | None = None,
) -> DurableHybridState:
    """Replay the valid durable prefix and rederive all reporter state.

    A torn final frame is ignored exactly as in the underlying journal. Any
    complete reporting frame whose persisted token/snapshot disagrees with the
    bound reporter semantics fails closed rather than being silently repaired.
    """
    atomic = atomic_module or _default_atomic()
    make_reporter = reporter_factory or _default_reporter_factory()
    events, valid_len, tail_status = atomic.decode_valid_prefix(blob)
    base = atomic.AtomicDualChannelJournal()
    reporter = make_reporter()
    pending_token = None
    latest_snapshot = None
    reporting_rows = 0

    for event in events:
        kind = event.get("kind")
        if kind == "ADMIT":
            status = base.apply(event)
            if status != "admitted":
                continue
            _check_binding(event)
            planned_size = len(event["slot_ids"])
            b_cap = int(event["b_cap"])
            exposure_weight = planned_size / b_cap
            token = reporter.admit(exposure_weight)
            persisted = _token_from_event(event)
            if _token_dict(token) != persisted:
                raise DurableHybridProtocolError("replayed admission token mismatch")
            if persisted.get("weight_prefix_digest") != event.get("reporting_weight_prefix_digest"):
                raise DurableHybridProtocolError("durable weight-prefix digest mismatch")
            if pending_token is not None:
                raise DurableHybridProtocolError("multiple pending reporting admissions")
            pending_token = token
            continue

        if kind == "CLOSE":
            active_before = base.active
            row_before = active_before.summary() if active_before is not None else None
            status = base.apply(event)
            if status != "closed":
                continue
            _check_binding(event)
            if pending_token is None or row_before is None:
                raise DurableHybridProtocolError("closed block lacks pending reporting admission")
            if event.get("reporting_closed_row") != row_before:
                raise DurableHybridProtocolError("durable closed-row summary mismatch")
            snapshot = reporter.observe(pending_token, float(row_before["block_score"]))
            persisted = _snapshot_from_event(event)
            if snapshot != persisted:
                raise DurableHybridProtocolError("replayed reporting snapshot mismatch")
            if persisted.get("weight_prefix_digest") != event.get("reporting_weight_prefix_digest"):
                raise DurableHybridProtocolError("close weight-prefix digest mismatch")
            pending_token = None
            latest_snapshot = snapshot
            reporting_rows += 1
            continue

        base.apply(event)

    if (base.active is None) != (pending_token is None):
        raise DurableHybridProtocolError("base/reporting pending state diverged")
    return DurableHybridState(
        base=base,
        reporter=reporter,
        pending_token=pending_token,
        latest_snapshot=latest_snapshot,
        valid_len=valid_len,
        tail_status=tail_status,
        reporting_rows=reporting_rows,
    )


def prepare_admit(
    blob: bytes,
    *,
    block_id: str,
    slot_ids: list[str] | tuple[str, ...],
    admitted_at: float,
    deadline: float,
    b_cap: int,
    atomic_module: Any | None = None,
    reporter_factory: Callable[[], Any] | None = None,
) -> tuple[bytes, dict[str, Any], dict[str, Any]]:
    """Prepare, but do not persist, an ADMIT frame.

    The returned frame is launch authority only after durable append/fsync. The
    third return value is informational preview state and is not scientific
    state until that durable acknowledgement occurs.
    """
    atomic = atomic_module or _default_atomic()
    state = recover(blob, atomic_module=atomic, reporter_factory=reporter_factory)
    if state.tail_status != "clean_eof":
        raise DurableHybridProtocolError("truncate/quarantine torn tail before preparing ADMIT")
    if state.base.active is not None or state.pending_token is not None:
        raise DurableHybridProtocolError("cannot admit while a block is active")
    event = atomic.AtomicDualChannelJournal.admit_event(block_id, slot_ids, admitted_at, deadline, b_cap)
    exposure_weight = len(tuple(slot_ids)) / int(b_cap)
    token = state.reporter.admit(exposure_weight)
    td = _token_dict(token)
    event["reporting_binding"] = _binding()
    event["reporting_admission"] = td
    event["reporting_admission_digest"] = _digest(td)
    event["reporting_weight_prefix_digest"] = td["weight_prefix_digest"]
    event["reporting_contract"] = {
        "pre_score_admission": True,
        "slot_launch_requires_durable_admit": True,
        "handoff_row_quarantined_if_guard_fails": True,
        "close_required_before_report_exposure": True,
    }
    return atomic.encode_frame(event), event, td


def prepare_slot(
    blob: bytes,
    *,
    block_id: str,
    slot_id: str,
    score: float,
    observed_at: float,
    atomic_module: Any | None = None,
    reporter_factory: Callable[[], Any] | None = None,
) -> tuple[bytes, dict[str, Any]]:
    atomic = atomic_module or _default_atomic()
    state = recover(blob, atomic_module=atomic, reporter_factory=reporter_factory)
    if state.tail_status != "clean_eof":
        raise DurableHybridProtocolError("truncate/quarantine torn tail before preparing SLOT")
    if state.base.active is None or state.base.active.block_id != str(block_id):
        raise DurableHybridProtocolError("slot lacks its durable active ADMIT")
    event = atomic.AtomicDualChannelJournal.slot_event(block_id, slot_id, score, observed_at)
    return atomic.encode_frame(event), event


def prepare_close(
    blob: bytes,
    *,
    block_id: str,
    closed_at: float,
    atomic_module: Any | None = None,
    reporter_factory: Callable[[], Any] | None = None,
) -> tuple[bytes, dict[str, Any], dict[str, Any]]:
    """Prepare CLOSE with the deterministic reporting observation embedded.

    The returned snapshot MUST NOT be exposed as a durable numerical report
    until the returned CLOSE frame is durably appended/fsynced.
    """
    atomic = atomic_module or _default_atomic()
    state = recover(blob, atomic_module=atomic, reporter_factory=reporter_factory)
    if state.tail_status != "clean_eof":
        raise DurableHybridProtocolError("truncate/quarantine torn tail before preparing CLOSE")
    if state.base.active is None or state.base.active.block_id != str(block_id):
        raise DurableHybridProtocolError("close lacks its durable active ADMIT")
    if state.pending_token is None:
        raise DurableHybridProtocolError("close lacks pending reporting token")
    if float(closed_at) < state.base.active.deadline:
        raise DurableHybridProtocolError("cannot prepare an early CLOSE")

    row = state.base.active.summary()
    snapshot = state.reporter.observe(state.pending_token, float(row["block_score"]))
    event = atomic.AtomicDualChannelJournal.close_event(block_id, closed_at)
    event["reporting_binding"] = _binding()
    event["reporting_observation"] = snapshot
    event["reporting_observation_digest"] = _digest(snapshot)
    event["reporting_weight_prefix_digest"] = snapshot["weight_prefix_digest"]
    event["reporting_closed_row"] = row
    return atomic.encode_frame(event), event, snapshot


__all__ = [
    "ATOMIC_FILENAME", "ATOMIC_BLOB", "REPORTER_FILENAME", "REPORTER_BLOB",
    "V3_FILENAME", "V3_BLOB", "K_GUARD_FILENAME", "K_GUARD_BLOB",
    "DurableHybridProtocolError", "DurableHybridState", "recover",
    "prepare_admit", "prepare_slot", "prepare_close",
]
