from itertools import product
from collections import Counter, defaultdict
import json

OUTCOMES = ("ok", "fail", "amb_applied", "amb_not_applied")
PRE = ("none", "takeover", "cancel")
TRANS = ("none", "crash", "takeover", "cancel")
POST_FINAL = ("none", "takeover", "cancel")
ORDERS = ("parent_first", "manifest_first")


def request_applies(outcome, retry):
    """Strong per-request idempotent retry: read-before-retry, then retry only if absent."""
    if outcome == "ok":
        return True
    if outcome == "fail":
        return False
    if outcome == "amb_applied":
        return True
    if outcome == "amb_not_applied":
        return bool(retry)  # the retry is assumed to succeed in this finite mechanism test
    raise ValueError(outcome)


def is_amb(outcome):
    return outcome.startswith("amb_")


def authority_live(pre, mid="none", post_data="none"):
    return pre == "none" and mid not in ("takeover", "cancel") and post_data not in ("takeover", "cancel")


def current_canceled(*transitions):
    return "cancel" in transitions


def split_eval(s):
    # Strong split candidate: deterministic txid, per-path read-before-retry, parent/epoch
    # revalidation before the second write, and terminality defined only by matching pair.
    reached1 = s["pre"] == "none"
    a1 = reached1 and request_applies(s["w1"], s["r1"])
    blocked_between = s["mid"] in ("takeover", "cancel")
    reached2 = reached1 and not blocked_between
    a2 = reached2 and request_applies(s["w2"], s["r2"])

    if s["order"] == "parent_first":
        parent_applied, manifest_applied = a1, a2
        manifest_outcome, manifest_retry, manifest_reached = s["w2"], s["r2"], reached2
    else:
        manifest_applied, parent_applied = a1, a2
        manifest_outcome, manifest_retry, manifest_reached = s["w1"], s["r1"], reached1

    pair_committed_before_later_transition = parent_applied and manifest_applied
    # A later takeover does not retroactively invalidate an already committed tx.
    # A later cancel creates a new current parent generation/lifecycle, so current terminal=false.
    current_terminal = pair_committed_before_later_transition and not current_canceled(s["post_data"], s["post_final"])

    # Pair-checked strong protocol never declares terminal from one file alone.
    false_terminal_pair_checked = False

    # Negative control: parent-local terminal bit is treated as sufficient authority.
    # This is false whenever parent says terminal but matching manifest is absent, or current parent later canceled.
    # Any parent-first success transiently exposes parent terminality before the manifest CAS.
    # For manifest-first, a false local terminal appears only if parent lands while manifest did not.
    false_terminal_parent_local = (
        (s["order"] == "parent_first" and a1) or
        (s["order"] == "manifest_first" and parent_applied and not manifest_applied)
    )

    partial = (parent_applied != manifest_applied)
    partial_exposure_any = bool(a1)  # any successful first file write is externally visible before the second file CAS
    recoverable_partial = partial  # with both current reads + txid/epoch, can finish or classify stale

    recovery_needed = (
        is_amb(s["w1"]) or (reached2 and is_amb(s["w2"])) or
        s["mid"] != "none" or s["post_data"] != "none" or s["post_final"] != "none" or partial
    )
    single_read_recoverable = False if recovery_needed else True

    # Negative control: blindly appending a canonical integration on ambiguous-applied retry duplicates it.
    blind_retry_duplicate = manifest_reached and manifest_outcome == "amb_applied" and manifest_retry

    return {
        "current_terminal": current_terminal,
        "false_terminal": false_terminal_pair_checked,
        "false_terminal_parent_local_ablation": false_terminal_parent_local,
        "partial": partial,
        "partial_exposure_any": partial_exposure_any,
        "recoverable_partial": recoverable_partial,
        "recovery_needed": recovery_needed,
        "single_read_recoverable": single_read_recoverable,
        "duplicate_integration": False,
        "terminal_single_read_provable": current_terminal and False,
        "blind_retry_duplicate_ablation": blind_retry_duplicate,
    }


def colocated_eval(s):
    # One CAS-protected object co-locates parent generation/lifecycle, integrator epoch,
    # canonical manifest and applied_integration_id. w1 is the single authoritative CAS.
    reached = s["pre"] == "none"
    applied = reached and request_applies(s["w1"], s["r1"])
    # All later cancel points change the same object and current terminal becomes false;
    # takeovers after a successful commit do not retroactively invalidate it.
    canceled_later = current_canceled(s["mid"], s["post_data"], s["post_final"])
    current_terminal = applied and not canceled_later

    recovery_needed = is_amb(s["w1"]) or any(x != "none" for x in (s["mid"], s["post_data"], s["post_final"]))
    # Because the authoritative state and integration id are co-located, one current object read
    # distinguishes applied/not-applied/current-canceled in this finite model.
    single_read_recoverable = True

    return {
        "current_terminal": current_terminal,
        "false_terminal": False,
        "partial": False,
        "partial_exposure_any": False,
        "recoverable_partial": False,
        "recovery_needed": recovery_needed,
        "single_read_recoverable": single_read_recoverable,
        "duplicate_integration": False,
        "terminal_single_read_provable": current_terminal,
    }


def event_eval(s):
    # Durable append-only intent is written first after initial authority check.
    intent = s["pre"] == "none"
    reached1 = intent
    a1 = reached1 and request_applies(s["w1"], s["r1"])
    blocked_between = s["mid"] in ("takeover", "cancel")
    reached2 = reached1 and not blocked_between
    a2 = reached2 and request_applies(s["w2"], s["r2"])

    if s["order"] == "parent_first":
        parent_applied, manifest_applied = a1, a2
    else:
        manifest_applied, parent_applied = a1, a2

    data_pair = parent_applied and manifest_applied
    authority_before_finalize = (
        intent and not blocked_between and s["post_data"] not in ("takeover", "cancel")
    )
    reached_final = data_pair and authority_before_finalize
    commit_event = reached_final and request_applies(s["final"], s["rf"])

    # Strong reader requires committed event + matching current parent/data pair.
    # A cancel after finalize makes the event historical/stale for current terminality.
    current_terminal = commit_event and not current_canceled(s["post_final"])
    false_terminal = False

    # Event-only negative control ignores current parent generation/lifecycle after the event.
    false_terminal_event_only = commit_event and current_canceled(s["post_final"])

    partial = intent and not current_terminal and (parent_applied or manifest_applied or data_pair)
    partial_exposure_any = bool(a1)  # physical split state exists after first data-file write even though not yet authoritative
    recoverable_partial = partial  # intent persists target tx; reconciler can inspect both files and current authority

    recovery_needed = (
        intent and (
            is_amb(s["w1"]) or (reached2 and is_amb(s["w2"])) or
            (reached_final and is_amb(s["final"])) or
            s["mid"] != "none" or s["post_data"] != "none" or s["post_final"] != "none" or partial
        )
    )
    # Current commit event alone is insufficient because current parent can supersede/cancel later.
    # Intent alone is also insufficient to distinguish which data write landed.
    single_read_recoverable = False if recovery_needed else True

    return {
        "current_terminal": current_terminal,
        "false_terminal": false_terminal,
        "false_terminal_event_only_ablation": false_terminal_event_only,
        "partial": partial,
        "partial_exposure_any": partial_exposure_any,
        "recoverable_partial": recoverable_partial,
        "recovery_needed": recovery_needed,
        "single_read_recoverable": single_read_recoverable,
        "duplicate_integration": False,
        "terminal_single_read_provable": current_terminal and False,
    }


def aggregate(evaluator, scenarios):
    c = Counter()
    for s in scenarios:
        r = evaluator(s)
        c["scenarios"] += 1
        for k, v in r.items():
            if v:
                c[k] += 1
        if r.get("recovery_needed"):
            if r.get("single_read_recoverable"):
                c["recovery_needed_single_read_yes"] += 1
            else:
                c["recovery_needed_single_read_no"] += 1
    return dict(c)


def main():
    scenarios = []
    for pre, order, w1, r1, mid, w2, r2, post_data, final, rf, post_final in product(
        PRE, ORDERS, OUTCOMES, (False, True), TRANS, OUTCOMES, (False, True), TRANS, OUTCOMES, (False, True), POST_FINAL
    ):
        scenarios.append({
            "pre": pre, "order": order,
            "w1": w1, "r1": r1, "mid": mid,
            "w2": w2, "r2": r2, "post_data": post_data,
            "final": final, "rf": rf, "post_final": post_final,
        })

    result = {
        "schema_version": 1,
        "model": "authority-domain atomicity finite mechanism lattice",
        "scenario_count": len(scenarios),
        "axes": {
            "pre_transition": list(PRE),
            "write_order": list(ORDERS),
            "request_outcome": list(OUTCOMES),
            "retry_after_ambiguous": [False, True],
            "mid_transition": list(TRANS),
            "post_data_transition": list(TRANS),
            "post_finalize_transition": list(POST_FINAL),
        },
        "protocols": {
            "split_two_cas_pair_checked": aggregate(split_eval, scenarios),
            "co_located_single_object_cas": aggregate(colocated_eval, scenarios),
            "split_append_only_intent_event_reconcile": aggregate(event_eval, scenarios),
        },
        "scope_notes": [
            "Counts are exhaustive over an equal-weight synthetic lattice, not operational failure probabilities.",
            "Per-request strong retry uses read-before-retry with deterministic txid; the retry after amb_not_applied is assumed to succeed.",
            "takeover invalidates an in-progress old integrator but does not retroactively invalidate a transaction already fully committed before takeover.",
            "cancel advances current parent lifecycle/generation and therefore removes old integration from current terminality even if historically committed.",
            "split pair-checked safety requires reading both authority files; parent-local terminality is reported separately as an unsafe ablation.",
            "event protocol treats the append-only commit event as necessary but not sufficient: current parent/data state must still be cross-checked.",
            "co-located one-CAS safety assumes every authority-changing writer updates the same object and preserves applied_integration_id.",
        ],
    }

    # Derived comparisons useful for checkpoint text.
    p = result["protocols"]
    derived = {}
    for name, d in p.items():
        n = d["scenarios"]
        derived[name] = {
            "terminal_rate": d.get("current_terminal", 0) / n,
            "partial_rate": d.get("partial", 0) / n,
            "partial_exposure_any_rate": d.get("partial_exposure_any", 0) / n,
            "recovery_needed": d.get("recovery_needed", 0),
            "single_read_recovery_fraction_when_needed": (
                d.get("recovery_needed_single_read_yes", 0) / d.get("recovery_needed", 1)
                if d.get("recovery_needed", 0) else 1.0
            ),
            "false_terminal": d.get("false_terminal", 0),
            "duplicate_integration": d.get("duplicate_integration", 0),
            "terminal_single_read_fraction": (d.get("terminal_single_read_provable", 0) / d.get("current_terminal", 1) if d.get("current_terminal", 0) else 1.0),
        }
    result["derived"] = derived

    print(json.dumps(result, indent=2, sort_keys=True))

if __name__ == "__main__":
    main()
