#!/usr/bin/env python3
import argparse, importlib.util, json, math
from pathlib import Path
import networkx as nx

HERE = Path(__file__).resolve().parent
BASE_PATH = HERE / "coalition_seeded_start_predictor_confirm_v1_runner.py"
spec = importlib.util.spec_from_file_location("seed_gate_base", BASE_PATH)
base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)

# Pre-outcome reproducibility/performance repair for the v2 holdout:
# - Raw truth bitsets are assignment-indexed and therefore not invariant under
#   variable relabeling. Hamming rank is invariant.
# - Search candidates only need live/allocated/rank; exhaustive truth checking
#   on every candidate is unnecessary and prohibitively expensive at n=16.
# - Every completed policy endpoint is checked against an exhaustive direct
#   truth oracle in that endpoint order's own relabeled coordinates, and its
#   Hamming rank is checked against the natural-order rank oracle.
_MASK_CACHE = {}
def _masks(n):
    if n in _MASK_CACHE:
        return _MASK_CACHE[n]
    total=1<<n; universe=(1<<total)-1; masks=[]
    for v in range(n):
        block=1<<v; period=block<<1; m=0; ones=(1<<block)-1
        for start in range(block,total,period):
            m |= ones<<start
        masks.append(m)
    _MASK_CACHE[n]=(universe,masks)
    return universe,masks

def _build_bdd(g, order):
    edges=base.relabeled_edges(g,order); mgr=base.ROBDD(g.number_of_nodes()); forest=[mgr.clause2(a,b) for a,b in edges]
    if not forest:
        root=1
    else:
        while len(forest)>1:
            nxt=[]
            for i in range(0,len(forest),2):
                nxt.append(forest[i] if i+1==len(forest) else mgr.and_(forest[i],forest[i+1]))
            forest=nxt
        root=forest[0]
    return mgr,root,edges

def _compile_fast(g, order, oracle_rank=None):
    mgr,root,_=_build_bdd(g,order)
    rank=mgr.rank(root)
    if oracle_rank is not None and rank!=oracle_rank:
        raise AssertionError("Hamming-rank oracle mismatch")
    return {"live":mgr.reachable(root),"allocated":len(mgr.nodes)-2,"rank":rank}

def _bdd_truth(mgr,root):
    universe,masks=_masks(mgr.n); cache={0:0,1:universe}
    def rec(u):
        if u in cache: return cache[u]
        var,lo,hi=mgr.nodes[u]; vm=masks[var]
        out=(rec(lo)&(universe^vm)) | (rec(hi)&vm)
        cache[u]=out; return out
    return rec(root)

def _verify_endpoint(g,order,oracle_rank):
    mgr,root,edges=_build_bdd(g,order)
    if mgr.rank(root)!=oracle_rank:
        raise AssertionError("endpoint Hamming-rank oracle mismatch")
    universe,masks=_masks(g.number_of_nodes()); direct=universe
    for a,b in edges: direct &= masks[a] | masks[b]
    if _bdd_truth(mgr,root)!=direct:
        raise AssertionError("endpoint direct truth-bitset oracle mismatch")
    return True

def _local_stage(g,order,oracle_rank):
    cur=_compile_fast(g,order,oracle_rank); compiles=1; best=None; current_width=base.vsw(g,order)
    for cand in base.neighbors(order):
        if base.vsw(g,cand)>current_width+1: continue
        r=_compile_fast(g,cand,oracle_rank); compiles+=1; key=(r["live"],r["allocated"],cand)
        if best is None or key<best[0]: best=(key,cand,r)
    if best and best[2]["live"]<cur["live"]: return best[1],best[2],compiles,True
    return order,cur,compiles,False

def _stage_arm(g,start,oracle_rank):
    o,r,c,ok=_local_stage(g,start,oracle_rank); return (o,r,c,1 if ok else 0)

def _run_arm(g,start,oracle_rank,max_moves=2,prestage=None):
    if prestage is None:
        order=start; total=0; accepted=0; current=None
        while accepted<max_moves:
            order,current,c,ok=_local_stage(g,order,oracle_rank); total+=c
            if not ok: break
            accepted+=1
        if current is None:
            current=_compile_fast(g,order,oracle_rank); total+=1
        return order,current,total,accepted
    order,current,total,accepted=prestage
    while accepted<max_moves:
        order,current,c,ok=_local_stage(g,order,oracle_rank); total+=c
        if not ok: break
        accepted+=1
    return order,current,total,accepted

def _commit_policy(g,arms,oracle_rank):
    staged={k:_stage_arm(g,v,oracle_rank) for k,v in arms.items()}; priority={"rcm":0,"natural":1,"seeded":2}
    winner=min(staged,key=lambda k:(staged[k][1]["live"],staged[k][2],priority[k]))
    order,r,total,acc=_run_arm(g,arms[winner],oracle_rank,2,staged[winner]); total += sum(staged[k][2] for k in staged if k!=winner)
    return {"live":r["live"],"compiles":total,"winner":winner,"order":order},staged

FAMILY_ORDER=("cubic","quartic","watts","erdos")
DEFAULT_CASES={
    "cubic":[884000,884001,884002,884003,884004,884005],
    "quartic":[884100,884101,884102,884103,884104,884105],
    "watts":[884200,884201,884202,884203,884204,884205],
    "erdos":[884300,884301,884302,884303,884304,884305],
}

def make_graph(family,seed):
    n=16
    if family=="cubic": g=nx.random_regular_graph(3,n,seed=seed)
    elif family=="quartic": g=nx.random_regular_graph(4,n,seed=seed)
    elif family=="watts": g=nx.watts_strogatz_graph(n,4,0.2,seed=seed)
    elif family=="erdos": g=nx.erdos_renyi_graph(n,0.25,seed=seed)
    else: raise ValueError(f"unknown family {family}")
    return nx.Graph(g)

def run_case(family,seed):
    g=make_graph(family,seed); natural=sorted(g.nodes()); rcm=list(nx.utils.reverse_cuthill_mckee_ordering(g)); seeded,sw,kd=base.seeded_order(g,seed,natural,rcm)
    oracle_rank=_compile_fast(g,natural)["rank"]
    two,_=_commit_policy(g,{"rcm":rcm,"natural":natural},oracle_rank)
    three,st3=_commit_policy(g,{"rcm":rcm,"natural":natural,"seeded":seeded},oracle_rank)
    _verify_endpoint(g,two["order"],oracle_rank); _verify_endpoint(g,three["order"],oracle_rank)
    stage_live=[st3["natural"][1]["live"],st3["rcm"][1]["live"],st3["seeded"][1]["live"]]
    label=int(stage_live[2]<stage_live[0] and stage_live[2]<stage_live[1]); x=base.graph_features(g,natural,rcm,seeded,sw,kd); p=base.probability(x); pred=int(p>=0.5); width_open=int(sw<=min(base.vsw(g,natural),base.vsw(g,rcm))+1)
    learned=three if pred else two; width=three if width_open else two
    return {"family":family,"seed":seed,"label":label,"prob":p,"pred":pred,"width_gate_open":bool(width_open),"widths":[base.vsw(g,natural),base.vsw(g,rcm),sw],"seeded_min_kendall":kd,"stage_live":stage_live,"two":[two["live"],two["compiles"]],"three":[three["live"],three["compiles"]],"learned":[learned["live"],learned["compiles"]],"width_plus1":[width["live"],width["compiles"]],"learned_regret":learned["live"]-three["live"],"width_regret":width["live"]-three["live"],"two_regret":two["live"]-three["live"],"oracle_ok":True}

def confusion(records,pred_key="pred"):
    tn=fp=fn=tp=0
    for r in records:
        y=r["label"]; p=int(r[pred_key])
        if y==0 and p==0: tn+=1
        elif y==0 and p==1: fp+=1
        elif y==1 and p==0: fn+=1
        else: tp+=1
    return [[tn,fp],[fn,tp]]

def auroc(records):
    pos=[r["prob"] for r in records if r["label"]==1]; neg=[r["prob"] for r in records if r["label"]==0]
    if not pos or not neg: return None
    wins=0.0
    for p in pos:
        for n in neg: wins += 1.0 if p>n else 0.5 if p==n else 0.0
    return wins/(len(pos)*len(neg))

def aggregate(records):
    three_comp=sum(r["three"][1] for r in records); learned_comp=sum(r["learned"][1] for r in records); width_comp=sum(r["width_plus1"][1] for r in records); two_comp=sum(r["two"][1] for r in records)
    def red(x): return 100.0*(three_comp-x)/three_comp if three_comp else 0.0
    return {"count":len(records),"positive_count":sum(r["label"] for r in records),"learned_open_count":sum(r["pred"] for r in records),"learned_open_rate":sum(r["pred"] for r in records)/len(records),"prob_min":min(r["prob"] for r in records),"prob_max":max(r["prob"] for r in records),"prob_mean":sum(r["prob"] for r in records)/len(records),"confusion":confusion(records),"auroc":auroc(records),"always_three":{"compiles":three_comp,"live_sum":sum(r["three"][0] for r in records)},"learned_gate":{"compiles":learned_comp,"compile_reduction_pct":red(learned_comp),"live_sum":sum(r["learned"][0] for r in records),"regret_sum":sum(r["learned_regret"] for r in records),"max_regret":max(r["learned_regret"] for r in records)},"width_plus1":{"compiles":width_comp,"compile_reduction_pct":red(width_comp),"live_sum":sum(r["width_plus1"][0] for r in records),"regret_sum":sum(r["width_regret"] for r in records),"max_regret":max(r["width_regret"] for r in records)},"two_arm":{"compiles":two_comp,"compile_reduction_pct":red(two_comp),"live_sum":sum(r["two"][0] for r in records),"regret_sum":sum(r["two_regret"] for r in records),"max_regret":max(r["two_regret"] for r in records)}}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--family",choices=FAMILY_ORDER); ap.add_argument("--seeds",nargs="+",type=int); args=ap.parse_args()
    if args.family: cases=[(args.family,s) for s in (args.seeds or DEFAULT_CASES[args.family])]
    else:
        if args.seeds: raise SystemExit("--seeds requires --family")
        cases=[(f,s) for f in FAMILY_ORDER for s in DEFAULT_CASES[f]]
    records=[run_case(f,s) for f,s in cases]
    out={"schema":"coalition_seeded_start_multifamily_transfer_v2_results","protocol":"coalition_seeded_start_multifamily_transfer_v2_protocol.json","oracle_note":"Search candidates check invariant Hamming rank. Completed two-arm/three-arm endpoints additionally match an exhaustive direct truth bitset in their own relabeled coordinates.","records":records,"aggregate":aggregate(records),"family_aggregate":{f:aggregate([r for r in records if r["family"]==f]) for f in FAMILY_ORDER if any(r["family"]==f for r in records)}}
    print(json.dumps(out,indent=2,sort_keys=True))
if __name__=="__main__": main()
