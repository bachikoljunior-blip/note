"""Audit-only snapshot for simultaneous V3 numeric reporting.

Scientific truth remains the atomic journal's immutable CLOSED rows. This module stores
no second row history: a snapshot is derived from a reconstructed reporter and is keyed
by the canonical rows_digest plus the frozen reporting contract and implementation tag.
Any consumer must rebuild from the journal and compare the key before trusting a stored
snapshot.
"""
from __future__ import annotations

from dataclasses import asdict
from hashlib import sha256
import json
from typing import Any, Iterable, Mapping


def _canon(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def build_reporting_snapshot(reporter: Any, implementation_tag: str) -> dict[str, Any]:
    snap = reporter.snapshot()
    contract = asdict(reporter.contract)
    identity = {
        "schema_version": 1,
        "rows_digest": snap["rows_digest"],
        "row_count": snap["row_count"],
        "contract": contract,
        "implementation_tag": str(implementation_tag),
    }
    snapshot_key = sha256(_canon(identity)).hexdigest()
    return {
        "schema_version": 1,
        "snapshot_key": snapshot_key,
        "identity": identity,
        "decision_contract": snap["decision_contract"],
        "marginal_numeric_bounds": snap["marginal_numeric_bounds"],
        "simultaneous_reporting_contract": snap["simultaneous_reporting_contract"],
        "tolerances": snap["tolerances"],
        "scientific_history_embedded": False,
        "recovery_rule": "rebuild reporter from canonical journal CLOSED rows and require exact snapshot_key plus numerical snapshot equality",
    }


def rebuild_snapshot_from_rows(
    reporter_cls: Any,
    stream_factory: Any,
    contract: Any,
    closed_rows: Iterable[Mapping[str, Any]],
    implementation_tag: str,
) -> dict[str, Any]:
    reporter = reporter_cls.replay(stream_factory, closed_rows, contract)
    return build_reporting_snapshot(reporter, implementation_tag)


def assert_snapshot_matches(stored: Mapping[str, Any], rebuilt: Mapping[str, Any]) -> None:
    if stored.get("snapshot_key") != rebuilt.get("snapshot_key"):
        raise AssertionError("snapshot identity mismatch: rows/contract/implementation changed")
    if _canon(stored) != _canon(rebuilt):
        raise AssertionError("snapshot payload mismatch under identical identity")
