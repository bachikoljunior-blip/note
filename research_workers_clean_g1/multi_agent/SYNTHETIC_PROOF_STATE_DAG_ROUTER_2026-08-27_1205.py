import hashlib, math, random
from collections import defaultdict

G = 1200
SRECS = [0.60, 0.80, 0.90, 0.97, 1.00]
SFPS = [0.00, 0.05, 0.15, 0.30]


def seed_int(*parts):
    s = "|".join(map(str, parts)).encode()
    return int(hashlib.sha256(s).hexdigest()[:16], 16)


def descendants(n, edges, src):
    adj = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
    seen, stack = set(), [src]
    while stack:
        u = stack.pop()
        for v in adj[u]:
            if v not in seen:
                seen.add(v)
                stack.append(v)
    return seen


def gen_graph(gid):
    rng = random.Random(seed_int("dag", gid))
    n = rng.randint(16, 34)
    names = ["proved_new_version", "overcaptured", "known_uncaptured", "unknown"]
    probs = [0.58, 0.16, 0.13, 0.13]
    states = []
    for _ in range(n):
        x, c = rng.random(), 0.0
        for name, p in zip(names, probs):
            c += p
            if x < c:
                states.append(name)
                break
    states[0] = "proved_new_version"

    mids = sorted(rng.sample(range(1, n - 1), rng.randint(3, min(7, n - 2))))
    true_edges = set(zip([0] + mids, mids + [n - 1]))
    p0 = rng.uniform(0.05, 0.12)
    for i in range(n - 1):
        for j in range(i + 1, n):
            if (i, j) in true_edges:
                continue
            if rng.random() < p0 * math.exp(-0.05 * (j - i - 1)):
                true_edges.add((i, j))

    ancestors = [s for s in range(n - 1) if n - 1 in descendants(n, true_edges, s)]
    src = random.Random(seed_int("src", gid)).choice(ancestors)
    true_closure = descendants(n, true_edges, src)

    runtime, missing = set(), []
    for e in true_edges:
        if states[e[1]] in ("proved_new_version", "overcaptured"):
            runtime.add(e)
        else:
            missing.append(e)

    rtfp_rng = random.Random(seed_int("rtfp", gid))
    for v in range(1, n):
        if states[v] != "overcaptured":
            continue
        for u in range(v):
            e = (u, v)
            if e not in true_edges and rtfp_rng.random() < 0.08:
                runtime.add(e)

    srng = random.Random(seed_int("static", gid))
    miss_u = {e: srng.random() for e in missing}
    fp_u = {}
    for v in range(1, n):
        if states[v] not in ("known_uncaptured", "unknown"):
            continue
        for u in range(v):
            e = (u, v)
            if e not in true_edges and e not in runtime:
                fp_u[e] = srng.random()

    return {
        "gid": gid,
        "n": n,
        "states": states,
        "true": true_edges,
        "src": src,
        "true_closure": true_closure,
        "runtime": runtime,
        "obs_closure": descendants(n, runtime, src),
        "miss_u": miss_u,
        "fp_u": fp_u,
    }


def evaluate(g, srec, sfp, policy):
    static = {e for e, u in g["miss_u"].items() if u < srec}
    # sfp is a sweep parameter; 0.10 scaling keeps the synthetic FP density moderate.
    static |= {e for e, u in g["fp_u"].items() if u < sfp * 0.10}
    union_closure = descendants(g["n"], g["runtime"] | static, g["src"])
    if policy == "local":
        replay = g["obs_closure"]
    elif policy == "union":
        replay = union_closure
    elif policy == "whole":
        replay = set(range(g["n"])) - {g["src"]}
    else:
        raise ValueError(policy)

    stale = g["true_closure"] - replay
    benign = replay - g["true_closure"]
    independent = max(0, (g["n"] - 1) - len(g["true_closure"]))
    preserved = 1.0 if independent == 0 else max(0.0, 1.0 - len(benign) / independent)
    return {
        "success": not stale,
        "cost": 1 + len(replay),
        "stale": len(stale),
        "benign": len(benign),
        "replay": len(replay),
        "preserved": preserved,
    }


def summarize(graphs, srec, sfp, policy):
    rows = [evaluate(g, srec, sfp, policy) for g in graphs]
    succ = sum(r["success"] for r in rows)
    cost = sum(r["cost"] for r in rows)
    return {
        "recovery": succ / len(rows),
        "stale_run": sum(r["stale"] > 0 for r in rows) / len(rows),
        "mean_replay": sum(r["replay"] for r in rows) / len(rows),
        "mean_benign": sum(r["benign"] for r in rows) / len(rows),
        "preserved": sum(r["preserved"] for r in rows) / len(rows),
        "correct_per_100k": 100000.0 * succ / cost,
    }


def main():
    graphs = [gen_graph(gid) for gid in range(G)]
    print("graphs", len(graphs), "mean_n", sum(g["n"] for g in graphs) / G,
          "mean_true_closure", sum(len(g["true_closure"]) for g in graphs) / G)

    print("\nMain sweep")
    for srec in SRECS:
        for sfp in SFPS:
            for policy in ("local", "union", "whole"):
                print(srec, sfp, policy, summarize(graphs, srec, sfp, policy))

    print("\nFine recall cliff at sfp=0.15")
    for srec in (0.97, 0.98, 0.99, 0.995, 0.999, 1.0):
        print(srec, summarize(graphs, srec, 0.15, "union"))

    print("\nFP cost sweep at srec=1.0")
    for sfp in SFPS:
        print(sfp, summarize(graphs, 1.0, sfp, "union"))


if __name__ == "__main__":
    main()
