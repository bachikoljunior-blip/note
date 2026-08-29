#!/usr/bin/env python3
import json
import sys
from pathlib import Path
from jsonschema import Draft202012Validator

SCHEMA_PATH = Path(__file__).with_name("paired_intervention_randomness_provider_binding_v1.schema.json")


def looks_floating(value: str) -> bool:
    x = value.strip().lower()
    return x in {"latest", "current", "unknown", "unversioned", "none", "na", "n/a"} or x.startswith("floating:")


def validate_bundle(bundle, schema=None):
    if schema is None:
        schema = json.loads(SCHEMA_PATH.read_text())
    structural = []
    for error in Draft202012Validator(schema).iter_errors(bundle):
        structural.append("schema:" + "/".join(map(str, error.path)) + ":" + error.message)
    if structural:
        return structural

    errors = []
    inference = bundle["inference_contract"]
    randomness = inference["randomness_control"]

    if looks_floating(inference["model_revision"]):
        errors.append("model_revision_must_be_immutable_not_floating")
    if looks_floating(inference["provider_execution_revision"]):
        errors.append("provider_execution_revision_must_be_immutable_not_floating")

    method = randomness["method"]
    if method == "explicit_seed":
        if "inference_seed" not in randomness or "provider_seed_semantics_digest" not in randomness:
            errors.append("explicit_seed_requires_inference_seed_and_provider_seed_semantics_digest")
    elif method == "captured_rng_state":
        if "rng_state_digest" not in randomness:
            errors.append("captured_rng_state_requires_rng_state_digest")
    elif method == "replay_equivalence":
        if "replay_equivalence_digest" not in randomness:
            errors.append("replay_equivalence_requires_replay_equivalence_digest")
    elif method == "temperature_zero":
        errors.append("temperature_zero_is_not_inference_randomness_binding")
    elif method == "selection_seed_only":
        errors.append("dataset_selection_seed_is_not_inference_randomness_binding")

    common_randomness_evidence = randomness["evidence_digest"]
    candidate_digest = bundle["candidate_intervention_digest"]
    seen = set()
    baseline_successes = 0
    intervention_successes = 0
    repairs = 0
    regressions = 0

    for i, pair in enumerate(bundle["pairs"]):
        instance_id = pair["instance_id"]
        if instance_id in seen:
            errors.append(f"duplicate_instance_id:{instance_id}")
        seen.add(instance_id)

        baseline = pair["baseline"]
        intervention = pair["intervention"]

        if baseline["receiver_effect"] != "absent":
            errors.append(f"pair[{i}]:baseline_receiver_effect_must_be_absent")
        if baseline["injected_intervention_digest"] is not None:
            errors.append(f"pair[{i}]:baseline_must_not_inject_intervention")
        if intervention["receiver_effect"] != "present":
            errors.append(f"pair[{i}]:intervention_receiver_effect_must_be_present")
        if intervention["injected_intervention_digest"] != candidate_digest:
            errors.append(f"pair[{i}]:intervention_digest_mismatch")
        if (
            baseline["randomness_evidence_digest"] != common_randomness_evidence
            or intervention["randomness_evidence_digest"] != common_randomness_evidence
        ):
            errors.append(f"pair[{i}]:randomness_evidence_not_common_binding")
        if baseline["trajectory_digest"] == intervention["trajectory_digest"]:
            errors.append(f"pair[{i}]:trajectory_digest_reused_across_arms")
        if baseline["inference_request_digest"] == intervention["inference_request_digest"]:
            errors.append(f"pair[{i}]:request_digest_must_reflect_intervention_delta")

        if baseline["success"]:
            baseline_successes += 1
        if intervention["success"]:
            intervention_successes += 1
        if (not baseline["success"]) and intervention["success"]:
            repairs += 1
        if baseline["success"] and (not intervention["success"]):
            regressions += 1

    expected = {
        "n_pairs": len(bundle["pairs"]),
        "baseline_successes": baseline_successes,
        "intervention_successes": intervention_successes,
        "repair_count": repairs,
        "regression_count": regressions,
        "net_gain": repairs - regressions,
    }
    for key, expected_value in expected.items():
        got = bundle["summary"][key]
        if got != expected_value:
            errors.append(f"summary_mismatch:{key}:expected={expected_value}:got={got}")

    return errors


def main():
    if len(sys.argv) != 2:
        raise SystemExit("usage: paired_intervention_randomness_provider_binding_validator_v1.py <bundle.json>")
    bundle = json.loads(Path(sys.argv[1]).read_text())
    errors = validate_bundle(bundle)
    print(json.dumps({"accepted": not errors, "errors": errors}, indent=2))
    raise SystemExit(0 if not errors else 1)


if __name__ == "__main__":
    main()
