#!/usr/bin/env python3
"""Finite synthetic stress model for anti-rollback/key-rotation/multi-path repair authority.

Equal-weight mechanism lattice, not an incident-rate model.
"""
from itertools import product, combinations
from collections import Counter
import json

PATHS = ["queue", "direct_api", "retry_worker", "restore_archive"]
PATH_PAIRS = list(combinations(PATHS, 2))
FINALITIES = ["FINAL", "PENDING"]
KEY_STATES = ["OLD_TRUSTED", "OLD_REVOKED", "TRUST_ROLLBACK"]
ANCHOR_STATES = ["CURRENT", "STALE_REPLICA", "LOST", "RECOVERED_FROM_QUORUM"]
UPDATE_STATES = ["CONFIRMED_APPLIED", "AMBIGUOUS_APPLIED", "AMBIGUOUS_NOT_APPLIED"]
RESTORED_CERTS = ["CURRENT", "SUPERSEDED"]
GEN_ADVANCES = [False, True]
DEDUPES = ["VALID", "EXPIRED"]
TRANSPORT_STATES = ["AVAILABLE", "RATE_LIMITED"]

POLICIES = [
    "permanent_tombstone",
    "signed_certificate_only",
    "single_anchor_min",
    "quorum_version_floor_only",
    "quorum_floor_coupled",
    "append_only_version_witness",
    "repo_single_object_cas",
    "safe_archive_external",
    "premature_repo_retire",
]

def scenarios():
    for (finality, pair, key_state, anchor_state, update_state,
         restored_cert, gen_advanced, dedupe, transport_state) in product(
             FINALITIES, PATH_PAIRS, KEY_STATES, ANCHOR_STATES, UPDATE_STATES,
             RESTORED_CERTS, GEN_ADVANCES, DEDUPES, TRANSPORT_STATES):
        current_v = 4 if gen_advanced else 3
        prev_v = current_v - 1
        cert_v = current_v if restored_cert == "CURRENT" else prev_v
        cert_sig_valid = (
            restored_cert == "CURRENT"
            or key_state in ("OLD_TRUSTED", "TRUST_ROLLBACK")
        )
        actual_floor = (
            current_v
            if update_state in ("CONFIRMED_APPLIED", "AMBIGUOUS_APPLIED")
            else prev_v
        )
        if anchor_state == "CURRENT":
            local_floor = actual_floor
        elif anchor_state == "STALE_REPLICA":
            local_floor = prev_v
        elif anchor_state == "LOST":
            local_floor = None
        else:
            local_floor = actual_floor
        yield {
            "finality": finality,
            "pair": pair,
            "key_state": key_state,
            "anchor_state": anchor_state,
            "update_state": update_state,
            "restored_cert": restored_cert,
            "gen_advanced": gen_advanced,
            "dedupe": dedupe,
            "transport_state": transport_state,
            "current_v": current_v,
            "prev_v": prev_v,
            "cert_v": cert_v,
            "cert_min": cert_v,
            "cert_sig_valid": cert_sig_valid,
            "actual_floor": actual_floor,
            "local_floor": local_floor,
        }

def quorum_available(s):
    return s["anchor_state"] != "LOST"

def witness_version(s):
    if s["anchor_state"] == "LOST":
        return None
    if s["anchor_state"] == "STALE_REPLICA":
        return s["prev_v"]
    return s["actual_floor"]

def finish(s, accept_requests, current_allowed, compact, durable_dedupe=False,
           recovery_reads=0):
    final = s["finality"] == "FINAL"
    if accept_requests == 0:
        effect_count = 0
    elif durable_dedupe or s["dedupe"] == "VALID":
        effect_count = 1
    else:
        effect_count = accept_requests
    unsafe_old = final and effect_count > 0
    return {
        "unsafe_old": unsafe_old,
        "duplicate": effect_count > 1,
        "false_pending_block": (not final) and effect_count == 0,
        "current_block": not current_allowed,
        "old_cert_replay": (
            unsafe_old
            and s["restored_cert"] == "SUPERSEDED"
            and s["cert_sig_valid"]
        ),
        "rollback_aba": unsafe_old and s["anchor_state"] == "STALE_REPLICA",
        "compact": compact,
        "safe_compaction": final and compact and not unsafe_old,
        "effect_count": effect_count,
        "recovery_reads": recovery_reads,
        "rate_limit_checkpoint": False,
    }

def evaluate(policy, s):
    # Scheduled-Chat repository transport interruption: fail closed, checkpoint,
    # and retry on a later invocation. No authority decision/effect is inferred.
    if s["transport_state"] == "RATE_LIMITED":
        return {
            "unsafe_old": False,
            "duplicate": False,
            "false_pending_block": False,
            "current_block": True,
            "old_cert_replay": False,
            "rollback_aba": False,
            "compact": False,
            "safe_compaction": False,
            "effect_count": 0,
            "recovery_reads": 0,
            "rate_limit_checkpoint": True,
        }

    final = s["finality"] == "FINAL"

    if policy == "permanent_tombstone":
        return finish(
            s, 0 if final else 2, True, False,
            durable_dedupe=True
        )

    if policy == "signed_certificate_only":
        if final:
            accept = (
                2 if s["cert_sig_valid"] and s["cert_min"] <= s["prev_v"]
                else 0
            )
            return finish(
                s, accept, s["restored_cert"] == "CURRENT", True
            )
        return finish(s, 2, s["restored_cert"] == "CURRENT", False)

    if policy == "single_anchor_min":
        floor = s["local_floor"]
        reads = 1 if s["anchor_state"] in (
            "STALE_REPLICA", "LOST", "RECOVERED_FROM_QUORUM"
        ) else 0
        if final:
            if floor is None:
                return finish(s, 0, False, False, recovery_reads=reads)
            return finish(
                s, 2 if s["prev_v"] >= floor else 0,
                True, True, recovery_reads=reads
            )
        return finish(s, 2, floor is not None, False, recovery_reads=reads)

    if policy == "quorum_version_floor_only":
        if final:
            if not quorum_available(s):
                return finish(s, 0, False, False, recovery_reads=1)
            return finish(
                s,
                2 if s["prev_v"] >= s["actual_floor"] else 0,
                True, True, recovery_reads=1
            )
        return finish(s, 2, quorum_available(s), False, recovery_reads=1)

    if policy == "quorum_floor_coupled":
        if final:
            if not quorum_available(s) or s["actual_floor"] != s["current_v"]:
                return finish(s, 0, False, False, recovery_reads=1)
            return finish(s, 0, True, True, recovery_reads=1)
        return finish(
            s, 2, True, False, durable_dedupe=True, recovery_reads=1
        )

    if policy == "append_only_version_witness":
        wv = witness_version(s)
        if final:
            if wv is None:
                return finish(s, 0, False, False, recovery_reads=1)
            accept = (
                2 if (
                    s["cert_sig_valid"]
                    and s["cert_v"] >= wv
                    and s["cert_min"] <= s["prev_v"]
                ) else 0
            )
            current_allowed = (
                s["restored_cert"] == "CURRENT" and s["cert_v"] >= wv
            )
            return finish(
                s, accept, current_allowed, True, recovery_reads=1
            )
        return finish(
            s, 2,
            wv is not None
            and s["restored_cert"] == "CURRENT"
            and s["cert_v"] >= wv,
            False, durable_dedupe=True, recovery_reads=1
        )

    if policy == "repo_single_object_cas":
        # The one repository authority object co-locates current_generation,
        # retirement floor, certificate/key epoch and applied transition ID.
        # An ambiguous response is reconciled by rereading that same object.
        if final:
            if s["update_state"] in (
                "CONFIRMED_APPLIED", "AMBIGUOUS_APPLIED"
            ):
                return finish(
                    s, 0, True, True,
                    durable_dedupe=True,
                    recovery_reads=(
                        1 if s["update_state"].startswith("AMBIGUOUS") else 0
                    )
                )
            # Readback proves the transition did not apply: keep tombstone and
            # fail closed for new current effects until a later CAS succeeds.
            return finish(
                s, 0, False, False,
                durable_dedupe=True, recovery_reads=1
            )
        return finish(s, 2, True, False, durable_dedupe=True)

    if policy == "safe_archive_external":
        # Strong semantic baseline that uses an independent quorum authority
        # plus current certificate. It is intentionally NOT Phase-1 acceptable
        # if that quorum is external hosted coordination.
        if final:
            if not quorum_available(s) or s["actual_floor"] != s["current_v"]:
                return finish(s, 0, False, False, recovery_reads=2)
            return finish(
                s, 0, s["restored_cert"] == "CURRENT", True,
                recovery_reads=2
            )
        return finish(
            s, 2, True, False, durable_dedupe=True, recovery_reads=2
        )

    if policy == "premature_repo_retire":
        # Negative control: install the coupled floor even while repair pending.
        if s["update_state"] in (
            "CONFIRMED_APPLIED", "AMBIGUOUS_APPLIED"
        ):
            return finish(
                s, 0, True, True,
                recovery_reads=(
                    1 if s["update_state"].startswith("AMBIGUOUS") else 0
                )
            )
        return finish(s, 0, False, False, recovery_reads=1)

    raise ValueError(policy)

def aggregate(rows, policies):
    out = {}
    for p in policies:
        c = Counter()
        for s in rows:
            r = evaluate(p, s)
            for k, v in r.items():
                if isinstance(v, bool):
                    c[k] += int(v)
                elif k == "recovery_reads":
                    c[k] += v
        out[p] = dict(c)
    return out

def main():
    rows = list(scenarios())
    available = [s for s in rows if s["transport_state"] == "AVAILABLE"]
    rate_limited = [s for s in rows if s["transport_state"] == "RATE_LIMITED"]

    result = {
        "schema_version": 1,
        "scenario_count": len(rows),
        "available_scenario_count": len(available),
        "rate_limited_scenario_count": len(rate_limited),
        "policy_aggregate_all": aggregate(rows, POLICIES),
        "policy_aggregate_available": aggregate(available, POLICIES),
        "targeted_slices": {},
        "phase1_acceptance": {
            "repo_single_object_cas": {
                "residual_richer_mode_or_user_execution": False,
                "external_hosted_coordination": False,
                "finite_monthly_trial_paid_quota_dependency": False,
                "incremental_monetary_cost": 0,
                "repository_transport_only": True,
                "rate_limit_behavior": "fail_closed_checkpoint_retry",
                "scope_limit": (
                    "authority object must be outside modeled application "
                    "restore domain; repository-wide history/ref rollback is "
                    "not solved by this leaf"
                ),
            },
            "quorum_floor_coupled": {
                "semantic_safety_in_model": True,
                "phase1_accepted": False,
                "reason": "requires independent hosted/distributed coordination in this comparison",
            },
            "safe_archive_external": {
                "semantic_safety_in_model": True,
                "phase1_accepted": False,
                "reason": "requires independent hosted/distributed coordination in this comparison",
            },
        },
    }

    def slice_count(pred, policy, metric):
        return sum(
            int(evaluate(policy, s)[metric])
            for s in available if pred(s)
        )

    floor_missing = lambda s: (
        s["finality"] == "FINAL"
        and s["update_state"] == "AMBIGUOUS_NOT_APPLIED"
        and s["anchor_state"] != "LOST"
    )
    old_cert_valid = lambda s: (
        s["finality"] == "FINAL"
        and s["restored_cert"] == "SUPERSEDED"
        and s["key_state"] in ("OLD_TRUSTED", "TRUST_ROLLBACK")
    )
    pending = lambda s: s["finality"] == "PENDING"

    result["targeted_slices"]["quorum_floor_missing_update"] = {
        "scenario_count": sum(1 for s in available if floor_missing(s)),
        "quorum_version_floor_only_unsafe": slice_count(
            floor_missing, "quorum_version_floor_only", "unsafe_old"
        ),
        "quorum_floor_coupled_unsafe": slice_count(
            floor_missing, "quorum_floor_coupled", "unsafe_old"
        ),
        "repo_single_object_cas_unsafe": slice_count(
            floor_missing, "repo_single_object_cas", "unsafe_old"
        ),
        "repo_single_object_cas_current_block": slice_count(
            floor_missing, "repo_single_object_cas", "current_block"
        ),
    }
    result["targeted_slices"]["valid_superseded_certificate"] = {
        "scenario_count": sum(1 for s in available if old_cert_valid(s)),
        "signed_certificate_only_unsafe": slice_count(
            old_cert_valid, "signed_certificate_only", "unsafe_old"
        ),
        "append_only_version_witness_unsafe": slice_count(
            old_cert_valid, "append_only_version_witness", "unsafe_old"
        ),
        "repo_single_object_cas_unsafe": slice_count(
            old_cert_valid, "repo_single_object_cas", "unsafe_old"
        ),
    }
    result["targeted_slices"]["pending_repair"] = {
        "scenario_count": sum(1 for s in available if pending(s)),
        "premature_repo_retire_false_block": slice_count(
            pending, "premature_repo_retire", "false_pending_block"
        ),
        "repo_single_object_cas_false_block": slice_count(
            pending, "repo_single_object_cas", "false_pending_block"
        ),
    }
    result["targeted_slices"]["rate_limit_interruption"] = {
        "scenario_count": len(rate_limited),
        "repo_single_object_cas_unsafe": sum(
            int(evaluate("repo_single_object_cas", s)["unsafe_old"])
            for s in rate_limited
        ),
        "repo_single_object_cas_duplicate": sum(
            int(evaluate("repo_single_object_cas", s)["duplicate"])
            for s in rate_limited
        ),
        "repo_single_object_cas_checkpoint": sum(
            int(evaluate("repo_single_object_cas", s)["rate_limit_checkpoint"])
            for s in rate_limited
        ),
    }

    print(json.dumps(result, indent=2, sort_keys=True))

if __name__ == "__main__":
    main()
