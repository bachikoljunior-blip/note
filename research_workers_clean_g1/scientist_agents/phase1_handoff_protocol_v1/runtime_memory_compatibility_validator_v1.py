#!/usr/bin/env python3
"""Deterministic semantic validator for runtime_memory_compatibility_v1.

This companion runs after candidate retrieval/admission. It checks that memory
injection for a particular decision step was revalidated against the current
state signature, current candidate set, memory snapshot and compatibility
policy. Empty injection is legal.
"""


def validate_runtime_compatibility(doc):
    codes = []
    runtime = doc.get("runtime", {})
    state = doc.get("state", {})
    candidates = doc.get("candidates", [])

    if runtime.get("checked_memory_snapshot_digest") != doc.get("memory_snapshot_digest"):
        codes.append("STALE_COMPATIBILITY_MEMORY_SNAPSHOT")
    if runtime.get("checked_policy_revision") != doc.get("compatibility_policy_revision"):
        codes.append("STALE_COMPATIBILITY_POLICY")
    if runtime.get("checked_state_revision") != state.get("state_revision"):
        codes.append("STALE_COMPATIBILITY_STATE_REVISION")
    if runtime.get("checked_state_signature_digest") != state.get("state_signature_digest"):
        codes.append("STALE_COMPATIBILITY_STATE_SIGNATURE")
    if runtime.get("checked_candidate_set_digest") != runtime.get("current_candidate_set_digest"):
        codes.append("STALE_COMPATIBILITY_CANDIDATE_SET")

    by_id = {}
    duplicate_candidate = False
    for candidate in candidates:
        record_id = candidate.get("record_id")
        if record_id in by_id:
            duplicate_candidate = True
        by_id[record_id] = candidate
    if duplicate_candidate:
        codes.append("DUPLICATE_COMPATIBILITY_CANDIDATE_ID")

    seen = set()
    for item in runtime.get("injected_memory", []):
        record_id = item.get("record_id")
        if record_id in seen and "DUPLICATE_COMPATIBILITY_INJECTION" not in codes:
            codes.append("DUPLICATE_COMPATIBILITY_INJECTION")
        seen.add(record_id)

        candidate = by_id.get(record_id)
        if candidate is None:
            if "UNKNOWN_COMPATIBILITY_MEMORY" not in codes:
                codes.append("UNKNOWN_COMPATIBILITY_MEMORY")
            continue
        if item.get("validated_packet_digest") != candidate.get("validated_packet_digest"):
            if "STALE_COMPATIBILITY_PACKET_DIGEST" not in codes:
                codes.append("STALE_COMPATIBILITY_PACKET_DIGEST")
        if candidate.get("compatibility") != "compatible":
            if "INCOMPATIBLE_MEMORY_INJECTION" not in codes:
                codes.append("INCOMPATIBLE_MEMORY_INJECTION")

    return codes


if __name__ == "__main__":
    import json
    import sys

    doc = json.load(sys.stdin)
    print(json.dumps({"codes": validate_runtime_compatibility(doc)}, indent=2))
