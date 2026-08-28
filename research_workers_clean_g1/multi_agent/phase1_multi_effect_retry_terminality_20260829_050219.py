#!/usr/bin/env python3
"""Finite synthetic two-effect retry/compensation terminality and behavior-archive stress test."""
from itertools import product
from collections import Counter,defaultdict
import math,json
STATES=["applied_final","failed_final","pending_apply","pending_fail"];H=[30,100,math.inf]
CONTRACTS={"reversible_comp":(True,False),"irreversible_comp":(True,True),"irreversible_no_comp":(False,True)}
TTL=[30,100];CH=[30,100,math.inf];CO=["success","late_failed"];AUTH=["current","superseded"];OVERLAP=["disjoint","shared"];FENCE=[False,True];CDEDUPE=[False,True]
POL=["neg_root_boolean","forward_certificate","rollback_certificate","mixed_vector_certificate","manual_fail_closed"]
def settle(s,h,t):
 if s=="applied_final":return "applied"
 if s=="failed_final":return "failed"
 if h<=t:return "applied" if s=="pending_apply" else "failed"
 return "unknown"
def fwd(states,hs,cs,t,auth,overlap,fence,safe=True):
 r=Counter();fs=[settle(s,h,t) for s,h in zip(states,hs)]
 if safe and "unknown" in fs:r["unresolved"]+=fs.count("unknown");return r
 need=[i for i,f in enumerate(fs) if f in ("failed","unknown")]
 if need and auth!="current":
  if safe:r["unresolved"]+=len(need);return r
  r["stale_authority"]+=len(need)
 if len(need)>=2 and overlap=="shared" and not fence:
  if safe:r["unresolved"]+=len(need);return r
  r["duplicate_authoritative_effect"]+=1
 for i in need:r["actions"]+=1;r["new_effects"]+=1;r["irreversible_issuance"]+=int(cs[i][1])
 r["terminal"]+=1;r["business_terminal"]+=1;r["orientation_forward"]+=1;r["residual_exposure"]+=sum(int(c[1]) for c in cs);return r
def rollback(states,hs,cs,t,ch,co,cd,safe=True,accept=False):
 r=Counter();fs=[settle(s,h,t) for s,h in zip(states,hs)]
 if safe and "unknown" in fs:r["unresolved"]+=fs.count("unknown");return r
 for i,f in enumerate(fs):
  if f not in ("applied","unknown"):continue
  comp,irr=cs[i]
  if not comp:
   if safe:r["unresolved"]+=1;r["residual_exposure"]+=int(irr);continue
   r["false_terminal_event"]+=1;r["residual_exposure"]+=int(irr);continue
  r["actions"]+=1;r["comp_issued"]+=1
  if accept:r["false_terminal_event"]+=int(co!="success");r["residual_exposure"]+=int(irr);continue
  if ch>t:
   if safe:r["unresolved"]+=1
   else:r["false_terminal_event"]+=1
   r["residual_exposure"]+=int(irr);continue
  if co=="success":r["residual_exposure"]+=int(irr);continue
  if cd and t>=30:r["actions"]+=1;r["comp_issued"]+=1;r["comp_depth2"]+=1;r["residual_exposure"]+=int(irr)
  else:r["unresolved"]+=1 if safe else 0;r["false_terminal_event"]+=0 if safe else 1;r["residual_exposure"]+=int(irr)
 if r["unresolved"]==0:r["terminal"]+=1;r["business_terminal"]+=1;r["orientation_rollback"]+=1
 return r
def mixed(states,hs,cs,t):
 r=Counter();fs=[settle(s,h,t) for s,h in zip(states,hs)]
 if "unknown" in fs:r["unresolved"]+=fs.count("unknown");return r
 r["terminal"]+=1;r["business_terminal"]+=1;r["orientation_mixed"]+=1;r["residual_exposure"]+=sum(int(f=="applied" and c[1]) for f,c in zip(fs,cs));return r
def neg(states,hs,cs,t,auth,overlap,fence,ch,co,cd):
 r=Counter();fs=[settle(s,h,t) for s,h in zip(states,hs)];u=fs.count("unknown");r["false_terminal_event"]+=u;need=[i for i,f in enumerate(fs) if f!="applied"]
 if need and auth!="current":r["stale_authority"]+=len(need);r["false_terminal_event"]+=len(need)
 if len(need)>=2 and overlap=="shared" and not fence:r["duplicate_authoritative_effect"]+=1
 r["actions"]+=len(need);r["new_effects"]+=len(need)
 for i,f in enumerate(fs):
  if f=="applied" and cs[i][0]:r["actions"]+=1;r["comp_issued"]+=1;r["false_terminal_event"]+=int(ch>t or co!="success")
 r["terminal"]+=1;r["business_terminal"]+=1;r["unsafe"]+=int(bool(r["false_terminal_event"] or r["stale_authority"] or r["duplicate_authoritative_effect"]));r["false_terminal_scenario"]+=r["unsafe"];return r
def manual():r=Counter();r["terminal"]+=1;r["manual_terminal"]+=1;return r
def pareto(bs):
 dims=["actions","new_effects","comp_issued","residual_exposure"];out=[]
 for i,(p,r) in enumerate(bs):
  v=tuple(r[d] for d in dims);dom=False
  for j,(_,q) in enumerate(bs):
   if i==j:continue
   w=tuple(q[d] for d in dims)
   if all(a<=b for a,b in zip(w,v)) and any(a<b for a,b in zip(w,v)):dom=True;break
  if not dom:out.append((p,r))
 return out
def main():
 totals={p:Counter() for p in POL};sl=defaultdict(Counter);arc=Counter();niches=Counter();n=0
 for s1,h1,c1,s2,h2,c2,t,ch,co,auth,ov,ef,cd in product(STATES,H,CONTRACTS,STATES,H,CONTRACTS,TTL,CH,CO,AUTH,OVERLAP,FENCE,CDEDUPE):
  states=[s1,s2];hs=[h1,h2];cs=[CONTRACTS[c1],CONTRACTS[c2]];n+=1;rs={"neg_root_boolean":neg(states,hs,cs,t,auth,ov,ef,ch,co,cd),"forward_certificate":fwd(states,hs,cs,t,auth,ov,ef),"rollback_certificate":rollback(states,hs,cs,t,ch,co,cd),"mixed_vector_certificate":mixed(states,hs,cs,t),"manual_fail_closed":manual()}
  for p,r in rs.items():
   if p!="neg_root_boolean":r["unsafe"]+=0
   totals[p]["scenarios"]+=1
   for k,v in r.items():totals[p][k]+=v
   totals[p]["business_terminal_scenarios"]+=int(r["business_terminal"]);totals[p]["manual_terminal_scenarios"]+=int(r["manual_terminal"]);totals[p]["unsafe_scenarios"]+=int(r["unsafe"]);totals[p]["false_terminal_scenarios"]+=int(r["false_terminal_scenario"]);totals[p]["unresolved_scenarios"]+=int(bool(r["unresolved"]))
  safe=[(p,rs[p]) for p in ("forward_certificate","rollback_certificate","mixed_vector_certificate") if rs[p]["business_terminal"]]
  if safe:
   arc["covered"]+=1;ors=set("F" if r["orientation_forward"] else "R" if r["orientation_rollback"] else "M" for _,r in safe);arc["multi_behavior"]+=int(len(ors)>1);nd=pareto(safe);arc["multi_pareto"]+=int(len(nd)>1)
   for p,r in nd:arc[p+"_pareto"]+=1;niches[("F" if r["orientation_forward"] else "R" if r["orientation_rollback"] else "M",min(r["actions"],4),min(r["new_effects"],2),min(r["comp_issued"],4),min(r["residual_exposure"],2))]+=1
  fs=[settle(s,h,t) for s,h in zip(states,hs)]
  def add(name):
   s=sl[name];s["scenarios"]+=1
   for p,r in rs.items():s[p+"_business_terminal"]+=int(r["business_terminal"]);s[p+"_unsafe"]+=int(r["unsafe"])
  if "unknown" in fs:add("at_least_one_unknown_retry_loop")
  if auth=="superseded" and any(f=="failed" for f in fs):add("superseded_parent_with_failed_effect")
  if ov=="shared" and not ef and fs.count("failed")==2:add("shared_effect_key_two_failed_no_fence")
  if co=="late_failed" and ch<=t and any(f=="applied" and c[0] for f,c in zip(fs,cs)):add("late_comp_failure")
 out={"model":{"scenario_count":n,"equal_weight_synthetic":True,"empirical_rate_claim":False,"effect_states":STATES,"horizons":[30,100,"unknown"],"contracts":list(CONTRACTS),"ttl":TTL,"comp_horizon":[30,100,"unknown"],"comp_outcome":CO,"parent_auth":AUTH,"effect_key_overlap":OVERLAP,"effect_fence":FENCE,"comp_dedupe":CDEDUPE},"policies":{},"safe_archive":{},"slices":{k:dict(v) for k,v in sl.items()},"scope_limits":["Finite synthetic two-effect mechanism lattice; not production failure rates.","mixed_vector_certificate is an explicit per-effect terminal disposition, not equivalent to all-forward or all-rollback business policy.","Unknown retry horizons block safe business terminality.","Late-failed compensation retry is a distinct linked compensation identity and requires compensation dedupe.","Manual terminal is operational/manual-attention only and is excluded from business-terminal archive coverage."]}
 for p,c in totals.items():d=dict(c);d["business_terminal_coverage"]=c["business_terminal_scenarios"]/n;d["unsafe_rate"]=c["unsafe_scenarios"]/n;out["policies"][p]=d
 out["safe_archive"]={"covered_scenarios":arc["covered"],"coverage":arc["covered"]/n,"multi_behavior_scenarios":arc["multi_behavior"],"multi_behavior_rate":arc["multi_behavior"]/n,"multi_pareto_scenarios":arc["multi_pareto"],"multi_pareto_rate":arc["multi_pareto"]/n,"pareto_branch_counts":{p:arc[p+"_pareto"] for p in ("forward_certificate","rollback_certificate","mixed_vector_certificate")},"behavior_niche_count":len(niches)}
 print(json.dumps(out,indent=2,sort_keys=True))
if __name__=="__main__":main()
