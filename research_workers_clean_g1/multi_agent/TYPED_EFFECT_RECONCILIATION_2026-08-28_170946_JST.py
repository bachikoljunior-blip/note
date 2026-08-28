from __future__ import annotations
from itertools import product
import json

EFFECTS = ("NONE", "PENDING", "PARTIAL", "COMPLETE")
READ_MODES = ("CURRENT", "STALE_NONE", "STALE_COMPLETE", "UNKNOWN")
COMP_RESIDUAL = ("PRESENT", "PARTIAL", "ABSENT")


def observe_effect(actual: str, mode: str) -> str:
    if mode == "CURRENT":
        return actual
    if mode == "STALE_NONE":
        return "NONE"
    if mode == "STALE_COMPLETE":
        return "COMPLETE"
    return "UNKNOWN"


def observe_residual(actual: str, mode: str) -> str:
    if mode == "CURRENT":
        return actual
    if mode == "STALE_NONE":
        return "ABSENT"
    if mode == "STALE_COMPLETE":
        return "PRESENT"
    return "UNKNOWN"


def summarize(rows, terminal_key="terminal", unsafe_key="unsafe"):
    worlds = len(rows)
    terminal = sum(bool(r[terminal_key]) for r in rows)
    unsafe = sum(bool(r[terminal_key]) and bool(r[unsafe_key]) for r in rows)
    return {
        "worlds": worlds,
        "terminal_admissions": terminal,
        "terminal_rate": terminal / worlds if worlds else None,
        "unsafe_terminal": unsafe,
        "unsafe_given_terminal": unsafe / terminal if terminal else None,
    }


def forward_retry_worlds():
    """Exact same-intent retry worlds after a fully certified idempotency contract.

    Certification guarantees one logical operation, not settlement finality.
    If the operation did not exist, an accepted retry may still leave it pending/partial/complete.
    If it already exists, the idempotent retry preserves that operation's current effect state.
    """
    rows = []
    for pre in EFFECTS:
        outcomes = ("PENDING", "PARTIAL", "COMPLETE") if pre == "NONE" else (pre,)
        for post in outcomes:
            rows.append({"pre": pre, "post": post})
    return rows


def forward_study():
    base = forward_retry_worlds()
    trust = []
    current = []
    reads = []
    freshness = []
    for w in base:
        safe = w["post"] == "COMPLETE"
        trust.append({**w, "terminal": True, "unsafe": not safe})
        current.append({**w, "terminal": safe, "unsafe": False})
        for mode in READ_MODES:
            obs = observe_effect(w["post"], mode)
            terminal_unqualified = obs == "COMPLETE"
            reads.append({**w, "mode": mode, "observed": obs,
                          "terminal": terminal_unqualified,
                          "unsafe": terminal_unqualified and not safe})
            terminal_qualified = mode == "CURRENT" and obs == "COMPLETE"
            freshness.append({**w, "mode": mode, "observed": obs,
                              "terminal": terminal_qualified,
                              "unsafe": False})
    return {
        "base_worlds": len(base),
        "trust_certified_retry_as_completion": summarize(trust),
        "authoritative_post_action_current_proof": summarize(current),
        "unqualified_complete_read_after_retry": summarize(reads),
        "freshness_qualified_complete_read_after_retry": summarize(freshness),
    }


def destructive_authority_study():
    rows_unqualified = []
    rows_qualified = []
    for actual, mode in product(EFFECTS, READ_MODES):
        obs = observe_effect(actual, mode)
        authorize = obs == "NONE"
        rows_unqualified.append({"actual": actual, "mode": mode, "observed": obs,
                                 "terminal": authorize, "unsafe": authorize and actual != "NONE"})
        authorize_q = mode == "CURRENT" and obs == "NONE"
        rows_qualified.append({"actual": actual, "mode": mode, "observed": obs,
                               "terminal": authorize_q, "unsafe": False})
    return {
        "interpretation": "terminal_admissions here mean destructive-action authority granted from an observed-absent state, not a completed rollback.",
        "absence_without_freshness": summarize(rows_unqualified),
        "freshness_qualified_absence": summarize(rows_qualified),
    }


def compensation_study():
    trust = []
    current = []
    reads = []
    qualified = []
    # Three different pre-compensation effect classes; a certified compensation request can be
    # accepted while its physical undo is still pending/partial or fully absent.
    for pre in ("PENDING", "PARTIAL", "COMPLETE"):
        for residual in COMP_RESIDUAL:
            safe = residual == "ABSENT"
            trust.append({"pre": pre, "residual": residual, "terminal": True, "unsafe": not safe})
            current.append({"pre": pre, "residual": residual, "terminal": safe, "unsafe": False})
            for mode in READ_MODES:
                obs = observe_residual(residual, mode)
                t = obs == "ABSENT"
                reads.append({"pre": pre, "residual": residual, "mode": mode, "observed": obs,
                              "terminal": t, "unsafe": t and not safe})
                tq = mode == "CURRENT" and obs == "ABSENT"
                qualified.append({"pre": pre, "residual": residual, "mode": mode, "observed": obs,
                                  "terminal": tq, "unsafe": False})
    return {
        "base_worlds": len(trust),
        "trust_compensation_idempotency_as_rollback_complete": summarize(trust),
        "authoritative_post_compensation_current_proof": summarize(current),
        "unqualified_absent_read_after_compensation": summarize(reads),
        "freshness_qualified_absent_read_after_compensation": summarize(qualified),
    }


def branching_point_of_no_return():
    """Toy A->{B,C} slice where C is irreversible once COMPLETE.

    The slice conditions on C already being COMPLETE, so clean rollback is structurally impossible.
    B can be NONE/PENDING/PARTIAL/COMPLETE and its exact same-intent retry contract may or may not
    be certified. Forward terminalization is possible if B is already COMPLETE or B is retryable.
    """
    rows = []
    for b_state, b_retry_cert in product(EFFECTS, (False, True)):
        rollback_possible = False
        forward_possible = b_state == "COMPLETE" or b_retry_cert
        rows.append({
            "B": b_state,
            "B_retry_certified": b_retry_cert,
            "C": "COMPLETE_IRREVERSIBLE",
            "rollback_possible": rollback_possible,
            "forward_reconciliation_possible": forward_possible,
        })
    return {
        "worlds_in_point_of_no_return_slice": len(rows),
        "clean_rollback_possible": sum(r["rollback_possible"] for r in rows),
        "safe_forward_reconciliation_available": sum(r["forward_reconciliation_possible"] for r in rows),
        "safe_forward_reconciliation_rate": sum(r["forward_reconciliation_possible"] for r in rows) / len(rows),
        "blocked_without_safe_terminal": sum(not r["forward_reconciliation_possible"] for r in rows),
    }


def run():
    return {
        "schema_version": 2,
        "mechanism": "typed asynchronous effect state + freshness-qualified reconciliation + symmetric compensation contract + branching point-of-no-return",
        "effect_states": EFFECTS,
        "read_modes": READ_MODES,
        "forward": forward_study(),
        "destructive_action_authority": destructive_authority_study(),
        "compensation": compensation_study(),
        "branching_point_of_no_return": branching_point_of_no_return(),
        "controller_implications": [
            "Treat idempotency certification as request-identity/multiplicity evidence, never as settlement/finality evidence.",
            "Store effect currentness separately as resource identity + typed state + amount + observation source + observation/version/event time + observed-at time.",
            "Webhook/event evidence must not silently become latest-state proof when delivery can duplicate or reorder; reconcile ordering/version and fetch current resource state when required by risk.",
            "Grant destructive compensation authority only from freshness-qualified current-state evidence; stale absence is not proof of no live effect.",
            "Give compensation its own same-intent idempotency contract and its own post-action effect proof; compensation request dedupe does not imply rollback completion.",
            "After an irreversible branch crosses a point of no return, prefer proven forward reconciliation when available; otherwise remain nonterminal rather than assert a clean rollback.",
        ],
        "scope": [
            "All proportions are exact counts on deliberately balanced synthetic mechanism lattices; they are not provider incident rates or empirical reliability estimates.",
            "CURRENT is an idealized authoritative freshness-qualified read. Real providers can have eventual consistency, endpoint-specific lag, and resource-version semantics that must be modeled separately.",
            "PENDING/PARTIAL/COMPLETE are generic controller states, not a claim that every provider exposes exactly these labels or monotone transitions.",
            "The branching study is a toy A->{B,C} slice conditioned on C already COMPLETE and irreversible; it demonstrates admissibility structure, not workflow prevalence.",
        ],
    }


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
