"""Clean-g1 multi_agent role-local synthetic pilot, 2026-08-26 16:00 JST.

Extends the 14:00/15:00 synthetic family. This is NOT an external empirical
claim. The main change is a pre-materialized per-proposal common-randomness
stream and a myopic opportunity-model value-of-information probe rule.

Budget: 1,200 evaluator calls; 16 archive cells; rho_A=rho_B=.6; 3 A calls;
up to 4 B calls. Policies: no_probe, eps05, target05, voi{4,12,36}.
The VoI controller probes (forces A-only) only in a decision-sensitive state
when an approximate future routing-regret reduction exceeds immediate lost
B-EVSI + 0.1*estimated proposal value + a small controller-cost proxy.
The horizon multiplier is multiplied by remaining budget fraction.

The 16:00 checkpoint reports 30 paired seeds/condition. This is a pilot and
intervals are intentionally reported; do not treat small differences as
established effects.
"""
from __future__ import annotations
import math, runpy
from pathlib import Path
import numpy as np

BASE=runpy.run_path(str(Path(__file__).with_name("SYNTHETIC_ONLINE_OPPORTUNITY_ROUTER_2026-08-26_1400.py")))
N=BASE["N_CELLS"]; params=BASE["params"]; prior_stats=BASE["prior_stats"]
build_likes=BASE["build_likes"]; b_evsi=BASE["b_evsi"]; decision=BASE["decision"]

class Events:
    def __init__(self,seed,n=700):
        r=np.random.default_rng(seed); self.cell=r.integers(0,N,n); self.mix=r.random(n)<.55
        self.beta=np.array([r.beta(*params(int(c))) for c in self.cell]); self.z=r.normal(size=n)
        self.uc=r.random(n); self.ucom=r.random(n); self.ua=r.random(n); self.ub=r.random(n)
        self.ual=r.random(n); self.ubl=r.random(n); self.uar=r.random((n,2)); self.ubr=r.random((n,4)); self.up=r.random(n)

def proposal(e,i,inc): return float(e.beta[i] if e.mix[i] else np.clip(inc+.04+.18*e.z[i],0,1))
def histories(e,i,better,errors,cross):
    qfa,qfr,qf_b,qr_b=errors; pa=(1-qfr) if better else qfa; pb=(1-qr_b) if better else qf_b
    if e.uc[i]<cross: u=e.ucom[i]; a1=u<pa; blat=u<pb
    else: a1=e.ua[i]<pa; blat=e.ub[i]<pb
    al=e.ual[i]<.6; bl=e.ubl[i]<.6
    ah=(bool(a1),bool(a1 if al else e.uar[i,0]<pa),bool(a1 if al else e.uar[i,1]<pa))
    bs=[bool(blat if bl else e.ubr[i,j]<pb) for j in range(4)]
    return ah,bs

class Opp:
    def __init__(self):
        self.bn=np.zeros(10,int); self.bs=np.zeros(10); self.bss=np.zeros(10)
        self.cn=np.zeros((N,10),int); self.cs=np.zeros((N,10)); self.css=np.zeros((N,10))
    def bi(self,x): return min(9,int(float(x)*10))
    def stats(self,c,x):
        b=self.bi(x); n=self.cn[c,b]; nb=self.bn[b]; bm=self.bs[b]/(nb+5.)
        mean=float(np.clip((self.cs[c,b]+8*bm)/(n+8),0,.1))
        if n>=2:
            rm=self.cs[c,b]/n; var=max((self.css[c,b]-n*rm*rm)/(n-1),1e-6); ne=n+8
        elif nb>=2:
            rm=self.bs[b]/nb; var=max((self.bss[b]-nb*rm*rm)/(nb-1),2.5e-5); ne=max(2,min(nb,20))
        else: var=.0025; ne=1
        se=math.sqrt(var/ne)
        if n<4: se=max(se,.0125/math.sqrt(n+1))
        return mean,se,var,max(n,1)
    def update(self,c,x,y):
        b=self.bi(x); self.bn[b]+=1; self.bs[b]+=y; self.bss[b]+=y*y
        self.cn[c,b]+=1; self.cs[c,b]+=y; self.css[c,b]+=y*y

def voi_reduction(ev,mean,se,var,n):
    zs=(-1.645,-.674,0,.674,1.645); ts=[min(.1,max(0,mean+se*z)) for z in zs]; act=ev>mean
    cur=sum(abs(ev-t) if ((ev>t)!=act) else 0 for t in ts)/len(ts); sd=math.sqrt(max(var,1e-6)); aft=[]
    for t in ts:
        for z in (-1,0,1):
            y=min(.1,max(0,t+sd*z)); m=(mean*n+y)/(n+1); a=ev>m
            aft.append(abs(ev-t) if ((ev>t)!=a) else 0)
    return max(0,cur-sum(aft)/len(aft))

def oracle_table(errors,cross):
    # Exact predecessor-style 64-sample fresh-A opportunity proxy for all cell/incumbent grid states.
    out=np.zeros((N,101)); tab=build_likes(errors,cross)
    for c in range(N):
      for gi in range(101):
        inc=gi/100; r=np.random.default_rng(8_100_000+c*50_000+gi*31+int(cross*100)*777+int(sum(errors)*1000)); vals=[]
        for _ in range(64):
          q=float(r.beta(*params(c)) if r.random()<.55 else np.clip(inc+r.normal(.04,.18),0,1)); better=q>inc
          prior,mup,mun=prior_stats(c,inc); qfa,qfr,qfb,qrb=errors; pa=(1-qfr) if better else qfa; pb=(1-qrb) if better else qfb
          if r.random()<cross: u=r.random(); a1=u<pa; _=u<pb
          else: a1=r.random()<pa; _=r.random()<pb
          al=r.random()<.6; ah=(bool(a1),bool(a1 if al else r.random()<pa),bool(a1 if al else r.random()<pa))
          promote,_=decision(prior,mup,mun,ah,(),tab); vals.append((q-inc)/3 if promote else 0)
        out[c,gi]=max(0,float(np.mean(vals)))
    return out

def run(seed,errors,cross,mode,oracle,hmult=12,budget=1200):
    e=Events(seed); tab=build_likes(errors,cross); r=np.random.default_rng(seed+999_000_000)
    inc=np.array([r.beta(*params(i)) for i in range(N)]); learn=Opp(); spent=b=probes=props=0; regret=rn=0; rare=[]
    i=0
    while spent+3<=budget and i<len(e.cell):
      c=int(e.cell[i]); old=float(inc[c]); q=proposal(e,i,old); better=q>old; props+=1; prior,mup,mun=prior_stats(c,old); ah,bs=histories(e,i,better,errors,cross); spent+=3
      mean,se,var,ne=learn.stats(c,old); oth=float(oracle[c,min(100,max(0,int(round(old*100))))]); rare += [abs(mean-oth)] if old<.2 else []
      ev0=b_evsi(prior,mup,mun,ah,(),tab); forced=False
      if mode=="eps05": forced=e.up[i]<.05
      elif mode=="target05": forced=(mean-1.96*se<=ev0<=mean+1.96*se) and e.up[i]<.05
      elif mode.startswith("voi") and mean-1.96*se<=ev0<=mean+1.96*se:
        future=hmult*max(0,(budget-spent)/budget)*voi_reduction(ev0,mean,se,var,ne)
        forced=future > max(ev0-mean,0)+.1*mean+5e-5
      probes+=int(forced); bh=(); used=False
      while len(bh)<4 and spent+1<=budget:
        ev=b_evsi(prior,mup,mun,ah,bh,tab); action=False if forced else ev>mean+1e-12; oa=ev>oth+1e-12
        if action!=oa: regret+=abs(ev-oth)
        rn+=1
        if not action: break
        bh+=(bs[len(bh)],); spent+=1; b+=1; used=True
      promote,_=decision(prior,mup,mun,ah,bh,tab); inc[c]=q if promote else inc[c]
      if not used: learn.update(c,old,float(inc[c]-old)/3)
      i+=1
    return dict(quality=float(inc.mean()),b_calls=b,probes=probes,proposals=props,route_regret=regret/max(rn,1),rare_mae=float(np.mean(rare)) if rare else float("nan"))

# See FOLLOWUP_2026-08-26_1600_JST.md for the completed 30-paired-seed table.
