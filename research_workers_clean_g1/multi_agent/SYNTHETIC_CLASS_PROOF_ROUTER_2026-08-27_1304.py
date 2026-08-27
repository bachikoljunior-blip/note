#!/usr/bin/env python3
"""Deterministic synthetic proof-contract rollback router study.

Scope: mechanism study only. It does not estimate real LangGraph/AgentFlow
capture rates. SHA-256 is used for every pseudo-random choice so reruns are
process-independent.
"""
import hashlib

SAFE = {"handoff", "reducer", "shared_memory"}
RISKY = {"conditional_routing", "dynamic_tool"}
RUNTIME_RECALL = {
    "handoff": 1.0,
    "reducer": 1.0,
    "shared_memory": 1.0,
    "conditional_routing": 0.55,
    "dynamic_tool": 0.65,
}
MIXED = [
    ("handoff", .25), ("reducer", .25), ("shared_memory", .15),
    ("conditional_routing", .20), ("dynamic_tool", .15),
]
INDEP = [("handoff", .45), ("reducer", .40), ("shared_memory", .15)]
STATIC_PROFILES = {
    "uniform_97": {"conditional_routing": .97, "dynamic_tool": .97},
    "enumerated_route_dynamic_gap": {"conditional_routing": 1.0, "dynamic_tool": .75},
    "complete": {"conditional_routing": 1.0, "dynamic_tool": 1.0},
}
POLICIES = ["local", "union", "scalar97", "global_strict",
            "classaware_strict", "whole"]

def u01(*parts):
    h = hashlib.sha256("|".join(map(str, parts)).encode()).digest()
    return int.from_bytes(h[:8], "big") / 2**64

def bern(p, *parts):
    return u01(*parts) < p

def wchoice(items, *parts):
    x, c = u01(*parts), 0.0
    for value, weight in items:
        c += weight
        if x < c:
            return value
    return items[-1][0]

def desc(n, edges, source=0):
    adj = [[] for _ in range(n)]
    for a, b in edges:
        adj[a].append(b)
    seen, stack = set(), [source]
    while stack:
        a = stack.pop()
        for b in adj[a]:
            if b not in seen:
                seen.add(b)
                stack.append(b)
    seen.discard(source)
    return seen

def gen(gid):
    na = 6 + int(u01(gid, "na") * 15)
    ni = 6 + int(u01(gid, "ni") * 15)
    n = 2 + na + ni
    affected = list(range(2, 2 + na))
    independent = list(range(2 + na, n))
    typ = {0: "source", 1: "independent_root"}
    for i, v in enumerate(affected):
        typ[v] = wchoice(MIXED, gid, "atype", i)
    for i, v in enumerate(independent):
        typ[v] = wchoice(INDEP, gid, "itype", i)
    edges, etype = [], {}
    prev = 0
    for i, v in enumerate(affected):
        edges.append((prev, v)); etype[(prev, v)] = typ[v]
        prior = [0] + affected[:i]
        if len(prior) > 1 and bern(.55, gid, "extraA", i):
            p = prior[int(u01(gid, "parentA", i) * len(prior)) % len(prior)]
            if p != prev and (p, v) not in etype:
                edges.append((p, v)); etype[(p, v)] = typ[v]
        prev = v
    prev = 1
    for i, v in enumerate(independent):
        edges.append((prev, v)); etype[(prev, v)] = typ[v]
        prior = [1] + independent[:i]
        if len(prior) > 1 and bern(.45, gid, "extraI", i):
            p = prior[int(u01(gid, "parentI", i) * len(prior)) % len(prior)]
            if p != prev and (p, v) not in etype:
                edges.append((p, v)); etype[(p, v)] = typ[v]
        prev = v
    return n, affected, independent, typ, edges, etype

def observed(gid, static_name, static_fp):
    n, affected, independent, typ, true_edges, etype = gen(gid)
    obs, sta = [], []
    sp = STATIC_PROFILES[static_name]
    for a, b in true_edges:
        t = etype[(a, b)]
        if bern(RUNTIME_RECALL[t], gid, static_name, static_fp, "obs", a, b):
            obs.append((a, b))
        sr = 1.0 if t in SAFE else sp[t]
        if bern(sr, gid, static_name, static_fp, "sta", a, b):
            sta.append((a, b))
    for v in independent:
        shared = [x for x in affected if typ[x] == "shared_memory" and x < v]
        if shared and bern(.08, gid, static_name, static_fp, "obsfp", v):
            a = shared[int(u01(gid, "obsfpp", v) * len(shared)) % len(shared)]
            if (a, v) not in true_edges:
                obs.append((a, v))
        if bern(static_fp, gid, static_name, static_fp, "stafp", v):
            pool = [0] + affected
            a = pool[int(u01(gid, "stafpp", v) * len(pool)) % len(pool)]
            if a < v and (a, v) not in true_edges:
                sta.append((a, v))
    return n, affected, independent, typ, obs, sta

def run_one(gid, static_name, static_fp, policy):
    n, affected, independent, typ, obs, sta = observed(gid, static_name, static_fp)
    risky = {typ[v] for v in affected if typ[v] in RISKY}
    union = list(set(obs) | set(sta))
    sp = STATIC_PROFILES[static_name]
    if policy == "local":
        replay = desc(n, obs)
    elif policy == "union":
        replay = desc(n, union)
    elif policy == "whole":
        replay = set(range(2, n))
    elif policy == "scalar97":
        if not risky:
            replay = desc(n, obs)
        else:
            avg = sum(sp[t] for t in RISKY) / len(RISKY)
            replay = desc(n, union) if avg >= .97 else set(range(2, n))
    elif policy == "global_strict":
        if not risky:
            replay = desc(n, obs)
        else:
            replay = desc(n, union) if min(sp[t] for t in RISKY) >= 1.0 else set(range(2, n))
    elif policy == "classaware_strict":
        if not risky:
            replay = desc(n, obs)
        else:
            replay = desc(n, union) if all(sp[t] >= 1.0 for t in risky) else set(range(2, n))
    missing = set(affected) - replay
    benign = set(independent) & replay
    return {
        "correct": int(not missing),
        "cost": 1 + len(replay),
        "preserved": (len(independent) - len(benign)) / len(independent),
        "benign_over": len(benign),
    }

def main():
    N = 3000
    for static_name in STATIC_PROFILES:
        for fp in (.02, .10, .30):
            print(f"\nstatic={static_name} fp={fp}")
            for policy in POLICIES:
                rs = [run_one(g, static_name, fp, policy) for g in range(N)]
                correct = sum(x["correct"] for x in rs)
                cost = sum(x["cost"] for x in rs)
                print(
                    policy,
                    f"recovery={correct/N:.4f}",
                    f"mean_cost={cost/N:.4f}",
                    f"preserved={sum(x['preserved'] for x in rs)/N:.4f}",
                    f"correct_per_100k={100000*correct/cost:.2f}",
                )
if __name__ == "__main__":
    main()
