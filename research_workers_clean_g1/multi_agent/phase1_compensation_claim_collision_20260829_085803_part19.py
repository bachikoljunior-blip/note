#!/usr/bin/env python3
from itertools import product
from collections import Counter
import json

RELATIONS = ["SAME_ORIGINAL", "DIFFERENT_ORIGINAL_SAME_PARENT"]
TIMINGS = ["NO_TAKEOVER", "TAKEOVER_BEFORE_FIRST_APPLY", "TAKEOVER_AFTER_FIRST_APPLY"]
FIRST_OUTCOMES = ["CONFIRMED_APPLIED", "AMBIG_APPLIED", "AMBIG_NOT_APPLIED"]
DEDUPES = ["VALID", "EXPIRED"]
STATUSES = ["DURABLE_STATUS", "NO_STATUS"]
VERIFIERS = ["AVAILABLE", "OUTAGE"]

POLICIES = [
    "parent_task_key_only",
    "original_effect_id_only_no_fence",
    "original_plus_claim_epoch_no_fence",
    "stable_original_kind_fenced_failclosed",
    "stable_original_kind_fenced_blind_retry",
    "single_fenced_compensator",
]

def first_applied(outcome):
    return outcome != "AMBIG_NOT_APPLIED"

def expected_units(s):
    return 1 if s["relation"] == "SAME_ORIGINAL" else 2

def weak_key_same(policy, s):
    if policy == "parent_task_key_only":
        return True
    if policy == "original_effect_id_only_no_fence":
        return s["relation"] == "SAME_ORIGINAL"
    if policy == "original_plus_claim_epoch_no_fence":
        if s["relation"] == "DIFFERENT_ORIGINAL_SAME_PARENT":
            return False
        return s["timing"] == "NO_TAKEOVER"
    raise ValueError(policy)

def evaluate(policy, s):
    c = Counter()
    expected = expected_units(s)

    if policy in (
        "parent_task_key_only",
        "original_effect_id_only_no_fence",
        "original_plus_claim_epoch_no_fence",
    ):
        first = 1 if first_applied(s["first_outcome"]) else 0
        same_key = weak_key_same(policy, s)
        suppressed = same_key and (
            s["status"] == "DURABLE_STATUS" or s["dedupe"] == "VALID"
        )
        second = (0 if first else 1) if suppressed else 1
        units = first + second

        c["terminal"] += 1
        c["applied_units"] += units

        if (
            s["relation"] == "SAME_ORIGINAL"
            and s["timing"] == "TAKEOVER_BEFORE_FIRST_APPLY"
            and first
        ):
            c["stale_writer_effect"] += 1

        if units > expected:
            c["overcomp_scenarios"] += 1
            c["overcomp_units"] += units - expected
            c["false_terminal"] += 1
        elif units < expected:
            c["undercomp_scenarios"] += 1
            c["undercomp_units"] += expected - units
            c["false_terminal"] += 1

        if same_key and s["relation"] == "DIFFERENT_ORIGINAL_SAME_PARENT":
            c["identity_alias"] += 1
        if not same_key and s["relation"] == "SAME_ORIGINAL":
            c["identity_split"] += 1
        return c

    if s["verifier"] == "OUTAGE":
        c["checkpoint"] += 1
        c["availability_block"] += 1
        return c

    ambiguous = s["first_outcome"] != "CONFIRMED_APPLIED"
    uncertain_no_safe_reconcile = (
        ambiguous
        and s["status"] == "NO_STATUS"
        and s["dedupe"] == "EXPIRED"
    )

    if policy in ("stable_original_kind_fenced_failclosed", "single_fenced_compensator"):
        if (
            s["relation"] == "SAME_ORIGINAL"
            and s["timing"] == "TAKEOVER_BEFORE_FIRST_APPLY"
        ):
            c["stale_writer_rejected"] += 1
            c["terminal"] += 1
            c["applied_units"] += 1
            return c

        if uncertain_no_safe_reconcile:
            c["checkpoint"] += 1
            c["ambiguous_orphan"] += 1
            return c

        units = expected
        c["terminal"] += 1
        c["applied_units"] += units

        if ambiguous:
            if s["status"] == "DURABLE_STATUS":
                c["durable_reconcile"] += 1
            else:
                c["safe_idempotent_retry"] += 1

        if (
            s["relation"] == "SAME_ORIGINAL"
            and s["timing"] == "TAKEOVER_AFTER_FIRST_APPLY"
        ):
            c["takeover_reuses_stable_comp_identity"] += 1
        return c

    if policy == "stable_original_kind_fenced_blind_retry":
        if (
            s["relation"] == "SAME_ORIGINAL"
            and s["timing"] == "TAKEOVER_BEFORE_FIRST_APPLY"
        ):
            c["stale_writer_rejected"] += 1
            c["terminal"] += 1
            c["applied_units"] += 1
            return c

        units = expected
        if uncertain_no_safe_reconcile:
            if s["first_outcome"] == "AMBIG_APPLIED":
                units = expected + 1
                c["duplicate_compensation"] += 1

        c["terminal"] += 1
        c["applied_units"] += units

        if units > expected:
            c["overcomp_scenarios"] += 1
            c["overcomp_units"] += units - expected
            c["false_terminal"] += 1
        return c

    raise ValueError(policy)

def main():
    scenarios = [
        dict(zip(
            ["relation", "timing", "first_outcome", "dedupe", "status", "verifier"],
            vals,
        ))
        for vals in product(
            RELATIONS, TIMINGS, FIRST_OUTCOMES, DEDUPES, STATUSES, VERIFIERS
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
        "different_originals_parent_key_suppression": selected(
            lambda s: s["relation"] == "DIFFERENT_ORIGINAL_SAME_PARENT"
            and (s["status"] == "DURABLE_STATUS" or s["dedupe"] == "VALID")
        ),
        "same_original_takeover_after_apply": selected(
            lambda s: s["relation"] == "SAME_ORIGINAL"
            and s["timing"] == "TAKEOVER_AFTER_FIRST_APPLY"
        ),
        "same_original_takeover_before_apply": selected(
            lambda s: s["relation"] == "SAME_ORIGINAL"
            and s["timing"] == "TAKEOVER_BEFORE_FIRST_APPLY"
        ),
        "ambiguous_no_status_expired_available": selected(
            lambda s: s["verifier"] == "AVAILABLE"
            and s["first_outcome"] != "CONFIRMED_APPLIED"
            and s["status"] == "NO_STATUS"
            and s["dedupe"] == "EXPIRED"
            and not (
                s["relation"] == "SAME_ORIGINAL"
                and s["timing"] == "TAKEOVER_BEFORE_FIRST_APPLY"
            )
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
            "parent_key_too_coarse": (
                "A compensation identity keyed only by parent/task aliases distinct original "
                "effects and can suppress a required second compensation."
            ),
            "claim_epoch_too_fine_for_effect_identity": (
                "Including claim epoch in the logical compensation identity splits one original "
                "effect across takeover and can authorize a second undo."
            ),
            "stable_effect_identity_plus_fence": (
                "The logical compensation ID should remain stable as a function of original effect "
                "ID plus compensation kind, while claim epoch is checked separately as writer authority."
            ),
            "ambiguous_recovery": (
                "After an ambiguous first compensation, takeover must reconcile the stable logical "
                "compensation identity using durable sink status or still-valid idempotency; otherwise fail closed."
            ),
            "conservation": (
                "Parent terminality must prove one required compensation unit per original effect; "
                "unique sink resource IDs are evidence of actual applies, not permission to exceed the required sum."
            ),
        },
    }
    print(json.dumps(result, indent=2, sort_keys=True))

if __name__ == "__main__":
    main()
