#!/usr/bin/env python3
"""Deterministic synthetic held-out provenance rollback router comparison.

Generated under frozen clean multi_agent control tuple:
note main 72c4b5abe2678e96c79ae2feae09cd0b02d97552
control revision 11, config revision 6.
"""
import hashlib, itertools, json
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression, LinearRegression

GRID = {
    "fanout":[2,3,4], "depth":[2,3,4],
    "r_observed":[0.8,0.9], "r_static":[0.85,0.95],
    "static_fp":[0.02,0.10], "overlap_u":[0.10,0.35,0.65,0.90],
    "independent_ratio":[0.25,1.0],
}
RUNS_PER_CONTEXT=100
COST_FEATURES=["fanout","depth","static_fp","independent_ratio","r_observed","r_static"]

def make_contexts():
    out=[]
    for f,d,ro,rs,fp,u,ir in itertools.product(
        GRID["fanout"],GRID["depth"],GRID["r_observed"],GRID["r_static"],
        GRID["static_fp"],GRID["overlap_u"],GRID["independent_ratio"]):
        qmin=max(0.0,(rs-ro)/(1-ro)); qmax=min(1.0,rs/(1-ro))
        q=qmin+u*(qmax-qmin); p=(rs-(1-ro)*q)/ro
        par={"depth":d,"fanout":f,"independent_ratio":ir,"overlap_u":u,
             "p_static_given_observed_hit":round(p,12),
             "q_static_given_observed_miss":round(q,12),
             "r_observed":ro,"r_static":rs,"static_fp":fp}
        canon=json.dumps(par,sort_keys=True,separators=(",",":"))
        cid=hashlib.sha256(canon.encode()).hexdigest()[:16]
        split="train" if f in {2,3} and d in {2,3} and u in {0.35,0.65} else "test"
        out.append({**par,"context_id":cid,"split":split})
    assert len(out)==576 and sum(x["split"]=="train" for x in out)==128
    return out

def simulate(c):
    f,d=c["fanout"],c["depth"]; ro=c["r_observed"]; rs=c["r_static"]
    fp=c["static_fp"]; q=c["q_static_given_observed_miss"]; p=c["p_static_given_observed_hit"]
    ir=c["independent_ratio"]; n_aff=sum(f**i for i in range(1,d+1))
    n_ind=max(1,int(round(n_aff*ir))); rows=[]
    for r in range(RUNS_PER_CONTEXT):
        seed=int(hashlib.sha256(f'{c["context_id"]}|{r}'.encode()).hexdigest()[:16],16)%(2**63-1)
        rng=np.random.default_rng(seed); crit=rng.integers(0,f,size=d)
        parent_reach=np.array([True]); critical_reach=True; reachable=0
        for level in range(1,d+1):
            npar=len(parent_reach)
            obs=rng.random(npar*f)<ro
            stat=rng.random(npar*f)<np.where(obs,p,q)
            child=np.repeat(parent_reach,f)&(obs|stat)
            reachable+=int(child.sum())
            idx=0
            for j in range(level): idx=idx*f+int(crit[j])
            if not child[idx]: critical_reach=False
            parent_reach=child
        fp_ind=int((rng.random(n_ind)<fp).sum())
        rows.append({
            "context_id":c["context_id"],"split":c["split"],"fanout":f,"depth":d,
            "r_observed":ro,"r_static":rs,"static_fp":fp,"overlap_u":c["overlap_u"],
            "q":q,"p":p,"independent_ratio":ir,"union_success":int(critical_reach),
            "union_calls":1+reachable+fp_ind,"whole_calls":1+n_aff+n_ind,"run":r})
    return rows

def feature(frame,joint):
    ru=(1-(1-frame.r_observed)*(1-frame.q)) if joint else (1-(1-frame.r_observed)*(1-frame.r_static))
    return (frame.depth*np.log(np.clip(ru,1e-9,1))).to_numpy().reshape(-1,1)

def router_metrics(frame,prob,pred_cost,threshold):
    pred_cost=np.clip(pred_cost,1,None); whole=frame.whole_calls.to_numpy()
    score=prob*whole/pred_cost; choose=score>=threshold
    succ=np.where(choose,frame.union_success.to_numpy(),1)
    calls=np.where(choose,frame.union_calls.to_numpy(),whole)
    return {"choose_union_rate":float(choose.mean()),"fail_rate":float(1-succ.mean()),
            "mean_calls":float(calls.mean()),"correct_per_100k":float(succ.sum()/calls.sum()*100000),
            "score":score,"choose":choose}

def tune(frame,prob,pred_cost,max_fail=.01):
    ratio=prob*frame.whole_calls.to_numpy()/np.clip(pred_cost,1,None)
    cand=np.unique(np.quantile(ratio,np.linspace(0,1,501))); best=None
    for t in cand:
        m=router_metrics(frame,prob,pred_cost,t)
        if m["fail_rate"]<=max_fail and (best is None or m["correct_per_100k"]>best["correct_per_100k"]):
            best={**m,"threshold":float(t)}
    return best

def fixed_rate(frame,score,rate):
    n=len(frame); k=int(round(n*rate)); idx=np.argsort(score)[::-1]
    choose=np.zeros(n,dtype=bool); choose[idx[:k]]=True
    succ=np.where(choose,frame.union_success.to_numpy(),1)
    calls=np.where(choose,frame.union_calls.to_numpy(),frame.whole_calls.to_numpy())
    return {"union_rate":float(choose.mean()),"fail_rate":float(1-succ.mean()),
            "mean_calls":float(calls.mean()),"correct_per_100k":float(succ.sum()/calls.sum()*100000)}

def main():
    rows=[]
    for c in make_contexts(): rows.extend(simulate(c))
    df=pd.DataFrame(rows); train=df[df.split=="train"].reset_index(drop=True); test=df[df.split=="test"].reset_index(drop=True)
    marginal=LogisticRegression(max_iter=1000).fit(feature(train,False),train.union_success)
    joint=LogisticRegression(max_iter=1000).fit(feature(train,True),train.union_success)
    cost=LinearRegression().fit(train[COST_FEATURES],train.union_calls)
    pc_train=cost.predict(train[COST_FEATURES]); pc_test=cost.predict(test[COST_FEATURES])
    pm_train=marginal.predict_proba(feature(train,False))[:,1]; pj_train=joint.predict_proba(feature(train,True))[:,1]
    bm=tune(train,pm_train,pc_train); bj=tune(train,pj_train,pc_train)
    pm=marginal.predict_proba(feature(test,False))[:,1]; pj=joint.predict_proba(feature(test,True))[:,1]
    mt=router_metrics(test,pm,pc_test,bm["threshold"]); jt=router_metrics(test,pj,pc_test,bj["threshold"])
    out={"contexts":576,"runs":len(df),"train_runs":len(train),"test_runs":len(test),
         "train_thresholds":{"marginal":bm["threshold"],"joint":bj["threshold"]},
         "heldout":{"marginal":{k:mt[k] for k in ["choose_union_rate","fail_rate","mean_calls","correct_per_100k"]},
                    "joint":{k:jt[k] for k in ["choose_union_rate","fail_rate","mean_calls","correct_per_100k"]}},
         "fixed_union_fraction":{}}
    score_m=pm*test.whole_calls.to_numpy()/np.clip(pc_test,1,None)
    score_j=pj*test.whole_calls.to_numpy()/np.clip(pc_test,1,None)
    for rate in [.05,.10,.15,.20,.30]:
        out["fixed_union_fraction"][str(rate)]={"marginal":fixed_rate(test,score_m,rate),"joint":fixed_rate(test,score_j,rate)}
    print(json.dumps(out,indent=2,sort_keys=True))

if __name__=="__main__": main()
