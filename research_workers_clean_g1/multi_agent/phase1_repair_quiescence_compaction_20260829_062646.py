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

def classify(terminal=False,compacted=False,retained=False,
             safe_compaction=False,aba=False,lost=False,dup=False,
             false_quiescence=False,unresolved=False):
    unsafe=aba or lost or dup or false_quiescence
    safe_terminal=terminal and not unsafe and not unresolved
    return dict(
        terminal=terminal,safe_terminal=safe_terminal,unsafe=unsafe,
        compacted=compacted,retained_state=retained,
        safe_compaction=safe_compaction,aba_resurrection=aba,
        lost_legitimate_repair=lost,duplicate_compensation=dup,
        false_quiescence=false_quiescence,unresolved=unresolved,
    )

def permanent_tombstone(s):
    if s["repair_state"]=="PENDING_REQUIRED":
        if s["old_repair_arrives"]:
            return classify(terminal=True,retained=True)
        return classify(retained=True,unresolved=True)
    return classify(terminal=True,retained=True)

def compacted_no_barrier_outcome(s):
    pending=s["repair_state"]=="PENDING_REQUIRED"
    arrives=s["old_repair_arrives"]
    if pending and not arrives:
        return classify(compacted=True,lost=True,false_quiescence=True,
                        unresolved=True)
    if pending and arrives and s["g3_advanced"]:
        return classify(compacted=True,aba=True,lost=True,
                        false_quiescence=True)
    if pending and arrives and not s["g3_advanced"]:
        return classify(terminal=True,compacted=True,safe_compaction=True)
    if not arrives:
        return classify(terminal=True,compacted=True,safe_compaction=True)
    if s["g3_advanced"]:
        return classify(compacted=True,aba=True,false_quiescence=True)
    if (s["repair_state"]=="FINAL_APPLIED" and
        s["repair_kind"]=="compensate" and not s["dedupe_valid"]):
        return classify(compacted=True,dup=True,false_quiescence=True)
    return classify(compacted=True,false_quiescence=True)

def finite_ttl_tombstone(s):
    if not s["ttl_expired"]:
        return permanent_tombstone(s)
    return compacted_no_barrier_outcome(s)

def registry_epoch_fenced(s):
    eligible=(s["proof_current"] and s["proof_complete"] and
              s["repair_state"]!="PENDING_REQUIRED")
    if not eligible:
        return permanent_tombstone(s)
    effective=dict(s)
    effective["old_repair_arrives"]=(
        s["old_repair_arrives"] and s["future_drift"]!="none"
    )
    return compacted_no_barrier_outcome(effective)

def early_retirement_barrier(s):
    eligible=(s["barrier_available"] and s["proof_current"] and
              s["proof_complete"])
    if not eligible:
        return permanent_tombstone(s)
    if s["repair_state"]=="PENDING_REQUIRED":
        return classify(compacted=True,lost=True,false_quiescence=True,
                        unresolved=not s["old_repair_arrives"])
    return classify(terminal=True,compacted=True,safe_compaction=True)

def finality_gated_retirement_barrier(s):
    eligible=(s["barrier_available"] and
              s["repair_state"]!="PENDING_REQUIRED")
    if eligible:
        return classify(terminal=True,compacted=True,safe_compaction=True)
    return permanent_tombstone(s)

def safe_archive(s):
    return finality_gated_retirement_barrier(s)

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
        "model":"repair-quiescence/tombstone-compaction finite mechanism lattice",
        "scenario_count":len(ss),
        "aggregate":aggregate(ss),
        "targeted_slices":{
            "current_complete_final_then_future_registry_drift_and_old_arrival":aggregate(select(
                ss,lambda s:s["proof_current"] and s["proof_complete"] and
                s["repair_state"]!="PENDING_REQUIRED" and
                s["future_drift"]!="none" and s["old_repair_arrives"]
            )),
            "early_barrier_while_legitimate_repair_pending":aggregate(select(
                ss,lambda s:s["barrier_available"] and s["proof_current"] and
                s["proof_complete"] and
                s["repair_state"]=="PENDING_REQUIRED"
            )),
            "ttl_expired_old_repair_arrives_after_g3":aggregate(select(
                ss,lambda s:s["ttl_expired"] and s["old_repair_arrives"] and
                s["g3_advanced"]
            )),
            "final_repair_and_barrier_available":aggregate(select(
                ss,lambda s:s["repair_state"]!="PENDING_REQUIRED" and
                s["barrier_available"]
            )),
        },
        "notes":[
            "Equal-weight synthetic mechanism counts, not production incident rates.",
            "A current/complete replay-registry proof is a snapshot; future source addition or retention extension can reopen replay after tombstone compaction.",
            "A monotonic sink-side retirement/minimum-repair-generation barrier blocks future old-generation repair only when every publication path respects it.",
            "Advancing the retirement barrier before historical repair is final loses still-legitimate repair.",
            "Fixed TTL is modeled as time-based deletion rather than a repair-quiescence certificate."
        ]
    }
    print(json.dumps(result,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
