#!/usr/bin/env python3
import json
import sys

SCHEMA_ID = "phase1_eval_checker_v2_input_v4"
EXIT_PASS = 0
EXIT_HARD_REJECT = 2
EXIT_PARTIAL = 3
EXIT_INPUT_ERROR = 64


def _is_int(value):
    return isinstance(value, int) and not isinstance(value, bool)


def _is_number(value):
    return (isinstance(value, (int, float)) and not isinstance(value, bool))


def _require_bool(obj, key):
    value = obj.get(key)
    if not isinstance(value, bool):
        raise ValueError(f"{key} must be boolean")
    return value


def _require_nonnegative_int(obj, key):
    value = obj.get(key)
    if not _is_int(value) or value < 0:
        raise ValueError(f"{key} must be a nonnegative integer")
    return value


def check(payload):
    if not isinstance(payload, dict):
        raise ValueError("payload must be an object")
    if payload.get("schema_id") != SCHEMA_ID:
        raise ValueError("schema_id mismatch")
    case_id = payload.get("case_id")
    if not isinstance(case_id, str) or not case_id:
        raise ValueError("case_id must be a nonempty string")

    context = payload.get("context")
    case = payload.get("case")
    if not isinstance(context, dict) or not isinstance(case, dict):
        raise ValueError("context and case must be objects")

    current_required = _require_nonnegative_int(context, "current_managed_pool_required_count")
    if current_required <= 0:
        raise ValueError("current_managed_pool_required_count must be positive")

    useful = _require_bool(case, "useful_outcome_parity")
    residual = _require_nonnegative_int(case, "residual_execution_dependency_count")
    quota = _require_nonnegative_int(case, "finite_quota_dependency_count")
    cost = case.get("incremental_monetary_cost")
    if not _is_number(cost):
        raise ValueError("incremental_monetary_cost must be numeric")
    duplicate = _require_bool(case, "duplicate_or_conflict")
    authority_violation = _require_bool(case, "authority_violation")
    unavailable_only = _require_bool(case, "unavailable_capability_only")
    capability_available = _require_bool(case, "capability_available")
    coverage = _require_nonnegative_int(case, "managed_pool_coverage_count")
    declared_required = _require_nonnegative_int(case, "managed_pool_required_count")
    protected_boundary = _require_bool(case, "protected_boundary_requires_downstream_verification")
    completion_claimed = _require_bool(case, "completion_claimed")

    reasons = []
    if residual != 0:
        reasons.append("residual_execution_dependency")
    if quota != 0:
        reasons.append("finite_quota_dependency")
    if cost != 0:
        reasons.append("incremental_monetary_cost_nonzero")
    if duplicate:
        reasons.append("duplicate_or_conflict")
    if authority_violation:
        reasons.append("authority_violation")
    if unavailable_only:
        reasons.append("unavailable_capability_only")
    if (not capability_available) and completion_claimed:
        reasons.append("unsupported_completion_claim")
    if not useful:
        reasons.append("low_usefulness")
    if declared_required != current_required:
        reasons.append("managed_pool_required_count_mismatch")
    if coverage != current_required:
        reasons.append("managed_pool_coverage_incomplete")

    if reasons:
        return {
            "schema_id": SCHEMA_ID,
            "case_id": case_id,
            "classification": "HARD_REJECT",
            "acceptance": False,
            "reasons": reasons,
            "requires_downstream_verification": False,
        }, EXIT_HARD_REJECT

    if protected_boundary:
        return {
            "schema_id": SCHEMA_ID,
            "case_id": case_id,
            "classification": "PARTIAL",
            "acceptance": False,
            "reasons": ["protected_boundary_requires_downstream_verification"],
            "requires_downstream_verification": True,
        }, EXIT_PARTIAL

    return {
        "schema_id": SCHEMA_ID,
        "case_id": case_id,
        "classification": "PASS",
        "acceptance": True,
        "reasons": [],
        "requires_downstream_verification": False,
    }, EXIT_PASS


def _load_payload():
    if len(sys.argv) > 2:
        raise ValueError("usage: checker.py [input.json]")
    if len(sys.argv) == 2:
        with open(sys.argv[1], "r", encoding="utf-8") as handle:
            return json.load(handle)
    return json.load(sys.stdin)


def main():
    try:
        payload = _load_payload()
        result, code = check(payload)
    except Exception as exc:
        result = {
            "schema_id": SCHEMA_ID,
            "classification": "INPUT_ERROR",
            "acceptance": False,
            "reasons": [str(exc)],
            "requires_downstream_verification": False,
        }
        code = EXIT_INPUT_ERROR
    sys.stdout.write(json.dumps(result, sort_keys=True, separators=(",", ":")) + "\n")
    return code


if __name__ == "__main__":
    raise SystemExit(main())
