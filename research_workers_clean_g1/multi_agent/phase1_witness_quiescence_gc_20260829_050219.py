#!/usr/bin/env python3
"""Finite synthetic stress test for deleting claim/incarnation witnesses only after source-qualified quiescence."""
from itertools import product
from collections import Counter, defaultdict
import json

WORKER_HORIZON={"w5":5,"w30":30,"unknown":None}
QUEUE_HORIZON={"none":0,"q14":14,"unknown":None}
ACTION_SOURCE=["worker","queue","both"]
ACTION_TYPE=["stale_result","stale_external_effect","stale_release"]
ACTION_AGE=[2,7,20,40,100]
TERMINATION=["none","best_effort_cancel","explicit_termination_ack"]
QUEUE_PROOF=["none","source_qualified_drain_ack"]
WITNESS_TTL=[5,14,30,90]
KEY_STATE=["retired","reused"]
SINK_SCOPE=["none","effect_only","all_authority"]
GC_EPOCH=["current","stale"]
GC_CRASH=["none","after_witness_delete_before_commit_marker"]
POLICIES=["time_only_ttl","cancel_ack_plus_ttl","source_qualified_quiescence","permanent_compact_witness","sink_durable_single_use"]

def worker_possible(h,a,t):
    if t=="explicit_termination_ack": return False
    return True if h is None else a<=h

def queue_possible(h,a,p):
    if p=="source_qualified_drain_ack" or h==0: return False
    return True if h is None else a<=h

def stale_possible(src,wh,qh,a,t,qp):
    w=worker_possible(wh,a,t); q=queue_possible(qh,a,qp)
    return w if src=="worker" else q if src=="queue" else w or q

def source_quiet(src,wh,qh,ttl,t,qp):
    w=t=="explicit_termination_ack" or (wh is not None and ttl>=wh)
    q=qp=="source_qualified_drain_ack" or qh==0 or (qh is not None and ttl>=qh)
    return w if src=="worker" else q if src=="queue" else w and q

def sink_protects(scope,typ):
    return scope=="all_authority" or (scope=="effect_only" and typ=="stale_external_effect")

def evaluate(policy,wh,qh,src,typ,age,t,qp,ttl,key,sink,epoch,crash):
    r=Counter(); possible=stale_possible(src,wh,qh,age,t,qp); after=age>ttl
    r["stale_action_possible"]=int(possible); r["action_after_ttl"]=int(after)
    if policy=="permanent_compact_witness":
        r["retained"]=1; r["storage_units"]=5; r["stale_action_blocked"]+=int(possible); return r
    if policy=="time_only_ttl": gc=True; r["storage_units"]=1
    elif policy=="cancel_ack_plus_ttl":
        gc=t=="explicit_termination_ack" or (wh is not None and ttl>=wh); r["storage_units"]=2
    elif policy=="source_qualified_quiescence":
        gc=source_quiet(src,wh,qh,ttl,t,qp) and epoch=="current"; r["storage_units"]=3
        if gc and crash!="none": r["gc_recovery_needed"]+=1; gc=False
    elif policy=="sink_durable_single_use":
        protected=sink_protects(sink,typ)
        gc=(protected or source_quiet(src,wh,qh,ttl,t,qp)) and epoch=="current"
        r["storage_units"]=2 if protected else 3
        if gc and crash!="none":
            r["gc_recovery_needed"]+=1
            if not protected: gc=False
    r["reclaimed"]+=int(gc); r["retained"]+=int(not gc)
    if not gc:
        r["stale_action_blocked"]+=int(possible); return r
    if not (possible and after): return r
    if policy=="sink_durable_single_use" and sink_protects(sink,typ):
        r["stale_action_blocked"]+=1; r["sink_witness_used"]+=1; return r
    r["stale_after_gc_accept"]+=1; r["aba_accept"]+=int(key=="reused")
    if typ=="stale_external_effect": r["duplicate_authoritative_effect"]+=1
    elif typ=="stale_result": r["stale_result_accept"]+=1; r["false_terminal_or_overwrite"]+=1
    elif key=="reused": r["new_claim_deleted"]+=1; r["false_exclusion_or_liveness"]+=1
    else: r["stale_release_no_target"]+=1
    return r

def unsafe(r):
    return int(bool(r["stale_after_gc_accept"] and (r["duplicate_authoritative_effect"] or r["stale_result_accept"] or r["new_claim_deleted"])))

def main():
    totals={p:Counter() for p in POLICIES}; slices=defaultdict(Counter); n=0
    dims=product(WORKER_HORIZON.items(),QUEUE_HORIZON.items(),ACTION_SOURCE,ACTION_TYPE,ACTION_AGE,TERMINATION,QUEUE_PROOF,WITNESS_TTL,KEY_STATE,SINK_SCOPE,GC_EPOCH,GC_CRASH)
    for (whn,wh),(qhn,qh),src,typ,age,t,qp,ttl,key,sink,epoch,crash in dims:
        n+=1; rs={}
        for p in POLICIES:
            r=evaluate(p,wh,qh,src,typ,age,t,qp,ttl,key,sink,epoch,crash); r["unsafe"]=unsafe(r); rs[p]=r; totals[p]["scenarios"]+=1
            for k,v in r.items(): totals[p][k]+=v
            for metric,field in [("unsafe","unsafe_scenarios"),("reclaimed","reclaimed_scenarios"),("retained","retained_scenarios"),("stale_after_gc_accept","stale_after_gc_scenarios"),("duplicate_authoritative_effect","duplicate_effect_scenarios"),("aba_accept","aba_accept_scenarios")]:
                totals[p][field]+=int(bool(r[metric]))
        def add_slice(name,extra=None):
            s=slices[name]; s["scenarios"]+=1
            for p,r in rs.items():
                s[p+"_reclaimed"]+=int(r["reclaimed"]); s[p+"_unsafe"]+=int(r["unsafe"])
                if extra:
                    for metric in extra: s[p+"_"+metric]+=int(r[metric])
        if qhn=="unknown" and src in ("queue","both") and qp=="none": add_slice("unknown_queue_replay_no_drain")
        if whn=="unknown" and src in ("worker","both") and t!="explicit_termination_ack": add_slice("unknown_worker_lifetime_no_ack")
        if t=="explicit_termination_ack" and qp=="source_qualified_drain_ack": add_slice("explicit_full_quiescence")
        if epoch=="stale": add_slice("stale_gc_epoch")
        if crash!="none": add_slice("gc_crash",["gc_recovery_needed"])
        if sink=="all_authority": add_slice("durable_all_authority_sink")
        if qhn=="q14" and src in ("queue","both") and qp=="none" and ttl<14 and age>ttl and age<=14:
            add_slice("known_q14_replay_outlives_ttl",["stale_after_gc_accept"])
    out={"model":{"scenario_count":n,"equal_weight_synthetic":True,"empirical_rate_claim":False,"dimensions":{"worker_horizon":list(WORKER_HORIZON),"queue_horizon":list(QUEUE_HORIZON),"action_source":ACTION_SOURCE,"action_type":ACTION_TYPE,"action_age":ACTION_AGE,"termination":TERMINATION,"queue_quiescence":QUEUE_PROOF,"witness_ttl":WITNESS_TTL,"key_state":KEY_STATE,"sink_scope":SINK_SCOPE,"gc_epoch":GC_EPOCH,"gc_crash":GC_CRASH}},"policies":{},"slices":{k:dict(v) for k,v in slices.items()},"scope_limits":["Finite mechanism lattice only; counts are not production probabilities.","Known worker/queue horizons are explicit source contracts; unknown horizons remain potentially unbounded in-model.","Explicit termination acknowledgement and source-qualified queue drain acknowledgement are strong capabilities, not inferred from best-effort cancellation or an empty queue read.","sink durable single-use is modeled only for action classes covered by sink_scope; it moves durable identity storage to the authority sink rather than eliminating it.","GC crash safety for source-qualified quiescence assumes an atomic/recoverable compact witness commit; stale GC epochs fail closed."]}
    for p,c in totals.items():
        d=dict(c); d["unsafe_rate"]=c["unsafe_scenarios"]/n; d["reclamation_coverage"]=c["reclaimed_scenarios"]/n; d["avg_storage_units"]=c["storage_units"]/n; out["policies"][p]=d
    print(json.dumps(out,indent=2,sort_keys=True))
if __name__=="__main__": main()
