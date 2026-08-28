#!/usr/bin/env python3
"""Deterministic semantic validator for memory_admission_runtime_v1.

This is a companion to the per-record failure_memory_validator_v2. It assumes
candidate packets have already passed that validator and checks the later
runtime transition from validated receiver decisions to actual memory injection.
"""


def validate_runtime_admission(doc):
    codes = []
    candidates = doc.get("candidates", [])
    runtime = doc.get("runtime", {})

    by_id = {}
    duplicate_candidate = False
    for c in candidates:
        rid = c.get("record_id")
        if rid in by_id:
            duplicate_candidate = True
        by_id[rid] = c
    if duplicate_candidate:
        codes.append("DUPLICATE_CANDIDATE_ID")

    if runtime.get("selection_context_digest") != doc.get("admission_context_digest"):
        codes.append("STALE_RUNTIME_ADMISSION_CONTEXT")
    if runtime.get("selection_policy_revision") != doc.get("admission_policy_revision"):
        codes.append("STALE_RUNTIME_ADMISSION_POLICY")

    selected = runtime.get("selected_memory", [])
    seen_selected = set()
    for s in selected:
        rid = s.get("record_id")
        if rid in seen_selected and "DUPLICATE_RUNTIME_MEMORY_SELECTION" not in codes:
            codes.append("DUPLICATE_RUNTIME_MEMORY_SELECTION")
        seen_selected.add(rid)

        candidate = by_id.get(rid)
        if candidate is None:
            if "UNKNOWN_RUNTIME_MEMORY" not in codes:
                codes.append("UNKNOWN_RUNTIME_MEMORY")
            continue
        if s.get("validated_packet_digest") != candidate.get("validated_packet_digest"):
            if "STALE_RUNTIME_MEMORY_DIGEST" not in codes:
                codes.append("STALE_RUNTIME_MEMORY_DIGEST")
        if candidate.get("receiver_decision") != "adopt":
            if "FORCED_MEMORY_AFTER_ABSTENTION" not in codes:
                codes.append("FORCED_MEMORY_AFTER_ABSTENTION")

    any_adopt = any(c.get("receiver_decision") == "adopt" for c in candidates)
    if runtime.get("fallback_policy") == "force_nonempty" and not any_adopt:
        codes.append("FORCE_NONEMPTY_POLICY_WITHOUT_ADOPTED_MEMORY")

    return codes


if __name__ == "__main__":
    import json
    import sys
    doc = json.load(sys.stdin)
    print(json.dumps({"codes": validate_runtime_admission(doc)}, indent=2))
