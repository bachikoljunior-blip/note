#!/usr/bin/env python3
"""Finite synthetic stress test for composing stale-writer/replay horizons across sequential and fan-out graphs."""
from itertools import product
from collections import Counter, defaultdict
import math, json
TOPOLOGIES={"chain3":[("e1","e2","e3")],"fanout2":[("e1","e2"),("e1","e3")]}
B1={"5":5,"20":20,"unknown":None};B2={"5":5,"14":14,"unknown":None};B3={"5":5,"30":30,"unknown":None}
DRAIN=list(range(8));TTLS=[5,14,20,40,70];AGES=[7,15,25,45,80]
TYPES=["canonical_result","external_effect"];SINK=["none","effect_only","all_authority"];KEY=["retired","reused"];EPOCH=["current","stale"]
POLICIES=["max_edge_heuristic","sum_all_edges_heuristic","root_quiet_only","graph_path_certificate","sink_chain_identity","permanent_root_witness"]
def edges(t):return sorted(set(e for p in TOPOLOGIES[t] for e in p))
def drained(m,e):return bool(m&(1<<{"e1":0,"e2":1,"e3":2}[e]))
def residual(e,b,m):return 0 if drained(m,e) else b[e]
def ph(path,b,m):
 s=0
 for e in path:
  v=residual(e,b,m)
  if v is None:return math.inf
  s+=v
 return s
def gh(t,b,m):return max(ph(p,b,m) for p in TOPOLOGIES[t])
def meh(t,b,m):
 vs=[]
 for e in edges(t):
  v=residual(e,b,m)
  if v is None:return math.inf
  vs.append(v)
 return max(vs) if vs else 0
def sah(t,b,m):
 s=0
 for e in edges(t):
  v=residual(e,b,m)
  if v is None:return math.inf
  s+=v
 return s
def protects(s,typ):return s=="all_authority" or (s=="effect_only" and typ=="external_effect")
def ev(policy,t,b,m,ttl,age,typ,sink,key,epoch):
 r=Counter();h=gh(t,b,m);possible=h>0 and age<=h;r["stale_descendant_possible"]+=int(possible);r["action_after_ttl"]+=int(age>ttl)
 if policy=="permanent_root_witness":r["retained"]+=1;r["storage_units"]+=5;r["stale_blocked"]+=int(possible);return r
 if epoch!="current" and policy in ("graph_path_certificate","sink_chain_identity","sum_all_edges_heuristic"):
  r["retained"]+=1;r["storage_units"]+={"graph_path_certificate":3,"sink_chain_identity":2,"sum_all_edges_heuristic":3}[policy];r["stale_blocked"]+=int(possible);r["stale_gc_blocked"]+=1;return r
 if policy=="max_edge_heuristic":req=meh(t,b,m);gc=req<math.inf and ttl>=req;r["storage_units"]+=2
 elif policy=="sum_all_edges_heuristic":req=sah(t,b,m);gc=req<math.inf and ttl>=req;r["storage_units"]+=3
 elif policy=="root_quiet_only":gc=drained(m,"e1");r["storage_units"]+=1
 elif policy=="graph_path_certificate":req=h;gc=req<math.inf and ttl>=req;r["storage_units"]+=3
 elif policy=="sink_chain_identity":
  p=protects(sink,typ);gc=True if p else h<math.inf and ttl>=h;r["sink_identity_used"]+=int(p);r["storage_units"]+=2 if p else 3
 r["reclaimed"]+=int(gc);r["retained"]+=int(not gc)
 if not gc:r["stale_blocked"]+=int(possible);return r
 if not(possible and age>ttl):return r
 if policy=="sink_chain_identity" and protects(sink,typ):r["stale_blocked"]+=1;return r
 r["stale_after_gc_accept"]+=1;r["aba_accept"]+=int(key=="reused")
 if typ=="external_effect":r["duplicate_authoritative_effect"]+=1
 else:r["stale_result_accept"]+=1;r["false_terminal_or_overwrite"]+=1
 return r
def unsafe(r):return int(bool(r["duplicate_authoritative_effect"] or r["stale_result_accept"]))
def main():
 totals={p:Counter() for p in POLICIES};sl=defaultdict(Counter);n=0
 for t,(_,b1),(_,b2),(_,b3),m,ttl,age,typ,sink,key,epoch in product(TOPOLOGIES,B1.items(),B2.items(),B3.items(),DRAIN,TTLS,AGES,TYPES,SINK,KEY,EPOCH):
  b={"e1":b1,"e2":b2,"e3":b3};n+=1;rs={};h=gh(t,b,m);graph_safe=h<math.inf and ttl>=h and epoch=="current"
  for p in POLICIES:
   r=ev(p,t,b,m,ttl,age,typ,sink,key,epoch);r["unsafe"]+=unsafe(r);rs[p]=r;totals[p]["scenarios"]+=1
   for k,v in r.items():totals[p][k]+=v
   totals[p]["unsafe_scenarios"]+=int(bool(r["unsafe"]));totals[p]["reclaimed_scenarios"]+=int(bool(r["reclaimed"]));totals[p]["overretained_vs_graph_scenarios"]+=int(graph_safe and not r["reclaimed"])
  def add(name):
   s=sl[name];s["scenarios"]+=1
   for p,r in rs.items():s[p+"_unsafe"]+=int(r["unsafe"]);s[p+"_reclaimed"]+=int(r["reclaimed"])
  if t=="chain3" and all(b[e] is not None for e in b) and m==0:add("bounded_chain_no_drains")
  if t=="fanout2" and all(b[e] is not None for e in b) and m==0:add("bounded_fanout_no_drains")
  if drained(m,"e1") and h>0:add("root_drained_descendants_remain")
  if math.isinf(h):add("unknown_undrained_edge")
  x=meh(t,b,m)
  if x<math.inf and ttl>=x and (h==math.inf or ttl<h):add("max_edge_false_quiescence_claim")
  x=sah(t,b,m)
  if t=="fanout2" and h<math.inf and ttl>=h and (x==math.inf or ttl<x) and epoch=="current":add("fanout_sum_overretains")
 out={"model":{"scenario_count":n,"equal_weight_synthetic":True,"empirical_rate_claim":False,"topologies":TOPOLOGIES,"edge_bounds":{"e1":B1,"e2":B2,"e3":B3},"ttl":TTLS,"ages":AGES,"drain_masks":DRAIN,"action_types":TYPES,"sink_scopes":SINK,"key_state":KEY,"gc_epoch":EPOCH},"policies":{},"slices":{k:dict(v) for k,v in sl.items()},"scope_limits":["Finite deterministic bounded-propagation model; not production failure rates.","A path horizon is the sum of residual sequential edge bounds; fan-out graph horizon is the maximum root-to-sink path sum.","Drain proof sets an edge's residual horizon to zero only as a strong source-qualified acknowledgement.","Unknown undrained edge yields an unbounded path and blocks graph-certificate reclamation unless the exact authority sink has a durable identity.","Sink identity protects only action types covered by sink_scope and moves, rather than eliminates, durable witness retention."]}
 for p,c in totals.items():d=dict(c);d["unsafe_rate"]=c["unsafe_scenarios"]/n;d["reclamation_coverage"]=c["reclaimed_scenarios"]/n;d["avg_storage_units"]=c["storage_units"]/n;out["policies"][p]=d
 print(json.dumps(out,indent=2,sort_keys=True))
if __name__=="__main__":main()
