"""Superseding reserved-score runtime bound to compliance-aware launch replay.

This module is the default-path bridge after
``durable_launch_capability_gate_compliance_2026-08-28.py``. Historical
reservation and score modules remain immutable, but every call that depends on
launch authority is injected with the compliance-aware gate.

It also corrects a provenance subtlety in the historical reservation module:
that module hard-codes the historical gate filename/blob into each RESERVE event
even when a different gate is dependency-injected. This facade rewrites only
that non-scientific provenance field before durable acknowledgement; the
reservation payload/digest and attempt identity are unchanged.
"""
from __future__ import annotations

from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path
import sys
from typing import Any

GATE_FILENAME = "durable_launch_capability_gate_compliance_2026-08-28.py"
GATE_BLOB = "a2aa84a3ef98d1647430a384a514d7cbc18303c3"
ATTEMPT_FILENAME = "durable_attempt_reservation_ledger_2026-08-28.py"
ATTEMPT_BLOB = "f51cc37e5897d8dc0f395da95c1f6dd1c12da791"
SCORE_FILENAME = "score_launch_capability_wrapper_2026-08-28.py"
SCORE_BLOB = "e610805ab1f495198c1b44ab82f02086233f1eda"
PIPELINE_FILENAME = "reserved_score_pipeline_2026-08-28.py"
PIPELINE_BLOB = "811bee4ddac614cd1ebd517a465cfb978006e91a"
CLOSE_FILENAME = "reservation_compliance_close_replay_2026-08-28.py"
CLOSE_BLOB = "ac69f485383118192b533e258bb6033b454ca9b3"
SCHEMA_VERSION = 1


def _canon(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()


def _digest(obj: Any) -> str:
    return sha256(_canon(obj)).hexdigest()


def _load(filename: str, name: str) -> Any:
    p = Path(__file__).resolve().with_name(filename)
    s = spec_from_file_location(name, p)
    if s is None or s.loader is None:
        raise ImportError(p)
    m = module_from_spec(s)
    sys.modules[name] = m
    s.loader.exec_module(m)
    return m


def _default_gate() -> Any:
    return _load(GATE_FILENAME, "_evaluation_compliance_runtime_gate")


def _default_attempt() -> Any:
    return _load(ATTEMPT_FILENAME, "_evaluation_compliance_runtime_attempt")


def _default_score() -> Any:
    return _load(SCORE_FILENAME, "_evaluation_compliance_runtime_score")


def _default_pipeline() -> Any:
    return _load(PIPELINE_FILENAME, "_evaluation_compliance_runtime_pipeline")


def _default_close() -> Any:
    return _load(CLOSE_FILENAME, "_evaluation_compliance_runtime_close")


def _binding() -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "gate": {"filename": GATE_FILENAME, "blob": GATE_BLOB},
        "attempt": {"filename": ATTEMPT_FILENAME, "blob": ATTEMPT_BLOB},
        "score": {"filename": SCORE_FILENAME, "blob": SCORE_BLOB},
        "pipeline": {"filename": PIPELINE_FILENAME, "blob": PIPELINE_BLOB},
        "compliance_close": {"filename": CLOSE_FILENAME, "blob": CLOSE_BLOB},
    }


class ComplianceReservedRuntimeError(RuntimeError):
    pass


def admit_and_issue_capability(
    writer: Any,
    main_blob: bytes,
    ledger_blob: bytes,
    **kwargs: Any,
) -> tuple[bytes, Any, dict[str, Any]]:
    gate = kwargs.pop("gate_module", None) or _default_gate()
    return gate.admit_and_issue_capability(
        writer, bytes(main_blob), bytes(ledger_blob), **kwargs
    )


def prepare_reservation(
    ledger_blob: bytes,
    main_blob: bytes,
    capability: Any,
    *,
    attempt_module: Any | None = None,
    gate_module: Any | None = None,
    score_module: Any | None = None,
    **kwargs: Any,
) -> tuple[bytes, dict[str, Any], Any]:
    attempt = attempt_module or _default_attempt()
    gate = gate_module or _default_gate()
    score = score_module or _default_score()
    legacy = gate._default_adapter()
    _old_frame, event, reservation = attempt.prepare_reservation(
        bytes(ledger_blob),
        bytes(main_blob),
        capability,
        gate_module=gate,
        adapter_module=legacy,
        score_wrapper_module=score,
        **kwargs,
    )
    event = dict(event)
    event["gate_binding"] = {"filename": GATE_FILENAME, "blob": GATE_BLOB}
    event["compliance_reserved_runtime_binding"] = _binding()
    if event.get("reservation_digest") != reservation.reservation_digest:
        raise ComplianceReservedRuntimeError("reservation digest changed before provenance rewrite")
    frame = attempt._encode_frame(event)
    return frame, event, reservation


def reserve_and_issue(
    writer: Any,
    ledger_blob: bytes,
    main_blob: bytes,
    capability: Any,
    **kwargs: Any,
) -> tuple[bytes, Any, Any]:
    attempt = kwargs.pop("attempt_module", None) or _default_attempt()
    gate = kwargs.pop("gate_module", None) or _default_gate()
    score = kwargs.pop("score_module", None) or _default_score()
    frame, _event, reservation = prepare_reservation(
        bytes(ledger_blob),
        bytes(main_blob),
        capability,
        attempt_module=attempt,
        gate_module=gate,
        score_module=score,
        **kwargs,
    )
    durable = writer.append_fsync_readback(bytes(ledger_blob), frame)
    permit = attempt.acknowledge_reservation(bytes(ledger_blob), frame, durable)
    return durable, permit, reservation


def launch_reserved_score(
    main_blob: bytes,
    ledger_blob: bytes,
    capability: Any,
    permit: Any,
    *,
    pipeline_module: Any | None = None,
    gate_module: Any | None = None,
    attempt_module: Any | None = None,
    score_module: Any | None = None,
    **kwargs: Any,
) -> Any:
    pipeline = pipeline_module or _default_pipeline()
    gate = gate_module or _default_gate()
    attempt = attempt_module or _default_attempt()
    score = score_module or _default_score()
    return pipeline.launch_reserved_score(
        bytes(main_blob),
        bytes(ledger_blob),
        capability,
        permit,
        gate_module=gate,
        adapter_module=gate._default_adapter(),
        score_module=score,
        attempt_module=attempt,
        **kwargs,
    )


def prepare_bound_slot(
    main_blob: bytes,
    ledger_blob: bytes,
    capability: Any,
    permit: Any,
    result: Any,
    *,
    pipeline_module: Any | None = None,
    gate_module: Any | None = None,
    attempt_module: Any | None = None,
    score_module: Any | None = None,
    **kwargs: Any,
) -> tuple[bytes, dict[str, Any], dict[str, Any]]:
    pipeline = pipeline_module or _default_pipeline()
    gate = gate_module or _default_gate()
    attempt = attempt_module or _default_attempt()
    score = score_module or _default_score()
    return pipeline.prepare_bound_slot(
        bytes(main_blob),
        bytes(ledger_blob),
        capability,
        permit,
        result,
        gate_module=gate,
        adapter_module=gate._default_adapter(),
        score_module=score,
        attempt_module=attempt,
        **kwargs,
    )


def prepare_commit(
    ledger_blob: bytes,
    permit: Any,
    *,
    slot_event_digest: str,
    committed_at: float,
    attempt_module: Any | None = None,
) -> tuple[bytes, dict[str, Any]]:
    attempt = attempt_module or _default_attempt()
    return attempt.prepare_commit(
        bytes(ledger_blob), permit,
        slot_event_digest=str(slot_event_digest), committed_at=float(committed_at),
    )


def prepare_recovery_commit_from_main(
    ledger_blob: bytes,
    main_blob: bytes,
    *,
    pipeline_module: Any | None = None,
    gate_module: Any | None = None,
    attempt_module: Any | None = None,
    **kwargs: Any,
) -> tuple[bytes, dict[str, Any], str]:
    pipeline = pipeline_module or _default_pipeline()
    gate = gate_module or _default_gate()
    attempt = attempt_module or _default_attempt()
    return pipeline.prepare_recovery_commit_from_main(
        bytes(ledger_blob),
        bytes(main_blob),
        gate_module=gate,
        adapter_module=gate._default_adapter(),
        attempt_module=attempt,
        **kwargs,
    )


def prepare_close(
    main_blob: bytes,
    ledger_blob: bytes,
    *,
    close_module: Any | None = None,
    gate_module: Any | None = None,
    attempt_module: Any | None = None,
    **kwargs: Any,
) -> tuple[bytes, dict[str, Any], dict[str, Any], Any]:
    close = close_module or _default_close()
    gate = gate_module or _default_gate()
    attempt = attempt_module or _default_attempt()
    legacy = gate._default_adapter()
    return close.prepare_close(
        bytes(main_blob),
        bytes(ledger_blob),
        legacy_module=legacy,
        attempt_module=attempt,
        **kwargs,
    )


def recover(
    main_blob: bytes,
    ledger_blob: bytes,
    *,
    close_module: Any | None = None,
    gate_module: Any | None = None,
    attempt_module: Any | None = None,
    **kwargs: Any,
) -> Any:
    close = close_module or _default_close()
    gate = gate_module or _default_gate()
    attempt = attempt_module or _default_attempt()
    return close.recover(
        bytes(main_blob),
        bytes(ledger_blob),
        legacy_module=gate._default_adapter(),
        attempt_module=attempt,
        **kwargs,
    )


__all__ = [
    "GATE_FILENAME", "GATE_BLOB", "ATTEMPT_FILENAME", "ATTEMPT_BLOB",
    "SCORE_FILENAME", "SCORE_BLOB", "PIPELINE_FILENAME", "PIPELINE_BLOB",
    "CLOSE_FILENAME", "CLOSE_BLOB", "SCHEMA_VERSION",
    "ComplianceReservedRuntimeError", "admit_and_issue_capability",
    "prepare_reservation", "reserve_and_issue", "launch_reserved_score",
    "prepare_bound_slot", "prepare_commit", "prepare_recovery_commit_from_main",
    "prepare_close", "recover",
]
