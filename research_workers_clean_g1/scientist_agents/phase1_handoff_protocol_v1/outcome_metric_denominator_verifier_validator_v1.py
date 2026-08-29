#!/usr/bin/env python3
"""Dependency-free validator for p1-protocol-065 outcome denominator provenance."""
from __future__ import annotations

import json
import math
import sys


def validate_metric(doc: dict) -> tuple[bool, list[str]]:
    errors: list[str] = []
    required = [
        "population_n", "evaluator_scored_n", "forced_failure_n",
        "pending_or_unscored_n", "metric_denominator_n", "numerator_n",
        "metric_reported", "metric_semantics_disclosed", "verifier_status",
        "claimed_scope",
    ]
    for key in required:
        if key not in doc:
            errors.append(f"missing:{key}")
    if errors:
        return False, errors

    count_keys = [
        "population_n", "evaluator_scored_n", "forced_failure_n",
        "pending_or_unscored_n", "metric_denominator_n", "numerator_n",
    ]
    if any(type(doc[key]) is not int or doc[key] < 0 for key in count_keys):
        return False, ["invalid_nonnegative_integer_count"]

    partition = doc["evaluator_scored_n"] + doc["forced_failure_n"] + doc["pending_or_unscored_n"]
    if partition != doc["population_n"]:
        errors.append("status_partition_does_not_equal_population")

    if doc["metric_reported"]:
        if doc["metric_denominator_n"] <= 0:
            errors.append("reported_metric_has_empty_denominator")
        else:
            if doc["numerator_n"] > doc["metric_denominator_n"]:
                errors.append("numerator_exceeds_denominator")
            if "metric_value" not in doc or doc["metric_value"] is None:
                errors.append("reported_metric_missing_value")
            else:
                expected = doc["numerator_n"] / doc["metric_denominator_n"]
                if not math.isclose(float(doc["metric_value"]), expected, rel_tol=1e-12, abs_tol=1e-12):
                    errors.append("metric_value_not_recomputable")
    elif doc["metric_denominator_n"] != 0 or doc["numerator_n"] != 0:
        errors.append("no_metric_claim_must_have_zero_metric_counts")

    if doc["claimed_scope"] == "uniform_completed_verification":
        if doc["verifier_status"] != "completed":
            errors.append("uniform_verification_claim_with_noncompleted_verifier")
        if doc["evaluator_scored_n"] != doc["population_n"]:
            errors.append("uniform_verification_claim_without_full_coverage")
        if doc["forced_failure_n"] or doc["pending_or_unscored_n"]:
            errors.append("uniform_verification_claim_with_heterogeneous_statuses")

    if (doc["forced_failure_n"] > 0 or doc["pending_or_unscored_n"] > 0) and not doc["metric_semantics_disclosed"]:
        errors.append("heterogeneous_statuses_without_metric_semantics_disclosure")

    if "slice_population_n" in doc:
        if doc["slice_population_n"] < doc["metric_denominator_n"]:
            errors.append("slice_population_smaller_than_denominator")
        if not doc.get("slice_coverage_disclosed", False):
            errors.append("slice_coverage_not_disclosed")

    return len(errors) == 0, errors


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: outcome_metric_denominator_verifier_validator_v1.py INPUT.json", file=sys.stderr)
        return 2
    with open(sys.argv[1], "r", encoding="utf-8") as fh:
        doc = json.load(fh)
    ok, errors = validate_metric(doc)
    print(json.dumps({"valid": ok, "errors": errors}, sort_keys=True))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
