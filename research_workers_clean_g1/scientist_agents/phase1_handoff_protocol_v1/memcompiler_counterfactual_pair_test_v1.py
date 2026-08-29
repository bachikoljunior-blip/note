#!/usr/bin/env python3
"""Adversarial semantic tests for memcompiler_counterfactual_pair_validator_v1."""
import copy
import hashlib
import json

from memcompiler_counterfactual_pair_validator_v1 import validate


H = lambda c: c * 64


def digest(obj):
    return hashlib.sha256(
        json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def valid_packet():
    pre = {
        "implementation_revision": "ec5a5790",
        "compiler_artifact_id": "xinrui-23/sciworld-qwen2.5-14b",
        "compiler_artifact_revision_or_digest": "3c0bae02a6411205b97738e8ef59fd61c4905339",
        "task_id": "scienceworld-task-3",
        "task_text_sha256": H("1"),
        "dataset_blob_or_sha256": "dataset-revision-1",
        "memory_database_sha256": H("2"),
        "memory_updates_frozen": True,
        "retrieval_query_sha256": H("3"),
        "retrieval_config_sha256": H("4"),
        "candidate_pool_digest": H("5"),
        "target_step_index": 7,
        "environment_state_snapshot_sha256": H("6"),
        "state_revision": "state-7",
        "state_sha256": H("7"),
        "brief_state_sha256": H("8"),
        "selector_policy_revision_or_digest": "selector-v1",
        "selected_memory": [{"memory_id": "m-17", "content_sha256": H("9")}],
        "output_type": "EXPERIENCE",
        "compiled_guidance_sha256": H("a"),
        "selector_output_sha256": H("b"),
        "executor_policy_revision_or_digest": "executor-v1",
        "executor_sampling_config_sha256": H("c"),
        "rng_state_sha256": H("d"),
    }
    return {
        "schema_version": 1,
        "claim_scope": "fixed_selected_identity_receiver_effect",
        "varying_dimension": "receiver_effect",
        "source_trace_path": "trace.json",
        "source_trace_blob_or_sha256": "trace-blob-1",
        "pre_effect_binding": pre,
        "pre_effect_binding_sha256": digest(pre),
        "condition_a": {
            "condition_id": "inject",
            "receiver_effect": "inject",
            "receiver_effect_payload_sha256": H("a"),
            "executor_input_sha256": H("e"),
            "outcome_artifact_sha256": H("f"),
        },
        "condition_b": {
            "condition_id": "abstain",
            "receiver_effect": "abstain",
            "receiver_effect_payload_sha256": None,
            "executor_input_sha256": H("0"),
            "outcome_artifact_sha256": H("1"),
        },
    }


def mutate(name, packet):
    p = copy.deepcopy(packet)
    pre = p["pre_effect_binding"]
    if name == "wrong_claim_scope":
        p["claim_scope"] = "fixed_candidate_pool_state_conditioned"
    elif name == "wrong_varying_dimension":
        p["varying_dimension"] = "selector_policy"
    elif name == "pre_effect_digest_tamper":
        p["pre_effect_binding_sha256"] = H("f")
    elif name == "memory_not_frozen":
        pre["memory_updates_frozen"] = False
        p["pre_effect_binding_sha256"] = digest(pre)
    elif name == "no_selected_identity":
        pre["selected_memory"] = []
        p["pre_effect_binding_sha256"] = digest(pre)
    elif name == "duplicate_selected_identity":
        pre["selected_memory"].append(copy.deepcopy(pre["selected_memory"][0]))
        p["pre_effect_binding_sha256"] = digest(pre)
    elif name == "selector_no_memory_guidance":
        pre["output_type"] = "BRIEF"
        pre["compiled_guidance_sha256"] = None
        p["condition_a"]["receiver_effect_payload_sha256"] = None
        p["pre_effect_binding_sha256"] = digest(pre)
    elif name == "same_effect":
        p["condition_b"]["receiver_effect"] = "inject"
        p["condition_b"]["receiver_effect_payload_sha256"] = H("a")
    elif name == "inject_wrong_payload":
        p["condition_a"]["receiver_effect_payload_sha256"] = H("9")
    elif name == "abstain_has_payload":
        p["condition_b"]["receiver_effect_payload_sha256"] = H("a")
    elif name == "same_executor_input":
        p["condition_b"]["executor_input_sha256"] = p["condition_a"]["executor_input_sha256"]
    elif name == "same_outcome_artifact":
        p["condition_b"]["outcome_artifact_sha256"] = p["condition_a"]["outcome_artifact_sha256"]
    elif name == "same_condition_id":
        p["condition_b"]["condition_id"] = p["condition_a"]["condition_id"]
    else:
        raise KeyError(name)
    return p


def main():
    cases = [("valid_control", valid_packet(), True)]
    negatives = [
        "wrong_claim_scope",
        "wrong_varying_dimension",
        "pre_effect_digest_tamper",
        "memory_not_frozen",
        "no_selected_identity",
        "duplicate_selected_identity",
        "selector_no_memory_guidance",
        "same_effect",
        "inject_wrong_payload",
        "abstain_has_payload",
        "same_executor_input",
        "same_outcome_artifact",
        "same_condition_id",
    ]
    for name in negatives:
        cases.append((name, mutate(name, valid_packet()), False))

    results = []
    for name, packet, expected in cases:
        errors = validate(packet)
        actual = not errors
        results.append({
            "case": name,
            "expected_valid": expected,
            "actual_valid": actual,
            "matched": actual == expected,
            "errors": errors,
        })

    print(json.dumps(results, indent=2, sort_keys=True))
    raise SystemExit(0 if all(x["matched"] for x in results) else 1)


if __name__ == "__main__":
    main()
