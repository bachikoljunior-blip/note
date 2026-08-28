#!/usr/bin/env python3
"""Fail-closed reconciliation from GitHub merge evidence to Rule Suite after_sha.

The helper separates an actual landed-effect SHA from causal attribution.  For
required-workflow Rule Suite reconciliation, the actual exact ref-update SHA is
what matters.  An ambiguous request can therefore become policy-verifiable if
a later authoritative PR read proves the PR merged to M, even when it cannot
prove which actor/request performed the merge.

Merge-queue / stacked operations are deliberately stricter: one terminal OID
is not assumed to cover every rule evaluation or merge group without explicit
coverage evidence.
"""
from __future__ import annotations
import json, sys

PASS = "PASS"
BLOCKED = "BLOCKED"
UNKNOWN = "UNKNOWN"


def derive_effect(doc):
    intent = doc.get("intent") or {}
    obs = doc.get("observations") or {}
    mode = intent.get("mode")

    if mode == "sync":
        r = obs.get("sync_merge_response") or {}
        if r.get("http_status") == 200 and r.get("merged") is True and r.get("sha"):
            return {
                "state": "EXACT_EFFECT_SHA",
                "sha": r["sha"],
                "source": "sync_merge_200",
                "caused_by_this_request": True,
            }
        pr = obs.get("post_pr_read") or {}
        if (
            pr.get("merged") is True
            and pr.get("merge_commit_sha")
            and obs.get("pre_pr_open_at_expected_head") is True
        ):
            return {
                "state": "EXACT_EFFECT_SHA",
                "sha": pr["merge_commit_sha"],
                "source": "post_merge_pr_read_after_ambiguous_sync_request",
                "caused_by_this_request": None,
            }
        return {"state": UNKNOWN, "reason": "no exact landed SHA"}

    if mode == "async":
        checkpoint = obs.get("async_intent_checkpoint") or {}
        result = obs.get("async_result") or {}
        if checkpoint.get("uuid") != result.get("uuid"):
            return {"state": UNKNOWN, "reason": "async result UUID not bound to checkpointed intent"}
        if checkpoint.get("expected_head_sha") != intent.get("expected_head_sha"):
            return {"state": UNKNOWN, "reason": "checkpointed expected head differs from intent"}
        if checkpoint.get("merge_method") != intent.get("merge_method"):
            return {"state": UNKNOWN, "reason": "checkpointed merge method differs from intent"}
        if checkpoint.get("merge_action") != intent.get("merge_action"):
            return {"state": UNKNOWN, "reason": "checkpointed merge action differs from intent"}

        if result.get("status") == "merged" and result.get("sha"):
            return {
                "state": "EXACT_EFFECT_SHA",
                "sha": result["sha"],
                "source": "terminal_async_result",
                "caused_by_this_request": True,
            }
        if result.get("status") == "pending":
            return {"state": UNKNOWN, "reason": "async merge still pending"}
        if result.get("status") == "failed":
            return {"state": UNKNOWN,
                    "reason": "failed async result has no documented exact ref-update SHA binding"}
        if result.get("status") == "expired_or_404":
            pr = obs.get("post_pr_read") or {}
            if (
                pr.get("merged") is True
                and pr.get("merge_commit_sha")
                and obs.get("pre_pr_open_at_expected_head") is True
            ):
                return {
                    "state": "EXACT_EFFECT_SHA",
                    "sha": pr["merge_commit_sha"],
                    "source": "post_merge_pr_read_after_expired_async_result",
                    "caused_by_this_request": None,
                }
        return {"state": UNKNOWN, "reason": "no exact terminal async effect SHA"}

    return {"state": UNKNOWN, "reason": "unsupported merge mode"}


def reconcile_required_workflows(doc):
    effect = derive_effect(doc)
    if effect.get("state") != "EXACT_EFFECT_SHA":
        return {"verdict": UNKNOWN, "effect": effect,
                "reason": "required-workflow Rule Suite cannot be effect-bound"}

    intent = doc.get("intent") or {}
    if intent.get("merge_action") == "merge_queue" or intent.get("stack_member_count", 1) > 1:
        if (doc.get("observations") or {}).get("rule_suite_coverage_complete") is not True:
            return {
                "verdict": UNKNOWN,
                "effect": effect,
                "reason": "queue/stack result is not proven to map to complete Rule Suite coverage",
            }

    suite = (doc.get("observations") or {}).get("rule_suite") or {}
    base_ref = intent.get("base_ref")
    if suite.get("ref") != base_ref or suite.get("after_sha") != effect.get("sha"):
        return {"verdict": UNKNOWN, "effect": effect,
                "reason": "Rule Suite ref/after_sha does not match exact landed effect"}

    ruleset_id = intent.get("ruleset_id")
    evaluations = suite.get("rule_evaluations")
    if not isinstance(evaluations, list):
        return {"verdict": UNKNOWN, "effect": effect,
                "reason": "Rule Suite detail missing"}
    matches = []
    for ev in evaluations:
        if not isinstance(ev, dict):
            continue
        source = ev.get("rule_source") or {}
        if (
            ev.get("rule_type") == "workflows"
            and ev.get("enforcement") == "active"
            and source.get("type") == "ruleset"
            and source.get("id") == ruleset_id
        ):
            matches.append(ev)
    if not matches:
        return {"verdict": UNKNOWN, "effect": effect,
                "reason": "applicable active workflows evaluation absent"}
    results = {ev.get("result") for ev in matches}
    if "fail" in results:
        return {"verdict": BLOCKED, "effect": effect,
                "reason": "required-workflow evaluation failed on exact effect"}
    if results == {"pass"}:
        return {"verdict": PASS, "effect": effect,
                "reason": "required-workflow evaluation passed on exact effect"}
    return {"verdict": UNKNOWN, "effect": effect,
            "reason": "workflows evaluation is not pass/fail"}


def base(mode="sync"):
    return {
        "intent": {
            "mode": mode,
            "expected_head_sha": "h" * 40,
            "merge_method": "squash",
            "merge_action": "direct_merge",
            "base_ref": "refs/heads/main",
            "ruleset_id": 42,
            "stack_member_count": 1,
        },
        "observations": {
            "pre_pr_open_at_expected_head": True,
            "rule_suite": {
                "ref": "refs/heads/main", "after_sha": "m" * 40,
                "rule_evaluations": [{
                    "rule_source": {"type": "ruleset", "id": 42},
                    "enforcement": "active", "result": "pass",
                    "rule_type": "workflows",
                }],
            },
        },
    }


def self_test():
    sync = base("sync")
    sync["observations"]["sync_merge_response"] = {
        "http_status": 200, "merged": True, "sha": "m" * 40}
    assert reconcile_required_workflows(sync)["verdict"] == PASS

    ambiguous = base("sync")
    ambiguous["observations"]["post_pr_read"] = {
        "merged": True, "merge_commit_sha": "m" * 40}
    out = reconcile_required_workflows(ambiguous)
    assert out["verdict"] == PASS
    assert out["effect"]["caused_by_this_request"] is None

    async_ok = base("async")
    async_ok["observations"]["async_intent_checkpoint"] = {
        "uuid": "u", "expected_head_sha": "h" * 40,
        "merge_method": "squash", "merge_action": "direct_merge"}
    async_ok["observations"]["async_result"] = {
        "uuid": "u", "status": "merged", "sha": "m" * 40}
    assert reconcile_required_workflows(async_ok)["verdict"] == PASS

    async_bad_uuid = json.loads(json.dumps(async_ok))
    async_bad_uuid["observations"]["async_result"]["uuid"] = "other"
    assert reconcile_required_workflows(async_bad_uuid)["verdict"] == UNKNOWN

    queue = json.loads(json.dumps(async_ok))
    queue["intent"]["merge_action"] = "merge_queue"
    queue["observations"]["async_intent_checkpoint"]["merge_action"] = "merge_queue"
    assert reconcile_required_workflows(queue)["verdict"] == UNKNOWN
    queue["observations"]["rule_suite_coverage_complete"] = True
    assert reconcile_required_workflows(queue)["verdict"] == PASS

    failed = json.loads(json.dumps(async_ok))
    failed["observations"]["async_result"] = {"uuid": "u", "status": "failed"}
    assert reconcile_required_workflows(failed)["verdict"] == UNKNOWN

    return {
        "sync_200_exact_sha": PASS,
        "ambiguous_sync_recovered_actual_effect": PASS,
        "async_terminal_exact_sha": PASS,
        "async_uuid_mismatch": UNKNOWN,
        "queue_without_complete_suite_mapping": UNKNOWN,
        "queue_with_explicit_complete_suite_mapping": PASS,
        "async_failure_without_effect_sha": UNKNOWN,
    }


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        print(json.dumps(self_test(), indent=2, sort_keys=True))
    else:
        print(json.dumps(reconcile_required_workflows(json.load(sys.stdin)), indent=2, sort_keys=True))
