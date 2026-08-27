"""Forward-only reservation-runtime provenance contract for evaluation blocks.

The scientific acceptance predicate must be fixed before score generation. This
helper therefore binds the already-frozen compliance runtime dependency set into
new ADMIT events. Historical ADMITs without this field are never reinterpreted.
"""
from __future__ import annotations
from hashlib import sha256
import json
from typing import Any

SCHEMA_VERSION = 1
CONTRACT_FIELD = "reserved_score_runtime_contract"
BINDING_FIELD = "compliance_reserved_runtime_binding"


def _canon(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def digest_obj(obj: Any) -> str:
    return sha256(_canon(obj)).hexdigest()


def contract_for_binding(binding: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "enforce_for_new_reservations": True,
        "binding_digest": digest_obj(binding),
        "scope": "reservation authorization provenance fixed pre-score; historical ADMITs without this contract are not reinterpreted",
    }


def bind_admit(event: dict[str, Any], binding: dict[str, Any]) -> dict[str, Any]:
    out = dict(event)
    if CONTRACT_FIELD in out:
        raise ValueError("ADMIT already contains reserved-score runtime contract")
    out[CONTRACT_FIELD] = contract_for_binding(binding)
    return out


def reservation_binding_status(
    admit_event: dict[str, Any],
    reserve_event: dict[str, Any] | None,
    expected_binding: dict[str, Any],
) -> tuple[bool, str, bool]:
    """Return (enforced, status, scientific_fail_closed).

    Missing contract means historical behavior and is diagnostic-only. Once a
    new ADMIT explicitly opts into the contract, any missing/mismatched RESERVE
    provenance is fail-closed because it violates a pre-score authorization
    predicate, not because of a post-hoc provenance preference.
    """
    c = admit_event.get(CONTRACT_FIELD)
    if not isinstance(c, dict):
        return False, "historical_no_runtime_contract", False
    expected_digest = digest_obj(expected_binding)
    if (
        c.get("schema_version") != SCHEMA_VERSION
        or c.get("enforce_for_new_reservations") is not True
        or c.get("binding_digest") != expected_digest
    ):
        return True, "invalid_or_unrecognized_admit_runtime_contract", True
    if reserve_event is None:
        return True, "missing_reserve_event", True
    observed = reserve_event.get(BINDING_FIELD)
    if not isinstance(observed, dict):
        return True, "reserve_runtime_binding_missing", True
    if observed != expected_binding or digest_obj(observed) != expected_digest:
        return True, "reserve_runtime_binding_mismatch", True
    return True, "compliant", False


__all__ = [
    "SCHEMA_VERSION", "CONTRACT_FIELD", "BINDING_FIELD", "digest_obj",
    "contract_for_binding", "bind_admit", "reservation_binding_status",
]
