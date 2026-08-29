#!/usr/bin/env python3
from itertools import product
import json

ALG=["gset","content_addressed","max_register","escrow_rights","noncommutative"]
DUP=[0,1]
CONFLICT=[0,1]
OWNER=["alive","crash","slow_late"]
GEN=[0,1]
GLOBAL_REDUCE=[0,1]
ALL_COMPLETE=[0,1]
RATE=["none","before_write","after_write_response_loss"]
STRATEGIES=[
    "own_gset_contribution",
    "own_content_addressed_contribution",
    "own_max_candidate",
    "static_escrow_disjoint_rights",
    "deterministic_single_owner",
    "shared_crdt_sink",
    "fenced_shared_sink",
]

def evaluate(sc,st):
    alg,dup,conflict,owner,gen,global_reduce,all_complete,rate=sc
    r=dict(
        supported=False, duplicate_safe=False, concurrent_semantics_safe=False,
        terminal_complete=False, needs_cross_role_reducer=False,
        owner_crash_blocks=False, stale_generation_risk=False,
        clean_observation_compatible=False, requires_shared_sink=False,
        restricted_current_clean_outcome=False,
        rate_recovery_required=(rate!="none"),
    )
    if st=="own_gset_contribution":
        r["clean_observation_compatible"]=True
        if alg=="gset":
            r["supported"]=True; r["duplicate_safe"]=True; r["concurrent_semantics_safe"]=True
            r["owner_crash_blocks"]=(owner=="crash")
            # A generation supersession requires selecting/filtering the current generation.
            r["needs_cross_role_reducer"]=bool(global_reduce or all_complete or gen)
            r["terminal_complete"]=bool(owner!="crash" and not r["needs_cross_role_reducer"])
            r["restricted_current_clean_outcome"]=r["terminal_complete"]
    elif st=="own_content_addressed_contribution":
        r["clean_observation_compatible"]=True
        if alg=="content_addressed":
            r["supported"]=True; r["duplicate_safe"]=True
            r["concurrent_semantics_safe"]=not conflict
            r["owner_crash_blocks"]=(owner=="crash")
            r["needs_cross_role_reducer"]=bool(global_reduce or all_complete or gen or conflict)
            r["terminal_complete"]=bool(owner!="crash" and not r["needs_cross_role_reducer"])
            r["restricted_current_clean_outcome"]=r["terminal_complete"]
    elif st=="own_max_candidate":
        r["clean_observation_compatible"]=True
        if alg=="max_register":
            r["supported"]=True; r["duplicate_safe"]=True; r["concurrent_semantics_safe"]=True
            r["owner_crash_blocks"]=(owner=="crash")
            r["needs_cross_role_reducer"]=True
    elif st=="static_escrow_disjoint_rights":
        r["clean_observation_compatible"]=True
        if alg=="escrow_rights":
            r["supported"]=True; r["duplicate_safe"]=True; r["concurrent_semantics_safe"]=True
            r["owner_crash_blocks"]=(owner=="crash")
            # Rights are never reassigned in this no-coordination variant; safety is retained by stranding unused rights.
            r["needs_cross_role_reducer"]=bool(global_reduce or all_complete)
            r["terminal_complete"]=bool(owner!="crash" and not r["needs_cross_role_reducer"])
            r["restricted_current_clean_outcome"]=r["terminal_complete"]
    elif st=="deterministic_single_owner":
        r["clean_observation_compatible"]=True
        if alg=="noncommutative":
            r["supported"]=True; r["duplicate_safe"]=True; r["concurrent_semantics_safe"]=True
            r["owner_crash_blocks"]=(owner=="crash")
            r["stale_generation_risk"]=bool(owner=="slow_late" and gen)
            r["needs_cross_role_reducer"]=bool(global_reduce or all_complete)
            r["terminal_complete"]=bool(owner!="crash" and not r["stale_generation_risk"] and not r["needs_cross_role_reducer"])
            r["restricted_current_clean_outcome"]=r["terminal_complete"]
    elif st=="shared_crdt_sink":
        r["requires_shared_sink"]=True
        if alg in {"gset","max_register","content_addressed"}:
            r["supported"]=True; r["duplicate_safe"]=True
            r["concurrent_semantics_safe"]=not (alg=="content_addressed" and conflict)
            r["owner_crash_blocks"]=(owner=="crash")
            r["terminal_complete"]=bool(owner!="crash" and r["concurrent_semantics_safe"])
    elif st=="fenced_shared_sink":
        r["requires_shared_sink"]=True
        r["supported"]=True; r["duplicate_safe"]=True; r["concurrent_semantics_safe"]=True
        r["terminal_complete"]=True
    return r

def slice_count(rows,st,pred,rpred):
    subset=[r for sc,s,r in rows if s==st and pred(sc)]
    return {"matching":sum(1 for r in subset if rpred(r)),"cases":len(subset)}

def main():
    scenarios=list(product(ALG,DUP,CONFLICT,OWNER,GEN,GLOBAL_REDUCE,ALL_COMPLETE,RATE))
    rows=[(sc,st,evaluate(sc,st)) for sc in scenarios for st in STRATEGIES]
    keys=["supported","duplicate_safe","concurrent_semantics_safe","terminal_complete",
          "needs_cross_role_reducer","owner_crash_blocks","stale_generation_risk",
          "clean_observation_compatible","requires_shared_sink","restricted_current_clean_outcome",
          "rate_recovery_required"]
    aggregates={}
    for st in STRATEGIES:
        rs=[r for sc,s,r in rows if s==st]
        aggregates[st]={k:sum(int(r[k]) for r in rs) for k in keys}
        aggregates[st]["scenario_count"]=len(rs)
    targeted={
        "gset_supported_duplicate_and_concurrency_safe":slice_count(rows,"own_gset_contribution",lambda sc:sc[0]=="gset",lambda r:r["duplicate_safe"] and r["concurrent_semantics_safe"]),
        "gset_current_clean_terminal_without_reducer":slice_count(rows,"own_gset_contribution",lambda sc:sc[0]=="gset",lambda r:r["terminal_complete"]),
        "content_addressed_conflicting_semantic_key_needs_reducer":slice_count(rows,"own_content_addressed_contribution",lambda sc:sc[0]=="content_addressed" and sc[2]==1,lambda r:r["needs_cross_role_reducer"] and not r["concurrent_semantics_safe"]),
        "max_candidate_always_needs_reducer":slice_count(rows,"own_max_candidate",lambda sc:sc[0]=="max_register",lambda r:r["needs_cross_role_reducer"] and not r["terminal_complete"]),
        "escrow_safe_but_owner_crash_strands_rights":slice_count(rows,"static_escrow_disjoint_rights",lambda sc:sc[0]=="escrow_rights" and sc[3]=="crash",lambda r:r["concurrent_semantics_safe"] and r["owner_crash_blocks"] and not r["terminal_complete"]),
        "escrow_current_clean_terminal_no_aggregate":slice_count(rows,"static_escrow_disjoint_rights",lambda sc:sc[0]=="escrow_rights",lambda r:r["terminal_complete"]),
        "single_owner_slow_late_generation_stale":slice_count(rows,"deterministic_single_owner",lambda sc:sc[0]=="noncommutative" and sc[3]=="slow_late" and sc[4]==1,lambda r:r["stale_generation_risk"]),
        "fenced_sink_full_positive_control":slice_count(rows,"fenced_shared_sink",lambda sc:True,lambda r:r["terminal_complete"] and r["duplicate_safe"] and r["concurrent_semantics_safe"]),
    }
    print(json.dumps({"scenario_count":len(scenarios),"strategy_evaluations":len(rows),"aggregates":aggregates,"targeted_slices":targeted},indent=2,sort_keys=True))

if __name__=="__main__":
    main()
