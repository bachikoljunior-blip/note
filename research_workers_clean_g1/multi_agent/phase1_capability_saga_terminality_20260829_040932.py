#!/usr/bin/env python3
from itertools import product
from collections import Counter
import json
CONTRACT=["revocable_until_effect","irrevocable_after_authorize"]
MINT=["atomic_with_parent","separate_read_then_mint"]
CAP=["single_use_durable","replayable"]
PARENT=["stable","supersede_before_mint","supersede_after_mint_before_first","supersede_after_first"]
E2=["ok","blocked"]
COMP=["none","available"]
COMP_OUT=["ok","ambiguous_applied","late_failed"]
TAKE=["none","dispatcher_takeover"]

def scenarios():
    ks=["contract","mint","cap","parent","e2","comp","comp_out","takeover"]
    return [dict(zip(ks,v)) for v in product(CONTRACT,MINT,CAP,PARENT,E2,COMP,COMP_OUT,TAKE)]
def b(): return dict(terminal=False,terminal_compensated=False,unsafe=False,stale_effect=False,duplicate_effect=False,partial_effect=False,false_terminal=False,comp_ambiguous=False,structural_block=False,parallel_dispatch=False,serialized_dispatch=False)

def revocable_local_check(s):
    r=b(); r["serialized_dispatch"]=True
    if s["contract"]!="revocable_until_effect": r["structural_block"]=True; return r
    if s["parent"]=="supersede_before_mint": return r
    if s["parent"]=="supersede_after_mint_before_first": r["stale_effect"]=r["unsafe"]=True; return r
    if s["takeover"]!="none" and s["cap"]=="replayable": r["duplicate_effect"]=r["unsafe"]=True
    if s["e2"]=="blocked": r["partial_effect"]=True; return r
    if s["parent"]=="supersede_after_first": r["partial_effect"]=True; return r
    if not r["unsafe"]: r["terminal"]=True
    return r

def cooperative_revocable_sink(s):
    r=b(); r["parallel_dispatch"]=True
    if s["contract"]!="revocable_until_effect" or s["cap"]!="single_use_durable": r["structural_block"]=True; return r
    if s["parent"]!="stable": return r
    if s["e2"]=="blocked": r["partial_effect"]=True; return r
    r["terminal"]=True; return r

def irrevocable_atomic_singleuse(s):
    r=b(); r["parallel_dispatch"]=True
    if s["contract"]!="irrevocable_after_authorize" or s["mint"]!="atomic_with_parent" or s["cap"]!="single_use_durable": r["structural_block"]=True; return r
    if s["parent"]=="supersede_before_mint": return r
    if s["e2"]=="blocked": r["partial_effect"]=True; return r
    r["terminal"]=True; return r

def irrevocable_separate_mint(s):
    r=b(); r["parallel_dispatch"]=True
    if s["contract"]!="irrevocable_after_authorize" or s["mint"]!="separate_read_then_mint": r["structural_block"]=True; return r
    if s["parent"]=="supersede_before_mint": r["stale_effect"]=r["unsafe"]=True
    if s["takeover"]!="none" and s["cap"]=="replayable": r["duplicate_effect"]=r["unsafe"]=True
    if s["e2"]=="blocked": r["partial_effect"]=True; return r
    if not r["unsafe"]: r["terminal"]=True
    return r

def saga_strong(s):
    r=b(); r["serialized_dispatch"]=True
    if s["contract"]!="irrevocable_after_authorize" or s["mint"]!="atomic_with_parent" or s["cap"]!="single_use_durable": r["structural_block"]=True; return r
    if s["parent"]=="supersede_before_mint": return r
    if s["e2"]=="ok": r["terminal"]=True; return r
    r["partial_effect"]=True
    if s["comp"]!="available": return r
    if s["comp_out"]=="ok": r["terminal_compensated"]=r["terminal"]=True; return r
    r["comp_ambiguous"]=True; return r

def neg_saga_terminal_on_comp_accept(s):
    r=b(); r["serialized_dispatch"]=True
    if s["contract"]!="irrevocable_after_authorize" or s["mint"]!="atomic_with_parent" or s["cap"]!="single_use_durable": r["structural_block"]=True; return r
    if s["parent"]=="supersede_before_mint": return r
    if s["e2"]=="ok": r["terminal"]=True; return r
    r["partial_effect"]=True
    if s["comp"]!="available": return r
    r["terminal_compensated"]=r["terminal"]=True
    if s["comp_out"]=="late_failed": r["false_terminal"]=r["unsafe"]=True
    if s["comp_out"]=="ambiguous_applied": r["comp_ambiguous"]=True
    return r
P={"revocable_local_check":revocable_local_check,"cooperative_revocable_sink":cooperative_revocable_sink,"irrevocable_atomic_singleuse":irrevocable_atomic_singleuse,"NEG_irrevocable_separate_mint":irrevocable_separate_mint,"saga_strong_finality":saga_strong,"NEG_saga_terminal_on_comp_accept":neg_saga_terminal_on_comp_accept}
def summ(rows):
    out={}
    for n,f in P.items():
        c=Counter()
        for s in rows:
            for k,v in f(s).items():
                if isinstance(v,bool): c[k]+=int(v)
        out[n]=dict(c)
    return out
def sl(rows,p):
    ss=[s for s in rows if p(s)]; return {"count":len(ss),"protocols":summ(ss)}
def main():
    rows=scenarios()
    print(json.dumps({"scenario_count":len(rows),"protocol_summary":summ(rows),"targeted_slices":{"revocable_after_local_check":sl(rows,lambda s:s["contract"]=="revocable_until_effect" and s["parent"]=="supersede_after_mint_before_first"),"irrevocable_atomic_after_mint_supersede":sl(rows,lambda s:s["contract"]=="irrevocable_after_authorize" and s["mint"]=="atomic_with_parent" and s["cap"]=="single_use_durable" and s["parent"] in ("supersede_after_mint_before_first","supersede_after_first")),"irrevocable_separate_mint_race":sl(rows,lambda s:s["contract"]=="irrevocable_after_authorize" and s["mint"]=="separate_read_then_mint" and s["parent"]=="supersede_before_mint"),"compensation_late_failure":sl(rows,lambda s:s["contract"]=="irrevocable_after_authorize" and s["mint"]=="atomic_with_parent" and s["cap"]=="single_use_durable" and s["e2"]=="blocked" and s["comp"]=="available" and s["comp_out"]=="late_failed"),"capability_replay_takeover":sl(rows,lambda s:s["contract"]=="irrevocable_after_authorize" and s["mint"]=="separate_read_then_mint" and s["cap"]=="replayable" and s["takeover"]=="dispatcher_takeover")},"scope_notes":["Equal-weight synthetic mechanism counts, not production probabilities.","Irrevocable-after-authorize changes semantics: parent supersession after successful atomic mint does not revoke the effect capability.","Atomic mint means parent-currentness validation and capability creation are one authority transition.","Single-use durable capability consumption is an explicit sink capability assumption.","Saga compensation is not rollback atomicity; strong terminality waits for compensation finality."]},indent=2,sort_keys=True))
if __name__=="__main__": main()
