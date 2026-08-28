#!/usr/bin/env python3
"""Fail-closed GitHub policy verifier for Phase-1 Chat capability probes.

Input is normalized JSON. This tool never calls GitHub. Missing evidence is
UNKNOWN; only complete evidence can produce PROVED_READY.
"""
from __future__ import annotations
import fnmatch, json, sys
from pathlib import PurePosixPath

PASS, BLOCKED, UNKNOWN = "PASS", "BLOCKED", "UNKNOWN"

def ordered_negation_fixture(patterns: list[str], path: str) -> bool:
    """Acceptance oracle for simple documented `*.sql`, `!test/*.sql` cases.
    Not a production gitignore parser.
    """
    matched = False
    p = PurePosixPath(path)
    for raw in patterns:
        neg = raw.startswith("!")
        pat = raw[1:] if neg else raw
        if p.match(pat) or fnmatch.fnmatchcase(path, pat):
            matched = not neg
    return matched

def _result(family, verdict, *reasons):
    return {"family": family, "verdict": verdict, "reasons": list(reasons)}

def _missing(comp, axes):
    return [k for k in axes if comp.get(k) is not True]

def _blockers(f):
    out = []
    for x in f.get("blocking_findings", []):
        if isinstance(x, str):
            out.append(x)
        elif isinstance(x, dict) and x.get("definitive") is True:
            out.append(str(x.get("reason") or x.get("code") or "definitive blocker"))
    return out

def verify_reviews(f):
    family = "pull_request_reviews"
    if f.get("applicable") is False:
        return _result(family, PASS, "not applicable")
    if (b := _blockers(f)):
        return _result(family, BLOCKED, *b)

    raw = f.get("policy_raw") or {}
    params = raw.get("parameters", raw) if isinstance(raw, dict) else {}
    req = dict(f.get("requirements") or {})
    for k in (
        "required_approving_review_count",
        "dismiss_stale_reviews_on_push",
        "required_reviewers",
        "require_code_owner_review",
        "require_last_push_approval",
        "required_review_thread_resolution",
        "require_extra_approval_for_unattributed_changes",
    ):
        if k in params:
            req[k] = params[k]

    comp, ev = f.get("completeness") or {}, f.get("evidence") or {}
    axes = ["policy", "reviews", "reviewer_permissions", "head_sha_binding", "shared_head_prs"]
    reviewer_rules = req.get("required_reviewers") or []
    has_patterns = any(isinstance(x, dict) and x.get("file_patterns") for x in reviewer_rules)
    if reviewer_rules:
        axes += ["changed_paths", "required_team_membership", "required_team_obligations"]
    if has_patterns:
        axes += ["required_reviewer_pattern_semantics"]
    if req.get("require_code_owner_review"):
        axes += ["changed_paths", "codeowners_base_file", "codeowner_obligations"]
    if req.get("require_last_push_approval"):
        axes += ["latest_reviewable_push"]
    if req.get("dismiss_stale_reviews_on_push"):
        axes += ["server_review_decision"]
    if req.get("required_review_thread_resolution"):
        axes += ["review_threads"]
    if req.get("require_extra_approval_for_unattributed_changes"):
        axes += ["pr_author_attribution"]
    if (miss := _missing(comp, axes)):
        return _result(family, UNKNOWN, "incomplete: " + ", ".join(miss))

    if has_patterns and ev.get("required_reviewer_pattern_engine") != "ordered_gitignore_negation":
        return _result(family, UNKNOWN, "required-reviewer pattern engine is not ordered_gitignore_negation")
    if (ev.get("changed_paths_source") == "rest_pull_files"
        and isinstance(ev.get("changed_file_count"), int)
        and ev["changed_file_count"] > 3000):
        return _result(family, UNKNOWN, "REST pull-files cap exceeded (3000)")

    if req.get("dismiss_stale_reviews_on_push"):
        d = ev.get("server_review_decision")
        if d in {"CHANGES_REQUESTED", "REVIEW_REQUIRED"}:
            return _result(family, BLOCKED, f"server_review_decision={d}")
        if d != "APPROVED":
            return _result(family, UNKNOWN, "server_review_decision not conclusively APPROVED")
    if req.get("required_review_thread_resolution") and ev.get("all_required_threads_resolved") is not True:
        return _result(family, BLOCKED if ev.get("all_required_threads_resolved") is False else UNKNOWN,
                       "required review threads unresolved or unknown")
    if req.get("require_code_owner_review") and ev.get("codeowner_approvals_satisfied") is not True:
        return _result(family, BLOCKED if ev.get("codeowner_approvals_satisfied") is False else UNKNOWN,
                       "code-owner approvals unsatisfied or unknown")
    if reviewer_rules and ev.get("required_team_approvals_satisfied") is not True:
        return _result(family, BLOCKED if ev.get("required_team_approvals_satisfied") is False else UNKNOWN,
                       "required reviewer-team approvals unsatisfied or unknown")
    if req.get("require_last_push_approval") and ev.get("last_push_approval_satisfied") is not True:
        return _result(family, BLOCKED if ev.get("last_push_approval_satisfied") is False else UNKNOWN,
                       "latest-push approval unsatisfied or unknown")
    if ev.get("same_head_blocker_absent") is not True:
        return _result(family, BLOCKED if ev.get("same_head_blocker_absent") is False else UNKNOWN,
                       "same-head blocking-review state not clear")

    configured = req.get("required_approving_review_count", 0)
    counted = ev.get("counted_current_authorized_approvals")
    if not isinstance(configured, int) or configured < 0 or not isinstance(counted, int) or counted < 0:
        return _result(family, UNKNOWN, "approval count invalid or missing")
    extra = 0
    if req.get("require_extra_approval_for_unattributed_changes"):
        attribution = ev.get("pr_author_attribution")
        if attribution == "copilot_unattributed":
            extra = 1
        elif attribution not in {"human", "copilot_attributed"}:
            return _result(family, UNKNOWN, "PR author attribution unknown")
    need = configured + extra
    if counted < need:
        return _result(family, BLOCKED, f"authorized approvals {counted} < required {need}")
    return _result(family, PASS, f"authorized approvals {counted} >= required {need}")

def verify_workflows(f, target_head):
    family = "required_workflows"
    if f.get("applicable") is False:
        return _result(family, PASS, "not applicable")
    if (b := _blockers(f)):
        return _result(family, BLOCKED, *b)
    comp = f.get("completeness") or {}
    if (miss := _missing(comp, ["policy", "target_sha_binding", "run_pagination", "workflow_identity"])):
        return _result(family, UNKNOWN, "incomplete: " + ", ".join(miss))
    raw = f.get("policy_raw") or {}
    params = raw.get("parameters", {}) if isinstance(raw, dict) else {}
    required = params.get("workflows") or (f.get("requirements") or {}).get("workflows") or []
    runs = (f.get("evidence") or {}).get("runs")
    if not isinstance(required, list) or not required or not isinstance(runs, list):
        return _result(family, UNKNOWN, "required workflow identities or runs missing")

    failures = []
    for wf in required:
        if not isinstance(wf, dict) or wf.get("repository_id") is None or not wf.get("path"):
            return _result(family, UNKNOWN, "invalid required workflow identity")
        candidates = [r for r in runs if isinstance(r, dict)
            and r.get("target_head_sha") == target_head
            and r.get("source_repository_id") == wf.get("repository_id")
            and r.get("source_path") == wf.get("path")
            and (wf.get("ref") is None or r.get("source_ref") == wf.get("ref"))
            and (wf.get("sha") is None or r.get("source_sha") == wf.get("sha"))]
        ident = (wf.get("repository_id"), wf.get("path"), wf.get("ref"), wf.get("sha"))
        if not candidates:
            failures.append(f"no exact run for {ident}")
        elif not any(r.get("conclusion") == "success" for r in candidates):
            failures.append(f"no successful exact run for {ident}")
    return _result(family, BLOCKED, *failures) if failures else _result(
        family, PASS, "all required workflow identities succeeded on exact target head")

def verify_generic(f):
    family = str(f.get("family"))
    contracts = {
        "required_status_checks": (["policy","head_sha_binding","pagination","app_provenance"], "all_required_checks_satisfied"),
        "required_deployments": (["policy","endpoint","target_sha_binding","environment_identity","current_state"], "all_required_deployments_succeeded"),
        "required_signatures": (["policy","update_range","commit_enumeration","verification"], "all_commits_verified"),
        "code_scanning": (["policy","endpoint","target_binding","analysis_and_alerts"], "rule_satisfied"),
        "code_quality": (["policy","endpoint","target_binding","findings"], "rule_satisfied"),
        "code_coverage": (["policy","endpoint","target_binding","coverage_result"], "rule_satisfied"),
    }
    if family not in contracts:
        return _result(family, UNKNOWN, "unknown family")
    if f.get("applicable") is False:
        return _result(family, PASS, "not applicable")
    if (b := _blockers(f)):
        return _result(family, BLOCKED, *b)
    axes, key = contracts[family]
    if (miss := _missing(f.get("completeness") or {}, axes)):
        return _result(family, UNKNOWN, "incomplete: " + ", ".join(miss))
    value = (f.get("evidence") or {}).get(key)
    if value is True:
        return _result(family, PASS, key)
    if value is False:
        return _result(family, BLOCKED, f"{key}=false")
    return _result(family, UNKNOWN, f"missing {key}")

def verify(doc):
    if doc.get("schema_version") != 2:
        return {"verdict": UNKNOWN, "error": "unsupported schema_version"}
    head = (doc.get("candidate") or {}).get("head_sha")
    if not head or (doc.get("completeness") or {}).get("policy_inventory") is not True:
        return {"verdict": UNKNOWN, "error": "candidate head or policy inventory incomplete"}
    results = []
    for f in doc.get("families", []):
        family = f.get("family")
        if family == "pull_request_reviews":
            results.append(verify_reviews(f))
        elif family == "required_workflows":
            results.append(verify_workflows(f, head))
        else:
            results.append(verify_generic(f))
    if not results:
        return {"verdict": UNKNOWN, "error": "no policy families supplied"}
    verdict = "PROVED_BLOCKED" if any(r["verdict"] == BLOCKED for r in results) else (
        "PROVED_READY" if all(r["verdict"] == PASS for r in results) else UNKNOWN)
    return {"verdict": verdict, "candidate_head_sha": head, "families": results}

def fixture(family):
    return {"schema_version":2, "candidate":{"head_sha":"a"*40},
            "completeness":{"policy_inventory":True}, "families":[family]}

def self_test():
    base_comp = {"policy":True,"reviews":True,"reviewer_permissions":True,
        "head_sha_binding":True,"shared_head_prs":True}
    copilot = fixture({"family":"pull_request_reviews","applicable":True,
        "policy_raw":{"type":"pull_request","parameters":{
            "required_approving_review_count":1,
            "require_extra_approval_for_unattributed_changes":True,
            "required_reviewers":[]}},
        "completeness":{**base_comp,"pr_author_attribution":True},
        "evidence":{"same_head_blocker_absent":True,
            "counted_current_authorized_approvals":1,
            "pr_author_attribution":"copilot_unattributed"}})

    raw_review = {"type":"pull_request","parameters":{
        "required_approving_review_count":1,
        "required_reviewers":[{"team_id":42,"required_approvals":1,
            "file_patterns":["*.sql","!test/*.sql"]}]}}
    rcomp = {**base_comp,"changed_paths":True,"required_team_membership":True,
        "required_team_obligations":True,"required_reviewer_pattern_semantics":True}
    fnmatch_only = fixture({"family":"pull_request_reviews","applicable":True,
        "policy_raw":raw_review,"completeness":rcomp,
        "evidence":{"same_head_blocker_absent":True,
            "counted_current_authorized_approvals":1,
            "required_team_approvals_satisfied":True,
            "required_reviewer_pattern_engine":"fnmatch_only"}})
    ordered = json.loads(json.dumps(fnmatch_only))
    ordered["families"][0]["evidence"]["required_reviewer_pattern_engine"] = "ordered_gitignore_negation"

    wf = {"repository_id":1234,"path":".github/workflows/required.yml","ref":"main","sha":"b"*40}
    wcomp = {"policy":True,"target_sha_binding":True,"run_pagination":True,"workflow_identity":True}
    exact_run = {"target_head_sha":"a"*40,"source_repository_id":1234,
        "source_path":".github/workflows/required.yml","source_ref":"main",
        "source_sha":"b"*40,"conclusion":"success"}
    wpass = fixture({"family":"required_workflows","applicable":True,
        "policy_raw":{"type":"workflows","parameters":{"workflows":[wf]}},
        "completeness":wcomp,"evidence":{"runs":[exact_run]}})
    wrong = json.loads(json.dumps(wpass))
    wrong["families"][0]["evidence"]["runs"][0]["source_repository_id"] = 9999

    cases = {
        "raw_copilot_key_blocks_one_approval": (copilot, "PROVED_BLOCKED"),
        "bare_fnmatch_collector_is_unknown": (fnmatch_only, UNKNOWN),
        "ordered_negation_collector_can_pass": (ordered, "PROVED_READY"),
        "required_workflow_exact_identity_pass": (wpass, "PROVED_READY"),
        "same_path_wrong_source_blocks": (wrong, "PROVED_BLOCKED"),
    }
    assert ordered_negation_fixture(["*.sql","!test/*.sql"], "prod/query.sql") is True
    assert ordered_negation_fixture(["*.sql","!test/*.sql"], "test/query.sql") is False
    out = {}
    for name, (doc, expected) in cases.items():
        got = verify(doc)["verdict"]
        assert got == expected, (name, got, expected)
        out[name] = got
    return out

if __name__ == "__main__":
    if "--self-test" in sys.argv:
        print(json.dumps(self_test(), indent=2, sort_keys=True))
    else:
        print(json.dumps(verify(json.load(sys.stdin)), indent=2, sort_keys=True))
