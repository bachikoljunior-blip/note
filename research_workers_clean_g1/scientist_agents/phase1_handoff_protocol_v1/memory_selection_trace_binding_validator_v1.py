#!/usr/bin/env python3
"""Semantic validator for memory_selection_trace_binding_v1.

The JSON Schema intentionally admits structurally valid overclaim cases. This
validator enforces cross-condition causal identity constraints.
"""
import json
import sys


def validate(packet):
    errors = []
    required = [
        "schema_version", "claim_level", "implementation_revision",
        "memory_bank_digest", "candidate_pool_digest", "memory_updates_frozen",
        "state_digest", "selector_policy_digest", "manipulated_variable",
        "conditions",
    ]
    for key in required:
        if key not in packet:
            errors.append(f"missing:{key}")
    if errors:
        return errors

    if packet["memory_updates_frozen"] is not True:
        errors.append("memory_updates_not_frozen")

    conditions = packet["conditions"]
    if len(conditions) < 2:
        errors.append("need_two_conditions")

    if packet["claim_level"] == "fixed_selected_identity_acceptance":
        if packet["manipulated_variable"] != "receiver_acceptance":
            errors.append("wrong_manipulated_variable")

        traces = []
        for condition in conditions:
            name = condition.get("name", "unknown")
            if condition.get("selection_trace_available") is not True:
                errors.append(f"selection_trace_unavailable:{name}")
                continue
            selected = condition.get("selected_memory")
            if selected is None:
                errors.append(f"selected_memory_missing:{name}")
                continue
            traces.append(tuple((item["id"], item["digest"]) for item in selected))

        if traces and any(trace != traces[0] for trace in traces[1:]):
            errors.append("selected_identity_differs")

        guidance = [c.get("compiled_guidance_digest") for c in conditions]
        if any(value is None for value in guidance):
            errors.append("compiled_guidance_digest_missing")
        elif guidance and any(value != guidance[0] for value in guidance[1:]):
            errors.append("compiled_guidance_differs")

        decisions = {c.get("injection_decision") for c in conditions}
        if not {"inject", "abstain"}.issubset(decisions):
            errors.append("acceptance_not_contrasted")

    elif packet["claim_level"] == "fixed_candidate_pool_state_conditioned":
        if not packet["candidate_pool_digest"]:
            errors.append("candidate_pool_digest_missing")
    else:
        errors.append("unknown_claim_level")

    return errors


def main():
    packet = json.load(sys.stdin)
    errors = validate(packet)
    print(json.dumps({"valid": not errors, "errors": errors}, sort_keys=True))
    raise SystemExit(0 if not errors else 1)


if __name__ == "__main__":
    main()
