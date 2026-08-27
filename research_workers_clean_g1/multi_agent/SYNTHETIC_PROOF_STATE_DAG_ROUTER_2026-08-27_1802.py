#!/usr/bin/env python3
"""
Deterministic mechanism study for proof-state-aware rollback routing.
Role-local clean synthetic experiment; not a production benchmark.

Generates 24-node DAGs with dependency surfaces:
proved, overcaptured, known_uncaptured, unknown.
Compares:
  local observed closure
  runtime ∪ static conservative union
  positive-proof-only router
  whole redraw
under matched replay-call budget while sweeping static-complement recall and FP rate.
"""
import hashlib, random, collections, statistics

N = 24
GRAPHS = 2500
STATIC_RECALLS = [0.70, 0.85, 0.95, 1.00]
STATIC_FPS = [0.02, 0.10, 0.30]
POLICIES = ["local", "union", "proof_router", "always_whole"]

def rng_for(*parts):
    h = hashlib.sha256("|".join(map(str, parts)).encode()).digest()
    return random.Random(int.from_bytes(h[:8], "big"))

def gen_dag(seed, n=N):
    r = rng_for("dag", seed)
    classes = ["proved", "overcaptured", "known_uncaptured", "unknown"]
    probs = [0.50, 0.15, 0.15, 0.20]
    edges = {}
    for j in range(1, n):
        k = 1 if j < 4 else r.choice([1, 1, 2, 2, 3])
        for i in r.sample(range(j), min(k, j)):
            edges[(i, j)] = r.choices(classes, probs)[0]
        if j >= 3 and r.random() < 0.25:
            i = r.randrange(j)
            edges[(i, j)] = r.choices(classes, probs)[0]
    return n, edges

def descendants(n, edge_set, src):
    adj = collections.defaultdict(list)
    for a, b in edge_set:
        adj[a].append(b)
    seen, stack = set(), [src]
    while stack:
        u = stack.pop()
        for v in adj.get(u, []):
            if v not in seen:
                seen.add(v)
                stack.append(v)
    return seen

def simulate_capture(seed, n, edges, static_recall, static_fp,
                     runtime_risky_recall=0.40, over_fp=0.08):
    r = rng_for("capture", seed, static_recall, static_fp)
    true = set(edges)
    observed = set()
    for e, cls in edges.items():
        if cls in ("proved", "overcaptured"):
            observed.add(e)
        elif r.random() < runtime_risky_recall:
            observed.add(e)
    candidates = [(i, j) for j in range(1, n) for i in range(j) if (i, j) not in true]
    for e in candidates:
        if r.random() < over_fp / max(1, n / 8):
            observed.add(e)
    static = set()
    for e in true:
        if e not in observed and r.random() < static_recall:
            static.add(e)
    for e in candidates:
        if e not in observed and r.random() < static_fp / max(1, n / 8):
            static.add(e)
    return observed, static

def affected_has_risky(edges, true_desc, src):
    for (a, b), cls in edges.items():
        if cls in ("known_uncaptured", "unknown") and (a == src or a in true_desc) and b in true_desc:
            return True
    return False

def evaluate(policy, n, edges, src, observed, static, static_recall):
    true = set(edges)
    td = descendants(n, true, src)
    od = descendants(n, observed, src)
    ud = descendants(n, observed | static, src)
    risky = affected_has_risky(edges, td, src)

    if policy == "local":
        replay = od
    elif policy == "union":
        replay = ud
    elif policy == "proof_router":
        if not risky:
            replay = od
        elif static_recall >= 0.999999:
            replay = ud
        else:
            replay = set(range(n)) - {src}
    elif policy == "always_whole":
        replay = set(range(n)) - {src}
    else:
        raise ValueError(policy)

    stale = len(td - replay)
    benign = len(replay - td)
    cost = 1 + len(replay)
    recovered = (stale == 0)
    independent_total = n - 1 - len(td)
    preserved_independent = max(0, independent_total - benign)
    return recovered, cost, stale, benign, preserved_independent

def run_condition(static_recall, static_fp):
    rows = {p: [] for p in POLICIES}
    for g in range(GRAPHS):
        n, edges = gen_dag(g)
        src = rng_for("src", g).randrange(0, max(1, n // 2))
        obs, stat = simulate_capture(g, n, edges, static_recall, static_fp)
        for p in POLICIES:
            rows[p].append(evaluate(p, n, edges, src, obs, stat, static_recall))
    out = {}
    for p, rs in rows.items():
        recovery = sum(x[0] for x in rs) / len(rs)
        mean_cost = statistics.mean(x[1] for x in rs)
        out[p] = {
            "recovery": recovery,
            "mean_cost": mean_cost,
            "stale_run_rate": sum(x[2] > 0 for x in rs) / len(rs),
            "mean_benign_over_replay": statistics.mean(x[3] for x in rs),
            "mean_preserved_independent": statistics.mean(x[4] for x in rs),
            "correct_endpoints_per_100k_cost": 100000 * recovery / mean_cost,
        }
    return out

def main():
    for sr in STATIC_RECALLS:
        for fp in STATIC_FPS:
            out = run_condition(sr, fp)
            print(f"\nstatic_recall={sr:.2f} static_fp={fp:.2f}")
            for p in POLICIES:
                x = out[p]
                print(
                    p,
                    f"recovery={x['recovery']:.4f}",
                    f"mean_cost={x['mean_cost']:.2f}",
                    f"correct/100k={x['correct_endpoints_per_100k_cost']:.1f}",
                    f"stale={x['stale_run_rate']:.4f}",
                    f"benign_over={x['mean_benign_over_replay']:.2f}",
                    f"preserved_independent={x['mean_preserved_independent']:.2f}",
                )

if __name__ == "__main__":
    main()
