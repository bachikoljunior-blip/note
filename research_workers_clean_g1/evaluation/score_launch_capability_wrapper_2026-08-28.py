"""Capability-gated score launch and result binding for evaluation slots.

The wrapper moves launch-capability validation in front of score generation.
A score-producing callable receives a deterministic attempt_id bound to the
acknowledged ADMIT capability, block/slot identity, and a caller-supplied
request_binding. The returned ScoreResult is integrity-bound to that same
attempt and can be converted into a SLOT frame only through the capability gate.

This is a structural non-adversarial control. Python cannot make the score
secret from a malicious caller, and historical lower-level modules remain
importable for reproducibility. An active runtime must route score launches
through this wrapper and require scorers to treat attempt_id as their immutable
sampling key when stochastic replay matters.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
import json
import math
from pathlib import Path
import sys
import time
from typing import Any, Callable

GATE_FILENAME = "durable_launch_capability_gate_2026-08-28.py"
GATE_BLOB = "e06dc0550f65182d31b96e6b841d680b487f3b41"
SCHEMA_VERSION = 1


def _canon(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _digest(obj: Any) -> str:
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
    return _load_sibling(GATE_FILENAME, "_evaluation_score_launch_gate")


class ScoreLaunchError(RuntimeError):
    pass


@dataclass(frozen=True)
class ScoreResult:
    schema_version: int
    block_id: str
    slot_id: str
    capability_digest: str
    request_binding_digest: str
    attempt_id: str
    score: float
    observed_at: float
    result_digest: str

    def payload(self) -> dict[str, Any]:
        d = asdict(self)
        d.pop("result_digest", None)
        return d


def _attempt_id(capability_digest: str, block_id: str, slot_id: str, request_binding_digest: str) -> str:
    return _digest({
        "schema_version": SCHEMA_VERSION,
        "capability_digest": capability_digest,
        "block_id": str(block_id),
        "slot_id": str(slot_id),
        "request_binding_digest": request_binding_digest,
    })


def _validate_result(result: ScoreResult) -> None:
    if int(result.schema_version) != SCHEMA_VERSION:
        raise ScoreLaunchError("unsupported result schema")
    if result.result_digest != _digest(result.payload()):
        raise ScoreLaunchError("score result digest mismatch")
    if not math.isfinite(float(result.score)) or not 0.0 <= float(result.score) <= 1.0:
        raise ScoreLaunchError("score lies outside [0,1]")
    if not math.isfinite(float(result.observed_at)):
        raise ScoreLaunchError("non-finite observed_at")


def launch_score(
    blob: bytes,
    capability: Any,
    *,
    block_id: str,
    slot_id: str,
    request_binding: Any,
    scorer: Callable[[str], float],
    clock: Callable[[], float] = time.time,
    gate_module: Any | None = None,
    adapter_module: Any | None = None,
) -> ScoreResult:
    """Validate capability before invoking scorer; invalid launch calls zero scorer work."""
    gate = gate_module or _default_gate()
    adapter = adapter_module or gate._default_adapter()
    # Intentional use of the bound gate's internal verifier so score generation
    # occurs strictly after the same durable checks used by SLOT persistence.
    gate._verify_capability_against_blob(
        bytes(blob), capability, block_id=str(block_id), slot_id=str(slot_id),
        adapter=adapter,
    )

    req_digest = _digest(request_binding)
    aid = _attempt_id(capability.capability_digest, str(block_id), str(slot_id), req_digest)
    score = float(scorer(aid))
    if not math.isfinite(score) or not 0.0 <= score <= 1.0:
        raise ScoreLaunchError("scorer returned value outside [0,1]")
    observed_at = float(clock())
    if not math.isfinite(observed_at):
        raise ScoreLaunchError("clock returned non-finite time")
    payload = {
        "schema_version": SCHEMA_VERSION,
        "block_id": str(block_id),
        "slot_id": str(slot_id),
        "capability_digest": capability.capability_digest,
        "request_binding_digest": req_digest,
        "attempt_id": aid,
        "score": score,
        "observed_at": observed_at,
    }
    return ScoreResult(**payload, result_digest=_digest(payload))


def prepare_result_slot(
    blob: bytes,
    capability: Any,
    result: ScoreResult,
    *,
    request_binding: Any,
    gate_module: Any | None = None,
    adapter_module: Any | None = None,
    reporter_factory: Any | None = None,
) -> tuple[bytes, dict[str, Any]]:
    """Persist only a result bound to this exact capability/request/attempt."""
    gate = gate_module or _default_gate()
    adapter = adapter_module or gate._default_adapter()
    _validate_result(result)
    if result.capability_digest != capability.capability_digest:
        raise ScoreLaunchError("result belongs to another launch capability")
    req_digest = _digest(request_binding)
    if result.request_binding_digest != req_digest:
        raise ScoreLaunchError("request binding digest mismatch")
    expected_attempt = _attempt_id(
        capability.capability_digest, result.block_id, result.slot_id, req_digest
    )
    if result.attempt_id != expected_attempt:
        raise ScoreLaunchError("attempt identity mismatch")

    return gate.prepare_slot_authorized(
        blob,
        capability,
        block_id=result.block_id,
        slot_id=result.slot_id,
        score=result.score,
        observed_at=result.observed_at,
        adapter_module=adapter,
        reporter_factory=reporter_factory,
    )


__all__ = [
    "GATE_FILENAME", "GATE_BLOB", "SCHEMA_VERSION",
    "ScoreLaunchError", "ScoreResult", "launch_score", "prepare_result_slot",
]
