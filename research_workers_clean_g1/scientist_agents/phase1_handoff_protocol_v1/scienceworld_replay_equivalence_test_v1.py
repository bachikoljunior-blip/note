#!/usr/bin/env python3
import copy
import hashlib
import json
from pathlib import Path

import jsonschema

from scienceworld_replay_equivalence_validator_v1 import environment_binding, validate

HERE = Path(__file__).resolve().parent
SCHEMA = json.loads((HERE / "scienceworld_replay_equivalence_v1.schema.json").read_text())


def h(s):
    return hashlib.sha256(s.encode()).hexdigest()


def d(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def base_packet():
    steps = [
        {"index": 0, "action": "look around", "action_sha256": h("look around"), "observation_sha256": h("obs0"), "reward_sha256": h("reward0"), "done": False, "info_sha256": h("info0")},
        {"index": 1, "action": "open door", "action_sha256": h("open door"), "observation_sha256": h("obs1"), "reward_sha256": h("reward1"), "done": False, "info_sha256": h("info1")},
    ]
    p = {
        "schema_version": 1,
        "claim_scope": "exact_branch_state_replay",
        "scienceworld": {
            "package_version": "1.2.2",
            "source_revision_or_artifact_digest": "pypi:scienceworld==1.2.2",
            "jar_sha256": h("jar"),
            "task_name": "task-1-boil",
            "variation_idx": 0,
            "simplification_str": "teleportAction",
            "env_step_limit": 100,
        },
        "reconstruction": {
            "mode": "action_prefix_replay",
            "native_snapshot_sha256": None,
            "reset_observation_sha256": h("resetobs"),
            "reset_object_tree_sha256": h("tree"),
            "reset_api_snapshot_sha256": h("api"),
            "action_prefix": steps,
            "action_prefix_sha256": d(steps),
            "branch_state_sha256": h("branch"),
            "replay_probe": {
                "run_count": 8,
                "all_branch_states_equal": True,
                "branch_state_sha256s": [h("branch")] * 8,
                "all_trace_digests_equal": True,
                "trace_sha256s": [h("trace")] * 8,
            },
        },
        "counterfactual_pair": {
            "condition_a_environment_binding_sha256": "0" * 64,
            "condition_b_environment_binding_sha256": "0" * 64,
            "same_environment_binding_required": True,
        },
        "evidence_scope": "exact task/variation/simplification/action-prefix only",
    }
    eh = environment_binding(p)
    p["counterfactual_pair"]["condition_a_environment_binding_sha256"] = eh
    p["counterfactual_pair"]["condition_b_environment_binding_sha256"] = eh
    return p


def recalc_pair(p):
    eh = environment_binding(p)
    p["counterfactual_pair"]["condition_a_environment_binding_sha256"] = eh
    p["counterfactual_pair"]["condition_b_environment_binding_sha256"] = eh


def cases():
    out = []
    def add(name, mutate, expected):
        p = base_packet()
        mutate(p)
        out.append((name, p, expected))

    add("valid_1_2_exact_prefix_8x", lambda p: None, True)
    def valid13(p):
        p["scienceworld"]["package_version"] = "1.3.0"
        p["scienceworld"]["source_revision_or_artifact_digest"] = "git:e8216d6044e8e39be9fcb185e3b2dfb602584b52"
        recalc_pair(p)
    add("valid_1_3_exact_prefix_8x", valid13, True)
    def native(p):
        p["claim_scope"] = "native_snapshot"
        p["reconstruction"]["mode"] = "native_snapshot"
        p["reconstruction"]["native_snapshot_sha256"] = h("snapshot")
        recalc_pair(p)
    add("valid_native_snapshot", native, True)
    add("fail_1_2_probe_too_small", lambda p: p["reconstruction"]["replay_probe"].update({"run_count": 2, "branch_state_sha256s": [h("branch")] * 2, "trace_sha256s": [h("trace")] * 2}), False)
    add("fail_branch_states_differ", lambda p: p["reconstruction"]["replay_probe"].update({"all_branch_states_equal": False, "branch_state_sha256s": [h("branch")] * 7 + [h("branch2")]}), False)
    add("fail_trace_digests_differ", lambda p: p["reconstruction"]["replay_probe"].update({"all_trace_digests_equal": False, "trace_sha256s": [h("trace")] * 7 + [h("trace2")]}), False)
    add("fail_action_prefix_digest", lambda p: p["reconstruction"].update({"action_prefix_sha256": h("wrong")}), False)
    add("fail_action_text_digest", lambda p: p["reconstruction"]["action_prefix"][0].update({"action_sha256": h("wrong")}), False)
    add("fail_noncontiguous_indices", lambda p: p["reconstruction"]["action_prefix"][1].update({"index": 2}), False)
    add("fail_pair_binding_differs", lambda p: p["counterfactual_pair"].update({"condition_b_environment_binding_sha256": h("other")}), False)
    add("fail_pair_not_canonical", lambda p: p["counterfactual_pair"].update({"condition_a_environment_binding_sha256": h("x"), "condition_b_environment_binding_sha256": h("x")}), False)
    add("fail_scope_overclaim", lambda p: p.update({"evidence_scope": "package_wide_determinism"}), False)
    def missing_native(p):
        p["claim_scope"] = "native_snapshot"
        p["reconstruction"]["mode"] = "native_snapshot"
        p["reconstruction"]["native_snapshot_sha256"] = None
    add("fail_native_missing", missing_native, False)
    add("fail_action_prefix_mode_has_snapshot", lambda p: p["reconstruction"].update({"native_snapshot_sha256": h("snapshot")}), False)
    return out


def main():
    results = []
    for name, packet, expected in cases():
        jsonschema.validate(packet, SCHEMA)
        errors = validate(packet)
        actual = not errors
        results.append({"name": name, "structurally_valid": True, "expected_valid": expected, "actual_valid": actual, "errors": errors})
        if actual != expected:
            raise AssertionError((name, expected, actual, errors))
    print(json.dumps({"cases": len(results), "semantic_expected": sum(r["actual_valid"] == r["expected_valid"] for r in results), "structurally_valid": sum(r["structurally_valid"] for r in results), "results": results}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
