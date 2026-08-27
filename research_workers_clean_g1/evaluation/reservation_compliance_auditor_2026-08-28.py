"""Reservation-aware fail-closed auditor for evaluation block CLOSE/replay.

This module is read-only over the main ADMIT/SLOT/CLOSE journal and the
one-attempt reservation ledger. It computes the *compliant scientific view*
of an active block without trusting lower-level SLOT acceptance.

A planned slot contributes its durable score only when:
1. a durable RESERVE exists for that exact block/slot;
2. the first canonical SLOT event is bound to that reservation;
3. the binding digest is valid and matches reservation identity;
4. a durable COMMIT exists and names the exact canonical SLOT event digest.

Otherwise the planned slot contributes score=1 (fail-closed). A valid bound
SLOT with no COMMIT is identified as reconcilable; callers should append the
recovery COMMIT, then re-audit before CLOSE. The auditor itself never launches
or re-runs a scorer.

This is an active-block compliance layer. It does not reinterpret already
closed historical blocks.
"""
from __future__ import annotations
from dataclasses import asdict, dataclass
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
import json
import math
from pathlib import Path
import sys
from typing import Any

ATOMIC_FILENAME = "atomic_dual_channel_journal_2026-08-27T2107_JST.py"
ATOMIC_BLOB = "36540f1e8d0b47d4c678f091da87e90c385ef6f7"
ATTEMPT_FILENAME = "durable_attempt_reservation_ledger_2026-08-28.py"
ATTEMPT_BLOB = "f51cc37e5897d8dc0f395da95c1f6dd1c12da791"
PIPELINE_FILENAME = "reserved_score_pipeline_2026-08-28.py"
PIPELINE_BLOB = "811bee4ddac614cd1ebd517a465cfb978006e91a"
SCHEMA_VERSION = 1

def _canon(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")

def _digest_obj(obj: Any) -> str:
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
    return _load_sibling(ATOMIC_FILENAME, "_evaluation_compliance_atomic")

def _default_attempt() -> Any:
    return _load_sibling(ATTEMPT_FILENAME, "_evaluation_compliance_attempt")

def _default_pipeline() -> Any:
    return _load_sibling(PIPELINE_FILENAME, "_evaluation_compliance_pipeline")

class ReservationComplianceError(RuntimeError):
    pass

@dataclass(frozen=True)
class SlotCompliance:
    slot_id: str
    status: str
    scientific_score: float
    slot_event_digest: str | None
    reservation_digest: str | None
    commit_event_digest: str | None
    reconcilable: bool

@dataclass(frozen=True)
class BlockComplianceAudit:
    schema_version: int
    block_id: str
    planned_size: int
    b_cap: int
    exposure_weight: float
    completed_compliant: int
    fail_closed_slots: int
    block_score: float
    all_slots_compliant: bool
    recovery_commits_required: tuple[str, ...]
    slot_audits: tuple[SlotCompliance, ...]
    active_event_conflicts: tuple[str, ...]
    out_of_plan_reservations: tuple[str, ...]
    compliance_digest: str

    def payload(self) -> dict[str, Any]:
        d = asdict(self)
        d.pop("compliance_digest", None)
        return d

def _canonicalize_active_events(events: list[dict[str, Any]], block_id: str, atomic: Any) -> tuple[list[dict[str, Any]], set[str]]:
    """Keep first event per event_id, record conflicting duplicate IDs for target block."""
    seen: dict[str, str] = {}
    out: list[dict[str, Any]] = []
    conflicts: set[str] = set()
    for event in events:
        eid = str(event.get("event_id"))
        digest = atomic.event_digest(event) if hasattr(atomic, "event_digest") else _digest_obj(event)
        old = seen.get(eid)
        if old is None:
            seen[eid] = digest
            out.append(event)
        elif old != digest and str(event.get("block_id")) == str(block_id):
            conflicts.add(eid)
    return out, conflicts

def _reservation_key(attempt: Any, block_id: str, slot_id: str) -> str:
    if hasattr(attempt, "_reservation_key"):
        return attempt._reservation_key(str(block_id), str(slot_id))
    return f"{block_id}\x1f{slot_id}"

def audit_active_block(
    main_blob: bytes,
    ledger_blob: bytes,
    *,
    block_id: str,
    atomic_module: Any | None = None,
    attempt_module: Any | None = None,
) -> BlockComplianceAudit:
    atomic = atomic_module or _default_atomic()
    attempt = attempt_module or _default_attempt()

    events, valid_len, tail_status = atomic.decode_valid_prefix(bytes(main_blob))
    if tail_status != "clean_eof" or valid_len != len(main_blob):
        raise ReservationComplianceError("repair/quarantine main-journal tail before compliance audit")
    try:
        reservation_state = attempt.recover(bytes(ledger_blob))
    except Exception as exc:
        raise ReservationComplianceError("reservation ledger recovery failed") from exc
    if reservation_state.tail_status != "clean_eof" or reservation_state.valid_len != len(ledger_blob):
        raise ReservationComplianceError("repair/quarantine reservation-ledger tail before compliance audit")

    canonical, conflicts = _canonicalize_active_events(events, str(block_id), atomic)
    admit_id = f"admit:{block_id}"
    if admit_id in conflicts:
        raise ReservationComplianceError("conflicting active ADMIT event")
    admits = [e for e in canonical if e.get("kind") == "ADMIT" and str(e.get("block_id")) == str(block_id)]
    if len(admits) != 1:
        raise ReservationComplianceError("expected exactly one canonical active ADMIT")
    if any(e.get("kind") == "CLOSE" and str(e.get("block_id")) == str(block_id) for e in canonical):
        raise ReservationComplianceError("block already has a canonical CLOSE")

    admit = admits[0]
    slot_ids = tuple(str(x) for x in admit.get("slot_ids", ()))
    if not slot_ids or len(set(slot_ids)) != len(slot_ids):
        raise ReservationComplianceError("invalid admitted slot plan")
    b_cap = int(admit["b_cap"])
    if b_cap < len(slot_ids):
        raise ReservationComplianceError("invalid admitted b_cap")

    slot_event_by_id: dict[str, dict[str, Any]] = {}
    for event in canonical:
        if event.get("kind") != "SLOT" or str(event.get("block_id")) != str(block_id):
            continue
        sid = str(event.get("slot_id"))
        if sid in slot_ids:
            slot_event_by_id[sid] = event

    prefix = f"{block_id}\x1f"
    out_of_plan: list[str] = []
    for key in reservation_state.reservations:
        if key.startswith(prefix):
            sid = key.split("\x1f", 1)[1]
            if sid not in slot_ids:
                out_of_plan.append(sid)
    if out_of_plan:
        out_of_plan.sort()

    audits: list[SlotCompliance] = []
    recovery_required: list[str] = []
    scores: list[float] = []

    for sid in slot_ids:
        eid = f"slot:{block_id}:{sid}"
        key = _reservation_key(attempt, str(block_id), sid)
        reservation = reservation_state.reservations.get(key)
        commit = reservation_state.commits.get(key)
        event = slot_event_by_id.get(sid)
        status: str
        score = 1.0
        reconcilable = False
        slot_digest: str | None = None
        reservation_digest = getattr(reservation, "reservation_digest", None) if reservation is not None else None
        commit_digest = _digest_obj(commit) if commit is not None else None

        if eid in conflicts:
            status = "slot_event_conflict"
        elif event is None:
            status = "reserved_missing_slot" if reservation is not None else "never_launched_missing_slot"
        elif reservation is None:
            status = "bypass_slot_without_reservation"
            slot_digest = atomic.event_digest(event) if hasattr(atomic, "event_digest") else _digest_obj(event)
        else:
            slot_digest = atomic.event_digest(event) if hasattr(atomic, "event_digest") else _digest_obj(event)
            binding = event.get("attempt_binding")
            if not isinstance(binding, dict):
                status = "reserved_slot_missing_attempt_binding"
            elif event.get("attempt_binding_digest") != _digest_obj(binding):
                status = "attempt_binding_digest_mismatch"
            else:
                expected = {
                    "schema_version": SCHEMA_VERSION,
                    "reservation_digest": reservation.reservation_digest,
                    "attempt_id": reservation.attempt_id,
                    "capability_digest": reservation.capability_digest,
                    "request_binding_digest": reservation.request_binding_digest,
                    "score_result_digest": binding.get("score_result_digest"),
                }
                if binding != expected:
                    status = "attempt_binding_reservation_mismatch"
                elif commit is None:
                    status = "bound_slot_missing_commit_reconcilable"
                    reconcilable = True
                    recovery_required.append(sid)
                elif commit.get("reservation_digest") != reservation.reservation_digest:
                    status = "commit_reservation_digest_mismatch"
                elif commit.get("slot_event_digest") != slot_digest:
                    status = "commit_slot_event_digest_mismatch"
                else:
                    y = float(event.get("score"))
                    if not math.isfinite(y) or y < 0 or y > 1:
                        status = "invalid_scientific_score"
                    else:
                        status = "compliant"
                        score = y

        scores.append(score)
        audits.append(SlotCompliance(
            slot_id=sid, status=status, scientific_score=score,
            slot_event_digest=slot_digest, reservation_digest=reservation_digest,
            commit_event_digest=commit_digest, reconcilable=reconcilable,
        ))

    block_score = sum(scores) / len(scores)
    completed = sum(a.status == "compliant" for a in audits)
    payload = {
        "schema_version": SCHEMA_VERSION,
        "block_id": str(block_id),
        "planned_size": len(slot_ids),
        "b_cap": b_cap,
        "exposure_weight": len(slot_ids) / b_cap,
        "completed_compliant": completed,
        "fail_closed_slots": len(slot_ids) - completed,
        "block_score": block_score,
        "all_slots_compliant": completed == len(slot_ids),
        "recovery_commits_required": tuple(recovery_required),
        "slot_audits": tuple(asdict(a) for a in audits),
        "active_event_conflicts": tuple(sorted(conflicts)),
        "out_of_plan_reservations": tuple(out_of_plan),
    }
    return BlockComplianceAudit(
        **{k: v for k, v in payload.items() if k != "slot_audits"},
        slot_audits=tuple(audits),
        compliance_digest=_digest_obj(payload),
    )

def prepare_one_recovery_commit(
    ledger_blob: bytes,
    main_blob: bytes,
    *,
    block_id: str,
    slot_id: str,
    committed_at: float,
    pipeline_module: Any | None = None,
) -> tuple[bytes, dict[str, Any], str]:
    pipeline = pipeline_module or _default_pipeline()
    return pipeline.prepare_recovery_commit_from_main(
        bytes(ledger_blob), bytes(main_blob),
        block_id=str(block_id), slot_id=str(slot_id), committed_at=float(committed_at),
    )

__all__ = [
    "ATOMIC_FILENAME", "ATOMIC_BLOB", "ATTEMPT_FILENAME", "ATTEMPT_BLOB",
    "PIPELINE_FILENAME", "PIPELINE_BLOB", "SCHEMA_VERSION",
    "ReservationComplianceError", "SlotCompliance", "BlockComplianceAudit",
    "audit_active_block", "prepare_one_recovery_commit",
]
