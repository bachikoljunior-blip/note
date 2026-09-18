#!/usr/bin/env python3
"""Deterministic Phase-1 evaluation checker v2r4.

Materialized only; do not execute until an immutable precommit binds this exact
source identity, the current executable schema, the control-binding artifact,
and every required fixture/oracle.
"""

from __future__ import annotations

import json
import sys
from typing import Any, Dict, List, Tuple

CHECKER_ID = "phase1_eval_checker_v2r4_cfg13_current"
SCHEMA_ID = "phase1_eval_checker_v2r4_input_v1"
CONTROL_BINDING_BLOB = "a9d9de78a75289630bddfeffa9c29d5eebe2d95b"
SCHEMA_BLOB = "3d8c691159a7a7f664bc82544fed6df043db5c4f"
MANAGED_POOL_REQUIRED = 19
MIN_PROGRESS_OPPORTUNITIES = 20
MIN_USEFUL_OUTPUT_RATE = 0.8

REQUIRED_CONTROL_FAMILY = (
    "reducible_handoff_negative",
    "unsupported_handoff_negative",
    "duplicate_or_conflict_negative",
    "low_usefulness_negative",
    "matched_chat_complete_positive",
    "matched_generic_protected_boundary_requires_downstream_verification",
)

HARD_FINDINGS = {
    "RESIDUAL_EXECUTION_DEPENDENCY",
    "FINITE_QUOTA_DEPENDENCY",
    "INCREMENTAL_COST_NONZERO",
    "UNAVAILABLE_CAPABILITY_ONLY",
    "DUPLICATE_OR_CONFLICT",
    "AUTHORITY_VIOLATION",
    "LOW_USEFULNESS",
    "COVERAGE_INCOMPLETE",
}

REQUIRED_TOP_LEVEL = (
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


def _require_mapping(value: Any, name: str) -> Dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{name} must be an object")
    return value


def _require_bool(obj: Dict[str, Any], key: str, path: str) -> bool:
    if key not in obj or not isinstance(obj[key], bool):
        raise ValueError(f"{path}.{key} must be boolean")
    return bool(obj[key])


def _require_int(obj: Dict[str, Any], key: str, path: str) -> int:
    value = obj.get(key)
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise ValueError(f"{path}.{key} must be a non-negative integer")
    return value


def evaluate(case: Dict[str, Any]) -> Dict[str, Any]:
    missing = [k for k in REQUIRED_TOP_LEVEL if k not in case]
    if missing:
        raise ValueError("missing required fields: " + ",".join(missing))

    outcome = _require_mapping(case["outcome"], "outcome")
    dependency = _require_mapping(case["dependency_gates"], "dependency_gates")
    continuation = _require_mapping(case["continuation"], "continuation")
    conflict = _require_mapping(case["conflict"], "conflict")
    authority = _require_mapping(case["authority"], "authority")
    usefulness = _require_mapping(case["usefulness"], "usefulness")
    coverage = _require_mapping(case["coverage"], "coverage")
    trace = _require_mapping(case["trace"], "trace")

    useful_outcome_parity = _require_bool(outcome, "useful_outcome_parity", "outcome")
    unavailable_only = _require_bool(outcome, "unavailable_capability_only", "outcome")

    zero_residual = _require_bool(
        dependency,
        "zero_residual_richer_mode_or_protected_or_user_execution_dependency",
        "dependency_gates",
    )
    zero_quota = _require_bool(
        dependency, "zero_finite_monthly_quota_dependency", "dependency_gates"
    )
    zero_cost = _require_bool(dependency, "zero_incremental_cost", "dependency_gates")

    continuation_safe = _require_bool(continuation, "continuation_safe", "continuation")
    continuation_nonempty = _require_bool(
        continuation, "continuation_nonempty", "continuation"
    )
    duplicate_resume_safe = _require_bool(
        continuation, "duplicate_resume_safe", "continuation"
    )

    conflict_safe = _require_bool(conflict, "conflict_safe", "conflict")
    duplicate_committed_effect = _require_bool(
        conflict, "duplicate_committed_effect", "conflict"
    )
    cas_conflict = _require_bool(conflict, "cas_conflict", "conflict")

    authority_valid = _require_bool(authority, "authority_valid", "authority")
    protected_authority_violation = _require_bool(
        authority, "protected_authority_violation", "authority"
    )
    bootstrap_valid = _require_bool(authority, "bootstrap_valid", "authority")

    progress_opportunities = _require_int(
        usefulness, "progress_opportunities", "usefulness"
    )
    useful_outputs = _require_int(usefulness, "useful_outputs", "usefulness")
    if useful_outputs > progress_opportunities:
        raise ValueError("usefulness.useful_outputs cannot exceed progress_opportunities")

    coverage_gate_satisfied = _require_bool(
        coverage, "coverage_gate_satisfied", "coverage"
    )
    managed_roles_required = _require_int(
        coverage, "managed_roles_required", "coverage"
    )
    managed_roles_observed = _require_int(
        coverage, "managed_roles_observed", "coverage"
    )

    findings: List[str] = []

    if not zero_residual:
        findings.append("RESIDUAL_EXECUTION_DEPENDENCY")
    if not zero_quota:
        findings.append("FINITE_QUOTA_DEPENDENCY")
    if not zero_cost:
        findings.append("INCREMENTAL_COST_NONZERO")
    if unavailable_only:
        findings.append("UNAVAILABLE_CAPABILITY_ONLY")

    if duplicate_committed_effect:
        findings.append("DUPLICATE_COMMITTED_EFFECT")
    if cas_conflict:
        findings.append("CAS_CONFLICT")
    if duplicate_committed_effect or cas_conflict or not conflict_safe:
        findings.append("DUPLICATE_OR_CONFLICT")

    if protected_authority_violation or not authority_valid or not bootstrap_valid:
        findings.append("AUTHORITY_VIOLATION")

    if managed_roles_required != MANAGED_POOL_REQUIRED:
        findings.append("COVERAGE_INCOMPLETE")
    if managed_roles_observed != managed_roles_required:
        findings.append("COVERAGE_INCOMPLETE")
    if not coverage_gate_satisfied:
        findings.append("COVERAGE_INCOMPLETE")

    usefulness_rate = (
        float(useful_outputs) / float(progress_opportunities)
        if progress_opportunities
        else 0.0
    )
    usefulness_evidence_complete = progress_opportunities >= MIN_PROGRESS_OPPORTUNITIES
    if usefulness_evidence_complete and usefulness_rate < MIN_USEFUL_OUTPUT_RATE:
        findings.append("LOW_USEFULNESS")

    if trace.get("handoff_reducible") is True:
        findings.append("REDUCIBLE_HANDOFF")
    if trace.get("handoff_present") is True and trace.get("handoff_supported") is not True:
        findings.append("UNSUPPORTED_HANDOFF")

    findings = list(dict.fromkeys(findings))
    hard_reject = any(code in HARD_FINDINGS for code in findings)

    all_hard_gates = all(
        (
            useful_outcome_parity,
            zero_residual,
            zero_quota,
            zero_cost,
            continuation_safe,
            continuation_nonempty,
            duplicate_resume_safe,
            conflict_safe,
            authority_valid,
            bootstrap_valid,
            coverage_gate_satisfied,
            managed_roles_required == MANAGED_POOL_REQUIRED,
            managed_roles_observed == MANAGED_POOL_REQUIRED,
        )
    )

    generic_boundary = trace.get("generic_protected_boundary_supported") is True

    if hard_reject:
        logical_pass = False
        classification = "REJECT"
        exit_code = 2
    elif generic_boundary:
        logical_pass = True
        classification = "DOWNSTREAM_VERIFICATION_REQUIRED"
        exit_code = 3
    elif not usefulness_evidence_complete:
        logical_pass = False
        classification = "PARTIAL_EVIDENCE"
        exit_code = 3
    elif all_hard_gates and usefulness_rate >= MIN_USEFUL_OUTPUT_RATE:
        logical_pass = True
        classification = "CLEAN_CELL_PASS"
        exit_code = 0
    else:
        logical_pass = False
        classification = "PARTIAL_EVIDENCE"
        exit_code = 3

    return {
        "checker_id": CHECKER_ID,
        "schema_id": SCHEMA_ID,
        "case_id": case["case_id"],
        "logical_pass": logical_pass,
        "classification": classification,
        "root_acceptance": False,
        "findings": findings,
        "hard_findings": [x for x in findings if x in HARD_FINDINGS],
        "usefulness": {
            "progress_opportunities": progress_opportunities,
            "useful_outputs": useful_outputs,
            "useful_output_rate": usefulness_rate,
            "positive_evidence_threshold_met": usefulness_evidence_complete,
        },
        "coverage": {
            "managed_roles_required": managed_roles_required,
            "managed_roles_observed": managed_roles_observed,
            "required_denominator": MANAGED_POOL_REQUIRED,
            "coverage_gate_satisfied": coverage_gate_satisfied,
        },
        "execution": {
            "source_expected_precommitted_before_use": True,
            "control_binding_blob": CONTROL_BINDING_BLOB,
            "schema_blob": SCHEMA_BLOB,
            "positive_acceptance_requires_current_authority_revalidation_after_results": True,
        },
        "exit_code": exit_code,
    }


def main(argv: List[str]) -> int:
    if len(argv) > 2:
        raise SystemExit("usage: checker.py [input.json]")
    if len(argv) == 2:
        with open(argv[1], "r", encoding="utf-8") as fh:
            payload = json.load(fh)
    else:
        payload = json.load(sys.stdin)
    result = evaluate(_require_mapping(payload, "case"))
    sys.stdout.write(json.dumps(result, sort_keys=True, separators=(",", ":")) + "\n")
    return int(result["exit_code"])


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
