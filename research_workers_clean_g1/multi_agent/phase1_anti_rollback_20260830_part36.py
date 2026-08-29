from collections import Counter

CANDIDATES = {
    "current_repo_bytes": dict(survives=False, discoverable=True, clean=True, zero_quota=True, no_protected=True, distinguishes=False, durable=True),
    "dangling_git_object_by_sha": dict(survives=True, discoverable=False, clean=True, zero_quota=True, no_protected=True, distinguishes=True, durable=True),
    "repository_activity_log": dict(survives=True, discoverable=True, clean=False, zero_quota=True, no_protected=True, distinguishes=True, durable=False),
    "connector_response_uri": dict(survives=True, discoverable=False, clean=False, zero_quota=True, no_protected=True, distinguishes=True, durable=False),
    "automation_runtime_metadata": dict(survives=True, discoverable=True, clean=False, zero_quota=True, no_protected=True, distinguishes=False, durable=True),
    "protected_branch_or_ruleset": dict(survives=True, discoverable=True, clean=True, zero_quota=False, no_protected=False, distinguishes=True, durable=True),
    "external_monotonic_store": dict(survives=True, discoverable=True, clean=False, zero_quota=False, no_protected=True, distinguishes=True, durable=True),
    "independent_repo_ref": dict(survives=False, discoverable=True, clean=True, zero_quota=True, no_protected=True, distinguishes=True, durable=True),
    "sha_pinned_only_in_role_state": dict(survives=False, discoverable=True, clean=True, zero_quota=True, no_protected=True, distinguishes=True, durable=True),
    "trusted_wall_clock": dict(survives=True, discoverable=True, clean=True, zero_quota=True, no_protected=True, distinguishes=False, durable=True),
}
REQUIRED = ["survives", "discoverable", "clean", "zero_quota", "no_protected", "distinguishes", "durable"]
WORLDS = ["legitimate_granted_g1", "cancelled_then_complete_rewind_to_granted_g1"]

def run():
    per_candidate = {}
    reason_counts = Counter()
    accepted_world_evaluations = 0
    for name, props in CANDIDATES.items():
        reasons = [k for k in REQUIRED if not props[k]]
        for r in reasons:
            reason_counts[r] += 1
        accepted = not reasons
        accepted_world_evaluations += (2 if accepted else 0)
        per_candidate[name] = {"accepted": accepted, "rejection_reasons": reasons, **props}
    return {
        "candidate_count": len(CANDIDATES),
        "world_count": len(WORLDS),
        "candidate_world_evaluations": len(CANDIDATES) * len(WORLDS),
        "accepted_candidates": sum(v["accepted"] for v in per_candidate.values()),
        "accepted_world_evaluations": accepted_world_evaluations,
        "rejection_reason_candidate_counts": dict(reason_counts),
        "per_candidate": per_candidate,
        "indistinguishability_pair": {
            "world_a": "repository legitimately remains at GRANTED(g1)",
            "world_b": "repository reached CANCELLED(g1), then every CLEAN-admissible same-domain repository/own-state witness is restored to the exact GRANTED(g1) bytes",
            "result": "Any deterministic current-state-only policy sees identical observations and must make the same decision in both worlds."
        }
    }

if __name__ == "__main__":
    import json
    print(json.dumps(run(), indent=2, sort_keys=True))
