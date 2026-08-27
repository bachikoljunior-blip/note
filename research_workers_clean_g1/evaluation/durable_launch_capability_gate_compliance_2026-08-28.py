"""Compliance-replay-aware durable launch capability gate.

This supersedes ``durable_launch_capability_gate_2026-08-28.py`` for runtimes
that may contain reservation-compliance CLOSE frames.

Why this exists
---------------
The historical launch gate delegated ADMIT/SLOT preparation and all recovery to
``durable_k_guard_hybrid_journal_2026-08-28.py``. A compliance CLOSE can
intentionally replace the raw lower-level block row with a fail-closed audited
row. Replaying that history through the historical adapter correctly rejects
the changed row, but that also prevents the *next* ADMIT.

This gate preserves the historical ADMIT wire format and score-wrapper API while
changing the recovery authority:
- ADMIT preparation and ADMIT acknowledgement replay through
  ``reservation_compliance_close_replay_2026-08-28.py``.
- SLOT authorization uses only raw append-only journal liveness/identity after a
  capability has already been issued by compliance-aware replay. It does not
  reinterpret historical numerical rows.
- the capability binds the exact durable ADMIT prefix and a digest of the
  compliance-replayed reporting history at admission.

The reservation ledger is required for ADMIT preparation/acknowledgement because
historical compliance CLOSE frames must be rederived against it. Per-slot
capability checks intentionally do not bind the changing reservation-ledger
prefix; reservations/COMMITs are enforced by the separate attempt-reservation
pipeline.

Compatibility
-------------
``_default_adapter()``, ``_verify_capability_against_blob`` and
``prepare_slot_authorized`` retain the signatures expected by the historical
score-launch wrapper. A caller that creates a new block must use
``admit_and_issue_capability(..., ledger_blob=...)`` from this module.

Historical files are not modified; this is a superseding runtime binding.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path
import sys
from typing import Any, Protocol

LEGACY_ADAPTER_FILENAME = "durable_k_guard_hybrid_journal_2026-08-28.py"
LEGACY_ADAPTER_BLOB = "d70f42076ad04549c82c5906132aaae59657e335"
COMPLIANCE_REPLAY_FILENAME = "reservation_compliance_close_replay_2026-08-28.py"
COMPLIANCE_REPLAY_BLOB = "ac69f485383118192b533e258bb6033b454ca9b3"
SCHEMA_VERSION = 2


def _canon(obj: Any) -> bytes:
    return json.dumps(
        obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


def _digest_obj(obj: Any) -> str:
    return sha256(_canon(obj)).hexdigest()


def _digest_bytes(blob: bytes) -> str:
    return sha256(blob).hexdigest()


def _load_sibling(filename: str, module_name: str) -> Any:
    p = Path(__file__).resolve().with_name(filename)
    s = spec_from_file_location(module_name, p)
    if s is None or s.loader is None:
        raise ImportError(p)
    m = module_from_spec(s)
    sys.modules[module_name] = m
    s.loader.exec_module(m)
    return m


def _default_adapter() -> Any:
    """Historical wire-format helper retained for score-wrapper compatibility."""
    return _load_sibling(LEGACY_ADAPTER_FILENAME, "_evaluation_compliance_launch_legacy")


def _default_compliance() -> Any:
    return _load_sibling(
        COMPLIANCE_REPLAY_FILENAME, "_evaluation_compliance_launch_replay"
    )


class LaunchCapabilityError(RuntimeError):
    pass


class DurableAppendWriter(Protocol):
    def append_fsync_readback(self, expected_before: bytes, frame: bytes) -> bytes:
        ...


@dataclass(frozen=True)
class LaunchCapability:
    schema_version: int
    block_id: str
    admit_event_id: str
    durable_prefix_len: int
    durable_prefix_sha256: str
    admit_event_digest: str
    reporting_admission_digest: str
    admitted_slot_set_digest: str
    deadline: float
    runtime_binding_digest: str
    compliance_history_digest: str
    capability_digest: str

    def payload(self) -> dict[str, Any]:
        d = asdict(self)
        d.pop("capability_digest", None)
        return d


@dataclass(frozen=True)
class _RawJournalState:
    base: Any
    active_admit: dict[str, Any] | None
    valid_len: int
    tail_status: str


def _runtime_binding() -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "legacy_wire_adapter": {
            "filename": LEGACY_ADAPTER_FILENAME,
            "blob": LEGACY_ADAPTER_BLOB,
        },
        "compliance_replay": {
            "filename": COMPLIANCE_REPLAY_FILENAME,
            "blob": COMPLIANCE_REPLAY_BLOB,
        },
    }


def _validate_capability_integrity(cap: LaunchCapability) -> None:
    if int(cap.schema_version) != SCHEMA_VERSION:
        raise LaunchCapabilityError("unsupported capability schema")
    if cap.runtime_binding_digest != _digest_obj(_runtime_binding()):
        raise LaunchCapabilityError("runtime binding mismatch")
    if cap.capability_digest != _digest_obj(cap.payload()):
        raise LaunchCapabilityError("capability digest mismatch")


def _decode_exact_admit(prefix: bytes, legacy: Any) -> tuple[Any, dict[str, Any]]:
    atomic = legacy._default_atomic()
    events, valid_len, tail_status = atomic.decode_valid_prefix(prefix)
    if tail_status != "clean_eof" or valid_len != len(prefix) or not events:
        raise LaunchCapabilityError(
            "acknowledged prefix is not a complete clean journal"
        )
    event = events[-1]
    if event.get("kind") != "ADMIT":
        raise LaunchCapabilityError("acknowledged boundary is not ADMIT")
    return atomic, event


def _raw_journal_state(blob: bytes, legacy: Any) -> _RawJournalState:
    """Replay only atomic liveness/identity, never numerical reporting semantics."""
    atomic = legacy._default_atomic()
    events, valid_len, tail_status = atomic.decode_valid_prefix(bytes(blob))
    base = atomic.AtomicDualChannelJournal()
    active_admit = None
    for event in events:
        status = base.apply(event)
        if event.get("kind") == "ADMIT" and status == "admitted":
            active_admit = event
        elif event.get("kind") == "CLOSE" and status == "closed":
            active_admit = None
    return _RawJournalState(
        base=base,
        active_admit=active_admit,
        valid_len=valid_len,
        tail_status=tail_status,
    )


def _reporting_fingerprint(state: Any) -> dict[str, Any]:
    """Stable admission-time summary of compliance-replayed reporting history."""
    latest_compliance = getattr(state, "latest_compliance", None)
    latest_snapshot = getattr(state, "latest_snapshot", None)
    reporter_state = state.reporter.state()
    pending = getattr(state, "pending_token", None)
    if pending is None:
        pending_payload = None
    elif hasattr(pending, "__dataclass_fields__"):
        pending_payload = asdict(pending)
    elif isinstance(pending, dict):
        pending_payload = pending
    else:
        pending_payload = repr(pending)
    return {
        "closed_rows": len(state.base.closed_rows),
        "reporting_rows": int(state.reporting_rows),
        "reporter": reporter_state,
        "pending_token": pending_payload,
        "latest_snapshot": latest_snapshot,
        "latest_compliance_digest": (
            _digest_obj(latest_compliance) if latest_compliance is not None else None
        ),
    }


def _recover_compliance(
    main_blob: bytes,
    ledger_blob: bytes,
    *,
    legacy: Any,
    compliance: Any,
    attempt_module: Any | None,
    reporter_factory: Any | None,
) -> Any:
    return compliance.recover(
        bytes(main_blob),
        bytes(ledger_blob),
        legacy_module=legacy,
        attempt_module=attempt_module,
        reporter_factory=reporter_factory,
    )


def prepare_admit_compliance(
    main_blob: bytes,
    ledger_blob: bytes,
    *,
    block_id: str,
    slot_ids: list[str] | tuple[str, ...],
    admitted_at: float,
    deadline: float,
    b_cap: int,
    adapter_module: Any | None = None,
    compliance_module: Any | None = None,
    attempt_module: Any | None = None,
    reporter_factory: Any | None = None,
) -> tuple[bytes, dict[str, Any], dict[str, Any]]:
    """Prepare legacy-compatible ADMIT from compliance-replayed reporter state."""
    legacy = adapter_module or _default_adapter()
    compliance = compliance_module or _default_compliance()
    state = _recover_compliance(
        bytes(main_blob),
        bytes(ledger_blob),
        legacy=legacy,
        compliance=compliance,
        attempt_module=attempt_module,
        reporter_factory=reporter_factory,
    )
    if state.tail_status != "clean_eof" or state.valid_len != len(main_blob):
        raise LaunchCapabilityError("repair/quarantine main tail before ADMIT")
    if state.base.active is not None or state.pending_token is not None:
        raise LaunchCapabilityError("cannot admit while a block is active")

    atomic = legacy._default_atomic()
    event = atomic.AtomicDualChannelJournal.admit_event(
        str(block_id), slot_ids, float(admitted_at), float(deadline), int(b_cap)
    )
    exposure_weight = len(tuple(slot_ids)) / int(b_cap)
    token = state.reporter.admit(exposure_weight)
    td = legacy._token_dict(token)
    event["reporting_binding"] = legacy._binding()
    event["reporting_admission"] = td
    event["reporting_admission_digest"] = _digest_obj(td)
    event["reporting_weight_prefix_digest"] = td["weight_prefix_digest"]
    event["reporting_contract"] = {
        "pre_score_admission": True,
        "slot_launch_requires_durable_admit": True,
        "handoff_row_quarantined_if_guard_fails": True,
        "close_required_before_report_exposure": True,
        "recovery_authority": COMPLIANCE_REPLAY_FILENAME,
    }
    event["launch_gate_binding"] = _runtime_binding()
    event["launch_gate_pre_admit_history_digest"] = _digest_obj(
        _reporting_fingerprint(state)
    )
    return atomic.encode_frame(event), event, td


def acknowledge_admit(
    expected_before: bytes,
    admit_frame: bytes,
    durable_readback: bytes,
    *,
    ledger_blob: bytes,
    adapter_module: Any | None = None,
    compliance_module: Any | None = None,
    attempt_module: Any | None = None,
    reporter_factory: Any | None = None,
) -> LaunchCapability:
    """Issue capability only after exact durable ADMIT readback + compliance replay."""
    legacy = adapter_module or _default_adapter()
    compliance = compliance_module or _default_compliance()
    expected = bytes(expected_before) + bytes(admit_frame)
    if durable_readback != expected:
        raise LaunchCapabilityError(
            "durable readback does not exactly acknowledge expected ADMIT append"
        )
    _, event = _decode_exact_admit(expected, legacy)

    state = _recover_compliance(
        expected,
        bytes(ledger_blob),
        legacy=legacy,
        compliance=compliance,
        attempt_module=attempt_module,
        reporter_factory=reporter_factory,
    )
    if state.tail_status != "clean_eof" or state.valid_len != len(expected):
        raise LaunchCapabilityError("acknowledged journal did not recover cleanly")
    if state.base.active is None or state.pending_token is None:
        raise LaunchCapabilityError(
            "acknowledged ADMIT is not the active durable admission"
        )
    if state.base.active.block_id != str(event.get("block_id")):
        raise LaunchCapabilityError(
            "active block differs from acknowledged ADMIT"
        )

    persisted_reporting_digest = event.get("reporting_admission_digest")
    if not isinstance(persisted_reporting_digest, str):
        raise LaunchCapabilityError("ADMIT lacks reporting admission digest")
    slot_ids = event.get("slot_ids")
    if not isinstance(slot_ids, list) or not slot_ids:
        raise LaunchCapabilityError("ADMIT lacks slot set")

    payload = {
        "schema_version": SCHEMA_VERSION,
        "block_id": str(event["block_id"]),
        "admit_event_id": str(event["event_id"]),
        "durable_prefix_len": len(expected),
        "durable_prefix_sha256": _digest_bytes(expected),
        "admit_event_digest": _digest_obj(event),
        "reporting_admission_digest": persisted_reporting_digest,
        "admitted_slot_set_digest": _digest_obj(slot_ids),
        "deadline": float(event["deadline"]),
        "runtime_binding_digest": _digest_obj(_runtime_binding()),
        "compliance_history_digest": _digest_obj(_reporting_fingerprint(state)),
    }
    return LaunchCapability(**payload, capability_digest=_digest_obj(payload))


def admit_and_issue_capability(
    writer: DurableAppendWriter,
    main_blob: bytes,
    ledger_blob: bytes,
    *,
    block_id: str,
    slot_ids: list[str] | tuple[str, ...],
    admitted_at: float,
    deadline: float,
    b_cap: int,
    adapter_module: Any | None = None,
    compliance_module: Any | None = None,
    attempt_module: Any | None = None,
    reporter_factory: Any | None = None,
) -> tuple[bytes, LaunchCapability, dict[str, Any]]:
    frame, event, _preview = prepare_admit_compliance(
        bytes(main_blob),
        bytes(ledger_blob),
        block_id=block_id,
        slot_ids=slot_ids,
        admitted_at=admitted_at,
        deadline=deadline,
        b_cap=b_cap,
        adapter_module=adapter_module,
        compliance_module=compliance_module,
        attempt_module=attempt_module,
        reporter_factory=reporter_factory,
    )
    durable = writer.append_fsync_readback(bytes(main_blob), frame)
    cap = acknowledge_admit(
        bytes(main_blob),
        frame,
        durable,
        ledger_blob=bytes(ledger_blob),
        adapter_module=adapter_module,
        compliance_module=compliance_module,
        attempt_module=attempt_module,
        reporter_factory=reporter_factory,
    )
    return durable, cap, event


def _verify_capability_against_blob(
    blob: bytes,
    cap: LaunchCapability,
    *,
    block_id: str,
    slot_id: str,
    adapter: Any,
) -> None:
    """Verify durable prefix and current raw active-block identity.

    This deliberately does *not* run legacy numerical replay; the capability was
    issued only after compliance-aware replay, and reservations may legitimately
    advance their sidecar ledger after issuance.
    """
    _validate_capability_integrity(cap)
    if str(block_id) != cap.block_id:
        raise LaunchCapabilityError("wrong block for launch capability")
    if len(blob) < cap.durable_prefix_len:
        raise LaunchCapabilityError(
            "journal is shorter than acknowledged capability prefix"
        )

    prefix = bytes(blob[: cap.durable_prefix_len])
    if _digest_bytes(prefix) != cap.durable_prefix_sha256:
        raise LaunchCapabilityError("acknowledged durable prefix changed")
    _, event = _decode_exact_admit(prefix, adapter)
    if _digest_obj(event) != cap.admit_event_digest:
        raise LaunchCapabilityError("ADMIT event digest mismatch")
    if (
        str(event.get("event_id")) != cap.admit_event_id
        or str(event.get("block_id")) != cap.block_id
    ):
        raise LaunchCapabilityError("ADMIT identity mismatch")
    if event.get("reporting_admission_digest") != cap.reporting_admission_digest:
        raise LaunchCapabilityError("reporting admission digest mismatch")
    if _digest_obj(event.get("slot_ids")) != cap.admitted_slot_set_digest:
        raise LaunchCapabilityError("admitted slot-set digest mismatch")
    if float(event.get("deadline")) != float(cap.deadline):
        raise LaunchCapabilityError("deadline mismatch")
    if str(slot_id) not in {str(x) for x in event.get("slot_ids", [])}:
        raise LaunchCapabilityError("slot is outside acknowledged admission")

    raw = _raw_journal_state(bytes(blob), adapter)
    if raw.tail_status != "clean_eof" or raw.valid_len != len(blob):
        raise LaunchCapabilityError(
            "repair/quarantine torn tail before slot launch"
        )
    if raw.base.active is None or raw.active_admit is None:
        raise LaunchCapabilityError(
            "launch capability is stale: no active durable admission"
        )
    if str(raw.active_admit.get("event_id")) != cap.admit_event_id:
        raise LaunchCapabilityError(
            "launch capability is stale: active ADMIT identity changed"
        )
    if _digest_obj(raw.active_admit) != cap.admit_event_digest:
        raise LaunchCapabilityError(
            "launch capability is stale: active ADMIT content changed"
        )
    if raw.base.active.block_id != cap.block_id:
        raise LaunchCapabilityError(
            "launch capability is stale: another block is active"
        )
    if float(raw.base.active.deadline) != float(cap.deadline):
        raise LaunchCapabilityError(
            "active deadline differs from capability"
        )
    if _digest_obj(list(raw.base.active.slot_ids)) != cap.admitted_slot_set_digest:
        raise LaunchCapabilityError(
            "active slot plan differs from capability"
        )


def prepare_slot_authorized(
    blob: bytes,
    capability: LaunchCapability,
    *,
    block_id: str,
    slot_id: str,
    score: float,
    observed_at: float,
    adapter_module: Any | None = None,
    reporter_factory: Any | None = None,
) -> tuple[bytes, dict[str, Any]]:
    """Prepare historical SLOT wire format after compliance-capability validation."""
    del reporter_factory
    legacy = adapter_module or _default_adapter()
    _verify_capability_against_blob(
        bytes(blob),
        capability,
        block_id=str(block_id),
        slot_id=str(slot_id),
        adapter=legacy,
    )
    atomic = legacy._default_atomic()
    event = atomic.AtomicDualChannelJournal.slot_event(
        str(block_id), str(slot_id), float(score), float(observed_at)
    )
    return atomic.encode_frame(event), event


__all__ = [
    "LEGACY_ADAPTER_FILENAME",
    "LEGACY_ADAPTER_BLOB",
    "COMPLIANCE_REPLAY_FILENAME",
    "COMPLIANCE_REPLAY_BLOB",
    "SCHEMA_VERSION",
    "LaunchCapabilityError",
    "DurableAppendWriter",
    "LaunchCapability",
    "prepare_admit_compliance",
    "acknowledge_admit",
    "admit_and_issue_capability",
    "prepare_slot_authorized",
]
