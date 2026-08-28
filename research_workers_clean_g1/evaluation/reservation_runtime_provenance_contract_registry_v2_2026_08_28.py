"""Forward-only registry for reservation-runtime provenance contract versions.

This module does not mutate historical contracts. It recognizes:
- no contract: historical behavior, diagnostic only;
- schema v1: exactly the frozen current compliance runtime binding;
- schema v2: an allowlisted binding_id whose exact binding/digest is frozen here.

Arbitrary caller-supplied bindings are never accepted. New replay-authorized
blocks use schema v2 and bind the replay authorization facade before scoring.
"""
from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
import json
from types import MappingProxyType
from typing import Any

SCHEMA_VERSION = 2
CONTRACT_FIELD = "reserved_score_runtime_contract"
BINDING_FIELD = "compliance_reserved_runtime_binding"

CURRENT_V1_BINDING_ID = "compliance_runtime_v1"
REPLAY_AUTHORIZED_V1_BINDING_ID = "replay_authorized_v1"

_CURRENT_V1_BINDING_RAW = {
    "schema_version": 1,
    "gate": {
        "filename": "durable_launch_capability_gate_compliance_2026-08-28.py",
        "blob": "a2aa84a3ef98d1647430a384a514d7cbc18303c3",
    },
    "attempt": {
        "filename": "durable_attempt_reservation_ledger_2026-08-28.py",
        "blob": "f51cc37e5897d8dc0f395da95c1f6dd1c12da791",
    },
    "score": {
        "filename": "score_launch_capability_wrapper_2026-08-28.py",
        "blob": "e610805ab1f495198c1b44ab82f02086233f1eda",
    },
    "pipeline": {
        "filename": "reserved_score_pipeline_2026-08-28.py",
        "blob": "811bee4ddac614cd1ebd517a465cfb978006e91a",
    },
    "compliance_close": {
        "filename": "reservation_compliance_close_replay_2026-08-28.py",
        "blob": "ac69f485383118192b533e258bb6033b454ca9b3",
    },
}

_REPLAY_AUTHORIZED_V1_BINDING_RAW = {
    "schema_version": 2,
    "base_compliance_runtime": _CURRENT_V1_BINDING_RAW,
    "deterministic_replay_authorization": {
        "filename": "deterministic_replay_authorization_facade_v1_2026_08_28.py",
        "blob": "f21613ebb6db487d70983ad46caf063ac86c804b",
    },
}

def _canon(obj: Any) -> bytes:
    return json.dumps(
        obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")

def digest_obj(obj: Any) -> str:
    return sha256(_canon(obj)).hexdigest()

# Store canonical JSON strings, not mutable nested dictionaries, so imported
# callers cannot mutate the registry authority in-process by modifying a shared
# dict object.
_BINDING_JSON = MappingProxyType({
    CURRENT_V1_BINDING_ID: _canon(_CURRENT_V1_BINDING_RAW).decode("utf-8"),
    REPLAY_AUTHORIZED_V1_BINDING_ID: _canon(_REPLAY_AUTHORIZED_V1_BINDING_RAW).decode("utf-8"),
})

class RuntimeContractRegistryError(RuntimeError):
    pass

def binding_registry_summary() -> dict[str, Any]:
    return {
        key: {"digest": digest_obj(json.loads(encoded)), "binding": json.loads(encoded)}
        for key, encoded in _BINDING_JSON.items()
    }

def binding_for_id(binding_id: str) -> dict[str, Any]:
    try:
        return json.loads(_BINDING_JSON[str(binding_id)])
    except KeyError as exc:
        raise RuntimeContractRegistryError(
            f"unknown reservation runtime binding_id {binding_id!r}"
        ) from exc

def contract_v2_for_binding_id(binding_id: str) -> dict[str, Any]:
    binding = binding_for_id(binding_id)
    return {
        "schema_version": SCHEMA_VERSION,
        "enforce_for_new_reservations": True,
        "binding_id": str(binding_id),
        "binding_digest": digest_obj(binding),
        "scope": (
            "reservation authorization provenance fixed pre-score; "
            "historical and schema-v1 ADMITs are not reinterpreted"
        ),
    }

def bind_admit_v2(event: dict[str, Any], binding_id: str) -> dict[str, Any]:
    out = dict(event)
    if CONTRACT_FIELD in out:
        raise RuntimeContractRegistryError(
            "ADMIT already contains reserved-score runtime contract"
        )
    out[CONTRACT_FIELD] = contract_v2_for_binding_id(binding_id)
    return out

def resolve_admit_binding(
    admit_event: dict[str, Any],
) -> tuple[bool, str, dict[str, Any] | None, str | None, bool]:
    """Return (enforced, status, expected_binding, binding_id, fail_closed)."""
    contract = admit_event.get(CONTRACT_FIELD)
    if not isinstance(contract, dict):
        return False, "historical_no_runtime_contract", None, None, False

    schema = contract.get("schema_version")
    if schema == 1:
        # Preserve the existing v1 contract exactly: it did not carry binding_id.
        expected = binding_for_id(CURRENT_V1_BINDING_ID)
        if (
            contract.get("enforce_for_new_reservations") is not True
            or contract.get("binding_digest") != digest_obj(expected)
        ):
            return True, "invalid_schema_v1_runtime_contract", None, None, True
        return True, "current_schema_v1", expected, CURRENT_V1_BINDING_ID, False

    if schema == SCHEMA_VERSION:
        binding_id = contract.get("binding_id")
        if not isinstance(binding_id, str) or binding_id not in _BINDING_JSON:
            return True, "unknown_schema_v2_binding_id", None, None, True
        expected = binding_for_id(binding_id)
        if (
            contract.get("enforce_for_new_reservations") is not True
            or contract.get("binding_digest") != digest_obj(expected)
        ):
            return True, "invalid_schema_v2_runtime_contract", None, binding_id, True
        return True, "recognized_schema_v2", expected, binding_id, False

    return True, "unsupported_runtime_contract_schema", None, None, True

def reservation_binding_status(
    admit_event: dict[str, Any],
    reserve_event: dict[str, Any] | None,
) -> tuple[bool, str, bool, str | None]:
    """Return (enforced, status, scientific_fail_closed, binding_id)."""
    enforced, cstatus, expected, binding_id, cfail = resolve_admit_binding(admit_event)
    if not enforced:
        return False, cstatus, False, None
    if cfail or expected is None:
        return True, cstatus, True, binding_id
    if reserve_event is None:
        return True, "missing_reserve_event", True, binding_id
    observed = reserve_event.get(BINDING_FIELD)
    if not isinstance(observed, dict):
        return True, "reserve_runtime_binding_missing", True, binding_id
    if observed != expected or digest_obj(observed) != digest_obj(expected):
        return True, "reserve_runtime_binding_mismatch", True, binding_id
    return True, "compliant", False, binding_id

__all__ = [
    "SCHEMA_VERSION", "CONTRACT_FIELD", "BINDING_FIELD",
    "CURRENT_V1_BINDING_ID", "REPLAY_AUTHORIZED_V1_BINDING_ID",
    "RuntimeContractRegistryError", "digest_obj", "binding_registry_summary",
    "binding_for_id", "contract_v2_for_binding_id", "bind_admit_v2",
    "resolve_admit_binding", "reservation_binding_status",
]
