#!/usr/bin/env python3
from itertools import product
from collections import Counter
import json

PLANS = ["FULL100", "SPLIT40_60"]
HANDOFFS = ["NO_TAKEOVER", "TAKEOVER_SAME_PLAN", "TAKEOVER_REPLAN_50_50"]
FIRST_OUTCOMES = ["CONFIRMED_APPLIED", "AMBIG_APPLIED", "AMBIG_NOT_APPLIED"]
DEDUPES = ["VALID", "EXPIRED"]
STATUSES = ["DURABLE_STATUS", "NO_STATUS"]
VERIFIERS = ["AVAILABLE", "OUTAGE"]

POLICIES = [
    "single_full_effect_key",
    "ordinal_segment_key",
    "amount_only_segment_key",
    "claim_epoch_ordinal_key",
    "range_contract_failclosed",
    "range_contract_blind_retry",
]

def first_amount(plan):
    return 100 if plan == "FULL100" else 40

def initial_key(policy, amount):
    if policy == "single_full_effect_key":
        return "full"
    if policy == "ordinal_segment_key":
        return "0"
    if policy == "claim_epoch_ordinal_key":
        return "e1:0"
    if policy == "amount_only_segment_key":
        return "amt:" + str(amount)
    raise ValueError(policy)

def subsequent_key(policy, ordinal, amount, handoff):
    if policy == "single_full_effect_key":
        return "full"
    if policy == "ordinal_segment_key":
        return str(ordinal)
    if policy == "claim_epoch_ordinal_key":
        epoch = "e2" if handoff != "NO_TAKEOVER" else "e1"
        return epoch + ":" + str(ordinal)
    if policy == "amount_only_segment_key":
        return "amt:" + str(amount)
    raise ValueError(policy)

def evaluate_weak(policy, s):
    c = Counter()
    amount1 = first_amount(s["plan"])
    protected = s["status"] == "DURABLE_STATUS" or s["dedupe"] == "VALID"
    memory = set()
    total = 0
    resources = 0

    first_applied = s["first_outcome"] != "AMBIG_NOT_APPLIED"
    key1 = initial_key(policy, amount1)

    if first_applied:
        total += amount1
        resources += 1
        if protected:
            memory.add(key1)

    if s["first_outcome"] != "CONFIRMED_APPLIED":
        retry_key = subsequent_key(policy, 0, amount1, s["handoff"])
        if protected and retry_key in memory:
            c["suppressed_retry"] += 1
        else:
            total += amount1
            resources += 1
            if protected:
                memory.add(retry_key)

    requests = []
    if s["handoff"] == "TAKEOVER_REPLAN_50_50":
        requests = [(0, 50), (1, 50)]
        c["naive_replan"] += 1
    elif s["plan"] == "SPLIT40_60":
        requests = [(1, 60)]

    for ordinal, amount in requests:
        key = subsequent_key(policy, ordinal, amount, s["handoff"])

        if (
            policy == "ordinal_segment_key"
            and s["handoff"] == "TAKEOVER_REPLAN_50_50"
            and ordinal == 0
            and protected
            and key in memory
            and amount != amount1
        ):
            c["ordinal_replan_payload_collision"] += 1

        if (
            policy == "amount_only_segment_key"
            and s["handoff"] == "TAKEOVER_REPLAN_50_50"
            and ordinal == 1
            and protected
            and key in memory
        ):
            c["same_amount_distinct_range_alias"] += 1

        if protected and key in memory:
            c["segment_alias_suppressed"] += 1
        else:
            total += amount
            resources += 1
            if protected:
                memory.add(key)

    c["terminal"] += 1
    c["applied_amount"] += total
    c["resource_apply_count"] += resources

    if total > 100:
        c["overrefund_scenarios"] += 1
        c["overrefund_amount"] += total - 100
        c["false_terminal"] += 1
    elif total < 100:
        c["underrefund_scenarios"] += 1
        c["underrefund_amount"] += 100 - total
        c["false_terminal"] += 1

    if policy == "claim_epoch_ordinal_key" and s["handoff"] != "NO_TAKEOVER":
        c["epoch_key_namespace_change"] += 1
    return c

def evaluate_range(policy, s):
    c = Counter()

    if s["verifier"] == "OUTAGE":
        c["checkpoint"] += 1
        c["availability_block"] += 1
        return c

    amount1 = first_amount(s["plan"])
    ambiguous = s["first_outcome"] != "CONFIRMED_APPLIED"
    uncertain = (
        ambiguous
        and s["status"] == "NO_STATUS"
        and s["dedupe"] == "EXPIRED"
    )
    actual_first = s["first_outcome"] != "AMBIG_NOT_APPLIED"

    if uncertain and policy == "range_contract_failclosed":
        c["checkpoint"] += 1
        c["ambiguous_partial_orphan"] += 1
        return c

    total = 0
    resources = 0

    if uncertain and policy == "range_contract_blind_retry":
        if actual_first:
            total += amount1 * 2
            resources += 2
            c["duplicate_first_range"] += 1
        else:
            total += amount1
            resources += 1
    else:
        total += amount1
        resources += 1
        if ambiguous:
            if s["status"] == "DURABLE_STATUS":
                c["durable_reconcile"] += 1
            elif s["dedupe"] == "VALID":
                c["safe_range_retry"] += 1

    remaining = 100 - amount1
    if remaining > 0:
        if s["handoff"] == "TAKEOVER_REPLAN_50_50":
            pieces = [min(50, remaining)]
            if remaining > pieces[0]:
                pieces.append(remaining - pieces[0])
            c["resegmented_remaining"] += 1
        else:
            pieces = [remaining]

        for amount in pieces:
            total += amount
            resources += 1
    elif s["handoff"] == "TAKEOVER_REPLAN_50_50":
        c["replan_no_remaining_noop"] += 1

    c["terminal"] += 1
    c["applied_amount"] += total
    c["resource_apply_count"] += resources

    if total > 100:
        c["overrefund_scenarios"] += 1
        c["overrefund_amount"] += total - 100
        c["false_terminal"] += 1
    elif total < 100:
        c["underrefund_scenarios"] += 1
        c["underrefund_amount"] += 100 - total
        c["false_terminal"] += 1

    return c

def evaluate(policy, s):
    if policy in ("range_contract_failclosed", "range_contract_blind_retry"):
        return evaluate_range(policy, s)
    return evaluate_weak(policy, s)

def main():
    scenarios = [
        dict(zip(
            ["plan", "handoff", "first_outcome", "dedupe", "status", "verifier"],
            vals,
        ))
        for vals in product(
            PLANS, HANDOFFS, FIRST_OUTCOMES, DEDUPES, STATUSES, VERIFIERS
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
        "split_plan_available": selected(
            lambda s: s["verifier"] == "AVAILABLE" and s["plan"] == "SPLIT40_60"
        ),
        "replan_available": selected(
            lambda s: s["verifier"] == "AVAILABLE"
            and s["handoff"] == "TAKEOVER_REPLAN_50_50"
        ),
        "ambiguous_no_status_expired_available": selected(
            lambda s: s["verifier"] == "AVAILABLE"
            and s["first_outcome"] != "CONFIRMED_APPLIED"
            and s["status"] == "NO_STATUS"
            and s["dedupe"] == "EXPIRED"
        ),
        "ambiguous_applied_no_status_expired_available": selected(
            lambda s: s["verifier"] == "AVAILABLE"
            and s["first_outcome"] == "AMBIG_APPLIED"
            and s["status"] == "NO_STATUS"
            and s["dedupe"] == "EXPIRED"
        ),
    }

    targeted = {}
    for name, members in slices.items():
        targeted[name] = {"scenario_count": len(members), "policies": {}}
        for policy in POLICIES:
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
            "full_key_too_coarse_for_partial": (
                "One full-effect idempotency key cannot safely identify multiple independently "
                "applied partial compensation resources."
            ),
            "ordinal_not_stable_under_replan": (
                "Ordinal segment identity is plan-relative. Replanning can reuse ordinal 0 for a "
                "different amount/range and either suppress or duplicate the wrong segment."
            ),
            "amount_not_range_identity": (
                "Amount alone is not a unique segment contract: two distinct 50-unit ranges alias "
                "under an amount-only key."
            ),
            "claim_epoch_not_segment_identity": (
                "Adding claim epoch to segment keys splits logical ranges across takeover and raises "
                "over-refund risk instead of fencing writers."
            ),
            "range_conservation": (
                "Safe partial compensation binds each logical segment to an immutable original-effect "
                "range/obligation contract and computes new segments only from the monotonic remaining range."
            ),
            "ambiguous_partial": (
                "Ambiguous partial application with no durable status and expired dedupe remains "
                "nonterminal; blind retry can duplicate the first range and exceed total conservation."
            ),
        },
    }
    print(json.dumps(result, indent=2, sort_keys=True))

if __name__ == "__main__":
    main()
