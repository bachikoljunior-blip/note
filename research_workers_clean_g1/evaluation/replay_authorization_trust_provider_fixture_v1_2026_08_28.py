"""Pinned trust-provider fixture for replay bootstrap validation.

This file is deliberately parameterless: callers cannot supply a replacement
certificate registry, runtime snapshot, or invalidation set at operation time.
It is a validation fixture for the bootstrap authority boundary, not a claim
that a static provider is sufficient for a live LLM runtime.
"""
from __future__ import annotations
from copy import deepcopy

SCHEMA_VERSION=1
REGISTRY_GENERATION="evaluation-toy-hash-score-2026-08-28-g1"
CERTIFICATE_ID="toy_hash_score_exact_v1"
CERTIFICATE_DIGEST="378b69c152e8d36dee8928fd820a0901dd561be7f00b6acaf3980871243800ab"
RUNTIME_SNAPSHOT={"attempt_id_version":"attempt-v1","decoder_config_digest":"64c93a49cdd811927701b5f07c69cbe08e165b62199f1ddcce19d1b65a03ef10","protected_statistic":"score","runtime_fingerprint_digest":"21015cd51044cdddf8c2f6635ad92430e4bb1e80db447d85096de49813d962a9","scorer_config_digest":"25f010a38b86a6d7335ea9d00df02351bf791740ebd4bfd3387950e3e5b03c87"}
INVALIDATION_CONDITIONS=()

def trusted_registry_payload():
    return {
        "generation":REGISTRY_GENERATION,
        "certificates":{CERTIFICATE_ID:CERTIFICATE_DIGEST},
        "revoked_certificate_ids":[],
    }

def runtime_snapshot_payload():
    return deepcopy(RUNTIME_SNAPSHOT)

def triggered_invalidation_conditions():
    return tuple(INVALIDATION_CONDITIONS)

__all__=[
    "SCHEMA_VERSION","REGISTRY_GENERATION","CERTIFICATE_ID","CERTIFICATE_DIGEST",
    "RUNTIME_SNAPSHOT","INVALIDATION_CONDITIONS","trusted_registry_payload",
    "runtime_snapshot_payload","triggered_invalidation_conditions",
]
