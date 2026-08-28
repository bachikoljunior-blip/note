#!/usr/bin/env python3
from itertools import product
from collections import Counter
import json

REPAIR_KINDS=["cancel","compensate"]
REPAIR_STATES=["FINAL_APPLIED","FINAL_NOOP","PENDING_REQUIRED"]
FUTURE_DRIFTS=["none","new_source","retention_extension"]

def scenarios():
    keys=["repair_kind","repair_state","proof_current","proof_complete",
          "future_drift","old_repair_arrives","ttl_expired","g3_advanced",
          "dedupe_valid","barrier_available"]
    out=[]
    for vals in product(
        REPAIR_KINDS,REPAIR_STATES,[False,True],[False,True],FUTURE_DRIFTS,
        [False,True],[False,True],[False,True],[False,True],[False,True]
    ):
        out.append(dict(zip(keys,vals)))
    return out

def classify(compacted=False,retained=False,safe_compaction=False,aba=False,
             lost=False,dup=False,false_quiescence=False,unresolved=False,
             terminal=False):
    unsafe=aba or lost or dup or false_quiescence
    safe_terminal=terminal and not unsafe and not unresolved
    return dict(
        compacted=compacted,retained_state=retained,
        safe_compaction=safe_compaction,aba_resurrection=aba,
        lost_legitimate_repair=lost,duplicate_compensation=dup,
        false_quiescence=false_quiescence,unresolved=unresolved,
        unsafe=unsafe,terminal=terminal,safe_terminal=safe_terminal,
    )

def permanent_tombstone(s):
    if s["repair_state"]=="PENDING_REQUIRED":
        if s["old_repair_arrives"]:
            return classify(retained=True,terminal=True)
        return classify(retained=True,unresolved=True)
    return classify(retained=True,terminal=True)

def compacted_no_barrier_outcome(s,effective_arrival=None):
    if effective_arrival is None:
        effective_arrival=s["old_repair_arrives"]
    state=s["repair_state"]
    if state=="PENDING_REQUIRED":
        if not effective_arrival:
            return classify(compacted=True,lost=True,
                            false_quiescence=True)
        if s["g3_advanced"]:
            return classify(compacted=True,aba=True,lost=True,
                            false_quiescence=True)
        return classify(compacted=True,safe_compaction=True,terminal=True)
    if not effective_arrival:
        return classify(compacted=True,safe_compaction=True,terminal=True)
    if s["g3_advanced"]:
        return classify(compacted=True,aba=True,false_quiescence=True)
    if (state=="FINAL_APPLIED" and s["repair_kind"]=="compensate"
        and not s["dedupe_valid"]):
        return classify(compacted=True,dup=True,false_quiescence=True)
    return classify(compacted=True,false_quiescence=True)

def finite_ttl_tombstone(s):
    if not s["ttl_expired"]:
        return permanent_tombstone(s)
    return compacted_no_barrier_outcome(s)

def registry_epoch_fenced(s):
    eligible=(
        s["proof_current"] and s["proof_complete"] and
        s["repair_state"]!="PENDING_REQUIRED"
    )
    if not eligible:
        return permanent_tombstone(s)
    effective_arrival=(
        s["old_repair_arrives"] and s["future_drift"]!="none"
    )
    return compacted_no_barrier_outcome(s,effective_arrival)

def early_retirement_barrier(s):
    eligible=(
        s["barrier_available"] and s["proof_current"] and s["proof_complete"]
    )
    if not eligible:
        return permanent_tombstone(s)
    if s["repair_state"]=="PENDING_REQUIRED":
        return classify(compacted=True,lost=True,false_quiescence=True)
    return classify(compacted=True,safe_compaction=True,terminal=True)

def finality_gated_retirement_barrier(s):
    eligible=(
        s["barrier_available"] and
        s["repair_state"]!="PENDING_REQUIRED"
    )
    if not eligible:
        return permanent_tombstone(s)
    return classify(compacted=True,safe_compaction=True,terminal=True)

def safe_archive(s):
    if s["barrier_available"] and s["repair_state"]!="PENDING_REQUIRED":
        return classify(compacted=True,safe_compaction=True,terminal=True)
    return permanent_tombstone(s)

POLICIES={
    "permanent_tombstone":permanent_tombstone,
    "finite_ttl_tombstone":finite_ttl_tombstone,
    "registry_epoch_fenced":registry_epoch_fenced,
    "early_retirement_barrier":early_retirement_barrier,
    "finality_gated_retirement_barrier":finality_gated_retirement_barrier,
    "safe_archive":safe_archive,
}

def aggregate(ss):
    out={}
    for name,fn in POLICIES.items():
        c=Counter(n=len(ss))
        for s in ss:
            r=fn(s)
            for k,v in r.items():
                if v is True:
                    c[k]+=1
        out[name]=dict(c)
    return out

def select(ss,pred):
    return [s for s in ss if pred(s)]

def main():
    ss=scenarios()
    result={
        "schema_version":1,
        "model":"repair-quiescence compaction finite mechanism lattice",
        "scenario_count":len(ss),
        "aggregate":aggregate(ss),
        "targeted_slices":{
            "registry_proof_then_future_drift_and_old_arrival":aggregate(select(
                ss,lambda s:
                s["proof_current"] and s["proof_complete"] and
                s["repair_state"]!="PENDING_REQUIRED" and
                s["future_drift"]!="none" and s["old_repair_arrives"]
            )),
            "early_barrier_while_legitimate_repair_pending":aggregate(select(
                ss,lambda s:
                s["barrier_available"] and s["proof_current"] and
                s["proof_complete"] and
                s["repair_state"]=="PENDING_REQUIRED"
            )),
            "ttl_expired_old_arrival_after_g3":aggregate(select(
                ss,lambda s:
                s["ttl_expired"] and s["old_repair_arrives"] and
                s["g3_advanced"]
            )),
            "final_repair_with_barrier_available":aggregate(select(
                ss,lambda s:
                s["barrier_available"] and
                s["repair_state"]!="PENDING_REQUIRED"
            )),
        },
        "notes":[
            "Equal-weight synthetic mechanism counts, not production incident rates.",
            "A source-registry proof is a snapshot; later replay-source/retention drift can invalidate it unless future mutation is fenced.",
            "A retirement barrier is modeled as a monotonic sink-side lower bound that rejects old-generation repair publications.",
            "The barrier is safe to compact against only after the historical repair vector is final; advancing it while repair is pending loses legitimate repair.",
            "retained_state counts one unit of retained per-incarnation witness for comparison, not bytes."
        ]
    }
    print(json.dumps(result,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
