"""Role-local synthetic follow-up for clean_g1 multi_agent, 2026-08-26 15:00 JST.

Extends SYNTHETIC_ONLINE_OPPORTUNITY_ROUTER_2026-08-26_1400.py without
changing its simulator family. This is not an external empirical claim.

Question: under the same 1,200 evaluator-call budget, does probing only when
the opportunity-cost confidence interval crosses the current B-EVSI decision
boundary beat no probing or fixed epsilon probing?

Primary comparison uses 150 paired seeds per condition and a low probe rate:
  no_probe   online learner from naturally A-only pipelines
  eps05      5% pre-A randomized A-only probes + natural A-only updates
  target05   5% randomized probe only when a 95% opportunity interval crosses
             first-step B EVSI + natural A-only updates
  oracle     predecessor oracle64 routing baseline

The uncertainty model is deliberately small: cell x 10 incumbent bins with
bin shrinkage. Empirical cell variance is used when available, bin variance as
fallback, and a broad prior variance when sparse. This is a controller
ablation, not a calibrated confidence procedure.
"""
from __future__ import annotations
import math, runpy
from pathlib import Path
import numpy as np

BASE = runpy.run_path(str(Path(__file__).with_name(
    "SYNTHETIC_ONLINE_OPPORTUNITY_ROUTER_2026-08-26_1400.py")))
N_CELLS=BASE["N_CELLS"]; params=BASE["params"]; proposal=BASE["proposal"]
prior_stats=BASE["prior_stats"]; build_likes=BASE["build_likes"]
latents=BASE["latents"]; a_history=BASE["a_history"]; b_verdict=BASE["b_verdict"]
b_evsi=BASE["b_evsi"]; decision=BASE["decision"]; oracle64=BASE["oracle64"]

class OpportunityCI:
    def __init__(self, z=1.96):
        self.z=z
        self.bn=np.zeros(10,int); self.bs=np.zeros(10); self.bss=np.zeros(10)
        self.cbn=np.zeros((N_CELLS,10),int)
        self.cbs=np.zeros((N_CELLS,10)); self.cbss=np.zeros((N_CELLS,10))
    @staticmethod
    def bi(inc): return min(9,int(float(inc)*10))
    def stats(self,cell,inc):
        b=self.bi(inc); n=self.cbn[cell,b]; nb=self.bn[b]
        bm=self.bs[b]/(nb+5.0)
        mean=float(np.clip((self.cbs[cell,b]+8.0*bm)/(n+8.0),0,0.10))
        if n>=2:
            rm=self.cbs[cell,b]/n
            var=max((self.cbss[cell,b]-n*rm*rm)/(n-1),1e-6); neff=n+8.0
        elif nb>=2:
            rm=self.bs[b]/nb
            var=max((self.bss[b]-nb*rm*rm)/(nb-1),2.5e-5); neff=max(2.0,min(nb,20.0))
        else:
            var=0.0025; neff=1.0
        se=math.sqrt(var/neff)
        if n<4: se=max(se,0.0125/math.sqrt(n+1.0))
        return mean,max(0.0,mean-self.z*se),min(0.10,mean+self.z*se)
    def update(self,cell,inc,y):
        b=self.bi(inc)
        self.bn[b]+=1; self.bs[b]+=y; self.bss[b]+=y*y
        self.cbn[cell,b]+=1; self.cbs[cell,b]+=y; self.cbss[cell,b]+=y*y

def run(seed,errors,cross,mode,budget=1200,eps=.05,target_p=.05):
    rng=np.random.default_rng(seed); tab=build_likes(errors,cross)
    incs=np.array([rng.beta(*params(i)) for i in range(N_CELLS)],float)
    learn=OpportunityCI(); spent=0; b_calls=probes=proposals=0
    mismatch=0; regret=0.0; route_n=0
    while spent+3<=budget:
        cell=int(rng.integers(0,N_CELLS)); inc0=float(incs[cell])
        q=proposal(rng,inc0,cell); proposals+=1; better=q>inc0
        prior,mup,mun=prior_stats(cell,inc0)
        fixed=(mode=="eps05" and rng.random()<eps)
        lat=latents(rng,better,errors,cross); ah=a_history(rng,lat); spent+=3
        mean,lo,hi=learn.stats(cell,inc0) if mode!="oracle" else (0,0,0)
        target=False
        if mode=="target05" and spent+1<=budget:
            ev0=b_evsi(prior,mup,mun,ah,(),tab)
            target=(lo<=ev0<=hi) and (rng.random()<target_p)
        forced=fixed or target
        probes+=int(forced)
        bh=(); used_b=False
        while len(bh)<4 and spent+1<=budget:
            ev=b_evsi(prior,mup,mun,ah,bh,tab)
            oth=oracle64(cell,inc0,errors,cross,tab)
            oracle_action=ev>oth+1e-12
            action=oracle_action if mode=="oracle" else (False if forced else ev>mean+1e-12)
            if mode!="oracle":
                route_n+=1
                if action!=oracle_action:
                    mismatch+=1; regret+=abs(ev-oth)
            if not action: break
            bh+=(b_verdict(rng,lat),); spent+=1; b_calls+=1; used_b=True
        promote,_=decision(prior,mup,mun,ah,bh,tab)
        old=float(incs[cell]); incs[cell]=q if promote else incs[cell]
        if mode!="oracle" and not used_b:
            learn.update(cell,inc0,float(incs[cell]-old)/3.0)
    return dict(quality=float(incs.mean()),b_calls=b_calls,probes=probes,
                proposals=proposals,route_mismatch=mismatch/max(route_n,1),
                route_regret=regret/max(route_n,1))

def condition(errors,cross,reps=150,base=7_200_000_000):
    modes=("no_probe","eps05","target05","oracle")
    xs={m:[run(base+r,errors,cross,m) for r in range(reps)] for m in modes}
    oq=np.array([x["quality"] for x in xs["oracle"]])
    out={}
    for m in modes:
        q=np.array([x["quality"] for x in xs[m]]); d=q-oq
        out[m]={"quality":float(q.mean()),"delta_vs_oracle":float(d.mean()),
                "halfwidth95_vs_oracle":0.0 if m=="oracle" else float(1.96*d.std(ddof=1)/math.sqrt(reps)),
                "b_calls":float(np.mean([x["b_calls"] for x in xs[m]])),
                "probe_proposals":float(np.mean([x["probes"] for x in xs[m]])),
                "route_regret":float(np.mean([x["route_regret"] for x in xs[m]]))}
    td=np.array([x["quality"] for x in xs["target05"]])-np.array([x["quality"] for x in xs["eps05"]])
    out["target_minus_eps05"]={"mean":float(td.mean()),"halfwidth95":float(1.96*td.std(ddof=1)/math.sqrt(reps))}
    return out

if __name__=="__main__":
    for name,errors,b in (("asymmetric",(.40,.20,.20,.20),7_200_000_000),
                          ("symmetric",(.40,.40,.40,.40),7_300_000_000)):
        for cross in (0.0,0.5,1.0):
            print(name,cross,condition(errors,cross,150,b+int(cross*1_000_000)))
