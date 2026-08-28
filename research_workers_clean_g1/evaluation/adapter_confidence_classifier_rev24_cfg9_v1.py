#!/usr/bin/env python3
import json
import sys

def classify(row):
    if row.get("required_canonical_case") and row.get("unsupported_completion"):
        return {
            "status": "HARD_REJECT",
            "acceptance_pass": False,
            "reason_code": "REQUIRED_CANONICAL_UNSUPPORTED_COMPLETION",
        }
    if row.get("independent_execution_evidence") and row.get("intended_runner_verdict") == "FAIL":
        return {
            "status": "HARD_REJECT",
            "acceptance_pass": False,
            "reason_code": "INTENDED_RUNNER_EXECUTION_FAIL",
        }
    if not row.get("wrapper_supported", True):
        return {
            "status": "BLOCKED_UNSUPPORTED",
            "acceptance_pass": False,
            "reason_code": "WRAPPER_UNSUPPORTED",
        }
    if not row.get("canonical_runner_identity_independently_proved"):
        return {
            "status": "PARTIAL",
            "acceptance_pass": False,
            "reason_code": "RUNNER_IDENTITY_UNPROVED",
        }
    if row.get("lexical_precedence_only") and not row.get("semantic_execution_proof"):
        return {
            "status": "PARTIAL",
            "acceptance_pass": False,
            "reason_code": "LEXICAL_PRECEDENCE_ONLY",
        }
    if (not row.get("independent_execution_evidence")
            or row.get("intended_runner_verdict") != "PASS"):
        return {
            "status": "PARTIAL",
            "acceptance_pass": False,
            "reason_code": "RUNNER_EXECUTION_EVIDENCE_MISSING",
        }
    if (row.get("pcy_relied_on")
            and not row.get("pcy_candidate_identity_independently_proved")):
        return {
            "status": "PARTIAL",
            "acceptance_pass": False,
            "reason_code": "PCY_TARGET_UNPROVED",
        }
    return {
        "status": "PASS",
        "acceptance_pass": True,
        "reason_code": "CANONICAL_RUNNER_INDEPENDENTLY_VERIFIED",
    }

def main():
    doc = json.load(sys.stdin)
    observed = []
    for row in doc["fixtures"]:
        result = classify(row["input"])
        observed.append({
            "id": row["id"],
            **result,
        })
    print(json.dumps({"observed": observed}, sort_keys=True, separators=(",", ":")))

if __name__ == "__main__":
    main()
