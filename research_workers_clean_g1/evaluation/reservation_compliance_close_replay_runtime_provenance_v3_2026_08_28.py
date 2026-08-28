"""Forward-only CLOSE/replay v3 for versioned reservation runtime provenance.

This module is a superseding replay layer. It preserves already-durable
historical and current-v1 CLOSE histories, while introducing a new CLOSE
binding for schema-v2 ``replay_authorized_v1`` ADMITs. A replay-authorized
ADMIT can never be downgraded to the historical/current-v1 CLOSE binding, and a
historical/current-v1 ADMIT can never be upgraded into the v3 replay binding.

Only ``prepare_close`` for a recognized schema-v2 replay-authorized ADMIT is
newly generative here. Existing historical/current-v1 histories are replayed,
not re-emitted or reinterpreted.
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
CURRENT_V1_AUDITOR_FILENAME = "reservation_compliance_auditor_runtime_provenance_2026-08-28.py"
CURRENT_V1_AUDITOR_BLOB = "dd5e09bde7e91b0f534896922aeb5b2529e92996"
CURRENT_V1_CONTRACT_FILENAME = "reservation_runtime_provenance_contract_2026-08-28.py"
CURRENT_V1_CONTRACT_BLOB = "f6a4d996381bd100038d6ccfcf1b7c5f3f28e905"
V2_AUDITOR_FILENAME = "reservation_compliance_auditor_runtime_provenance_v2_2026_08_28.py"
V2_AUDITOR_BLOB = "b74465bd5f68882cee4c5b3fbd2a98d73a684b81"
V2_REGISTRY_FILENAME = "reservation_runtime_provenance_contract_registry_v2_2026_08_28.py"
V2_REGISTRY_BLOB = "c4d0439dba3ddf2183835c3fbaa3b3012ec1f468"
SCHEMA_VERSION = 3


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
    return _load(ATOMIC_FILENAME, "_evaluation_runtimeprov_v3_close_atomic")


def _default_legacy():
    return _load(LEGACY_FILENAME, "_evaluation_runtimeprov_v3_close_legacy")


def _default_historical_auditor():
    return _load(HISTORICAL_AUDITOR_FILENAME, "_evaluation_runtimeprov_v3_close_historical_auditor")


def _default_current_v1_auditor():
    return _load(CURRENT_V1_AUDITOR_FILENAME, "_evaluation_runtimeprov_v3_close_v1_auditor")


def _default_v2_auditor():
    return _load(V2_AUDITOR_FILENAME, "_evaluation_runtimeprov_v3_close_v2_auditor")


def _default_v2_registry():
    return _load(V2_REGISTRY_FILENAME, "_evaluation_runtimeprov_v3_close_registry")


def _historical_binding() -> dict[str, Any]:
    return {
        "schema_version": 1,
        "atomic": {"filename": ATOMIC_FILENAME, "blob": ATOMIC_BLOB},
        "legacy_reporting": {"filename": LEGACY_FILENAME, "blob": LEGACY_BLOB},
        "reservation_compliance": {"filename": HISTORICAL_AUDITOR_FILENAME, "blob": HISTORICAL_AUDITOR_BLOB},
    }


def _current_v1_binding() -> dict[str, Any]:
    return {
        "schema_version": 2,
        "atomic": {"filename": ATOMIC_FILENAME, "blob": ATOMIC_BLOB},
        "legacy_reporting": {"filename": LEGACY_FILENAME, "blob": LEGACY_BLOB},
        "reservation_compliance": {"filename": CURRENT_V1_AUDITOR_FILENAME, "blob": CURRENT_V1_AUDITOR_BLOB},
        "runtime_provenance_contract": {"filename": CURRENT_V1_CONTRACT_FILENAME, "blob": CURRENT_V1_CONTRACT_BLOB},
    }


def _replay_v3_binding() -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "atomic": {"filename": ATOMIC_FILENAME, "blob": ATOMIC_BLOB},
        "legacy_reporting": {"filename": LEGACY_FILENAME, "blob": LEGACY_BLOB},
        "reservation_compliance": {"filename": V2_AUDITOR_FILENAME, "blob": V2_AUDITOR_BLOB},
        "runtime_provenance_contract_registry": {"filename": V2_REGISTRY_FILENAME, "blob": V2_REGISTRY_BLOB},
        "required_admit_binding_id": "replay_authorized_v1",
    }


class ComplianceCloseRuntimeProvenanceV3Error(RuntimeError):
    pass


class RecoveryCommitRequired(ComplianceCloseRuntimeProvenanceV3Error):
    def __init__(self, slots):
        self.slots = tuple(slots)
        super().__init__(f"reconcile bound SLOT COMMITs before CLOSE: {self.slots}")


class ComplianceReplayStateV3:
    def __init__(self, base, reporter, pending_token, latest_snapshot, latest_compliance, valid_len, tail_status, reporting_rows, active_admit):
        self.base = base
        self.reporter = reporter
        self.pending_token = pending_token
        self.latest_snapshot = latest_snapshot
        self.latest_compliance = latest_compliance
        self.valid_len = valid_len
        self.tail_status = tail_status
        self.reporting_rows = reporting_rows
        self.active_admit = active_admit

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
            "active_runtime_contract": self.active_admit.get("reserved_score_runtime_contract") if isinstance(self.active_admit, dict) else None,
        }


def _token_dict(legacy, token):
    return legacy._token_dict(token) if hasattr(legacy, "_token_dict") else asdict(token)


def _token_from_event(legacy, event):
    if hasattr(legacy, "_token_from_event"):
        return legacy._token_from_event(event)
    token = event.get("reporting_admission")
    if not isinstance(token, dict) or event.get("reporting_admission_digest") != _digest(token):
        raise ComplianceCloseRuntimeProvenanceV3Error("invalid reporting admission")
    return token


def _snapshot_from_event(legacy, event):
    if hasattr(legacy, "_snapshot_from_event"):
        return legacy._snapshot_from_event(event)
    snap = event.get("reporting_observation")
    if not isinstance(snap, dict) or event.get("reporting_observation_digest") != _digest(snap):
        raise ComplianceCloseRuntimeProvenanceV3Error("invalid reporting observation")
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


def _raw_contract(admit: dict[str, Any] | None, registry: Any) -> dict[str, Any] | None:
    if not isinstance(admit, dict):
        return None
    c = admit.get(registry.CONTRACT_FIELD)
    return c if isinstance(c, dict) else None


def classify_admit_for_close(admit: dict[str, Any], registry: Any) -> tuple[str, str | None]:
    c = _raw_contract(admit, registry)
    if c is None:
        return "historical", None
    if c.get("schema_version") == 1:
        return "current_v1", registry.CURRENT_V1_BINDING_ID
    enforced, status, _expected, binding_id, fail_closed = registry.resolve_admit_binding(admit)
    if enforced and not fail_closed and status == "recognized_schema_v2" and binding_id == registry.REPLAY_AUTHORIZED_V1_BINDING_ID:
        return "replay_v2", binding_id
    return "invalid_v2_or_cross_version", binding_id


def select_replay_auditor(active_admit: dict[str, Any], reporting_binding: dict[str, Any], *, registry: Any, historical_auditor: Any, current_v1_auditor: Any, v2_auditor: Any) -> tuple[str, Any]:
    admit_class, _binding_id = classify_admit_for_close(active_admit, registry)
    if reporting_binding == _historical_binding():
        if admit_class != "historical":
            raise ComplianceCloseRuntimeProvenanceV3Error("runtime-contracted ADMIT cannot use historical compliance CLOSE")
        return "historical", historical_auditor
    if reporting_binding == _current_v1_binding():
        if admit_class not in {"historical", "current_v1"}:
            raise ComplianceCloseRuntimeProvenanceV3Error("schema-v2/unsupported ADMIT cannot use current-v1 compliance CLOSE")
        return "current_v1", current_v1_auditor
    if reporting_binding == _replay_v3_binding():
        if admit_class != "replay_v2":
            raise ComplianceCloseRuntimeProvenanceV3Error("replay-v3 compliance CLOSE requires recognized replay_authorized_v1 ADMIT")
        return "replay_v2", v2_auditor
    raise ComplianceCloseRuntimeProvenanceV3Error("unknown compliance CLOSE reporting binding")


def _audit_with_selected(selected_class: str, auditor: Any, *, prefix: bytes, ledger_blob: bytes, block_id: str, atomic: Any, attempt_module: Any, registry: Any):
    kwargs = {"block_id": str(block_id), "atomic_module": atomic, "attempt_module": attempt_module}
    if selected_class == "replay_v2":
        kwargs["contract_module"] = registry
    return auditor.audit_active_block(bytes(prefix), bytes(ledger_blob), **kwargs)


def recover(main_blob: bytes, ledger_blob: bytes, *, atomic_module=None, legacy_module=None, historical_auditor_module=None, current_v1_auditor_module=None, v2_auditor_module=None, registry_module=None, attempt_module=None, reporter_factory: Callable[[], Any] | None = None):
    atomic = atomic_module or _default_atomic()
    legacy = legacy_module or _default_legacy()
    historical = historical_auditor_module or _default_historical_auditor()
    current_v1 = current_v1_auditor_module or _default_current_v1_auditor()
    v2 = v2_auditor_module or _default_v2_auditor()
    registry = registry_module or _default_v2_registry()
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
                    raise ComplianceCloseRuntimeProvenanceV3Error("replayed admission token mismatch")
                if persisted.get("weight_prefix_digest") != event.get("reporting_weight_prefix_digest"):
                    raise ComplianceCloseRuntimeProvenanceV3Error("admission weight-prefix digest mismatch")
                if pending is not None:
                    raise ComplianceCloseRuntimeProvenanceV3Error("multiple pending reporting admissions")
                pending = token
            prefix += atomic.encode_frame(event)
            continue

        if kind == "SLOT":
            base.apply(event)
            prefix += atomic.encode_frame(event)
            continue

        if kind == "CLOSE" and "reservation_compliance" in event:
            if pending is None or base.active is None or active_admit is None:
                raise ComplianceCloseRuntimeProvenanceV3Error("compliance CLOSE lacks active admission")
            bid = str(event.get("block_id"))
            if base.active.block_id != bid:
                raise ComplianceCloseRuntimeProvenanceV3Error("compliance CLOSE block mismatch")
            selected_class, chosen = select_replay_auditor(active_admit, event.get("reporting_binding"), registry=registry, historical_auditor=historical, current_v1_auditor=current_v1, v2_auditor=v2)
            audit = _audit_with_selected(selected_class, chosen, prefix=prefix, ledger_blob=bytes(ledger_blob), block_id=bid, atomic=atomic, attempt_module=attempt_module, registry=registry)
            persisted_audit = event.get("reservation_compliance")
            if not isinstance(persisted_audit, dict) or event.get("reservation_compliance_digest") != _digest(persisted_audit):
                raise ComplianceCloseRuntimeProvenanceV3Error("persisted compliance digest mismatch")
            if persisted_audit != _json_obj(audit.payload()):
                raise ComplianceCloseRuntimeProvenanceV3Error("rederived compliance audit mismatch")
            if audit.recovery_commits_required:
                raise ComplianceCloseRuntimeProvenanceV3Error("closed block still had reconcilable missing COMMIT")
            row = _compliance_row(audit)
            if event.get("reporting_closed_row") != row:
                raise ComplianceCloseRuntimeProvenanceV3Error("persisted closed row mismatch")
            snapshot = reporter.observe(pending, float(audit.block_score))
            persisted_snapshot = _snapshot_from_event(legacy, event)
            if snapshot != persisted_snapshot:
                raise ComplianceCloseRuntimeProvenanceV3Error("replayed reporting snapshot mismatch")
            if persisted_snapshot.get("weight_prefix_digest") != event.get("reporting_weight_prefix_digest"):
                raise ComplianceCloseRuntimeProvenanceV3Error("close weight-prefix digest mismatch")
            status = base.apply(event)
            if status != "closed":
                raise ComplianceCloseRuntimeProvenanceV3Error(f"atomic CLOSE rejected: {status}")
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
            if active_admit is not None and _raw_contract(active_admit, registry) is not None:
                raise ComplianceCloseRuntimeProvenanceV3Error("runtime-contracted ADMIT cannot use legacy non-compliance CLOSE")
            active_before = base.active
            row_before = active_before.summary() if active_before is not None else None
            status = base.apply(event)
            if status == "closed":
                legacy._check_binding(event)
                if pending is None or row_before is None:
                    raise ComplianceCloseRuntimeProvenanceV3Error("legacy CLOSE lacks pending admission")
                if event.get("reporting_closed_row") != row_before:
                    raise ComplianceCloseRuntimeProvenanceV3Error("legacy closed-row mismatch")
                snapshot = reporter.observe(pending, float(row_before["block_score"]))
                persisted_snapshot = _snapshot_from_event(legacy, event)
                if snapshot != persisted_snapshot:
                    raise ComplianceCloseRuntimeProvenanceV3Error("legacy reporting snapshot mismatch")
                pending = None
                active_admit = None
                latest_snapshot = snapshot
                latest_compliance = None
                reporting_rows += 1
            prefix += atomic.encode_frame(event)
            continue

        raise ComplianceCloseRuntimeProvenanceV3Error(f"unknown main-journal kind {kind!r}")

    if (base.active is None) != (pending is None):
        raise ComplianceCloseRuntimeProvenanceV3Error("base/reporting pending state diverged")
    return ComplianceReplayStateV3(base, reporter, pending, latest_snapshot, latest_compliance, valid_len, tail_status, reporting_rows, active_admit)


def prepare_close(main_blob: bytes, ledger_blob: bytes, *, block_id: str, closed_at: float, atomic_module=None, legacy_module=None, historical_auditor_module=None, current_v1_auditor_module=None, v2_auditor_module=None, registry_module=None, attempt_module=None, reporter_factory=None):
    atomic = atomic_module or _default_atomic()
    legacy = legacy_module or _default_legacy()
    v2 = v2_auditor_module or _default_v2_auditor()
    registry = registry_module or _default_v2_registry()
    state = recover(bytes(main_blob), bytes(ledger_blob), atomic_module=atomic, legacy_module=legacy, historical_auditor_module=historical_auditor_module, current_v1_auditor_module=current_v1_auditor_module, v2_auditor_module=v2, registry_module=registry, attempt_module=attempt_module, reporter_factory=reporter_factory)
    if state.tail_status != "clean_eof" or state.valid_len != len(main_blob):
        raise ComplianceCloseRuntimeProvenanceV3Error("repair/quarantine main tail before CLOSE")
    if state.base.active is None or state.base.active.block_id != str(block_id) or state.pending_token is None or state.active_admit is None:
        raise ComplianceCloseRuntimeProvenanceV3Error("CLOSE lacks durable active block/reporting admission")
    if float(closed_at) < state.base.active.deadline:
        raise ComplianceCloseRuntimeProvenanceV3Error("cannot prepare early CLOSE")

    admit_class, binding_id = classify_admit_for_close(state.active_admit, registry)
    if admit_class != "replay_v2" or binding_id != registry.REPLAY_AUTHORIZED_V1_BINDING_ID:
        raise ComplianceCloseRuntimeProvenanceV3Error("v3 prepare_close is forward-only and requires recognized replay_authorized_v1 ADMIT")

    audit = v2.audit_active_block(bytes(main_blob), bytes(ledger_blob), block_id=str(block_id), contract_module=registry, atomic_module=atomic, attempt_module=attempt_module)
    if audit.recovery_commits_required:
        raise RecoveryCommitRequired(audit.recovery_commits_required)

    snapshot = state.reporter.observe(state.pending_token, float(audit.block_score))
    event = atomic.AtomicDualChannelJournal.close_event(str(block_id), float(closed_at))
    event["reporting_binding"] = _replay_v3_binding()
    event["reporting_observation"] = snapshot
    event["reporting_observation_digest"] = _digest(snapshot)
    event["reporting_weight_prefix_digest"] = snapshot["weight_prefix_digest"]
    event["reporting_closed_row"] = _compliance_row(audit)
    audit_payload = _json_obj(audit.payload())
    event["reservation_compliance"] = audit_payload
    event["reservation_compliance_digest"] = _digest(audit_payload)
    event["reservation_runtime_provenance_close_v3"] = {
        "forward_only": True,
        "required_admit_binding_id": registry.REPLAY_AUTHORIZED_V1_BINDING_ID,
        "historical_no_contract_replayed_not_reinterpreted": True,
        "current_schema_v1_replayed_not_reinterpreted": True,
        "cross_version_downgrade_rejected": True,
    }
    return atomic.encode_frame(event), event, snapshot, audit


__all__ = [
    "SCHEMA_VERSION", "ComplianceCloseRuntimeProvenanceV3Error", "RecoveryCommitRequired",
    "ComplianceReplayStateV3", "classify_admit_for_close", "select_replay_auditor",
    "recover", "prepare_close",
]
