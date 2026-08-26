"""Clean-g1 multi_agent role-local synthetic diagnostic, 2026-08-26 17:07 JST.

This reproduces the single-common-suffix counterfactual teacher used in the
17:07 checkpoint. It imports the frozen predecessor simulator family and does
not claim external empirical validity.

For decision-sensitive states where baseline would route to B, clone archive
and opportunity-model state after the three A calls. Compare two actions:
  probe: force A-only completion and learn its realized opportunity label;
  route: follow the learned B-routing threshold.
Then replay the same pre-materialized future event suffix under the baseline
no-probe policy until an equal evaluator-call cap. The teacher target is final
mean archive quality(probe) - quality(route).

The checkpoint reports 800 states/condition for H in {60,120,240}. A single
suffix per state is intentionally diagnostic; its weak agreement is the reason
the next frontier calls for replicated suffixes before treating it as a label.
"""
from __future__ import annotations
import math, runpy
from dataclasses import dataclass
from pathlib import Path
import numpy as np

P = runpy.run_path(str(Path(__file__).with_name("SYNTHETIC_MYOPIC_VOI_PROBING_2026-08-26_1600.py")))
N=P["N"]; params=P["params"]; prior_stats=P["prior_stats"]
build_likes=P["build_likes"]; b_evsi=P["b_evsi"]; decision=P["decision"]
Events=P["Events"]; proposal=P["proposal"]; histories=P["histories"]; Opp=P["Opp"]
voi_reduction=P["voi_reduction"]

@dataclass
class State:
    inc: np.ndarray
    learn: object
    spent: int
    idx: int

def future_step(e,state,errors,cross,tab,cap):
    i=state.idx
    if state.spent+3>cap or i>=len(e.cell): return False
    c=int(e.cell[i]); old=float(state.inc[c]); q=proposal(e,i,old); better=q>old
    prior,mup,mun=prior_stats(c,old); ah,bs=histories(e,i,better,errors,cross)
    state.spent+=3; mean,_,_,_=state.learn.stats(c,old); bh=(); used=False
    while len(bh)<4 and state.spent+1<=cap:
        if b_evsi(prior,mup,mun,ah,bh,tab)<=mean+1e-12: break
        bh+=(bs[len(bh)],); state.spent+=1; used=True
    promote,_=decision(prior,mup,mun,ah,bh,tab)
    state.inc[c]=q if promote else state.inc[c]
    if not used: state.learn.update(c,old,float(state.inc[c]-old)/3)
    state.idx+=1
    return True

def branch_current(e,base,cur,errors,cross,tab,action,cap):
    st=State(base.inc.copy(),base.learn.clone(),base.spent,base.idx)
    c,old,q,ah,bs,prior,mup,mun=cur; mean,_,_,_=st.learn.stats(c,old)
    bh=(); used=False
    if action=="route":
        while len(bh)<4 and st.spent+1<=cap:
            if b_evsi(prior,mup,mun,ah,bh,tab)<=mean+1e-12: break
            bh+=(bs[len(bh)],); st.spent+=1; used=True
    promote,_=decision(prior,mup,mun,ah,bh,tab)
    st.inc[c]=q if promote else st.inc[c]
    if action=="probe" or not used: st.learn.update(c,old,float(st.inc[c]-old)/3)
    st.idx+=1
    while future_step(e,st,errors,cross,tab,cap): pass
    return float(st.inc.mean())

def collect(errors,cross,max_states=800,horizons=(60,120,240),hmult=4):
    rec=[]; tab=build_likes(errors,cross)
    for seed in range(500):
        e=Events(6_000_000_000+seed+int(cross*10000),n=1500)
        r=np.random.default_rng(7_000_000_000+seed+int(cross*10000))
        st=State(np.array([r.beta(*params(i)) for i in range(N)]),Opp(),0,0); budget=1200
        while st.spent+3<=budget and st.idx<len(e.cell) and len(rec)<max_states:
            i=st.idx; c=int(e.cell[i]); old=float(st.inc[c]); q=proposal(e,i,old); better=q>old
            prior,mup,mun=prior_stats(c,old); ah,bs=histories(e,i,better,errors,cross); st.spent+=3
            mean,se,var,ne=st.learn.stats(c,old); ev0=b_evsi(prior,mup,mun,ah,(),tab)
            future=hmult*max(0,(budget-st.spent)/budget)*voi_reduction(ev0,mean,se,var,ne)
            margin=future-(max(ev0-mean,0)+.1*mean+5e-5)
            if mean-1.96*se<=ev0<=mean+1.96*se and ev0>mean+1e-12:
                base=State(st.inc.copy(),st.learn.clone(),st.spent,st.idx)
                row={"local_probe":margin>0}
                cur=(c,old,q,ah,bs,prior,mup,mun)
                for H in horizons:
                    cap=min(budget,st.spent+H)
                    row[f"teacher_{H}"]=branch_current(e,base,cur,errors,cross,tab,"probe",cap)-branch_current(e,base,cur,errors,cross,tab,"route",cap)
                rec.append(row)
            bh=(); used=False
            while len(bh)<4 and st.spent+1<=budget:
                if b_evsi(prior,mup,mun,ah,bh,tab)<=mean+1e-12: break
                bh+=(bs[len(bh)],); st.spent+=1; used=True
            promote,_=decision(prior,mup,mun,ah,bh,tab)
            st.inc[c]=q if promote else st.inc[c]
            if not used: st.learn.update(c,old,float(st.inc[c]-old)/3)
            st.idx+=1
        if len(rec)>=max_states: break
    return rec

def summarize(rows):
    lp=np.array([r["local_probe"] for r in rows],bool); out={"n":len(rows),"local_probe_rate":float(lp.mean())}
    for H in (60,120,240):
        t=np.array([r[f"teacher_{H}"] for r in rows],float); tp=t>0
        out[H]={"mean":float(t.mean()),"hw95":float(1.96*t.std(ddof=1)/math.sqrt(len(t))),"sign_agreement":float((lp==tp).mean()),"false_probe_rate":float(np.mean(lp & ~tp)),"missed_probe_rate":float(np.mean(~lp & tp)),"teacher_probe_rate":float(tp.mean())}
    return out

if __name__=="__main__":
    for name,errors in (("asymmetric_x0",(.40,.20,.20,.20)),("weak_symmetric_x0",(.40,.40,.40,.40))):
        print(name,summarize(collect(errors,0.0)))
