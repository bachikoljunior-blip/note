#!/usr/bin/env python3
"""Tri-state GitHub policy evidence verifier.

Consumes a normalized JSON document on stdin and emits a JSON verdict.
It does not call GitHub. It is deliberately fail-closed: missing policy/evidence
completeness produces UNKNOWN rather than READY.
"""
from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from typing import Any

PASS = "PASS"
BLOCKED = "BLOCKED"
UNKNOWN = "UNKNOWN"

OVERALL_READY = "PROVED_READY"
OVERALL_BLOCKED = "PROVED_BLOCKED"
OVERALL_UNKNOWN = "UNKNOWN"

@dataclass
class FamilyResult:
    family: str
    verdict: str
    reasons: list[str]

def _b(d: dict[str, Any], key: str) -> bool:
    return d.get(key) is True

def _missing(d: dict[str, Any], keys: list[str]) -> list[str]:
    return [k for k in keys if d.get(k) is not True]

def _definitive_blockers(f: dict[str, Any]) -> list[str]:
    out = []
    for x in f.get("blocking_findings", []):
        if isinstance(x, str):
            out.append(x)
        elif isinstance(x, dict) and x.get("definitive") is True:
            out.append(str(x.get("reason") or x.get("code") or "definitive blocker"))
    return out

def _generic(f: dict[str, Any], required_axes: list[str], pass_key: str) -> FamilyResult:
    name = str(f["family"])
    if f.get("applicable") is False:
        return FamilyResult(name, PASS, ["not applicable"])
    blockers = _definitive_blockers(f)
    if blockers:
        return FamilyResult(name, BLOCKED, blockers)
    comp = f.get("completeness") or {}
    miss = _missing(comp, required_axes)
    if miss:
        return FamilyResult(name, UNKNOWN, [f"incomplete: {', '.join(miss)}"])
    ev = f.get("evidence") or {}
    if ev.get(pass_key) is True:
        return FamilyResult(name, PASS, [pass_key])
    if ev.get(pass_key) is False:
        return FamilyResult(name, BLOCKED, [f"{pass_key}=false"])
    return FamilyResult(name, UNKNOWN, [f"missing {pass_key}"])

def _reviews(f: dict[str, Any]) -> FamilyResult:
    name = "pull_request_reviews"
    if f.get("applicable") is False:
        return FamilyResult(name, PASS, ["not applicable"])
    blockers = _definitive_blockers(f)
    if blockers:
        return FamilyResult(name, BLOCKED, blockers)

    req = f.get("requirements") or {}
    comp = f.get("completeness") or {}
    ev = f.get("evidence") or {}

    axes = ["policy", "reviews", "reviewer_permissions", "head_sha_binding", "shared_head_prs"]
    if req.get("required_review_thread_resolution"):
        axes.append("review_threads")
    if req.get("require_code_owner_review"):
        axes += ["changed_paths", "codeowners_base_file", "codeowner_obligations"]
    if req.get("required_reviewers"):
        axes += ["changed_paths", "required_reviewer_pattern_semantics",
                 "required_team_membership", "required_team_obligations"]
    if req.get("require_last_push_approval"):
        axes += ["latest_reviewable_push"]
    if req.get("dismiss_stale_reviews_on_push"):
        # Server-derived reviewDecision (or an explicitly equivalent authoritative
        # field) is required because merge-base/diff changes can invalidate approval.
        axes += ["server_review_decision"]
    if req.get("copilot_extra_approval_may_apply"):
        axes += ["pr_author_attribution"]

    miss = _missing(comp, axes)
    if miss:
        return FamilyResult(name, UNKNOWN, [f"incomplete: {', '.join(miss)}"])

    # GitHub REST's PR-files list is capped at 3000 changed files. A wrapper that
    # paginates that endpoint is still incomplete above the service cap unless it
    # supplies a different authoritative complete source.
    if (ev.get("changed_paths_source") == "rest_pull_files"
            and isinstance(ev.get("changed_file_count"), int)
            and ev["changed_file_count"] > 3000):
        return FamilyResult(name, UNKNOWN, ["REST pull-files cap exceeded (3000)"])

    if req.get("dismiss_stale_reviews_on_push"):
        decision = ev.get("server_review_decision")
        if decision in {"CHANGES_REQUESTED", "REVIEW_REQUIRED"}:
            return FamilyResult(name, BLOCKED, [f"server_review_decision={decision}"])
        if decision != "APPROVED":
            return FamilyResult(name, UNKNOWN, ["server_review_decision not conclusively APPROVED"])

    if req.get("required_review_thread_resolution"):
        resolved = ev.get("all_required_threads_resolved")
        if resolved is False:
            return FamilyResult(name, BLOCKED, ["unresolved required review thread"])
        if resolved is not True:
            return FamilyResult(name, UNKNOWN, ["thread resolution result missing"])

    if req.get("require_code_owner_review"):
        sat = ev.get("codeowner_approvals_satisfied")
        if sat is False:
            return FamilyResult(name, BLOCKED, ["required code-owner approval missing"])
        if sat is not True:
            return FamilyResult(name, UNKNOWN, ["code-owner satisfaction missing"])

    if req.get("required_reviewers"):
        sat = ev.get("required_team_approvals_satisfied")
        if sat is False:
            return FamilyResult(name, BLOCKED, ["required reviewer-team approval missing"])
        if sat is not True:
            return FamilyResult(name, UNKNOWN, ["required reviewer-team satisfaction missing"])

    if req.get("require_last_push_approval"):
        sat = ev.get("last_push_approval_satisfied")
        if sat is False:
            return FamilyResult(name, BLOCKED, ["latest reviewable push lacks required independent approval"])
        if sat is not True:
            return FamilyResult(name, UNKNOWN, ["latest-push approval result missing"])

    if ev.get("same_head_blocker_absent") is False:
        return FamilyResult(name, BLOCKED, ["another open PR sharing the head has a blocking review"])
    if ev.get("same_head_blocker_absent") is not True:
        return FamilyResult(name, UNKNOWN, ["shared-head blocker state missing"])

    configured = req.get("required_approving_review_count", 0)
    if not isinstance(configured, int) or configured < 0:
        return FamilyResult(name, UNKNOWN, ["invalid configured approval count"])
    extra = 0
    if req.get("copilot_extra_approval_may_apply"):
        attribution = ev.get("pr_author_attribution")
        setting = ev.get("copilot_extra_approval_active")
        if setting is None:
            return FamilyResult(name, UNKNOWN, ["Copilot extra-approval setting unknown"])
        if setting is True and attribution == "copilot_unattributed":
            extra = 1
        elif attribution not in {"human", "copilot_attributed", "copilot_unattributed"}:
            return FamilyResult(name, UNKNOWN, ["PR author attribution unknown"])

    counted = ev.get("counted_current_authorized_approvals")
    if not isinstance(counted, int) or counted < 0:
        return FamilyResult(name, UNKNOWN, ["current authorized approval count missing"])
    need = configured + extra
    if counted < need:
        return FamilyResult(name, BLOCKED, [f"authorized approvals {counted} < required {need}"])
    return FamilyResult(name, PASS, [f"authorized approvals {counted} >= required {need}"])

def _merge_queue(f: dict[str, Any], document: dict[str, Any]) -> FamilyResult:
    name = "merge_queue"
    if f.get("applicable") is False:
        return FamilyResult(name, PASS, ["not applicable"])
    blockers = _definitive_blockers(f)
    if blockers:
        return FamilyResult(name, BLOCKED, blockers)
    comp = f.get("completeness") or {}
    ev = f.get("evidence") or {}
    stage = document.get("stage", "pre_enqueue")
    if stage == "pre_enqueue":
        # A queue-required branch necessarily has a later merge-group evidence stage.
        if not _b(comp, "policy"):
            return FamilyResult(name, UNKNOWN, ["merge-queue policy incomplete"])
        return FamilyResult(name, UNKNOWN, ["queue handoff / merge-group evidence still required"])
    miss = _missing(comp, ["policy", "enqueue_transaction", "merge_group_sha", "queue_state"])
    if miss:
        return FamilyResult(name, UNKNOWN, [f"incomplete: {', '.join(miss)}"])
    if ev.get("queue_failed") is True:
        return FamilyResult(name, BLOCKED, ["queue transaction failed"])
    if ev.get("queue_stage_satisfied") is True:
        return FamilyResult(name, PASS, ["queue stage satisfied"])
    return FamilyResult(name, UNKNOWN, ["queue stage not conclusively satisfied"])

def family_result(f: dict[str, Any], document: dict[str, Any]) -> FamilyResult:
    name = f.get("family")
    if name == "pull_request_reviews":
        return _reviews(f)
    if name == "required_status_checks":
        return _generic(f, ["policy", "head_sha_binding", "pagination", "app_provenance"],
                        "all_required_checks_satisfied")
    if name == "required_workflows":
        return _generic(f, ["policy", "target_sha_binding", "run_pagination", "workflow_identity"],
                        "all_required_workflows_satisfied")
    if name == "required_deployments":
        return _generic(f, ["policy", "endpoint", "target_sha_binding", "environment_identity",
                            "current_state"],
                        "all_required_deployments_succeeded")
    if name == "required_signatures":
        return _generic(f, ["policy", "update_range", "commit_enumeration", "verification"],
                        "all_commits_verified")
    if name == "code_scanning":
        return _generic(f, ["policy", "endpoint", "target_binding", "analysis_and_alerts"],
                        "rule_satisfied")
    if name == "code_quality":
        return _generic(f, ["policy", "endpoint", "target_binding", "findings"],
                        "rule_satisfied")
    if name == "code_coverage":
        return _generic(f, ["policy", "endpoint", "target_binding", "coverage_result"],
                        "rule_satisfied")
    if name == "merge_queue":
        return _merge_queue(f, document)
    return FamilyResult(str(name), UNKNOWN, ["unknown family"])

def verify(document: dict[str, Any]) -> dict[str, Any]:
    if document.get("schema_version") != 1:
        return {"verdict": OVERALL_UNKNOWN, "error": "unsupported schema_version"}
    meta = document.get("candidate") or {}
    if not meta.get("head_sha") or not _b(document.get("completeness") or {}, "policy_inventory"):
        return {"verdict": OVERALL_UNKNOWN, "error": "candidate head or policy inventory incomplete"}

    results = [family_result(f, document) for f in document.get("families", [])]
    if not results:
        return {"verdict": OVERALL_UNKNOWN, "error": "no policy families supplied"}

    if any(r.verdict == BLOCKED for r in results):
        overall = OVERALL_BLOCKED
    elif all(r.verdict == PASS for r in results):
        overall = OVERALL_READY
    else:
        overall = OVERALL_UNKNOWN
    return {
        "verdict": overall,
        "candidate_head_sha": meta["head_sha"],
        "stage": document.get("stage", "pre_enqueue"),
        "families": [{"family": r.family, "verdict": r.verdict, "reasons": r.reasons}
                     for r in results],
    }

def _fixture_doc(families: list[dict[str, Any]], stage: str = "pre_enqueue") -> dict[str, Any]:
    return {
        "schema_version": 1,
        "candidate": {"head_sha": "a" * 40},
        "stage": stage,
        "completeness": {"policy_inventory": True},
        "families": families,
    }

def self_test() -> dict[str, str]:
    fixtures: dict[str, tuple[dict[str, Any], str]] = {}

    fixtures["narrow_review_pass"] = (_fixture_doc([{
        "family": "pull_request_reviews",
        "applicable": True,
        "requirements": {"required_approving_review_count": 1},
        "completeness": {
            "policy": True, "reviews": True, "reviewer_permissions": True,
            "head_sha_binding": True, "shared_head_prs": True,
        },
        "evidence": {
            "same_head_blocker_absent": True,
            "counted_current_authorized_approvals": 1,
        },
    }]), OVERALL_READY)

    fixtures["team_membership_missing"] = (_fixture_doc([{
        "family": "pull_request_reviews",
        "applicable": True,
        "requirements": {
            "required_approving_review_count": 1,
            "required_reviewers": [{"team": 1}],
        },
        "completeness": {
            "policy": True, "reviews": True, "reviewer_permissions": True,
            "head_sha_binding": True, "shared_head_prs": True,
            "changed_paths": True, "required_reviewer_pattern_semantics": True,
            "required_team_membership": False, "required_team_obligations": True,
        },
        "evidence": {
            "same_head_blocker_absent": True,
            "counted_current_authorized_approvals": 1,
            "required_team_approvals_satisfied": True,
        },
    }]), OVERALL_UNKNOWN)

    fixtures["rest_pr_files_3001"] = (_fixture_doc([{
        "family": "pull_request_reviews",
        "applicable": True,
        "requirements": {
            "required_approving_review_count": 1,
            "require_code_owner_review": True,
        },
        "completeness": {
            "policy": True, "reviews": True, "reviewer_permissions": True,
            "head_sha_binding": True, "shared_head_prs": True,
            "changed_paths": True, "codeowners_base_file": True,
            "codeowner_obligations": True,
        },
        "evidence": {
            "same_head_blocker_absent": True,
            "counted_current_authorized_approvals": 2,
            "codeowner_approvals_satisfied": True,
            "changed_paths_source": "rest_pull_files",
            "changed_file_count": 3001,
        },
    }]), OVERALL_UNKNOWN)

    fixtures["copilot_extra_approval"] = (_fixture_doc([{
        "family": "pull_request_reviews",
        "applicable": True,
        "requirements": {
            "required_approving_review_count": 1,
            "copilot_extra_approval_may_apply": True,
        },
        "completeness": {
            "policy": True, "reviews": True, "reviewer_permissions": True,
            "head_sha_binding": True, "shared_head_prs": True,
            "pr_author_attribution": True,
        },
        "evidence": {
            "same_head_blocker_absent": True,
            "counted_current_authorized_approvals": 1,
            "copilot_extra_approval_active": True,
            "pr_author_attribution": "copilot_unattributed",
        },
    }]), OVERALL_BLOCKED)

    fixtures["stale_review_server_decision"] = (_fixture_doc([{
        "family": "pull_request_reviews",
        "applicable": True,
        "requirements": {
            "required_approving_review_count": 1,
            "dismiss_stale_reviews_on_push": True,
        },
        "completeness": {
            "policy": True, "reviews": True, "reviewer_permissions": True,
            "head_sha_binding": True, "shared_head_prs": True,
            "server_review_decision": True,
        },
        "evidence": {
            "same_head_blocker_absent": True,
            "counted_current_authorized_approvals": 1,
            "server_review_decision": "REVIEW_REQUIRED",
        },
    }]), OVERALL_BLOCKED)

    fixtures["shared_head_blocker"] = (_fixture_doc([{
        "family": "pull_request_reviews",
        "applicable": True,
        "requirements": {"required_approving_review_count": 1},
        "completeness": {
            "policy": True, "reviews": True, "reviewer_permissions": True,
            "head_sha_binding": True, "shared_head_prs": True,
        },
        "evidence": {
            "same_head_blocker_absent": False,
            "counted_current_authorized_approvals": 1,
        },
    }]), OVERALL_BLOCKED)

    fixtures["deployment_endpoint_missing"] = (_fixture_doc([{
        "family": "required_deployments",
        "applicable": True,
        "completeness": {
            "policy": True, "endpoint": False, "target_sha_binding": True,
            "environment_identity": True, "current_state": False,
        },
        "evidence": {"all_required_deployments_succeeded": True},
    }]), OVERALL_UNKNOWN)

    fixtures["queue_pre_enqueue"] = (_fixture_doc([{
        "family": "merge_queue",
        "applicable": True,
        "completeness": {"policy": True},
        "evidence": {},
    }]), OVERALL_UNKNOWN)

    observed: dict[str, str] = {}
    for name, (doc, expected) in fixtures.items():
        got = verify(doc)["verdict"]
        if got != expected:
            raise AssertionError(f"{name}: expected {expected}, got {got}")
        observed[name] = got
    return observed

def main() -> int:
    if len(sys.argv) > 1 and sys.argv[1] == "--self-test":
        print(json.dumps(self_test(), indent=2, sort_keys=True))
        return 0
    doc = json.load(sys.stdin)
    print(json.dumps(verify(doc), indent=2, sort_keys=True))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
