"""CLOSE/replay that enforces pre-score reservation runtime provenance.

Historical compliance CLOSE events remain replayable with the frozen historical
auditor. A block whose ADMIT contains ``reserved_score_runtime_contract`` may
only be closed by this new binding, which rederives the provenance-aware audit.
Thus the acceptance predicate is fixed before score generation and cannot be
bypassed by falling back to the historical CLOSE path.
"""
from __future__ import annotations
from dataclasses import asdict
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
HISTORICAL_AUDITOR_FILENAME = "reservation_compliance_auditor_2026-08-28.py"
HISTORICAL_AUDITOR_BLOB = "0a845daa2675ba2c769c231769b1729f7e78f01d"
AUDITOR_FILENAME = "reservation_compliance_auditor_runtime_provenance_2026-08-28.py"
AUDITOR_BLOB = "dd5e09bde7e91b0f534896922aeb5b2529e92996"
CONTRACT_FILENAME = "reservation_runtime_provenance_contract_2026-08-28.py"
CONTRACT_BLOB = "f6a4d996381bd100038d6ccfcf1b7c5f3f28e905"
SCHEMA_VERSION = 2


def _canon(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _digest(obj: Any) -> str:
    return sha256(_canon(obj)).hexdigest()


def _json_obj(obj: Any) -> Any:
    return json.loads(_canon(obj).decode("utf-8"))


def _load(filename: str, name: str) -> Any:
    p = Path(__file__).resolve().with_name(filename)
    s = spec_from_file_location(name, p)
    if s is None or s.loader is None:
        raise ImportError(p)
    m = module_from_spec(s)
    sys.modules[name] = m
    s.loader.exec_module(m)
    return m


def _default_atomic():
    return _load(ATOMIC_FILENAME, "_evaluation_runtimeprov_close_atomic")


def _default_legacy():
    return _load(LEGACY_FILENAME, "_evaluation_runtimeprov_close_legacy")


def _default_auditor():
    return _load(AUDITOR_FILENAME, "_evaluation_runtimeprov_close_auditor")


def _default_historical_auditor():
    return _load(HISTORICAL_AUDITOR_FILENAME, "_evaluation_runtimeprov_close_historical_auditor")


def _default_contract():
    return _load(CONTRACT_FILENAME, "_evaluation_runtimeprov_close_contract")


def _binding() -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "atomic": {"filename": ATOMIC_FILENAME, "blob": ATOMIC_BLOB},
        "legacy_reporting": {"filename": LEGACY_FILENAME, "blob": LEGACY_BLOB},
        "reservation_compliance": {"filename": AUDITOR_FILENAME, "blob": AUDITOR_BLOB},
        "runtime_provenance_contract": {"filename": CONTRACT_FILENAME, "blob": CONTRACT_BLOB},
    }


def _historical_binding() -> dict[str, Any]:
    return {
        "schema_version": 1,
        "atomic": {"filename": ATOMIC_FILENAME, "blob": ATOMIC_BLOB},
        "legacy_reporting": {"filename": LEGACY_FILENAME, "blob": LEGACY_BLOB},
        "reservation_compliance": {"filename": HISTORICAL_AUDITOR_FILENAME, "blob": HISTORICAL_AUDITOR_BLOB},
    }


class ComplianceCloseRuntimeProvenanceError(RuntimeError):
    pass


class RecoveryCommitRequired(ComplianceCloseRuntimeProvenanceError):
    def __init__(self, slots):
        self.slots = tuple(slots)
        super().__init__(f"reconcile bound SLOT COMMITs before CLOSE: {self.slots}")


class ComplianceReplayState:
    def __init__(self, base, reporter, pending_token, latest_snapshot, latest_compliance, valid_len, tail_status, reporting_rows):
        self.base = base
        self.reporter = reporter
        self.pending_token = pending_token
        self.latest_snapshot = latest_snapshot
        self.latest_compliance = latest_compliance
        self.valid_len = valid_len
        self.tail_status = tail_status
        self.reporting_rows = reporting_rows

    def state(self):
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


def _token_dict(legacy, token):
    return legacy._token_dict(token) if hasattr(legacy, "_token_dict") else asdict(token)


def _token_from_event(legacy, event):
    if hasattr(legacy, "_token_from_event"):
        return legacy._token_from_event(event)
    token = event.get("reporting_admission")
    if not isinstance(token, dict) or event.get("reporting_admission_digest") != _digest(token):
        raise ComplianceCloseRuntimeProvenanceError("invalid reporting admission")
    return token


def _snapshot_from_event(legacy, event):
    if hasattr(legacy, "_snapshot_from_event"):
        return legacy._snapshot_from_event(event)
    snap = event.get("reporting_observation")
    if not isinstance(snap, dict) or event.get("reporting_observation_digest") != _digest(snap):
        raise ComplianceCloseRuntimeProvenanceError("invalid reporting observation")
    return snap


def _compliance_row(audit):
    return {
        "block_id": audit.block_id,
        "planned_size": audit.planned_size,
        "completed_canonical": audit.completed_compliant,
        "missing_or_failed": audit.fail_closed_slots,
        "block_score": audit.block_score,
        "exposure_weight": audit.exposure_weight,
    }


def _has_runtime_contract(admit, contract):
    return isinstance(admit.get(contract.CONTRACT_FIELD), dict)


def recover(
    main_blob: bytes,
    ledger_blob: bytes,
    *,
    atomic_module=None,
    legacy_module=None,
    auditor_module=None,
    historical_auditor_module=None,
    contract_module=None,
    attempt_module=None,
    reporter_factory: Callable[[], Any] | None = None,
):
    atomic = atomic_module or _default_atomic()
    legacy = legacy_module or _default_legacy()
    auditor = auditor_module or _default_auditor()
    historical = historical_auditor_module or _default_historical_auditor()
    contract = contract_module or _default_contract()
    make_reporter = reporter_factory or legacy._default_reporter_factory()

    events, valid_len, tail_status = atomic.decode_valid_prefix(bytes(main_blob))
    base = atomic.AtomicDualChannelJournal()
    reporter = make_reporter()
    pending = None
    latest_snapshot = None
    latest_compliance = None
    reporting_rows = 0
    prefix = b""
    active_admit = None

    for event in events:
        kind = event.get("kind")
        if kind == "ADMIT":
            status = base.apply(event)
            if status == "admitted":
                legacy._check_binding(event)
                active_admit = event
                token = reporter.admit(len(event["slot_ids"]) / int(event["b_cap"]))
                persisted = _token_from_event(legacy, event)
                if _token_dict(legacy, token) != persisted:
                    raise ComplianceCloseRuntimeProvenanceError("replayed admission token mismatch")
                if persisted.get("weight_prefix_digest") != event.get("reporting_weight_prefix_digest"):
                    raise ComplianceCloseRuntimeProvenanceError("admission weight-prefix digest mismatch")
                if pending is not None:
                    raise ComplianceCloseRuntimeProvenanceError("multiple pending reporting admissions")
                pending = token
            prefix += atomic.encode_frame(event)
            continue

        if kind == "SLOT":
            base.apply(event)
            prefix += atomic.encode_frame(event)
            continue

        if kind == "CLOSE" and "reservation_compliance" in event:
            if pending is None or base.active is None or active_admit is None:
                raise ComplianceCloseRuntimeProvenanceError("compliance CLOSE lacks active admission")
            bid = str(event.get("block_id"))
            if base.active.block_id != bid:
                raise ComplianceCloseRuntimeProvenanceError("compliance CLOSE block mismatch")
            binding = event.get("reporting_binding")
            contracted = _has_runtime_contract(active_admit, contract)
            if binding == _binding():
                chosen = auditor
            elif binding == _historical_binding() and not contracted:
                chosen = historical
            elif binding == _historical_binding() and contracted:
                raise ComplianceCloseRuntimeProvenanceError(
                    "runtime-contracted ADMIT cannot use historical compliance CLOSE"
                )
            else:
                raise ComplianceCloseRuntimeProvenanceError("unknown compliance CLOSE reporting binding")

            audit = chosen.audit_active_block(
                prefix, bytes(ledger_blob), block_id=bid,
                atomic_module=atomic, attempt_module=attempt_module,
            )
            persisted_audit = event.get("reservation_compliance")
            if not isinstance(persisted_audit, dict) or event.get("reservation_compliance_digest") != _digest(persisted_audit):
                raise ComplianceCloseRuntimeProvenanceError("persisted compliance digest mismatch")
            if persisted_audit != _json_obj(audit.payload()):
                raise ComplianceCloseRuntimeProvenanceError("rederived compliance audit mismatch")
            if audit.recovery_commits_required:
                raise ComplianceCloseRuntimeProvenanceError("closed block still had reconcilable missing COMMIT")
            row = _compliance_row(audit)
            if event.get("reporting_closed_row") != row:
                raise ComplianceCloseRuntimeProvenanceError("persisted closed row mismatch")
            snapshot = reporter.observe(pending, float(audit.block_score))
            persisted_snapshot = _snapshot_from_event(legacy, event)
            if snapshot != persisted_snapshot:
                raise ComplianceCloseRuntimeProvenanceError("replayed reporting snapshot mismatch")
            if persisted_snapshot.get("weight_prefix_digest") != event.get("reporting_weight_prefix_digest"):
                raise ComplianceCloseRuntimeProvenanceError("close weight-prefix digest mismatch")
            status = base.apply(event)
            if status != "closed":
                raise ComplianceCloseRuntimeProvenanceError(f"atomic CLOSE rejected: {status}")
            base.closed_rows[-1] = row
            base.closed_by_block[bid] = row
            pending = None
            active_admit = None
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
                if pending is None or row_before is None:
                    raise ComplianceCloseRuntimeProvenanceError("legacy CLOSE lacks pending admission")
                if event.get("reporting_closed_row") != row_before:
                    raise ComplianceCloseRuntimeProvenanceError("legacy closed-row mismatch")
                snapshot = reporter.observe(pending, float(row_before["block_score"]))
                persisted_snapshot = _snapshot_from_event(legacy, event)
                if snapshot != persisted_snapshot:
                    raise ComplianceCloseRuntimeProvenanceError("legacy reporting snapshot mismatch")
                pending = None
                active_admit = None
                latest_snapshot = snapshot
                latest_compliance = None
                reporting_rows += 1
            prefix += atomic.encode_frame(event)
            continue

        raise ComplianceCloseRuntimeProvenanceError(f"unknown main-journal kind {kind!r}")

    if (base.active is None) != (pending is None):
        raise ComplianceCloseRuntimeProvenanceError("base/reporting pending state diverged")
    return ComplianceReplayState(
        base, reporter, pending, latest_snapshot, latest_compliance,
        valid_len, tail_status, reporting_rows,
    )


def prepare_close(
    main_blob: bytes,
    ledger_blob: bytes,
    *,
    block_id: str,
    closed_at: float,
    atomic_module=None,
    legacy_module=None,
    auditor_module=None,
    historical_auditor_module=None,
    contract_module=None,
    attempt_module=None,
    reporter_factory=None,
):
    atomic = atomic_module or _default_atomic()
    legacy = legacy_module or _default_legacy()
    auditor = auditor_module or _default_auditor()
    contract = contract_module or _default_contract()
    state = recover(
        bytes(main_blob), bytes(ledger_blob),
        atomic_module=atomic, legacy_module=legacy, auditor_module=auditor,
        historical_auditor_module=historical_auditor_module,
        contract_module=contract, attempt_module=attempt_module,
        reporter_factory=reporter_factory,
    )
    if state.tail_status != "clean_eof" or state.valid_len != len(main_blob):
        raise ComplianceCloseRuntimeProvenanceError("repair/quarantine main tail before CLOSE")
    if state.base.active is None or state.base.active.block_id != str(block_id) or state.pending_token is None:
        raise ComplianceCloseRuntimeProvenanceError("CLOSE lacks durable active block/reporting admission")
    if float(closed_at) < state.base.active.deadline:
        raise ComplianceCloseRuntimeProvenanceError("cannot prepare early CLOSE")

    audit = auditor.audit_active_block(
        bytes(main_blob), bytes(ledger_blob), block_id=str(block_id),
        atomic_module=atomic, attempt_module=attempt_module,
    )
    if audit.recovery_commits_required:
        raise RecoveryCommitRequired(audit.recovery_commits_required)

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
    event["reservation_runtime_provenance_contract"] = {
        "pre_score_admit_binding_required_for_enforcement": True,
        "historical_admits_not_reinterpreted": True,
        "runtime_contracted_admit_cannot_use_historical_close": True,
    }
    return atomic.encode_frame(event), event, snapshot, audit


__all__ = [
    "ComplianceCloseRuntimeProvenanceError", "RecoveryCommitRequired",
    "ComplianceReplayState", "recover", "prepare_close",
]
