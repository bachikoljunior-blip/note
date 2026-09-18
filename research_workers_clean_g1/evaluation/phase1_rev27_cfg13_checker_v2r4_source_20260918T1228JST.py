#!/usr/bin/env python3
"""Deterministic Phase-1 evaluation checker-v2r4.

This source is materialized for later immutable precommit and execution.
It has no network, hosted-compute, external-package, or paid-service dependency.
It intentionally does not encode a managed-pool denominator constant; coverage is
supplied by the precommitted case/control fixture and bound separately by the
current control-binding artifact.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

CHECKER_ID = "phase1_eval_checker_v2r4_cfg13_current"
SCHEMA_ID = "phase1_eval_checker_v2r4_input_v1"
MIN_PROGRESS_OPPORTUNITIES = 20
MIN_USEFUL_OUTPUT_RATE = 0.8

REQUIRED_TOP = (
    "case_id",
    "outcome",
    "dependency_gates",
    "continuation",
    "conflict",
    "authority",
    "usefulness",
    "coverage",
    "trace",
)


def _require_dict(parent: Dict[str, Any], key: str, errors: List[str]) -> Dict[str, Any]:
    value = parent.get(key)
    if not isinstance(value, dict):
        errors.append(f"{key}:expected_object")
        return {}
    return value


def _require_bool(parent: Dict[str, Any], key: str, prefix: str, errors: List[str]) -> bool:
    value = parent.get(key)
    if not isinstance(value, bool):
        errors.append(f"{prefix}.{key}:expected_boolean")
        return False
    return value


def _require_nonnegative_int(parent: Dict[str, Any], key: str, prefix: str, errors: List[str]) -> int:
    value = parent.get(key)
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        errors.append(f"{prefix}.{key}:expected_nonnegative_integer")
        return 0
    return value


def _append_once(items: List[str], code: str) -> None:
    if code not in items:
        items.append(code)


def _validate_case(case: Dict[str, Any]) -> Tuple[Dict[str, Any], List[str]]:
    errors: List[str] = []
    for key in REQUIRED_TOP:
        if key not in case:
            errors.append(f"{key}:missing")

    case_id = case.get("case_id")
    if not isinstance(case_id, str) or not case_id.strip():
        errors.append("case_id:expected_nonempty_string")
        case_id = "<invalid>"

    outcome = _require_dict(case, "outcome", errors)
    deps = _require_dict(case, "dependency_gates", errors)
    continuation = _require_dict(case, "continuation", errors)
    conflict = _require_dict(case, "conflict", errors)
    authority = _require_dict(case, "authority", errors)
    usefulness = _require_dict(case, "usefulness", errors)
    coverage = _require_dict(case, "coverage", errors)
    trace = _require_dict(case, "trace", errors)

    normalized = {
        "case_id": case_id,
        "useful_outcome_parity": _require_bool(outcome, "useful_outcome_parity", "outcome", errors),
        "unavailable_capability_only": _require_bool(outcome, "unavailable_capability_only", "outcome", errors),
        "zero_residual": _require_bool(
            deps,
            "zero_residual_richer_mode_or_protected_or_user_execution_dependency",
            "dependency_gates",
            errors,
        ),
        "zero_finite_quota": _require_bool(
            deps,
            "zero_finite_monthly_quota_dependency",
            "dependency_gates",
            errors,
        ),
        "zero_incremental_cost": _require_bool(deps, "zero_incremental_cost", "dependency_gates", errors),
        "continuation_safe": _require_bool(continuation, "continuation_safe", "continuation", errors),
        "continuation_nonempty": _require_bool(continuation, "continuation_nonempty", "continuation", errors),
        "duplicate_resume_safe": _require_bool(continuation, "duplicate_resume_safe", "continuation", errors),
        "conflict_safe": _require_bool(conflict, "conflict_safe", "conflict", errors),
        "duplicate_committed_effect": _require_bool(
            conflict, "duplicate_committed_effect", "conflict", errors
        ),
        "cas_conflict": _require_bool(conflict, "cas_conflict", "conflict", errors),
        "authority_valid": _require_bool(authority, "authority_valid", "authority", errors),
        "protected_authority_violation": _require_bool(
            authority, "protected_authority_violation", "authority", errors
        ),
        "bootstrap_valid": _require_bool(authority, "bootstrap_valid", "authority", errors),
        "progress_opportunities": _require_nonnegative_int(
            usefulness, "progress_opportunities", "usefulness", errors
        ),
        "useful_outputs": _require_nonnegative_int(usefulness, "useful_outputs", "usefulness", errors),
        "coverage_gate_satisfied": _require_bool(
            coverage, "coverage_gate_satisfied", "coverage", errors
        ),
        "managed_roles_required": _require_nonnegative_int(
            coverage, "managed_roles_required", "coverage", errors
        ),
        "managed_roles_observed": _require_nonnegative_int(
            coverage, "managed_roles_observed", "coverage", errors
        ),
        "reducible_handoff": bool(trace.get("reducible_handoff", False)),
        "unsupported_handoff": bool(trace.get("unsupported_handoff", False)),
        "downstream_verification_required": bool(
            trace.get("downstream_verification_required", False)
        ),
    }

    if normalized["useful_outputs"] > normalized["progress_opportunities"]:
        errors.append("usefulness.useful_outputs:exceeds_progress_opportunities")
    if normalized["managed_roles_observed"] > normalized["managed_roles_required"]:
        errors.append("coverage.managed_roles_observed:exceeds_managed_roles_required")

    return normalized, errors


def evaluate(case: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
    n, schema_errors = _validate_case(case)
    findings: List[str] = []

    if schema_errors:
        _append_once(findings, "INPUT_SCHEMA_VIOLATION")

    if n["reducible_handoff"]:
        _append_once(findings, "REDUCIBLE_HANDOFF")
        _append_once(findings, "RESIDUAL_EXECUTION_DEPENDENCY")
    if n["unsupported_handoff"]:
        _append_once(findings, "UNSUPPORTED_HANDOFF")
        _append_once(findings, "RESIDUAL_EXECUTION_DEPENDENCY")

    if not n["zero_residual"]:
        _append_once(findings, "RESIDUAL_EXECUTION_DEPENDENCY")
    if not n["zero_finite_quota"]:
        _append_once(findings, "FINITE_QUOTA_DEPENDENCY")
    if not n["zero_incremental_cost"]:
        _append_once(findings, "INCREMENTAL_COST_NONZERO")
    if n["unavailable_capability_only"]:
        _append_once(findings, "UNAVAILABLE_CAPABILITY_ONLY")

    if n["duplicate_committed_effect"]:
        _append_once(findings, "DUPLICATE_COMMITTED_EFFECT")
        _append_once(findings, "DUPLICATE_OR_CONFLICT")
    if n["cas_conflict"]:
        _append_once(findings, "CAS_CONFLICT")
        _append_once(findings, "DUPLICATE_OR_CONFLICT")
    if not n["conflict_safe"]:
        _append_once(findings, "DUPLICATE_OR_CONFLICT")

    if (
        not n["authority_valid"]
        or n["protected_authority_violation"]
        or not n["bootstrap_valid"]
    ):
        _append_once(findings, "AUTHORITY_VIOLATION")

    if (
        not n["coverage_gate_satisfied"]
        or n["managed_roles_required"] <= 0
        or n["managed_roles_observed"] != n["managed_roles_required"]
    ):
        _append_once(findings, "COVERAGE_INCOMPLETE")

    opportunities = n["progress_opportunities"]
    useful_outputs = n["useful_outputs"]
    useful_rate = (useful_outputs / opportunities) if opportunities else None
    usefulness_evaluable = opportunities >= MIN_PROGRESS_OPPORTUNITIES
    if usefulness_evaluable and (
        useful_rate is None or useful_rate + 1e-12 < MIN_USEFUL_OUTPUT_RATE
    ):
        _append_once(findings, "LOW_USEFULNESS")

    hard_gate_booleans = (
        n["useful_outcome_parity"],
        n["zero_residual"],
        n["zero_finite_quota"],
        n["zero_incremental_cost"],
        n["continuation_safe"],
        n["continuation_nonempty"],
        n["duplicate_resume_safe"],
        n["conflict_safe"],
        n["authority_valid"],
        n["bootstrap_valid"],
        not n["protected_authority_violation"],
        n["coverage_gate_satisfied"],
        n["managed_roles_required"] > 0,
        n["managed_roles_observed"] == n["managed_roles_required"],
        not n["unavailable_capability_only"],
    )

    hard_reject = bool(findings)
    logical_pass = (not hard_reject) and all(hard_gate_booleans)

    if hard_reject:
        classification = "HARD_REJECT"
        exit_code = 2
    elif n["downstream_verification_required"]:
        classification = "DOWNSTREAM_VERIFICATION_REQUIRED"
        logical_pass = True
        exit_code = 3
    elif not usefulness_evaluable:
        classification = "PARTIAL_EVIDENCE"
        logical_pass = False
        exit_code = 3
    elif useful_rate is None or useful_rate + 1e-12 < MIN_USEFUL_OUTPUT_RATE:
        # Defensive branch; LOW_USEFULNESS should already have made this HARD_REJECT.
        classification = "HARD_REJECT"
        logical_pass = False
        _append_once(findings, "LOW_USEFULNESS")
        exit_code = 2
    elif logical_pass:
        classification = "CLEAN_CELL_PASS"
        exit_code = 0
    else:
        classification = "PARTIAL_EVIDENCE"
        exit_code = 3

    result = {
        "checker_id": CHECKER_ID,
        "schema_id": SCHEMA_ID,
        "case_id": n["case_id"],
        "logical_pass": logical_pass,
        "classification": classification,
        "findings": findings,
        "schema_errors": schema_errors,
        "metrics": {
            "progress_opportunities": opportunities,
            "useful_outputs": useful_outputs,
            "useful_output_rate": useful_rate,
            "minimum_progress_opportunities": MIN_PROGRESS_OPPORTUNITIES,
            "minimum_useful_output_rate": MIN_USEFUL_OUTPUT_RATE,
            "usefulness_evaluable": usefulness_evaluable,
            "managed_roles_required": n["managed_roles_required"],
            "managed_roles_observed": n["managed_roles_observed"],
        },
        "root_acceptance": False,
        "positive_acceptance_requires_current_authority_revalidation": True,
        "denominator_constant_embedded": False,
    }
    return result, exit_code


def main(argv: List[str]) -> int:
    if len(argv) != 2:
        sys.stderr.write("usage: checker_v2r4.py CASE.json\n")
        return 64

    path = Path(argv[1])
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        result = {
            "checker_id": CHECKER_ID,
            "schema_id": SCHEMA_ID,
            "case_id": "<unreadable>",
            "logical_pass": False,
            "classification": "HARD_REJECT",
            "findings": ["INPUT_SCHEMA_VIOLATION"],
            "schema_errors": [f"input_read_or_parse_error:{type(exc).__name__}"],
            "root_acceptance": False,
            "positive_acceptance_requires_current_authority_revalidation": True,
            "denominator_constant_embedded": False,
        }
        sys.stdout.write(json.dumps(result, sort_keys=True, separators=(",", ":")) + "\n")
        return 2

    if not isinstance(payload, dict):
        payload = {"case_id": "<invalid>"}

    result, exit_code = evaluate(payload)
    sys.stdout.write(json.dumps(result, sort_keys=True, separators=(",", ":")) + "\n")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
