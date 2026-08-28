#!/usr/bin/env python3
"""Authorization revision / effect-lease classifier.

Phase-1 clean open-source artifact. This is a fail-closed evidence classifier,
not an authorization engine. It separates four claims that are easy to conflate:

1. an exact authorization decision existed,
2. that decision is bound to an explicit authorization-data revision,
3. the revision can fence later reads against stale authorization state,
4. a later external side effect is actually leased/atomic with that decision.

Current public-source anchor:
- SpiceDB/Authzed API main d5fc38fe34ec0a74f782e4328d978a3cbac633b4
  CheckPermissionResponse.checked_at is a ZedToken; Consistency supports
  at_least_as_fresh and at_exact_snapshot; relationship writes return written_at.
- OpenFGA API main 6981fff8d33bee21dd9a2001608e6d6c5f553977
  Check exposes allowed plus optional HIGHER_CONSISTENCY and model pinning, but
  the documented Check response does not expose a tuple-state revision token.
- Kubernetes SSAR (from the preceding role-local checkpoint) is an exact
  observation-time authorization decision but has no decision revision/lease.

The classifier deliberately refuses to infer an effect lease merely from a
revision-bearing authorization decision.
"""
from __future__ import annotations

import json
import sys


def classify(e: dict) -> dict:
    if e.get("authoritative_exact_operation_check") is not True:
        return {
            "decision_state": "UNPROVED",
            "revision_state": "NONE",
            "effect_state": "UNPROVED",
            "resume_rule": "FAIL_CLOSED",
        }

    if e.get("allowed") is not True:
        return {
            "decision_state": "DENIED_OR_NO_PERMISSION",
            "revision_state": "BOUND" if e.get("decision_revision_token") else "NONE",
            "effect_state": "BLOCKED",
            "resume_rule": "DO_NOT_MUTATE",
        }

    if e.get("decision_revision_token"):
        if e.get("exact_snapshot_replay"):
            revision_state = "EXACT_REPLAYABLE"
        elif e.get("minimum_freshness_fence"):
            revision_state = "MIN_FRESHNESS_ONLY"
        else:
            revision_state = "BOUND_OPAQUE"
    else:
        revision_state = "NONE"

    # Only a gate enforced by the effect system at the same decision revision
    # (or an equivalent atomic transaction) can rise to effect-lease evidence.
    if (
        e.get("same_effect_system_enforces_decision_revision") is True
        and e.get("effect_atomic_with_authorization") is True
    ):
        effect_state = "EFFECT_LEASE_OR_ATOMIC_GATE"
        resume_rule = "REVALIDATE_GATE_IDENTITY_THEN_EFFECT"
    elif e.get("pending_external_mutation") is True:
        effect_state = "NOT_LEASED"
        resume_rule = "RECHECK_CURRENT_AUTH_AT_MUTATION_BOUNDARY"
    elif e.get("minimum_freshness_fence") is True:
        effect_state = "READ_FENCE_ONLY"
        resume_rule = "USE_REVISION_FOR_CAUSAL_READS_ONLY"
    else:
        effect_state = "OBSERVATION_ONLY"
        resume_rule = "OBSERVATION_ONLY"

    return {
        "decision_state": "ALLOWED_AT_CHECK",
        "revision_state": revision_state,
        "effect_state": effect_state,
        "resume_rule": resume_rule,
    }


def self_test() -> dict:
    fixtures = {
        "kubernetes_ssar_allowed": {
            "authoritative_exact_operation_check": True,
            "allowed": True,
            "decision_revision_token": False,
            "pending_external_mutation": True,
        },
        "spicedb_check_allowed_pending_external_write": {
            "authoritative_exact_operation_check": True,
            "allowed": True,
            "decision_revision_token": True,
            "exact_snapshot_replay": True,
            "minimum_freshness_fence": True,
            "pending_external_mutation": True,
            "same_effect_system_enforces_decision_revision": False,
            "effect_atomic_with_authorization": False,
        },
        "spicedb_versioned_content_read": {
            "authoritative_exact_operation_check": True,
            "allowed": True,
            "decision_revision_token": True,
            "exact_snapshot_replay": True,
            "minimum_freshness_fence": True,
            "pending_external_mutation": False,
        },
        "spicedb_denied": {
            "authoritative_exact_operation_check": True,
            "allowed": False,
            "decision_revision_token": True,
            "exact_snapshot_replay": True,
        },
        "role_metadata_only": {
            "authoritative_exact_operation_check": False,
            "allowed": True,
        },
        "hypothetical_atomic_revision_gate": {
            "authoritative_exact_operation_check": True,
            "allowed": True,
            "decision_revision_token": True,
            "exact_snapshot_replay": True,
            "same_effect_system_enforces_decision_revision": True,
            "effect_atomic_with_authorization": True,
            "pending_external_mutation": True,
        },
    }
    got = {name: classify(evidence) for name, evidence in fixtures.items()}

    assert got["kubernetes_ssar_allowed"] == {
        "decision_state": "ALLOWED_AT_CHECK",
        "revision_state": "NONE",
        "effect_state": "NOT_LEASED",
        "resume_rule": "RECHECK_CURRENT_AUTH_AT_MUTATION_BOUNDARY",
    }
    assert got["spicedb_check_allowed_pending_external_write"] == {
        "decision_state": "ALLOWED_AT_CHECK",
        "revision_state": "EXACT_REPLAYABLE",
        "effect_state": "NOT_LEASED",
        "resume_rule": "RECHECK_CURRENT_AUTH_AT_MUTATION_BOUNDARY",
    }
    assert got["spicedb_versioned_content_read"]["effect_state"] == "READ_FENCE_ONLY"
    assert got["spicedb_denied"]["effect_state"] == "BLOCKED"
    assert got["role_metadata_only"]["decision_state"] == "UNPROVED"
    assert got["hypothetical_atomic_revision_gate"]["effect_state"] == "EFFECT_LEASE_OR_ATOMIC_GATE"
    return got


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        print(json.dumps(self_test(), indent=2, sort_keys=True))
    else:
        print(json.dumps(classify(json.load(sys.stdin)), indent=2, sort_keys=True))
