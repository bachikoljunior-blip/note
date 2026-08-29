#!/usr/bin/env python3
"""Semantic validator for generic_residual_boundary_v1.

The packet is intentionally not a success/acceptance packet. It records a
fully prepared remainder only after all safe Chat-capable predecessors are
complete, binds the observed unavailable/protected capability to immutable
evidence, and leaves final irreducibility acceptance to a separate authority.
"""


def validate_generic_residual_boundary(doc, context):
    codes = []
    task = doc.get("task", {})
    residual = doc.get("residual", {})
    classification = doc.get("classification", {})

    if (task.get("head_sha") != context.get("current_head_sha")
            or task.get("revision") != context.get("current_revision")):
        codes.append("STALE_BOUNDARY_TASK")

    if any(item.get("status") != "complete" for item in doc.get("chat_predecessors", [])):
        codes.append("CHAT_CAPABLE_PREDECESSOR_INCOMPLETE")

    if residual.get("required_capability") in set(doc.get("sender", {}).get("capabilities", [])):
        codes.append("REDUCIBLE_BOUNDARY")

    if residual.get("sender_execution_attempted") is True:
        codes.append("PROTECTED_EFFECT_EXECUTED_BY_SENDER")

    evidence = doc.get("evidence", [])
    evidence_digests = {item.get("digest") for item in evidence}
    if residual.get("availability_evidence_digest") not in evidence_digests:
        codes.append("MISSING_AVAILABILITY_EVIDENCE")

    predecessor_digests = {item.get("evidence_digest") for item in doc.get("chat_predecessors", [])}
    if not predecessor_digests.issubset(evidence_digests):
        codes.append("MISSING_PREDECESSOR_EVIDENCE")

    if any(item.get("immutable") is not True for item in evidence):
        codes.append("MUTABLE_BOUNDARY_EVIDENCE")

    if classification.get("clean_acceptance_claimed") is True:
        codes.append("CLEAN_FINAL_ACCEPTANCE_CLAIM")
    if classification.get("downstream_verification_required") is not True:
        codes.append("MISSING_DOWNSTREAM_VERIFICATION")

    expected_actor = {
        "protected_primary_writer": "protected_authority_holder",
        "exclusive_external_authority": "exclusive_external_authority_holder",
        "user_only_input_or_authorization": "user_input_owner",
    }.get(residual.get("boundary_kind"))
    if expected_actor and doc.get("external_action_required", {}).get("actor_class") != expected_actor:
        codes.append("BOUNDARY_ACTOR_MISMATCH")

    return sorted(set(codes))


if __name__ == "__main__":
    import json
    import sys
    payload = json.load(sys.stdin)
    print(json.dumps({"codes": validate_generic_residual_boundary(payload["doc"], payload["context"])}, indent=2))
