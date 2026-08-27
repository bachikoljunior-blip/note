#!/usr/bin/env python3
import json, math, platform, random, statistics, sys, time
import networkx as nx

PROTOCOL_BLOB="4572296bdc1f9a285bc63a9155649167bd36eca6"
RANDOM_ORDER_SEED=880401; CLAUSE_SEED=880503; MAX_NODES=2_000_000; MAX_SECONDS=45.0
FAMILIES=[
 {"id":"path18","kind":"path_graph","n":18},
 {"id":"binary_tree15","kind":"balanced_binary_tree","n":15},
 {"id":"grid4x4","kind":"grid_2d","rows":4,"cols":4,"n":16},
 {"id":"cubic18_s880301","kind":"random_3_regular","n":18,"seed":880301},
 {"id":"cubic18_s880319","kind":"random_3_regular","n":18,"seed":880319},]
ORDERS=["natural","reverse_natural","reverse_cuthill_mckee","greedy_vertex_separation","best_of_16_seeded_random_by_vertex_separation"]
SCHEDULES=["lexicographic_incremental","seeded_random_incremental","balanced_pairwise"]

def stable_seed(text,base):
 h=base
 for ch in text.encode(): h=((h*131)^ch)&0xffffffff
 return h

def build_graph(s):
 if s["kind"]=="path_graph": return nx.path_graph(s["n"])
 if s["kind"]=="balanced_binary_tree": return nx.balanced_tree(2,3)
 if s["kind"]=="grid_2d":
  r=nx.grid_2d_graph(s["rows"],s["cols"]); return nx.relabel_nodes(r,{v:i for i,v in enumerate(sorted(r.nodes()))})
 if s["kind"]=="random_3_regular": return nx.random_regular_graph(3,s["n"],seed=s["seed"])
 raise ValueError(s)

def frontier_size(g,prefix):
 p=set(prefix); return sum(1 for u in p if any(v not in p for v in g.neighbors(u)))

def vsw(g,order):
 p=[]; best=0
 for v in order[:-1]: p.append(v); best=max(best,frontier_size(g,p))
 return best

def greedy_vs_order(g):
 rem=set(g.nodes()); p=[]
 while rem:
  _,_,v=min((frontier_size(g,p+[v]),g.degree[v],v) for v in sorted(rem)); p.append(v); rem.remove(v)
 return p

def order_for(g,fid,name):
 nodes=sorted(g.nodes())
 if name=="natural": return nodes
 if name=="reverse_natural": return nodes[::-1]
 if name=="reverse_cuthill_mckee": return list(nx.utils.reverse_cuthill_mckee_ordering(g))
 if name=="greedy_vertex_separation": return greedy_vs_order(g)
 if name=="best_of_16_seeded_random_by_vertex_separation":
  rng=random.Random(stable_seed(fid,RANDOM_ORDER_SEED)); cs=[]
  for _ in range(16):
   o=nodes[:]; rng.shuffle(o); cs.append((vsw(g,o),o))
  return min(cs,key=lambda x:(x[0],x[1]))[1]
 raise ValueError(name)

class GuardedOut(RuntimeError): pass
class ROBDD:
 def __init__(self,n):
  self.n=n; self.nodes=[None,None]; self.unique={}; self.apply_cache={}; self.clause_cache={}; self.rank_cache={}; self.truth_cache={0:0}
  self.apply_calls=0; self.apply_hits=0; self.start=time.perf_counter(); self.var_masks=None; self.universe=None
 def guard(self):
  if len(self.nodes)-2>MAX_NODES: raise GuardedOut("max_allocated_nodes")
  if time.perf_counter()-self.start>MAX_SECONDS: raise GuardedOut("max_compile_seconds")
 def varpos(self,u): return self.n if u<=1 else self.nodes[u][0]
 def mk(self,var,lo,hi):
  if lo==hi:return lo
  k=(var,lo,hi)
  if k in self.unique:return self.unique[k]
  self.guard(); u=len(self.nodes); self.nodes.append(k); self.unique[k]=u; return u
 def clause2(self,a,b):
  k=tuple(sorted((a,b)))
  if k in self.clause_cache:return self.clause_cache[k]
  x,y=k
  if x==y: out=self.mk(x,0,1)
  else: out=self.mk(x,self.mk(y,0,1),1)
  self.clause_cache[k]=out; return out
 def and_(self,u,v):
  self.apply_calls+=1
  if u==0 or v==0:return 0
  if u==1:return v
  if v==1:return u
  if u==v:return u
  if u>v:u,v=v,u
  k=(u,v)
  if k in self.apply_cache:self.apply_hits+=1; return self.apply_cache[k]
  self.guard(); p=min(self.varpos(u),self.varpos(v))
  if self.varpos(u)==p: _,ulo,uhi=self.nodes[u]
  else: ulo=uhi=u
  if self.varpos(v)==p: _,vlo,vhi=self.nodes[v]
  else: vlo=vhi=v
  out=self.mk(p,self.and_(ulo,vlo),self.and_(uhi,vhi)); self.apply_cache[k]=out; return out
 def reachable(self,roots):
  if isinstance(roots,int): roots=[roots]
  seen=set(); st=list(roots)
  while st:
   u=st.pop()
   if u<=1 or u in seen:continue
   seen.add(u); _,lo,hi=self.nodes[u]; st.extend((lo,hi))
  return len(seen)
 def _rank(self,u,level):
  k=(u,level)
  if k in self.rank_cache:return self.rank_cache[k]
  if u==0: out=(0,)*(self.n-level+1)
  elif u==1: out=tuple(math.comb(self.n-level,k) for k in range(self.n-level+1))
  else:
   var,lo,hi=self.nodes[u]; plo=self._rank(lo,var+1); phi=self._rank(hi,var+1); br=[0]*(self.n-var+1)
   for k,x in enumerate(plo): br[k]+=x
   for k,x in enumerate(phi): br[k+1]+=x
   gap=var-level
   if gap:
    acc=[0]*(self.n-level+1)
    for a in range(gap+1):
     ca=math.comb(gap,a)
     for b,cb in enumerate(br): acc[a+b]+=ca*cb
    out=tuple(acc)
   else: out=tuple(br)
  self.rank_cache[k]=out; return out
 def rank(self,r): return list(self._rank(r,0))
 def _ensure_masks(self):
  if self.var_masks is not None:return
  total=1<<self.n; self.universe=(1<<total)-1; masks=[]
  for v in range(self.n):
   block=1<<v; period=block<<1; m=0
   ones=(1<<block)-1
   for start in range(block,total,period): m |= ones<<start
   masks.append(m)
  self.var_masks=masks; self.truth_cache[1]=self.universe
 def truth_bits(self,u):
  self._ensure_masks()
  if u in self.truth_cache:return self.truth_cache[u]
  var,lo,hi=self.nodes[u]; vm=self.var_masks[var]
  out=(self.truth_bits(lo)&(self.universe^vm)) | (self.truth_bits(hi)&vm)
  self.truth_cache[u]=out; return out

def relabeled_edges(g,order):
 p={v:i for i,v in enumerate(order)}; return sorted(tuple(sorted((p[u],p[v]))) for u,v in g.edges())

def direct_truth_bits(n,edges):
 total=1<<n; universe=(1<<total)-1; masks=[]
 for v in range(n):
  block=1<<v; period=block<<1; m=0; ones=(1<<block)-1
  for start in range(block,total,period): m |= ones<<start
  masks.append(m)
 out=universe
 for a,b in edges: out &= masks[a] | masks[b]
 return out

def compile_cell(g,fid,oname,order,sched):
 edges=relabeled_edges(g,order); mgr=ROBDD(g.number_of_nodes()); peak=0; peakf=0; root=None; guard=None; t=time.perf_counter()
 try:
  if sched in ("lexicographic_incremental","seeded_random_incremental"):
   seq=edges[:]
   if sched=="seeded_random_incremental": random.Random(stable_seed(fid+":"+oname,CLAUSE_SEED)).shuffle(seq)
   root=1
   for a,b in seq: root=mgr.and_(root,mgr.clause2(a,b)); peak=max(peak,mgr.reachable(root))
  else:
   forest=[mgr.clause2(a,b) for a,b in edges]; peakf=mgr.reachable(forest) if forest else 0
   if not forest:root=1
   else:
    while len(forest)>1:
     nxt=[]
     for i in range(0,len(forest),2): nxt.append(forest[i] if i+1==len(forest) else mgr.and_(forest[i],forest[i+1]))
     forest=nxt; peakf=max(peakf,mgr.reachable(forest))
    root=forest[0]
 except GuardedOut as e: guard=str(e)
 row={"family":fid,"n":g.number_of_nodes(),"edges":g.number_of_edges(),"order":oname,"order_vertices":order,"order_vertex_separation_width":vsw(g,order),"schedule":sched,"guarded_out":guard,"compile_wall_clock_ms":1000*(time.perf_counter()-t),"apply_recursive_calls":mgr.apply_calls,"apply_cache_hits":mgr.apply_hits,"unique_node_allocations":len(mgr.nodes)-2,"final_allocated_nonterminal_nodes":len(mgr.nodes)-2,"peak_reachable_nodes_during_incremental_schedule":peak if sched!="balanced_pairwise" else None,"peak_forest_reachable_nodes":peakf if sched=="balanced_pairwise" else None}
 if guard or root is None:return row
 row["final_reachable_nonterminal_nodes"]=mgr.reachable(root); tr=time.perf_counter(); row["exact_rank_count_vector"]=mgr.rank(root); row["rank_count_wall_clock_ms"]=1000*(time.perf_counter()-tr); row["rank_cache_states"]=len(mgr.rank_cache)
 tc=time.perf_counter(); got=mgr.truth_bits(root); want=direct_truth_bits(g.number_of_nodes(),edges); row["truth_bitset_check_ms"]=1000*(time.perf_counter()-tc); row["assignment_checks"]=1<<g.number_of_nodes(); row["assignment_mismatches"]=0 if got==want else (got^want).bit_count()
 return row

def rankdata(xs):
 ix=sorted(enumerate(xs),key=lambda kv:kv[1]); r=[0.0]*len(xs); i=0
 while i<len(ix):
  j=i+1
  while j<len(ix) and ix[j][1]==ix[i][1]:j+=1
  z=(i+j-1)/2+1
  for k in range(i,j):r[ix[k][0]]=z
  i=j
 return r

def pearson(xs,ys):
 if len(xs)<2:return None
 mx,my=statistics.mean(xs),statistics.mean(ys); dx=[x-mx for x in xs]; dy=[y-my for y in ys]; den=math.sqrt(sum(x*x for x in dx)*sum(y*y for y in dy)); return None if den==0 else sum(a*b for a,b in zip(dx,dy))/den

def main():
 cells=[]; orders=[]; refs={}; rank_mis={}
 for s in FAMILIES:
  g=build_graph(s)
  for oname in ORDERS:
   o=order_for(g,s["id"],oname); orders.append({"family":s["id"],"order":oname,"vertex_separation_width":vsw(g,o),"vertices":o})
   for sched in SCHEDULES:
    r=compile_cell(g,s["id"],oname,o,sched); cells.append(r); q=r.get("exact_rank_count_vector")
    if q is not None:
     if s["id"] not in refs:refs[s["id"]]=q
     elif refs[s["id"]]!=q:rank_mis[s["id"]]=rank_mis.get(s["id"],0)+1
 valid=[r for r in cells if not r.get("guarded_out") and r.get("assignment_mismatches")==0]
 correctness={"guarded_cells":sum(bool(r.get("guarded_out")) for r in cells),"assignment_mismatch_cells":sum((r.get("assignment_mismatches") or 0)>0 for r in cells),"rank_vector_mismatch_families":rank_mis,"passed":not rank_mis and all((r.get("assignment_mismatches") or 0)==0 for r in cells if not r.get("guarded_out"))}
 canon=[r for r in valid if r["schedule"]=="balanced_pairwise"]; widths=[r["order_vertex_separation_width"] for r in canon]; lnodes=[math.log2(max(1,r["final_reachable_nonterminal_nodes"])) for r in canon]; rho=pearson(rankdata(widths),rankdata(lnodes)) if canon else None
 by={}
 for r in valid:by.setdefault((r["family"],r["order"]),{})[r["schedule"]]=r
 ratios=[]
 for k,d in by.items():
  if all(s in d for s in SCHEDULES):
   lex,rand,bal=d[SCHEDULES[0]],d[SCHEDULES[1]],d[SCHEDULES[2]]; ratios.append({"family":k[0],"order":k[1],"balanced_vs_lex_allocated_ratio":bal["final_allocated_nonterminal_nodes"]/max(1,lex["final_allocated_nonterminal_nodes"]),"random_vs_lex_allocated_ratio":rand["final_allocated_nonterminal_nodes"]/max(1,lex["final_allocated_nonterminal_nodes"]),"balanced_vs_lex_apply_calls_ratio":bal["apply_recursive_calls"]/max(1,lex["apply_recursive_calls"]),"random_vs_lex_apply_calls_ratio":rand["apply_recursive_calls"]/max(1,lex["apply_recursive_calls"]),"final_live_nodes_equal":len({lex["final_reachable_nonterminal_nodes"],rand["final_reachable_nonterminal_nodes"],bal["final_reachable_nonterminal_nodes"]})==1})
 fam={}
 for s in FAMILIES:
  rr=[r for r in valid if r["family"]==s["id"] and r["schedule"]=="balanced_pairwise"]
  if rr:fam[s["id"]]={"n":rr[0]["n"],"edges":rr[0]["edges"],"min_vertex_separation_width":min(r["order_vertex_separation_width"] for r in rr),"max_vertex_separation_width":max(r["order_vertex_separation_width"] for r in rr),"min_final_live_nodes":min(r["final_reachable_nonterminal_nodes"] for r in rr),"max_final_live_nodes":max(r["final_reachable_nonterminal_nodes"] for r in rr),"best_order_by_final_live_nodes":min(rr,key=lambda r:(r["final_reachable_nonterminal_nodes"],r["order"]))["order"]}
 out={"schema":"coalition_boundary_width_pathology_v0_results","protocol_blob":PROTOCOL_BLOB,"environment":{"python":sys.version.split()[0],"platform":platform.platform(),"networkx":nx.__version__},"correctness":correctness,"aggregate":{"cells":len(cells),"valid_cells":len(valid),"spearman_vertex_separation_vs_log2_final_live_nodes":rho,"median_balanced_vs_lex_allocated_ratio":statistics.median(x["balanced_vs_lex_allocated_ratio"] for x in ratios) if ratios else None,"median_balanced_vs_lex_apply_calls_ratio":statistics.median(x["balanced_vs_lex_apply_calls_ratio"] for x in ratios) if ratios else None,"all_schedule_final_live_nodes_equal":all(x["final_live_nodes_equal"] for x in ratios)},"family_summary":fam,"orders":orders,"schedule_ratios":ratios,"cells":cells,"scope":"Exact only for the preregistered positive monotone 2-CNF graph instances and tested fixed orders/schedules. Random cubic graphs are not certified expanders. Timing/allocation are implementation/environment specific. This v0 does not implement CUDD dynamic reordering or an alternative TDD/d-DNNF representation."}
 print(json.dumps(out,indent=2,sort_keys=True))
if __name__=="__main__":main()
