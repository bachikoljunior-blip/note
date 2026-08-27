"""Complete forward-contract runtime for reservation authorization provenance.

New ADMITs bind the frozen reservation-runtime dependency set before score
generation. Reservation/score mechanics delegate to the frozen compliance
runtime, while CLOSE/replay defaults to the provenance-aware superseding layer.
Historical blocks remain replayable under their historical predicate.
"""
from __future__ import annotations
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import sys
from typing import Any

BASE_FILENAME = "reserved_score_runtime_compliance_2026-08-28.py"
BASE_BLOB = "3e58813f34079e7f92eb0728bd7f9c27810d5418"
CONTRACT_FILENAME = "reservation_runtime_provenance_contract_2026-08-28.py"
CONTRACT_BLOB = "f6a4d996381bd100038d6ccfcf1b7c5f3f28e905"
CLOSE_FILENAME = "reservation_compliance_close_replay_runtime_provenance_2026-08-28.py"
CLOSE_BLOB = "c9982f2ef14cff5b1f59b314e95250745706c5e4"
SCHEMA_VERSION = 2


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
    return _load(BASE_FILENAME, "_evaluation_runtime_provenance_base")


def _contract() -> Any:
    return _load(CONTRACT_FILENAME, "_evaluation_runtime_provenance_contract")


def _default_close() -> Any:
    return _load(CLOSE_FILENAME, "_evaluation_runtime_provenance_close")


def admit_and_issue_capability(writer: Any, main_blob: bytes, ledger_blob: bytes, **kwargs: Any):
    base = kwargs.pop("base_runtime_module", None) or _base()
    contract = kwargs.pop("contract_module", None) or _contract()
    gate = kwargs.pop("gate_module", None) or base._default_gate()
    frame, event, _preview = gate.prepare_admit_compliance(
        bytes(main_blob), bytes(ledger_blob), **kwargs
    )
    event = contract.bind_admit(event, base._binding())
    atomic = gate._default_adapter()._default_atomic()
    frame = atomic.encode_frame(event)
    durable = writer.append_fsync_readback(bytes(main_blob), frame)
    ack_kwargs = {
        k: v for k, v in kwargs.items()
        if k in {"adapter_module", "compliance_module", "attempt_module", "reporter_factory"}
    }
    cap = gate.acknowledge_admit(
        bytes(main_blob), frame, durable, ledger_blob=bytes(ledger_blob), **ack_kwargs
    )
    return durable, cap, event


def prepare_reservation(*args: Any, **kwargs: Any):
    return (kwargs.pop("base_runtime_module", None) or _base()).prepare_reservation(*args, **kwargs)


def reserve_and_issue(*args: Any, **kwargs: Any):
    return (kwargs.pop("base_runtime_module", None) or _base()).reserve_and_issue(*args, **kwargs)


def launch_reserved_score(*args: Any, **kwargs: Any):
    return (kwargs.pop("base_runtime_module", None) or _base()).launch_reserved_score(*args, **kwargs)


def prepare_bound_slot(*args: Any, **kwargs: Any):
    return (kwargs.pop("base_runtime_module", None) or _base()).prepare_bound_slot(*args, **kwargs)


def prepare_commit(*args: Any, **kwargs: Any):
    return (kwargs.pop("base_runtime_module", None) or _base()).prepare_commit(*args, **kwargs)


def prepare_recovery_commit_from_main(*args: Any, **kwargs: Any):
    return (kwargs.pop("base_runtime_module", None) or _base()).prepare_recovery_commit_from_main(*args, **kwargs)


def prepare_close(*args: Any, **kwargs: Any):
    close_module = kwargs.pop("close_module", None) or _default_close()
    base = kwargs.pop("base_runtime_module", None) or _base()
    return base.prepare_close(*args, close_module=close_module, **kwargs)


def recover(*args: Any, **kwargs: Any):
    close_module = kwargs.pop("close_module", None) or _default_close()
    base = kwargs.pop("base_runtime_module", None) or _base()
    return base.recover(*args, close_module=close_module, **kwargs)


__all__ = [
    "BASE_FILENAME", "BASE_BLOB", "CONTRACT_FILENAME", "CONTRACT_BLOB",
    "CLOSE_FILENAME", "CLOSE_BLOB", "SCHEMA_VERSION",
    "admit_and_issue_capability", "prepare_reservation", "reserve_and_issue",
    "launch_reserved_score", "prepare_bound_slot", "prepare_commit",
    "prepare_recovery_commit_from_main", "prepare_close", "recover",
]
