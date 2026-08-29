#!/usr/bin/env python3
import copy
import hashlib
import json
from pathlib import Path

from paired_intervention_randomness_provider_binding_validator_v1 import validate_bundle


def dg(text):
    return "sha256:" + hashlib.sha256(text.encode()).hexdigest()


BASE = {
    "protocol_version": "p1-protocol-063-v1",
    "bundle_id": "example",
    "source_revision": "abcdef1234567890",
    "dataset_manifest_digest": dg("dataset"),
    "dataset_selection_seed": 42,
    "candidate_intervention_digest": dg("skill"),
    "inference_contract": {
        "provider": "example-provider",
        "model_id": "example-model",
        "model_revision": "immutable-model-rev",
        "provider_execution_revision": "immutable-provider-exec-rev",
        "decoding_config_digest": dg("decode"),
        "randomness_control": {
            "method": "explicit_seed",
            "evidence_digest": dg("rng-evidence"),
            "inference_seed": 42,
            "provider_seed_semantics_digest": dg("seed-semantics"),
        },
    },
    "judge_contract": {
        "judge_id": "judge",
        "judge_revision": "judge-rev",
        "judge_config_digest": dg("judge-config"),
    },
    "pairs": [
        {
            "instance_id": "i1",
            "instance_digest": dg("i1"),
            "environment_snapshot_digest": dg("env1"),
            "baseline": {
                "receiver_effect": "absent",
                "injected_intervention_digest": None,
                "trajectory_digest": dg("b1traj"),
                "inference_request_digest": dg("b1req"),
                "inference_response_digest": dg("b1resp"),
                "randomness_evidence_digest": dg("rng-evidence"),
                "success": False,
            },
            "intervention": {
                "receiver_effect": "present",
                "injected_intervention_digest": dg("skill"),
                "trajectory_digest": dg("t1traj"),
                "inference_request_digest": dg("t1req"),
                "inference_response_digest": dg("t1resp"),
                "randomness_evidence_digest": dg("rng-evidence"),
                "success": True,
            },
        },
        {
            "instance_id": "i2",
            "instance_digest": dg("i2"),
            "environment_snapshot_digest": dg("env2"),
            "baseline": {
                "receiver_effect": "absent",
                "injected_intervention_digest": None,
                "trajectory_digest": dg("b2traj"),
                "inference_request_digest": dg("b2req"),
                "inference_response_digest": dg("b2resp"),
                "randomness_evidence_digest": dg("rng-evidence"),
                "success": True,
            },
            "intervention": {
                "receiver_effect": "present",
                "injected_intervention_digest": dg("skill"),
                "trajectory_digest": dg("t2traj"),
                "inference_request_digest": dg("t2req"),
                "inference_response_digest": dg("t2resp"),
                "randomness_evidence_digest": dg("rng-evidence"),
                "success": False,
            },
        },
    ],
    "summary": {
        "n_pairs": 2,
        "baseline_successes": 1,
        "intervention_successes": 1,
        "repair_count": 1,
        "regression_count": 1,
        "net_gain": 0,
    },
}


def case(name):
    d = copy.deepcopy(BASE)
    rc = d["inference_contract"]["randomness_control"]
    if name == "accept_explicit_inference_seed_with_provider_semantics":
        pass
    elif name == "reject_selection_seed_only":
        rc["method"] = "selection_seed_only"
    elif name == "reject_temperature_zero_as_randomness_binding":
        rc["method"] = "temperature_zero"
    elif name == "reject_missing_provider_seed_semantics":
        rc.pop("provider_seed_semantics_digest")
    elif name == "accept_captured_rng_state":
        rc["method"] = "captured_rng_state"
        rc["rng_state_digest"] = dg("rng-state")
        rc.pop("inference_seed", None)
        rc.pop("provider_seed_semantics_digest", None)
    elif name == "accept_replay_equivalence":
        rc["method"] = "replay_equivalence"
        rc["replay_equivalence_digest"] = dg("replay")
        rc.pop("inference_seed", None)
        rc.pop("provider_seed_semantics_digest", None)
    elif name == "reject_floating_model_revision":
        d["inference_contract"]["model_revision"] = "latest"
    elif name == "reject_floating_provider_execution_revision":
        d["inference_contract"]["provider_execution_revision"] = "unknown"
    elif name == "reject_rng_evidence_drift":
        d["pairs"][1]["intervention"]["randomness_evidence_digest"] = dg("other")
    elif name == "reject_baseline_injects_intervention":
        d["pairs"][0]["baseline"]["injected_intervention_digest"] = dg("skill")
    elif name == "reject_intervention_digest_mismatch":
        d["pairs"][0]["intervention"]["injected_intervention_digest"] = dg("other-skill")
    elif name == "reject_duplicate_instance_id":
        d["pairs"][1]["instance_id"] = "i1"
    elif name == "reject_request_digest_not_changed_by_effect":
        d["pairs"][0]["intervention"]["inference_request_digest"] = d["pairs"][0]["baseline"]["inference_request_digest"]
    elif name == "reject_trajectory_digest_reuse":
        d["pairs"][0]["intervention"]["trajectory_digest"] = d["pairs"][0]["baseline"]["trajectory_digest"]
    elif name == "reject_nonrecomputable_summary":
        d["summary"]["net_gain"] = 9
    else:
        raise KeyError(name)
    return d


def main():
    manifest = json.loads(Path(__file__).with_name(
        "paired_intervention_randomness_provider_binding_test_manifest_v1.json"
    ).read_text())
    rows = []
    for test in manifest["tests"]:
        errors = validate_bundle(case(test["name"]))
        actual_accept = not errors
        rows.append({
            "name": test["name"],
            "expected_accept": test["expected_accept"],
            "actual_accept": actual_accept,
            "pass": actual_accept == test["expected_accept"],
            "errors": errors,
        })
    print(json.dumps(rows, indent=2))
    if not all(row["pass"] for row in rows):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
