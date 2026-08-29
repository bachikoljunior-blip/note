#!/usr/bin/env python3
"""Phase-1 multi_agent Part 33 finite stress model.

Same-generation abandoned reservation cleanup with phase-scoped timeout,
deterministic task-owned resume, and a single grant-record CAS cancellation fork.
Equal-weight synthetic counts; not production rates. No network required.
"""
from itertools import product
import json

PHASES = ["PREPARED", "GRANTED", "AUTHORIZED"]
RELATIONS = ["same_task", "replacement"]
RACES = ["cancel_first", "authorize_first"]
EFFECT_DOMAINS = ["repo_atomic", "external_nonfenced"]
MECHANISMS = [
    "timeout_all",
    "prepared_only_timeout",
    "separate_cancel_flag",
    "grant_record_cas",
    "parent_generation_only",
    "staging_integrator",
]


def evaluate(mech, phase, relation, late_old, cancel_req, race,
             effect_domain, registry_complete, deterministic_same_id):
    unsafe = progress = blocked = false_block = duplicate = reconcile = stale_old = 0
    replacement = relation == "replacement"

    if not replacement:
        if mech in ("prepared_only_timeout", "grant_record_cas", "parent_generation_only"):
            if deterministic_same_id:
                progress = 1
                reconcile = int(phase == "AUTHORIZED")
            else:
                duplicate = 1
                unsafe = int(phase in ("GRANTED", "AUTHORIZED"))
                progress = int(phase == "PREPARED")
                blocked = int(not progress)
        elif mech == "timeout_all":
            progress = 1
            if late_old and phase in ("GRANTED", "AUTHORIZED"):
                unsafe = duplicate = stale_old = 1
        elif mech == "separate_cancel_flag":
            progress = 1
            if cancel_req and late_old and phase in ("GRANTED", "AUTHORIZED") and effect_domain == "external_nonfenced":
                unsafe = duplicate = 1
        elif mech == "staging_integrator":
            if registry_complete:
                progress = 1
                reconcile = int(phase == "AUTHORIZED")
            else:
                progress = 1
                if phase in ("GRANTED", "AUTHORIZED") and late_old:
                    unsafe = duplicate = 1
        return locals_result(unsafe, progress, blocked, false_block, duplicate, reconcile, stale_old)

    # Replacement task within the same parent generation.
    if mech == "timeout_all":
        progress = 1
        if phase in ("GRANTED", "AUTHORIZED") and late_old:
            unsafe = stale_old = 1

    elif mech == "prepared_only_timeout":
        if phase == "PREPARED":
            progress = 1
        else:
            blocked = 1
            if phase == "GRANTED" and cancel_req:
                false_block = 1
            if phase == "AUTHORIZED":
                reconcile = 1

    elif mech == "separate_cancel_flag":
        if phase == "PREPARED":
            progress = 1
        elif phase == "GRANTED":
            if cancel_req:
                progress = 1
                if late_old:
                    unsafe = stale_old = 1
            else:
                blocked = 1
        else:  # AUTHORIZED
            if cancel_req:
                progress = 1
                unsafe = 1  # authorization is already irreversible
                stale_old = int(late_old)
            else:
                blocked = reconcile = 1

    elif mech == "grant_record_cas":
        if phase == "PREPARED":
            # No authority exists yet; prepared-cell cleanup can be lease/time based.
            progress = 1
        elif phase == "GRANTED":
            if cancel_req:
                # CANCELLED and AUTHORIZED are competing transitions from the same
                # GRANTED record. Exactly one CAS branch may win.
                if race == "cancel_first":
                    progress = 1
                else:
                    blocked = reconcile = 1
            else:
                blocked = 1
        else:  # AUTHORIZED
            blocked = reconcile = 1

    elif mech == "parent_generation_only":
        # Safe, but same-generation replacement cannot reclaim anything.
        blocked = 1
        if phase == "PREPARED":
            false_block = 1
        if phase == "GRANTED" and cancel_req:
            false_block = 1
        if phase == "AUTHORIZED":
            reconcile = 1

    elif mech == "staging_integrator":
        if not registry_complete:
            progress = 1
            if phase in ("GRANTED", "AUTHORIZED"):
                unsafe = 1
                stale_old = int(late_old)
        else:
            if phase == "PREPARED":
                progress = 1
            elif phase == "GRANTED":
                if cancel_req:
                    progress = 1
                else:
                    blocked = 1
            else:
                blocked = reconcile = 1

    return locals_result(unsafe, progress, blocked, false_block, duplicate, reconcile, stale_old)


def locals_result(unsafe, progress, blocked, false_block, duplicate, reconcile, stale_old):
    return {
        "unsafe": unsafe,
        "progress": progress,
        "blocked": blocked,
        "false_block": false_block,
        "duplicate": duplicate,
        "reconcile": reconcile,
        "stale_old": stale_old,
    }


def build_concurrency_rows():
    rows = []
    for vals in product(
        PHASES, RELATIONS, [False, True], [False, True], RACES,
        EFFECT_DOMAINS, [False, True], [False, True]
    ):
        phase, relation, late_old, cancel_req, race, effect_domain, registry_complete, deterministic_same_id = vals
        for mech in MECHANISMS:
            rows.append({
                "phase": phase,
                "relation": relation,
                "late_old": late_old,
                "cancel_req": cancel_req,
                "race": race,
                "effect_domain": effect_domain,
                "registry_complete": registry_complete,
                "deterministic_same_id": deterministic_same_id,
                "mech": mech,
                **evaluate(mech, *vals),
            })
    return rows


def build_recovery_rows():
    statuses = ["PREPARED", "GRANTED", "AUTHORIZED"]
    interruptions = ["none", "response_loss_transition", "rate_limit", "crash"]
    rows = []
    for status, interruption, durable_record, deterministic_res_id, durable_effect_id, domain in product(
        statuses, interruptions, [False, True], [False, True], [False, True], EFFECT_DOMAINS
    ):
        resumable = orphan = duplicate = fail_closed = checkpoint = unresolved_external = 0
        if interruption == "rate_limit":
            checkpoint = 1
        if not durable_record:
            if status in ("GRANTED", "AUTHORIZED") or interruption != "none":
                orphan = 1
        else:
            if status in ("PREPARED", "GRANTED"):
                if deterministic_res_id:
                    resumable = 1
                else:
                    duplicate = 1
            else:  # AUTHORIZED
                if domain == "repo_atomic":
                    resumable = 1
                else:
                    fail_closed = unresolved_external = 1
                    if not durable_effect_id:
                        duplicate = 1
        rows.append({
            "status": status,
            "interruption": interruption,
            "durable_record": durable_record,
            "deterministic_res_id": deterministic_res_id,
            "durable_effect_id": durable_effect_id,
            "domain": domain,
            "resumable": resumable,
            "orphan": orphan,
            "duplicate": duplicate,
            "fail_closed": fail_closed,
            "checkpoint": checkpoint,
            "unresolved_external": unresolved_external,
        })
    return rows


def aggregate(rows):
    out = {}
    for mech in MECHANISMS:
        x = [r for r in rows if r["mech"] == mech]
        out[mech] = {"n": len(x)}
        for k in ["unsafe", "progress", "blocked", "false_block", "duplicate", "reconcile", "stale_old"]:
            out[mech][k] = sum(r[k] for r in x)
    return out


def main():
    c = build_concurrency_rows()
    r = build_recovery_rows()
    common = [x for x in c if x["registry_complete"] and x["deterministic_same_id"]]
    print(json.dumps({
        "concurrency_scenario_count": len(c) // len(MECHANISMS),
        "concurrency_strategy_evaluations": len(c),
        "recovery_scenario_count": len(r),
        "common_strong_slice": aggregate(common),
        "note": "Equal-weight finite synthetic mechanism counts; not production rates."
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
