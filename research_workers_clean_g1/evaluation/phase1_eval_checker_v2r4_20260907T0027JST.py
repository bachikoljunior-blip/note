#!/usr/bin/env python3
"""Deterministic Phase-1 evaluation checker v2r4.

This source is materialized under frozen evaluation authority but is not itself
positive acceptance evidence. Execution is permitted only after a later
immutable precommit binds the exact persisted source/schema/control identities.
"""
from __future__ import annotations
import json
import sys

CHECKER_ID = "phase1_eval_checker_v2r4"
CHECKER_VERSION = 4
ROOT_CONTROL_REVISION = 27
ROOT_GIT_BLOB_SHA = "0eee15a94c23400653d84506da1f795081a6ef24"
EVALUATION_CONFIG_REVISION = 13
EVALUATION_CONFIG_GIT_BLOB_SHA = "5e70affae8abde5dc1c87dc8fd75595d6e16f069"
CURRENT_MANAGED_POOL_DENOMINATOR = 18

CONTROL_FAMILY = (
    "reducible_handoff_negative",
    "unsupported_handoff_negative",
    "duplicate_or_conflict_negative",
    "low_usefulness_negative",
    "matched_chat_complete_positive",
    "matched_generic_protected_boundary_requires_downstream_verification",
)

def _nonnegative_int(v):
    return isinstance(v, int) and not isinstance(v, bool) and v >= 0

def _number(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)

def validate_case(case):
    errors = []
    required = (
        "case_id",
        "control_family",
        "useful_outcome_parity",
        "residual_richer_mode_execution_dependencies",
        "residual_protected_or_manual_user_execution_dependencies",
        "finite_monthly_trial_paid_quota_dependencies",
        "incremental_monetary_cost",
        "continuation_safe",
        "conflict_safe",
        "authority_safe",
        "usefulness_positive",
        "current_managed_role_coverage",
        "current_managed_role_denominator",
    )
    for key in required:
        if key not in case:
            errors.append("missing:" + key)

    if errors:
        return sorted(set(errors))

    if not isinstance(case["case_id"], str):
        errors.append("type:case_id")
    if case["control_family"] not in CONTROL_FAMILY:
        errors.append("value:control_family")
    for key in ("useful_outcome_parity", "continuation_safe", "conflict_safe", "authority_safe", "usefulness_positive"):
        if not isinstance(case[key], bool):
            errors.append("type:" + key)
    for key in (
        "residual_richer_mode_execution_dependencies",
        "residual_protected_or_manual_user_execution_dependencies",
        "finite_monthly_trial_paid_quota_dependencies",
        "current_managed_role_coverage",
        "current_managed_role_denominator",
    ):
        if not _nonnegative_int(case[key]):
            errors.append("range:" + key)
    if not _number(case["incremental_monetary_cost"]) or case["incremental_monetary_cost"] < 0:
        errors.append("range:incremental_monetary_cost")
    return sorted(set(errors))

def evaluate(case):
    validation_errors = validate_case(case)
    if validation_errors:
        return {
            "checker_id": CHECKER_ID,
            "checker_version": CHECKER_VERSION,
            "case_id": case.get("case_id"),
            "decision": "invalid_input",
            "hard_gate_pass": False,
            "reasons": validation_errors,
        }

    reasons = []
    if not case["useful_outcome_parity"]:
        reasons.append("useful_outcome_parity_not_proven")
    if case["residual_richer_mode_execution_dependencies"] != 0:
        reasons.append("residual_richer_mode_execution_dependency")
    if case["residual_protected_or_manual_user_execution_dependencies"] != 0:
        reasons.append("residual_protected_or_manual_user_execution_dependency")
    if case["finite_monthly_trial_paid_quota_dependencies"] != 0:
        reasons.append("finite_monthly_trial_paid_quota_dependency")
    if case["incremental_monetary_cost"] != 0:
        reasons.append("incremental_monetary_cost_nonzero")
    if not case["continuation_safe"]:
        reasons.append("continuation_safety_failure")
    if not case["conflict_safe"]:
        reasons.append("duplicate_or_conflict_safety_failure")
    if not case["authority_safe"]:
        reasons.append("authority_safety_failure")
    if not case["usefulness_positive"]:
        reasons.append("low_usefulness")
    if case["current_managed_role_denominator"] != CURRENT_MANAGED_POOL_DENOMINATOR:
        reasons.append("managed_pool_denominator_mismatch")
    if case["current_managed_role_coverage"] != CURRENT_MANAGED_POOL_DENOMINATOR:
        reasons.append("managed_pool_coverage_incomplete")

    hard_gate_pass = not reasons
    if hard_gate_pass and case["control_family"] == "matched_generic_protected_boundary_requires_downstream_verification":
        decision = "requires_downstream_verification"
        hard_gate_pass = False
        reasons = ["generic_protected_boundary_requires_independent_downstream_verification"]
    else:
        decision = "pass" if hard_gate_pass else "fail"

    return {
        "checker_id": CHECKER_ID,
        "checker_version": CHECKER_VERSION,
        "root_control_revision": ROOT_CONTROL_REVISION,
        "root_git_blob_sha": ROOT_GIT_BLOB_SHA,
        "evaluation_config_revision": EVALUATION_CONFIG_REVISION,
        "evaluation_config_git_blob_sha": EVALUATION_CONFIG_GIT_BLOB_SHA,
        "case_id": case["case_id"],
        "control_family": case["control_family"],
        "decision": decision,
        "hard_gate_pass": hard_gate_pass,
        "reasons": sorted(reasons),
    }

def main(argv):
    if len(argv) != 2:
        raise SystemExit("usage: phase1_eval_checker_v2r4.py <case.json>")
    with open(argv[1], "r", encoding="utf-8") as f:
        case = json.load(f)
    sys.stdout.write(json.dumps(evaluate(case), sort_keys=True, separators=(",", ":")) + "\n")
    return 0

if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
