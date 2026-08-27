#!/usr/bin/env python3
import argparse, importlib.util, json
from pathlib import Path
import networkx as nx

HERE=Path(__file__).resolve().parent
BASE_PATH=HERE/"coalition_seeded_start_multifamily_transfer_v2_runner.py"
spec=importlib.util.spec_from_file_location("v2",BASE_PATH)
v2=importlib.util.module_from_spec(spec); spec.loader.exec_module(v2)
base=v2.base

FAMILY_ORDER=("cubic","quartic","watts","erdos")
DEFAULT_CASES={
  "cubic":[885000,885001,885002,885003,885004,885005],
  "quartic":[885100,885101,885102,885103,885104,885105],
  "watts":[885200,885201,885202,885203,885204,885205],
  "erdos":[885300,885301,885302,885303,885304,885305],
}

def make_graph(family,seed):
    n=18
    if family=="cubic": g=nx.random_regular_graph(3,n,seed=seed)
    elif family=="quartic": g=nx.random_regular_graph(4,n,seed=seed)
    elif family=="watts": g=nx.watts_strogatz_graph(n,4,0.2,seed=seed)
    elif family=="erdos": g=nx.erdos_renyi_graph(n,0.25,seed=seed)
    else: raise ValueError(f"unknown family {family}")
    return nx.Graph(g)

def partial_seed(g,start,oracle_rank,budget=32):
    cur=v2._compile_fast(g,start,oracle_rank); comp=1; width=base.vsw(g,start)
    best_key=(cur["live"],cur["allocated"],start); best_order=start; best_res=cur; eligible=[]
    for cand in base.neighbors(start):
        if base.vsw(g,cand)<=width+1: eligible.append(cand)
    count=min(budget,len(eligible))
    for cand in eligible[:count]:
        r=v2._compile_fast(g,cand,oracle_rank); comp+=1; key=(r["live"],r["allocated"],cand)
        if key<best_key: best_key,best_order,best_res=key,cand,r
    return {"cur":cur,"best_order":best_order,"best_res":best_res,"compiles":comp,"probe_count":count,"remaining":eligible[count:]}

def complete_seed(g,state,oracle_rank):
    best_key=(state["best_res"]["live"],state["best_res"]["allocated"],state["best_order"]); best_order=state["best_order"]; best_res=state["best_res"]; comp=state["compiles"]
    for cand in state["remaining"]:
        r=v2._compile_fast(g,cand,oracle_rank); comp+=1; key=(r["live"],r["allocated"],cand)
        if key<best_key: best_key,best_order,best_res=key,cand,r
    return (best_order,best_res,comp,1 if best_res["live"]<state["cur"]["live"] else 0)

def probe_policy(g,natural,rcm,seeded,oracle_rank,budget=32):
    staged_conv={"rcm":v2._stage_arm(g,rcm,oracle_rank),"natural":v2._stage_arm(g,natural,oracle_rank)}
    conv_winner=min(staged_conv,key=lambda k:(staged_conv[k][1]["live"],staged_conv[k][2],{"rcm":0,"natural":1}[k])); conv_live=staged_conv[conv_winner][1]["live"]
    ps=partial_seed(g,seeded,oracle_rank,budget); triggered=ps["best_res"]["live"]<conv_live
    if triggered: seeded_stage=complete_seed(g,ps,oracle_rank)
    else: seeded_stage=(ps["best_order"],ps["best_res"],ps["compiles"],1 if ps["best_res"]["live"]<ps["cur"]["live"] else 0)
    staged={**staged_conv,"seeded":seeded_stage}; priority={"rcm":0,"natural":1,"seeded":2}; starts={"rcm":rcm,"natural":natural,"seeded":seeded}
    winner=min(staged,key=lambda k:(staged[k][1]["live"],staged[k][2],priority[k])); order,r,total,acc=v2._run_arm(g,starts[winner],oracle_rank,2,staged[winner]); total+=sum(staged[k][2] for k in staged if k!=winner)
    v2._verify_endpoint(g,order,oracle_rank)
    return {"live":r["live"],"compiles":total,"winner":winner,"triggered":triggered,"probe_live":ps["best_res"]["live"],"conventional_stage_live":conv_live,"probe_count":ps["probe_count"],"order":order}

def run_case(family,seed):
    g=make_graph(family,seed); natural=sorted(g.nodes()); rcm=list(nx.utils.reverse_cuthill_mckee_ordering(g)); seeded,sw,kd=base.seeded_order(g,seed,natural,rcm); oracle_rank=v2._compile_fast(g,natural)["rank"]
    two,_=v2._commit_policy(g,{"rcm":rcm,"natural":natural},oracle_rank); three,st3=v2._commit_policy(g,{"rcm":rcm,"natural":natural,"seeded":seeded},oracle_rank); probe=probe_policy(g,natural,rcm,seeded,oracle_rank,32)
    v2._verify_endpoint(g,two["order"],oracle_rank); v2._verify_endpoint(g,three["order"],oracle_rank)
    q=min(two["live"],three["live"]); benefit=three["live"]<two["live"]; harm=three["live"]>two["live"]
    return {"family":family,"seed":seed,"widths":[base.vsw(g,natural),base.vsw(g,rcm),sw],"seeded_min_kendall":kd,"two":[two["live"],two["compiles"]],"three":[three["live"],three["compiles"]],"probe":[probe["live"],probe["compiles"]],"probe_triggered":probe["triggered"],"probe_live":probe["probe_live"],"conventional_stage_live":probe["conventional_stage_live"],"quality_oracle":q,"probe_regret":probe["live"]-q,"seeded_final_benefit":benefit,"seeded_final_harm":harm,"oracle_ok":true}

def aggregate(records):
    three_comp=sum(r["three"][1] for r in records); probe_comp=sum(r["probe"][1] for r in records); two_comp=sum(r["two"][1] for r in records); qsum=sum(r["quality_oracle"] for r in records); plive=sum(r["probe"][0] for r in records)
    return {"count":len(records),"trigger_count":sum(r["probe_triggered"] for r in records),"trigger_rate":sum(r["probe_triggered"] for r in records)/len(records),"seeded_benefit_count":sum(r["seeded_final_benefit"] for r in records),"seeded_harm_count":sum(r["seeded_final_harm"] for r in records),"always_three":{"compiles":three_comp,"live_sum":sum(r["three"][0] for r in records)},"two_arm":{"compiles":two_comp,"live_sum":sum(r["two"][0] for r in records)},"quality_oracle_live_sum":qsum,"probe_complete":{"compiles":probe_comp,"compile_reduction_pct":100.0*(three_comp-probe_comp)/three_comp,"live_sum":plive,"regret_sum":plive-qsum,"max_regret":max(r["probe_regret"] for r in records),"positive_regret_cases":[{"family":r["family"],"seed":r["seed"],"regret":r["probe_regret"]} for r in records if r["probe_regret"]>0]},"benefit_retention":[{"family":r["family"],"seed":r["seed"],"triggered":r["probe_triggered"],"probe_regret":r["probe_regret"],"two_live":r["two"][0],"three_live":r["three"][0],"probe_live":r["probe"][0]} for r in records if r["seeded_final_benefit"]],"harm_cases":[{"family":r["family"],"seed":r["seed"],"triggered":r["probe_triggered"],"two_live":r["two"][0],"three_live":r["three"][0],"probe_live":r["probe"][0]} for r in records if r["seeded_final_harm"]]}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--family",choices=FAMILY_ORDER); ap.add_argument("--seeds",nargs="+",type=int); args=ap.parse_args()
    if args.family: cases=[(args.family,s) for s in (args.seeds or DEFAULT_CASES[args.family])]
    else:
        if args.seeds: raise SystemExit("--seeds requires --family")
        cases=[(f,s) for f in FAMILY_ORDER for s in DEFAULT_CASES[f]]
    records=[run_case(f,s) for f,s in cases]
    out={"schema":"coalition_seeded_probe_complete_v0_results","protocol":"coalition_seeded_probe_complete_v0_protocol.json","records":records,"aggregate":aggregate(records),"family_aggregate":{f:aggregate([r for r in records if r["family"]==f]) for f in FAMILY_ORDER if any(r["family"]==f for r in records)}}
    print(json.dumps(out,indent=2,sort_keys=True))
if __name__=="__main__": main()
