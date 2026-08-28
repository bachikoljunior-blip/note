#!/usr/bin/env python3
"""GitHub merge/effect + Rule Suite reconciler, Phase-1 V2.

Fail-closed invariants:
- Pre-merge policy/auth observations are planning evidence, never reusable leases.
- Async merge intent is bound only by expected head + method + action. A 409
  existing UUID may be adopted only when the polled pending details match.
- `enqueued` is queue admission, not a landed base-branch effect.
- Final effect proof is an exact target-ref transition chain.
- Rule Suite proof must cover that exact transition chain edge-for-edge using
  ref + before_sha + after_sha. `bypass` is not `pass`.
- `evaluation_result` is kept separate from active enforcement result.
"""
from __future__ import annotations
import json
import sys
from collections import defaultdict

PASS = "PASS"
BLOCKED = "BLOCKED"
UNKNOWN = "UNKNOWN"
BYPASS = "BYPASS"

REQUEST_PENDING_INTENT_BOUND = "REQUEST_PENDING_INTENT_BOUND"
REQUEST_PENDING_EQUIVALENT_INTENT = "REQUEST_PENDING_EQUIVALENT_INTENT"
QUEUE_ADMITTED_NOT_FINAL = "QUEUE_ADMITTED_NOT_FINAL"
DIRECT_EFFECT_EXACT = "DIRECT_EFFECT_EXACT"
FINAL_BASE_EFFECT_EXACT = "FINAL_BASE_EFFECT_EXACT"
ACTUAL_EFFECT_CAUSALITY_UNKNOWN = "ACTUAL_EFFECT_CAUSALITY_UNKNOWN"
PROVED_NO_EFFECT_FOR_BOUND_ASYNC_REQUEST = "PROVED_NO_EFFECT_FOR_BOUND_ASYNC_REQUEST"


def _pending_matches_intent(intent, details):
    return all(
        details.get(k) == intent.get(k)
        for k in ("expected_head_sha", "merge_method", "merge_action")
    )


def derive_async_request_state(doc):
    intent = doc.get("intent") or {}
    obs = doc.get("observations") or {}
    result = obs.get("async_result") or {}
    status = result.get("status")
    details = result.get("details") or {}
    checkpoint = obs.get("async_intent_checkpoint") or {}
    submission_status = obs.get("async_submission_http_status")

    if status == "pending":
        uuid = details.get("uuid")
        if not uuid:
            return {"state": UNKNOWN, "reason": "pending result missing details.uuid"}
        if not _pending_matches_intent(intent, details):
            return {
                "state": UNKNOWN,
                "reason": "existing/pending request options differ from current intent",
                "uuid": uuid,
            }
        if checkpoint:
            if checkpoint.get("uuid") != uuid:
                return {"state": UNKNOWN, "reason": "pending UUID differs from checkpoint"}
            for k in ("expected_head_sha", "merge_method", "merge_action"):
                if checkpoint.get(k) != intent.get(k):
                    return {"state": UNKNOWN, "reason": f"checkpoint {k} differs from intent"}
            return {
                "state": REQUEST_PENDING_INTENT_BOUND,
                "uuid": uuid,
                "caused_by_this_request": True,
            }
        if submission_status == 409:
            return {
                "state": REQUEST_PENDING_EQUIVALENT_INTENT,
                "uuid": uuid,
                "caused_by_this_request": None,
                "reason": "existing request has equivalent pending intent; do not blind-retry",
            }
        return {
            "state": UNKNOWN,
            "reason": "pending intent matches, but no durable UUID checkpoint or 409 recovery context",
        }

    lookup_uuid = obs.get("async_lookup_uuid")
    terminal_bound = bool(checkpoint and lookup_uuid and checkpoint.get("uuid") == lookup_uuid)

    if status == "merged":
        if not (details.get("sha") and terminal_bound):
            return {
                "state": UNKNOWN,
                "reason": "terminal merged result lacks details.sha or durable lookup-UUID binding",
            }
        return {
            "state": DIRECT_EFFECT_EXACT,
            "sha": details["sha"],
            "caused_by_this_request": True,
            "uuid": lookup_uuid,
        }

    if status == "enqueued":
        if not terminal_bound:
            return {
                "state": QUEUE_ADMITTED_NOT_FINAL,
                "caused_by_this_request": None,
                "reason": "queue admission observed but not bound to checkpointed async request",
            }
        return {
            "state": QUEUE_ADMITTED_NOT_FINAL,
            "caused_by_this_request": True,
            "uuid": lookup_uuid,
        }

    if status == "failed":
        if terminal_bound:
            return {
                "state": PROVED_NO_EFFECT_FOR_BOUND_ASYNC_REQUEST,
                "caused_by_this_request": True,
                "uuid": lookup_uuid,
                "reason": details.get("message"),
            }
        return {
            "state": BLOCKED,
            "reason": "failed result observed without durable lookup-UUID binding",
        }

    if status == "expired_or_404":
        pr = obs.get("post_pr_read") or {}
        if (
            pr.get("merged") is True
            and pr.get("merge_commit_sha")
            and obs.get("pre_pr_open_at_expected_head") is True
        ):
            return {
                "state": ACTUAL_EFFECT_CAUSALITY_UNKNOWN,
                "sha": pr["merge_commit_sha"],
                "caused_by_this_request": None,
                "reason": "async result expired; actual merge recovered from PR state only",
            }
        return {
            "state": UNKNOWN,
            "reason": "24h async result expired and no exact effect recovery",
        }

    return {"state": UNKNOWN, "reason": "unknown/missing async status"}


def derive_request_state(doc):
    intent = doc.get("intent") or {}
    obs = doc.get("observations") or {}
    if intent.get("mode") == "sync":
        r = obs.get("sync_merge_response") or {}
        if r.get("http_status") == 200 and r.get("merged") is True and r.get("sha"):
            return {
                "state": DIRECT_EFFECT_EXACT,
                "sha": r["sha"],
                "caused_by_this_request": True,
            }
        pr = obs.get("post_pr_read") or {}
        if (
            pr.get("merged") is True
            and pr.get("merge_commit_sha")
            and obs.get("pre_pr_open_at_expected_head") is True
        ):
            return {
                "state": ACTUAL_EFFECT_CAUSALITY_UNKNOWN,
                "sha": pr["merge_commit_sha"],
                "caused_by_this_request": None,
                "reason": "actual merge recovered after ambiguous sync response",
            }
        return {"state": UNKNOWN, "reason": "no exact sync effect evidence"}
    if intent.get("mode") == "async":
        return derive_async_request_state(doc)
    return {"state": UNKNOWN, "reason": "unsupported merge mode"}


def _validate_transition_chain(intent, chain, expected_final_sha=None):
    if not isinstance(chain, list) or not chain:
        return None, "target-ref transition chain absent"
    base_ref = intent.get("base_ref")
    initial = intent.get("base_before_sha")
    if not (base_ref and initial):
        return None, "intent missing base_ref/base_before_sha"

    prev = initial
    normalized = []
    for i, edge in enumerate(chain):
        if not isinstance(edge, dict):
            return None, f"transition edge {i} not an object"
        if edge.get("ref") != base_ref:
            return None, f"transition edge {i} ref mismatch"
        if edge.get("before_sha") != prev:
            return None, f"transition edge {i} does not continue previous after_sha"
        after = edge.get("after_sha")
        if not after or after == edge.get("before_sha"):
            return None, f"transition edge {i} missing/non-advancing after_sha"
        normalized.append({
            "ref": base_ref,
            "before_sha": edge["before_sha"],
            "after_sha": after,
        })
        prev = after
    if expected_final_sha and prev != expected_final_sha:
        return None, "final target-ref SHA differs from merge result SHA"
    return normalized, None


def derive_final_effect(doc):
    intent = doc.get("intent") or {}
    obs = doc.get("observations") or {}
    req = derive_request_state(doc)

    if req.get("state") in (PROVED_NO_EFFECT_FOR_BOUND_ASYNC_REQUEST, BLOCKED):
        return req

    chain = obs.get("base_ref_transition_chain")
    if req.get("state") in (DIRECT_EFFECT_EXACT, ACTUAL_EFFECT_CAUSALITY_UNKNOWN):
        normalized, err = _validate_transition_chain(intent, chain, req.get("sha"))
        if err:
            return {"state": UNKNOWN, "reason": err, "request": req}
        return {
            "state": FINAL_BASE_EFFECT_EXACT,
            "ref": intent["base_ref"],
            "initial_sha": normalized[0]["before_sha"],
            "final_sha": normalized[-1]["after_sha"],
            "transitions": normalized,
            "caused_by_this_request": req.get("caused_by_this_request"),
            "request_state": req.get("state"),
        }

    if req.get("state") == QUEUE_ADMITTED_NOT_FINAL:
        completion = obs.get("queue_completion") or {}
        if completion.get("all_intended_prs_merged") is not True:
            return {
                "state": UNKNOWN,
                "reason": "queue admission is terminal for async request but not final merge outcome",
                "request": req,
            }
        final_sha = completion.get("base_final_sha")
        normalized, err = _validate_transition_chain(intent, chain, final_sha)
        if err:
            return {"state": UNKNOWN, "reason": err, "request": req}
        if completion.get("member_vector_fingerprint") != intent.get("member_vector_fingerprint"):
            return {
                "state": UNKNOWN,
                "reason": "queue completion not bound to checkpointed stack/member vector",
                "request": req,
            }
        return {
            "state": FINAL_BASE_EFFECT_EXACT,
            "ref": intent["base_ref"],
            "initial_sha": normalized[0]["before_sha"],
            "final_sha": normalized[-1]["after_sha"],
            "transitions": normalized,
            "caused_by_this_request": req.get("caused_by_this_request"),
            "request_state": req.get("state"),
            "queue_groups_observed": len(normalized),
        }

    return {"state": UNKNOWN, "reason": req.get("reason"), "request": req}


def _suite_key(s):
    return (s.get("ref"), s.get("before_sha"), s.get("after_sha"))


def reconcile_rule_suites(doc):
    effect = derive_final_effect(doc)
    if effect.get("state") == PROVED_NO_EFFECT_FOR_BOUND_ASYNC_REQUEST:
        return {
            "verdict": BLOCKED,
            "effect": effect,
            "policy_state": "NO_EFFECT_FOR_BOUND_ASYNC_REQUEST",
        }
    if effect.get("state") != FINAL_BASE_EFFECT_EXACT:
        return {
            "verdict": UNKNOWN,
            "effect": effect,
            "policy_state": "NO_EXACT_FINAL_EFFECT",
        }

    suites = (doc.get("observations") or {}).get("rule_suites")
    if not isinstance(suites, list):
        return {
            "verdict": UNKNOWN,
            "effect": effect,
            "policy_state": "RULE_SUITE_COVERAGE_MISSING",
        }

    by_key = defaultdict(list)
    for s in suites:
        if isinstance(s, dict):
            by_key[_suite_key(s)].append(s)

    matched = []
    for edge in effect["transitions"]:
        key = (edge["ref"], edge["before_sha"], edge["after_sha"])
        candidates = by_key.get(key, [])
        if len(candidates) != 1:
            return {
                "verdict": UNKNOWN,
                "effect": effect,
                "policy_state": "RULE_SUITE_COVERAGE_AMBIGUOUS_OR_MISSING",
                "reason": f"expected exactly one Rule Suite for transition {key}, got {len(candidates)}",
            }
        matched.append(candidates[0])

    active_results = [s.get("result") for s in matched]
    evaluate_fail_ids = [
        s.get("id") for s in matched if s.get("evaluation_result") == "fail"
    ]

    if any(r == "fail" for r in active_results):
        return {
            "verdict": UNKNOWN,
            "effect": effect,
            "policy_state": "SERVER_EVIDENCE_CONFLICT",
            "matched_suite_ids": [s.get("id") for s in matched],
            "evaluate_fail_suite_ids": evaluate_fail_ids,
        }

    if any(r not in ("pass", "bypass") for r in active_results):
        return {
            "verdict": UNKNOWN,
            "effect": effect,
            "policy_state": "RULE_SUITE_RESULT_UNKNOWN",
            "matched_suite_ids": [s.get("id") for s in matched],
            "evaluate_fail_suite_ids": evaluate_fail_ids,
        }

    if "bypass" in active_results:
        return {
            "verdict": BYPASS,
            "effect": effect,
            "policy_state": "ACTIVE_RULES_BYPASS_EXACT_EFFECT_CHAIN",
            "matched_suite_ids": [s.get("id") for s in matched],
            "evaluate_fail_suite_ids": evaluate_fail_ids,
            "reason": "at least one landed transition used active-rule bypass; do not classify as policy pass",
        }

    return {
        "verdict": PASS,
        "effect": effect,
        "policy_state": "ACTIVE_RULES_PASS_EXACT_EFFECT_CHAIN",
        "matched_suite_ids": [s.get("id") for s in matched],
        "evaluate_fail_suite_ids": evaluate_fail_ids,
        "evaluate_warning": "EVALUATE_WOULD_FAIL_IF_ACTIVE" if evaluate_fail_ids else None,
    }


def base(mode="async"):
    return {
        "intent": {
            "mode": mode,
            "expected_head_sha": "h" * 40,
            "merge_method": "squash",
            "merge_action": "direct_merge",
            "base_ref": "refs/heads/main",
            "base_before_sha": "b" * 40,
            "member_vector_fingerprint": "vector-v1",
        },
        "observations": {
            "pre_pr_open_at_expected_head": True,
            "base_ref_transition_chain": [{
                "ref": "refs/heads/main",
                "before_sha": "b" * 40,
                "after_sha": "m" * 40,
            }],
            "rule_suites": [{
                "id": 1,
                "ref": "refs/heads/main",
                "before_sha": "b" * 40,
                "after_sha": "m" * 40,
                "result": "pass",
                "evaluation_result": "pass",
            }],
        },
    }


def checkpoint(doc, uuid="u"):
    doc["observations"]["async_intent_checkpoint"] = {
        "uuid": uuid,
        "expected_head_sha": doc["intent"]["expected_head_sha"],
        "merge_method": doc["intent"]["merge_method"],
        "merge_action": doc["intent"]["merge_action"],
    }


def self_test():
    o = {}

    sync = base("sync")
    sync["observations"]["sync_merge_response"] = {
        "http_status": 200, "merged": True, "sha": "m" * 40}
    assert reconcile_rule_suites(sync)["verdict"] == PASS
    o["sync_exact_single_transition"] = PASS

    pending = base()
    checkpoint(pending)
    pending["observations"]["async_result"] = {
        "status": "pending",
        "details": {
            "uuid": "u",
            "merge_method": "squash",
            "merge_action": "direct_merge",
            "expected_head_sha": "h" * 40,
        },
    }
    assert derive_request_state(pending)["state"] == REQUEST_PENDING_INTENT_BOUND
    o["pending_checkpoint_bound"] = PASS

    mismatch = json.loads(json.dumps(pending))
    mismatch["observations"]["async_result"]["details"]["merge_action"] = "merge_queue"
    assert derive_request_state(mismatch)["state"] == UNKNOWN
    o["pending_option_mismatch"] = PASS

    recovered409 = base()
    recovered409["observations"]["async_submission_http_status"] = 409
    recovered409["observations"]["async_result"] = json.loads(json.dumps(
        pending["observations"]["async_result"]))
    assert derive_request_state(recovered409)["state"] == REQUEST_PENDING_EQUIVALENT_INTENT
    o["409_equivalent_intent_adopt"] = PASS

    merged = base()
    checkpoint(merged)
    merged["observations"]["async_lookup_uuid"] = "u"
    merged["observations"]["async_result"] = {
        "status": "merged", "details": {"sha": "m" * 40}}
    assert reconcile_rule_suites(merged)["verdict"] == PASS
    o["async_merged_nested_sha"] = PASS

    oldshape = json.loads(json.dumps(merged))
    oldshape["observations"]["async_result"] = {
        "status": "merged", "sha": "m" * 40}
    assert derive_request_state(oldshape)["state"] == UNKNOWN
    o["reject_old_top_level_sha"] = PASS

    wrongbefore = json.loads(json.dumps(merged))
    wrongbefore["observations"]["rule_suites"][0]["before_sha"] = "x" * 40
    assert reconcile_rule_suites(wrongbefore)["verdict"] == UNKNOWN
    o["suite_wrong_before"] = PASS

    bypass = json.loads(json.dumps(merged))
    bypass["observations"]["rule_suites"][0]["result"] = "bypass"
    assert reconcile_rule_suites(bypass)["verdict"] == BYPASS
    o["bypass_not_pass"] = PASS

    evalfail = json.loads(json.dumps(merged))
    evalfail["observations"]["rule_suites"][0]["evaluation_result"] = "fail"
    e = reconcile_rule_suites(evalfail)
    assert e["verdict"] == PASS and e["evaluate_warning"] == "EVALUATE_WOULD_FAIL_IF_ACTIVE"
    o["evaluate_result_separate"] = PASS

    queued = base()
    queued["intent"]["merge_action"] = "merge_queue"
    checkpoint(queued)
    queued["observations"]["async_lookup_uuid"] = "u"
    queued["observations"]["async_result"] = {
        "status": "enqueued", "details": {"message": "added"}}
    assert derive_final_effect(queued)["state"] == UNKNOWN
    o["enqueued_not_landed"] = PASS

    qdone = json.loads(json.dumps(queued))
    qdone["observations"]["queue_completion"] = {
        "all_intended_prs_merged": True,
        "base_final_sha": "m" * 40,
        "member_vector_fingerprint": "vector-v1",
    }
    assert reconcile_rule_suites(qdone)["verdict"] == PASS
    o["queue_final_single_group"] = PASS

    qsplit = json.loads(json.dumps(qdone))
    qsplit["observations"]["base_ref_transition_chain"] = [
        {"ref": "refs/heads/main", "before_sha": "b" * 40, "after_sha": "c" * 40},
        {"ref": "refs/heads/main", "before_sha": "c" * 40, "after_sha": "m" * 40},
    ]
    qsplit["observations"]["rule_suites"] = [
        {"id": 10, "ref": "refs/heads/main", "before_sha": "b" * 40,
         "after_sha": "c" * 40, "result": "pass", "evaluation_result": "pass"},
        {"id": 11, "ref": "refs/heads/main", "before_sha": "c" * 40,
         "after_sha": "m" * 40, "result": "pass", "evaluation_result": "pass"},
    ]
    assert reconcile_rule_suites(qsplit)["verdict"] == PASS
    o["queue_split_complete_suite_chain"] = PASS

    qgap = json.loads(json.dumps(qsplit))
    qgap["observations"]["rule_suites"] = qgap["observations"]["rule_suites"][1:]
    assert reconcile_rule_suites(qgap)["verdict"] == UNKNOWN
    o["queue_split_missing_suite_edge"] = PASS

    failed = base()
    checkpoint(failed)
    failed["observations"]["async_lookup_uuid"] = "u"
    failed["observations"]["async_result"] = {
        "status": "failed", "details": {"message": "rule failed"}}
    assert derive_request_state(failed)["state"] == PROVED_NO_EFFECT_FOR_BOUND_ASYNC_REQUEST
    assert reconcile_rule_suites(failed)["verdict"] == BLOCKED
    o["bound_failed_no_request_effect"] = PASS

    expired = base()
    checkpoint(expired)
    expired["observations"]["async_result"] = {
        "status": "expired_or_404", "details": {}}
    expired["observations"]["post_pr_read"] = {
        "merged": True, "merge_commit_sha": "m" * 40}
    x = reconcile_rule_suites(expired)
    assert x["verdict"] == PASS
    assert x["effect"]["caused_by_this_request"] is None
    o["expired_actual_effect_causality_unknown"] = PASS

    return o


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        print(json.dumps(self_test(), indent=2, sort_keys=True))
    else:
        print(json.dumps(reconcile_rule_suites(json.load(sys.stdin)), indent=2, sort_keys=True))
