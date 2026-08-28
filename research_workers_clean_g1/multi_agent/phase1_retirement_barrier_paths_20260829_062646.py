#!/usr/bin/env python3
from itertools import product
from collections import Counter
import json

PATHS=["queue","direct_api","retry_worker","restore_archive"]
SINK_STATES=["current","stale_replica","rolled_back"]
CERT_STATES=["current","stale","none"]

def scenarios():
    keys=["repair_final","path","path_guard_intact","sink_state","cert_state",
          "anchor_available","old_repair_arrives","current_generation_advanced",
          "repair_kind","dedupe_valid"]
    return [dict(zip(keys,v)) for v in product(
        [False,True],PATHS,[False,True],SINK_STATES,CERT_STATES,
        [False,True],[False,True],[False,True],["cancel","compensate"],[False,True]
    )]

def classify(s,compacted=False,retained=False,old_allowed=False,
             current_blocked=False,validation_cost=0):
    final=s["repair_final"]
    arrival=s["old_repair_arrives"]
    bypass=bool(final and arrival and old_allowed)
    aba=bool(bypass and s["current_generation_advanced"])
    dup=bool(
        bypass and s["repair_kind"]=="compensate" and not s["dedupe_valid"]
    )
    lost=bool((not final) and arrival and not old_allowed)
    unsafe=bypass or lost or dup
    safe_compaction=bool(compacted and final and not unsafe)
    return dict(
        compacted=compacted,retained_state=retained,
        bypassed_old_generation_publication=bypass,
        rollback_aba=(aba and s["sink_state"]=="rolled_back"),
        aba_resurrection=aba,duplicate_compensation=dup,
        legitimate_repair_blocked=lost,
        current_work_blocked=current_blocked,
        unsafe=unsafe,safe_compaction=safe_compaction,
        validation_cost=validation_cost,
    )

def permanent_tombstone(s):
    return classify(
        s,retained=True,old_allowed=not s["repair_final"],validation_cost=1
    )

def coordinator_only_barrier(s):
    if not s["repair_final"]:
        return classify(s,retained=True,old_allowed=True,validation_cost=1)
    covered=(
        s["path"] in ("queue","retry_worker") and s["path_guard_intact"]
    )
    return classify(s,compacted=True,old_allowed=not covered,validation_cost=1)

def sink_local_barrier(s):
    if not s["repair_final"]:
        return classify(s,retained=True,old_allowed=True,validation_cost=1)
    reject=s["sink_state"]=="current"
    return classify(s,compacted=True,old_allowed=not reject,validation_cost=1)

def all_path_certificate_only(s):
    if not s["repair_final"]:
        return classify(s,retained=True,old_allowed=True,validation_cost=1)
    if s["path_guard_intact"]:
        if s["cert_state"]=="current":
            return classify(s,compacted=True,old_allowed=False,validation_cost=1)
        return classify(
            s,compacted=True,old_allowed=False,current_blocked=True,
            validation_cost=2
        )
    return classify(s,compacted=True,old_allowed=True,validation_cost=1)

def certificate_plus_sink_min(s):
    if not s["repair_final"]:
        return classify(s,retained=True,old_allowed=True,validation_cost=2)
    if s["path_guard_intact"]:
        if s["cert_state"]=="current":
            return classify(s,compacted=True,old_allowed=False,validation_cost=2)
        return classify(
            s,compacted=True,old_allowed=False,current_blocked=True,
            validation_cost=2
        )
    if s["sink_state"]=="current":
        return classify(s,compacted=True,old_allowed=False,validation_cost=2)
    return classify(s,compacted=True,old_allowed=True,validation_cost=2)

def premature_all_path_retire(s):
    if s["path_guard_intact"]:
        if s["cert_state"]=="current":
            return classify(s,compacted=True,old_allowed=False,validation_cost=2)
        return classify(
            s,compacted=True,old_allowed=False,current_blocked=True,
            validation_cost=2
        )
    if s["sink_state"]=="current":
        return classify(s,compacted=True,old_allowed=False,validation_cost=2)
    if s["anchor_available"]:
        return classify(s,compacted=True,old_allowed=False,validation_cost=3)
    return classify(
        s,compacted=True,old_allowed=False,current_blocked=True,
        validation_cost=3
    )

def safe_archive(s):
    if not s["repair_final"]:
        return classify(s,retained=True,old_allowed=True,validation_cost=2)
    if s["path_guard_intact"]:
        if s["cert_state"]=="current":
            return classify(s,compacted=True,old_allowed=False,validation_cost=2)
        return classify(
            s,compacted=True,old_allowed=False,current_blocked=True,
            validation_cost=2
        )
    if s["sink_state"]=="current":
        return classify(s,compacted=True,old_allowed=False,validation_cost=2)
    if s["anchor_available"]:
        return classify(s,compacted=True,old_allowed=False,validation_cost=3)
    return classify(
        s,compacted=True,old_allowed=False,current_blocked=True,
        validation_cost=3
    )

POLICIES={
    "permanent_tombstone":permanent_tombstone,
    "coordinator_only_barrier":coordinator_only_barrier,
    "sink_local_barrier":sink_local_barrier,
    "all_path_certificate_only":all_path_certificate_only,
    "certificate_plus_sink_min":certificate_plus_sink_min,
    "premature_all_path_retire":premature_all_path_retire,
    "safe_archive":safe_archive,
}

def aggregate(ss):
    out={}
    for name,fn in POLICIES.items():
        c=Counter(n=len(ss))
        cost=0
        for s in ss:
            r=fn(s)
            cost+=r["validation_cost"]
            for k,v in r.items():
                if isinstance(v,bool) and v:
                    c[k]+=1
        c["validation_cost_total"]=cost
        out[name]=dict(c)
    return out

def select(ss,pred):
    return [s for s in ss if pred(s)]

def main():
    ss=scenarios()
    result={
        "schema_version":1,
        "model":"all-path retirement-barrier bypass/rollback finite mechanism lattice",
        "scenario_count":len(ss),
        "aggregate":aggregate(ss),
        "targeted_slices":{
            "all_path_guard_bypassed_sink_stale_or_rollback_final_old_arrival":
                aggregate(select(
                    ss,lambda s:
                    s["repair_final"] and s["old_repair_arrives"] and
                    not s["path_guard_intact"] and s["sink_state"]!="current"
                )),
            "degraded_layers_anchor_available":aggregate(select(
                ss,lambda s:
                s["repair_final"] and s["old_repair_arrives"] and
                not s["path_guard_intact"] and s["sink_state"]!="current" and
                s["anchor_available"]
            )),
            "degraded_layers_no_anchor":aggregate(select(
                ss,lambda s:
                s["repair_final"] and not s["path_guard_intact"] and
                s["sink_state"]!="current" and not s["anchor_available"]
            )),
            "guard_intact_certificate_stale_or_missing":aggregate(select(
                ss,lambda s:
                s["repair_final"] and s["path_guard_intact"] and
                s["cert_state"]!="current"
            )),
            "pending_repair_old_arrival":aggregate(select(
                ss,lambda s:
                not s["repair_final"] and s["old_repair_arrives"]
            )),
            "direct_or_restore_final_old_arrival":aggregate(select(
                ss,lambda s:
                s["repair_final"] and s["old_repair_arrives"] and
                s["path"] in ("direct_api","restore_archive")
            )),
        },
        "notes":[
            "Equal-weight synthetic mechanism counts, not production incident rates.",
            "path_guard_intact models whether a publication path still enforces its retirement certificate; restore/rollback may disable this guard.",
            "sink_state models a sink-local minimum-generation witness that can be current, stale, or rolled back.",
            "anchor_available is a monotonic anti-rollback authority that can reconstruct/reassert the minimum generation when path and sink layers are degraded.",
            "safe_archive fails closed for current work when no current certificate, sink minimum, or anti-rollback anchor can be verified.",
            "validation_cost_total is a relative synthetic proof-check count, not latency."
        ]
    }
    print(json.dumps(result,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
