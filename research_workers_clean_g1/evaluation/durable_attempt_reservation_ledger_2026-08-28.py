"""Durable one-attempt reservation ledger for capability-gated evaluation scores.

A reservation is durably acknowledged before score generation. The default
retry policy is fail-closed: if a process crashes after reservation but before
a score-bearing SLOT becomes durable, recovery does not issue another launch
permit. This prevents a stochastic choose-among-retries channel at the cost of
marking the slot unresolved.

The sidecar ledger is launch-control state, not a replacement for the main
ADMIT/SLOT/CLOSE scientific journal. A durable SLOT remains the scientific
score evidence. Historical journal modules are unchanged.

Concurrency scope
-----------------
The ledger assumes its DurableAppendWriter serializes writers correctly. A
whole-file CAS without a cross-process lock is not sufficient mutual exclusion
for concurrent OS processes. The fail-closed retry rule prevents sequential
duplicate relaunch after recovery, but cooperating multi-process deployments
still need a writer lease/flock/fencing layer.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
import hmac
import json
import math
import secrets
from pathlib import Path
import sys
from typing import Any, Protocol

GATE_FILENAME = "durable_launch_capability_gate_2026-08-28.py"
GATE_BLOB = "e06dc0550f65182d31b96e6b841d680b487f3b41"
SCORE_WRAPPER_FILENAME = "score_launch_capability_wrapper_2026-08-28.py"
SCORE_WRAPPER_BLOB = "e610805ab1f495198c1b44ab82f02086233f1eda"
SCHEMA_VERSION = 1
_BOOT_SECRET = secrets.token_bytes(32)
FAIL_CLOSED = "fail_closed_unresolved"
DETERMINISTIC_REPLAY = "deterministic_attempt_id_replay"


def _canon(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _digest_obj(obj: Any) -> str:
    return sha256(_canon(obj)).hexdigest()


def _digest_bytes(blob: bytes) -> str:
    return sha256(blob).hexdigest()


def _encode_frame(event: dict[str, Any]) -> bytes:
    body = _canon(event)
    return f"{len(body):08x}:{sha256(body).hexdigest()}:".encode("ascii") + body + b"\n"


def _decode_valid_prefix(blob: bytes) -> tuple[list[dict[str, Any]], int, str]:
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
    return _load_sibling(GATE_FILENAME, "_evaluation_attempt_gate")


def _default_score_wrapper() -> Any:
    return _load_sibling(SCORE_WRAPPER_FILENAME, "_evaluation_attempt_score_wrapper")


class AttemptReservationError(RuntimeError):
    pass


class DurableAppendWriter(Protocol):
    def append_fsync_readback(self, expected_before: bytes, frame: bytes) -> bytes:
        ...


@dataclass(frozen=True)
class AttemptReservation:
    schema_version: int
    block_id: str
    slot_id: str
    capability_digest: str
    request_binding_digest: str
    attempt_id: str
    reserved_at: float
    retry_policy: str
    reservation_digest: str

    def payload(self) -> dict[str, Any]:
        d = asdict(self)
        d.pop("reservation_digest", None)
        return d


@dataclass(frozen=True)
class AttemptLaunchPermit:
    schema_version: int
    block_id: str
    slot_id: str
    capability_digest: str
    request_binding_digest: str
    attempt_id: str
    retry_policy: str
    reservation_digest: str
    ledger_prefix_len: int
    ledger_prefix_sha256: str
    permit_mac: str

    def payload(self) -> dict[str, Any]:
        d = asdict(self)
        d.pop("permit_mac", None)
        return d


@dataclass
class ReservationState:
    reservations: dict[str, AttemptReservation]
    commits: dict[str, dict[str, Any]]
    valid_len: int
    tail_status: str

    def key(self, block_id: str, slot_id: str) -> str:
        return f"{block_id}\x1f{slot_id}"


def _reservation_key(block_id: str, slot_id: str) -> str:
    return f"{block_id}\x1f{slot_id}"


def recover(blob: bytes) -> ReservationState:
    events, valid_len, tail_status = _decode_valid_prefix(blob)
    reservations: dict[str, AttemptReservation] = {}
    commits: dict[str, dict[str, Any]] = {}
    seen_event: dict[str, str] = {}
    for event in events:
        eid = str(event.get("event_id"))
        ed = _digest_obj(event)
        old = seen_event.get(eid)
        if old is not None:
            if old == ed:
                continue
            raise AttemptReservationError("conflicting reservation-ledger event_id")
        seen_event[eid] = ed
        kind = event.get("kind")
        block_id = str(event.get("block_id"))
        slot_id = str(event.get("slot_id"))
        key = _reservation_key(block_id, slot_id)
        if kind == "RESERVE":
            payload = event.get("reservation")
            if not isinstance(payload, dict):
                raise AttemptReservationError("missing reservation payload")
            if event.get("reservation_digest") != _digest_obj(payload):
                raise AttemptReservationError("reservation payload digest mismatch")
            reservation = AttemptReservation(**payload, reservation_digest=event["reservation_digest"])
            if key in reservations:
                raise AttemptReservationError("duplicate semantic reservation")
            reservations[key] = reservation
        elif kind == "COMMIT":
            if key not in reservations:
                raise AttemptReservationError("commit without reservation")
            if key in commits:
                raise AttemptReservationError("duplicate semantic commit")
            if event.get("reservation_digest") != reservations[key].reservation_digest:
                raise AttemptReservationError("commit reservation digest mismatch")
            commits[key] = event
        else:
            raise AttemptReservationError(f"unknown reservation-ledger kind {kind!r}")
    return ReservationState(reservations, commits, valid_len, tail_status)


def _validate_capability_for_slot(
    main_blob: bytes,
    capability: Any,
    block_id: str,
    slot_id: str,
    *,
    gate: Any,
    adapter: Any,
) -> None:
    gate._verify_capability_against_blob(
        bytes(main_blob), capability, block_id=str(block_id), slot_id=str(slot_id), adapter=adapter
    )


def prepare_reservation(
    ledger_blob: bytes,
    main_blob: bytes,
    capability: Any,
    *,
    block_id: str,
    slot_id: str,
    request_binding: Any,
    reserved_at: float,
    retry_policy: str = FAIL_CLOSED,
    gate_module: Any | None = None,
    adapter_module: Any | None = None,
    score_wrapper_module: Any | None = None,
) -> tuple[bytes, dict[str, Any], AttemptReservation]:
    gate = gate_module or _default_gate()
    adapter = adapter_module or gate._default_adapter()
    score_wrapper = score_wrapper_module or _default_score_wrapper()
    _validate_capability_for_slot(main_blob, capability, block_id, slot_id, gate=gate, adapter=adapter)
    if retry_policy not in {FAIL_CLOSED, DETERMINISTIC_REPLAY}:
        raise AttemptReservationError("unsupported retry policy")
    if not math.isfinite(float(reserved_at)):
        raise AttemptReservationError("non-finite reserved_at")
    state = recover(bytes(ledger_blob))
    if state.tail_status != "clean_eof":
        raise AttemptReservationError("repair/quarantine torn reservation tail before reserve")
    key = _reservation_key(str(block_id), str(slot_id))
    if key in state.reservations:
        raise AttemptReservationError("slot already has a durable attempt reservation")

    req_digest = _digest_obj(request_binding)
    attempt_id = score_wrapper._attempt_id(
        capability.capability_digest, str(block_id), str(slot_id), req_digest
    )
    payload = {
        "schema_version": SCHEMA_VERSION,
        "block_id": str(block_id),
        "slot_id": str(slot_id),
        "capability_digest": capability.capability_digest,
        "request_binding_digest": req_digest,
        "attempt_id": attempt_id,
        "reserved_at": float(reserved_at),
        "retry_policy": retry_policy,
    }
    rd = _digest_obj(payload)
    reservation = AttemptReservation(**payload, reservation_digest=rd)
    event = {
        "schema_version": SCHEMA_VERSION,
        "kind": "RESERVE",
        "event_id": f"reserve:{block_id}:{slot_id}",
        "block_id": str(block_id),
        "slot_id": str(slot_id),
        "reservation": payload,
        "reservation_digest": rd,
        "gate_binding": {"filename": GATE_FILENAME, "blob": GATE_BLOB},
        "score_wrapper_binding": {"filename": SCORE_WRAPPER_FILENAME, "blob": SCORE_WRAPPER_BLOB},
    }
    return _encode_frame(event), event, reservation


def acknowledge_reservation(
    ledger_before: bytes,
    reservation_frame: bytes,
    durable_readback: bytes,
) -> AttemptLaunchPermit:
    expected = bytes(ledger_before) + bytes(reservation_frame)
    if durable_readback != expected:
        raise AttemptReservationError("durable reservation readback mismatch")
    state = recover(expected)
    if state.tail_status != "clean_eof" or state.valid_len != len(expected):
        raise AttemptReservationError("reservation ledger did not recover cleanly")
    events, _, _ = _decode_valid_prefix(expected)
    if not events or events[-1].get("kind") != "RESERVE":
        raise AttemptReservationError("ack boundary is not RESERVE")
    event = events[-1]
    key = _reservation_key(str(event["block_id"]), str(event["slot_id"]))
    reservation = state.reservations[key]
    payload = {
        "schema_version": SCHEMA_VERSION,
        "block_id": reservation.block_id,
        "slot_id": reservation.slot_id,
        "capability_digest": reservation.capability_digest,
        "request_binding_digest": reservation.request_binding_digest,
        "attempt_id": reservation.attempt_id,
        "retry_policy": reservation.retry_policy,
        "reservation_digest": reservation.reservation_digest,
        "ledger_prefix_len": len(expected),
        "ledger_prefix_sha256": _digest_bytes(expected),
    }
    mac = hmac.new(_BOOT_SECRET, _canon(payload), sha256).hexdigest()
    return AttemptLaunchPermit(**payload, permit_mac=mac)


def reserve_and_issue(
    writer: DurableAppendWriter,
    ledger_blob: bytes,
    main_blob: bytes,
    capability: Any,
    **kwargs: Any,
) -> tuple[bytes, AttemptLaunchPermit, AttemptReservation]:
    frame, _event, reservation = prepare_reservation(
        ledger_blob, main_blob, capability, **kwargs
    )
    durable = writer.append_fsync_readback(bytes(ledger_blob), frame)
    permit = acknowledge_reservation(ledger_blob, frame, durable)
    return durable, permit, reservation


def validate_launch_permit(
    ledger_blob: bytes,
    permit: AttemptLaunchPermit,
    *,
    allow_recovery_replay: bool = False,
) -> AttemptReservation:
    expected_mac = hmac.new(_BOOT_SECRET, _canon(permit.payload()), sha256).hexdigest()
    if not hmac.compare_digest(permit.permit_mac, expected_mac):
        raise AttemptReservationError("launch permit is invalid for this process epoch")
    if len(ledger_blob) < permit.ledger_prefix_len:
        raise AttemptReservationError("reservation ledger shorter than permit prefix")
    prefix = bytes(ledger_blob[:permit.ledger_prefix_len])
    if _digest_bytes(prefix) != permit.ledger_prefix_sha256:
        raise AttemptReservationError("reservation ledger prefix changed")
    state = recover(bytes(ledger_blob))
    if state.tail_status != "clean_eof":
        raise AttemptReservationError("repair/quarantine torn reservation tail before launch")
    key = _reservation_key(permit.block_id, permit.slot_id)
    reservation = state.reservations.get(key)
    if reservation is None or reservation.reservation_digest != permit.reservation_digest:
        raise AttemptReservationError("reservation missing or changed")
    if key in state.commits:
        raise AttemptReservationError("attempt already committed")
    if reservation.retry_policy == FAIL_CLOSED and allow_recovery_replay:
        raise AttemptReservationError("fail-closed reservation cannot be relaunched after recovery")
    if reservation.retry_policy == DETERMINISTIC_REPLAY and allow_recovery_replay:
        return reservation
    return reservation


def recover_deterministic_replay_permit(
    ledger_blob: bytes,
    main_blob: bytes,
    capability: Any,
    *,
    block_id: str,
    slot_id: str,
    request_binding: Any,
    gate_module: Any | None = None,
    adapter_module: Any | None = None,
    score_wrapper_module: Any | None = None,
) -> AttemptLaunchPermit:
    """Explicitly reissue only the same attempt under deterministic-replay policy.

    A fail-closed reservation can never be recovered into a new launch permit.
    """
    gate = gate_module or _default_gate()
    adapter = adapter_module or gate._default_adapter()
    score_wrapper = score_wrapper_module or _default_score_wrapper()
    _validate_capability_for_slot(main_blob, capability, block_id, slot_id, gate=gate, adapter=adapter)
    state = recover(bytes(ledger_blob))
    if state.tail_status != "clean_eof":
        raise AttemptReservationError("repair/quarantine torn reservation tail before recovery")
    key = _reservation_key(str(block_id), str(slot_id))
    reservation = state.reservations.get(key)
    if reservation is None:
        raise AttemptReservationError("no durable reservation to recover")
    if key in state.commits:
        raise AttemptReservationError("attempt already committed")
    if reservation.retry_policy != DETERMINISTIC_REPLAY:
        raise AttemptReservationError("fail-closed reservation cannot be relaunched")
    req_digest = _digest_obj(request_binding)
    expected_attempt = score_wrapper._attempt_id(
        capability.capability_digest, str(block_id), str(slot_id), req_digest
    )
    if (
        reservation.capability_digest != capability.capability_digest
        or reservation.request_binding_digest != req_digest
        or reservation.attempt_id != expected_attempt
    ):
        raise AttemptReservationError("recovery binding differs from durable reservation")
    payload = {
        "schema_version": SCHEMA_VERSION,
        "block_id": reservation.block_id,
        "slot_id": reservation.slot_id,
        "capability_digest": reservation.capability_digest,
        "request_binding_digest": reservation.request_binding_digest,
        "attempt_id": reservation.attempt_id,
        "retry_policy": reservation.retry_policy,
        "reservation_digest": reservation.reservation_digest,
        "ledger_prefix_len": len(ledger_blob),
        "ledger_prefix_sha256": _digest_bytes(bytes(ledger_blob)),
    }
    mac = hmac.new(_BOOT_SECRET, _canon(payload), sha256).hexdigest()
    return AttemptLaunchPermit(**payload, permit_mac=mac)


def recovery_disposition(ledger_blob: bytes, *, block_id: str, slot_id: str) -> str:
    state = recover(bytes(ledger_blob))
    if state.tail_status != "clean_eof":
        return "repair_tail_before_decision"
    key = _reservation_key(str(block_id), str(slot_id))
    reservation = state.reservations.get(key)
    if reservation is None:
        return "unreserved"
    if key in state.commits:
        return "committed_no_relaunch"
    if reservation.retry_policy == DETERMINISTIC_REPLAY:
        return "same_attempt_replay_requires_explicit_recovery_authorization"
    return "fail_closed_unresolved_no_relaunch"


def prepare_commit(
    ledger_blob: bytes,
    permit: AttemptLaunchPermit,
    *,
    slot_event_digest: str,
    committed_at: float,
) -> tuple[bytes, dict[str, Any]]:
    reservation = validate_launch_permit(ledger_blob, permit)
    if not math.isfinite(float(committed_at)):
        raise AttemptReservationError("non-finite committed_at")
    event = {
        "schema_version": SCHEMA_VERSION,
        "kind": "COMMIT",
        "event_id": f"commit:{reservation.block_id}:{reservation.slot_id}",
        "block_id": reservation.block_id,
        "slot_id": reservation.slot_id,
        "reservation_digest": reservation.reservation_digest,
        "slot_event_digest": str(slot_event_digest),
        "committed_at": float(committed_at),
    }
    return _encode_frame(event), event


__all__ = [
    "GATE_FILENAME", "GATE_BLOB", "SCORE_WRAPPER_FILENAME", "SCORE_WRAPPER_BLOB",
    "SCHEMA_VERSION", "FAIL_CLOSED", "DETERMINISTIC_REPLAY",
    "AttemptReservationError", "AttemptReservation", "AttemptLaunchPermit", "ReservationState",
    "recover", "prepare_reservation", "acknowledge_reservation", "reserve_and_issue",
    "validate_launch_permit", "recover_deterministic_replay_permit", "recovery_disposition", "prepare_commit",
]
