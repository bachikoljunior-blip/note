import hashlib, math, statistics
from collections import Counter, defaultdict, deque

SURFACES = ["handoff","shared_memory","conditional_routing","dynamic_tool","reducer","custom_wrapper"]
SURF_W = {"handoff":.24,"shared_memory":.18,"conditional_routing":.16,"dynamic_tool":.14,"reducer":.16,"custom_wrapper":.12}
RUNTIME_P = {"handoff":.98,"shared_memory":.93,"conditional_routing":.72,"dynamic_tool":.62,"reducer":.97,"custom_wrapper":.55}
RISKY = ["conditional_routing","dynamic_tool","custom_wrapper"]

def u01(*parts):
    s = "|".join(map(str, parts)).encode()
    return int.from_bytes(hashlib.sha256(s).digest()[:8], "big") / 2**64

def choose_weighted(key, items, weights):
    x = u01(*key); acc = 0.0
    for item, w in zip(items, weights):
        acc += w
        if x < acc: return item
    return items[-1]

def gen_graph(gid, n_layers=5, width=5):
    layers = [[0]]; node = 1
    for _ in range(1, n_layers + 1):
        layers.append(list(range(node, node + width))); node += width
    edges = []
    for l in range(1, n_layers + 1):
        prev = layers[l-1]
        earlier = [x for lay in layers[:l] for x in lay]
        for v in layers[l]:
            p = prev[int(u01("parent", gid, v) * len(prev)) % len(prev)]
            s = choose_weighted(("surf0",gid,p,v), SURFACES, [SURF_W[z] for z in SURFACES])
            edges.append((p,v,s))
            if u01("extra1",gid,v) < .45:
                q = earlier[int(u01("q1",gid,v) * len(earlier)) % len(earlier)]
                if q != p:
                    s = choose_weighted(("surf1",gid,q,v), SURFACES, [SURF_W[z] for z in SURFACES])
                    edges.append((q,v,s))
            if u01("extra2",gid,v) < .15:
                q = earlier[int(u01("q2",gid,v) * len(earlier)) % len(earlier)]
                if all(not (a == q and b == v) for a,b,_ in edges):
                    s = choose_weighted(("surf2",gid,q,v), SURFACES, [SURF_W[z] for z in SURFACES])
                    edges.append((q,v,s))
    return list(range(node)), edges

def descendants(nodes, edges, root=0):
    adj = defaultdict(list)
    for a,b,*_ in edges: adj[a].append(b)
    seen = {root}; q = deque([root])
    while q:
        a = q.popleft()
        for b in adj[a]:
            if b not in seen: seen.add(b); q.append(b)
    return seen - {root}

def capture_graph(gid, regime="independent"):
    nodes, edges = gen_graph(gid)
    blind = None; known_blind = False
    if regime == "surface_blind" and u01("has_blind",gid) < .40:
        blind = RISKY[int(u01("which_blind",gid) * len(RISKY)) % len(RISKY)]
        known_blind = u01("known_blind",gid) < .50
    runtime = []; static = []
    for i,(a,b,s) in enumerate(edges):
        if regime == "independent":
            rp, sp = RUNTIME_P[s], .90
        elif blind == s:
            rp, sp = 0.0, 0.0
        else:
            rp, sp = min(.995, RUNTIME_P[s] + .055), .98
        if u01("rt",regime,gid,i) < rp: runtime.append((a,b,s))
        if u01("st",regime,gid,i) < sp: static.append((a,b,s))
    return dict(gid=gid,nodes=nodes,edges=edges,runtime=runtime,static=static,blind=blind,known_blind=known_blind)

def gm(g):
    td = descendants(g["nodes"], g["edges"])
    ue = list({e for e in g["runtime"] + g["static"]})
    ud = descendants(g["nodes"], ue)
    return dict(edge_rt=len(g["runtime"])/len(g["edges"]), edge_st=len(g["static"])/len(g["edges"]),
                recovery_union=td <= ud, cost_union=1+len(ud), cost_whole=len(g["nodes"]))

def regime_summary(regime, n=3000, start=20000):
    xs=[(capture_graph(g,regime)) for g in range(start,start+n)]
    ms=[gm(g) for g in xs]
    return dict(runtime_edge_recall=statistics.mean(m["edge_rt"] for m in ms),
                static_edge_recall=statistics.mean(m["edge_st"] for m in ms),
                union_full_recovery=statistics.mean(m["recovery_union"] for m in ms),
                union_mean_cost=statistics.mean(m["cost_union"] for m in ms),
                blind_fraction=statistics.mean(g["blind"] is not None for g in xs))

def calibrate(n=5000):
    d={s:Counter() for s in SURFACES}
    for gid in range(n):
        g=capture_graph(gid,"surface_blind"); rt=set(g["runtime"]); st=set(g["static"])
        for e in g["edges"]:
            s=e[2]; x=d[s]; x["n"]+=1; r=e in rt; q=e in st
            x["r"]+=r; x["st"]+=q; x["rmiss"]+=(not r); x["st_on_rmiss"]+=(q and not r)
    out={}
    for s,x in d.items():
        r=x["r"]/x["n"]; st=x["st"]/x["n"]; c=x["st_on_rmiss"]/x["rmiss"]
        out[s]=dict(r=r,st=st,c=c,u_ind=1-(1-r)*(1-st),u_joint=r+(1-r)*c)
    return out

EST=calibrate()

def safety_score(g, mode):
    # A hidden whole-surface blind spot is absent from ordinary observed inventory.
    visible=Counter(s for _,_,s in g["runtime"]+g["static"])
    if mode == "proof" and g["known_blind"] and g["blind"]:
        return -1e9
    total=0.0
    for s,n in visible.items():
        u=EST[s]["u_ind"] if mode == "marginal" else EST[s]["u_joint"]
        total += math.sqrt(n)*math.log(max(u,1e-12))
    return total

def router_eval(frac, mode, n=5000, start=10000):
    data=[]
    for gid in range(start,start+n):
        g=capture_graph(gid,"surface_blind"); m=gm(g)
        data.append((safety_score(g,mode),gid,g,m))
    k=int(frac*n)
    selected=set(gid for _,gid,_,_ in sorted(data,key=lambda x:(x[0],-x[1]),reverse=True)[:k])
    correct=0; totalcost=0; ucounts=Counter(); ucorr=Counter(); pop=Counter()
    for _,gid,g,m in data:
        typ="no_blind" if g["blind"] is None else ("known_blind" if g["known_blind"] else "unknown_blind")
        pop[typ]+=1
        if gid in selected:
            ucounts[typ]+=1; rec=m["recovery_union"]; cost=m["cost_union"]; ucorr[typ]+=int(rec)
        else:
            rec=True; cost=m["cost_whole"]
        correct += int(rec); totalcost += cost
    return dict(recovery=correct/n,mean_cost=totalcost/n,correct_per_100k=correct/totalcost*100000,
                union_counts=dict(ucounts),
                union_recovery_by_type={t:(ucorr[t]/ucounts[t] if ucounts[t] else None) for t in ["no_blind","known_blind","unknown_blind"]},
                population_counts=dict(pop))

if __name__ == "__main__":
    print("independent", regime_summary("independent"))
    print("surface_blind", regime_summary("surface_blind"))
    print("calibration", EST)
    for frac in [.2,.4,.6,.8]:
        print("union_capacity", frac)
        for mode in ["marginal","joint","proof"]:
            print(mode, router_eval(frac,mode))
