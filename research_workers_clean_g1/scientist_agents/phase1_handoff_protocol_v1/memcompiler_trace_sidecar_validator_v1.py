#!/usr/bin/env python3
"""Semantic validator for memcompiler_trace_sidecar_v1.

The sidecar is deliberately content-bounded: raw memory text is not required.
It binds a frozen memory database and once-per-episode candidate pool to
per-step selector outputs so a later counterfactual can distinguish
"same candidate pool" from "same selected identity".
"""
import hashlib
import json
import sys


def _pool_digest(entries):
    canonical = sorted(
        ({"memory_id": x["memory_id"], "content_sha256": x["content_sha256"]} for x in entries),
        key=lambda x: (x["memory_id"], x["content_sha256"]),
    )
    blob = json.dumps(canonical, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(blob).hexdigest()


def _selector_digest(step):
    payload = {
        "output_type": step["output_type"],
        "selected_memory": sorted(
            step["selected_memory"],
            key=lambda x: (x["memory_id"], x["content_sha256"]),
        ),
        "compiled_guidance_sha256": step["compiled_guidance_sha256"],
    }
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(blob).hexdigest()


def validate(packet):
    errors = []
    if packet.get("memory_updates_frozen") is not True:
        errors.append("memory_updates_not_frozen")

    snap = packet.get("retrieval_snapshot", {})
    pool = snap.get("candidate_pool", [])
    expected_pool_digest = _pool_digest(pool)
    if snap.get("candidate_pool_digest") != expected_pool_digest:
        errors.append("candidate_pool_digest_mismatch")

    identities = [(x.get("memory_id"), x.get("content_sha256")) for x in pool]
    if len(identities) != len(set(identities)):
        errors.append("duplicate_candidate_identity")

    pool_map = {x["memory_id"]: x["content_sha256"] for x in pool}
    seen_steps = set()
    for step in packet.get("steps", []):
        idx = step.get("step_index")
        if idx in seen_steps:
            errors.append(f"duplicate_step_index:{idx}")
        seen_steps.add(idx)

        if step.get("candidate_pool_digest") != snap.get("candidate_pool_digest"):
            errors.append(f"step_candidate_pool_drift:{idx}")

        seen_selected = set()
        for ref in step.get("selected_memory", []):
            mid = ref.get("memory_id")
            dg = ref.get("content_sha256")
            if mid in seen_selected:
                errors.append(f"duplicate_selected_memory:{idx}:{mid}")
            seen_selected.add(mid)
            if mid not in pool_map:
                errors.append(f"selected_memory_not_in_pool:{idx}:{mid}")
            elif pool_map[mid] != dg:
                errors.append(f"selected_memory_digest_mismatch:{idx}:{mid}")

        output = step.get("output_type")
        selected = step.get("selected_memory", [])
        guidance = step.get("compiled_guidance_sha256")
        effect = step.get("receiver_effect")

        if output in ("EXPERIENCE", "HYBRID"):
            if not selected:
                errors.append(f"memory_output_without_selected_identity:{idx}")
            if guidance is None:
                errors.append(f"memory_output_without_guidance_digest:{idx}")
            if effect != "inject":
                errors.append(f"memory_output_not_injected:{idx}")
        elif output == "NOACTION":
            if selected:
                errors.append(f"noaction_has_selected_memory:{idx}")
            if guidance is not None:
                errors.append(f"noaction_has_guidance:{idx}")
            if effect != "abstain":
                errors.append(f"noaction_not_abstain:{idx}")
        elif output == "BRIEF":
            if effect != "abstain":
                errors.append(f"brief_only_injected_as_memory:{idx}")

        if step.get("selector_output_sha256") != _selector_digest(step):
            errors.append(f"selector_output_digest_mismatch:{idx}")

    return errors


def main():
    packet = json.load(sys.stdin)
    errors = validate(packet)
    print(json.dumps({"valid": not errors, "errors": errors}, sort_keys=True))
    raise SystemExit(0 if not errors else 1)


if __name__ == "__main__":
    main()
