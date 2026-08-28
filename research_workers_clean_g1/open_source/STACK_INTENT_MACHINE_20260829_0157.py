#!/usr/bin/env python3
"""Pure state reconciler for durable GitHub stacked-PR async-merge intent.

No network calls. It distinguishes the API's requested-top expected SHA from
the client's full ordered member snapshot and fails closed on ambiguous states.
"""
from __future__ import annotations
import json, sys

READY = "READY_TO_SUBMIT"
RESUME = "RESUME"
CONFLICT = "CONFLICT"
UNKNOWN = "UNKNOWN"
QUEUE_OK = "QUEUE_EVIDENCE_OK"
MERGED_OK = "MERGED_EVIDENCE_OK"
EXPIRED_UNKNOWN = "EXPIRED_UNKNOWN"

def _member_key(m):
    return (m.get("pr_number"), m.get("position"), m.get("head_sha"),
            m.get("direct_base_ref"), m.get("direct_base_sha"))

def intended_group(capsule):
    members = capsule["stack"]["members"]
    requested = capsule["requested"]["pr_number"]
    out = []
    for m in members:
        out.append(m["pr_number"])
        if m["pr_number"] == requested:
            return out
    raise ValueError("requested PR is not in member vector")

def same_snapshot(capsule, observed):
    stack = capsule["stack"]
    if observed.get("number") != stack.get("number"):
        return False, "stack number drift"
    if observed.get("base_ref") != stack.get("base_ref"):
        return False, "stack base ref drift"
    if observed.get("base_sha") != stack.get("base_sha"):
        return False, "stack base sha drift"
    expected = [_member_key(x) for x in stack.get("members", [])]
    actual = [_member_key(x) for x in observed.get("members", [])]
    if actual != expected:
        return False, "ordered member/head/base vector drift"
    return True, "exact stack snapshot"

def same_request(capsule, request):
    return (
        request.get("expected_head_sha") == capsule["requested"]["expected_head_sha"]
        and request.get("merge_method") == capsule["merge_method"]
        and request.get("merge_action") == capsule["merge_action"]
    )

def reconcile(capsule, observation):
    state = capsule.get("state")
    if state == "STACK_SNAPSHOT":
        ok, reason = same_snapshot(capsule, observation.get("stack") or {})
        return {"verdict": READY if ok else CONFLICT, "reason": reason}

    if state == "SUBMIT_UNKNOWN":
        recovered = observation.get("recoverable_async_request")
        if recovered is None:
            return {"verdict": UNKNOWN,
                    "reason": "no exact recoverable request identity; blind retry is unsafe"}
        if same_request(capsule, recovered):
            return {"verdict": RESUME, "uuid": recovered.get("uuid"),
                    "reason": "matching async request recovered"}
        return {"verdict": CONFLICT, "reason": "recovered async request identity mismatches intent"}

    if state in {"ACCEPTED_U", "EXISTING_U_MATCH", "PENDING"}:
        result = observation.get("async_result")
        if observation.get("result_not_found_after_retention") is True:
            return {"verdict": EXPIRED_UNKNOWN,
                    "reason": "async result expired; 404 does not prove no request existed"}
        if not isinstance(result, dict):
            return {"verdict": UNKNOWN, "reason": "async result missing"}
        if not same_request(capsule, result):
            return {"verdict": CONFLICT, "reason": "pending/result request identity mismatch"}
        status = result.get("status")
        if status in {None, "pending", "in_progress"}:
            return {"verdict": RESUME, "uuid": result.get("uuid"),
                    "reason": "matching async request still pending"}
        if status == "failed":
            return {"verdict": "FAILED", "reason": str(result.get("failure_reason") or "async merge failed")}
        if status == "merged":
            return reconcile({**capsule, "state":"MERGED"}, observation)
        if status == "queued":
            return reconcile({**capsule, "state":"QUEUED"}, observation)
        return {"verdict": UNKNOWN, "reason": f"unrecognized async status {status!r}"}

    if state == "QUEUED":
        groups = observation.get("merge_groups")
        if not isinstance(groups, list) or not groups:
            return {"verdict": UNKNOWN, "reason": "merge-group evidence missing"}
        flattened = []
        seen_shas = set()
        for g in groups:
            sha = g.get("sha")
            prs = g.get("member_pr_numbers")
            if not isinstance(sha, str) or len(sha) != 40 or sha in seen_shas:
                return {"verdict": UNKNOWN, "reason": "invalid/duplicate merge-group SHA evidence"}
            seen_shas.add(sha)
            if not isinstance(prs, list) or not all(isinstance(x, int) for x in prs):
                return {"verdict": UNKNOWN, "reason": "merge-group membership incomplete"}
            flattened.extend(prs)
        wanted = intended_group(capsule)
        if flattened != wanted:
            return {"verdict": CONFLICT,
                    "reason": f"merge groups cover {flattened}, expected contiguous stack group {wanted}"}
        return {"verdict": QUEUE_OK, "merge_group_count": len(groups),
                "reason": "ordered merge groups exactly cover intended stack group"}

    if state == "MERGED":
        merged = observation.get("merged_pr_numbers")
        wanted = intended_group(capsule)
        if not isinstance(merged, list):
            return {"verdict": UNKNOWN, "reason": "terminal member states missing"}
        if merged != wanted:
            return {"verdict": CONFLICT, "reason": f"merged members {merged}, expected {wanted}"}
        oid = observation.get("terminal_merge_commit_oid")
        if not isinstance(oid, str) or len(oid) != 40:
            return {"verdict": UNKNOWN, "reason": "terminal merge commit OID missing"}
        return {"verdict": MERGED_OK, "reason": "all intended members verified merged"}

    if state in {"FAILED", "EXPIRED_UNKNOWN", "EXISTING_U_MISMATCH", "ALREADY_200"}:
        return {"verdict": UNKNOWN, "reason": f"{state} requires explicit repository reconciliation"}

    return {"verdict": UNKNOWN, "reason": f"unsupported state {state!r}"}

def fixture_capsule(state="STACK_SNAPSHOT"):
    return {
        "schema_version": 1,
        "repository": "octo/repo",
        "stack": {
            "number": 7, "base_ref": "main", "base_sha": "0"*40,
            "members": [
                {"pr_number": 11, "position": 1, "head_sha": "1"*40,
                 "direct_base_ref":"main", "direct_base_sha":"0"*40},
                {"pr_number": 12, "position": 2, "head_sha": "2"*40,
                 "direct_base_ref":"feature-1", "direct_base_sha":"1"*40},
                {"pr_number": 13, "position": 3, "head_sha": "3"*40,
                 "direct_base_ref":"feature-2", "direct_base_sha":"2"*40},
            ],
        },
        "requested": {"pr_number": 13, "expected_head_sha": "3"*40},
        "merge_method": "merge", "merge_action": "merge_queue", "state": state,
    }

def self_test():
    c = fixture_capsule()
    exact = {"stack": json.loads(json.dumps(c["stack"]))}
    assert reconcile(c, exact)["verdict"] == READY

    drift = json.loads(json.dumps(exact))
    drift["stack"]["members"][0]["head_sha"] = "9"*40
    assert reconcile(c, drift)["verdict"] == CONFLICT

    u = fixture_capsule("SUBMIT_UNKNOWN")
    matching = {"recoverable_async_request": {
        "uuid":"u1", "expected_head_sha":"3"*40,
        "merge_method":"merge", "merge_action":"merge_queue"}}
    assert reconcile(u, matching)["verdict"] == RESUME

    mismatch = json.loads(json.dumps(matching))
    mismatch["recoverable_async_request"]["expected_head_sha"] = "8"*40
    assert reconcile(u, mismatch)["verdict"] == CONFLICT

    q = fixture_capsule("QUEUED")
    groups = {"merge_groups": [
        {"sha":"a"*40, "member_pr_numbers":[11,12]},
        {"sha":"b"*40, "member_pr_numbers":[13]},
    ]}
    assert reconcile(q, groups)["verdict"] == QUEUE_OK

    p = fixture_capsule("PENDING")
    assert reconcile(p, {"result_not_found_after_retention":True})["verdict"] == EXPIRED_UNKNOWN
    return {
        "exact_snapshot":"READY_TO_SUBMIT",
        "lower_member_drift":"CONFLICT",
        "recover_matching_request":"RESUME",
        "reject_mismatched_request":"CONFLICT",
        "multi_group_queue":"QUEUE_EVIDENCE_OK",
        "expired_result":"EXPIRED_UNKNOWN",
    }

if __name__ == "__main__":
    if "--self-test" in sys.argv:
        print(json.dumps(self_test(), indent=2, sort_keys=True))
    else:
        payload = json.load(sys.stdin)
        print(json.dumps(reconcile(payload["capsule"], payload["observation"]), indent=2, sort_keys=True))
