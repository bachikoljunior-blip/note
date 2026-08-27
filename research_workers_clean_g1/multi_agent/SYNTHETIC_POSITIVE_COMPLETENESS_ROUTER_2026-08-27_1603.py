"""Deterministic clean-role mechanism study.

Models rollback routing over 30-node DAGs with dependency surfaces carrying
proof classes. It is NOT a measurement of any production agent framework.
All pseudo-randomness is SHA-256 seeded for reproducibility.
"""
import collections
import hashlib
import math
import random

N_GRAPHS = 5000
N = 30
SURFACES = ["keyed", "reducer", "handoff", "whole", "runnable", "routing", "dynamic_tool"]
WEIGHTS = [0.22, 0.14, 0.16, 0.10, 0.12, 0.14, 0.12]
RUNTIME_RECALL = {
    "keyed": 1.0,
    "reducer": 1.0,
    "handoff": 1.0,
    "whole": 1.0,
    "runnable": 0.0,
    "routing": 0.0,
    "dynamic_tool": 0.5,
}
PROOF_CLASS = {
    "keyed": "proved_new_version",
    "reducer": "proved_new_version",
    "handoff": "proved_new_version",
    "whole": "overcaptured",
    "runnable": "known_uncaptured",
    "routing": "unknown",
    "dynamic_tool": "unknown",
}
SAFE = {"proved_new_version", "overcaptured"}


def rng_for(*parts):
    h = hashlib.sha256("||".join(map(str, parts)).encode()).hexdigest()
    return random.Random(int(h[:16], 16))


def desc(edges, src):
    adj = [[] for _ in range(N)]
    for a, b in edges:
        adj[a].append(b)
    seen = set()
    stack = [src]
    while stack:
        u = stack.pop()
        for v in adj[u]:
            if v not in seen:
                seen.add(v)
                stack.append(v)
    return seen


def gen_graph(gid):
    r = rng_for("graph", gid)
    e = []
    p = 0.105
    for i in range(N - 1):
        for j in range(i + 1, N):
            prob = p * math.exp(-(j - i - 1) / 18)
            if r.random() < prob:
                e.append((i, j, r.choices(SURFACES, weights=WEIGHTS, k=1)[0]))
    for i in range(0, N - 1, 5):
        j = min(N - 1, i + r.randint(1, 4))
        if not any(a == i and b == j for a, b, _ in e):
            e.append((i, j, r.choices(SURFACES, weights=WEIGHTS, k=1)[0]))
    candidates = [i for i in range(N // 2) if len(desc([(a, b) for a, b, _ in e], i)) >= 2]
    return e, r.choice(candidates) if candidates else 0


def runtime_graph(gid, true_edges):
    r = rng_for("runtime", gid)
    obs = set()
    true_pairs = {(a, b) for a, b, _ in true_edges}
    for a, b, s in true_edges:
        if r.random() < RUNTIME_RECALL[s]:
            obs.add((a, b))
    # whole-state reads may conservatively overcapture unrelated writers
    whole_targets = {b for a, b, s in true_edges if s == "whole"}
    for a in range(N - 1):
        for b in range(a + 1, N):
            if (a, b) not in true_pairs and b in whole_targets and r.random() < 0.01:
                obs.add((a, b))
    return obs


def static_graph(gid, true_edges, recall, fp_load):
    r = rng_for("static", gid, recall, fp_load)
    true_pairs = {(a, b) for a, b, _ in true_edges}
    out = set()
    for a, b, _ in true_edges:
        if r.random() < recall:
            out.add((a, b))
    nonedges = [(a, b) for a in range(N - 1) for b in range(a + 1, N) if (a, b) not in true_pairs]
    # fp_load = expected number of static false edges / number of true edges
    q = min(1.0, fp_load * len(true_pairs) / max(1, len(nonedges)))
    for a, b in nonedges:
        if r.random() < q:
            out.add((a, b))
    return out


def affected_classes(true_edges, src, true_desc):
    reachable = {src} | true_desc
    return {
        PROOF_CLASS[s]
        for a, b, s in true_edges
        if a in reachable and b in true_desc
    }


def run(static_recall, fp_load=0.0):
    names = ["local", "warning_failclosed", "union", "positive_proof", "whole"]
    counts = {p: collections.Counter() for p in names}
    sums = {p: collections.defaultdict(float) for p in names}
    subset = collections.Counter()
    for gid in range(N_GRAPHS):
        true_edges, src = gen_graph(gid)
        true_pairs = [(a, b) for a, b, _ in true_edges]
        td = desc(true_pairs, src)
        rt = runtime_graph(gid, true_edges)
        st = static_graph(gid, true_edges, static_recall, fp_load)
        local = desc(rt, src)
        union = desc(rt | st, src)
        whole = set(range(N)) - {src}
        classes = affected_classes(true_edges, src, td)
        has_known = "known_uncaptured" in classes
        has_unknown = "unknown" in classes
        safe = classes.issubset(SAFE)
        subset[("no_known", "unknown" if has_unknown else "no_unknown")] += int(not has_known)
        subset[("known", "unknown" if has_unknown else "no_unknown")] += int(has_known)
        policies = {
            "local": local,
            # warnings help only for known blind spots; silent unknown surfaces remain risky
            "warning_failclosed": whole if has_known else local,
            "union": union,
            "whole": whole,
        }
        if safe:
            policies["positive_proof"] = local
        elif static_recall == 1.0:
            # synthetic positive contract: the static complement is complete for this run family
            policies["positive_proof"] = union
        else:
            policies["positive_proof"] = whole
        all_nontrue = whole - td
        for name, replay in policies.items():
            recovered = td.issubset(replay)
            cost = 1 + len(replay)
            counts[name]["events"] += 1
            counts[name]["recovered"] += int(recovered)
            sums[name]["cost"] += cost
            sums[name]["replay"] += len(replay)
            sums[name]["stale"] += len(td - replay) / len(td)
            sums[name]["over"] += len(replay - td)
            sums[name]["preserved"] += len(all_nontrue - replay) / max(1, len(all_nontrue))
    rows = []
    for name in names:
        ev = counts[name]["events"]
        rows.append({
            "policy": name,
            "recovery": counts[name]["recovered"] / ev,
            "mean_replay": sums[name]["replay"] / ev,
            "mean_stale_fraction": sums[name]["stale"] / ev,
            "mean_benign_overreplay": sums[name]["over"] / ev,
            "independent_work_preserved": sums[name]["preserved"] / ev,
            "correct_endpoints_per_100k_calls": counts[name]["recovered"] / sums[name]["cost"] * 100000,
        })
    return rows


if __name__ == "__main__":
    for recall in (0.90, 0.97, 0.99, 0.995, 1.0):
        print("static_recall", recall)
        for row in run(recall, 0.0):
            print(row)
    print("complete-static false-positive load sweep")
    for fp in (0.0, 0.25, 1.0):
        print("fp_load", fp)
        for row in run(1.0, fp):
            if row["policy"] in ("union", "positive_proof"):
                print(row)
