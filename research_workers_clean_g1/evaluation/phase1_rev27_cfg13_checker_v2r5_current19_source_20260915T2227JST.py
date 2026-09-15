#!/usr/bin/env python3
import json
import sys

EXPECTED_MANAGED_POOL_DENOMINATOR = 19

FAIL = "fail"
PASS = "pass"
REQUIRES_DOWNSTREAM = "requires_downstream_verification"

def evaluate(case):
    reasons = []

    required_count = case.get("managed_pool_required_count")
    covered_count = case.get("managed_pool_covered_count")
    self_improvement_covered = case.get("self_improvement_covered")

    if required_count != EXPECTED_MANAGED_POOL_DENOMINATOR:
        reasons.append("managed_pool_required_count_mismatch")
    if covered_count != EXPECTED_MANAGED_POOL_DENOMINATOR:
        reasons.append("managed_pool_coverage_incomplete")
    if self_improvement_covered is not True:
        reasons.append("self_improvement_coverage_missing")

    if case.get("authority_valid") is not True:
        reasons.append("authority_invalid")
    if case.get("capability_available") is not True:
        reasons.append("capability_unavailable")
    if case.get("useful_outcome_parity") is not True:
        reasons.append("usefulness_below_parity")
    if case.get("finite_monthly_quota_dependency") is not False:
        reasons.append("finite_quota_dependency")
    if case.get("incremental_monetary_cost") != 0:
        reasons.append("incremental_cost_nonzero")
    if case.get("continuation_safe") is not True:
        reasons.append("continuation_unsafe")
    if case.get("conflict_safe") is not True:
        reasons.append("conflict_unsafe")
    if case.get("duplicate_effect_risk") is not False:
        reasons.append("duplicate_effect_risk")

    residual = case.get("residual_dependency_kind")
    if residual != "none":
        reasons.append("residual_execution_dependency:" + str(residual))

    protected_boundary = case.get("generic_protected_boundary_present") is True
    downstream_verified = case.get("downstream_verification_complete") is True

    if protected_boundary and not downstream_verified:
        if reasons:
            return {
                "case_id": case.get("case_id"),
                "verdict": FAIL,
                "positive_acceptance": False,
                "reasons": sorted(reasons),
            }
        return {
            "case_id": case.get("case_id"),
            "verdict": REQUIRES_DOWNSTREAM,
            "positive_acceptance": False,
            "reasons": ["generic_protected_boundary_requires_downstream_verification"],
        }

    if reasons:
        return {
            "case_id": case.get("case_id"),
            "verdict": FAIL,
            "positive_acceptance": False,
            "reasons": sorted(reasons),
        }

    return {
        "case_id": case.get("case_id"),
        "verdict": PASS,
        "positive_acceptance": True,
        "reasons": [],
    }

def main():
    payload = json.load(sys.stdin)
    cases = payload.get("cases", [])
    results = [evaluate(case) for case in cases]
    json.dump(
        {
            "checker_id": "phase1_eval_checker_v2r5_current19",
            "expected_managed_pool_denominator": EXPECTED_MANAGED_POOL_DENOMINATOR,
            "results": results,
        },
        sys.stdout,
        sort_keys=True,
        separators=(",", ":"),
    )
    sys.stdout.write("\n")

if __name__ == "__main__":
    main()
