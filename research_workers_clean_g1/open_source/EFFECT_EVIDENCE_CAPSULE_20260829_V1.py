#!/usr/bin/env python3
"""Validate a durable GitHub merge/effect evidence capsule.

This collector-side helper is intentionally fail-closed. It does not perform
network I/O or authorize/merge anything. It normalizes observations that a
Chat/recovery layer must durably preserve before server-side evidence ages out.

Key properties:
- member vector is preserved in full; its SHA-256 fingerprint is drift detection,
  not authority;
- if the dedicated Stacks endpoint is unavailable, PR resources may reconstruct
  the vector only when every stack position 1..size is present with exact head SHA;
- request admission, queue admission, final base effect, and Rule Suite policy
  evidence stay separate;
- Rule Suites must cover each exact base-ref transition by
  (ref, before_sha, after_sha).
"""
from __future__ import annotations
import hashlib
import json
import sys

PASS = "PASS"
UNKNOWN = "UNKNOWN"
NOT_STACKED = "NOT_STACKED"
UNKNOWN_MEMBER_VECTOR = "UNKNOWN_MEMBER_VECTOR"
MEMBER_VECTOR_EXACT = "MEMBER_VECTOR_EXACT"

def canonical_json(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)

def member_vector_fingerprint(members):
    payload = [
        {
            "position": m["position"],
            "pr_number": m["pr_number"],
            "head_sha": m["head_sha"],
            "direct_base_ref": m.get("direct_base_ref"),
        }
        for m in members
    ]
    return hashlib.sha256(canonical_json(payload).encode("utf-8")).hexdigest()

def reconstruct_member_vector_from_prs(anchor_pr_number, pr_resources):
    """Reconstruct ordered stack vector from raw PR REST resources.

    Official GitHub Stacked PR docs expose on stacked PR resources:
    stack.id/number/size/position/base.{ref,sha}. This is enough to reconstruct
    the member vector only if we possess every member PR resource.
    """
    if not isinstance(pr_resources, list):
        return {"state": UNKNOWN_MEMBER_VECTOR, "reason": "PR resource collection missing"}

    anchor = next((p for p in pr_resources if p.get("number") == anchor_pr_number), None)
    if not anchor:
        return {"state": UNKNOWN_MEMBER_VECTOR, "reason": "anchor PR absent"}

    s = anchor.get("stack")
    if s is None:
        return {
            "state": UNKNOWN_MEMBER_VECTOR,
            "reason": "anchor PR has no stack object; standalone vs API/connector field omission is not proved",
        }
    required = ("id", "number", "size", "position", "base")
    if any(k not in s for k in required):
        return {"state": UNKNOWN_MEMBER_VECTOR, "reason": "anchor stack object incomplete"}

    stack_id = s["id"]
    stack_number = s["number"]
    size = s["size"]
    base = s.get("base") or {}
    if not isinstance(size, int) or size < 2 or not base.get("ref") or not base.get("sha"):
        return {"state": UNKNOWN_MEMBER_VECTOR, "reason": "invalid anchor stack size/base"}

    members = []
    seen_positions = set()
    for p in pr_resources:
        ps = p.get("stack")
        if not isinstance(ps, dict):
            continue
        if ps.get("id") != stack_id or ps.get("number") != stack_number:
            continue
        if ps.get("size") != size:
            return {"state": UNKNOWN_MEMBER_VECTOR, "reason": "member stack.size disagreement"}
        pbase = ps.get("base") or {}
        if pbase.get("ref") != base.get("ref") or pbase.get("sha") != base.get("sha"):
            return {"state": UNKNOWN_MEMBER_VECTOR, "reason": "member stack.base disagreement"}
        pos = ps.get("position")
        head = p.get("head") or {}
        direct_base = p.get("base") or {}
        if not isinstance(pos, int) or pos < 1 or pos > size:
            return {"state": UNKNOWN_MEMBER_VECTOR, "reason": "invalid stack.position"}
        if pos in seen_positions:
            return {"state": UNKNOWN_MEMBER_VECTOR, "reason": "duplicate stack.position"}
        if not isinstance(p.get("number"), int) or not head.get("sha") or not head.get("ref"):
            return {"state": UNKNOWN_MEMBER_VECTOR, "reason": "member PR/head identity incomplete"}
        seen_positions.add(pos)
        members.append(
            {
                "position": pos,
                "pr_number": p["number"],
                "head_sha": head["sha"],
                "head_ref": head["ref"],
                "direct_base_ref": direct_base.get("ref"),
            }
        )

    if len(members) != size or seen_positions != set(range(1, size + 1)):
        return {
            "state": UNKNOWN_MEMBER_VECTOR,
            "reason": f"incomplete stack membership: got positions {sorted(seen_positions)}, expected 1..{size}",
        }

    members.sort(key=lambda m: m["position"])

    if members[0].get("direct_base_ref") != base["ref"]:
        return {"state": UNKNOWN_MEMBER_VECTOR, "reason": "bottom PR does not directly target stack base"}
    for prev, cur in zip(members, members[1:]):
        if cur.get("direct_base_ref") != prev.get("head_ref"):
            return {
                "state": UNKNOWN_MEMBER_VECTOR,
                "reason": f"PR {cur['pr_number']} base does not target prior member head",
            }

    return {
        "state": MEMBER_VECTOR_EXACT,
        "stack_id": stack_id,
        "stack_number": stack_number,
        "stack_base_ref": base["ref"],
        "stack_base_sha": base["sha"],
        "members": members,
        "member_vector_fingerprint": member_vector_fingerprint(members),
        "source": "complete_pr_resource_stack_objects",
    }

def normalize_member_vector_from_stack_resource(stack):
    """Normalize the dedicated GET /stacks/{n} response.

    The stack resource is ordered bottom->top but does not repeat direct base refs
    in its minimal member objects, so this normalizer preserves exact order/head
    identity without inventing unavailable direct-base evidence.
    """
    if not isinstance(stack, dict):
        return {"state": UNKNOWN_MEMBER_VECTOR, "reason": "stack resource missing"}
    prs = stack.get("pull_requests")
    base = stack.get("base") or {}
    if not isinstance(prs, list) or len(prs) < 2 or not base.get("ref"):
        return {"state": UNKNOWN_MEMBER_VECTOR, "reason": "stack resource incomplete"}
    members = []
    for i, p in enumerate(prs, 1):
        head = p.get("head") or {}
        if not isinstance(p.get("number"), int) or not head.get("sha"):
            return {"state": UNKNOWN_MEMBER_VECTOR, "reason": "stack member identity incomplete"}
        members.append({
            "position": i,
            "pr_number": p["number"],
            "head_sha": head["sha"],
            "head_ref": head.get("ref"),
            "direct_base_ref": None,
        })
    return {
        "state": MEMBER_VECTOR_EXACT,
        "stack_number": stack.get("number"),
        "stack_base_ref": base["ref"],
        "members": members,
        "member_vector_fingerprint": member_vector_fingerprint(members),
        "source": "dedicated_stack_resource",
    }

def validate_transition_chain(base_ref, base_before_sha, transitions, base_final_sha):
    if not base_ref or not base_before_sha or not base_final_sha:
        return {"state": UNKNOWN, "reason": "base identity incomplete"}
    if not isinstance(transitions, list) or not transitions:
        return {"state": UNKNOWN, "reason": "transition chain absent"}
    prev = base_before_sha
    out = []
    for i, edge in enumerate(transitions):
        if edge.get("ref") != base_ref or edge.get("before_sha") != prev or not edge.get("after_sha"):
            return {"state": UNKNOWN, "reason": f"transition edge {i} does not form exact chain"}
        if edge["after_sha"] == edge["before_sha"]:
            return {"state": UNKNOWN, "reason": f"transition edge {i} is non-advancing"}
        out.append({
            "ref": base_ref,
            "before_sha": edge["before_sha"],
            "after_sha": edge["after_sha"],
        })
        prev = edge["after_sha"]
    if prev != base_final_sha:
        return {"state": UNKNOWN, "reason": "transition chain does not end at base_final_sha"}
    return {"state": PASS, "transitions": out}

def validate_rule_suite_coverage(transitions, suites):
    if not isinstance(suites, list):
        return {"state": UNKNOWN, "reason": "Rule Suites missing"}
    by_key = {}
    duplicate = set()
    for s in suites:
        if not isinstance(s, dict):
            continue
        key = (s.get("ref"), s.get("before_sha"), s.get("after_sha"))
        if key in by_key:
            duplicate.add(key)
        by_key[key] = s
    if duplicate:
        return {"state": UNKNOWN, "reason": "duplicate Rule Suite transition keys", "keys": sorted(map(str, duplicate))}
    matched = []
    for edge in transitions:
        key = (edge["ref"], edge["before_sha"], edge["after_sha"])
        s = by_key.get(key)
        if not s or not s.get("id"):
            return {"state": UNKNOWN, "reason": f"missing exact Rule Suite for {key}"}
        if s.get("exact_readback_by_id") is not True:
            return {"state": UNKNOWN, "reason": f"Rule Suite {s.get('id')} not exact-read back by persisted ID"}
        matched.append(s)
    return {"state": PASS, "suite_ids": [s["id"] for s in matched]}

def validate_capsule(c):
    if not isinstance(c, dict) or c.get("schema_version") != 1:
        return {"verdict": UNKNOWN, "reason": "unsupported capsule schema"}
    intent = c.get("effect_intent") or {}
    mv = intent.get("member_vector")
    if mv:
        members = mv.get("members")
        if not isinstance(members, list) or not members:
            return {"verdict": UNKNOWN, "reason": "member vector missing members"}
        if member_vector_fingerprint(members) != mv.get("fingerprint"):
            return {"verdict": UNKNOWN, "reason": "member-vector fingerprint mismatch"}

    final = c.get("final_effect") or {}
    chain = validate_transition_chain(
        intent.get("base_ref"),
        intent.get("base_before_sha"),
        final.get("base_ref_transition_chain"),
        final.get("base_final_sha"),
    )
    if chain["state"] != PASS:
        return {"verdict": UNKNOWN, "reason": chain["reason"]}

    suites = validate_rule_suite_coverage(chain["transitions"], c.get("rule_suites"))
    if suites["state"] != PASS:
        return {"verdict": UNKNOWN, "reason": suites["reason"]}

    return {
        "verdict": PASS,
        "member_vector_fingerprint": mv.get("fingerprint") if mv else None,
        "transition_count": len(chain["transitions"]),
        "rule_suite_ids": suites["suite_ids"],
    }

def _pr(n, pos, size=3, stack_id=77, stack_number=9, base="main", base_sha="b"*40,
        head_ref=None, head_sha=None, direct_base=None):
    head_ref = head_ref or f"layer-{n}"
    head_sha = head_sha or (str(n % 10) * 40)
    return {
        "number": n,
        "head": {"ref": head_ref, "sha": head_sha},
        "base": {"ref": direct_base},
        "stack": {
            "id": stack_id,
            "number": stack_number,
            "size": size,
            "position": pos,
            "base": {"ref": base, "sha": base_sha},
        },
    }

def self_test():
    p1 = _pr(101, 1, head_ref="a", direct_base="main")
    p2 = _pr(102, 2, head_ref="b", direct_base="a")
    p3 = _pr(103, 3, head_ref="c", direct_base="b")
    exact = reconstruct_member_vector_from_prs(102, [p3, p1, p2])
    assert exact["state"] == MEMBER_VECTOR_EXACT
    assert [m["pr_number"] for m in exact["members"]] == [101, 102, 103]

    missing = reconstruct_member_vector_from_prs(102, [p1, p2])
    assert missing["state"] == UNKNOWN_MEMBER_VECTOR

    nostack = json.loads(json.dumps(p2))
    nostack.pop("stack")
    assert reconstruct_member_vector_from_prs(102, [nostack])["state"] == UNKNOWN_MEMBER_VECTOR

    mismatch = json.loads(json.dumps(p3))
    mismatch["stack"]["size"] = 4
    assert reconstruct_member_vector_from_prs(102, [p1, p2, mismatch])["state"] == UNKNOWN_MEMBER_VECTOR

    brokenchain = json.loads(json.dumps(p3))
    brokenchain["base"]["ref"] = "wrong"
    assert reconstruct_member_vector_from_prs(102, [p1, p2, brokenchain])["state"] == UNKNOWN_MEMBER_VECTOR

    direct = normalize_member_vector_from_stack_resource({
        "number": 9, "base": {"ref": "main"},
        "pull_requests": [
            {"number": 101, "head": {"ref": "a", "sha": "1"*40}},
            {"number": 102, "head": {"ref": "b", "sha": "2"*40}},
        ],
    })
    assert direct["state"] == MEMBER_VECTOR_EXACT

    transitions = [
        {"ref": "refs/heads/main", "before_sha": "a"*40, "after_sha": "b"*40},
        {"ref": "refs/heads/main", "before_sha": "b"*40, "after_sha": "c"*40},
    ]
    assert validate_transition_chain("refs/heads/main", "a"*40, transitions, "c"*40)["state"] == PASS
    assert validate_transition_chain("refs/heads/main", "x"*40, transitions, "c"*40)["state"] == UNKNOWN

    suites = [
        {"id": 1, "ref": "refs/heads/main", "before_sha": "a"*40, "after_sha": "b"*40, "exact_readback_by_id": True},
        {"id": 2, "ref": "refs/heads/main", "before_sha": "b"*40, "after_sha": "c"*40, "exact_readback_by_id": True},
    ]
    assert validate_rule_suite_coverage(transitions, suites)["state"] == PASS
    assert validate_rule_suite_coverage(transitions, suites[:1])["state"] == UNKNOWN
    dup = suites + [dict(suites[0])]
    assert validate_rule_suite_coverage(transitions, dup)["state"] == UNKNOWN

    members = exact["members"]
    cap = {
        "schema_version": 1,
        "effect_intent": {
            "base_ref": "refs/heads/main",
            "base_before_sha": "a"*40,
            "member_vector": {"members": members, "fingerprint": member_vector_fingerprint(members)},
        },
        "final_effect": {
            "base_final_sha": "c"*40,
            "base_ref_transition_chain": transitions,
        },
        "rule_suites": suites,
    }
    assert validate_capsule(cap)["verdict"] == PASS
    bad = json.loads(json.dumps(cap))
    bad["effect_intent"]["member_vector"]["fingerprint"] = "0"*64
    assert validate_capsule(bad)["verdict"] == UNKNOWN

    return {
        "pr_resource_complete_vector": PASS,
        "pr_resource_missing_member": PASS,
        "pr_resource_stack_field_absent_is_unknown": PASS,
        "pr_resource_size_disagreement": PASS,
        "pr_resource_chain_break": PASS,
        "dedicated_stack_resource_vector": PASS,
        "transition_chain_complete": PASS,
        "transition_chain_wrong_start": PASS,
        "rule_suite_edge_coverage": PASS,
        "rule_suite_missing_edge": PASS,
        "rule_suite_duplicate_edge": PASS,
        "capsule_full_pass": PASS,
        "capsule_member_fingerprint_drift": PASS,
    }

if __name__ == "__main__":
    if "--self-test" in sys.argv:
        print(json.dumps(self_test(), indent=2, sort_keys=True))
    else:
        print(json.dumps(validate_capsule(json.load(sys.stdin)), indent=2, sort_keys=True))
