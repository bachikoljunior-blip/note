#!/usr/bin/env python3
from itertools import product
import json

# Synthetic cross-authority TOCTOU model.
# Original effect B is already exactly compensated by 40. Original A requires 60.
# An authoritative sink read observes resource A at version 3 as SETTLED or FAILED.
# A version-4 transition may occur at one of several points before repository terminal publication.

AXES = {
    "initial": ["SETTLED", "FAILED"],
    "transition": ["SAME", "FLIP", "REVERSED"],
    "stage": ["NONE", "BEFORE_REREAD", "BETWEEN_REREAD_AND_CHECK", "AFTER_CHECK_BEFORE_REPO"],
    "absorbing_token": ["NO", "YES"],
    "verifier": ["AVAILABLE", "OUTAGE"],
    "takeover": ["NO", "YES"],
    "cas": ["CONFIRMED_APPLIED", "AMBIG_APPLIED", "AMBIG_NOT_APPLIED"],
    "repeat": ["NO", "YES"],
}
SCENARIOS = [dict(zip(AXES, vals)) for vals in product(*AXES.values())]


def target(initial, transition):
    if transition == "SAME":
        return initial
    if transition == "FLIP":
        return "FAILED" if initial == "SETTLED" else "SETTLED"
    if transition == "REVERSED":
        return "REVERSED"
    raise ValueError(transition)


def transition(state, sc):
    if sc["stage"] == "NONE":
        return
    state["version"] = 4
    state["status"] = target(sc["initial"], sc["transition"])


def maybe_replace(status, sc):
    if status not in ("FAILED", "REVERSED"):
        return 0
    if sc["verifier"] != "AVAILABLE":
        return None
    # Replacement is stable over the failed resource/version, not claim epoch.
    return 1


def exact_truth(old_status, replacements):
    a_amount = (60 if old_status == "SETTLED" else 0) + 60 * replacements
    return a_amount == 60, a_amount


def repository_terminal(decide_terminal, exact, sc):
    """Stable applied_transition_id makes ambiguous retry at-most-one repository transition."""
    if not decide_terminal:
        return {
            "terminal": False,
            "false_terminal": False,
            "exact": exact,
            "repo_writes": 0,
        }

    outcome = sc["cas"]
    if outcome == "CONFIRMED_APPLIED":
        return {"terminal": True, "false_terminal": not exact, "exact": exact, "repo_writes": 1}
    if outcome == "AMBIG_APPLIED":
        # Repeat recovery first reads the stable transition identity and does not write twice.
        return {"terminal": True, "false_terminal": not exact, "exact": exact, "repo_writes": 1}

    # AMBIG_NOT_APPLIED: without recovery the repository remains nonterminal; with recovery,
    # the stable transition identity lets the retry apply once.
    if sc["repeat"] == "YES":
        return {"terminal": True, "false_terminal": not exact, "exact": exact, "repo_writes": 1}
    return {"terminal": False, "false_terminal": False, "exact": exact, "repo_writes": 0}


def finish(state, replacements, decide_terminal, sc):
    exact, amount = exact_truth(state["status"], replacements)
    out = repository_terminal(decide_terminal, exact, sc)
    out.update({"replacement_count": replacements, "a_amount": amount})
    return out


def read_then_repo(sc):
    state = {"version": 3, "status": sc["initial"]}
    replacements = maybe_replace(sc["initial"], sc)
    if replacements is None:
        return finish(state, 0, False, sc)
    if sc["stage"] != "NONE":
        transition(state, sc)
    return finish(state, replacements, True, sc)


def reread_then_repo(sc):
    state = {"version": 3, "status": sc["initial"]}
    if sc["stage"] == "BEFORE_REREAD":
        transition(state, sc)

    # This is a genuinely authoritative read at this instant, but it does not freeze the sink.
    observed = state["status"]
    replacements = maybe_replace(observed, sc)
    if replacements is None:
        return finish(state, 0, False, sc)

    if sc["stage"] in ("BETWEEN_REREAD_AND_CHECK", "AFTER_CHECK_BEFORE_REPO"):
        transition(state, sc)
    return finish(state, replacements, True, sc)


def sink_compare_only(sc):
    state = {"version": 3, "status": sc["initial"]}
    if sc["stage"] in ("BEFORE_REREAD", "BETWEEN_REREAD_AND_CHECK"):
        transition(state, sc)

    # Conditional compare occurs in the authoritative sink at this instant and handles current state.
    # It does NOT seal/finalize the resource, so another transition may still occur afterwards.
    replacements = maybe_replace(state["status"], sc)
    if replacements is None:
        return finish(state, 0, False, sc)

    if sc["stage"] == "AFTER_CHECK_BEFORE_REPO":
        transition(state, sc)
    return finish(state, replacements, True, sc)


def sink_compare_and_seal(sc):
    state = {"version": 3, "status": sc["initial"]}
    if sc["stage"] in ("BEFORE_REREAD", "BETWEEN_REREAD_AND_CHECK"):
        transition(state, sc)

    # The protected sink operation compares/reads current state and atomically seals the old
    # resource finality plus any needed replacement. An AFTER_CHECK invalidating transition is rejected.
    replacements = maybe_replace(state["status"], sc)
    if replacements is None:
        return finish(state, 0, False, sc)
    return finish(state, replacements, True, sc)


def absorbing_token(sc):
    state = {"version": 3, "status": sc["initial"]}
    if sc["absorbing_token"] != "YES":
        return finish(state, 0, False, sc)

    # A valid token means the v3 finality semantics are absorbing: later invalidating transitions
    # are not legal. A failed/reversed absorbing state may be replaced using a stable failed-resource key.
    replacements = maybe_replace(state["status"], sc)
    if replacements is None:
        return finish(state, 0, False, sc)
    return finish(state, replacements, True, sc)


DETAIL = {
    "READ_THEN_REPO_CAS": [read_then_repo(s) for s in SCENARIOS],
    "DURABLE_V3_WITNESS_REPO_CAS": [read_then_repo(s) for s in SCENARIOS],
    "REREAD_THEN_REPO_CAS": [reread_then_repo(s) for s in SCENARIOS],
    "SINK_COMPARE_ONLY_THEN_REPO_CAS": [sink_compare_only(s) for s in SCENARIOS],
    "SINK_COMPARE_AND_SEAL": [sink_compare_and_seal(s) for s in SCENARIOS],
    "ABSORBING_FINALITY_TOKEN": [absorbing_token(s) for s in SCENARIOS],
}


def summarize(rows):
    return {
        "terminal": sum(r["terminal"] for r in rows),
        "false_terminal": sum(r["false_terminal"] for r in rows),
        "exact_terminal": sum(r["terminal"] and r["exact"] for r in rows),
        "duplicate_repository_transition": sum(r["repo_writes"] > 1 for r in rows),
    }


def select(pred):
    return [i for i, s in enumerate(SCENARIOS) if pred(s)]


def slice_stats(policy, indices):
    rows = DETAIL[policy]
    return {
        "n": len(indices),
        "terminal": sum(rows[i]["terminal"] for i in indices),
        "false_terminal": sum(rows[i]["false_terminal"] for i in indices),
        "exact_terminal": sum(rows[i]["terminal"] and rows[i]["exact"] for i in indices),
    }


OUT = {
    "scenario_count": len(SCENARIOS),
    "policies": {p: summarize(rows) for p, rows in DETAIL.items()},
    "slices": {},
}

# A transition before an actual re-read can be repaired by that read, but a read made earlier cannot.
idx = select(lambda s: s["initial"] == "SETTLED"
             and s["transition"] in ("FLIP", "REVERSED")
             and s["stage"] == "BEFORE_REREAD"
             and s["verifier"] == "AVAILABLE"
             and s["cas"] == "CONFIRMED_APPLIED")
OUT["slices"]["invalidation_before_reread_read_once"] = slice_stats("READ_THEN_REPO_CAS", idx)
OUT["slices"]["invalidation_before_reread_reread"] = slice_stats("REREAD_THEN_REPO_CAS", idx)

# Even a sink-local conditional compare is stale if it does not seal and the sink changes afterwards.
idx = select(lambda s: s["initial"] == "SETTLED"
             and s["transition"] in ("FLIP", "REVERSED")
             and s["stage"] == "AFTER_CHECK_BEFORE_REPO"
             and s["cas"] == "CONFIRMED_APPLIED")
OUT["slices"]["postcheck_invalidation_reread"] = slice_stats("REREAD_THEN_REPO_CAS", idx)
OUT["slices"]["postcheck_invalidation_compare_only"] = slice_stats("SINK_COMPARE_ONLY_THEN_REPO_CAS", idx)
OUT["slices"]["postcheck_invalidation_compare_and_seal"] = slice_stats("SINK_COMPARE_AND_SEAL", idx)
OUT["slices"]["postcheck_invalidation_absorbing_token"] = slice_stats("ABSORBING_FINALITY_TOKEN", idx)

# Failed v3 is replaced; if the old resource later flips to SETTLED, a compare-only policy overcompensates.
idx = select(lambda s: s["initial"] == "FAILED"
             and s["transition"] == "FLIP"
             and s["stage"] == "AFTER_CHECK_BEFORE_REPO"
             and s["verifier"] == "AVAILABLE"
             and s["cas"] == "CONFIRMED_APPLIED")
OUT["slices"]["failed_then_old_settles_compare_only"] = slice_stats("SINK_COMPARE_ONLY_THEN_REPO_CAS", idx)
OUT["slices"]["failed_then_old_settles_compare_and_seal"] = slice_stats("SINK_COMPARE_AND_SEAL", idx)

# Persisting the read does not freeze the external authority domain.
idx = select(lambda s: s["stage"] != "NONE" and s["cas"] == "CONFIRMED_APPLIED")
OUT["slices"]["read_once_transitioned"] = slice_stats("READ_THEN_REPO_CAS", idx)
OUT["slices"]["durable_witness_transitioned"] = slice_stats("DURABLE_V3_WITNESS_REPO_CAS", idx)

# Ambiguous repository CAS is separately made idempotent by stable applied_transition_id.
idx = select(lambda s: s["cas"] in ("AMBIG_APPLIED", "AMBIG_NOT_APPLIED") and s["repeat"] == "YES")
OUT["slices"]["stable_repo_transition_id_ambiguous_repeat"] = {
    "n": len(idx),
    "max_repository_writes": max(DETAIL["SINK_COMPARE_AND_SEAL"][i]["repo_writes"] for i in idx),
    "duplicate_repository_transition": sum(DETAIL["SINK_COMPARE_AND_SEAL"][i]["repo_writes"] > 1 for i in idx),
}

OUT["interpretation"] = {
    "scope": "Synthetic finite mechanism lattice; counts are not production failure rates.",
    "strong_rule": "A current read or compare is only a point-in-time fact. Cross-authority terminal publication is safe only if the sink returns an absorbing finality token or a protected compare-and-seal operation atomically prevents later invalidating resource transitions; repository CAS/idempotency solves only the repository side.",
    "protected_boundary": "The external sink/status authority must either expose absorbing finality semantics or perform a conditional seal/finalization of the exact effect-vector version before repository terminal publication. A CLEAN repository writer cannot synthesize that cross-authority atomicity from an earlier read, ETag/resourceVersion compare, or durable local witness.",
}

print(json.dumps(OUT, indent=2, sort_keys=True))
