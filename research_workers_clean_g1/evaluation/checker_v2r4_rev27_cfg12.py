#!/usr/bin/env python3
"""Phase-1 evaluation checker v2r4 for control27/config12.

This source is intentionally materialized before its executable JSON schema,
control fixtures, immutable precommit, or any checker execution. It uses only
Python's standard library and performs no network, hosted-runner, quota-bearing,
or paid-service work.
"""
from __future__ import annotations

import argparse
import json
import sys
from typing import Any, Dict, List, Tuple

CHECKER_VERSION = "v2r4_rev27_cfg12"
EXPECTED_SCHEMA_VERSION = "phase1-eval-v2r4"
EXPECTED_ROLE_COUNT = 18
PASS_EXIT = 0
HARD_REJECT_EXIT = 2
PARTIAL_EXIT = 3
INPUT_ERROR_EXIT = 4


def _bool(value: Any) -> bool:
    return value is True


def _num(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    return None


def _fail(code: str, path: str, detail: str) -> Dict[str, str]:
    return {"code": code, "path": path, "detail": detail}


def evaluate(payload: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
    """Evaluate one candidate payload.

    Aggregate gates are checked before per-record gates. Any residual richer-mode,
    protected-primary, manual-user, finite-quota, positive-cost, unavailable-only,
    low-usefulness, coverage, continuation, conflict, or authority defect prevents
    acceptance. A generic protected-boundary candidate that explicitly requires
    downstream verification is non-accepting PARTIAL rather than a PASS.
    """
    failures: List[Dict[str, str]] = []
    partials: List[Dict[str, str]] = []

    if not isinstance(payload, dict):
        result = {
            "checker_version": CHECKER_VERSION,
            "status": "HARD_REJECT",
            "accepted": False,
            "failures": [_fail("INPUT_TYPE", "$", "payload must be a JSON object")],
            "partials": [],
        }
        return result, INPUT_ERROR_EXIT

    if payload.get("schema_version") != EXPECTED_SCHEMA_VERSION:
        failures.append(_fail("SCHEMA_VERSION", "$.schema_version", f"must equal {EXPECTED_SCHEMA_VERSION}"))

    aggregate = payload.get("aggregate")
    if not isinstance(aggregate, dict):
        failures.append(_fail("AGGREGATE_MISSING", "$.aggregate", "aggregate object is required"))
        aggregate = {}

    coverage = aggregate.get("coverage")
    if not isinstance(coverage, dict):
        failures.append(_fail("COVERAGE_MISSING", "$.aggregate.coverage", "coverage object is required"))
        coverage = {}
    intended = coverage.get("intended_roles")
    covered = coverage.get("covered_roles")
    if intended != EXPECTED_ROLE_COUNT or covered != EXPECTED_ROLE_COUNT:
        failures.append(_fail("COVERAGE_NOT_18_OF_18", "$.aggregate.coverage", "positive acceptance requires intended_roles=18 and covered_roles=18"))

    usefulness = aggregate.get("usefulness")
    if not isinstance(usefulness, dict):
        failures.append(_fail("USEFULNESS_MISSING", "$.aggregate.usefulness", "usefulness object is required"))
        usefulness = {}
    if not _bool(usefulness.get("meets_threshold")):
        failures.append(_fail("LOW_USEFULNESS", "$.aggregate.usefulness.meets_threshold", "useful outcome parity threshold must be met"))
    parity_score = _num(usefulness.get("parity_score"))
    threshold = _num(usefulness.get("threshold"))
    if parity_score is None or threshold is None or parity_score < threshold:
        failures.append(_fail("USEFULNESS_PARITY_SCORE", "$.aggregate.usefulness", "parity_score and threshold must be numeric and parity_score >= threshold"))

    if _bool(aggregate.get("residual_richer_mode_execution")):
        failures.append(_fail("RESIDUAL_RICHER_MODE", "$.aggregate.residual_richer_mode_execution", "residual richer-mode execution is forbidden"))
    if _bool(aggregate.get("residual_protected_primary_execution")):
        failures.append(_fail("RESIDUAL_PROTECTED_PRIMARY", "$.aggregate.residual_protected_primary_execution", "protected-primary execution cannot count as solved"))
    if _bool(aggregate.get("residual_manual_user_execution")):
        failures.append(_fail("RESIDUAL_MANUAL_USER", "$.aggregate.residual_manual_user_execution", "manual-user execution cannot count as solved"))
    if _bool(aggregate.get("finite_monthly_trial_paid_quota_dependency")):
        failures.append(_fail("FINITE_QUOTA_DEPENDENCY", "$.aggregate.finite_monthly_trial_paid_quota_dependency", "accepted route must operate with optional monthly/trial/paid quota at zero"))
    cost = _num(aggregate.get("incremental_monetary_cost"))
    if cost is None or cost != 0.0:
        failures.append(_fail("NONZERO_OR_UNKNOWN_COST", "$.aggregate.incremental_monetary_cost", "incremental monetary cost must be exactly zero"))
    if _bool(aggregate.get("unavailable_capability_only")):
        failures.append(_fail("UNAVAILABLE_CAPABILITY_ONLY", "$.aggregate.unavailable_capability_only", "unavailable capability is an unresolved child, not acceptance"))
    if not _bool(aggregate.get("continuation_safe")):
        failures.append(_fail("CONTINUATION_UNSAFE", "$.aggregate.continuation_safe", "continuation safety is required"))
    if not _bool(aggregate.get("conflict_safe")):
        failures.append(_fail("CONFLICT_UNSAFE", "$.aggregate.conflict_safe", "duplicate/conflict safety is required"))
    if not _bool(aggregate.get("authority_bound")):
        failures.append(_fail("AUTHORITY_UNBOUND", "$.aggregate.authority_bound", "exact authority binding is required"))

    records = payload.get("records")
    if not isinstance(records, list) or not records:
        failures.append(_fail("RECORDS_MISSING", "$.records", "nonempty records array is required"))
        records = []

    seen_roles = set()
    for index, record in enumerate(records):
        path = f"$.records[{index}]"
        if not isinstance(record, dict):
            failures.append(_fail("RECORD_TYPE", path, "record must be an object"))
            continue
        role = record.get("role")
        if not isinstance(role, str) or not role:
            failures.append(_fail("ROLE_MISSING", f"{path}.role", "role must be a nonempty string"))
        elif role in seen_roles:
            failures.append(_fail("DUPLICATE_ROLE_RECORD", f"{path}.role", "duplicate role/effect evidence is conflict-unsafe"))
        else:
            seen_roles.add(role)

        if not _bool(record.get("useful_outcome_parity")):
            failures.append(_fail("RECORD_LOW_USEFULNESS", f"{path}.useful_outcome_parity", "record must demonstrate useful outcome parity"))
        if _bool(record.get("residual_external_execution")):
            failures.append(_fail("RECORD_EXTERNAL_EXECUTION", f"{path}.residual_external_execution", "one residual external execution step is a hard failure"))
        if _bool(record.get("quota_dependency_at_zero")):
            failures.append(_fail("RECORD_QUOTA_ZERO_FAILURE", f"{path}.quota_dependency_at_zero", "candidate must still work when optional quota is zero"))
        if _bool(record.get("unavailable_capability_only")):
            failures.append(_fail("RECORD_UNAVAILABLE_ONLY", f"{path}.unavailable_capability_only", "unavailable-only is not completion"))
        if not _bool(record.get("continuation_safe")):
            failures.append(_fail("RECORD_CONTINUATION_UNSAFE", f"{path}.continuation_safe", "record continuation must be safe"))
        if not _bool(record.get("conflict_safe")):
            failures.append(_fail("RECORD_CONFLICT_UNSAFE", f"{path}.conflict_safe", "record must be duplicate/conflict safe"))

        protected_boundary = _bool(record.get("generic_protected_boundary"))
        downstream_required = _bool(record.get("downstream_verification_required"))
        downstream_present = _bool(record.get("downstream_verification_present"))
        if protected_boundary:
            if not downstream_required:
                failures.append(_fail("PROTECTED_BOUNDARY_UNSCOPED", f"{path}.downstream_verification_required", "generic protected-boundary evidence must explicitly require downstream verification"))
            elif not downstream_present:
                partials.append(_fail("DOWNSTREAM_VERIFICATION_REQUIRED", path, "protected-boundary evidence is non-accepting until downstream verification exists"))

    if failures:
        status = "HARD_REJECT"
        accepted = False
        exit_code = HARD_REJECT_EXIT
    elif partials:
        status = "PARTIAL"
        accepted = False
        exit_code = PARTIAL_EXIT
    else:
        status = "PASS"
        accepted = True
        exit_code = PASS_EXIT

    result = {
        "checker_version": CHECKER_VERSION,
        "status": status,
        "accepted": accepted,
        "aggregate_first": True,
        "expected_role_count": EXPECTED_ROLE_COUNT,
        "observed_unique_role_records": len(seen_roles),
        "failures": failures,
        "partials": partials,
    }
    return result, exit_code


def _load_input(path: str | None) -> Dict[str, Any]:
    if path:
        with open(path, "r", encoding="utf-8", newline=None) as handle:
            return json.load(handle)
    return json.load(sys.stdin)


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Phase-1 richer-mode-dependency elimination checker v2r4")
    parser.add_argument("input", nargs="?", help="UTF-8 JSON candidate payload; stdin when omitted")
    args = parser.parse_args(argv)
    try:
        payload = _load_input(args.input)
        result, exit_code = evaluate(payload)
    except (OSError, json.JSONDecodeError) as exc:
        result = {
            "checker_version": CHECKER_VERSION,
            "status": "HARD_REJECT",
            "accepted": False,
            "failures": [_fail("INPUT_READ_OR_JSON", "$", str(exc))],
            "partials": [],
        }
        exit_code = INPUT_ERROR_EXIT
    sys.stdout.write(json.dumps(result, sort_keys=True, separators=(",", ":")) + "\n")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
