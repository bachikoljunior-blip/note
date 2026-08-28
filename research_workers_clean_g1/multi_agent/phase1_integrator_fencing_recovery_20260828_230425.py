from itertools import product
from collections import Counter, defaultdict
import json

PROTOCOLS = ["cas_only", "cancel_only", "generation_leaf_integrator_epoch_fenced"]

def scenarios():
    sid = 0
    for parent_event in ["none", "supersede", "cancel"]:
        cancel_obs_vals = [False] if parent_event == "none" else [False, True]
        eq_vals = [(False, False, False)] if parent_event != "supersede" else list(product([False, True], repeat=3))
        reval_vals = [False] if parent_event != "supersede" else [False, True]
        for integrator_takeover, cancel_observed, cas_conflict, crash in product([False, True], cancel_obs_vals, [False, True], [False, True]):
            move_vals = [False, True] if crash else [False]
            for canonical_move_after_crash in move_vals:
                for late_timing in ["none", "before_cas", "after_cas_before_resume", "after_resume"]:
                    epoch_vals = [False] if late_timing == "none" else [False, True]
                    for late_leaf_epoch_current in epoch_vals:
                        for eq in eq_vals:
                            for explicit_revalidation in reval_vals:
                                sid += 1
                                yield {
                                    "id": sid,
                                    "parent_event": parent_event,
                                    "integrator_takeover_between_read_cas": integrator_takeover,
                                    "cancel_observed_before_cas": cancel_observed,
                                    "cas_conflict_before_cas": cas_conflict,
                                    "crash_after_cas_attempt": crash,
                                    "canonical_move_after_crash": canonical_move_after_crash,
                                    "late_child_timing": late_timing,
                                    "late_leaf_epoch_current_for_old_parent": late_leaf_epoch_current,
                                    "equivalence": {
                                        "task_hash": eq[0],
                                        "input_digest": eq[1],
                                        "effect_contract": eq[2],
                                    },
                                    "explicit_revalidation": explicit_revalidation,
                                }

def exact_equivalence(s):
    e = s["equivalence"]
    return e["task_hash"] and e["input_digest"] and e["effect_contract"]

def run_protocol(s, protocol):
    parent_event = s["parent_event"]
    takeover = s["integrator_takeover_between_read_cas"]
    cancel_seen = s["cancel_observed_before_cas"]
    conflict = s["cas_conflict_before_cas"]
    crash = s["crash_after_cas_attempt"]
    moved = s["canonical_move_after_crash"]
    late = s["late_child_timing"] != "none"
    late_epoch_current = s["late_leaf_epoch_current_for_old_parent"]
    exact_eq = exact_equivalence(s)
    revalidate = s["explicit_revalidation"]

    old_integrator_current_at_cas = not takeover
    parent_still_same_active_generation = parent_event == "none"

    if protocol == "cas_only":
        old_cas_attempted = True
        old_cas_succeeds = True
        authority_valid = parent_still_same_active_generation and old_integrator_current_at_cas
    elif protocol == "cancel_only":
        old_cas_attempted = not (parent_event != "none" and cancel_seen)
        old_cas_succeeds = old_cas_attempted
        authority_valid = parent_still_same_active_generation and old_integrator_current_at_cas
    else:
        old_cas_attempted = True
        old_cas_succeeds = parent_still_same_active_generation and old_integrator_current_at_cas
        authority_valid = old_cas_succeeds

    false_parent_terminalization = old_cas_succeeds and not authority_valid

    crash_outcome_unresolved = False
    if crash and old_cas_succeeds and moved:
        if protocol in ("cas_only", "cancel_only"):
            crash_outcome_unresolved = True
        else:
            crash_outcome_unresolved = False

    late_accepted = False
    late_accept_reason = None
    if late:
        if protocol == "cas_only":
            late_accepted = True
            late_accept_reason = "name_match_auto_adopt"
        elif protocol == "cancel_only":
            if parent_event == "none" or not cancel_seen:
                late_accepted = True
                late_accept_reason = "cancel_not_observed"
        else:
            if parent_event == "none":
                if late_epoch_current and not old_cas_succeeds:
                    late_accepted = True
                    late_accept_reason = "current_generation_current_leaf_epoch_unfilled_slot"
            elif parent_event == "supersede":
                if revalidate and exact_eq:
                    late_accepted = True
                    late_accept_reason = "explicit_exact_revalidation"

    orphan_accepted_child_result = False
    if late_accepted and parent_event in ("supersede", "cancel"):
        safe_explicit_adoption = (
            protocol == "generation_leaf_integrator_epoch_fenced"
            and parent_event == "supersede"
            and revalidate
            and exact_eq
            and late_accept_reason == "explicit_exact_revalidation"
        )
        orphan_accepted_child_result = not safe_explicit_adoption

    duplicate_authoritative_child_integration = old_cas_succeeds and late_accepted

    safe_revalidated_new_parent_terminal = (
        protocol == "generation_leaf_integrator_epoch_fenced"
        and parent_event == "supersede"
        and revalidate
        and exact_eq
    )

    if parent_event == "none":
        current_parent_terminal = old_cas_succeeds and authority_valid
        terminal_is_safe = current_parent_terminal
    elif parent_event == "supersede":
        if protocol == "generation_leaf_integrator_epoch_fenced":
            current_parent_terminal = safe_revalidated_new_parent_terminal
            terminal_is_safe = current_parent_terminal
        else:
            current_parent_terminal = old_cas_succeeds
            terminal_is_safe = False if current_parent_terminal else False
    else:
        current_parent_terminal = False
        terminal_is_safe = False

    safe_state = not (
        false_parent_terminalization
        or orphan_accepted_child_result
        or duplicate_authoritative_child_integration
        or crash_outcome_unresolved
    )

    recoverable = safe_state

    return {
        "old_cas_attempted": old_cas_attempted,
        "old_cas_succeeds": old_cas_succeeds,
        "false_parent_terminalization": false_parent_terminalization,
        "late_accepted": late_accepted,
        "late_accept_reason": late_accept_reason,
        "orphan_accepted_child_result": orphan_accepted_child_result,
        "duplicate_authoritative_child_integration": duplicate_authoritative_child_integration,
        "crash_outcome_unresolved": crash_outcome_unresolved,
        "safe_revalidated_new_parent_terminal": safe_revalidated_new_parent_terminal,
        "current_parent_terminal": current_parent_terminal,
        "terminal_is_safe": terminal_is_safe,
        "safe_state": safe_state,
        "recoverable": recoverable,
        "cas_conflict_was_retried": conflict and old_cas_attempted,
    }

def aggregate(rows):
    c = Counter()
    for _, o in rows:
        c["scenarios"] += 1
        for k in [
            "old_cas_attempted", "old_cas_succeeds", "false_parent_terminalization",
            "late_accepted", "orphan_accepted_child_result", "duplicate_authoritative_child_integration",
            "crash_outcome_unresolved", "safe_revalidated_new_parent_terminal",
            "current_parent_terminal", "terminal_is_safe", "safe_state", "recoverable",
            "cas_conflict_was_retried",
        ]:
            if o[k]:
                c[k] += 1
    return dict(c)

def slice_count(rows, pred, metric=None):
    selected = [(s,o) for s,o in rows if pred(s,o)]
    if metric is None:
        return len(selected)
    return sum(1 for s,o in selected if o[metric])

def main():
    scens = list(scenarios())
    result = {
        "model": {
            "scenario_count": len(scens),
            "protocol_contracts": {
                "cas_only": "same-file blob-SHA CAS; blind refresh+retry on storage conflict; no parent-generation, leaf-epoch, or integrator-epoch authority check; current-content-only crash readback",
                "cancel_only": "CAS-only plus best-effort cancellation signal; old work is blocked only if cancellation is observed before the authoritative write",
                "generation_leaf_integrator_epoch_fenced": "revalidate current parent generation + leaf slot/epoch + integrator epoch immediately before CAS; preserve monotonic applied_integration_id for crash reconciliation; superseded child adoption requires explicit exact task_hash + input_digest + effect_contract proof",
            },
            "event_order": [
                "integrator_read(g1, integrator_epoch=1, child A1/B1 current)",
                "optional parent_supersede_or_cancel",
                "optional integrator_takeover(epoch=2)",
                "optional late old-child completion",
                "integrator_CAS(with optional storage conflict + one retry)",
                "optional crash_before_readback",
                "optional later canonical move",
                "resume_reconcile",
                "optional explicit superseded-child revalidation"
            ],
            "scope": "finite balanced mechanism lattice; not an operational incidence estimate",
        },
        "protocols": {},
        "mechanism_slices": {},
        "negative_control": {},
    }

    all_rows = {}
    for p in PROTOCOLS:
        rows = [(s, run_protocol(s,p)) for s in scens]
        all_rows[p] = rows
        result["protocols"][p] = aggregate(rows)

    slices = {}
    for p, rows in all_rows.items():
        slices[p] = {
            "parent_transition_old_cas_slice": {
                "n": slice_count(rows, lambda s,o: s["parent_event"] != "none"),
                "false_parent_terminalization": slice_count(rows, lambda s,o: s["parent_event"] != "none", "false_parent_terminalization"),
            },
            "integrator_takeover_no_parent_change_slice": {
                "n": slice_count(rows, lambda s,o: s["parent_event"] == "none" and s["integrator_takeover_between_read_cas"]),
                "false_parent_terminalization": slice_count(rows, lambda s,o: s["parent_event"] == "none" and s["integrator_takeover_between_read_cas"], "false_parent_terminalization"),
            },
            "crash_then_canonical_move_after_success_slice": {
                "n": slice_count(rows, lambda s,o: s["crash_after_cas_attempt"] and s["canonical_move_after_crash"] and o["old_cas_succeeds"]),
                "crash_outcome_unresolved": slice_count(rows, lambda s,o: s["crash_after_cas_attempt"] and s["canonical_move_after_crash"] and o["old_cas_succeeds"], "crash_outcome_unresolved"),
            },
            "late_after_parent_transition_slice": {
                "n": slice_count(rows, lambda s,o: s["parent_event"] != "none" and s["late_child_timing"] != "none"),
                "orphan_accepted_child_result": slice_count(rows, lambda s,o: s["parent_event"] != "none" and s["late_child_timing"] != "none", "orphan_accepted_child_result"),
            },
            "parent_transition_with_storage_conflict_slice": {
                "n": slice_count(rows, lambda s,o: s["parent_event"] != "none" and s["cas_conflict_before_cas"]),
                "false_parent_terminalization": slice_count(rows, lambda s,o: s["parent_event"] != "none" and s["cas_conflict_before_cas"], "false_parent_terminalization"),
            },
            "parent_transition_cancel_observed_slice": {
                "n": slice_count(rows, lambda s,o: s["parent_event"] != "none" and s["cancel_observed_before_cas"]),
                "false_parent_terminalization": slice_count(rows, lambda s,o: s["parent_event"] != "none" and s["cancel_observed_before_cas"], "false_parent_terminalization"),
            },
            "parent_transition_cancel_delayed_slice": {
                "n": slice_count(rows, lambda s,o: s["parent_event"] != "none" and not s["cancel_observed_before_cas"]),
                "false_parent_terminalization": slice_count(rows, lambda s,o: s["parent_event"] != "none" and not s["cancel_observed_before_cas"], "false_parent_terminalization"),
            },
        }
    result["mechanism_slices"] = slices

    fenced_rows = all_rows["generation_leaf_integrator_epoch_fenced"]
    reval_slice = [(s,o) for s,o in fenced_rows if s["parent_event"] == "supersede" and s["late_child_timing"] != "none"]
    result["revalidation"] = {
        "superseded_late_child_scenarios": len(reval_slice),
        "safe_adoptions": sum(1 for s,o in reval_slice if o["late_accepted"] and not o["orphan_accepted_child_result"]),
        "accepted_without_explicit_revalidation": sum(1 for s,o in reval_slice if o["late_accepted"] and not s["explicit_revalidation"]),
        "accepted_with_nonexact_equivalence": sum(1 for s,o in reval_slice if o["late_accepted"] and not exact_equivalence(s)),
    }

    neg = Counter()
    for s,o in fenced_rows:
        if s["parent_event"] == "supersede" and s["late_child_timing"] != "none":
            neg["superseded_late_child_scenarios"] += 1
            neg["auto_admitted"] += 1
            if not (s["explicit_revalidation"] and exact_equivalence(s)):
                neg["orphan_authority"] += 1
    result["negative_control"] = {
        "fenced_but_name_match_auto_adopt": dict(neg)
    }

    ablation = {}
    ablation["remove_parent_generation_gate"] = {
        "new_false_parent_terminalization": sum(
            1 for s in scens if s["parent_event"] != "none" and not s["integrator_takeover_between_read_cas"]
        )
    }
    ablation["remove_integrator_epoch_gate"] = {
        "new_false_parent_terminalization": sum(
            1 for s in scens if s["parent_event"] == "none" and s["integrator_takeover_between_read_cas"]
        )
    }
    ablation["remove_child_slot_single_assignment"] = {
        "new_duplicate_authoritative_child_integration": sum(
            1 for s in scens
            if s["parent_event"] == "none"
            and not s["integrator_takeover_between_read_cas"]
            and s["late_child_timing"] != "none"
            and s["late_leaf_epoch_current_for_old_parent"]
        )
    }
    ablation["remove_applied_integration_id_log"] = {
        "new_crash_outcome_unresolved": sum(
            1 for s,o in fenced_rows
            if o["old_cas_succeeds"] and s["crash_after_cas_attempt"] and s["canonical_move_after_crash"]
        )
    }
    ablation["remove_exact_revalidation_gate"] = {
        "new_orphan_authority": neg["orphan_authority"]
    }
    result["one_gate_ablation"] = ablation

    examples = {}
    for p, rows in all_rows.items():
        ex = next(({"scenario":s,"outcome":o} for s,o in rows if o["false_parent_terminalization"]), None)
        if ex: examples[p+"_false_terminal_example"] = ex
        ex2 = next(({"scenario":s,"outcome":o} for s,o in rows if o["crash_outcome_unresolved"]), None)
        if ex2: examples[p+"_crash_ambiguity_example"] = ex2
        ex3 = next(({"scenario":s,"outcome":o} for s,o in rows if o["orphan_accepted_child_result"]), None)
        if ex3: examples[p+"_orphan_example"] = ex3
    result["examples"] = examples

    print(json.dumps(result, indent=2, sort_keys=True))

if __name__ == "__main__":
    main()
