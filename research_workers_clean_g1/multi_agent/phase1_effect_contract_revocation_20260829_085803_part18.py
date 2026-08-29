#!/usr/bin/env python3
from itertools import product
from collections import Counter
import json

CONTRACTS = [
    "IRREVERSIBLE_ONCE_AUTHORIZED",
    "REVOCABLE_UNTIL_PARENT_TERMINAL",
    "COMPENSATABLE",
]
EVENTS = ["NONE", "TAKEOVER_ONLY", "EXPLICIT_REVOKE"]
TOMBSTONES = ["PRESENT", "MISSING"]
COMPENSATIONS = ["CONFIRMED", "AMBIG_APPLIED", "FAILED", "NOT_SENT"]
COMP_IDS = ["DURABLE", "NONE"]
DEDUPES = ["VALID", "EXPIRED"]
VERIFIERS = ["AVAILABLE", "OUTAGE"]

POLICIES = [
    "historical_receipt_always_success",
    "current_epoch_only",
    "contract_aware_proof",
    "contract_aware_blind_retry",
    "comp_request_is_terminal",
    "epoch_change_means_revoke",
    "fail_closed_on_any_change",
]

def expected_disposition(s):
    contract = s["contract"]
    event = s["event"]

    if event in ("NONE", "TAKEOVER_ONLY") or contract == "IRREVERSIBLE_ONCE_AUTHORIZED":
        return "SUCCESS"

    if contract == "REVOCABLE_UNTIL_PARENT_TERMINAL":
        return "CANCELLED" if s["tombstone"] == "PRESENT" else "NONTERMINAL"

    if s["compensation"] == "CONFIRMED":
        return "COMPENSATED"
    if s["compensation"] == "AMBIG_APPLIED":
        if s["comp_id"] == "DURABLE" or s["dedupe"] == "VALID":
            return "COMPENSATED"
        return "NONTERMINAL"
    return "NONTERMINAL"

def evaluate(policy, s):
    c = Counter()
    expected = expected_disposition(s)

    if policy == "historical_receipt_always_success":
        observed = "SUCCESS"

    elif policy in ("current_epoch_only", "fail_closed_on_any_change"):
        observed = "SUCCESS" if s["event"] == "NONE" else "NONTERMINAL"

    else:
        if s["verifier"] == "OUTAGE":
            c["checkpoint"] += 1
            if expected != "NONTERMINAL":
                c["availability_block"] += 1
            return c

        if policy == "contract_aware_proof":
            observed = expected
            if (
                s["contract"] == "COMPENSATABLE"
                and s["event"] == "EXPLICIT_REVOKE"
                and s["compensation"] == "AMBIG_APPLIED"
                and s["comp_id"] == "NONE"
                and s["dedupe"] == "VALID"
            ):
                c["safe_comp_retry"] += 1
            if (
                s["contract"] == "COMPENSATABLE"
                and s["event"] == "EXPLICIT_REVOKE"
                and s["compensation"] == "AMBIG_APPLIED"
                and s["comp_id"] == "DURABLE"
            ):
                c["durable_comp_reconcile"] += 1

        elif policy == "contract_aware_blind_retry":
            observed = expected
            if (
                s["contract"] == "COMPENSATABLE"
                and s["event"] == "EXPLICIT_REVOKE"
                and s["compensation"] == "AMBIG_APPLIED"
                and s["comp_id"] == "NONE"
                and s["dedupe"] == "EXPIRED"
            ):
                observed = "COMPENSATED"
                c["duplicate_compensation"] += 1
                c["blind_retry_after_expiry"] += 1

        elif policy == "comp_request_is_terminal":
            if (
                s["contract"] == "COMPENSATABLE"
                and s["event"] == "EXPLICIT_REVOKE"
                and s["compensation"] != "NOT_SENT"
            ):
                observed = "COMPENSATED"
            else:
                observed = expected

        elif policy == "epoch_change_means_revoke":
            if s["event"] == "TAKEOVER_ONLY":
                if s["contract"] == "IRREVERSIBLE_ONCE_AUTHORIZED":
                    observed = "SUCCESS"
                elif s["contract"] == "REVOCABLE_UNTIL_PARENT_TERMINAL":
                    observed = "CANCELLED" if s["tombstone"] == "PRESENT" else "NONTERMINAL"
                else:
                    if (
                        s["compensation"] == "CONFIRMED"
                        or (
                            s["compensation"] == "AMBIG_APPLIED"
                            and (s["comp_id"] == "DURABLE" or s["dedupe"] == "VALID")
                        )
                    ):
                        observed = "COMPENSATED"
                    else:
                        observed = "NONTERMINAL"
            else:
                observed = expected
        else:
            raise ValueError(policy)

    if observed == "NONTERMINAL":
        c["nonterminal"] += 1
        if expected != "NONTERMINAL":
            c["false_block"] += 1
    else:
        c["terminal"] += 1
        c["terminal_" + observed.lower()] += 1
        if observed != expected:
            c["unsafe_terminal"] += 1
            c["wrong_disposition"] += 1

    return c

def main():
    scenarios = [
        dict(zip(
            [
                "contract", "event", "tombstone", "compensation",
                "comp_id", "dedupe", "verifier"
            ],
            vals,
        ))
        for vals in product(
            CONTRACTS, EVENTS, TOMBSTONES, COMPENSATIONS,
            COMP_IDS, DEDUPES, VERIFIERS
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
        "irreversible_change_available": selected(
            lambda s: s["verifier"] == "AVAILABLE"
            and s["contract"] == "IRREVERSIBLE_ONCE_AUTHORIZED"
            and s["event"] != "NONE"
        ),
        "revocable_takeover_only_available": selected(
            lambda s: s["verifier"] == "AVAILABLE"
            and s["contract"] == "REVOCABLE_UNTIL_PARENT_TERMINAL"
            and s["event"] == "TAKEOVER_ONLY"
        ),
        "revocable_explicit_revoke_available": selected(
            lambda s: s["verifier"] == "AVAILABLE"
            and s["contract"] == "REVOCABLE_UNTIL_PARENT_TERMINAL"
            and s["event"] == "EXPLICIT_REVOKE"
        ),
        "comp_failed_after_revoke_available": selected(
            lambda s: s["verifier"] == "AVAILABLE"
            and s["contract"] == "COMPENSATABLE"
            and s["event"] == "EXPLICIT_REVOKE"
            and s["compensation"] == "FAILED"
        ),
        "comp_ambiguous_no_id_expired_available": selected(
            lambda s: s["verifier"] == "AVAILABLE"
            and s["contract"] == "COMPENSATABLE"
            and s["event"] == "EXPLICIT_REVOKE"
            and s["compensation"] == "AMBIG_APPLIED"
            and s["comp_id"] == "NONE"
            and s["dedupe"] == "EXPIRED"
        ),
    }

    targeted = {}
    for name, members in slices.items():
        targeted[name] = {"scenario_count": len(members), "policies": {}}
        for policy in (
            "historical_receipt_always_success",
            "current_epoch_only",
            "contract_aware_proof",
            "contract_aware_blind_retry",
            "comp_request_is_terminal",
            "epoch_change_means_revoke",
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
            "epoch_not_revocation": (
                "An authority epoch change is not by itself semantic revocation. TAKEOVER_ONLY "
                "must not invalidate an effect that was validly authorized and applied."
            ),
            "contract_specific_history": (
                "A historical apply-time receipt remains terminal evidence for irreversible effects, "
                "but revocable/compensatable contracts require explicit revocation or compensation state."
            ),
            "revocation_tombstone": (
                "For revocable effects, an explicit current revocation tombstone can establish a "
                "CANCELLED terminal disposition; epoch mismatch alone cannot substitute for it."
            ),
            "compensation_finality": (
                "For compensatable effects, compensation request/attempt is not terminal. A durable "
                "compensation effect identity/status or still-valid idempotent retry proof is needed."
            ),
            "ambiguous_compensation": (
                "Blind retry after ambiguous compensation plus dedupe expiry can duplicate the undo "
                "effect; fail closed unless durable compensation identity/status resolves it."
            ),
        },
    }
    print(json.dumps(result, indent=2, sort_keys=True))

if __name__ == "__main__":
    main()
