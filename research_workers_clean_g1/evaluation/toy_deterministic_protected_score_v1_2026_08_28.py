"""Deterministic toy protected-statistic scorer for replay-bootstrap validation.

This is a research fixture, not an LLM scorer. The protected statistic is a
content-addressed score digest that is a pure function of attempt_id.
"""
from __future__ import annotations
from hashlib import sha256

SCHEMA_VERSION = 1
DOMAIN = b"evaluation-toy-protected-score-v1\0"

def protected_value_digest(attempt_id: str) -> str:
    if not isinstance(attempt_id, str) or not attempt_id:
        raise ValueError("attempt_id must be nonempty string")
    return sha256(DOMAIN + attempt_id.encode("utf-8")).hexdigest()

def score(attempt_id: str) -> float:
    d = protected_value_digest(attempt_id)
    return int(d[:13], 16) / float(16**13 - 1)

__all__ = ["SCHEMA_VERSION", "DOMAIN", "protected_value_digest", "score"]
