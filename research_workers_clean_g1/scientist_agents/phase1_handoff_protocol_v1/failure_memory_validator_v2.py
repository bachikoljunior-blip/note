#!/usr/bin/env python3
"""Semantic validator for failure-memory handoff v2.

V2 preserves v1's raw-provenance, target-freshness, curator-freshness,
evidence-availability/contradiction, cross-domain revalidation and enforcement
rules, and adds four invariants:

1. failure claims must bind to the implementation revision/mechanism fingerprint
   that actually produced the source failure;
2. domain-general prequalification is bound to the current receiver policy
   revision and may be explicitly revoked;
3. revalidation is bound to the receiver's current evidence-registry revision,
   and superseded evidence cannot authorize adoption;
4. any failure memory that constrains/prunes the target action set requires an
   explicit target-applicability check, even when boundary metadata exists.
"""
from __future__ import annotations

import copy
import json
import sys
from pathlib import Path


def _append(codes: list[str], code: str) -> None:
    if code not in codes:
        codes.append(code)


def semantic_validate(record: dict, handoff_packet: dict, context: dict) -> list[str]:
    codes: list[str] = []

    raw = {branch["digest"]: branch for branch in handoff_packet.get("negative_branches", [])}
    bound_branches = []
    for digest in record["source_branch_digests"]:
        branch = raw.get(digest)
        if branch is None or not branch.get("immutable", False):
            _append(codes, "FAILURE_MEMORY_PROVENANCE_MISSING")
            continue
        bound_branches.append(branch)

    # The curator's textual record must point to the exact implementation/mechanism
    # lineage recorded by the immutable source branch. Near-date or same-repo
    # lineage is insufficient.
    mp = record["mechanism_provenance"]
    for branch in bound_branches:
        if (
            branch.get("implementation_revision") != mp["implementation_revision"]
            or branch.get("mechanism_fingerprint") != mp["mechanism_fingerprint"]
            or branch.get("artifact_digest") != mp["artifact_digest"]
        ):
            _append(codes, "FAILURE_MEMORY_MECHANISM_PROVENANCE_MISMATCH")
            break

    current_curator = context.get("current_curator_record_digests", {}).get(record["record_id"])
    if current_curator is None or record["curator_record_digest"] != current_curator:
        _append(codes, "FAILURE_MEMORY_CURATOR_STALE")

    if record["target_context_signature"] != context["current_target_context_signature"]:
        _append(codes, "FAILURE_MEMORY_TARGET_STALE")

    transfer_class = record["transfer_class"]
    decision = record["receiver_decision"]
    use_mode = record["use_mode"]
    rv = record["revalidation"]
    checks = {item["name"]: item for item in rv["checks"]}
    check_results = {name: item["result"] for name, item in checks.items()}

    required_cross = set(context.get(
        "required_cross_domain_checks",
        ["mechanism_assumption_compatibility", "target_probe"],
    ))
    required_constraint = set(context.get(
        "required_constraint_checks",
        ["target_applicability"],
    ))

    # Revalidation evidence is evaluated against a versioned receiver-side registry.
    if decision == "adopt" and rv["evidence_registry_revision"] != context.get("current_evidence_registry_revision"):
        _append(codes, "FAILURE_MEMORY_REVALIDATION_REGISTRY_STALE")

    # Cross-domain memories are hypotheses until mechanism compatibility and a
    # bounded target probe pass.
    if transfer_class == "cross_domain" and decision == "adopt":
        checks_pass = all(check_results.get(name) == "pass" for name in required_cross)
        if not rv["required"] or rv["status"] != "pass" or not checks_pass:
            _append(codes, "FAILURE_MEMORY_REVALIDATION_REQUIRED")

    # A domain-general bypass is policy-scoped, not self-declared. The receiver
    # must have a live prequalification entry for this curator digest under the
    # current policy revision, and the digest must not be revoked.
    if transfer_class == "domain_general" and decision == "adopt":
        entries = context.get("domain_general_prequalifications", {})
        entry = entries.get(record["curator_record_digest"])
        current_policy = context.get("current_prequalification_policy_revision")
        revoked = set(context.get("revoked_prequalification_digests", []))
        live_prequalification = bool(
            entry
            and entry.get("policy_revision") == current_policy
            and entry.get("status") == "active"
            and record["curator_record_digest"] not in revoked
        )
        if not live_prequalification:
            checks_pass = all(check_results.get(name) == "pass" for name in required_cross)
            if not rv["required"] or rv["status"] != "pass" or not checks_pass:
                _append(codes, "FAILURE_MEMORY_DOMAIN_GENERAL_UNQUALIFIED")
            _append(codes, "FAILURE_MEMORY_PREQUALIFICATION_STALE_OR_REVOKED")

    available = set(context.get("available_evidence_digests", []))
    contradicted = set(context.get("contradicted_evidence_digests", []))
    superseded = set(context.get("superseded_evidence_digests", []))
    if decision == "adopt":
        for item in rv["checks"]:
            if item["result"] != "pass":
                continue
            digest = item["evidence"]["digest"]
            if digest not in available:
                _append(codes, "FAILURE_MEMORY_REVALIDATION_EVIDENCE_MISSING")
            if digest in contradicted:
                _append(codes, "FAILURE_MEMORY_REVALIDATION_EVIDENCE_CONTRADICTED")
                _append(codes, "FAILURE_MEMORY_CONTRADICTED")
            if digest in superseded:
                _append(codes, "FAILURE_MEMORY_REVALIDATION_EVIDENCE_SUPERSEDED")

    if decision == "adopt" and (
        rv["status"] == "fail" or any(item["result"] == "fail" for item in rv["checks"])
    ):
        _append(codes, "FAILURE_MEMORY_CONTRADICTED")

    # Boundary text is not executable authority. Any record that narrows/prunes
    # the target action set must carry an explicit receiver-side applicability
    # check whose evidence is live under the current registry.
    if use_mode == "constraint":
        applicability_pass = all(check_results.get(name) == "pass" for name in required_constraint)
        if not applicability_pass:
            _append(codes, "FAILURE_MEMORY_APPLICABILITY_CHECK_REQUIRED")
        if decision != "adopt":
            _append(codes, "FAILURE_MEMORY_ENFORCEMENT_INVALID")
        elif rv["required"] and rv["status"] != "pass":
            _append(codes, "FAILURE_MEMORY_ENFORCEMENT_INVALID")
        elif any(code in codes for code in {
            "FAILURE_MEMORY_PROVENANCE_MISSING",
            "FAILURE_MEMORY_MECHANISM_PROVENANCE_MISMATCH",
            "FAILURE_MEMORY_CURATOR_STALE",
            "FAILURE_MEMORY_TARGET_STALE",
            "FAILURE_MEMORY_REVALIDATION_REGISTRY_STALE",
            "FAILURE_MEMORY_REVALIDATION_REQUIRED",
            "FAILURE_MEMORY_DOMAIN_GENERAL_UNQUALIFIED",
            "FAILURE_MEMORY_PREQUALIFICATION_STALE_OR_REVOKED",
            "FAILURE_MEMORY_REVALIDATION_EVIDENCE_MISSING",
            "FAILURE_MEMORY_REVALIDATION_EVIDENCE_CONTRADICTED",
            "FAILURE_MEMORY_REVALIDATION_EVIDENCE_SUPERSEDED",
            "FAILURE_MEMORY_CONTRADICTED",
            "FAILURE_MEMORY_APPLICABILITY_CHECK_REQUIRED",
        }):
            _append(codes, "FAILURE_MEMORY_ENFORCEMENT_INVALID")

    return sorted(codes)


def _resolve(container, path):
    cur = container
    for key in path:
        cur = cur[key]
    return cur


def apply_mutation(record: dict, packet: dict, context: dict, mutation: dict) -> None:
    root = {"record": record, "packet": packet, "context": context}[mutation["target"]]
    path = mutation["path"]
    op = mutation["op"]
    if op == "set":
        parent = _resolve(root, path[:-1]) if path[:-1] else root
        parent[path[-1]] = mutation["value"]
    elif op == "append":
        _resolve(root, path).append(mutation["value"])
    elif op == "delete_index":
        del _resolve(root, path)[mutation["index"]]
    elif op == "delete_key":
        parent = _resolve(root, path[:-1]) if path[:-1] else root
        del parent[path[-1]]
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
        print("usage: failure_memory_validator_v2.py failure_memory_tests_v2.json", file=sys.stderr)
        return 2
    spec = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    passed, total = run_tests(spec)
    print(f"{passed}/{total} tests passed")
    return 0 if passed == total else 1


if __name__ == "__main__":
    raise SystemExit(main())
