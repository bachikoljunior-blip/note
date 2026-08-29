#!/usr/bin/env python3
from itertools import product
from collections import Counter
import json

HISTORIES = ["LEGIT_G3", "G4_THEN_ROLLBACK"]
THREATS = [
    "NO_ROLLBACK",
    "REF_ONLY",
    "REPO_GUARD_MUTABLE",
    "REPO_RECREATE",
    "ORG_GUARD_MUTABLE",
    "PLATFORM_ROLLBACK",
]
TIMINGS = ["BEFORE_READ", "AFTER_READ_BEFORE_WRITE"]
DEDUPE = ["VALID", "EXPIRED"]
TRANSPORT = ["AVAILABLE", "RATE_LIMITED"]

POLICIES = [
    "cas_only",
    "repo_guard_once",
    "repo_guard_read_each",
    "org_guard_once",
    "org_guard_read_each",
    "atomic_guard_epoch_plus_ref",
    "external_monotonic_floor",
    "fail_closed_no_proof",
]

def decision(policy, s):
    if s["transport"] == "RATE_LIMITED":
        return "CHECKPOINT"

    if s["history"] == "LEGIT_G3":
        if policy == "fail_closed_no_proof":
            return "REJECT_G3"
        return "ACCEPT_G3"

    threat = s["threat"]
    timing = s["timing"]

    if threat == "NO_ROLLBACK":
        return "REJECT_G3"
    if policy == "cas_only":
        return "ACCEPT_G3"
    if policy == "repo_guard_once":
        return "REJECT_G3" if threat == "REF_ONLY" else "ACCEPT_G3"
    if policy == "repo_guard_read_each":
        if threat == "REF_ONLY":
            return "REJECT_G3"
        if threat in ("REPO_GUARD_MUTABLE", "REPO_RECREATE") and timing == "BEFORE_READ":
            return "REJECT_G3"
        return "ACCEPT_G3"
    if policy == "org_guard_once":
        return "REJECT_G3" if threat in ("REF_ONLY", "REPO_GUARD_MUTABLE", "REPO_RECREATE") else "ACCEPT_G3"
    if policy == "org_guard_read_each":
        if threat in ("REF_ONLY", "REPO_GUARD_MUTABLE", "REPO_RECREATE"):
            return "REJECT_G3"
        if threat == "ORG_GUARD_MUTABLE" and timing == "BEFORE_READ":
            return "REJECT_G3"
        return "ACCEPT_G3"
    if policy == "atomic_guard_epoch_plus_ref":
        return "ACCEPT_G3" if threat == "PLATFORM_ROLLBACK" else "REJECT_G3"
    if policy == "external_monotonic_floor":
        return "REJECT_G3"
    if policy == "fail_closed_no_proof":
        return "REJECT_G3"
    raise ValueError(policy)

def main():
    scenarios = [
        dict(zip(["history", "threat", "timing", "dedupe", "transport"], vals))
        for vals in product(HISTORIES, THREATS, TIMINGS, DEDUPE, TRANSPORT)
    ]

    metrics = {}
    for policy in POLICIES:
        c = Counter()
        for s in scenarios:
            d = decision(policy, s)
            c["total"] += 1
            if d == "CHECKPOINT":
                c["checkpoint"] += 1
                continue
            if s["history"] == "LEGIT_G3":
                if d == "ACCEPT_G3":
                    c["legit_accept"] += 1
                else:
                    c["false_block"] += 1
            else:
                if d == "ACCEPT_G3":
                    c["unsafe_old_accept"] += 1
                    if s["dedupe"] == "EXPIRED":
                        c["duplicate_effect"] += 1
                else:
                    c["safe_reject"] += 1
        metrics[policy] = dict(c)

    def slice_count(threat, timing=None):
        out = []
        for s in scenarios:
            if s["history"] != "G4_THEN_ROLLBACK" or s["transport"] != "AVAILABLE":
                continue
            if s["threat"] != threat:
                continue
            if timing is not None and s["timing"] != timing:
                continue
            out.append(s)
        return out

    targeted = {}
    for name, threat, timing, policy in [
        ("ref_only_repo_guard_once", "REF_ONLY", None, "repo_guard_once"),
        ("repo_guard_toctou", "REPO_GUARD_MUTABLE", "AFTER_READ_BEFORE_WRITE", "repo_guard_read_each"),
        ("org_guard_toctou", "ORG_GUARD_MUTABLE", "AFTER_READ_BEFORE_WRITE", "org_guard_read_each"),
        ("platform_rollback_atomic_local", "PLATFORM_ROLLBACK", None, "atomic_guard_epoch_plus_ref"),
        ("platform_rollback_external_floor", "PLATFORM_ROLLBACK", None, "external_monotonic_floor"),
    ]:
        ss = slice_count(threat, timing)
        outcomes = Counter(decision(policy, s) for s in ss)
        targeted[name] = {
            "scenario_count": len(ss),
            "policy": policy,
            "outcomes": dict(outcomes),
        }

    result = {
        "scenario_count": len(scenarios),
        "available_transport_count": sum(s["transport"] == "AVAILABLE" for s in scenarios),
        "rate_limited_count": sum(s["transport"] == "RATE_LIMITED" for s in scenarios),
        "metrics": metrics,
        "targeted_slices": targeted,
        "mechanism_claims": {
            "one_time_guard_sufficient_scope": (
                "A server-enforced guard installed once is sufficient only when mutation/bypass of "
                "that guard is outside the modeled threat and the guarded ref operation is the "
                "effect being protected."
            ),
            "read_each_publish_limit": (
                "Reading guard state before each publication improves detection when guard loss "
                "is already observable before the read, but does not close disable/bypass after "
                "the read and before the write."
            ),
            "atomic_compare_limit": (
                "An atomic guard-epoch+ref update would close that local TOCTOU, but remains in the "
                "same platform rollback domain unless its epoch authority is outside that domain."
            ),
            "minimum_generic_boundary": (
                "The anti-rollback trust root must be outside the deepest rollback/mutation domain "
                "included in the threat model; otherwise fail closed."
            ),
        },
    }
    print(json.dumps(result, indent=2, sort_keys=True))

if __name__ == "__main__":
    main()
