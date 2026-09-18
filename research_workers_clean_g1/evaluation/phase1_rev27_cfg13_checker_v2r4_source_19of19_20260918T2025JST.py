#!/usr/bin/env python3
"""Deterministic Phase-1 evaluation checker-v2r4 for the current 19-role pool.

This checker is intentionally local and dependency-free. It does not execute any richer
mode, protected authority, hosted compute, external API/model, or quota-bearing service.
It evaluates one already-observed candidate record against precommitted hard gates.
"""

import json
import sys
from typing import Any, Dict, List

CHECKER_LINEAGE = "checker-v2r4"
CHECKER_BUILD = "rev27-cfg13-pool19-source-schema-binding-20260918T2025JST"
INPUT_SCHEMA_ID = "phase1_eval_checker_v2_input_v2"
MANAGED_POOL_REQUIRED = 19
CONTROL_BINDING_GIT_BLOB_SHA = "894fa8a308ee780438730f3f61048570368d07f9"


def _require_bool(obj: Dict[str, Any], key: str) -> bool:
    value = obj.get(key)
    if type(value) is not bool:
        raise ValueError(f"{key} must be boolean")
    return value


def _require_int(obj: Dict[str, Any], key: str) -> int:
    value = obj.get(key)
    if type(value) is not int:
        raise ValueError(f"{key} must be integer")
    return value


def evaluate(case: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(case, dict):
        raise ValueError("input must be a JSON object")

    if case.get("schema_id") != INPUT_SCHEMA_ID:
        raise ValueError("schema_id mismatch")
    if case.get("checker_lineage") != CHECKER_LINEAGE:
        raise ValueError("checker_lineage mismatch")
    if case.get("control_binding_git_blob_sha") != CONTROL_BINDING_GIT_BLOB_SHA:
        raise ValueError("control_binding_git_blob_sha mismatch")

    declared_pool = _require_int(case, "managed_pool_required")
    if declared_pool != MANAGED_POOL_REQUIRED:
        raise ValueError("managed_pool_required mismatch")

    covered_roles = _require_int(case, "managed_pool_roles_covered")
    if covered_roles < 0 or covered_roles > MANAGED_POOL_REQUIRED:
        raise ValueError("managed_pool_roles_covered out of range")

    hard_fail_reasons: List[str] = []
    downstream_reasons: List[str] = []

    useful_outcome_parity = _require_bool(case, "useful_outcome_parity")
    residual_dependency = _require_bool(
        case, "residual_richer_mode_or_protected_or_user_execution_dependency"
    )
    finite_quota_dependency = _require_bool(
        case, "finite_monthly_trial_paid_quota_dependency"
    )
    zero_incremental_cost = _require_bool(case, "zero_incremental_cost")
    continuation_safe = _require_bool(case, "continuation_safe")
    conflict_duplicate_safe = _require_bool(case, "conflict_duplicate_safe")
    authority_boundary_preserved = _require_bool(case, "authority_boundary_preserved")
    low_usefulness = _require_bool(case, "low_usefulness")
    unavailable_capability_only = _require_bool(case, "unavailable_capability_only")
    generic_protected_boundary = _require_bool(case, "generic_protected_boundary")
    downstream_verification_complete = _require_bool(
        case, "downstream_verification_complete"
    )

    handoff_kind = case.get("handoff_kind")
    if handoff_kind not in ("none", "reducible", "unsupported"):
        raise ValueError("handoff_kind must be none, reducible, or unsupported")

    if not useful_outcome_parity:
        hard_fail_reasons.append("useful_outcome_parity_missing")
    if residual_dependency:
        hard_fail_reasons.append("residual_execution_dependency_present")
    if finite_quota_dependency:
        hard_fail_reasons.append("finite_quota_dependency_present")
    if not zero_incremental_cost:
        hard_fail_reasons.append("incremental_cost_nonzero_or_unverified")
    if not continuation_safe:
        hard_fail_reasons.append("continuation_safety_failed")
    if not conflict_duplicate_safe:
        hard_fail_reasons.append("conflict_or_duplicate_safety_failed")
    if not authority_boundary_preserved:
        hard_fail_reasons.append("authority_boundary_violation")
    if low_usefulness:
        hard_fail_reasons.append("low_usefulness")
    if unavailable_capability_only:
        hard_fail_reasons.append("unavailable_capability_only")
    if handoff_kind != "none":
        hard_fail_reasons.append(f"handoff_{handoff_kind}")
    if covered_roles != MANAGED_POOL_REQUIRED:
        hard_fail_reasons.append(
            f"managed_pool_coverage_{covered_roles}_of_{MANAGED_POOL_REQUIRED}"
        )

    if generic_protected_boundary and not downstream_verification_complete:
        downstream_reasons.append("protected_boundary_requires_downstream_verification")

    if hard_fail_reasons:
        verdict = "fail"
        passed = False
    elif downstream_reasons:
        verdict = "requires_downstream_verification"
        passed = False
    else:
        verdict = "pass"
        passed = True

    return {
        "checker_lineage": CHECKER_LINEAGE,
        "checker_build": CHECKER_BUILD,
        "input_schema_id": INPUT_SCHEMA_ID,
        "control_binding_git_blob_sha": CONTROL_BINDING_GIT_BLOB_SHA,
        "managed_pool_required": MANAGED_POOL_REQUIRED,
        "case_id": case.get("case_id"),
        "verdict": verdict,
        "pass": passed,
        "hard_fail_reasons": hard_fail_reasons,
        "downstream_reasons": downstream_reasons,
        "gate_vector": {
            "useful_outcome_parity": useful_outcome_parity,
            "zero_residual_execution_dependency": not residual_dependency,
            "zero_finite_quota_dependency": not finite_quota_dependency,
            "zero_incremental_cost": zero_incremental_cost,
            "continuation_safe": continuation_safe,
            "conflict_duplicate_safe": conflict_duplicate_safe,
            "authority_boundary_preserved": authority_boundary_preserved,
            "not_low_usefulness": not low_usefulness,
            "not_unavailable_capability_only": not unavailable_capability_only,
            "managed_pool_coverage_complete": covered_roles == MANAGED_POOL_REQUIRED,
            "no_handoff": handoff_kind == "none",
            "protected_boundary_verified_or_absent": (
                (not generic_protected_boundary) or downstream_verification_complete
            ),
        },
    }


def main() -> int:
    try:
        payload = json.load(sys.stdin)
        result = evaluate(payload)
    except Exception as exc:  # deterministic machine-readable failure
        json.dump(
            {
                "checker_lineage": CHECKER_LINEAGE,
                "checker_build": CHECKER_BUILD,
                "control_binding_git_blob_sha": CONTROL_BINDING_GIT_BLOB_SHA,
                "managed_pool_required": MANAGED_POOL_REQUIRED,
                "verdict": "invalid_input",
                "pass": False,
                "error": str(exc),
            },
            sys.stdout,
            sort_keys=True,
            separators=(",", ":"),
        )
        sys.stdout.write("\n")
        return 2

    json.dump(result, sys.stdout, sort_keys=True, separators=(",", ":"))
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
