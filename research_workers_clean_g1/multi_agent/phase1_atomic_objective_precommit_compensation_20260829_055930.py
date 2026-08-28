#!/usr/bin/env python3
from itertools import product
from collections import Counter
import json

def scenarios():
    out=[]
    for objective in ["atomic","forward","mixed","manual"]:
        for a_rev,b_rev,cap,takeover,drift in product([False,True], repeat=5):
            pre_cases=[("none",False,False)] if not cap else [
                ("clear",False,False),
                ("ambiguous",False,False),
                ("ambiguous",False,True),
                ("ambiguous",True,False),
                ("ambiguous",True,True),
            ]
            for pre_resp, pre_status, pre_applied in pre_cases:
                for comp_avail in [False,True]:
                    if not (a_rev and comp_avail):
                        comp_cases=[("none",False,False,False)]
                    else:
                        comp_cases=[
                            ("success",False,False,False),
                            ("failed",False,False,False),
                            ("ambiguous",False,False,False),
                            ("ambiguous",False,False,True),
                            ("ambiguous",True,False,False),
                            ("ambiguous",True,False,True),
                            ("ambiguous",False,True,False),
                            ("ambiguous",False,True,True),
                        ]
                    for comp_finality, comp_idemp, comp_status, comp_applied in comp_cases:
                        out.append(dict(objective=objective,a_rev=a_rev,b_rev=b_rev,cap=cap,
                            pre_resp=pre_resp,pre_status=pre_status,pre_applied=pre_applied,
                            comp_avail=comp_avail,comp_finality=comp_finality,comp_idemp=comp_idemp,
                            comp_status=comp_status,comp_applied=comp_applied,takeover=takeover,drift=drift))
    return out

def evaluate(policy,s):
    drift=s["drift"] or s["takeover"]
    a,b,actions=1,0,1
    dup_comp=dup_eff=0
    if policy=="per_fragment_fence":
        if not drift: b,actions,status=1,2,"success"
        else: status="manual" if s["objective"]=="manual" else "pending"
    elif policy=="fail_closed_manual":
        if not drift: b,actions,status=1,2,"success"
        else: status="manual"
    elif policy=="compensate_after_partial":
        if not drift:
            b,actions,status=1,2,"success"
        elif s["a_rev"] and s["comp_avail"]:
            actions+=1
            if s["comp_finality"]=="success":
                a,status=0,"rollback"
            elif s["comp_finality"]=="failed":
                status="manual" if s["objective"]=="manual" else "pending"
            elif s["comp_status"]:
                if s["comp_applied"]: a,status=0,"rollback"
                else: status="manual" if s["objective"]=="manual" else "pending"
            elif s["comp_idemp"]:
                actions+=1; a,status=0,"rollback"
            else:
                status="manual" if s["objective"]=="manual" else "pending"
        else:
            status="manual" if s["objective"]=="manual" else "pending"
    elif policy=="blind_comp_retry":
        if not drift:
            b,actions,status=1,2,"success"
        elif s["a_rev"] and s["comp_avail"]:
            actions+=1
            if s["comp_finality"]=="success":
                a,status=0,"rollback"
            elif s["comp_finality"]=="failed":
                status="manual" if s["objective"]=="manual" else "pending"
            elif s["takeover"]:
                actions+=1
                if s["comp_applied"] and not s["comp_idemp"]: dup_comp=1
                a,status=0,"rollback"
            elif s["comp_applied"]:
                a,status=0,"rollback"
            else:
                status="manual" if s["objective"]=="manual" else "pending"
        else:
            status="manual" if s["objective"]=="manual" else "pending"
    elif policy=="atomic_precommit":
        a=b=actions=0
        if not s["cap"]:
            status="manual" if s["objective"]=="manual" else "pending_no_effect"
        else:
            actions=1
            if s["pre_resp"]=="clear":
                a=b=1; status="success"
            elif s["pre_status"]:
                if s["pre_applied"]: a=b=1; status="success"
                else: status="safe_abort"
            else:
                if s["pre_applied"]: a=b=1
                status="pending_unknown"
    elif policy=="partial_as_done":
        if not drift: b,actions,status=1,2,"success"
        else: status="success"
    else:
        raise ValueError(policy)

    partial=(a==1 and b==0)
    false_atomic=int(s["objective"]=="atomic" and status in ("success","rollback","safe_abort") and partial)
    false_success=int(status=="success" and (a,b)!=(1,1))
    unsafe=int(bool(dup_comp or dup_eff or false_atomic or false_success))
    terminal=int(status in ("success","rollback","safe_abort","manual"))
    autonomous=int(status in ("success","rollback","safe_abort"))
    if s["objective"]=="atomic":
        resolved=int((a,b) in [(1,1),(0,0)] and autonomous)
    elif s["objective"]=="forward":
        resolved=int((a,b)==(1,1) and status=="success")
    elif s["objective"]=="mixed":
        resolved=int(((a,b)==(1,1) and status=="success") or ((a,b)==(0,0) and status in ("rollback","safe_abort")))
    else:
        resolved=int(((a,b)==(1,1) and status=="success") or status=="manual")
    if unsafe: resolved=0
    return dict(status=status,unsafe=unsafe,false_atomic_terminal=false_atomic,dup_comp=dup_comp,dup_eff=dup_eff,
        residual=int(partial),irreversible_residual=int(partial and not s["a_rev"]),manual=int(status=="manual"),
        terminal=terminal,autonomous_terminal=autonomous,objective_resolved=resolved,actions=actions)

def main():
    ss=scenarios()
    policies=["per_fragment_fence","atomic_precommit","compensate_after_partial",
              "fail_closed_manual","blind_comp_retry","partial_as_done"]
    res={"scenario_count":len(ss),"policy_summary":{}}
    for p in policies:
        c=Counter()
        for s in ss:
            o=evaluate(p,s)
            for k,v in o.items():
                if isinstance(v,int): c[k]+=v
        res["policy_summary"][p]=dict(c)
    strong=policies[:4]
    res["archive"]={
        "safe_objective_coverage_union":sum(any(evaluate(p,s)["objective_resolved"] and not evaluate(p,s)["unsafe"] for p in strong) for s in ss),
        "safe_terminal_union":sum(any(evaluate(p,s)["terminal"] and not evaluate(p,s)["unsafe"] for p in strong) for s in ss),
        "safe_autonomous_terminal_union":sum(any(evaluate(p,s)["autonomous_terminal"] and not evaluate(p,s)["unsafe"] for p in strong) for s in ss),
    }
    print(json.dumps(res,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
