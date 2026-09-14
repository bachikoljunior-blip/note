#!/usr/bin/env python3
import json
import sys

CHECKER_ID = "phase1_eval_checker_v2r4"
CHECKER_VERSION = 4
CURRENT_MANAGED_POOL_SIZE = 18


def evaluate(case):
    failures = []
    hard_true = (
        "useful_outcome_parity",
        "continuation_safe",
        "conflict_safe",
        "authority_valid",
        "clean_boundary_preserved",
    )
    for key in hard_true:
        if case.get(key) is not True:
            failures.append(key)

    if case.get("residual_execution_dependency") != "none":
        failures.append("residual_execution_dependency")
    if case.get("finite_monthly_quota_dependency") != "none":
        failures.append("finite_monthly_quota_dependency")
    if case.get("incremental_monetary_cost") != 0:
        failures.append("incremental_monetary_cost")
    if case.get("managed_pool_coverage_current") != CURRENT_MANAGED_POOL_SIZE:
        failures.append("managed_pool_coverage_current")
    if case.get("unavailable_capability_only") is True:
        failures.append("unavailable_capability_only")
    if case.get("duplicate_or_conflict_detected") is True:
        failures.append("duplicate_or_conflict_detected")
    if case.get("low_usefulness") is True:
        failures.append("low_usefulness")

    downstream_required = case.get("downstream_verification_required") is True
    if failures:
        verdict = "fail"
    elif downstream_required:
        verdict = "requires_downstream_verification"
    else:
        verdict = "pass"

    return {
        "checker_id": CHECKER_ID,
        "checker_version": CHECKER_VERSION,
        "case_id": case.get("case_id"),
        "verdict": verdict,
        "hard_gate_failures": sorted(set(failures)),
        "downstream_verification_required": downstream_required,
        "positive_acceptance_eligible": verdict == "pass",
    }


def main():
    payload = json.load(sys.stdin)
    cases = payload.get("cases")
    if not isinstance(cases, list) or not cases:
        raise SystemExit("input must contain nonempty cases list")
    output = {
        "checker_id": CHECKER_ID,
        "checker_version": CHECKER_VERSION,
        "results": [evaluate(case) for case in cases],
    }
    json.dump(output, sys.stdout, sort_keys=True, separators=(",", ":"))
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
