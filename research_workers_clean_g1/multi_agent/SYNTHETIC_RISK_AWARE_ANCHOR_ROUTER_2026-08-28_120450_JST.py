import numpy as np, pandas as pd
from scipy.stats import beta
from itertools import product

SEED=2026082812
rng=np.random.default_rng(SEED)

# rank distributions for the true intervention anchor among 8 symptom-ranked candidates
base={
 'good':np.array([.75,.15,.06,.02,.01,.005,.003,.002]),
 'mid': np.array([.50,.22,.12,.07,.04,.025,.015,.01]),
 'poor':np.array([.30,.22,.15,.10,.08,.06,.05,.04]),
}
# shifted test distribution: localizer degrades on poor symptoms while preserving support
shift={k:v.copy() for k,v in base.items()}
shift['poor']=np.array([.22,.20,.16,.12,.10,.08,.07,.05])
assert all(abs(v.sum()-1)<1e-9 for v in base.values())
assert all(abs(v.sum()-1)<1e-9 for v in shift.values())
severe={k:v.copy() for k,v in base.items()}
severe['poor']=np.array([.15,.17,.16,.14,.12,.10,.09,.07])
assert abs(severe['poor'].sum()-1)<1e-9

# calibration rank data, fixed before test
ncal=1200
cal={}
for g,p in base.items():
    ranks=rng.choice(np.arange(1,9),size=ncal,p=p)
    emp=[]; lo=[]
    for k in range(1,9):
        x=(ranks<=k).sum()
        emp.append(x/ncal)
        # Jeffreys lower 95% bound on top-k coverage
        lo.append(beta.ppf(.025,x+.5,ncal-x+.5))
    cal[g]={'emp':np.array(emp),'lo':np.array(lo)}

# risk axes and componentwise minimum required localization coverage
D_vals=[5,20,80,200]
E_vals=['none','reversible','irreversible']
A_vals=['low','high']
S_vals=['known','unknown']
D_req={5:.70,20:.80,80:.90,200:.95}
E_req={'none':.70,'reversible':.90,'irreversible':1.01}
A_req={'low':.70,'high':.95}
S_req={'known':.70,'unknown':1.01}

def vector_target(D,E,A,S): return max(D_req[D],E_req[E],A_req[A],S_req[S])

def scalar_target(D,E,A,S):
    # Deliberately commensurated baseline: low-risk axes can offset hard-risk axes.
    d={5:0,20:1/3,80:2/3,200:1}[D]
    e={'none':0,'reversible':.5,'irreversible':1}[E]
    a={'low':0,'high':1}[A]
    s={'known':0,'unknown':1}[S]
    score=.35*d+.25*e+.20*a+.20*s
    return .70+.25*score

def pick_k(g,target,kind='lo'):
    if target>1: return None
    arr=cal[g][kind]
    ok=np.where(arr>=target)[0]
    return None if len(ok)==0 else int(ok[0]+1)

# monotonicity check for vector policy: increasing risk on any axis cannot reduce scope k or switch whole->local.
def scope_ord(k): return 99 if k is None else k
viol=[]
for g in base:
  for D,E,A,S in product(D_vals,E_vals,A_vals,S_vals):
    k=pick_k(g,vector_target(D,E,A,S),'lo')
    neigh=[]
    di=D_vals.index(D)
    if di+1<len(D_vals): neigh.append((D_vals[di+1],E,A,S,'D'))
    ei=E_vals.index(E)
    if ei+1<len(E_vals): neigh.append((D,E_vals[ei+1],A,S,'E'))
    if A=='low': neigh.append((D,E,'high',S,'A'))
    if S=='known': neigh.append((D,E,A,'unknown','S'))
    for D2,E2,A2,S2,ax in neigh:
      k2=pick_k(g,vector_target(D2,E2,A2,S2),'lo')
      if scope_ord(k2)<scope_ord(k): viol.append((g,D,E,A,S,ax,k,k2))


def simulate(testdist,N=250_000):
    groups=rng.choice(np.array(['good','mid','poor']),size=N,p=[.45,.35,.20])
    D=rng.choice(D_vals,size=N,p=[.35,.30,.22,.13])
    E=rng.choice(E_vals,size=N,p=[.82,.13,.05])
    A=rng.choice(A_vals,size=N,p=[.90,.10])
    S=rng.choice(S_vals,size=N,p=[.95,.05])
    rank=np.empty(N,dtype=int)
    for g in base:
        ix=np.where(groups==g)[0]
        rank[ix]=rng.choice(np.arange(1,9),size=len(ix),p=testdist[g])
    u=rng.random(N)
    rows=[]
    policies=['top1','top3','scalar_ci','vector_mean','vector_ci','vector_robust05','vector_robust10','whole']
    for pol in policies:
        ks=np.empty(N,dtype=int); ks.fill(-1)
        targets=np.empty(N)
        for i in range(N):
            g=groups[i]; d=int(D[i]); e=E[i]; a=A[i]; s=S[i]
            vt=vector_target(d,e,a,s); targets[i]=vt
            if pol=='top1': k=1
            elif pol=='top3': k=3
            elif pol=='whole': k=None
            elif pol=='scalar_ci': k=pick_k(g,scalar_target(d,e,a,s),'lo')
            elif pol=='vector_mean': k=pick_k(g,vt,'emp')
            elif pol=='vector_ci': k=pick_k(g,vt,'lo')
            elif pol.startswith('vector_robust'):
                eps=.05 if pol.endswith('05') else .10
                if vt>1: k=None
                else:
                    arr=cal[g]['lo']-eps
                    ok=np.where(arr>=vt)[0]
                    k=None if len(ok)==0 else int(ok[0]+1)
            ks[i]=-1 if k is None else k
        iswhole=ks==-1
        local_cost=np.minimum(300.0,D.astype(float)*(1+.25*np.maximum(ks-1,0)))
        cost=np.where(iswhole,300.0,local_cost)
        success=np.where(iswhole,u<.75,(rank<=ks)&(u<.85))
        truecov=np.ones(N)
        for g in base:
            cdf=np.cumsum(testdist[g])
            ix=np.where((groups==g)&(~iswhole))[0]
            if len(ix): truecov[ix]=cdf[ks[ix]-1]
        unsafe=(~iswhole)&((targets>1)|(truecov+1e-12<targets))
        rows.append({
            'policy':pol,
            'success_rate':success.mean(),
            'mean_cost':cost.mean(),
            'success_per_100k_cost':success.sum()/cost.sum()*100000,
            'local_fraction':(~iswhole).mean(),
            'unsafe_admission_rate':unsafe.mean(),
            'unsafe_given_local':unsafe.sum()/max((~iswhole).sum(),1),
            'mean_k_given_local':ks[~iswhole].mean() if (~iswhole).any() else np.nan,
        })
    return pd.DataFrame(rows)

iid=simulate(base)
shifted=simulate(shift)
severed=simulate(severe)
print('CALIBRATION')
for g in base:
 print(g,'emp',np.round(cal[g]['emp'],4),'lo',np.round(cal[g]['lo'],4))
print('\nMONOTONICITY_VIOLATIONS',len(viol))
print('\nIID')
print(iid.to_string(index=False,float_format=lambda x:f'{x:.5f}'))
print('\nSHIFTED')
print(shifted.to_string(index=False,float_format=lambda x:f'{x:.5f}'))
print('\nSEVERE_SHIFT')
print(severed.to_string(index=False,float_format=lambda x:f'{x:.5f}'))
out=pd.concat([iid.assign(regime='iid'),shifted.assign(regime='poor_localizer_shift'),severed.assign(regime='poor_localizer_severe_shift')],ignore_index=True)
out.to_csv('risk_anchor_router_results.csv',index=False)
