#!/usr/bin/env python3
from itertools import product
import json

ROLES=[1,3,11]
OVERLAP=[1,2,3]
REPLAY=[0,1]
CRASH=[0,1]
TAKEOVER=[0,1]
LATE=[0,1]
RECREATE=[0,1]
RATE=["none","before_admit","after_admit_response_loss"]
SCAN=["scan_before_slip","scan_after_slip"]
STRATEGIES=[
    "scheduler_role_count_only",
    "dynamic_prepared_scan",
    "fixed_role_slot_name_only",
    "fixed_role_slot_incarnation",
    "fixed_role_slot_queue2_incarnation",
    "global_root_counter",
]

def evaluate(sc, st):
    R,O,replay,crash,takeover,late,recreate,rate,scan=sc
    attempts_per_role=O+replay
    total_attempts=R*attempts_per_role
    can_admit=rate!="before_admit"
    slip_distinct=(R*O if can_admit and scan=="scan_before_slip" else 0)
    out=dict(
        finite_bound_proven=False, structural_bound=None,
        actual_authoritative=0, bound_violation=False,
        duplicate_logical_admission=False, stale_release_unsafe=False,
        response_loss_ambiguous=False, wide_terminal=False,
        false_exclusion=False, unseen_post_ticket_admissions=0,
        global_hotspot_touches=0, local_slot_touches=0,
        zero_global_write_bound=False, rate_limit_fail_closed=False,
    )
    if st=="scheduler_role_count_only":
        actual=(R*O + (R if replay else 0)) if can_admit else 0
        out.update(
            actual_authoritative=actual, structural_bound=R,
            bound_violation=actual>R,
            duplicate_logical_admission=bool(replay and can_admit),
            response_loss_ambiguous=bool(rate=="after_admit_response_loss" and can_admit),
            unseen_post_ticket_admissions=(slip_distinct + (R if replay and can_admit and scan=="scan_before_slip" else 0)),
            zero_global_write_bound=True,
            wide_terminal=not crash,
            rate_limit_fail_closed=rate=="before_admit",
        )
    elif st=="dynamic_prepared_scan":
        out.update(
            actual_authoritative=(R*O if can_admit else 0),
            unseen_post_ticket_admissions=slip_distinct,
            zero_global_write_bound=True,
            rate_limit_fail_closed=rate=="before_admit",
            wide_terminal=bool((not crash or takeover) and scan=="scan_after_slip"),
            false_exclusion=bool(crash and not takeover),
        )
    elif st=="fixed_role_slot_name_only":
        out.update(
            actual_authoritative=(R if can_admit else 0),
            finite_bound_proven=True, structural_bound=R,
            unseen_post_ticket_admissions=(R if can_admit and scan=="scan_before_slip" else 0),
            local_slot_touches=(total_attempts if can_admit else 0),
            zero_global_write_bound=True,
            rate_limit_fail_closed=rate=="before_admit",
            false_exclusion=bool(crash and not takeover),
            stale_release_unsafe=bool(crash and takeover and late and recreate and can_admit),
        )
        out["wide_terminal"]=bool((not crash or takeover) and not out["stale_release_unsafe"])
    elif st=="fixed_role_slot_incarnation":
        out.update(
            actual_authoritative=(R if can_admit else 0),
            finite_bound_proven=True, structural_bound=R,
            unseen_post_ticket_admissions=(R if can_admit and scan=="scan_before_slip" else 0),
            local_slot_touches=(total_attempts if can_admit else 0),
            zero_global_write_bound=True,
            rate_limit_fail_closed=rate=="before_admit",
            false_exclusion=bool(crash and not takeover),
            wide_terminal=bool(not crash or takeover),
        )
    elif st=="fixed_role_slot_queue2_incarnation":
        out.update(
            actual_authoritative=(R if can_admit else 0),
            finite_bound_proven=True, structural_bound=R,
            unseen_post_ticket_admissions=(R if can_admit and scan=="scan_before_slip" else 0),
            local_slot_touches=(min(attempts_per_role,2)*R if can_admit else 0),
            zero_global_write_bound=True,
            rate_limit_fail_closed=rate=="before_admit",
            false_exclusion=bool(crash and not takeover),
            wide_terminal=bool(not crash or takeover),
        )
        out["queue_overflow_fail_closed"]=bool(can_admit and attempts_per_role>2)
    elif st=="global_root_counter":
        out.update(
            actual_authoritative=(min(R,R*O) if can_admit else 0),
            finite_bound_proven=True, structural_bound=R,
            unseen_post_ticket_admissions=0,
            global_hotspot_touches=total_attempts+1+(R if crash and takeover else 0),
            zero_global_write_bound=False,
            rate_limit_fail_closed=rate=="before_admit",
            false_exclusion=bool(crash and not takeover),
            wide_terminal=bool(not crash or takeover),
        )
    return out

def main():
    scenarios=list(product(ROLES,OVERLAP,REPLAY,CRASH,TAKEOVER,LATE,RECREATE,RATE,SCAN))
    rows=[(sc,st,evaluate(sc,st)) for sc in scenarios for st in STRATEGIES]
    aggregates={}
    for st in STRATEGIES:
        rs=[r for sc,s,r in rows if s==st]
        aggregates[st]={
            "scenario_count": len(rs),
            "finite_bound_proven": sum(r["finite_bound_proven"] for r in rs),
            "bound_violation": sum(r["bound_violation"] for r in rs),
            "duplicate_logical_admission": sum(r["duplicate_logical_admission"] for r in rs),
            "stale_release_unsafe": sum(r["stale_release_unsafe"] for r in rs),
            "response_loss_ambiguous": sum(r["response_loss_ambiguous"] for r in rs),
            "wide_terminal": sum(r["wide_terminal"] for r in rs),
            "false_exclusion": sum(r["false_exclusion"] for r in rs),
            "total_unseen_post_ticket_admissions": sum(r["unseen_post_ticket_admissions"] for r in rs),
            "max_unseen_post_ticket_admissions": max(r["unseen_post_ticket_admissions"] for r in rs),
            "global_hotspot_touches": sum(r["global_hotspot_touches"] for r in rs),
            "local_slot_touches": sum(r["local_slot_touches"] for r in rs),
            "rate_limit_fail_closed": sum(r["rate_limit_fail_closed"] for r in rs),
        }

    def slice_count(st, sc_pred, r_pred):
        subset=[r for sc,s,r in rows if s==st and sc_pred(sc)]
        return sum(r_pred(r) for r in subset),len(subset)

    targeted={
        "role_count_overlap_bound": slice_count(
            "scheduler_role_count_only",
            lambda sc: sc[1]>1 and sc[7]!="before_admit",
            lambda r:r["bound_violation"]),
        "role_count_replay_duplicate": slice_count(
            "scheduler_role_count_only",
            lambda sc: sc[2]==1 and sc[7]!="before_admit",
            lambda r:r["duplicate_logical_admission"]),
        "name_slot_aba": slice_count(
            "fixed_role_slot_name_only",
            lambda sc: sc[3] and sc[4] and sc[5] and sc[6] and sc[7]!="before_admit",
            lambda r:r["stale_release_unsafe"]),
        "incarnation_slot_scan_before_slip": slice_count(
            "fixed_role_slot_incarnation",
            lambda sc: sc[8]=="scan_before_slip" and sc[7]!="before_admit",
            lambda r:r["unseen_post_ticket_admissions"]<=r["structural_bound"]),
        "dynamic_scan_before_slip": slice_count(
            "dynamic_prepared_scan",
            lambda sc: sc[8]=="scan_before_slip" and sc[7]!="before_admit",
            lambda r:r["unseen_post_ticket_admissions"]>0),
    }
    print(json.dumps({
        "scenario_count":len(scenarios),
        "strategy_evaluations":len(rows),
        "aggregates":aggregates,
        "targeted_slices":targeted,
    },indent=2,sort_keys=True))

if __name__=="__main__":
    main()
