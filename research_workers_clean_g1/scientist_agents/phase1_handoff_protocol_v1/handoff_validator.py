#!/usr/bin/env python3
"""Semantic validator and adversarial test runner for handoff_packet.schema.json.

The JSON Schema handles structure. This runner handles cross-field invariants
that JSON Schema cannot express directly (digest equality, freshness, authority
intersection, idempotent replay reconciliation, and terminal-evidence rules).

Usage:
    python handoff_validator.py handoff_adversarial_tests.json
"""
from __future__ import annotations
import copy
import hashlib
import json
import sys
from pathlib import Path

def sha256_text(text: str) -> str:
    return "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()

def semantic_validate(packet: dict, context: dict) -> list[str]:
    codes: list[str] = []

    # Fresh task identity.
    if (packet["task"]["head_sha"] != context["current_head_sha"]
            or packet["task"]["revision"] != context["current_revision"]):
        codes.append("STALE_REVISION")

    required = set(packet["handoff"]["required_capabilities"])
    sender_caps = set(packet["sender"]["capabilities"])
    receiver_caps = set(packet["receiver"]["capabilities"])
    allowed_caps = set(packet["scope"]["allowed_capabilities"])
    reason = packet["handoff"]["reason_kind"]
    authority_mode = packet["handoff"]["authority_mode"]

    # Irreducibility: routine delegation is forbidden. A sender may request an
    # independently owned exclusive capability only when it does not possess it.
    if reason in {"missing_capability", "missing_credential",
                  "exclusive_instrument_authority"}:
        if required & sender_caps:
            codes.append("HANDOFF_NOT_IRREDUCIBLE")
        if authority_mode != "independent_exclusive":
            codes.append("AUTHORITY_MODE_INVALID")
    elif reason == "independent_certification":
        if (packet["sender"]["actor_id"] == packet["receiver"]["actor_id"]
                or authority_mode != "independent_exclusive"):
            codes.append("HANDOFF_NOT_IRREDUCIBLE")

    # No authority amplification. Delegated authority must additionally be
    # possessed by the sender; independently owned exclusive authority need not.
    if not allowed_caps.issubset(required) or not allowed_caps.issubset(receiver_caps):
        codes.append("AUTHORITY_AMPLIFICATION")
    if authority_mode == "delegated" and not allowed_caps.issubset(sender_caps):
        codes.append("AUTHORITY_AMPLIFICATION")

    # Requested action must be inspectable and within the explicit role scope.
    if not packet["scope"]["inspectable"]:
        codes.append("UNINSPECTABLE_ACTION")
    allowed_actions = {
        item["kind"]: item["required_capability"]
        for item in packet["scope"]["allowed_actions"]
    }
    if packet["action"]["kind"] not in allowed_actions:
        codes.append("ROLE_SCOPE_VIOLATION")
    else:
        required_cap = allowed_actions[packet["action"]["kind"]
        if required_cap not in allowed_caps:
            codes.append("ROLE_SCOPE_VIOLATION")

    # Claims do not substitute for artifacts. Inputs and the pending action must
    # exist as immutable, digest-addressed artifacts.
    artifact_digests = {a["digest"] for a in packet["artifacts"]}
    pending_digests = {
        a["digest"] for a in packet["artifacts"]
        if a["role"] == "pending_action"
    }
    if (not set(packet["action"]["input_digests"]).issubset(artifact_digests)
            or packet["action"]["action_digest"] not in pending_digests):
        codes.append("MISSING_ARTIFACT")

    # Approval binds to exact executable content and exact referenced inputs.
    if sha256_text(packet["action"]["canonical_payload"]) != packet["action"]["action_digest"]:
        codes.append("ACTION_DIGEST_MISMATCH")
    if (packet["authorization"]["bound_action_digest"] != packet["action"]["action_digest"]
            or set(packet["authorization"]["bound_input_digests"])
               != set(packet["action"]["input_digests"])):
        codes.append("ACTION_BINDING_MISMATCH")
    if not packet["authorization"]["single_use"]:
        codes.append("AUTHORIZATION_REUSABLE")

    # Retry after an observed external effect requires explicit reconciliation.
    key = packet["action"]["idempotency_key"]
    seen = set(context.get("seen_idempotency_keys", []))
    reconciled = set(context.get("reconciled_idempotency_keys", []))
    if key in seen and key not in reconciled:
        codes.append("DUPLICATE_REPLAY")

    # Raw negative/abandoned branches remain immutable source evidence. Derived
    # summaries may be added elsewhere but cannot replace or mutate the sources.
    if any(not branch["immutable"] for branch in packet["negative_branches"]):
        codes.append("NEGATIVE_BRANCH_MUTABLE")

    # An LLM verdict is advisory; terminal success is derived from deterministic
    # or external-state evidence and every required check must pass.
    if packet["status"] == "complete":
        if packet["verification"]["terminal_verifier_kind"] == "llm_only":
            codes.append("LLM_VERIFIER_TERMINAL")
        results = packet["verification"]["results"]
        if any(results.get(check) != "pass"
               for check in packet["verification"]["required_checks"]):
            codes.append("FALSE_COMPLETION")

    # Control returns only with the evidence named by the handoff contract.
    if packet["status"] in {"executed", "complete"}:
        required_kinds = set(packet["return_contract"]["required_evidence_kinds"])
        observed_kinds = {
            item["kind"] for item in packet["return_contract"]["return_evidence"]
        }
        if not required_kinds.issubset(observed_kinds):
            codes.append("MISSING_RETURN_EVIDENCE")

    return sorted(set(codes))

def _resolve(container, path):
    cur = container
    for key in path:
        cur = cur[key]
    return cur

def apply_mutation(packet: dict, context: dict, mutation: dict) -> None:
    root = packet if mutation["target"] == "packet" else context
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
        packet = copy.deepcopy(spec["base_packet"])
        context = copy.deepcopy(spec["base_context"])
        for mutation in case["mutations"]:
            apply_mutation(packet, context, mutation)
        codes = semantic_validate(packet, context)
        if case["should_pass"]:
            ok = not codes
        else:
            ok = all(code in codes for code in case["expected_failure_codes"])
        status = "PASS" if ok else "FAIL"
        print(f"{status} {case['name']}: {codes}")
        passed += int(ok)
    return passed, total

def main() -> int:
    if len(sys.argv) != 2:
        print("usage: handoff_validator.py handoff_adversarial_tests.json", file=sys.stderr)
        return 2
    spec = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    passed, total = run_tests(spec)
    print(f"{passed}/{total} tests passed")
    return 0 if passed == total else 1

if __name__ == "__main__":
    raise SystemExit(main())
