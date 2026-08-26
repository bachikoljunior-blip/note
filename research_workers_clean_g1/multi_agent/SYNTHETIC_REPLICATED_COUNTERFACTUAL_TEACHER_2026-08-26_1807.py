"""Clean-g1 multi_agent role-local synthetic diagnostic, 2026-08-26 18:07 JST.

Replicates the counterfactual teacher within selected archive states rather than
using one future suffix as a binary label. This is a synthetic diagnostic, not
an external empirical claim.

Frozen semantic family:
- predecessor: SYNTHETIC_COUNTERFACTUAL_VOI_TEACHER_2026-08-26_1707.py
- 16 cells, 1,200 evaluator-call budget
- rho_A=rho_B=.6; 3 sunk A calls; up to 4 B calls
- regimes: asymmetric A(.40/.20), B(.20/.20) and weak symmetric A=B(.40/.40)
- cross_mix=0
- 150 decision-sensitive selected states per regime
- within-state paired common-randomness suffix replication R={2,4,8,16}
- horizons H={60,120,240,remaining-budget}

For each selected state and each replicate, probe and route branches share the
same independently generated future suffix. The state-level teacher value is
mean final archive quality(probe)-quality(route) across the first R suffixes.
The script reports sign stability versus R=16 and horizon agreement against the
remaining-budget teacher. Do not train a router from these labels without an
additional reliability criterion.
"""
from __future__ import annotations
import math, runpy
from dataclasses import dataclass
from pathlib import Path
import numpy as np

P = runpy.run_path(str(Path(__file__).with_name(
    "SYNTHETIC_COUNTERFACTUAL_VOI_TEACHER_2026-08-26_1707.py")))
N=P["N"]; params=P["params"]; prior_stats=P["prior_stats"]
build_likes=P["build_likes"]; b_evsi=P["b_evsi"]; decision=P["decision"]
Events=P["Events"]; proposal=P["proposal"]; histories=P["histories"]; Opp=P["Opp"]
voi_reduction=P["voi_reduction"]

@dataclass
class Selected:
    inc: np.ndarray
    learn: object
    spent: int
    c: int
    old: float
    q: float
    ah: tuple
    bs: tuple
    prior: float
    mup: float
    mun: float
    local_probe: bool

@dataclass
class State:
    inc: np.ndarray
    learn: object
    spent: int
    idx: int = 0

def future_step(e,state,errors,cross,tab,cap):
    i=state.idx
    if state.spent+3>cap or i>=len(e.cell): return False
    c=int(e.cell[i]); old=float(state.inc[c]); q=proposal(e,i,old); better=q>old
    prior,mup,mun=prior_stats(c,old); ah,bs=histories(e,i,better,errors,cross)
    state.spent+=3
    mean,_,_,_=state.learn.stats(c,old)
    bh=(); used=False
    while len(bh)<4 and state.spent+1<=cap:
        if b_evsi(prior,mup,mun,ah,bh,tab)<=mean+1e-12: break
        bh+=(bs[len(bh)],); state.spent+=1; used=True
    promote,_=decision(prior,mup,mun,ah,bh,tab)
    state.inc[c]=q if promote else state.inc[c]
    if not used: state.learn.update(c,old,float(state.inc[c]-old)/3)
    state.idx+=1
    return True

def collect_selected(errors,cross,max_states,seed_base,hmult=4,budget=1200):
    rec=[]; tab=build_likes(errors,cross)
    for seed_i in range(800):
        e=Events(seed_base+seed_i+int(cross*10000),n=1500)
        r=np.random.default_rng(seed_base+1_000_000_000+seed_i+int(cross*10000))
        st=State(np.array([r.beta(*params(i)) for i in range(N)]),Opp(),0,0)
        while st.spent+3<=budget and st.idx<len(e.cell) and len(rec)<max_states:
            i=st.idx; c=int(e.cell[i]); old=float(st.inc[c]); q=proposal(e,i,old); better=q>old
            prior,mup,mun=prior_stats(c,old); ah,bs=histories(e,i,better,errors,cross)
            st.spent+=3
            mean,se,var,ne=st.learn.stats(c,old)
            ev0=b_evsi(prior,mup,mun,ah,(),tab)
            future=hmult*max(0,(budget-st.spent)/budget)*voi_reduction(ev0,mean,se,var,ne)
            margin=future-(max(ev0-mean,0)+.1*mean+5e-5)
            if mean-1.96*se<=ev0<=mean+1.96*se and ev0>mean+1e-12:
                rec.append(Selected(st.inc.copy(),st.learn.clone(),st.spent,c,old,q,
                                    ah,tuple(bs),prior,mup,mun,margin>0))
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

def branch_suffix(sel,e,errors,cross,tab,action,H,budget=1200):
    st=State(sel.inc.copy(),sel.learn.clone(),sel.spent,0)
    mean,_,_,_=st.learn.stats(sel.c,sel.old)
    cap=min(budget,sel.spent+H)
    bh=(); used=False
    if action=="route":
        while len(bh)<4 and st.spent+1<=cap:
            if b_evsi(sel.prior,sel.mup,sel.mun,sel.ah,bh,tab)<=mean+1e-12: break
            bh+=(sel.bs[len(bh)],); st.spent+=1; used=True
    promote,_=decision(sel.prior,sel.mup,sel.mun,sel.ah,bh,tab)
    st.inc[sel.c]=sel.q if promote else st.inc[sel.c]
    if action=="probe" or not used:
        st.learn.update(sel.c,sel.old,float(st.inc[sel.c]-sel.old)/3)
    while future_step(e,st,errors,cross,tab,cap): pass
    return float(st.inc.mean())

def replicated(selected,errors,cross,seed_base_first100,seed_base_extra,Rmax=16,budget=1200):
    tab=build_likes(errors,cross); horizons=(60,120,240,"remaining"); rows=[]
    for si,sel in enumerate(selected):
        vals={h:[] for h in horizons}
        for r in range(Rmax):
            base = seed_base_first100 if si < 100 else seed_base_extra
            local_si = si if si < 100 else si-100
            e=Events(base+local_si*1000+r+int(sum(errors)*10000),n=1500)
            for h in horizons:
                H=(budget-sel.spent) if h=="remaining" else h
                vals[h].append(branch_suffix(sel,e,errors,cross,tab,"probe",H,budget)
                               -branch_suffix(sel,e,errors,cross,tab,"route",H,budget))
        rows.append((sel.local_probe,vals))
    return rows

def sgn(x,eps=1e-12):
    return 1 if x>eps else (-1 if x<-eps else 0)

def summarize(rows):
    horizons=(60,120,240,"remaining")
    full={h:np.array([np.mean(v[h][:16]) for _,v in rows]) for h in horizons}
    for h in horizons:
        s16=np.array([sgn(x) for x in full[h]])
        local=np.array([1 if lp else -1 for lp,_ in rows])
        print("H",h,"R16 mean",full[h].mean(),
              "hw95",1.96*full[h].std(ddof=1)/math.sqrt(len(rows)),
              "directional_fraction",np.mean(s16!=0),
              "local_directional_agreement",
              np.mean(local[s16!=0]==s16[s16!=0]) if np.any(s16!=0) else np.nan)
        for R in (2,4,8,16):
            arr=np.array([v[h][:R] for _,v in rows],float)
            m=arr.mean(axis=1); sr=np.array([sgn(x) for x in m])
            mask=s16!=0
            agree=np.mean(sr[mask]==s16[mask]) if np.any(mask) else np.nan
            se=arr.std(axis=1,ddof=1)/math.sqrt(R)
            decisive=np.mean((np.abs(m)>1.96*se)&(np.abs(m)>1e-12)) if R>=4 else np.nan
            print(" R",R,"dir_sign_agree_R16",agree,
                  "median_state_se",np.median(se),"decisive95",decisive)
    rem=full["remaining"]; srem=np.array([sgn(x) for x in rem])
    for h in (60,120,240):
        sh=np.array([sgn(x) for x in full[h]])
        mask=(sh!=0)&(srem!=0)
        print("horizon",h,"vs remaining directional_overlap",np.mean(mask),
              "sign_agreement",np.mean(sh[mask]==srem[mask]) if np.any(mask) else np.nan,
              "corr",np.corrcoef(full[h],rem)[0,1])

if __name__=="__main__":
    regimes=(
        ("asymmetric",(.40,.20,.20,.20),6_100_000_000,22_000_000_000,24_000_000_000),
        ("weak_symmetric",(.40,.40,.40,.40),6_200_000_000,23_000_000_000,25_000_000_000),
    )
    for name,errors,state_seed,suffix_seed_first,suffix_seed_extra in regimes:
        print("\nREGIME",name)
        selected=collect_selected(errors,0.0,150,state_seed)
        rows=replicated(selected,errors,0.0,suffix_seed_first,suffix_seed_extra)
        summarize(rows)
