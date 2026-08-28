#!/usr/bin/env python3
from itertools import product
from collections import Counter
import json

def scenarios():
    out=[]
    for objective in ["global_atomic","saga_allowed","manual_allowed"]:
        for takeover,drift,tail_idemp,core_comp in product([False,True], repeat=4):
            core_cases=[
                ("clear",False,True),
                ("ambiguous",False,False),
                ("ambiguous",False,True),
                ("ambiguous",True,False),
                ("ambiguous",True,True),
            ]
            tail_cases=[
                ("clear",False,True),
                ("ambiguous",False,False),
                ("ambiguous",False,True),
                ("ambiguous",True,False),
                ("ambiguous",True,True),
            ]
            for core_resp,core_status,core_actual in core_cases:
                for tail_resp,tail_status,tail_actual in tail_cases:
                    comp_cases=["none"] if not core_comp else ["success","failed","ambiguous"]
                    for comp_final in comp_cases:
                        out.append(dict(objective=objective,takeover=takeover,drift=drift,tail_idemp=tail_idemp,
                            core_comp=core_comp,core_resp=core_resp,core_status=core_status,core_actual=core_actual,
                            tail_resp=tail_resp,tail_status=tail_status,tail_actual=tail_actual,comp_final=comp_final))
    return out

def evaluate(policy,s):
    core=tail=0
    actions=0
    drift=s["drift"] or s["takeover"]
    if policy=="pretend_global_atomic":
        actions+=1
        core=int(s["core_resp"]=="clear" or (s["core_resp"]=="ambiguous" and s["core_actual"]))
        if not drift:
            actions+=1
            tail=int(s["tail_resp"]=="clear" or (s["tail_resp"]=="ambiguous" and s["tail_actual"]))
        status="success"
    else:
        actions+=1
        if s["core_resp"]=="clear":
            core,core_known=1,True
        elif s["core_status"]:
            core,core_known=int(s["core_actual"]),True
        else:
            core,core_known=int(s["core_actual"]),False

        if not core_known:
            status="manual" if (policy=="manual_after_core" or s["objective"]=="manual_allowed") else "pending_core_unknown"
        elif core==0:
            status="safe_abort"
        else:
            if drift:
                tail_known_absent=True
                tail_resolved=False
            else:
                actions+=1
                if s["tail_resp"]=="clear":
                    tail,tail_resolved,tail_known_absent=1,True,False
                elif s["tail_status"]:
                    tail=int(s["tail_actual"])
                    tail_resolved=bool(tail)
                    tail_known_absent=not bool(tail)
                elif s["tail_idemp"]:
                    actions+=1
                    tail,tail_resolved,tail_known_absent=1,True,False
                else:
                    tail=int(s["tail_actual"])
                    tail_resolved=False
                    tail_known_absent=False

            if tail_resolved and tail==1:
                status="success"
            elif policy=="atomic_core_fenced_tail":
                status="manual" if s["objective"]=="manual_allowed" else "pending_tail"
            elif policy=="manual_after_core":
                status="manual"
            elif policy=="saga_partition":
                if tail_known_absent and s["core_comp"]:
                    actions+=1
                    if s["comp_final"]=="success":
                        core=0
                        status="safe_abort"
                    else:
                        status="manual" if s["objective"]=="manual_allowed" else "pending_comp"
                else:
                    status="manual" if s["objective"]=="manual_allowed" else "pending_tail"
            else:
                raise ValueError(policy)

    false_global=int(status=="success" and not (core==1 and tail==1))
    unsafe=false_global
    terminal=int(status in ("success","safe_abort","manual"))
    autonomous=int(status in ("success","safe_abort"))
    if s["objective"] in ("global_atomic","saga_allowed"):
        resolved=int(autonomous and ((core,tail)==(1,1) or (core,tail)==(0,0)))
    else:
        resolved=int(status=="manual" or (autonomous and ((core,tail)==(1,1) or (core,tail)==(0,0)))
    if unsafe: resolved=0
    return dict(status=status,unsafe=unsafe,false_global=false_global,residual_core_only=int(core==1 and tail==0),
                manual=int(status=="manual"),terminal=terminal,autonomous_terminal=autonomous,
                objective_resolved=resolved,actions=actions)

def main():
    ss=scenarios()
    policies=["pretend_global_atomic","atomic_core_fenced_tail","saga_partition","manual_after_core"]
    result={"scenario_count":len(ss),"policy_summary":{}}
    for p in policies:
        c=Counter()
        for s in ss:
            o=evaluate(p,s)
            for k,v in o.items():
                if isinstance(v,int): c[k]+=v
        result["policy_summary"][p]=dict(c)
    strong=policies[1:]
    result["archive"]={
        "safe_objective_coverage_union":sum(any(evaluate(p,s)["objective_resolved"] and not evaluate(p,s)["unsafe"] for p in strong) for s in ss),
        "safe_terminal_union":sum(any(evaluate(p,s)["terminal"] and not evaluate(p,s)["unsafe"] for p in strong) for s in ss),
        "safe_autonomous_terminal_union":sum(any(evaluate(p,s)["autonomous_terminal"] and not evaluate(p,s)["unsafe"] for p in strong) for s in ss),
    }
    print(json.dumps(result,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
