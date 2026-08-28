#!/usr/bin/env python3
from itertools import product
from collections import Counter
import json

def scenarios():
    out=[]
    for p1,p2 in product([False,True], repeat=2):
        for crash in ["none","before_decision","after_decision_before_notify","after_p1_notify"]:
            for takeover,query,heuristic,late_old in product([False,True], repeat=4):
                for supersede in ["none","before_decision","after_decision"]:
                    if crash=="before_decision" and supersede=="after_decision":
                        continue
                    out.append(dict(p1=p1,p2=p2,crash=crash,takeover=takeover,query=query,
                                    heuristic=heuristic,late_old=late_old,supersede=supersede))
    return out

def evaluate(policy,s):
    st=["PREPARED" if s["p1"] else "NONE","PREPARED" if s["p2"] else "NONE"]
    all_prepared=s["p1"] and s["p2"]
    intended="COMMIT" if all_prepared and s["supersede"]!="before_decision" else "ABORT"
    actions=int(s["p1"])+int(s["p2"])
    durable_decision=None
    stale_apply=false_abort=decision_violation=0

    def notify(i,decision):
        nonlocal actions
        if st[i]=="PREPARED":
            st[i]=decision
            actions+=1

    if policy=="durable_decision_2pc":
        if s["crash"]=="before_decision":
            if s["takeover"]:
                for i in [0,1]: notify(i,"ABORT")
                status="safe_abort"
            else:
                status="manual"
        else:
            durable_decision=intended
            actions+=1
            if s["crash"]=="none":
                for i in [0,1]: notify(i,durable_decision)
            elif s["crash"]=="after_decision_before_notify":
                if s["takeover"] or s["query"]:
                    for i in [0,1]: notify(i,durable_decision)
            elif s["crash"]=="after_p1_notify":
                notify(0,durable_decision)
                if s["takeover"] or s["query"]:
                    notify(1,durable_decision)
            if s["late_old"]:
                for i in [0,1]: notify(i,durable_decision)
            status="success" if all(x=="COMMIT" for x in st) else ("safe_abort" if all(x in ("ABORT","NONE") for x in st) else "manual")

    elif policy=="timeout_heuristic":
        if s["crash"]=="before_decision":
            if s["takeover"] or s["heuristic"]:
                for i in [0,1]: notify(i,"ABORT")
                status="safe_abort"
            else:
                status="manual"
        else:
            durable_decision=intended
            actions+=1
            if s["crash"]=="none":
                for i in [0,1]: notify(i,durable_decision)
            elif s["crash"]=="after_decision_before_notify":
                if s["takeover"] or s["query"]:
                    for i in [0,1]: notify(i,durable_decision)
                elif s["heuristic"]:
                    for i in [0,1]: notify(i,"ABORT")
            elif s["crash"]=="after_p1_notify":
                notify(0,durable_decision)
                if s["takeover"] or s["query"]:
                    notify(1,durable_decision)
                elif s["heuristic"]:
                    notify(1,"ABORT")
            if s["late_old"]:
                for i in [0,1]:
                    if st[i]=="PREPARED": notify(i,durable_decision)
            status="success" if all(x=="COMMIT" for x in st) else ("safe_abort" if all(x in ("ABORT","NONE") for x in st) else "manual")

    elif policy=="coordinator_memory_only":
        memory_decision=None if s["crash"]=="before_decision" else intended
        if s["crash"]=="before_decision":
            if s["takeover"]:
                for i in [0,1]: notify(i,"ABORT")
                status="safe_abort"
            else:
                status="manual"
        elif s["crash"]=="none":
            if memory_decision=="COMMIT" and s["supersede"]=="after_decision": stale_apply=1
            for i in [0,1]: notify(i,memory_decision)
            status="success" if all(x=="COMMIT" for x in st) else "safe_abort"
        elif s["crash"]=="after_decision_before_notify":
            if s["takeover"]:
                for i in [0,1]: notify(i,"ABORT")
                if intended=="COMMIT": false_abort=1
                status="safe_abort"
            elif s["late_old"]:
                if memory_decision=="COMMIT" and s["supersede"]=="after_decision": stale_apply=1
                for i in [0,1]: notify(i,memory_decision)
                status="success" if all(x=="COMMIT" for x in st) else "safe_abort"
            else:
                status="manual"
        else:
            if memory_decision=="COMMIT" and s["supersede"]=="after_decision": stale_apply=1
            notify(0,memory_decision)
            if s["takeover"]:
                notify(1,"ABORT")
                if intended=="COMMIT": false_abort=1
            elif s["late_old"]:
                notify(1,memory_decision)
            status="success" if all(x=="COMMIT" for x in st) else ("safe_abort" if all(x in ("ABORT","NONE") for x in st) else "manual")

    elif policy=="manual_prepared_reconciliation":
        if s["crash"]=="none":
            decision=intended
            if s["supersede"]=="after_decision" and decision=="COMMIT":
                decision="ABORT"
                false_abort=1
            for i in [0,1]: notify(i,decision)
            status="success" if all(x=="COMMIT" for x in st) else "safe_abort"
        elif s["crash"]=="after_p1_notify":
            decision=intended
            if not (decision=="COMMIT" and s["supersede"]=="after_decision"):
                notify(0,decision)
            status="manual"
        else:
            status="manual"
    else:
        raise ValueError(policy)

    split=int("COMMIT" in st and "ABORT" in st)
    if durable_decision=="COMMIT" and any(x=="ABORT" for x in st): decision_violation=1
    if durable_decision=="ABORT" and any(x=="COMMIT" for x in st): decision_violation=1
    unsafe=int(bool(split or decision_violation or stale_apply))
    autonomous=int(status in ("success","safe_abort"))
    return dict(status=status,unsafe=unsafe,split=split,decision_violation=decision_violation,stale_apply=stale_apply,
                false_abort=false_abort,orphan_prepared=sum(x=="PREPARED" for x in st),manual=int(status=="manual"),
                terminal=int(status in ("success","safe_abort","manual")),autonomous_terminal=autonomous,
                objective_resolved=int(autonomous and not unsafe),commit_success=int(status=="success" and intended=="COMMIT" and not unsafe),
                actions=actions)

def main():
    ss=scenarios()
    policies=["durable_decision_2pc","timeout_heuristic","coordinator_memory_only","manual_prepared_reconciliation"]
    result={"scenario_count":len(ss),"policy_summary":{}}
    for p in policies:
        c=Counter()
        for s in ss:
            o=evaluate(p,s)
            for k,v in o.items():
                if isinstance(v,int): c[k]+=v
        result["policy_summary"][p]=dict(c)
    print(json.dumps(result,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
