from itertools import product
from collections import Counter
import json

REL = ["UNCHANGED", "CHANGED"]
PROOF = ["ABSORBING", "CURRENT_ONLY", "ACTIVE"]
COMP = ["FINAL", "AMBIGUOUS", "FAILED", "LATE_REVERSAL"]
COUPLING = ["INDEPENDENT", "COUPLED"]
BOOL = [False, True]

def unchanged_ready(proof, reseal):
    return proof == "ABSORBING" or (proof == "CURRENT_ONLY" and reseal)

def retirement_ready(comp, reseal):
    return comp == "FINAL" or (comp == "LATE_REVERSAL" and reseal)

def scenarios():
    out = []
    for relA, relB in product(REL, repeat=2):
        if relA == relB == "UNCHANGED":
            continue
        for proofA, proofB, compA, compB, coupling, early, takeover, response_loss, reseal, transfer in product(
            PROOF, PROOF, COMP, COMP, COUPLING, BOOL, BOOL, BOOL, BOOL, BOOL
        ):
            if relA == "UNCHANGED" and compA != "FINAL":
                continue
            if relB == "UNCHANGED" and compB != "FINAL":
                continue
            out.append({
                "relA": relA, "relB": relB,
                "proofA": proofA, "proofB": proofB,
                "compA": compA, "compB": compB,
                "coupling": coupling,
                "early": early,
                "takeover": takeover,
                "response_loss": response_loss,
                "reseal": reseal,
                "transfer": transfer,
            })
    return out

def evaluate(s, strategy):
    rels = [s["relA"], s["relB"]]
    proofs = [s["proofA"], s["proofB"]]
    comps = [s["compA"], s["compB"]]
    changed = [i for i, r in enumerate(rels) if r == "CHANGED"]
    completed = [False, False]
    unsafe = False
    duplicate_comp = False
    duplicate_new = False
    reasons = []

    if strategy == "blind_changed":
        for i in range(2):
            if rels[i] == "UNCHANGED":
                completed[i] = True
                if not unchanged_ready(proofs[i], s["reseal"]):
                    unsafe = True
                    duplicate_new = True
                    reasons.append("unchanged_without_absorbing_adoption")
            else:
                completed[i] = True
                unsafe = True
                reasons.append("changed_new_before_old_retirement")
        if s["early"]:
            unsafe = True

    elif strategy == "weak_compensate_retry":
        for i in range(2):
            if rels[i] == "UNCHANGED":
                if proofs[i] in ("ABSORBING", "CURRENT_ONLY"):
                    completed[i] = True
            else:
                apparent = comps[i] in ("FINAL", "LATE_REVERSAL")
                if (s["takeover"] or s["response_loss"]) and comps[i] in ("AMBIGUOUS", "FINAL", "LATE_REVERSAL"):
                    duplicate_comp = True
                if apparent:
                    completed[i] = True
                    if comps[i] == "LATE_REVERSAL":
                        unsafe = True
                        reasons.append("late_compensation_reversal")
                elif s["early"]:
                    completed[i] = True
                    unsafe = True
                    reasons.append("early_g2_before_retirement")
        if s["coupling"] == "COUPLED" and len(changed) == 2 and sum(completed[i] for i in changed) == 1:
            unsafe = True
            reasons.append("coupled_mixed_generation")

    elif strategy == "vector_retire_then_activate":
        unchanged_ok = all(
            unchanged_ready(proofs[i], s["reseal"])
            for i in range(2) if rels[i] == "UNCHANGED"
        )
        changed_ok = all(retirement_ready(comps[i], s["reseal"]) for i in changed)
        if unchanged_ok and changed_ok:
            completed = [True, True]

    elif strategy == "per_component_retire_then_activate":
        for i in range(2):
            if rels[i] == "UNCHANGED":
                if unchanged_ready(proofs[i], s["reseal"]):
                    completed[i] = True
            elif retirement_ready(comps[i], s["reseal"]):
                completed[i] = True
        if s["coupling"] == "COUPLED" and len(changed) == 2:
            if sum(completed[i] for i in changed) == 1:
                unsafe = True
                reasons.append("coupled_mixed_generation")

    elif strategy == "graph_barrier":
        for i in range(2):
            if rels[i] == "UNCHANGED" and unchanged_ready(proofs[i], s["reseal"]):
                completed[i] = True
        if s["coupling"] == "INDEPENDENT" or len(changed) < 2:
            for i in changed:
                if retirement_ready(comps[i], s["reseal"]):
                    completed[i] = True
        else:
            if all(retirement_ready(comps[i], s["reseal"]) for i in changed):
                for i in changed:
                    completed[i] = True

    elif strategy == "atomic_group_transfer":
        for i in range(2):
            if rels[i] == "UNCHANGED" and unchanged_ready(proofs[i], s["reseal"]):
                completed[i] = True
        if s["transfer"]:
            for i in changed:
                completed[i] = True

    else:
        raise ValueError(strategy)

    return {
        "terminal": all(completed),
        "unsafe": unsafe,
        "duplicate_comp": duplicate_comp,
        "duplicate_new": duplicate_new,
        "progress": sum(completed),
        "reasons": sorted(set(reasons)),
    }

def summarize(rows, strategy):
    c = Counter()
    reasons = Counter()
    for s in rows:
        r = evaluate(s, strategy)
        c["terminal"] += int(r["terminal"])
        c["unsafe"] += int(r["unsafe"])
        c["duplicate_comp"] += int(r["duplicate_comp"])
        c["duplicate_new"] += int(r["duplicate_new"])
        c["progress_units"] += r["progress"]
        c["unsafe_terminal"] += int(r["terminal"] and r["unsafe"])
        c["safe_nonterminal"] += int((not r["terminal"]) and (not r["unsafe"]))
        for reason in r["reasons"]:
            reasons[reason] += 1
    return dict(c), dict(reasons)

def main():
    rows = scenarios()
    strategies = [
        "blind_changed",
        "weak_compensate_retry",
        "vector_retire_then_activate",
        "per_component_retire_then_activate",
        "graph_barrier",
        "atomic_group_transfer",
    ]
    result = {
        "schema_version": 1,
        "scenario_count": len(rows),
        "strategies": {},
        "slices": {},
        "interpretation": {
            "scope": "Two-resource finite synthetic mechanism lattice; counts are not production failure rates.",
            "safety_definition": "No changed-contract g2 authority is live while conflicting g1 authority can still revive; coupled changed resources cannot expose a mixed logical generation unless the coupling contract explicitly permits it.",
        },
    }
    for st in strategies:
        counts, reasons = summarize(rows, st)
        result["strategies"][st] = {"counts": counts, "reasons": reasons}

    coupled_partial = [
        s for s in rows
        if s["relA"] == s["relB"] == "CHANGED"
        and s["coupling"] == "COUPLED"
        and (
            int(retirement_ready(s["compA"], s["reseal"]))
            + int(retirement_ready(s["compB"], s["reseal"]))
            == 1
        )
    ]
    independent_partial = [
        s for s in rows
        if s["relA"] == s["relB"] == "CHANGED"
        and s["coupling"] == "INDEPENDENT"
        and (
            int(retirement_ready(s["compA"], s["reseal"]))
            + int(retirement_ready(s["compB"], s["reseal"]))
            == 1
        )
    ]
    late_no_reseal = [
        s for s in rows
        if not s["reseal"] and any(
            s[f"rel{x}"] == "CHANGED" and s[f"comp{x}"] == "LATE_REVERSAL"
            for x in ("A", "B")
        )
    ]
    graph_adv = [
        s for s in rows
        if not evaluate(s, "graph_barrier")["unsafe"]
        and evaluate(s, "graph_barrier")["progress"]
           > evaluate(s, "vector_retire_then_activate")["progress"]
    ]

    result["slices"] = {
        "coupled_two_changed_exactly_one_retired": {
            "count": len(coupled_partial),
            "per_component_unsafe": sum(evaluate(s, "per_component_retire_then_activate")["unsafe"] for s in coupled_partial),
            "graph_barrier_unsafe": sum(evaluate(s, "graph_barrier")["unsafe"] for s in coupled_partial),
        },
        "independent_two_changed_exactly_one_retired": {
            "count": len(independent_partial),
            "per_component_progress_units": sum(evaluate(s, "per_component_retire_then_activate")["progress"] for s in independent_partial),
            "vector_barrier_progress_units": sum(evaluate(s, "vector_retire_then_activate")["progress"] for s in independent_partial),
            "graph_barrier_progress_units": sum(evaluate(s, "graph_barrier")["progress"] for s in independent_partial),
        },
        "late_reversal_without_reseal": {
            "count": len(late_no_reseal),
            "weak_unsafe": sum(evaluate(s, "weak_compensate_retry")["unsafe"] for s in late_no_reseal),
            "graph_terminal": sum(evaluate(s, "graph_barrier")["terminal"] for s in late_no_reseal),
        },
        "graph_barrier_safe_progress_advantage_over_vector": {
            "scenario_count": len(graph_adv),
            "extra_progress_units": sum(
                evaluate(s, "graph_barrier")["progress"]
                - evaluate(s, "vector_retire_then_activate")["progress"]
                for s in graph_adv
            ),
        },
    }

    assert result["strategies"]["graph_barrier"]["counts"]["unsafe"] == 0
    assert result["strategies"]["vector_retire_then_activate"]["counts"]["unsafe"] == 0
    assert result["strategies"]["atomic_group_transfer"]["counts"]["unsafe"] == 0
    assert result["slices"]["coupled_two_changed_exactly_one_retired"]["per_component_unsafe"] == len(coupled_partial)
    assert result["slices"]["independent_two_changed_exactly_one_retired"]["vector_barrier_progress_units"] == 0

    print(json.dumps(result, indent=2, sort_keys=True))

if __name__ == "__main__":
    main()
