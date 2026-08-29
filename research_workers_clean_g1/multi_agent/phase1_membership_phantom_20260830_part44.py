#!/usr/bin/env python3
from itertools import product
import json

N=[1,3,11]
CHG=["none","add","remove","readd","rename","migrate"]
TIM=["before_request","after_request_before_scan","after_scan_before_publish"]
OVER=[0,1]
STALE=[0,1]
MRL=[0,1]
SRL=[0,1]
RATE=["none","membership_write","slot_create"]
CTRL=[0,1]
STRATS=[
    "fixed_slot_snapshot_no_membership_epoch",
    "append_registry_snapshot",
    "separate_membership_epoch_recheck",
    "co_located_membership_ticket",
    "global_root_every_admission",
]

def evaluate(sc, st):
    n,chg,timing,overlap,stale,mrl,srl,rate,ctrl=sc
    new_like=chg in {"add","readd","rename","migrate"}
    remove_like=chg in {"remove","rename","migrate"}
    after_request=timing!="before_request"
    after_scan=timing=="after_scan_before_publish"
    mw=rate!="membership_write"
    sw=rate!="slot_create"
    change_effective=(chg!="none" and mw) or bool(ctrl)
    local=n*(1+overlap)
    r=dict(
        phantom_role_unsafe=False, stale_membership_publish=False,
        false_exclusion_stale_slot=False, membership_retry=False,
        finite_current_membership_bound=False, finite_progress_proven=False,
        membership_response_loss_ambiguous=False,
        slot_response_loss_ambiguous=False,
        global_hotspot_touches=0, membership_root_writes=0,
        local_slot_writes=0, zero_global_write_per_local_admission=True,
        rate_limit_fail_closed=False, control_advance_fenced=False,
    )
    if st=="fixed_slot_snapshot_no_membership_epoch":
        r.update(
            finite_current_membership_bound=True,
            finite_progress_proven=bool(not after_request and not ctrl),
            phantom_role_unsafe=bool(new_like and after_request and mw and sw),
            stale_membership_publish=bool(ctrl or (chg!="none" and after_request and mw)),
            false_exclusion_stale_slot=bool(remove_like and stale and after_request and mw),
            membership_response_loss_ambiguous=bool(mrl and chg!="none" and mw),
            slot_response_loss_ambiguous=bool(srl and new_like and sw),
            local_slot_writes=local, rate_limit_fail_closed=rate!="none")
    elif st=="append_registry_snapshot":
        r.update(
            finite_current_membership_bound=True,
            finite_progress_proven=bool(not after_scan and not ctrl),
            phantom_role_unsafe=bool(new_like and after_scan and mw and sw),
            stale_membership_publish=bool(ctrl or (chg!="none" and after_scan and mw)),
            false_exclusion_stale_slot=bool(remove_like and stale and after_scan and mw),
            membership_response_loss_ambiguous=bool(mrl and chg!="none" and mw),
            slot_response_loss_ambiguous=bool(srl and new_like and sw and chg in {"readd","rename","migrate"}),
            local_slot_writes=local, rate_limit_fail_closed=rate!="none")
    elif st=="separate_membership_epoch_recheck":
        retry=bool(change_effective and after_request)
        r.update(
            finite_current_membership_bound=True,
            membership_retry=retry, finite_progress_proven=not retry,
            control_advance_fenced=bool(ctrl),
            membership_root_writes=(1 if chg!="none" and mw else 0),
            local_slot_writes=local, rate_limit_fail_closed=rate!="none")
    elif st=="co_located_membership_ticket":
        r.update(
            finite_current_membership_bound=True, finite_progress_proven=True,
            control_advance_fenced=bool(ctrl),
            membership_root_writes=1+(1 if chg!="none" and timing=="before_request" and mw else 0),
            local_slot_writes=local, rate_limit_fail_closed=rate!="none")
    elif st=="global_root_every_admission":
        r.update(
            finite_current_membership_bound=True, finite_progress_proven=True,
            control_advance_fenced=bool(ctrl),
            zero_global_write_per_local_admission=False,
            global_hotspot_touches=local+1+(1 if chg!="none" and mw else 0),
            rate_limit_fail_closed=rate!="none")
    return r

def main():
    scenarios=list(product(N,CHG,TIM,OVER,STALE,MRL,SRL,RATE,CTRL))
    rows=[(sc,st,evaluate(sc,st)) for sc in scenarios for st in STRATS]
    out={}
    bool_keys=[
        "phantom_role_unsafe","stale_membership_publish","false_exclusion_stale_slot",
        "membership_retry","finite_current_membership_bound","finite_progress_proven",
        "membership_response_loss_ambiguous","slot_response_loss_ambiguous",
        "rate_limit_fail_closed","control_advance_fenced"]
    for st in STRATS:
        rs=[r for sc,s,r in rows if s==st]
        a={k:sum(int(r[k]) for r in rs) for k in bool_keys}
        a.update(
            scenario_count=len(rs),
            global_hotspot_touches=sum(r["global_hotspot_touches"] for r in rs),
            membership_root_writes=sum(r["membership_root_writes"] for r in rs),
            local_slot_writes=sum(r["local_slot_writes"] for r in rs))
        out[st]=a
    print(json.dumps({"scenario_count":len(scenarios),"strategy_evaluations":len(rows),"aggregates":out},indent=2,sort_keys=True))

if __name__=="__main__":
    main()
