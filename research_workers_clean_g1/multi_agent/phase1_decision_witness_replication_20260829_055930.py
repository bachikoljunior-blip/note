#!/usr/bin/env python3
from collections import Counter
import json

def scenarios():
    out=[]
    for mask in range(1,8):
        written={i for i in range(3) if mask & (1<<i)}
        for failed in [None,0,1,2]:
            for target in [0,1,2]:
                for decision in ["COMMIT","ABORT"]:
                    for reuse in [False,True]:
                        for old_opposite in [False,True]:
                            if not reuse and old_opposite:
                                continue
                            old=("ABORT" if decision=="COMMIT" else "COMMIT") if old_opposite else decision
                            out.append(dict(written=written,failed=failed,target=target,decision=decision,reuse=reuse,old_decision=old))
    return out

def node_state(s,i):
    if s["failed"]==i: return ("DOWN",None)
    if i in s["written"]: return ("CUR",s["decision"])
    if s["reuse"]: return ("OLD",s["old_decision"])
    return ("NONE",None)

def evaluate(policy,s):
    if policy in ("w2r1_accept_any","w2r1_versioned","w2r2_unversioned","w2r2_versioned"):
        ack=len(s["written"])>=2; W=2
    elif policy=="dual_all2":
        ack=0 in s["written"] and 1 in s["written"]; W=2
    elif policy in ("single_default_abort","single_failclosed"):
        ack=0 in s["written"]; W=1
    elif policy=="manual_any":
        ack=len(s["written"])>=1; W=1
    else: raise ValueError(policy)
    if not ack:
        return dict(unsafe=0,wrong=0,stale_accept=0,lost=0,mixed=0,write_unavailable=1,
                    read_unavailable=0,manual=0,recovered=0,ack=0,write_cost=W,read_cost=0)

    observed=[]; R=0
    if policy.startswith("single"):
        R=1; st=node_state(s,0)
        if st[0]!="DOWN": observed=[st]
    elif policy=="dual_all2":
        R=1
        for i in [0,1]:
            st=node_state(s,i)
            if st[0]!="DOWN": observed=[st]; break
    elif policy in ("w2r1_accept_any","w2r1_versioned","manual_any"):
        R=1; st=node_state(s,s["target"])
        if st[0]!="DOWN": observed=[st]
    else:
        R=2
        avail=[i for i in range(3) if s["failed"]!=i]
        if len(avail)>=2: observed=[node_state(s,i) for i in avail[:2]]

    if not observed:
        if policy=="single_default_abort":
            wrong=int(s["decision"]!="ABORT")
            return dict(unsafe=wrong,wrong=wrong,stale_accept=0,lost=1,mixed=0,write_unavailable=0,
                        read_unavailable=1,manual=0,recovered=int(not wrong),ack=1,write_cost=W,read_cost=R)
        return dict(unsafe=0,wrong=0,stale_accept=0,lost=1,mixed=0,write_unavailable=0,
                    read_unavailable=1,manual=1,recovered=0,ack=1,write_cost=W,read_cost=R)

    kinds={k for k,_ in observed}
    vals=[v for _,v in observed if v]
    mixed=int("CUR" in kinds and ("OLD" in kinds or "NONE" in kinds))
    chosen=None; stale_accept=0; lost=manual=0

    if policy in ("single_default_abort","w2r1_accept_any"):
        k,v=observed[0]
        if k=="NONE": chosen="ABORT"
        elif k in ("CUR","OLD"):
            chosen=v; stale_accept=int(k=="OLD")
    elif policy in ("single_failclosed","w2r1_versioned","manual_any"):
        k,v=observed[0]
        if k=="CUR": chosen=v
        else: manual=1; lost=1
    elif policy=="dual_all2":
        k,v=observed[0]
        if k=="CUR": chosen=v
        else: manual=1; lost=1
    elif policy=="w2r2_versioned":
        current=[v for k,v in observed if k=="CUR"]
        if current: chosen=current[0]
        else: manual=1; lost=1
    elif policy=="w2r2_unversioned":
        if "OLD" in kinds: stale_accept=1
        value_set=set(vals)
        if len(value_set)==1 and vals: chosen=vals[0]
        elif len(value_set)>1: chosen="ABORT"
        else: chosen="ABORT"

    wrong=int(chosen is not None and chosen!=s["decision"])
    recovered=int(chosen is not None and not wrong and not stale_accept)
    unsafe=int(bool(wrong or stale_accept))
    return dict(unsafe=unsafe,wrong=wrong,stale_accept=stale_accept,lost=lost,mixed=mixed,
                write_unavailable=0,read_unavailable=0,manual=manual,recovered=recovered,ack=1,
                write_cost=W,read_cost=R)

def main():
    ss=scenarios()
    policies=["single_default_abort","single_failclosed","dual_all2","w2r1_accept_any",
              "w2r1_versioned","w2r2_unversioned","w2r2_versioned","manual_any"]
    result={"schema_version":1,"model":"phase1_decision_witness_replication_quorum_failover",
            "scenario_count":len(ss),"policy_summary":{}}
    for p in policies:
        c=Counter()
        for s in ss: c.update(evaluate(p,s))
        result["policy_summary"][p]=dict(c)
    stale_r1=[s for s in ss if len(s["written"])>=2 and s["reuse"] and s["old_decision"]!=s["decision"]
              and s["target"] not in s["written"] and s["failed"]!=s["target"]]
    mixed_q=[]
    for s in ss:
        if len(s["written"])<2: continue
        avail=[i for i in range(3) if s["failed"]!=i]
        if len(avail)<2: continue
        obs=[node_state(s,i) for i in avail[:2]]
        if any(k=="CUR" for k,_ in obs) and any(k=="OLD" for k,_ in obs): mixed_q.append(s)
    one_write_replica_lost=[s for s in ss if len(s["written"])==2 and s["failed"] in s["written"]]
    result["slices"]={
      "write_quorum_read_one_hits_opposite_old_generation":{
        "scenario_count":len(stale_r1),
        "accept_any_unsafe":sum(evaluate("w2r1_accept_any",s)["unsafe"] for s in stale_r1),
        "versioned_failclosed_manual":sum(evaluate("w2r1_versioned",s)["manual"] for s in stale_r1)},
      "quorum_read_observes_current_plus_old_generation":{
        "scenario_count":len(mixed_q),
        "unversioned_unsafe":sum(evaluate("w2r2_unversioned",s)["unsafe"] for s in mixed_q),
        "versioned_unsafe":sum(evaluate("w2r2_versioned",s)["unsafe"] for s in mixed_q)},
      "write_quorum_then_one_written_replica_lost":{
        "scenario_count":len(one_write_replica_lost),
        "w2r2_versioned_recovered":sum(evaluate("w2r2_versioned",s)["recovered"] for s in one_write_replica_lost),
        "w2r2_versioned_unsafe":sum(evaluate("w2r2_versioned",s)["unsafe"] for s in one_write_replica_lost)}
    }
    print(json.dumps(result,indent=2,sort_keys=True))

if __name__=="__main__": main()
