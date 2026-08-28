#!/usr/bin/env python3
"""Fail-closed checker for GitHub required-workflow policy attribution.

A Workflow Run can prove target head and referenced reusable-workflow source
identity. Those fields do not prove that the run was required by a ruleset,
because ordinary reusable-workflow executions expose the same shape.

Only an authoritative rule-evaluation / ruleset-attribution result can PASS or
BLOCK this policy family. Source/run matching remains diagnostic evidence.
"""
from __future__ import annotations
import json, sys

PASS = "PASS"
BLOCKED = "BLOCKED"
UNKNOWN = "UNKNOWN"

def _source_matches(wf, run, target_head):
    if run.get("target_head_sha") != target_head:
        return False
    if run.get("source_repository_id") != wf.get("repository_id"):
        return False
    if run.get("source_path") != wf.get("path"):
        return False
    if wf.get("ref") is not None and run.get("source_ref") != wf.get("ref"):
        return False
    if wf.get("sha") is not None and run.get("source_sha") != wf.get("sha"):
        return False
    return True

def check(doc):
    if doc.get("schema_version") != 1:
        return {"verdict": UNKNOWN, "reason": "unsupported schema_version"}
    if doc.get("applicable") is False:
        return {"verdict": PASS, "reason": "not applicable"}

    target_head = doc.get("target_head_sha")
    rule = doc.get("required_workflow_rule") or {}
    required = rule.get("workflows")
    if not target_head or not isinstance(required, list) or not required:
        return {"verdict": UNKNOWN, "reason": "target head or required-workflow identities missing"}
    for wf in required:
        if not isinstance(wf, dict) or wf.get("repository_id") is None or not wf.get("path"):
            return {"verdict": UNKNOWN, "reason": "invalid required-workflow identity"}

    evaluation = doc.get("authoritative_rule_evaluation") or {}
    eval_bound = (
        evaluation.get("target_head_sha") == target_head
        and evaluation.get("ruleset_id") == rule.get("ruleset_id")
        and evaluation.get("rule_identity_bound") is True
        and evaluation.get("source") in {
            "server_effective_rule_evaluation",
            "ruleset_attributed_execution",
        }
    )
    if eval_bound:
        verdict = evaluation.get("verdict")
        if verdict == "pass":
            return {
                "verdict": PASS,
                "reason": "authoritative required-workflow rule evaluation passed on exact target head",
                "ruleset_id": rule.get("ruleset_id"),
            }
        if verdict == "blocked":
            return {
                "verdict": BLOCKED,
                "reason": "authoritative required-workflow rule evaluation blocked exact target head",
                "ruleset_id": rule.get("ruleset_id"),
                "details": evaluation.get("details"),
            }

    runs = doc.get("workflow_runs")
    if not isinstance(runs, list):
        runs = []
    matches = []
    for wf in required:
        exact = [r for r in runs if isinstance(r, dict) and _source_matches(wf, r, target_head)]
        matches.append({
            "workflow": {
                "repository_id": wf.get("repository_id"),
                "path": wf.get("path"),
                "ref": wf.get("ref"),
                "sha": wf.get("sha"),
            },
            "exact_run_count": len(exact),
            "successful_exact_run_count": sum(r.get("conclusion") == "success" for r in exact),
        })

    return {
        "verdict": UNKNOWN,
        "reason": "source-matching workflow runs do not prove required-ruleset attribution",
        "source_identity_diagnostics": matches,
        "required_missing_signal": "authoritative ruleset/rule evaluation bound to exact target head",
    }

def fixture():
    return {
        "schema_version": 1,
        "applicable": True,
        "target_head_sha": "a" * 40,
        "required_workflow_rule": {
            "ruleset_id": 42,
            "workflows": [{
                "repository_id": 550782323,
                "path": ".github/workflows/integration_test.yaml",
                "ref": "refs/heads/main",
                "sha": "b" * 40,
            }],
        },
        "workflow_runs": [{
            "target_head_sha": "a" * 40,
            "source_repository_id": 550782323,
            "source_path": ".github/workflows/integration_test.yaml",
            "source_ref": "refs/heads/main",
            "source_sha": "b" * 40,
            "conclusion": "success",
            "event": "schedule",
        }],
        "authoritative_rule_evaluation": {},
    }

def self_test():
    base = fixture()
    source_only = check(base)
    assert source_only["verdict"] == UNKNOWN
    assert source_only["source_identity_diagnostics"][0]["successful_exact_run_count"] == 1

    good = json.loads(json.dumps(base))
    good["authoritative_rule_evaluation"] = {
        "source": "server_effective_rule_evaluation",
        "ruleset_id": 42,
        "rule_identity_bound": True,
        "target_head_sha": "a" * 40,
        "verdict": "pass",
    }
    assert check(good)["verdict"] == PASS

    blocked = json.loads(json.dumps(good))
    blocked["authoritative_rule_evaluation"]["verdict"] = "blocked"
    assert check(blocked)["verdict"] == BLOCKED

    wrong_head = json.loads(json.dumps(good))
    wrong_head["authoritative_rule_evaluation"]["target_head_sha"] = "c" * 40
    assert check(wrong_head)["verdict"] == UNKNOWN

    moving_ref = json.loads(json.dumps(base))
    moving_ref["workflow_runs"][0]["source_sha"] = "c" * 40
    out = check(moving_ref)
    assert out["verdict"] == UNKNOWN
    assert out["source_identity_diagnostics"][0]["exact_run_count"] == 0

    return {
        "ordinary_reusable_source_match_without_ruleset_attribution": source_only["verdict"],
        "authoritative_exact_rule_pass": PASS,
        "authoritative_exact_rule_blocked": BLOCKED,
        "mismatched_rule_evaluation_head": UNKNOWN,
        "source_sha_mismatch": UNKNOWN,
    }

if __name__ == "__main__":
    if "--self-test" in sys.argv:
        print(json.dumps(self_test(), indent=2, sort_keys=True))
    else:
        print(json.dumps(check(json.load(sys.stdin)), indent=2, sort_keys=True))
