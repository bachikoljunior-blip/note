"""Durable ADMIT acknowledgement and launch-capability gate.

This module closes the remaining caller-discipline gap in the durable
ADMIT/SLOT/CLOSE adapter. A slot launcher must present a LaunchCapability that
can only be issued after an ADMIT frame has been append+fsync'd and read back
exactly.

Scope
-----
This is a crash/integrity capability, not an adversarial authentication token.
Its SHA-256 bindings detect stale, truncated, changed, or wrong-block durable
prefixes. It assumes the supplied DurableAppendWriter actually implements the
documented single-writer append+fsync+readback contract. A malicious caller
that bypasses this module and invokes the historical adapter directly is
outside this module's enforcement boundary; historical modules remain
immutable for reproducibility.

Scientific ordering contract
----------------------------
1. ``admit_and_issue_capability`` asks the bound adapter to prepare ADMIT.
2. The writer must CAS the expected current blob, append exactly that frame,
   fsync it, then return the complete durable journal bytes.
3. Only exact readback acknowledgement can issue a LaunchCapability.
4. ``prepare_slot_authorized`` is the slot-launch entry point. It rejects
   absent, malformed, stale, truncated, changed-prefix, wrong-block, wrong-slot,
   closed-block, and post-handoff capabilities before score-bearing SLOT
   preparation.
5. The same capability may authorize all slots of its one active block. It
   becomes unusable after CLOSE/recovery advances to another block.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path
import sys
from typing import Any, Protocol

ADAPTER_FILENAME = "durable_k_guard_hybrid_journal_2026-08-28.py"
ADAPTER_BLOB = "d70f42076ad04549c82c5906132aaae59657e335"
SCHEMA_VERSION = 1


def _canon(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


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
    return _load_sibling(ADAPTER_FILENAME, "_evaluation_launch_cap_adapter")


class LaunchCapabilityError(RuntimeError):
    pass


class DurableAppendWriter(Protocol):
    """Storage boundary required by ``admit_and_issue_capability``.

    The implementation must:
    - verify its current durable bytes equal ``expected_before`` (CAS);
    - append exactly ``frame`` once;
    - fsync/otherwise obtain the storage system's durability acknowledgement;
    - read back and return the complete durable journal bytes after that ack.

    Returning speculative page-cache or caller-memory bytes violates this API.
    """

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
    adapter_binding_digest: str
    capability_digest: str

    def payload(self) -> dict[str, Any]:
        d = asdict(self)
        d.pop("capability_digest", None)
        return d


def _adapter_binding() -> dict[str, Any]:
    return {"filename": ADAPTER_FILENAME, "blob": ADAPTER_BLOB}


def _validate_capability_integrity(cap: LaunchCapability) -> None:
    if int(cap.schema_version) != SCHEMA_VERSION:
        raise LaunchCapabilityError("unsupported capability schema")
    if cap.adapter_binding_digest != _digest_obj(_adapter_binding()):
        raise LaunchCapabilityError("adapter binding mismatch")
    if cap.capability_digest != _digest_obj(cap.payload()):
        raise LaunchCapabilityError("capability digest mismatch")


def _decode_exact_admit(prefix: bytes, adapter: Any) -> tuple[Any, dict[str, Any]]:
    atomic = adapter._default_atomic()
    events, valid_len, tail_status = atomic.decode_valid_prefix(prefix)
    if tail_status != "clean_eof" or valid_len != len(prefix) or not events:
        raise LaunchCapabilityError("acknowledged prefix is not a complete clean journal")
    event = events[-1]
    if event.get("kind") != "ADMIT":
        raise LaunchCapabilityError("acknowledged boundary is not ADMIT")
    return atomic, event


def acknowledge_admit(
    expected_before: bytes,
    admit_frame: bytes,
    durable_readback: bytes,
    *,
    adapter_module: Any | None = None,
) -> LaunchCapability:
    """Issue capability only after exact durable ADMIT readback acknowledgement."""
    adapter = adapter_module or _default_adapter()
    expected = bytes(expected_before) + bytes(admit_frame)
    if durable_readback != expected:
        raise LaunchCapabilityError("durable readback does not exactly acknowledge expected ADMIT append")
    _, event = _decode_exact_admit(expected, adapter)

    state = adapter.recover(expected)
    if state.tail_status != "clean_eof":
        raise LaunchCapabilityError("acknowledged journal did not recover cleanly")
    if state.base.active is None or state.pending_token is None:
        raise LaunchCapabilityError("acknowledged ADMIT is not the active durable admission")
    if state.base.active.block_id != str(event.get("block_id")):
        raise LaunchCapabilityError("active block differs from acknowledged ADMIT")

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
        "adapter_binding_digest": _digest_obj(_adapter_binding()),
    }
    return LaunchCapability(**payload, capability_digest=_digest_obj(payload))


def admit_and_issue_capability(
    writer: DurableAppendWriter,
    blob: bytes,
    *,
    block_id: str,
    slot_ids: list[str] | tuple[str, ...],
    admitted_at: float,
    deadline: float,
    b_cap: int,
    adapter_module: Any | None = None,
    reporter_factory: Any | None = None,
) -> tuple[bytes, LaunchCapability, dict[str, Any]]:
    """Prepare ADMIT, durably append+fsync+readback it, then issue capability."""
    adapter = adapter_module or _default_adapter()
    frame, event, _preview = adapter.prepare_admit(
        blob,
        block_id=block_id,
        slot_ids=slot_ids,
        admitted_at=admitted_at,
        deadline=deadline,
        b_cap=b_cap,
        reporter_factory=reporter_factory,
    )
    durable = writer.append_fsync_readback(bytes(blob), frame)
    cap = acknowledge_admit(blob, frame, durable, adapter_module=adapter)
    return durable, cap, event


def _verify_capability_against_blob(
    blob: bytes,
    cap: LaunchCapability,
    *,
    block_id: str,
    slot_id: str,
    adapter: Any,
) -> None:
    _validate_capability_integrity(cap)
    if str(block_id) != cap.block_id:
        raise LaunchCapabilityError("wrong block for launch capability")
    if len(blob) < cap.durable_prefix_len:
        raise LaunchCapabilityError("journal is shorter than acknowledged capability prefix")

    prefix = bytes(blob[: cap.durable_prefix_len])
    if _digest_bytes(prefix) != cap.durable_prefix_sha256:
        raise LaunchCapabilityError("acknowledged durable prefix changed")
    _, event = _decode_exact_admit(prefix, adapter)
    if _digest_obj(event) != cap.admit_event_digest:
        raise LaunchCapabilityError("ADMIT event digest mismatch")
    if str(event.get("event_id")) != cap.admit_event_id or str(event.get("block_id")) != cap.block_id:
        raise LaunchCapabilityError("ADMIT identity mismatch")
    if event.get("reporting_admission_digest") != cap.reporting_admission_digest:
        raise LaunchCapabilityError("reporting admission digest mismatch")
    if _digest_obj(event.get("slot_ids")) != cap.admitted_slot_set_digest:
        raise LaunchCapabilityError("admitted slot-set digest mismatch")
    if float(event.get("deadline")) != float(cap.deadline):
        raise LaunchCapabilityError("deadline mismatch")
    if str(slot_id) not in {str(x) for x in event.get("slot_ids", [])}:
        raise LaunchCapabilityError("slot is outside acknowledged admission")

    state = adapter.recover(bytes(blob))
    if state.tail_status != "clean_eof":
        raise LaunchCapabilityError("repair/quarantine torn tail before slot launch")
    if state.base.active is None or state.pending_token is None:
        raise LaunchCapabilityError("launch capability is stale: no active durable admission")
    if state.base.active.block_id != cap.block_id:
        raise LaunchCapabilityError("launch capability is stale: another block is active")
    if float(state.base.active.deadline) != float(cap.deadline):
        raise LaunchCapabilityError("active deadline differs from capability")
    if _digest_obj(list(state.base.active.slot_ids)) != cap.admitted_slot_set_digest:
        raise LaunchCapabilityError("active slot plan differs from capability")


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
    """The capability-gated score-bearing SLOT preparation entry point."""
    adapter = adapter_module or _default_adapter()
    _verify_capability_against_blob(
        bytes(blob), capability, block_id=block_id, slot_id=slot_id, adapter=adapter
    )
    return adapter.prepare_slot(
        blob,
        block_id=block_id,
        slot_id=slot_id,
        score=score,
        observed_at=observed_at,
        reporter_factory=reporter_factory,
    )


__all__ = [
    "ADAPTER_FILENAME", "ADAPTER_BLOB", "SCHEMA_VERSION",
    "LaunchCapabilityError", "DurableAppendWriter", "LaunchCapability",
    "acknowledge_admit", "admit_and_issue_capability", "prepare_slot_authorized",
]
