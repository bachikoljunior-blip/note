#!/usr/bin/env python3
"""Offline validator for durable GitHub Rule Suite discovery/readback.

Network collectors feed this helper list-page metadata plus exact suite-ID
readbacks. The validator refuses to turn a partial/permission-limited list into
policy evidence.
"""
from __future__ import annotations
import json
import sys

PASS = "PASS"
UNKNOWN = "UNKNOWN"

def transition_key(x):
    return (x.get("ref"), x.get("before_sha"), x.get("after_sha"))

def discover_rule_suites(doc):
    transitions = doc.get("transitions")
    listing = doc.get("listing") or {}
    if not isinstance(transitions, list) or not transitions:
        return {"verdict": UNKNOWN, "reason": "transition chain missing"}
    if listing.get("permission_ok") is not True:
        return {"verdict": UNKNOWN, "reason": "Rule Suite list permission not proved"}
    if listing.get("pagination_complete") is not True:
        return {"verdict": UNKNOWN, "reason": "Rule Suite list pagination incomplete"}
    if listing.get("evaluate_status") != "all":
        return {"verdict": UNKNOWN, "reason": "list did not request active+evaluate suites"}
    if listing.get("time_period") != "month":
        return {"verdict": UNKNOWN, "reason": "collector did not use maximum documented discovery window"}
    if listing.get("ref_filter") != transitions[0].get("ref"):
        return {"verdict": UNKNOWN, "reason": "Rule Suite ref filter differs from transition ref"}

    pages = listing.get("pages")
    if not isinstance(pages, list) or not pages:
        return {"verdict": UNKNOWN, "reason": "Rule Suite pages absent"}

    by_key = {}
    duplicates = set()
    for page in pages:
        if not isinstance(page, list):
            return {"verdict": UNKNOWN, "reason": "invalid Rule Suite page"}
        for s in page:
            if not isinstance(s, dict):
                continue
            key = transition_key(s)
            if key in by_key:
                duplicates.add(key)
            by_key[key] = s
    if duplicates:
        return {"verdict": UNKNOWN, "reason": "duplicate Rule Suites for exact transition", "keys": sorted(map(str, duplicates))}

    selected = []
    for edge in transitions:
        key = transition_key(edge)
        suite = by_key.get(key)
        if not suite or not suite.get("id"):
            return {"verdict": UNKNOWN, "reason": f"no unique suite discovered for {key}"}
        selected.append(suite)

    persisted_ids = doc.get("persisted_suite_ids")
    expected_ids = [s["id"] for s in selected]
    if persisted_ids != expected_ids:
        return {"verdict": UNKNOWN, "reason": "persisted suite IDs differ from discovered transition order"}

    details = doc.get("exact_suite_readbacks")
    if not isinstance(details, list):
        return {"verdict": UNKNOWN, "reason": "exact suite-ID readbacks absent"}
    detail_by_id = {}
    for d in details:
        if not isinstance(d, dict) or not d.get("id"):
            continue
        if d["id"] in detail_by_id:
            return {"verdict": UNKNOWN, "reason": "duplicate exact suite-ID readback"}
        detail_by_id[d["id"]] = d

    normalized = []
    for listed in selected:
        d = detail_by_id.get(listed["id"])
        if not d:
            return {"verdict": UNKNOWN, "reason": f"suite ID {listed['id']} not exact-read back"}
        if transition_key(d) != transition_key(listed):
            return {"verdict": UNKNOWN, "reason": f"suite ID {listed['id']} transition changed on exact readback"}
        for k in ("result", "evaluation_result"):
            if d.get(k) != listed.get(k):
                return {"verdict": UNKNOWN, "reason": f"suite ID {listed['id']} {k} changed on exact readback"}
        normalized.append({
            "id": d["id"],
            "ref": d["ref"],
            "before_sha": d["before_sha"],
            "after_sha": d["after_sha"],
            "result": d.get("result"),
            "evaluation_result": d.get("evaluation_result"),
            "rule_evaluations": d.get("rule_evaluations"),
            "exact_readback_by_id": True,
        })

    return {
        "verdict": PASS,
        "suite_ids": expected_ids,
        "rule_suites": normalized,
    }

def fixture():
    transitions = [
        {"ref":"refs/heads/main","before_sha":"a"*40,"after_sha":"b"*40},
        {"ref":"refs/heads/main","before_sha":"b"*40,"after_sha":"c"*40},
    ]
    s1 = {"id":11, **transitions[0], "result":"pass","evaluation_result":"pass"}
    s2 = {"id":12, **transitions[1], "result":"pass","evaluation_result":"fail"}
    return {
        "transitions": transitions,
        "listing": {
            "permission_ok": True,
            "pagination_complete": True,
            "evaluate_status": "all",
            "time_period": "month",
            "ref_filter": "refs/heads/main",
            "pages": [[s1],[s2]],
        },
        "persisted_suite_ids": [11,12],
        "exact_suite_readbacks": [
            {**s1, "rule_evaluations":[]},
            {**s2, "rule_evaluations":[]},
        ],
    }

def self_test():
    base = fixture()
    assert discover_rule_suites(base)["verdict"] == PASS

    x = json.loads(json.dumps(base)); x["listing"]["permission_ok"] = False
    assert discover_rule_suites(x)["verdict"] == UNKNOWN
    x = json.loads(json.dumps(base)); x["listing"]["pagination_complete"] = False
    assert discover_rule_suites(x)["verdict"] == UNKNOWN
    x = json.loads(json.dumps(base)); x["listing"]["evaluate_status"] = "active"
    assert discover_rule_suites(x)["verdict"] == UNKNOWN
    x = json.loads(json.dumps(base)); x["listing"]["time_period"] = "week"
    assert discover_rule_suites(x)["verdict"] == UNKNOWN
    x = json.loads(json.dumps(base)); x["listing"]["pages"] = [x["listing"]["pages"][0]]
    assert discover_rule_suites(x)["verdict"] == UNKNOWN
    x = json.loads(json.dumps(base)); x["listing"]["pages"][1].append(dict(x["listing"]["pages"][1][0]))
    assert discover_rule_suites(x)["verdict"] == UNKNOWN
    x = json.loads(json.dumps(base)); x["persisted_suite_ids"] = [12,11]
    assert discover_rule_suites(x)["verdict"] == UNKNOWN
    x = json.loads(json.dumps(base)); x["exact_suite_readbacks"][1]["after_sha"] = "d"*40
    assert discover_rule_suites(x)["verdict"] == UNKNOWN
    x = json.loads(json.dumps(base)); x["exact_suite_readbacks"] = x["exact_suite_readbacks"][:1]
    assert discover_rule_suites(x)["verdict"] == UNKNOWN

    return {
        "complete_two_edge_discovery": PASS,
        "permission_failure_unknown": PASS,
        "pagination_incomplete_unknown": PASS,
        "evaluate_scope_incomplete_unknown": PASS,
        "short_discovery_window_unknown": PASS,
        "missing_edge_unknown": PASS,
        "duplicate_edge_unknown": PASS,
        "persisted_id_order_mismatch_unknown": PASS,
        "exact_readback_transition_mismatch_unknown": PASS,
        "exact_readback_missing_unknown": PASS,
    }

if __name__ == "__main__":
    if "--self-test" in sys.argv:
        print(json.dumps(self_test(), indent=2, sort_keys=True))
    else:
        print(json.dumps(discover_rule_suites(json.load(sys.stdin)), indent=2, sort_keys=True))
