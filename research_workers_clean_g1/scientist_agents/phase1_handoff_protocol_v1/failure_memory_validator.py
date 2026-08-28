#!/usr/bin/env python3
"""Semantic validator for bounded failure-memory records handed between agents.

The companion JSON Schema checks structure and bounded payload size. This file
checks cross-field lifecycle invariants: raw-source provenance, target freshness,
curator-record freshness, evidence availability/contradiction, target-side
revalidation before cross-domain adoption, qualified domain-general bypass, and
non-enforcement of rejected or unqualified records.
"""
from __future__ import annotations

import copy
import json
import sys
from pathlib import Path


def semantic_validate(record: dict, handoff_packet: dict, context: dict) -> list[str]:
    codes: list[str] = []

    # A derived record must remain anchored to immutable raw failed/abandoned
    # evidence carried by the lifecycle packet; the summary never replaces it.
    raw = {
        branch["digest"]: branch
        for branch in handoff_packet.get("negative_branches", [])
    }
    for digest in record["source_branch_digests"]:
        branch = raw.get(digest)
        if branch is None or not branch.get("immutable", False):
            codes.append("FAILURE_MEMORY_PROVENANCE_MISSING")
            break

    # Curated summaries are versioned evidence. A stale curator digest must not
    # remain authoritative after the record has been revised or superseded.
    current_curator = context.get("current_curator_record_digests", {}).get(
        record["record_id"]
    )
    if current_curator is None or record["curator_record_digest"] != current_curator:
        codes.append("FAILURE_MEMORY_CURATOR_STALE")

    # Revalidation is target-specific. A record qualified against an older target
    # context cannot be silently reused after the target/task assumptions change.
    if record["target_context_signature"] != context["current_target_context_signature"]:
        codes.append("FAILURE_MEMORY_TARGET_STALE")

    transfer_class = record["transfer_class"]
    decision = record["receiver_decision"]
    use_mode = record["use_mode"]
    rv = record["revalidation"]
    check_results = {item["name"]: item["result"] for item in rv["checks"]}

    required_checks = set(context.get(
        "required_cross_domain_checks",
        ["mechanism_assumption_compatibility", "target_probe"],
    ))

    # Cross-domain memories are hypotheses, not authority. Before adoption they
    # must pass explicit mechanism-assumption compatibility and a target-side
    # probe. This catches cases where a numerically successful source method is
    # anti-diffusive or otherwise invalid under the target's governing signs.
    if transfer_class == "cross_domain" and decision == "adopt":
        checks_pass = all(check_results.get(name) == "pass" for name in required_checks)
        if not rv["required"] or rv["status"] != "pass" or not checks_pass:
            codes.append("FAILURE_MEMORY_REVALIDATION_REQUIRED")

    # A self-declared "domain_general" label cannot bypass target revalidation.
    # Bypass is allowed only when the current curator digest has been separately
    # prequalified by the receiving context. Otherwise the record must satisfy
    # the same target checks as cross-domain transfer.
    if transfer_class == "domain_general" and decision == "adopt":
        prequalified = set(context.get("prequalified_domain_general_digests", []))
        if record["curator_record_digest"] not in prequalified:
            checks_pass = all(check_results.get(name) == "pass" for name in required_checks)
            if not rv["required"] or rv["status"] != "pass" or not checks_pass:
                codes.append("FAILURE_MEMORY_DOMAIN_GENERAL_UNQUALIFIED")

    # A "pass" label is insufficient if the referenced evidence is unavailable
    # in the receiving context or has been explicitly contradicted/superseded.
    available_evidence = set(context.get("available_evidence_digests", []))
    contradicted_evidence = set(context.get("contradicted_evidence_digests", []))
    if decision == "adopt":
        for item in rv["checks"]:
            if item["result"] != "pass":
                continue
            digest = item["evidence"]["digest"]
            if digest not in available_evidence:
                codes.append("FAILURE_MEMORY_REVALIDATION_EVIDENCE_MISSING")
            if digest in contradicted_evidence:
                codes.append("FAILURE_MEMORY_REVALIDATION_EVIDENCE_CONTRADICTED")
                codes.append("FAILURE_MEMORY_CONTRADICTED")

    # A failed target-side probe is direct evidence against adoption.
    if decision == "adopt" and (rv["status"] == "fail" or any(
        item["result"] == "fail" for item in rv["checks"]
    )):
        codes.append("FAILURE_MEMORY_CONTRADICTED")

    # A transferred memory may constrain future actions only after explicit
    # receiver adoption and any required revalidation. Rejected/held records stay
    # inspectable advisory evidence rather than mutating the admissible action set.
    if use_mode == "constraint":
        if decision != "adopt":
            codes.append("FAILURE_MEMORY_ENFORCEMENT_INVALID")
        elif rv["required"] and rv["status"] != "pass":
            codes.append("FAILURE_MEMORY_ENFORCEMENT_INVALID")
        elif any(code in codes for code in {
            "FAILURE_MEMORY_CURATOR_STALE",
            "FAILURE_MEMORY_TARGET_STALE",
            "FAILURE_MEMORY_REVALIDATION_REQUIRED",
            "FAILURE_MEMORY_DOMAIN_GENERAL_UNQUALIFIED",
            "FAILURE_MEMORY_REVALIDATION_EVIDENCE_MISSING",
            "FAILURE_MEMORY_REVALIDATION_EVIDENCE_CONTRADICTED",
            "FAILURE_MEMORY_CONTRADICTED",
        }):
            codes.append("FAILURE_MEMORY_ENFORCEMENT_INVALID")

    return sorted(set(codes))


def _resolve(container, path):
    cur = container
    for key in path:
        cur = cur[key]
    return cur


def apply_mutation(record: dict, packet: dict, context: dict, mutation: dict) -> None:
    target_name = mutation["target"]
    root = {"record": record, "packet": packet, "context": context}[target_name]
    path = mutation["path"]
    op = mutation["op"]
    if op == "set":
        parent = _resolve(root, path[:-1]) if path[:-1] else root
        parent[path[-1]] = mutation["value"]
    elif op == "append":
        _resolve(root, path).append(mutation["value"])
    elif op == "delete_index":
        del _resolve(root, path)[mutation["index"]]
    else:
        raise ValueError(f"unsupported mutation op: {op}")


def run_tests(spec: dict) -> tuple[int, int]:
    passed = 0
    total = 0
    for case in spec["cases"]:
        total += 1
        record = copy.deepcopy(spec["base_record"])
        packet = copy.deepcopy(spec["base_handoff_packet"])
        context = copy.deepcopy(spec["base_context"])
        for mutation in case["mutations"]:
            apply_mutation(record, packet, context, mutation)
        codes = semantic_validate(record, packet, context)
        ok = (not codes) if case["should_pass"] else all(
            code in codes for code in case["expected_failure_codes"]
        )
        print(f"{'PASS' if ok else 'FAIL'} {case['name']}: {codes}")
        passed += int(ok)
    return passed, total


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: failure_memory_validator.py failure_memory_tests.json", file=sys.stderr)
        return 2
    spec = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    passed, total = run_tests(spec)
    print(f"{passed}/{total} tests passed")
    return 0 if passed == total else 1


if __name__ == "__main__":
    raise SystemExit(main())
