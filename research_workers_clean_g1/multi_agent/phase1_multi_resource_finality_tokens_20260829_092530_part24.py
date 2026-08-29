#!/usr/bin/env python3
from itertools import product
import json

RES = ("R1", "R2")
EVENTS = ["NONE"] + [f"{r}_{kind}" for r in RES for kind in ("FLIP", "REVOKE", "EXPIRE")]
AXES = {
    "r1_initial": ["SETTLED", "FAILED"],
    "r2_initial": ["SETTLED", "FAILED"],
    "mid_event": EVENTS,
    "post_event": EVENTS,
    "order": ["R1_FIRST", "R2_FIRST"],
    "absorbing_available": ["NO", "YES"],
    "verifier": ["AVAILABLE", "OUTAGE"],
    "takeover": ["NO", "YES"],
    "cas": ["CONFIRMED_APPLIED", "AMBIG_APPLIED", "AMBIG_NOT_APPLIED"],
    "repeat": ["NO", "YES"],
}
SCENARIOS = [dict(zip(AXES, vals)) for vals in product(*AXES.values())]


def new_state(sc):
    return {
        r: {
            "status": sc[f"{r.lower()}_initial"],
            "version": 1,
            "replacement": 0,
            "token_version": None,
            "token_valid": False,
            "sealed": False,
        }
        for r in RES
    }


def amount(x):
    return (30 if x["status"] == "SETTLED" else 0) + 30 * x["replacement"]


def apply_event(state, event):
    if event == "NONE":
        return
    r, kind = event.split("_")
    x = state[r]
    if x["sealed"]:
        # Absorbing/sealed finality rejects later invalidation/revocation in this model.
        return
    if kind == "FLIP":
        x["status"] = "FAILED" if x["status"] == "SETTLED" else "SETTLED"
        x["version"] += 1
        if x["token_version"] is not None:
            x["token_valid"] = False
    elif kind in ("REVOKE", "EXPIRE"):
        if x["token_version"] is not None:
            x["token_valid"] = False
    else:
        raise ValueError(kind)


def ensure_exact_current(x, sc):
    current = amount(x)
    if current == 30:
        return True
    if current > 30:
        return False
    if sc["verifier"] != "AVAILABLE":
        return False
    x["replacement"] += 1
    return True


def issue_token(x, absorbing=False):
    x["token_version"] = x["version"]
    x["token_valid"] = True
    if absorbing:
        x["sealed"] = True


def exact_amount_vector(state):
    return all(amount(state[r]) == 30 for r in RES)


def all_tokens_current(state):
    return all(
        state[r]["token_valid"] and state[r]["token_version"] == state[r]["version"]
        for r in RES
    )


def repository_terminal(decide, safe, sc):
    # Stable applied_transition_id: ambiguous repository CAS is read/reconciled before retry.
    if not decide:
        return {"terminal": False, "unsafe_terminal": False, "repo_writes": 0}
    if sc["cas"] in ("CONFIRMED_APPLIED", "AMBIG_APPLIED"):
        return {"terminal": True, "unsafe_terminal": not safe, "repo_writes": 1}
    if sc["repeat"] == "YES":
        return {"terminal": True, "unsafe_terminal": not safe, "repo_writes": 1}
    return {"terminal": False, "unsafe_terminal": False, "repo_writes": 0}


def finish(state, decide, sc, protected_ops=0):
    exact = exact_amount_vector(state)
    valid = all_tokens_current(state)
    out = repository_terminal(decide, exact and valid, sc)
    out.update({
        "exact_amount": exact,
        "tokens_valid": valid,
        "duplicate_replacement": any(state[r]["replacement"] > 1 for r in RES),
        "protected_ops": protected_ops,
    })
    return out


def acquire_revocable(state, r, sc):
    x = state[r]
    if not ensure_exact_current(x, sc):
        return False
    issue_token(x, absorbing=False)
    return True


def sequential_revocable(sc):
    state = new_state(sc)
    order = RES if sc["order"] == "R1_FIRST" else tuple(reversed(RES))
    if not acquire_revocable(state, order[0], sc):
        return finish(state, False, sc)
    apply_event(state, sc["mid_event"])
    if not acquire_revocable(state, order[1], sc):
        return finish(state, False, sc)
    apply_event(state, sc["post_event"])
    return finish(state, True, sc)


def recheck_all_then_repo(sc):
    state = new_state(sc)
    order = RES if sc["order"] == "R1_FIRST" else tuple(reversed(RES))
    if not acquire_revocable(state, order[0], sc):
        return finish(state, False, sc)
    apply_event(state, sc["mid_event"])
    if not acquire_revocable(state, order[1], sc):
        return finish(state, False, sc)

    # Refresh both current tokens immediately before repository publication.
    for r in RES:
        if not ensure_exact_current(state[r], sc):
            return finish(state, False, sc, protected_ops=1)
        issue_token(state[r], absorbing=False)
    apply_event(state, sc["post_event"])
    return finish(state, True, sc, protected_ops=1)


def seal_one(state, r, sc):
    if not ensure_exact_current(state[r], sc):
        return False
    issue_token(state[r], absorbing=True)
    return True


def per_resource_seal(sc, require_existing_absorbing=False):
    state = new_state(sc)
    if require_existing_absorbing and sc["absorbing_available"] != "YES":
        return finish(state, False, sc)
    order = RES if sc["order"] == "R1_FIRST" else tuple(reversed(RES))
    if not seal_one(state, order[0], sc):
        return finish(state, False, sc, protected_ops=1)
    apply_event(state, sc["mid_event"])
    if not seal_one(state, order[1], sc):
        return finish(state, False, sc, protected_ops=2)
    apply_event(state, sc["post_event"])
    return finish(state, True, sc, protected_ops=2)


def vector_atomic_seal(sc):
    state = new_state(sc)
    # The mid event happens before one vector-level atomic finalization.
    apply_event(state, sc["mid_event"])
    missing = []
    for r in RES:
        current = amount(state[r])
        if current > 30:
            return finish(state, False, sc, protected_ops=1)
        if current == 0:
            missing.append(r)
    if missing and sc["verifier"] != "AVAILABLE":
        return finish(state, False, sc, protected_ops=1)
    for r in missing:
        state[r]["replacement"] += 1
    for r in RES:
        issue_token(state[r], absorbing=True)
    apply_event(state, sc["post_event"])
    return finish(state, True, sc, protected_ops=1)


DETAIL = {
    "SEQUENTIAL_REVOCABLE_TOKENS": [sequential_revocable(s) for s in SCENARIOS],
    "RECHECK_ALL_THEN_REPO": [recheck_all_then_repo(s) for s in SCENARIOS],
    "PER_RESOURCE_COMPARE_AND_SEAL": [per_resource_seal(s, False) for s in SCENARIOS],
    "VECTOR_ATOMIC_SEAL": [vector_atomic_seal(s) for s in SCENARIOS],
    "ABSORBING_PER_RESOURCE_TOKENS": [per_resource_seal(s, True) for s in SCENARIOS],
}


def summarize(rows):
    return {
        "terminal": sum(r["terminal"] for r in rows),
        "unsafe_terminal": sum(r["unsafe_terminal"] for r in rows),
        "safe_terminal": sum(r["terminal"] and not r["unsafe_terminal"] for r in rows),
        "duplicate_replacement": sum(r["duplicate_replacement"] for r in rows),
        "protected_ops_on_terminal": sum(r["protected_ops"] for r in rows if r["terminal"]),
        "duplicate_repository_transition": sum(r["repo_writes"] > 1 for r in rows),
    }


def select(pred):
    return [i for i, s in enumerate(SCENARIOS) if pred(s)]


def slice_stats(policy, idx):
    rows = DETAIL[policy]
    return {
        "n": len(idx),
        "terminal": sum(rows[i]["terminal"] for i in idx),
        "unsafe_terminal": sum(rows[i]["unsafe_terminal"] for i in idx),
        "safe_terminal": sum(rows[i]["terminal"] and not rows[i]["unsafe_terminal"] for i in idx),
    }


OUT = {
    "scenario_count": len(SCENARIOS),
    "policies": {p: summarize(rows) for p, rows in DETAIL.items()},
    "slices": {},
}

# First revocable token disappears before the second token is collected.
idx = select(lambda s:
    s["r1_initial"] == "SETTLED" and s["r2_initial"] == "SETTLED"
    and s["post_event"] == "NONE" and s["cas"] == "CONFIRMED_APPLIED"
    and ((s["order"] == "R1_FIRST" and s["mid_event"] in ("R1_REVOKE", "R1_EXPIRE"))
         or (s["order"] == "R2_FIRST" and s["mid_event"] in ("R2_REVOKE", "R2_EXPIRE"))))
OUT["slices"]["first_token_revoked_sequential"] = slice_stats("SEQUENTIAL_REVOCABLE_TOKENS", idx)
OUT["slices"]["first_token_revoked_recheck"] = slice_stats("RECHECK_ALL_THEN_REPO", idx)
OUT["slices"]["first_token_revoked_per_resource_seal"] = slice_stats("PER_RESOURCE_COMPARE_AND_SEAL", idx)

# Token revocation/expiry after the last recheck is still a TOCTOU unless token semantics are absorbing.
idx = select(lambda s:
    s["r1_initial"] == "SETTLED" and s["r2_initial"] == "SETTLED"
    and s["mid_event"] == "NONE"
    and s["post_event"] in ("R1_REVOKE", "R1_EXPIRE", "R2_REVOKE", "R2_EXPIRE")
    and s["cas"] == "CONFIRMED_APPLIED")
OUT["slices"]["postcheck_token_loss_recheck"] = slice_stats("RECHECK_ALL_THEN_REPO", idx)
OUT["slices"]["postcheck_token_loss_per_resource_seal"] = slice_stats("PER_RESOURCE_COMPARE_AND_SEAL", idx)
OUT["slices"]["postcheck_token_loss_vector_seal"] = slice_stats("VECTOR_ATOMIC_SEAL", idx)

# Resource truth changes after the last recheck.
idx = select(lambda s:
    s["r1_initial"] == "SETTLED" and s["r2_initial"] == "SETTLED"
    and s["mid_event"] == "NONE" and s["post_event"] in ("R1_FLIP", "R2_FLIP")
    and s["verifier"] == "AVAILABLE" and s["cas"] == "CONFIRMED_APPLIED")
OUT["slices"]["postcheck_resource_flip_recheck"] = slice_stats("RECHECK_ALL_THEN_REPO", idx)
OUT["slices"]["postcheck_resource_flip_per_resource_seal"] = slice_stats("PER_RESOURCE_COMPARE_AND_SEAL", idx)

# Existing independently absorbing tokens are safe but deliberately unavailable in half the lattice.
idx = select(lambda s: s["absorbing_available"] == "YES" and s["cas"] == "CONFIRMED_APPLIED")
OUT["slices"]["absorbing_available"] = slice_stats("ABSORBING_PER_RESOURCE_TOKENS", idx)

# Stable repository transition ID separately handles response loss / takeover.
idx = select(lambda s: s["cas"] in ("AMBIG_APPLIED", "AMBIG_NOT_APPLIED") and s["repeat"] == "YES")
OUT["slices"]["ambiguous_repo_cas_repeat"] = {
    "n": len(idx),
    "max_repository_writes": max(DETAIL["VECTOR_ATOMIC_SEAL"][i]["repo_writes"] for i in idx),
    "duplicate_repository_transition": sum(DETAIL["VECTOR_ATOMIC_SEAL"][i]["repo_writes"] > 1 for i in idx),
}

# Liveness micro-control: if one required component is temporarily hot/unsealable, a coarse vector seal
# makes no durable finality progress; independent per-resource seals can finalize the unaffected component.
OUT["hot_component_liveness_microcontrol"] = {
    "cases": 2,
    "per_resource_seal_unaffected_components_durably_finalized": 2,
    "vector_atomic_seal_unaffected_components_durably_finalized": 0,
    "scope": "Two toy cases, one with R1 hot and one with R2 hot; mechanism illustration, not a production contention rate."
}

OUT["interpretation"] = {
    "scope": "Synthetic finite mechanism lattice; unsafe terminal includes invalid/revoked token authority as well as wrong amount truth. Counts are not production failure rates.",
    "strong_rule": "A vector can be assembled sequentially only from component proofs that remain absorbing after issuance. Revocable/current-only component tokens require another current check and still have a post-check race. For decomposable resource invariants, independently absorbing per-resource seals compose safely; a vector-level atomic seal is also safe but is coarser for liveness.",
    "protected_boundary": "The sink/status authority must supply either independently absorbing per-resource finality/seal semantics or a vector-level atomic compare-and-seal. Revocable/expiring current tokens cannot be upgraded to an immutable vector certificate by repository logic alone."
}

print(json.dumps(OUT, indent=2, sort_keys=True))
