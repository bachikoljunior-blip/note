"""Reservation-aware score launch, bound SLOT persistence, and crash reconciliation.

This composes:
- durable ADMIT LaunchCapability,
- durable one-attempt reservation/AttemptLaunchPermit,
- pre-score capability-gated scoring,
- main-journal SLOT persistence enriched with immutable attempt binding,
- sidecar COMMIT after SLOT durability.

If a crash occurs after bound SLOT durability but before reservation COMMIT,
recovery can reconcile COMMIT from the durable main SLOT without re-running the
scorer. If no bound SLOT is durable, the default fail-closed reservation remains
unresolved and no stochastic retry is authorized.
"""
from __future__ import annotations

from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
import json
import math
from pathlib import Path
import sys
from typing import Any, Callable

GATE_FILENAME = "durable_launch_capability_gate_2026-08-28.py"
GATE_BLOB = "e06dc0550f65182d31b96e6b841d680b487f3b41"
SCORE_FILENAME = "score_launch_capability_wrapper_2026-08-28.py"
SCORE_BLOB = "e610805ab1f495198c1b44ab82f02086233f1eda"
ATTEMPT_FILENAME = "durable_attempt_reservation_ledger_2026-08-28.py"
ATTEMPT_BLOB = "f51cc37e5897d8dc0f395da95c1f6dd1c12da791"
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


def _default_gate() -> Any:
    return _load_sibling(GATE_FILENAME, "_evaluation_reserved_pipeline_gate")


def _default_score() -> Any:
    return _load_sibling(SCORE_FILENAME, "_evaluation_reserved_pipeline_score")


def _default_attempt() -> Any:
    return _load_sibling(ATTEMPT_FILENAME, "_evaluation_reserved_pipeline_attempt")


class ReservedPipelineError(RuntimeError):
    pass


def _verify_permit_bindings(capability: Any, permit: Any, request_binding: Any, *, score: Any) -> str:
    req_digest = score._digest(request_binding)
    if permit.capability_digest != capability.capability_digest:
        raise ReservedPipelineError("attempt permit belongs to another capability")
    if permit.request_binding_digest != req_digest:
        raise ReservedPipelineError("attempt permit request binding mismatch")
    expected_attempt = score._attempt_id(
        capability.capability_digest, permit.block_id, permit.slot_id, req_digest
    )
    if permit.attempt_id != expected_attempt:
        raise ReservedPipelineError("attempt permit identity mismatch")
    return req_digest


def launch_reserved_score(
    main_blob: bytes,
    ledger_blob: bytes,
    capability: Any,
    permit: Any,
    *,
    request_binding: Any,
    scorer: Callable[[str], float],
    clock: Callable[[], float],
    gate_module: Any | None = None,
    adapter_module: Any | None = None,
    score_module: Any | None = None,
    attempt_module: Any | None = None,
) -> Any:
    gate = gate_module or _default_gate()
    adapter = adapter_module or gate._default_adapter()
    score = score_module or _default_score()
    attempt = attempt_module or _default_attempt()
    reservation = attempt.validate_launch_permit(bytes(ledger_blob), permit)
    _verify_permit_bindings(capability, permit, request_binding, score=score)
    if reservation.block_id != permit.block_id or reservation.slot_id != permit.slot_id:
        raise ReservedPipelineError("reservation and permit scope differ")

    result = score.launch_score(
        main_blob,
        capability,
        block_id=permit.block_id,
        slot_id=permit.slot_id,
        request_binding=request_binding,
        scorer=scorer,
        clock=clock,
        gate_module=gate,
        adapter_module=adapter,
    )
    if result.attempt_id != permit.attempt_id:
        raise ReservedPipelineError("scorer result attempt differs from durable reservation")
    return result


def prepare_bound_slot(
    main_blob: bytes,
    ledger_blob: bytes,
    capability: Any,
    permit: Any,
    result: Any,
    *,
    request_binding: Any,
    gate_module: Any | None = None,
    adapter_module: Any | None = None,
    score_module: Any | None = None,
    attempt_module: Any | None = None,
    reporter_factory: Any | None = None,
) -> tuple[bytes, dict[str, Any], dict[str, Any]]:
    gate = gate_module or _default_gate()
    adapter = adapter_module or gate._default_adapter()
    score = score_module or _default_score()
    attempt = attempt_module or _default_attempt()
    reservation = attempt.validate_launch_permit(bytes(ledger_blob), permit)
    req_digest = _verify_permit_bindings(capability, permit, request_binding, score=score)
    frame, event = score.prepare_result_slot(
        main_blob,
        capability,
        result,
        request_binding=request_binding,
        gate_module=gate,
        adapter_module=adapter,
        reporter_factory=reporter_factory,
    )
    del frame
    if result.attempt_id != reservation.attempt_id:
        raise ReservedPipelineError("result does not match durable reservation attempt")
    binding = {
        "schema_version": SCHEMA_VERSION,
        "reservation_digest": reservation.reservation_digest,
        "attempt_id": reservation.attempt_id,
        "capability_digest": reservation.capability_digest,
        "request_binding_digest": req_digest,
        "score_result_digest": result.result_digest,
    }
    event = dict(event)
    event["attempt_binding"] = binding
    event["attempt_binding_digest"] = _digest_obj(binding)
    event["attempt_contract"] = {
        "reservation_required_before_score": True,
        "bound_slot_required_for_recovery_commit": True,
        "default_uncommitted_recovery": "fail_closed_unresolved_no_relaunch",
    }
    atomic = adapter._default_atomic()
    return atomic.encode_frame(event), event, binding


def persist_bound_slot(
    writer: Any,
    main_blob: bytes,
    ledger_blob: bytes,
    capability: Any,
    permit: Any,
    result: Any,
    *,
    request_binding: Any,
    gate_module: Any | None = None,
    adapter_module: Any | None = None,
    score_module: Any | None = None,
    attempt_module: Any | None = None,
    reporter_factory: Any | None = None,
) -> tuple[bytes, dict[str, Any], str]:
    frame, event, _binding = prepare_bound_slot(
        main_blob, ledger_blob, capability, permit, result,
        request_binding=request_binding,
        gate_module=gate_module, adapter_module=adapter_module,
        score_module=score_module, attempt_module=attempt_module,
        reporter_factory=reporter_factory,
    )
    durable = writer.append_fsync_readback(bytes(main_blob), frame)
    return durable, event, _digest_obj(event)


def prepare_recovery_commit_from_main(
    ledger_blob: bytes,
    main_blob: bytes,
    *,
    block_id: str,
    slot_id: str,
    committed_at: float,
    gate_module: Any | None = None,
    adapter_module: Any | None = None,
    attempt_module: Any | None = None,
) -> tuple[bytes, dict[str, Any], str]:
    """Reconcile only an already-durable bound SLOT; never re-run scoring."""
    gate = gate_module or _default_gate()
    adapter = adapter_module or gate._default_adapter()
    attempt = attempt_module or _default_attempt()
    if not math.isfinite(float(committed_at)):
        raise ReservedPipelineError("non-finite committed_at")
    state = attempt.recover(bytes(ledger_blob))
    if state.tail_status != "clean_eof":
        raise ReservedPipelineError("repair reservation tail before reconciliation")
    key = attempt._reservation_key(str(block_id), str(slot_id))
    reservation = state.reservations.get(key)
    if reservation is None:
        raise ReservedPipelineError("no reservation for main SLOT")
    if key in state.commits:
        raise ReservedPipelineError("reservation already committed")

    atomic = adapter._default_atomic()
    events, valid_len, tail_status = atomic.decode_valid_prefix(bytes(main_blob))
    if tail_status != "clean_eof" or valid_len != len(main_blob):
        raise ReservedPipelineError("main journal is not a clean durable prefix")
    target_id = f"slot:{block_id}:{slot_id}"
    matches = [e for e in events if str(e.get("event_id")) == target_id]
    if len(matches) != 1:
        raise ReservedPipelineError("expected exactly one durable SLOT event")
    slot_event = matches[0]
    if slot_event.get("kind") != "SLOT":
        raise ReservedPipelineError("target event is not SLOT")
    binding = slot_event.get("attempt_binding")
    if not isinstance(binding, dict):
        raise ReservedPipelineError("durable SLOT lacks attempt binding")
    if slot_event.get("attempt_binding_digest") != _digest_obj(binding):
        raise ReservedPipelineError("attempt binding digest mismatch")
    expected = {
        "schema_version": SCHEMA_VERSION,
        "reservation_digest": reservation.reservation_digest,
        "attempt_id": reservation.attempt_id,
        "capability_digest": reservation.capability_digest,
        "request_binding_digest": reservation.request_binding_digest,
        "score_result_digest": binding.get("score_result_digest"),
    }
    if binding != expected:
        raise ReservedPipelineError("durable SLOT binding differs from reservation")
    slot_event_digest = _digest_obj(slot_event)
    commit_event = {
        "schema_version": attempt.SCHEMA_VERSION,
        "kind": "COMMIT",
        "event_id": f"commit:{reservation.block_id}:{reservation.slot_id}",
        "block_id": reservation.block_id,
        "slot_id": reservation.slot_id,
        "reservation_digest": reservation.reservation_digest,
        "slot_event_digest": slot_event_digest,
        "committed_at": float(committed_at),
    }
    return attempt._encode_frame(commit_event), commit_event, slot_event_digest


def persist_recovery_commit(
    writer: Any,
    ledger_blob: bytes,
    main_blob: bytes,
    **kwargs: Any,
) -> tuple[bytes, dict[str, Any], str]:
    frame, event, slot_event_digest = prepare_recovery_commit_from_main(
        ledger_blob, main_blob, **kwargs
    )
    durable = writer.append_fsync_readback(bytes(ledger_blob), frame)
    return durable, event, slot_event_digest


__all__ = [
    "GATE_FILENAME", "GATE_BLOB", "SCORE_FILENAME", "SCORE_BLOB",
    "ATTEMPT_FILENAME", "ATTEMPT_BLOB", "SCHEMA_VERSION",
    "ReservedPipelineError", "launch_reserved_score", "prepare_bound_slot",
    "persist_bound_slot", "prepare_recovery_commit_from_main", "persist_recovery_commit",
]
