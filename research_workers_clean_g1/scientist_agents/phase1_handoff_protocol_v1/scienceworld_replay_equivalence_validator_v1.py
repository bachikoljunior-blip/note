#!/usr/bin/env python3
"""Validate ScienceWorld state-reconstruction evidence for matched counterfactuals.

This checks exact replay provenance, not package-wide determinism or an outcome
benefit. Action-prefix replay is accepted only when the exact environment
identity and prefix have empirical replay-equivalence evidence; native snapshots
can be used directly when their bytes are bound.
"""
import hashlib
import json
import sys


def _digest(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def _major_minor(version):
    parts = version.split(".")
    try:
        return tuple(int(x) for x in parts[:2])
    except Exception:
        return None


def environment_binding(packet):
    sw = packet.get("scienceworld", {})
    rec = packet.get("reconstruction", {})
    return _digest({
        "scienceworld": sw,
        "mode": rec.get("mode"),
        "native_snapshot_sha256": rec.get("native_snapshot_sha256"),
        "reset_observation_sha256": rec.get("reset_observation_sha256"),
        "reset_object_tree_sha256": rec.get("reset_object_tree_sha256"),
        "reset_api_snapshot_sha256": rec.get("reset_api_snapshot_sha256"),
        "action_prefix_sha256": rec.get("action_prefix_sha256"),
        "branch_state_sha256": rec.get("branch_state_sha256"),
    })


def validate(packet):
    errors = []
    sw = packet.get("scienceworld", {})
    rec = packet.get("reconstruction", {})
    pair = packet.get("counterfactual_pair", {})
    mode = rec.get("mode")

    if packet.get("claim_scope") == "native_snapshot" and mode != "native_snapshot":
        errors.append("claim_scope_native_snapshot_but_mode_differs")
    if packet.get("claim_scope") == "exact_branch_state_replay" and mode not in ("native_snapshot", "action_prefix_replay"):
        errors.append("unsupported_reconstruction_mode")

    steps = rec.get("action_prefix", [])
    canonical_prefix = [{
        "index": s.get("index"),
        "action": s.get("action"),
        "action_sha256": s.get("action_sha256"),
        "observation_sha256": s.get("observation_sha256"),
        "reward_sha256": s.get("reward_sha256"),
        "done": s.get("done"),
        "info_sha256": s.get("info_sha256"),
    } for s in steps]
    if rec.get("action_prefix_sha256") != _digest(canonical_prefix):
        errors.append("action_prefix_digest_mismatch")
    if [s.get("index") for s in steps] != list(range(len(steps))):
        errors.append("action_prefix_indices_not_contiguous")
    for s in steps:
        action_digest = hashlib.sha256(s.get("action", "").encode()).hexdigest()
        if s.get("action_sha256") != action_digest:
            errors.append(f"action_text_digest_mismatch:{s.get('index')}")

    if mode == "native_snapshot":
        if not rec.get("native_snapshot_sha256"):
            errors.append("native_snapshot_missing")
    elif mode == "action_prefix_replay":
        if rec.get("native_snapshot_sha256") is not None:
            errors.append("action_prefix_mode_native_snapshot_must_be_null")
        probe = rec.get("replay_probe", {})
        n = probe.get("run_count", 0)
        states = probe.get("branch_state_sha256s", [])
        traces = probe.get("trace_sha256s", [])
        if n < 2:
            errors.append("replay_probe_needs_multiple_runs")
        if len(states) != n or len(traces) != n:
            errors.append("replay_probe_count_mismatch")
        if not probe.get("all_branch_states_equal"):
            errors.append("branch_states_not_equal")
        if not probe.get("all_trace_digests_equal"):
            errors.append("trace_digests_not_equal")
        if len(set(states)) != 1 or (states and states[0] != rec.get("branch_state_sha256")):
            errors.append("branch_state_digest_evidence_mismatch")
        if len(set(traces)) != 1:
            errors.append("trace_digest_evidence_mismatch")

        # Official ScienceWorld evidence shows a known pre-1.3 stochastic path.
        # For <=1.2.x require a stronger exact-prefix empirical probe instead of
        # treating task/variation identity as sufficient state identity.
        mm = _major_minor(sw.get("package_version", ""))
        if mm is not None and mm <= (1, 2) and n < 8:
            errors.append("scienceworld_1_2_or_older_requires_8_run_exact_prefix_probe")

    env_hash = environment_binding(packet)
    a = pair.get("condition_a_environment_binding_sha256")
    b = pair.get("condition_b_environment_binding_sha256")
    if pair.get("same_environment_binding_required") is not True:
        errors.append("same_environment_binding_not_required")
    if a != b:
        errors.append("counterfactual_environment_bindings_differ")
    if a != env_hash or b != env_hash:
        errors.append("counterfactual_environment_binding_not_canonical")

    if packet.get("evidence_scope", "") in ("all_scienceworld_tasks", "package_wide_determinism"):
        errors.append("scope_overclaims_exact_replay_evidence")

    return errors


def main():
    packet = json.load(sys.stdin)
    errors = validate(packet)
    print(json.dumps({"valid": not errors, "errors": errors}, sort_keys=True))
    raise SystemExit(0 if not errors else 1)


if __name__ == "__main__":
    main()
