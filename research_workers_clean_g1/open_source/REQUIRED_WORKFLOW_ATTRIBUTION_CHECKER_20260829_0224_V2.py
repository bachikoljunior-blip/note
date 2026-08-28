#!/usr/bin/env python3
"""Fail-closed GitHub required-workflow verifier with rule-suite reconciliation.

Workflow-run provenance can diagnose exact target/source workflow identity, but
ordinary reusable-workflow runs expose the same provenance. Therefore run
matching alone never PASSes the ruleset requirement.

GitHub repository rule suites are authoritative rule evaluations, but they are
about a concrete attempted ref update (`ref`, `before_sha`, `after_sha`). A rule
suite can therefore decide this family only when the caller has separately
bound that exact `after_sha` to the intended effect being reconciled. Historical
or merely same-branch rule suites never count as preflight evidence.
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

def _diagnostics(required, runs, target_head):
    out = []
    for wf in required:
        exact = [
            r for r in runs
            if isinstance(r, dict) and _source_matches(wf, r, target_head)
        ]
        out.append({
            "workflow": {
                "repository_id": wf.get("repository_id"),
                "path": wf.get("path"),
                "ref": wf.get("ref"),
                "sha": wf.get("sha"),
            },
            "exact_run_count": len(exact),
            "successful_exact_run_count": sum(
                r.get("conclusion") == "success" for r in exact
            ),
        })
    return out

def _bound_rule_suite_verdict(doc, rule):
    suite = doc.get("rule_suite") or {}
    binding = doc.get("effect_binding") or {}
    expected_ref = binding.get("ref")
    expected_after = binding.get("after_sha")
    if not (
        binding.get("exact_after_sha_bound") is True
        and isinstance(expected_after, str) and expected_after
        and suite.get("after_sha") == expected_after
        and suite.get("ref") == expected_ref
    ):
        return None

    evaluations = suite.get("rule_evaluations")
    if not isinstance(evaluations, list):
        return None
    matches = []
    for ev in evaluations:
        if not isinstance(ev, dict):
            continue
        src = ev.get("rule_source") or {}
        if (
            ev.get("rule_type") == "workflows"
            and src.get("type") == "ruleset"
            and src.get("id") == rule.get("ruleset_id")
            and ev.get("enforcement") == "active"
        ):
            matches.append(ev)

    if not matches:
        return None
    results = {ev.get("result") for ev in matches}
    if "fail" in results:
        return {
            "verdict": BLOCKED,
            "reason": "exact bound rule suite reports required-workflow rule failure",
            "rule_suite_id": suite.get("id"),
            "after_sha": suite.get("after_sha"),
        }
    if results == {"pass"}:
        return {
            "verdict": PASS,
            "reason": "exact bound rule suite reports required-workflow rule pass",
            "rule_suite_id": suite.get("id"),
            "after_sha": suite.get("after_sha"),
        }
    return None

def check(doc):
    if doc.get("schema_version") != 2:
        return {"verdict": UNKNOWN, "reason": "unsupported schema_version"}
    if doc.get("applicable") is False:
        return {"verdict": PASS, "reason": "not applicable"}

    target_head = doc.get("target_head_sha")
    rule = doc.get("required_workflow_rule") or {}
    required = rule.get("workflows")
    if not target_head or not isinstance(required, list) or not required:
        return {"verdict": UNKNOWN, "reason": "target head or required-workflow identities missing"}
    if rule.get("ruleset_id") is None:
        return {"verdict": UNKNOWN, "reason": "ruleset_id missing"}
    for wf in required:
        if not isinstance(wf, dict) or wf.get("repository_id") is None or not wf.get("path"):
            return {"verdict": UNKNOWN, "reason": "invalid required-workflow identity"}

    suite_result = _bound_rule_suite_verdict(doc, rule)
    if suite_result is not None:
        suite_result["source_identity_diagnostics"] = _diagnostics(
            required, doc.get("workflow_runs") or [], target_head
        )
        return suite_result

    return {
        "verdict": UNKNOWN,
        "reason": (
            "workflow source matches are not ruleset attribution; no exact "
            "effect-bound rule-suite evaluation is available"
        ),
        "source_identity_diagnostics": _diagnostics(
            required, doc.get("workflow_runs") or [], target_head
        ),
        "required_missing_signal": (
            "rule suite whose ref/after_sha is exactly bound to the intended "
            "effect and whose workflows evaluation is sourced from this ruleset"
        ),
    }

def fixture():
    return {
        "schema_version": 2,
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
        "effect_binding": {
            "ref": "refs/heads/main",
            "after_sha": "m" * 40,
            "exact_after_sha_bound": False,
        },
        "rule_suite": {
            "id": 21,
            "ref": "refs/heads/main",
            "before_sha": "p" * 40,
            "after_sha": "m" * 40,
            "result": "pass",
            "evaluation_result": "pass",
            "rule_evaluations": [{
                "rule_source": {"type": "ruleset", "id": 42, "name": "required CI"},
                "enforcement": "active",
                "result": "pass",
                "rule_type": "workflows",
            }],
        },
    }

def self_test():
    base = fixture()

    source_only = json.loads(json.dumps(base))
    source_only["rule_suite"] = {}
    assert check(source_only)["verdict"] == UNKNOWN
    assert check(source_only)["source_identity_diagnostics"][0]["successful_exact_run_count"] == 1

    historical_suite = json.loads(json.dumps(base))
    historical_suite["effect_binding"]["exact_after_sha_bound"] = True
    historical_suite["effect_binding"]["after_sha"] = "x" * 40
    assert check(historical_suite)["verdict"] == UNKNOWN

    unbound_same_sha = json.loads(json.dumps(base))
    assert check(unbound_same_sha)["verdict"] == UNKNOWN

    exact_pass = json.loads(json.dumps(base))
    exact_pass["effect_binding"]["exact_after_sha_bound"] = True
    assert check(exact_pass)["verdict"] == PASS

    exact_fail = json.loads(json.dumps(exact_pass))
    exact_fail["rule_suite"]["result"] = "fail"
    exact_fail["rule_suite"]["evaluation_result"] = "fail"
    exact_fail["rule_suite"]["rule_evaluations"][0]["result"] = "fail"
    assert check(exact_fail)["verdict"] == BLOCKED

    wrong_ruleset = json.loads(json.dumps(exact_pass))
    wrong_ruleset["rule_suite"]["rule_evaluations"][0]["rule_source"]["id"] = 999
    assert check(wrong_ruleset)["verdict"] == UNKNOWN

    wrong_rule_type = json.loads(json.dumps(exact_pass))
    wrong_rule_type["rule_suite"]["rule_evaluations"][0]["rule_type"] = "required_status_checks"
    assert check(wrong_rule_type)["verdict"] == UNKNOWN

    return {
        "ordinary_source_match_without_rule_suite": UNKNOWN,
        "historical_suite_wrong_effect_sha": UNKNOWN,
        "same_sha_but_unbound_effect": UNKNOWN,
        "exact_effect_bound_suite_pass": PASS,
        "exact_effect_bound_suite_fail": BLOCKED,
        "wrong_ruleset_source": UNKNOWN,
        "wrong_rule_type": UNKNOWN,
    }

if __name__ == "__main__":
    if "--self-test" in sys.argv:
        print(json.dumps(self_test(), indent=2, sort_keys=True))
    else:
        print(json.dumps(check(json.load(sys.stdin)), indent=2, sort_keys=True))
