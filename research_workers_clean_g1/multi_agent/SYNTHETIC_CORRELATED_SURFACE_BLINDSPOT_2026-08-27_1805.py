#!/usr/bin/env python3
"""Deterministic mechanism study for correlated dependency-surface blind spots.
Clean role-local synthetic experiment; not a deployment benchmark.
"""
import hashlib, random, collections, statistics

SURFACES = ["handoff","reducer","shared_memory","conditional_routing","dynamic_tool","custom_wrapper"]
SAFE = {"handoff","reducer","shared_memory"}
RISKY = {"conditional_routing","dynamic_tool","custom_wrapper"}
N = 28
TRAIN_GRAPHS = 3000
TEST_GRAPHS = 6000

def rng_for(*parts):
    h = hashlib.sha256("|".join(map(str, parts)).encode()).digest()
    return random.Random(int.from_bytes(h[:8], "big"))

def gen_dag(seed, test=False):
    r = rng_for("dag", seed, test)
    probs = [0.28,0.18,0.20,0.18,0.16,0.0] if not test else [0.24,0.16,0.18,0.16,0.14,0.12]
    edges = {}
    for j in range(1, N):
        k = 1 if j < 4 else r.choice([1,1,2,2,3])
        for i in r.sample(range(j), min(k,j)):
            edges[(i,j)] = r.choices(SURFACES, probs)[0]
        if j >= 4 and r.random() < 0.20:
            i = r.randrange(j)
            edges[(i,j)] = r.choices(SURFACES, probs)[0]
    return edges

def capture(seed, edges, test=False):
    r = rng_for("capture", seed, test)
    runtime, static = set(), set()
    custom_blind = test and (r.random() < 0.08)
    for e, surf in edges.items():
        if surf in SAFE:
            runtime.add(e)
            continue
        rr = 0.82
        ss = 1.00 if surf == "conditional_routing" else 0.90
        blind = surf == "custom_wrapper" and custom_blind
        if blind:
            rhit = shit = False
        else:
            if surf == "custom_wrapper" and test:
                rhit = r.random() < min(1.0, rr / 0.92)
                shit = r.random() < min(1.0, ss / 0.92)
            else:
                rhit = r.random() < rr
                shit = r.random() < ss
        if rhit: runtime.add(e)
        if shit: static.add(e)
    true = set(edges)
    for j in range(1, N):
        for i in range(j):
            e = (i,j)
            if e not in true and r.random() < 0.004:
                static.add(e)
    return runtime, static

def descendants(edges, src):
    adj = collections.defaultdict(list)
    for a,b in edges: adj[a].append(b)
    seen, stack = set(), [src]
    while stack:
        u = stack.pop()
        for v in adj.get(u,[]):
            if v not in seen:
                seen.add(v); stack.append(v)
    return seen

def train_stats():
    stats = {s:{"n":0,"static":0,"miss_r":0,"static_given_miss":0} for s in RISKY}
    for g in range(TRAIN_GRAPHS):
        edges = gen_dag(g, False); rt, st = capture(g, edges, False)
        for e,s in edges.items():
            if s not in RISKY: continue
            d=stats[s]; d["n"]+=1; d["static"] += e in st
            if e not in rt:
                d["miss_r"]+=1; d["static_given_miss"] += e in st
    return stats

def affected_surfaces(edges, src, td):
    return {s for (a,b),s in edges.items() if (a == src or a in td) and b in td}

def replay(policy, edges, src, rt, st, stats):
    true=set(edges); td=descendants(true,src); rd=descendants(rt,src); ud=descendants(rt|st,src)
    risky=affected_surfaces(edges,src,td) & RISKY
    if policy == "local":
        rep=rd
    elif policy == "pooled_union":
        rep=ud if risky else rd
    elif policy == "surface_conditional":
        ok=True
        for s in risky:
            d=stats.get(s)
            if not d or d["miss_r"] == 0 or d["static_given_miss"] / d["miss_r"] < 0.88:
                ok=False; break
        rep=ud if ok else set(range(N))-{src}
    elif policy == "positive_proof":
        if not risky: rep=rd
        elif risky <= {"conditional_routing"}: rep=ud
        else: rep=set(range(N))-{src}
    elif policy == "whole":
        rep=set(range(N))-{src}
    else: raise ValueError(policy)
    stale=len(td-rep); cost=1+len(rep)
    return stale == 0, cost, "custom_wrapper" in risky

def main():
    stats=train_stats()
    print("train conditional complement:")
    for s in ["conditional_routing","dynamic_tool"]:
        d=stats[s]
        print(s, d["static_given_miss"] / d["miss_r"])
    policies=["local","pooled_union","surface_conditional","positive_proof","whole"]
    rows={p:[] for p in policies}
    for g in range(TEST_GRAPHS):
        edges=gen_dag(g,True); rt,st=capture(g,edges,True)
        src=rng_for("src",g).randrange(0,N//2)
        for p in policies: rows[p].append(replay(p,edges,src,rt,st,stats))
    for p in policies:
        rs=rows[p]
        rec=sum(x[0] for x in rs)/len(rs); cost=statistics.mean(x[1] for x in rs)
        cr=[x for x in rs if x[2]]
        print(p, "recovery", round(rec,4), "mean_cost", round(cost,2),
              "correct/100k", round(100000*rec/cost,1),
              "custom_wrapper_recovery", round(sum(x[0] for x in cr)/len(cr),4))

if __name__ == "__main__": main()
