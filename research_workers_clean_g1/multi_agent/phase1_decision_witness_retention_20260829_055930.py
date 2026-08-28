#!/usr/bin/env python3
from itertools import product
from collections import Counter
import json

def scenarios():
    return [
        dict(decision=decision,p1_final=p1_final,p2_final=p2_final,ack_loss=ack_loss,
             ttl_expired=ttl_expired,backup_restore=backup_restore,reuse=reuse,late_old=late_old)
        for decision,p1_final,p2_final,ack_loss,ttl_expired,backup_restore,reuse,late_old in product(
            ["COMMIT","ABORT"],[False,True],[False,True],[False,True],
            [False,True],[False,True],[False,True],[False,True])
    ]

def evaluate(policy,s):
    old_prepared=[not s["p1_final"], (not s["p2_final"]) or s["backup_restore"]]
    old_prepared_count=sum(old_prepared)
    both_acked=s["p1_final"] and s["p2_final"] and not s["ack_loss"]
    decision_available=generation_fence=False
    false_exclusion=0
    if policy=="ttl_delete":
        decision_available=not s["ttl_expired"]
        generation_fence=decision_available
        storage=100 if decision_available else 0
    elif policy=="all_acks_delete":
        decision_available=not both_acked
        generation_fence=decision_available
        storage=100 if decision_available else 0
    elif policy=="compact_witness":
        decision_available=True
        generation_fence=True
        storage=10
    elif policy=="generation_watermark":
        generation_fence=True
        storage=5
    elif policy=="manual_forever":
        decision_available=True
        generation_fence=True
        storage=100
    elif policy=="name_tombstone":
        generation_fence=True
        storage=5
        if s["reuse"]: false_exclusion=1
    else:
        raise ValueError(policy)

    wrong_count=stale_generation=reads=0
    remaining=old_prepared_count
    if old_prepared_count:
        reads+=1
        if decision_available:
            remaining=0
        elif policy in ("generation_watermark","name_tombstone"):
            remaining=old_prepared_count
        else:
            if s["late_old"] and not s["reuse"]:
                remaining=0
            else:
                if s["decision"]=="COMMIT":
                    wrong_count=old_prepared_count
                remaining=0

    if s["reuse"]:
        reads+=1
        if not generation_fence and s["late_old"]:
            stale_generation=1

    unsafe=int(bool(wrong_count or stale_generation))
    return dict(
        unsafe=unsafe,
        wrong_late_decision=int(bool(wrong_count)),
        wrong_late_decision_count=wrong_count,
        stale_generation_apply=stale_generation,
        orphan_prepared=remaining,
        false_exclusion=false_exclusion,
        manual=int(remaining>0),
        old_terminal=int(remaining==0 and not unsafe),
        autonomous_terminal=int(remaining==0 and not unsafe),
        storage_units=storage,
        recovery_reads=reads
    )

def main():
    ss=scenarios()
    policies=["ttl_delete","all_acks_delete","compact_witness","generation_watermark","manual_forever","name_tombstone"]
    result={"scenario_count":len(ss),"policy_summary":{}}
    for p in policies:
        c=Counter()
        for s in ss:
            for k,v in evaluate(p,s).items(): c[k]+=v
        result["policy_summary"][p]=dict(c)
    print(json.dumps(result,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
