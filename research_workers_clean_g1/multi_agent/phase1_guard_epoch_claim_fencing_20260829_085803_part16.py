#!/usr/bin/env python3
from itertools import product
from collections import Counter
import json

TIMINGS = ["STABLE_E1", "E2_BEFORE_CLIENT_READ", "E2_AFTER_CLIENT_READ_BEFORE_EFFECT"]
OLD_RESPONSES = ["CONFIRMED", "AMBIG_APPLIED", "AMBIG_NOT_APPLIED"]
CONTRACTS = ["MATCH", "MISMATCH"]
DEDUPES = ["VALID", "EXPIRED"]
VERIFIERS = ["AVAILABLE", "OUTAGE"]

POLICIES = [
    "claim_no_guard_epoch_no_sink_check",
    "claim_guard_epoch_no_sink_check",
    "claim_guard_epoch_client_read",
    "claim_guard_epoch_sink_atomic",
    "reclaim_e2_exact_contract_sink_atomic",
    "fail_closed_no_guard_proof",
]

def evaluate(policy, s):
    c = Counter()
    timing = s["timing"]
    verifier = s["verifier"]
    current_epoch = "e1" if timing == "STABLE_E1" else "e2"

    if policy == "fail_closed_no_guard_proof":
        c["checkpoint"] += 1
        if timing == "STABLE_E1":
            c["current_progress_block"] += 1
        return c

    if policy in ("claim_no_guard_epoch_no_sink_check", "claim_guard_epoch_no_sink_check"):
        old_accept = True
    elif policy == "claim_guard_epoch_client_read":
        if verifier == "OUTAGE":
            c["checkpoint"] += 1
            if timing == "STABLE_E1":
                c["current_progress_block"] += 1
            return c
        old_accept = timing != "E2_BEFORE_CLIENT_READ"
    elif policy in ("claim_guard_epoch_sink_atomic", "reclaim_e2_exact_contract_sink_atomic"):
        if verifier == "OUTAGE":
            c["checkpoint"] += 1
            if timing == "STABLE_E1":
                c["current_progress_block"] += 1
            return c
        old_accept = current_epoch == "e1"
    else:
        raise ValueError(policy)

    if old_accept:
        c["old_effect_accepted"] += 1
        if current_epoch == "e2":
            c["unsafe_stale_effect"] += 1
        if s["old_response"] == "AMBIG_APPLIED" and s["dedupe"] == "EXPIRED":
            c["ambiguous_retry_duplicate"] += 1
    else:
        c["old_effect_rejected"] += 1

    if current_epoch == "e2":
        if policy == "reclaim_e2_exact_contract_sink_atomic":
            if s["contract"] == "MATCH":
                c["safe_reuse"] += 1
                c["current_e2_publish"] += 1
            else:
                c["mismatch_reuse_rejected"] += 1
        else:
            c["current_e2_publish"] += 1

        if old_accept and c["current_e2_publish"] and s["dedupe"] == "EXPIRED":
            c["old_plus_new_duplicate"] += 1

    return c

def main():
    scenarios = [
        dict(zip(
            ["timing", "old_response", "contract", "dedupe", "verifier"],
            vals
        ))
        for vals in product(TIMINGS, OLD_RESPONSES, CONTRACTS, DEDUPES, VERIFIERS)
    ]

    metrics = {}
    for policy in POLICIES:
        total = Counter()
        for s in scenarios:
            total["total"] += 1
            total.update(evaluate(policy, s))
        metrics[policy] = dict(total)

    targeted = {}
    slices = [
        ("guard_key_alone_transition", "E2_BEFORE_CLIENT_READ",
         "claim_guard_epoch_no_sink_check"),
        ("client_read_toctou", "E2_AFTER_CLIENT_READ_BEFORE_EFFECT",
         "claim_guard_epoch_client_read"),
        ("sink_atomic_transition", "E2_AFTER_CLIENT_READ_BEFORE_EFFECT",
         "claim_guard_epoch_sink_atomic"),
        ("exact_contract_reuse", "E2_BEFORE_CLIENT_READ",
         "reclaim_e2_exact_contract_sink_atomic"),
    ]
    for name, timing, policy in slices:
        members = [s for s in scenarios if s["timing"] == timing]
        c = Counter()
        for s in members:
            c.update(evaluate(policy, s))
        targeted[name] = {"scenario_count": len(members), "policy": policy, "metrics": dict(c)}

    result = {
        "scenario_count": len(scenarios),
        "metrics": metrics,
        "targeted_slices": targeted,
        "claims": {
            "guard_epoch_key_only": (
                "Including guard_epoch in claim identity does not itself fence an authoritative "
                "sink. In this model it is behaviorally identical to omitting the epoch when the "
                "sink never compares it to current authority."
            ),
            "client_read_limit": (
                "A client-side guard read can reject an epoch transition visible before the read, "
                "but remains vulnerable if authority changes after the read and before effect."
            ),
            "sink_atomic_requirement": (
                "Stale-authority exclusion requires the authoritative sink to atomically validate "
                "current guard epoch at effect application, or an equivalent server-side invariant."
            ),
            "idempotency_separate": (
                "Even perfect epoch fencing does not resolve an ambiguous applied response after "
                "dedupe expiry; durable effect identity/idempotency remains a separate obligation."
            ),
            "revalidation_reuse": (
                "A staged result from e1 may be reused under a fresh e2 claim only after exact "
                "contract revalidation; computation reuse must not inherit e1 authority."
            ),
        },
    }
    print(json.dumps(result, indent=2, sort_keys=True))

if __name__ == "__main__":
    main()
