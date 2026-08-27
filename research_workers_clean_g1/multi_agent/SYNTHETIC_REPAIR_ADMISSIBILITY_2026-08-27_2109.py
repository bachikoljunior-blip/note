import random
from collections import defaultdict, Counter

SURFACES=["handoff","shared_memory","conditional_routing","dynamic_tool","custom_wrapper"]
ACTUAL={"handoff":.995,"shared_memory":.99,"conditional_routing":.90,"dynamic_tool":.82,"custom_wrapper":.68}
RUNTIME={"handoff":.99,"shared_memory":.98,"conditional_routing":.88,"dynamic_tool":.82,"custom_wrapper":.72}
STATIC={"handoff":.99,"shared_memory":.97,"conditional_routing":.92,"dynamic_tool":.90,"custom_wrapper":.86}
FP=.02

def closure(edges,src):
    out=defaultdict(list)
    for a,b in edges: out[a].append(b)
    seen={src}; stack=[src]
    while stack:
        a=stack.pop()
        for b in out[a]:
            if b not in seen: seen.add(b); stack.append(b)
    return seen

def make(seed,proof_avail=.92):
    r=random.Random(seed*1000003+19+int(proof_avail*1000))
    n=r.randint(20,45); M=r.randint(3,7); mod=[r.randrange(M) for _ in range(n)]
    edges=set(); surf={}
    for i in range(n):
        for j in range(i+1,n):
            p=.092*(1.8 if mod[i]==mod[j] else .42)
            if r.random()<p:
                e=(i,j); edges.add(e)
                surf[e]=r.choices(SURFACES,weights=[3,3,2,2,1] if mod[i]==mod[j] else [5,1,2,2,1])[0]
    if not edges: edges.add((0,n-1)); surf[(0,n-1)]="handoff"
    out=defaultdict(list)
    for a,b in edges: out[a].append(b)
    source=r.choice([i for i in range(n) if out[i]])
    true_closure=closure(edges,source)
    epoch_current=(r.random()>=.12) or (r.random()<.94)
    mod_surfaces=defaultdict(set)
    for (a,b),s in surf.items(): mod_surfaces[mod[a]].add(s)
    actual={}; proof={}
    for m in range(M):
        actual[m]=all(r.random()<ACTUAL[s] for s in mod_surfaces[m])
        proof[m]=actual[m] and r.random()<proof_avail
    runtime=set(); static=set()
    for e in edges:
        a,b=e; s=surf[e]; m=mod[a]
        if actual[m]:
            if r.random()<.62: runtime.add(e)
            else: static.add(e)
            if r.random()<.55: runtime.add(e)
            if r.random()<.60: static.add(e)
        else:
            if r.random()<RUNTIME[s]: runtime.add(e)
            if r.random()<STATIC[s]: static.add(e)
    for i in range(n):
        for j in range(i+1,n):
            if (i,j) not in edges and r.random()<FP: static.add((i,j))
    effects={}
    for node in range(n):
        if r.random()<.11:
            kind=r.choices(["replayable","irreversible","authorization"],weights=[5,3,2])[0]
            record=r.random() < (.992 if kind=="replayable" else .975)
            equiv=r.random() < (.99 if kind=="replayable" else .955)
            effects[node]=(kind,record,equiv)
    return dict(n=n,M=M,mod=mod,edges=edges,source=source,true=true_closure,runtime=runtime,static=static,
                potential=runtime|static,epoch=epoch_current,proof=proof,effects=effects)

def effect_safe(c,nodes):
    return all(x not in c["effects"] or (c["effects"][x][1] and c["effects"][x][2]) for x in nodes)

def vcost(c,nodes,global_mode=False):
    if global_mode:
        mods=set(range(c["M"])); ec=len(c["potential"]); ef=len(c["effects"])
    else:
        mods={c["mod"][x] for x in nodes}; ec=sum(a in nodes or b in nodes for a,b in c["potential"]); ef=sum(x in c["effects"] for x in nodes)
    return .4+.045*len(nodes)+.025*ec+.10*len(mods)+.14*ef

def evaluate(c,policy):
    n=c["n"]
    if policy=="union_no_proof":
        nodes=closure(c["potential"],c["source"]); val=.25
        safe=c["true"].issubset(nodes) and effect_safe(c,nodes)
        return safe,not safe,False,len(nodes)+val,"union"
    if policy=="global":
        val=vcost(c,set(range(n)),True)
        ok=c["epoch"] and all(c["proof"][m] for m in range(c["M"])) and effect_safe(c,set(range(n)))
        if ok:
            nodes=closure(c["potential"],c["source"]); safe=c["true"].issubset(nodes) and effect_safe(c,nodes)
            return safe,not safe,False,len(nodes)+val,"local_globalcert"
        if effect_safe(c,set(range(n))): return True,False,False,n+val,"whole"
        return False,False,True,val,"block"
    cand=closure(c["potential"],c["source"]); mods={c["mod"][x] for x in cand}; val=vcost(c,cand,False)
    ok=c["epoch"] and all(c["proof"][m] for m in mods) and effect_safe(c,cand)
    if ok:
        safe=c["true"].issubset(cand) and effect_safe(c,cand)
        return safe,not safe,False,len(cand)+val,"local_repaircert"
    if effect_safe(c,set(range(n))): return True,False,False,n+val,"whole"
    return False,False,True,val,"block"

def run(N=20000,proof_avail=.92):
    policies=["union_no_proof","global","repair"]
    A={p:dict(s=0,u=0,b=0,cost=0.,m=Counter()) for p in policies}
    for seed in range(N):
        c=make(seed,proof_avail)
        for p in policies:
            s,u,b,cost,mode=evaluate(c,p); a=A[p]
            a["s"]+=s; a["u"]+=u; a["b"]+=b; a["cost"]+=cost; a["m"][mode]+=1
    for p,a in A.items():
        print(p,{"success":a["s"]/N,"unsafe":a["u"]/N,"blocked":a["b"]/N,"mean_total_cost":a["cost"]/N,
                 "success_per_100k_cost":a["s"]/a["cost"]*100000,"modes":{k:v/N for k,v in a["m"].items()}})

if __name__=="__main__":
    run()
    for q in (.60,.75,.90,1.0):
        print("proof_availability",q); run(8000,q)
