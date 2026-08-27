"""Compliance-aware CLOSE/replay for reservation-bound evaluation evidence.

This superseding close/replay layer preserves legacy ADMIT/SLOT semantics but
changes the scientific closed row for active reservation-aware blocks:
only SLOTs accepted by ``reservation_compliance_auditor_2026-08-28.py`` may
contribute their recorded score. All other planned slots contribute 1.

A valid bound SLOT missing only sidecar COMMIT must be reconciled before CLOSE.
The resulting compliance audit and digest are embedded in CLOSE and rederived
on every replay from the pre-CLOSE main prefix plus reservation ledger.

Compatibility boundary
----------------------
Legacy ADMIT and legacy CLOSE events remain replayable. A compliance CLOSE uses
a new reporting binding. Any runtime component that still calls the older
``durable_k_guard_hybrid_journal`` replay directly must be upgraded before this
new CLOSE format is deployed; otherwise it will reject the changed closed row.
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
LEGACY_FILENAME = "durable_k_guard_hybrid_journal_2026-08-28.py"
LEGACY_BLOB = "d70f42076ad04549c82c5906132aaae59657e335"
AUDITOR_FILENAME = "reservation_compliance_auditor_2026-08-28.py"
AUDITOR_BLOB = "0a845daa2675ba2c769c231769b1729f7e78f01d"
SCHEMA_VERSION = 1

def _canon(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")

def _digest(obj: Any) -> str:
    return sha256(_canon(obj)).hexdigest()

def _json_obj(obj: Any) -> Any:
    return json.loads(_canon(obj).decode("utf-8"))

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
    return _load_sibling(ATOMIC_FILENAME, "_evaluation_compliance_close_atomic")

def _default_legacy() -> Any:
    return _load_sibling(LEGACY_FILENAME, "_evaluation_compliance_close_legacy")

def _default_auditor() -> Any:
    return _load_sibling(AUDITOR_FILENAME, "_evaluation_compliance_close_auditor")

def _binding() -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "atomic": {"filename": ATOMIC_FILENAME, "blob": ATOMIC_BLOB},
        "legacy_reporting": {"filename": LEGACY_FILENAME, "blob": LEGACY_BLOB},
        "reservation_compliance": {"filename": AUDITOR_FILENAME, "blob": AUDITOR_BLOB},
    }

class ComplianceCloseError(RuntimeError):
    pass

class RecoveryCommitRequired(ComplianceCloseError):
    def __init__(self, slots: tuple[str, ...]) -> None:
        self.slots = tuple(slots)
        super().__init__(f"reconcile bound SLOT COMMITs before CLOSE: {self.slots}")

@dataclass
class ComplianceReplayState:
    base: Any
    reporter: Any
    pending_token: Any | None
    latest_snapshot: dict[str, Any] | None
    latest_compliance: dict[str, Any] | None
    valid_len: int
    tail_status: str
    reporting_rows: int

    def state(self) -> dict[str, Any]:
        return {
            "closed_rows": len(self.base.closed_rows),
            "active_block": self.base.active.block_id if self.base.active is not None else None,
            "reporter": self.reporter.state(),
            "pending_token": asdict(self.pending_token) if self.pending_token is not None else None,
            "latest_snapshot": self.latest_snapshot,
            "latest_compliance": self.latest_compliance,
            "valid_len": self.valid_len,
            "tail_status": self.tail_status,
            "reporting_rows": self.reporting_rows,
        }

def _legacy_token_dict(legacy: Any, token: Any) -> dict[str, Any]:
    if hasattr(legacy, "_token_dict"):
        return legacy._token_dict(token)
    return asdict(token)

def _legacy_token_from_event(legacy: Any, event: dict[str, Any]) -> dict[str, Any]:
    if hasattr(legacy, "_token_from_event"):
        return legacy._token_from_event(event)
    token = event.get("reporting_admission")
    if not isinstance(token, dict) or event.get("reporting_admission_digest") != _digest(token):
        raise ComplianceCloseError("invalid legacy reporting admission")
    return token

def _legacy_snapshot_from_event(legacy: Any, event: dict[str, Any]) -> dict[str, Any]:
    if hasattr(legacy, "_snapshot_from_event"):
        return legacy._snapshot_from_event(event)
    snap = event.get("reporting_observation")
    if not isinstance(snap, dict) or event.get("reporting_observation_digest") != _digest(snap):
        raise ComplianceCloseError("invalid reporting observation")
    return snap

def _check_new_binding(event: dict[str, Any]) -> None:
    if event.get("reporting_binding") != _binding():
        raise ComplianceCloseError("compliance CLOSE reporting binding mismatch")

def _compliance_row(audit: Any) -> dict[str, Any]:
    return {
        "block_id": audit.block_id,
        "planned_size": audit.planned_size,
        "completed_canonical": audit.completed_compliant,
        "missing_or_failed": audit.fail_closed_slots,
        "block_score": audit.block_score,
        "exposure_weight": audit.exposure_weight,
    }

def recover(
    main_blob: bytes,
    ledger_blob: bytes,
    *,
    atomic_module: Any | None = None,
    legacy_module: Any | None = None,
    auditor_module: Any | None = None,
    attempt_module: Any | None = None,
    reporter_factory: Callable[[], Any] | None = None,
) -> ComplianceReplayState:
    atomic = atomic_module or _default_atomic()
    legacy = legacy_module or _default_legacy()
    auditor = auditor_module or _default_auditor()
    make_reporter = reporter_factory or legacy._default_reporter_factory()

    events, valid_len, tail_status = atomic.decode_valid_prefix(bytes(main_blob))
    base = atomic.AtomicDualChannelJournal()
    reporter = make_reporter()
    pending_token = None
    latest_snapshot = None
    latest_compliance = None
    reporting_rows = 0
    prefix = b""

    for event in events:
        kind = event.get("kind")
        if kind == "ADMIT":
            status = base.apply(event)
            if status == "admitted":
                legacy._check_binding(event)
                exposure_weight = len(event["slot_ids"]) / int(event["b_cap"])
                token = reporter.admit(exposure_weight)
                persisted = _legacy_token_from_event(legacy, event)
                if _legacy_token_dict(legacy, token) != persisted:
                    raise ComplianceCloseError("replayed admission token mismatch")
                if persisted.get("weight_prefix_digest") != event.get("reporting_weight_prefix_digest"):
                    raise ComplianceCloseError("admission weight-prefix digest mismatch")
                if pending_token is not None:
                    raise ComplianceCloseError("multiple pending reporting admissions")
                pending_token = token
            prefix += atomic.encode_frame(event)
            continue

        if kind == "SLOT":
            base.apply(event)
            prefix += atomic.encode_frame(event)
            continue

        if kind == "CLOSE" and "reservation_compliance" in event:
            if pending_token is None or base.active is None:
                raise ComplianceCloseError("compliance CLOSE lacks active admission")
            bid = str(event.get("block_id"))
            if base.active.block_id != bid:
                raise ComplianceCloseError("compliance CLOSE block mismatch")
            _check_new_binding(event)
            audit = auditor.audit_active_block(
                prefix, bytes(ledger_blob), block_id=bid,
                atomic_module=atomic, attempt_module=attempt_module,
            )
            persisted_audit = event.get("reservation_compliance")
            if not isinstance(persisted_audit, dict):
                raise ComplianceCloseError("missing persisted reservation compliance")
            if event.get("reservation_compliance_digest") != _digest(persisted_audit):
                raise ComplianceCloseError("persisted compliance digest mismatch")
            if persisted_audit != _json_obj(audit.payload()):
                raise ComplianceCloseError("rederived compliance audit mismatch")
            if audit.recovery_commits_required:
                raise ComplianceCloseError("closed block still had reconcilable missing COMMIT")
            expected_row = _compliance_row(audit)
            if event.get("reporting_closed_row") != expected_row:
                raise ComplianceCloseError("persisted compliance closed row mismatch")
            snapshot = reporter.observe(pending_token, float(audit.block_score))
            persisted_snapshot = _legacy_snapshot_from_event(legacy, event)
            if snapshot != persisted_snapshot:
                raise ComplianceCloseError("replayed compliance reporting snapshot mismatch")
            if persisted_snapshot.get("weight_prefix_digest") != event.get("reporting_weight_prefix_digest"):
                raise ComplianceCloseError("compliance close weight-prefix digest mismatch")

            status = base.apply(event)
            if status != "closed":
                raise ComplianceCloseError(f"atomic CLOSE rejected during compliance replay: {status}")
            base.closed_rows[-1] = expected_row
            base.closed_by_block[bid] = expected_row
            pending_token = None
            latest_snapshot = snapshot
            latest_compliance = persisted_audit
            reporting_rows += 1
            prefix += atomic.encode_frame(event)
            continue

        if kind == "CLOSE":
            active_before = base.active
            row_before = active_before.summary() if active_before is not None else None
            status = base.apply(event)
            if status == "closed":
                legacy._check_binding(event)
                if pending_token is None or row_before is None:
                    raise ComplianceCloseError("legacy CLOSE lacks pending admission")
                if event.get("reporting_closed_row") != row_before:
                    raise ComplianceCloseError("legacy closed-row mismatch")
                snapshot = reporter.observe(pending_token, float(row_before["block_score"]))
                persisted_snapshot = _legacy_snapshot_from_event(legacy, event)
                if snapshot != persisted_snapshot:
                    raise ComplianceCloseError("legacy reporting snapshot mismatch")
                if persisted_snapshot.get("weight_prefix_digest") != event.get("reporting_weight_prefix_digest"):
                    raise ComplianceCloseError("legacy close weight-prefix digest mismatch")
                pending_token = None
                latest_snapshot = snapshot
                latest_compliance = None
                reporting_rows += 1
            prefix += atomic.encode_frame(event)
            continue

        raise ComplianceCloseError(f"unknown main-journal kind {kind!r}")

    if (base.active is None) != (pending_token is None):
        raise ComplianceCloseError("base/reporting pending state diverged")
    return ComplianceReplayState(
        base=base,
        reporter=reporter,
        pending_token=pending_token,
        latest_snapshot=latest_snapshot,
        latest_compliance=latest_compliance,
        valid_len=valid_len,
        tail_status=tail_status,
        reporting_rows=reporting_rows,
    )

def prepare_close(
    main_blob: bytes,
    ledger_blob: bytes,
    *,
    block_id: str,
    closed_at: float,
    atomic_module: Any | None = None,
    legacy_module: Any | None = None,
    auditor_module: Any | None = None,
    attempt_module: Any | None = None,
    reporter_factory: Callable[[], Any] | None = None,
) -> tuple[bytes, dict[str, Any], dict[str, Any], Any]:
    atomic = atomic_module or _default_atomic()
    legacy = legacy_module or _default_legacy()
    auditor = auditor_module or _default_auditor()
    state = recover(
        bytes(main_blob), bytes(ledger_blob),
        atomic_module=atomic, legacy_module=legacy, auditor_module=auditor,
        attempt_module=attempt_module, reporter_factory=reporter_factory,
    )
    if state.tail_status != "clean_eof" or state.valid_len != len(main_blob):
        raise ComplianceCloseError("repair/quarantine main tail before CLOSE")
    if state.base.active is None or state.base.active.block_id != str(block_id):
        raise ComplianceCloseError("CLOSE lacks durable active block")
    if state.pending_token is None:
        raise ComplianceCloseError("CLOSE lacks pending reporting admission")
    if float(closed_at) < state.base.active.deadline:
        raise ComplianceCloseError("cannot prepare early CLOSE")

    audit = auditor.audit_active_block(
        bytes(main_blob), bytes(ledger_blob), block_id=str(block_id),
        atomic_module=atomic, attempt_module=attempt_module,
    )
    if audit.recovery_commits_required:
        raise RecoveryCommitRequired(tuple(audit.recovery_commits_required))

    snapshot = state.reporter.observe(state.pending_token, float(audit.block_score))
    event = atomic.AtomicDualChannelJournal.close_event(str(block_id), float(closed_at))
    event["reporting_binding"] = _binding()
    event["reporting_observation"] = snapshot
    event["reporting_observation_digest"] = _digest(snapshot)
    event["reporting_weight_prefix_digest"] = snapshot["weight_prefix_digest"]
    event["reporting_closed_row"] = _compliance_row(audit)
    audit_payload = _json_obj(audit.payload())
    event["reservation_compliance"] = audit_payload
    event["reservation_compliance_digest"] = _digest(audit_payload)
    event["reservation_compliance_contract"] = {
        "bound_slot_requires_reserve_binding_commit": True,
        "noncompliant_planned_slot_score": 1.0,
        "missing_commit_must_reconcile_before_close": True,
        "lower_level_slot_acceptance_is_not_scientific_authority": True,
    }
    return atomic.encode_frame(event), event, snapshot, audit

__all__ = [
    "ATOMIC_FILENAME", "ATOMIC_BLOB", "LEGACY_FILENAME", "LEGACY_BLOB",
    "AUDITOR_FILENAME", "AUDITOR_BLOB", "SCHEMA_VERSION",
    "ComplianceCloseError", "RecoveryCommitRequired", "ComplianceReplayState",
    "recover", "prepare_close",
]
