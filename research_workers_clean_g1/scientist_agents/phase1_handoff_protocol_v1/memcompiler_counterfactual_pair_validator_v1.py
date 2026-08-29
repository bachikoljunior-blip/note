#!/usr/bin/env python3
"""Validate fixed-selected-identity inject-vs-abstain counterfactual pairs.

This checks causal-isolation provenance, not whether injection improves an
outcome. A valid pair has one canonical pre-effect binding so memory state,
selected identity, compiled guidance, environment snapshot, executor policy,
sampling configuration and RNG state cannot drift between conditions. Only the
final receiver effect may vary.
"""
import hashlib
import json
import sys


def _digest(obj):
    blob = json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(blob).hexdigest()


def validate(packet):
    errors = []

    if packet.get("claim_scope") != "fixed_selected_identity_receiver_effect":
        errors.append("claim_scope_not_fixed_selected_identity_receiver_effect")
    if packet.get("varying_dimension") != "receiver_effect":
        errors.append("varying_dimension_not_receiver_effect")

    pre = packet.get("pre_effect_binding", {})
    if packet.get("pre_effect_binding_sha256") != _digest(pre):
        errors.append("pre_effect_binding_digest_mismatch")

    if pre.get("memory_updates_frozen") is not True:
        errors.append("memory_updates_not_frozen")

    selected = pre.get("selected_memory", [])
    if not selected:
        errors.append("selected_identity_missing")
    identities = [(x.get("memory_id"), x.get("content_sha256")) for x in selected]
    if len(identities) != len(set(identities)):
        errors.append("duplicate_selected_identity")

    if pre.get("output_type") not in ("EXPERIENCE", "HYBRID"):
        errors.append("selector_output_not_memory_bearing")
    guidance = pre.get("compiled_guidance_sha256")
    if guidance is None:
        errors.append("compiled_guidance_missing")

    critical = [
        "implementation_revision",
        "compiler_artifact_id",
        "compiler_artifact_revision_or_digest",
        "task_id",
        "task_text_sha256",
        "dataset_blob_or_sha256",
        "memory_database_sha256",
        "retrieval_query_sha256",
        "retrieval_config_sha256",
        "candidate_pool_digest",
        "target_step_index",
        "environment_state_snapshot_sha256",
        "state_revision",
        "state_sha256",
        "brief_state_sha256",
        "selector_policy_revision_or_digest",
        "selector_output_sha256",
        "executor_policy_revision_or_digest",
        "executor_sampling_config_sha256",
        "rng_state_sha256",
    ]
    for key in critical:
        value = pre.get(key)
        if value is None or value == "":
            errors.append(f"missing_pre_effect_binding:{key}")

    if not packet.get("source_trace_path") or not packet.get("source_trace_blob_or_sha256"):
        errors.append("source_trace_binding_missing")

    a = packet.get("condition_a", {})
    b = packet.get("condition_b", {})
    if a.get("condition_id") == b.get("condition_id"):
        errors.append("condition_ids_not_distinct")

    effects = {a.get("receiver_effect"), b.get("receiver_effect")}
    if effects != {"inject", "abstain"}:
        errors.append("pair_must_contain_exactly_inject_and_abstain")

    for cond in (a, b):
        effect = cond.get("receiver_effect")
        payload = cond.get("receiver_effect_payload_sha256")
        cid = cond.get("condition_id", "unknown")
        if effect == "inject" and payload != guidance:
            errors.append(f"inject_payload_not_compiled_guidance:{cid}")
        if effect == "abstain" and payload is not None:
            errors.append(f"abstain_payload_must_be_null:{cid}")

    # The intervention must reach the executor. If the two executor-input
    # digests are identical, the claimed inject-vs-abstain effect was not
    # actually materialized at the receiver boundary.
    if a.get("executor_input_sha256") == b.get("executor_input_sha256"):
        errors.append("receiver_effect_not_materialized_in_executor_input")

    # Outcome artifacts must be separately bound so an evaluator cannot reuse
    # one cached result as evidence for both conditions.
    if a.get("outcome_artifact_sha256") == b.get("outcome_artifact_sha256"):
        errors.append("outcome_artifacts_not_independently_bound")

    return errors


def main():
    packet = json.load(sys.stdin)
    errors = validate(packet)
    print(json.dumps({"valid": not errors, "errors": errors}, sort_keys=True))
    raise SystemExit(0 if not errors else 1)


if __name__ == "__main__":
    main()
