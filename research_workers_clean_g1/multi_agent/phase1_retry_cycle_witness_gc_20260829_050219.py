#!/usr/bin/env python3
"""Finite synthetic stress test for cyclic retry/redrive horizons and sink-witness GC."""
from itertools import product
from collections import Counter,defaultdict
import math,json
CLOCK=["absolute_deadline","per_attempt_reset","unbounded"];BOUND=[30,100];ATTEMPTS=[2,4,"unbounded"]
REDRIVE=["none","once_preserve_age","once_reset_age","repeat_reset_age"];ACK=[False,True];ROOT=[14,30,90];SINKTTL=[14,30,90]
AGE=[20,50,120,250];SCOPE=["none","all_authority"];ATTEMPT_ID=["unique","reused"];EPOCH=["current","stale"];TYPE=["canonical_result","external_effect"]
POL=["acyclic_projection","attempt_count_times_bound","absolute_deadline_certificate","loop_termination_certificate","neg_sink_ttl_only","sink_identity_graph_gated","permanent_witness"]
def base(c,b,a):
 if c=="absolute_deadline":return b
 if c=="unbounded" or a=="unbounded":return math.inf
 return b*a
def horizon(c,b,a,r,ack):
 if ack:return 0
 h=base(c,b,a)
 if r in ("none","once_preserve_age"):return h
 if r=="once_reset_age":return math.inf if math.isinf(h) else 2*h
 return math.inf if h>0 else 0
def exact(scope,aid):return scope=="all_authority" and aid=="unique"
def ev(p,c,b,a,r,ack,rt,st,age,scope,aid,epoch,typ):
 x=Counter();h=horizon(c,b,a,r,ack);possible=h>0 and age<=h;x["stale_possible"]+=int(possible)
 if p=="permanent_witness":x["retained"]+=1;x["storage_units"]+=5;x["blocked"]+=int(possible);return x
 if epoch!="current" and p not in ("acyclic_projection","neg_sink_ttl_only"):
  x["retained"]+=1;x["storage_units"]+=3;x["blocked"]+=int(possible);x["stale_epoch_blocked"]+=1;return x
 if p=="acyclic_projection":req=b;gc=rt>=req;x["storage_units"]+=1
 elif p=="attempt_count_times_bound":
  req=0 if ack else b if c=="absolute_deadline" else b*a if c=="per_attempt_reset" and a!="unbounded" else math.inf;gc=req<math.inf and rt>=req;x["storage_units"]+=2
 elif p=="absolute_deadline_certificate":
  req=0 if ack else b if c=="absolute_deadline" and r in ("none","once_preserve_age") else math.inf;gc=req<math.inf and rt>=req;x["storage_units"]+=2
 elif p=="loop_termination_certificate":req=h;gc=req<math.inf and rt>=req;x["storage_units"]+=3
 elif p=="neg_sink_ttl_only":gc=exact(scope,aid);x["storage_units"]+=2
 elif p=="sink_identity_graph_gated":
  e=exact(scope,aid);gc=True if e and (h==0 or (h<math.inf and st>=h)) else h<math.inf and rt>=h;x["sink_identity_used"]+=int(e and gc);x["storage_units"]+=2 if e and gc else 3
 x["reclaimed"]+=int(gc);x["retained"]+=int(not gc)
 if not gc:x["blocked"]+=int(possible);return x
 if not(possible and age>rt):return x
 if p in ("neg_sink_ttl_only","sink_identity_graph_gated") and exact(scope,aid) and age<=st:x["blocked"]+=1;x["sink_identity_used"]+=1;return x
 x["stale_after_gc_accept"]+=1
 if typ=="external_effect":x["duplicate_authoritative_effect"]+=1
 else:x["stale_result_accept"]+=1;x["false_terminal_or_overwrite"]+=1
 return x
def unsafe(x):return int(bool(x["duplicate_authoritative_effect"] or x["stale_result_accept"]))
def main():
 totals={p:Counter() for p in POL};sl=defaultdict(Counter);n=0
 for c,b,a,r,ack,rt,st,age,scope,aid,epoch,typ in product(CLOCK,BOUND,ATTEMPTS,REDRIVE,ACK,ROOT,SINKTTL,AGE,SCOPE,ATTEMPT_ID,EPOCH,TYPE):
  h=horizon(c,b,a,r,ack);n+=1;rs={};safe=h<math.inf and rt>=h and epoch=="current"
  for p in POL:
   x=ev(p,c,b,a,r,ack,rt,st,age,scope,aid,epoch,typ);x["unsafe"]+=unsafe(x);rs[p]=x;totals[p]["scenarios"]+=1
   for k,v in x.items():totals[p][k]+=v
   totals[p]["unsafe_scenarios"]+=int(x["unsafe"]);totals[p]["reclaimed_scenarios"]+=int(x["reclaimed"]);totals[p]["overretained_vs_loop_scenarios"]+=int(safe and not x["reclaimed"])
  def add(name):
   s=sl[name];s["scenarios"]+=1
   for p,x in rs.items():s[p+"_unsafe"]+=int(x["unsafe"]);s[p+"_reclaimed"]+=int(x["reclaimed"])
  if r in ("once_reset_age","repeat_reset_age") and not ack:add("redrive_resets_age")
  if r=="repeat_reset_age" and not ack:add("unbounded_redrive_cycle")
  if c=="absolute_deadline" and r in ("none","once_preserve_age") and not ack:add("absolute_deadline_supported")
  if c=="per_attempt_reset" and a!="unbounded" and r=="none" and not ack:add("bounded_attempt_reset_no_redrive")
  if scope=="all_authority" and aid=="unique":add("exact_sink_identity")
  if scope=="all_authority" and aid=="reused":add("reused_attempt_id_sink_collision")
  if ack:add("explicit_loop_termination")
  if c=="per_attempt_reset" and a!="unbounded" and r in ("once_reset_age","repeat_reset_age") and not ack and rt>=b*a and (math.isinf(h) or rt<h):add("attempt_count_undercounts_redrive")
 out={"model":{"scenario_count":n,"equal_weight_synthetic":True,"empirical_rate_claim":False,"retry_clock":CLOCK,"bound":BOUND,"attempts":ATTEMPTS,"redrive":REDRIVE,"loop_ack":ACK,"root_ttl":ROOT,"sink_ttl":SINKTTL,"action_age":AGE,"sink_scope":SCOPE,"attempt_id":ATTEMPT_ID,"epoch":EPOCH,"action_type":TYPE},"policies":{},"slices":{k:dict(v) for k,v in sl.items()},"scope_limits":["Finite synthetic retry-loop model only; not production failure rates.","absolute_deadline means retries share one end-to-end age budget; per_attempt_reset means each attempt can consume a fresh bound.","Redrive reset semantics are source-specific and must be documented before use.","Sink identity is effective only when unique for the current incarnation/action and retained through the reachable retry horizon.","Explicit loop termination is modeled as a strong source-qualified proof."]}
 for p,c in totals.items():d=dict(c);d["unsafe_rate"]=c["unsafe_scenarios"]/n;d["reclamation_coverage"]=c["reclaimed_scenarios"]/n;d["avg_storage_units"]=c["storage_units"]/n;out["policies"][p]=d
 print(json.dumps(out,indent=2,sort_keys=True))
if __name__=="__main__":main()
