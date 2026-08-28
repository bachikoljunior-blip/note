"""Pinned trust-provider fixture for replay bootstrap v2 validation.

Parameterless fixture: certificate registry, runtime snapshot, and invalidation
state are fixed by file bytes. This validates the bootstrap authority boundary;
it is not a production live-runtime attestor.
"""
from __future__ import annotations
from copy import deepcopy

SCHEMA_VERSION=2
REGISTRY_GENERATION="evaluation-toy-hash-score-2026-08-28-g2"
CERTIFICATE_ID="toy_hash_score_exact_v2"
CERTIFICATE_DIGEST="e251dbc677432641ddbdf7d6dd3d3cd7fefd810e786baa1e8d068157467eba14"
RUNTIME_SNAPSHOT={"attempt_id_version":"attempt-v1","decoder_config_digest":"344bd0124c1d4dc5b757060cbb1b6455932a3ea08afe015b9acd2edcfa767125","protected_statistic":"score","runtime_fingerprint_digest":"e1b56afedbc4bb74c06fbd06685b5c61459791f4354e3469b62332be6aea9153","scorer_config_digest":"9c76d9a50d2187b00d132b5491e7bd119abde18f9e6351f52ab9b869a40fb39e"}
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
