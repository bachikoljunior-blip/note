#!/usr/bin/env python3
import itertools, json, math, random, statistics
from collections import Counter, defaultdict
from scipy.sparse import dok_matrix
from scipy.sparse.csgraph import maximum_flow

N_PLAYERS=10
PLAYERS=list(range(N_PLAYERS))
SUPPORTS=[[0,1],[2,3],[4,5],[6,7],[0,2,4,6,8,9]]
SUPPORT_MASKS=[sum(1<<i for i in s) for s in SUPPORTS]
NCOAL=1<<N_PLAYERS
BUDGETS=[128,256,384,512,640,768,896,1024]
THRESHOLDS=[0.001,0.005]
SCALE=math.factorial(N_PLAYERS)
SRC=NCOAL
SNK=NCOAL+1
NN=NCOAL+2
INF=10*SCALE

def value(mask):
    return int(any(mask & sm == sm for sm in SUPPORT_MASKS))
V=[value(m) for m in range(NCOAL)]

def objective_coeff(player):
    c=[0]*NCOAL
    bit=1<<player
    for mask in range(NCOAL):
        if mask & bit:
            continue
        k=mask.bit_count()
        w=math.factorial(k)*math.factorial(N_PLAYERS-k-1)
        c[mask]-=w
        c[mask|bit]+=w
    return c

def build_base(player):
    c=objective_coeff(player)
    cap=dok_matrix((NN,NN),dtype=int)
    positive=0
    for node,w in enumerate(c):
        if w>0:
            cap[SRC,node]=w; positive+=w
        elif w<0:
            cap[node,SNK]=-w
    for mask in range(NCOAL):
        for j in PLAYERS:
            if not mask & (1<<j):
                cap[mask,mask|(1<<j)]=INF
    return cap.tocsr(),positive

BASE={i:build_base(i) for i in [8,9]}

def upper(sampled,player):
    base,positive=BASE[player]
    mat=base.tolil(copy=True)
    for mask in sampled:
        if V[mask]:
            mat[SRC,mask]=int(mat[SRC,mask])+INF
        else:
            mat[mask,SNK]=int(mat[mask,SNK])+INF
    flow=maximum_flow(mat.tocsr(),SRC,SNK)
    return float((positive-flow.flow_value)/SCALE)

def exact_shapley(player):
    total=0.0
    bit=1<<player
    for mask in range(NCOAL):
        if mask & bit:
            continue
        k=mask.bit_count()
        w=math.factorial(k)*math.factorial(N_PLAYERS-k-1)/SCALE
        total += w*(V[mask|bit]-V[mask])
    return total

truth={i:exact_shapley(i) for i in [8,9]}
vals=defaultdict(list)
first={eps:{i:[] for i in [8,9]} for eps in THRESHOLDS}
for seed in range(1000,2000):
    rng=random.Random(seed*1000003+303)
    order=list(range(NCOAL)); rng.shuffle(order)
    earliest={(eps,i):None for eps in THRESHOLDS for i in [8,9]}
    for budget in BUDGETS:
        sampled=set(order[:budget])
        for i in [8,9]:
            u=upper(sampled,i)
            vals[(budget,i)].append(u)
            for eps in THRESHOLDS:
                if earliest[(eps,i)] is None and u <= eps+1e-12:
                    earliest[(eps,i)]=budget
    for eps in THRESHOLDS:
        for i in [8,9]:
            first[eps][i].append(earliest[(eps,i)])

out={"truth":truth,"budgets":{},"first_certification":{}}
for budget in BUDGETS:
    out["budgets"][str(budget)]={}
    for i in [8,9]:
        a=vals[(budget,i)]
        out["budgets"][str(budget)][str(i)]={
            "median_upper":statistics.median(a),
            "p95_upper":sorted(a)[int(.95*(len(a)-1))],
            "cert_rate_eps_0.001":sum(x<=.001+1e-12 for x in a)/len(a),
            "cert_rate_eps_0.005":sum(x<=.005+1e-12 for x in a)/len(a),
        }
for eps in THRESHOLDS:
    out["first_certification"][str(eps)]={str(i):{str(k):v for k,v in Counter(first[eps][i]).items()} for i in [8,9]}
print(json.dumps(out,indent=2,sort_keys=True))
