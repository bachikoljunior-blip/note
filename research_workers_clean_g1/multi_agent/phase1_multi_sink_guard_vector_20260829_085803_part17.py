#!/usr/bin/env python3
from itertools import product
from collections import Counter
import json

TIMINGS = ["STABLE_E1", "E2_BEFORE_APPLY", "E2_AFTER_APPLY"]
RESPONSES = ["CONFIRMED", "AMBIG_APPLIED"]
B_DEDUPE = ["VALID", "EXPIRED"]
VERIFIERS = ["AVAILABLE", "OUTAGE"]
CONTRACTS = ["MATCH", "MISMATCH"]

POLICIES = [
    "scalar_current_epoch_atomic",
    "scalar_any_historical_no_sink_check",
    "vector_claim_only_no_sink_check",
    "vector_atomic_ephemeral_b_dedupe",
    "vector_atomic_durable_effect_ids",
    "vector_atomic_exact_reuse_durable",
    "serial_fail_closed",
]

def final_epoch(timing):
    return "e1" if timing == "STABLE_E1" else "e2"

def applied_epoch_atomic(timing):
    if timing == "E2_BEFORE_APPLY":
        return "e2"
    return "e1"

def old_authorized(timing):
    return timing != "E2_BEFORE_APPLY"

def evaluate(policy, s):
    c = Counter()

    if policy in ("scalar_any_historical_no_sink_check", "vector_claim_only_no_sink_check"):
        stale_count = sum(
            t == "E2_BEFORE_APPLY" for t in (s["a_timing"], s["b_timing"])
        )
        c["terminal"] += 1
        c["old_effects_applied"] += 2
        c["stale_effect_accept"] += stale_count
        if stale_count:
            c["false_terminal"] += 1
        if s["b_response"] == "AMBIG_APPLIED" and s["b_dedupe"] == "EXPIRED":
            c["duplicate_effect"] += 1
        return c

    if s["verifier"] == "OUTAGE":
        c["checkpoint"] += 1
        c["current_progress_block"] += 1
        return c

    a_applied_epoch = applied_epoch_atomic(s["a_timing"])
    b_applied_epoch = applied_epoch_atomic(s["b_timing"])
    before_count = sum(
        t == "E2_BEFORE_APPLY" for t in (s["a_timing"], s["b_timing"])
    )
    c["valid_effects"] += 2
    c["old_rejected"] += before_count
    c["new_effects"] += before_count

    if policy == "scalar_current_epoch_atomic":
        scalar = (
            "e2"
            if "e2" in (final_epoch(s["a_timing"]), final_epoch(s["b_timing"]))
            else "e1"
        )
        if a_applied_epoch == scalar and b_applied_epoch == scalar:
            c["terminal"] += 1
        else:
            c["false_block"] += 1
        return c

    if policy == "vector_atomic_ephemeral_b_dedupe":
        c["terminal"] += 1
        if (
            old_authorized(s["b_timing"])
            and s["b_response"] == "AMBIG_APPLIED"
            and s["b_dedupe"] == "EXPIRED"
        ):
            c["duplicate_effect"] += 1
        return c

    if policy == "vector_atomic_durable_effect_ids":
        c["terminal"] += 1
        c["durable_reconciliations"] += int(
            old_authorized(s["a_timing"]) and s["a_response"] == "AMBIG_APPLIED"
        )
        c["durable_reconciliations"] += int(
            old_authorized(s["b_timing"]) and s["b_response"] == "AMBIG_APPLIED"
        )
        return c

    if policy == "vector_atomic_exact_reuse_durable":
        c["terminal"] += 1
        for timing in (s["a_timing"], s["b_timing"]):
            if timing == "E2_BEFORE_APPLY":
                if s["contract"] == "MATCH":
                    c["safe_staged_reuse"] += 1
                else:
                    c["staged_reuse_rejected_recompute"] += 1
        return c

    if policy == "serial_fail_closed":
        if (
            old_authorized(s["b_timing"])
            and s["b_response"] == "AMBIG_APPLIED"
            and s["b_dedupe"] == "EXPIRED"
        ):
            c["checkpoint"] += 1
            c["ambiguous_block"] += 1
        else:
            c["terminal"] += 1
        return c

    raise ValueError(policy)

def main():
    scenarios = [
        dict(zip(
            [
                "a_timing", "b_timing", "a_response", "b_response",
                "b_dedupe", "verifier", "contract"
            ],
            vals,
        ))
        for vals in product(
            TIMINGS, TIMINGS, RESPONSES, RESPONSES,
            B_DEDUPE, VERIFIERS, CONTRACTS
        )
    ]

    metrics = {}
    for policy in POLICIES:
        c = Counter(total=len(scenarios))
        for s in scenarios:
            c.update(evaluate(policy, s))
        metrics[policy] = dict(c)

    def selected(predicate):
        return [s for s in scenarios if predicate(s)]

    slices = {
        "mixed_final_epoch_vector_available": selected(
            lambda s: s["verifier"] == "AVAILABLE"
            and final_epoch(s["a_timing"]) != final_epoch(s["b_timing"])
        ),
        "both_e2_after_apply_available": selected(
            lambda s: s["verifier"] == "AVAILABLE"
            and s["a_timing"] == "E2_AFTER_APPLY"
            and s["b_timing"] == "E2_AFTER_APPLY"
        ),
        "any_e2_before_apply_available": selected(
            lambda s: s["verifier"] == "AVAILABLE"
            and (
                s["a_timing"] == "E2_BEFORE_APPLY"
                or s["b_timing"] == "E2_BEFORE_APPLY"
            )
        ),
        "b_ambiguous_expired_old_authorized_available": selected(
            lambda s: s["verifier"] == "AVAILABLE"
            and old_authorized(s["b_timing"])
            and s["b_response"] == "AMBIG_APPLIED"
            and s["b_dedupe"] == "EXPIRED"
        ),
    }

    targeted = {}
    for name, members in slices.items():
        targeted[name] = {"scenario_count": len(members), "policies": {}}
        for policy in (
            "scalar_current_epoch_atomic",
            "vector_claim_only_no_sink_check",
            "vector_atomic_ephemeral_b_dedupe",
            "vector_atomic_durable_effect_ids",
        ):
            c = Counter()
            for s in members:
                c.update(evaluate(policy, s))
            targeted[name]["policies"][policy] = dict(c)

    result = {
        "scenario_count": len(scenarios),
        "available_verifier_count": sum(s["verifier"] == "AVAILABLE" for s in scenarios),
        "verifier_outage_count": sum(s["verifier"] == "OUTAGE" for s in scenarios),
        "metrics": metrics,
        "targeted_slices": targeted,
        "claims": {
            "scalar_epoch_too_coarse": (
                "A single current parent epoch is safe only by over-serializing in asynchronous "
                "sink transitions. It cannot represent that one sink legitimately applied under e1 "
                "while another required e2."
            ),
            "historical_receipts_need_sink_validation": (
                "Accepting any historical receipt without a sink-time authority proof false-"
                "terminalizes when an old effect was applied after that sink had already advanced."
            ),
            "per_effect_certificate": (
                "Parent terminality can safely use per-effect receipts that prove sink-time atomic "
                "authority validation plus effect identity; the receipt need not equal the sink's "
                "later current epoch if the effect was validly applied before that later transition."
            ),
            "idempotency_vector_separate": (
                "A correct per-sink authority vector does not prevent duplicate retry at a sink "
                "whose ambiguous-applied effect cannot be reconciled after dedupe expiry."
            ),
            "staged_reuse": (
                "Fresh-epoch takeover can reuse immutable computation only after exact contract "
                "revalidation; effect authority comes from the new sink check, not from the old stage."
            ),
        },
    }
    print(json.dumps(result, indent=2, sort_keys=True))

if __name__ == "__main__":
    main()
