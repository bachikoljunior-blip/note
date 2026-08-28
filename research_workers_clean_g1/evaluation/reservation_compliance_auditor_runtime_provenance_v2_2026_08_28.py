"""Reservation compliance auditor with versioned runtime-provenance registry.

This supersedes the single-binding runtime-provenance auditor only for callers
that explicitly select it. Scientific SLOT/COMMIT compliance remains delegated
to the frozen base auditor. Runtime provenance is resolved from the pre-score
ADMIT contract through an allowlisted contract registry:
- historical ADMIT: no runtime-provenance enforcement;
- schema-v1 ADMIT: exact frozen compliance_runtime_v1;
- schema-v2 ADMIT: exact allowlisted binding_id, including replay_authorized_v1.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path
import sys
from typing import Any

BASE_AUDITOR_FILENAME = "reservation_compliance_auditor_2026-08-28.py"
BASE_AUDITOR_BLOB = "0a845daa2675ba2c769c231769b1729f7e78f01d"
CONTRACT_FILENAME = "reservation_runtime_provenance_contract_registry_v2_2026_08_28.py"
CONTRACT_BLOB = "c4d0439dba3ddf2183835c3fbaa3b3012ec1f468"
SCHEMA_VERSION = 2

def _canon(obj: Any) -> bytes:
    return json.dumps(
        obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")

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

def _base() -> Any:
    return _load(BASE_AUDITOR_FILENAME, "_evaluation_runtime_prov_v2_base")

def _contract() -> Any:
    return _load(CONTRACT_FILENAME, "_evaluation_runtime_prov_v2_contract")

@dataclass(frozen=True)
class RuntimeSlotComplianceV2:
    slot_id: str
    base_status: str
    runtime_provenance_status: str
    runtime_binding_id: str | None
    final_status: str
    scientific_score: float
    reconcilable: bool

@dataclass(frozen=True)
class RuntimeBlockComplianceAuditV2:
    schema_version: int
    block_id: str
    planned_size: int
    b_cap: int
    exposure_weight: float
    completed_compliant: int
    fail_closed_slots: int
    block_score: float
    all_slots_compliant: bool
    recovery_commits_required: tuple[str, ...]
    slot_audits: tuple[RuntimeSlotComplianceV2, ...]
    runtime_contract_enforced: bool
    runtime_binding_id: str | None
    base_compliance_digest: str
    runtime_compliance_digest: str

    def payload(self):
        d = asdict(self)
        d.pop("runtime_compliance_digest", None)
        return d

def audit_active_block(
    main_blob: bytes,
    ledger_blob: bytes,
    *,
    block_id: str,
    base_auditor_module: Any | None = None,
    contract_module: Any | None = None,
    atomic_module: Any | None = None,
    attempt_module: Any | None = None,
) -> RuntimeBlockComplianceAuditV2:
    base = base_auditor_module or _base()
    contract = contract_module or _contract()
    atomic = atomic_module or base._default_atomic()
    attempt = attempt_module or base._default_attempt()

    old = base.audit_active_block(
        bytes(main_blob), bytes(ledger_blob), block_id=str(block_id),
        atomic_module=atomic, attempt_module=attempt,
    )

    mevents, mvalid, mtail = atomic.decode_valid_prefix(bytes(main_blob))
    if mtail != "clean_eof" or mvalid != len(main_blob):
        raise base.ReservationComplianceError("main tail not clean")
    admits = [
        e for e in mevents
        if e.get("kind") == "ADMIT" and str(e.get("block_id")) == str(block_id)
    ]
    if len(admits) != 1:
        raise base.ReservationComplianceError(
            "expected one active ADMIT for runtime provenance v2 audit"
        )
    admit = admits[0]

    levents, lvalid, ltail = attempt._decode_valid_prefix(bytes(ledger_blob))
    if ltail != "clean_eof" or lvalid != len(ledger_blob):
        raise base.ReservationComplianceError("ledger tail not clean")
    reserve_by_slot = {
        str(e.get("slot_id")): e
        for e in levents
        if e.get("kind") == "RESERVE" and str(e.get("block_id")) == str(block_id)
    }

    enforced, cstatus, _expected, admit_binding_id, cfail = (
        contract.resolve_admit_binding(admit)
    )
    slots: list[RuntimeSlotComplianceV2] = []
    scores: list[float] = []
    recovery: list[str] = []

    for a in old.slot_audits:
        _enforced, pstatus, pfail, binding_id = contract.reservation_binding_status(
            admit, reserve_by_slot.get(a.slot_id)
        )
        # Invalid contract is a block-level pre-score provenance failure; apply
        # it to every planned slot rather than letting per-slot absence mask it.
        if cfail:
            pstatus = cstatus
            pfail = True
            binding_id = admit_binding_id
        if pfail:
            score = 1.0
            recon = False
            final = f"runtime_provenance_fail:{pstatus}"
        else:
            score = float(a.scientific_score)
            recon = bool(a.reconcilable)
            final = str(a.status)
            if recon:
                recovery.append(a.slot_id)
        scores.append(score)
        slots.append(RuntimeSlotComplianceV2(
            slot_id=a.slot_id,
            base_status=str(a.status),
            runtime_provenance_status=pstatus,
            runtime_binding_id=binding_id,
            final_status=final,
            scientific_score=score,
            reconcilable=recon,
        ))

    if not scores:
        raise base.ReservationComplianceError("active block has no planned slots")

    completed = sum(s.final_status == "compliant" for s in slots)
    payload = {
        "schema_version": SCHEMA_VERSION,
        "block_id": str(block_id),
        "planned_size": old.planned_size,
        "b_cap": old.b_cap,
        "exposure_weight": old.exposure_weight,
        "completed_compliant": completed,
        "fail_closed_slots": old.planned_size - completed,
        "block_score": sum(scores) / len(scores),
        "all_slots_compliant": completed == old.planned_size,
        "recovery_commits_required": tuple(recovery),
        "slot_audits": tuple(asdict(s) for s in slots),
        "runtime_contract_enforced": enforced,
        "runtime_binding_id": admit_binding_id,
        "base_compliance_digest": old.compliance_digest,
    }
    return RuntimeBlockComplianceAuditV2(
        **{k: v for k, v in payload.items() if k != "slot_audits"},
        slot_audits=tuple(slots),
        runtime_compliance_digest=_digest(payload),
    )

__all__ = [
    "BASE_AUDITOR_FILENAME", "BASE_AUDITOR_BLOB",
    "CONTRACT_FILENAME", "CONTRACT_BLOB", "SCHEMA_VERSION",
    "RuntimeSlotComplianceV2", "RuntimeBlockComplianceAuditV2",
    "audit_active_block",
]
