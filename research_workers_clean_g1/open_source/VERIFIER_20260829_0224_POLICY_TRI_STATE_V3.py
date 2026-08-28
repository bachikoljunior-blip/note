#!/usr/bin/env python3
"""Fail-closed GitHub policy verifier v3.

This revision supersedes v2 for the required_workflows family.  Exact Workflow
Run source provenance is diagnostic only: ordinary reusable-workflow executions
can have the same shape.  PASS/BLOCKED for required workflows therefore needs
an exact effect-bound GitHub Rule Suite evaluation from the applicable ruleset.

Other policy-family logic is intentionally reused from the frozen v2 verifier.
"""
from __future__ import annotations
import json, sys
import VERIFIER_20260829_0157_POLICY_TRI_STATE_V2 as v2

PASS, BLOCKED, UNKNOWN = v2.PASS, v2.BLOCKED, v2.UNKNOWN


def _result(family, verdict, *reasons):
    return {"family": family, "verdict": verdict, "reasons": list(reasons)}


def _missing(comp, axes):
    return [k for k in axes if comp.get(k) is not True]


def _blockers(f):
    return v2._blockers(f)


def _workflow_diagnostics(required, runs, target_head):
    out = []
    for wf in required:
        candidates = [r for r in runs if isinstance(r, dict)
            and r.get("target_head_sha") == target_head
            and r.get("source_repository_id") == wf.get("repository_id")
            and r.get("source_path") == wf.get("path")
            and (wf.get("ref") is None or r.get("source_ref") == wf.get("ref"))
            and (wf.get("sha") is None or r.get("source_sha") == wf.get("sha"))]
        out.append({
            "repository_id": wf.get("repository_id"),
            "path": wf.get("path"),
            "ref": wf.get("ref"),
            "sha": wf.get("sha"),
            "exact_run_count": len(candidates),
            "successful_exact_run_count": sum(
                r.get("conclusion") == "success" for r in candidates),
        })
    return out


def verify_workflows(f, target_head):
    family = "required_workflows"
    if f.get("applicable") is False:
        return _result(family, PASS, "not applicable")
    if (b := _blockers(f)):
        return _result(family, BLOCKED, *b)

    comp = f.get("completeness") or {}
    axes = ["policy", "target_sha_binding", "run_pagination", "workflow_identity",
            "effect_binding", "rule_suite_detail"]
    if (miss := _missing(comp, axes)):
        return _result(family, UNKNOWN, "incomplete: " + ", ".join(miss))

    raw = f.get("policy_raw") or {}
    params = raw.get("parameters", {}) if isinstance(raw, dict) else {}
    required = params.get("workflows") or (f.get("requirements") or {}).get("workflows") or []
    runs = (f.get("evidence") or {}).get("runs")
    if not isinstance(required, list) or not required or not isinstance(runs, list):
        return _result(family, UNKNOWN, "required workflow identities or run diagnostics missing")
    for wf in required:
        if not isinstance(wf, dict) or wf.get("repository_id") is None or not wf.get("path"):
            return _result(family, UNKNOWN, "invalid required workflow identity")

    ruleset_id = f.get("ruleset_id")
    if ruleset_id is None:
        return _result(family, UNKNOWN, "ruleset_id missing")

    ev = f.get("evidence") or {}
    binding = ev.get("effect_binding") or {}
    suite = ev.get("rule_suite") or {}
    if not (
        binding.get("exact_after_sha_bound") is True
        and isinstance(binding.get("after_sha"), str)
        and binding.get("after_sha")
        and suite.get("after_sha") == binding.get("after_sha")
        and suite.get("ref") == binding.get("ref")
    ):
        return _result(family, UNKNOWN,
                       "Rule Suite is not exactly bound to the intended ref-update effect")

    evaluations = suite.get("rule_evaluations")
    if not isinstance(evaluations, list):
        return _result(family, UNKNOWN, "Rule Suite detail lacks rule_evaluations")
    matches = []
    for rule_eval in evaluations:
        if not isinstance(rule_eval, dict):
            continue
        source = rule_eval.get("rule_source") or {}
        if (
            rule_eval.get("rule_type") == "workflows"
            and rule_eval.get("enforcement") == "active"
            and source.get("type") == "ruleset"
            and source.get("id") == ruleset_id
        ):
            matches.append(rule_eval)
    if not matches:
        return _result(family, UNKNOWN,
                       "no active workflows evaluation from the applicable ruleset")
    results = {x.get("result") for x in matches}
    if "fail" in results:
        return _result(family, BLOCKED,
                       "exact effect-bound required-workflow Rule Suite evaluation failed")
    if results == {"pass"}:
        diag = _workflow_diagnostics(required, runs, target_head)
        return {"family": family, "verdict": PASS,
                "reasons": ["exact effect-bound required-workflow Rule Suite evaluation passed"],
                "workflow_run_diagnostics": diag}
    return _result(family, UNKNOWN, "required-workflow Rule Suite result is not pass/fail")


def verify(doc):
    if doc.get("schema_version") != 3:
        return {"verdict": UNKNOWN, "error": "unsupported schema_version"}
    head = (doc.get("candidate") or {}).get("head_sha")
    if not head or (doc.get("completeness") or {}).get("policy_inventory") is not True:
        return {"verdict": UNKNOWN, "error": "candidate head or policy inventory incomplete"}
    results = []
    for f in doc.get("families", []):
        family = f.get("family")
        if family == "pull_request_reviews":
            results.append(v2.verify_reviews(f))
        elif family == "required_workflows":
            results.append(verify_workflows(f, head))
        else:
            results.append(v2.verify_generic(f))
    if not results:
        return {"verdict": UNKNOWN, "error": "no policy families supplied"}
    verdict = "PROVED_BLOCKED" if any(r["verdict"] == BLOCKED for r in results) else (
        "PROVED_READY" if all(r["verdict"] == PASS for r in results) else UNKNOWN)
    return {"verdict": verdict, "candidate_head_sha": head, "families": results}


def fixture(workflow_family):
    return {"schema_version": 3, "candidate": {"head_sha": "a" * 40},
            "completeness": {"policy_inventory": True}, "families": [workflow_family]}


def workflow_family():
    wf = {"repository_id": 1234, "path": ".github/workflows/required.yml",
          "ref": "refs/heads/main", "sha": "b" * 40}
    return {
        "family": "required_workflows", "applicable": True, "ruleset_id": 42,
        "policy_raw": {"type": "workflows", "parameters": {"workflows": [wf]}},
        "completeness": {"policy": True, "target_sha_binding": True,
                         "run_pagination": True, "workflow_identity": True,
                         "effect_binding": True, "rule_suite_detail": True},
        "evidence": {
            "runs": [{"target_head_sha": "a" * 40, "source_repository_id": 1234,
                      "source_path": ".github/workflows/required.yml",
                      "source_ref": "refs/heads/main", "source_sha": "b" * 40,
                      "conclusion": "success", "event": "schedule"}],
            "effect_binding": {"ref": "refs/heads/main", "after_sha": "m" * 40,
                               "exact_after_sha_bound": False},
            "rule_suite": {"id": 21, "ref": "refs/heads/main", "after_sha": "m" * 40,
                           "rule_evaluations": [{
                               "rule_source": {"type": "ruleset", "id": 42},
                               "enforcement": "active", "result": "pass",
                               "rule_type": "workflows"}]},
        },
    }


def self_test():
    source_match_only = fixture(workflow_family())
    assert verify(source_match_only)["verdict"] == UNKNOWN

    exact_pass = json.loads(json.dumps(source_match_only))
    exact_pass["families"][0]["evidence"]["effect_binding"]["exact_after_sha_bound"] = True
    assert verify(exact_pass)["verdict"] == "PROVED_READY"

    exact_fail = json.loads(json.dumps(exact_pass))
    exact_fail["families"][0]["evidence"]["rule_suite"]["rule_evaluations"][0]["result"] = "fail"
    assert verify(exact_fail)["verdict"] == "PROVED_BLOCKED"

    wrong_ruleset = json.loads(json.dumps(exact_pass))
    wrong_ruleset["families"][0]["evidence"]["rule_suite"]["rule_evaluations"][0]["rule_source"]["id"] = 99
    assert verify(wrong_ruleset)["verdict"] == UNKNOWN

    historical = json.loads(json.dumps(exact_pass))
    historical["families"][0]["evidence"]["rule_suite"]["after_sha"] = "x" * 40
    assert verify(historical)["verdict"] == UNKNOWN

    no_runs = json.loads(json.dumps(exact_pass))
    no_runs["families"][0]["evidence"]["runs"] = []
    # Server rule evaluation is authoritative; run provenance remains diagnostic.
    assert verify(no_runs)["verdict"] == "PROVED_READY"

    return {
        "ordinary_source_match_without_effect_binding": UNKNOWN,
        "exact_effect_bound_rule_suite_pass": "PROVED_READY",
        "exact_effect_bound_rule_suite_fail": "PROVED_BLOCKED",
        "wrong_ruleset_source": UNKNOWN,
        "historical_rule_suite": UNKNOWN,
        "authoritative_rule_suite_without_matching_run_diagnostic": "PROVED_READY",
    }


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        print(json.dumps(self_test(), indent=2, sort_keys=True))
    else:
        print(json.dumps(verify(json.load(sys.stdin)), indent=2, sort_keys=True))
