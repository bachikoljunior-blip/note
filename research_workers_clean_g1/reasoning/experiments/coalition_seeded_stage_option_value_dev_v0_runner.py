#!/usr/bin/env python3
import importlib.util, json
from pathlib import Path
import networkx as nx

HERE=Path(__file__).resolve().parent
BASE_PATH=HERE/"coalition_seeded_start_multifamily_transfer_v2_runner.py"
spec=importlib.util.spec_from_file_location("stage_base",BASE_PATH)
base=importlib.util.module_from_spec(spec); spec.loader.exec_module(base)

FAMILIES=("cubic","quartic","watts","erdos")

def make_graph(n,family,seed):
    if family=="cubic": g=nx.random_regular_graph(3,n,seed=seed)
    elif family=="quartic": g=nx.random_regular_graph(4,n,seed=seed)
    elif family=="watts": g=nx.watts_strogatz_graph(n,4,0.2,seed=seed)
    elif family=="erdos": g=nx.erdos_renyi_graph(n,0.25,seed=seed)
    else: raise ValueError(family)
    return nx.Graph(g)

def stage_arm(g,start,oracle):
    cur=base._compile_fast(g,start,oracle); width=base.base.vsw(g,start)
    best=(cur["live"],cur["allocated"],start,cur); c=1
    for cand in base.base.neighbors(start):
        if base.base.vsw(g,cand)>width+1: continue
        r=base._compile_fast(g,cand,oracle); c+=1
        if (r["live"],r["allocated"],cand)<best[:3]: best=(r["live"],r["allocated"],cand,r)
    if best[0]<cur["live"]: return best[2],best[3],c,1
    return start,cur,c,0

def run_arm(g,start,oracle,pre):
    order,current,total,accepted=pre
    while accepted<2:
        order,current,c,ok=stage_arm(g,order,oracle); total+=c
        if not ok: break
        accepted+=1
    return order,current,total,accepted

def challenger(n,family,seed):
    g=make_graph(n,family,seed); natural=sorted(g.nodes()); rcm=list(nx.utils.reverse_cuthill_mckee_ordering(g))
    seeded,sw,kd=base.base.seeded_order(g,seed,natural,rcm); oracle=base._compile_fast(g,natural)["rank"]
    ns=stage_arm(g,natural,oracle); rs=stage_arm(g,rcm,oracle)
    wname,wst=min((("rcm",rs),("natural",ns)),key=lambda kv:(kv[1][1]["live"],kv[1][2],0 if kv[0]=="rcm" else 1))
    two_start=rcm if wname=="rcm" else natural
    two_order,two_res,two_wcost,_=run_arm(g,two_start,oracle,wst)
    two_cost=two_wcost+(ns[2] if wname=="rcm" else rs[2]); incumbent=two_res["live"]
    base._verify_endpoint(g,two_order,oracle)

    events=[]; idx=0; init=base._compile_fast(g,seeded,oracle); idx+=1
    best_seen=init["live"]; best_event_idx=idx; best_order=seeded
    events.append({"idx":idx,"stage":0,"live":init["live"],"best":best_seen})
    first_cert=idx if init["live"]<incumbent else None
    order=seeded; accepted=0; stage_bounds=[]
    while accepted<2:
        cur=base._compile_fast(g,order,oracle); idx+=1
        if cur["live"]<best_seen: best_seen=cur["live"]; best_event_idx=idx; best_order=order
        if first_cert is None and cur["live"]<incumbent: first_cert=idx
        width=base.base.vsw(g,order)
        events.append({"idx":idx,"stage":accepted+1,"live":cur["live"],"best":best_seen})
        best=(cur["live"],cur["allocated"],order,cur)
        elig=[cand for cand in base.base.neighbors(order) if base.base.vsw(g,cand)<=width+1]
        stage_start=idx-1
        for ci,cand in enumerate(elig,1):
            r=base._compile_fast(g,cand,oracle); idx+=1
            if (r["live"],r["allocated"],cand)<best[:3]: best=(r["live"],r["allocated"],cand,r)
            if r["live"]<best_seen: best_seen=r["live"]; best_event_idx=idx; best_order=cand
            if first_cert is None and r["live"]<incumbent: first_cert=idx
            events.append({"idx":idx,"stage":accepted+1,"stage_candidate":ci,"stage_eligible":len(elig),"live":r["live"],"best":best_seen,"remaining_stage":len(elig)-ci})
        stage_bounds.append((stage_start,idx,len(elig),best[0],cur["live"]))
        if best[0]<cur["live"]: order=best[2]; accepted+=1
        else: break
    base._verify_endpoint(g,best_order,oracle)
    return {"n":n,"family":family,"seed":seed,"two_live":incumbent,"two_cost":two_cost,"events":events,"first_cert":first_cert,"total_challenger":idx,"exhaustive_best":best_seen,"gain":max(0,incumbent-best_seen),"best_event_idx":best_event_idx,"stage_bounds":stage_bounds,"seed_start_live":init["live"],"sw":sw,"kd":kd}

def summarize(n,family,seed):
    r=challenger(n,family,seed); inc=r["two_live"]
    ev65=next((e for e in r["events"] if e["idx"]==65),r["events"][-1]); best65=ev65["best"]
    cert65=best65<inc; gap65=best65-inc; remains=r["total_challenger"]>ev65["idx"]
    v1_stop=bool(remains and not cert65 and gap65>11)
    s1=r["stage_bounds"][0]; s1end=s1[1]; s1live=s1[3]
    s1gain=max(0,inc-s1live); stage2=len(r["stage_bounds"])>1
    first_gain=0
    if r["first_cert"] is not None:
        first_gain=inc-next(e["best"] for e in r["events"] if e["idx"]==r["first_cert"])
    return {"n":n,"family":family,"seed":seed,"incumbent_live":inc,"challenger_live_at_65":best65,"gap65":gap65,"v1_stop_region":v1_stop,"stage1_end_compile":s1end,"stage1_end_live":s1live,"stage1_self_improvement":s1live<r["seed_start_live"],"stage1_immediate_incumbent_gain":s1gain,"stage1_remaining_cost_from_65":max(0,s1end-65),"stage2_exists":stage2,"first_incumbent_certificate_compile":r["first_cert"],"first_incumbent_certificate_gain":first_gain,"final_challenger_compile":r["total_challenger"],"final_challenger_live":r["exhaustive_best"],"exhaustive_gain":r["gain"],"gateway_positive":bool(r["gain"]>0 and s1gain==0 and stage2),"seed_start_live":r["seed_start_live"],"best_event_idx":r["best_event_idx"],"stage_bounds":r["stage_bounds"]}

def cases():
    for n,base_seed in ((16,916000),(18,917000)):
        for j,f in enumerate(FAMILIES):
            for seed in range(base_seed+100*j,base_seed+100*j+20): yield n,f,seed

def aggregate(rows):
    stop=[r for r in rows if r["v1_stop_region"]]; pos=[r for r in stop if r["exhaustive_gain"]>0]; gate=[r for r in stop if r["gateway_positive"]]
    tail=sum(max(0,r["final_challenger_compile"]-65) for r in stop); s1=sum(r["stage1_remaining_cost_from_65"] for r in stop)
    return {"total_cases":len(rows),"stop_region_count":len(stop),"stop_region_positive_count":len(pos),"stop_region_total_gain":sum(r["exhaustive_gain"] for r in pos),"gateway_positive_count":len(gate),"gateway_gain":sum(r["exhaustive_gain"] for r in gate),"gateway_positive_fraction_of_positives":len(gate)/len(pos) if pos else None,"gateway_gain_fraction":sum(r["exhaustive_gain"] for r in gate)/sum(r["exhaustive_gain"] for r in pos) if pos else None,"stage1_immediate_positive_count":sum(r["stage1_immediate_incumbent_gain"]>0 for r in pos),"first_cert_stage1_count":sum(r["first_incumbent_certificate_compile"]<=r["stage1_end_compile"] for r in pos),"first_cert_stage2_count":sum(r["first_incumbent_certificate_compile"]>r["stage1_end_compile"] for r in pos),"stage1_remaining_cost_total":s1,"full_tail_cost_total":tail,"finish_stage1_cost_fraction_of_full_tail":s1/tail if tail else None}

def main():
    rows=[summarize(*c) for c in cases()]
    out={"schema":"coalition_seeded_stage_option_value_dev_v0_full_results","protocol":"coalition_seeded_stage_option_value_dev_v0_protocol.json","aggregate":aggregate(rows),"records":rows}
    print(json.dumps(out,indent=2,sort_keys=True))

if __name__=="__main__": main()
