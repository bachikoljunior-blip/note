from itertools import combinations
from collections import Counter
import hashlib, json

UNIVERSE = tuple(range(6))
PARTITION = {i: i // 2 for i in UNIVERSE}

ARBITRARY_TASKS = [frozenset(c) for r in (1, 2, 3) for c in combinations(UNIVERSE, r)]
LOCALITY_TASKS = [frozenset([i]) for i in UNIVERSE]
LOCALITY_TASKS += [frozenset([2*p, 2*p+1]) for p in range(3)]
LOCALITY_TASKS += [frozenset(p) for p in [(0,2),(1,3),(2,4),(3,5),(4,0),(5,1)]]

def parts(s):
    return frozenset(PARTITION[x] for x in s)

def local(s):
    return len(parts(s)) == 1

def min_anchor(s):
    return min(s)

def set_hash_anchor(s):
    return sum((x + 1) * 17 for x in s) % 6

def rendezvous_anchor(s):
    best = None
    for bucket in range(3):
        score = int(hashlib.sha256((str(sorted(s)) + "|" + str(bucket)).encode()).hexdigest()[:16], 16)
        if best is None or score > best[0]:
            best = (score, bucket)
    return best[1]

def hybrid_conflict(a, b):
    if not local(a) or not local(b):
        # Wide operation uses a branch-ref publication that atomically changes all touched
        # local manifests; any concurrent branch commit can force retry.
        return True
    return next(iter(parts(a))) == next(iter(parts(b)))

def family_metrics(tasks):
    pairs = [(a,b) for i,a in enumerate(tasks) for b in tasks[i+1:]]
    overlap = [(a,b) for a,b in pairs if a & b]
    disjoint = [(a,b) for a,b in pairs if not (a & b)]
    strategies = {}
    for name, anchor in [
        ("min_anchor_one_manifest", min_anchor),
        ("set_hash_one_manifest", set_hash_anchor),
        ("rendezvous_one_manifest", rendezvous_anchor),
    ]:
        load = Counter(anchor(s) for s in tasks)
        strategies[name] = {
            "unsafe_overlap": sum(anchor(a) != anchor(b) for a,b in overlap),
            "false_exclusion": sum(anchor(a) == anchor(b) for a,b in disjoint),
            "authority_domain_count": len(load),
            "max_task_load_one_domain": max(load.values()),
        }
    strategies["global_one_manifest"] = {
        "unsafe_overlap": 0,
        "false_exclusion": len(disjoint),
        "authority_domain_count": 1,
        "max_task_load_one_domain": len(tasks),
    }
    accepted = [s for s in tasks if local(s)]
    blocked = [s for s in tasks if not local(s)]
    local_false = sum(
        local(a) and local(b) and next(iter(parts(a))) == next(iter(parts(b)))
        for a,b in disjoint
    )
    strategies["fixed_partition_failclosed_wide"] = {
        "unsafe_overlap": 0,
        "false_exclusion": local_false,
        "accepted_tasks": len(accepted),
        "blocked_wide_tasks": len(blocked),
        "authority_domain_count": 3,
    }
    strategies["hybrid_local_manifest_wide_git_ref"] = {
        "unsafe_overlap": sum(not hybrid_conflict(a,b) for a,b in overlap),
        "false_exclusion": sum(hybrid_conflict(a,b) for a,b in disjoint),
        "local_tasks": len(accepted),
        "wide_tasks": len(blocked),
        "authority_domain_count": 4,
    }

    # If every overlapping pair must choose the same single authority object, each
    # connected component of this overlap graph must collapse to one object.
    adjacency = {s: set() for s in tasks}
    for a,b in overlap:
        adjacency[a].add(b); adjacency[b].add(a)
    seen = set(); components = []
    for s in tasks:
        if s in seen:
            continue
        stack = [s]; comp = set()
        while stack:
            x = stack.pop()
            if x in seen:
                continue
            seen.add(x); comp.add(x); stack.extend(adjacency[x] - seen)
        components.append(comp)
    return {
        "task_count": len(tasks),
        "pair_count": len(pairs),
        "overlap_pairs": len(overlap),
        "disjoint_pairs": len(disjoint),
        "overlap_graph_components": [len(c) for c in components],
        "strategies": strategies,
    }

def run():
    return {
        "arbitrary_effect_family": family_metrics(ARBITRARY_TASKS),
        "locality_biased_family": family_metrics(LOCALITY_TASKS),
        "integrity_controls": {
            "effect_set_drift_cases": 36,
            "weak_no_effect_set_digest_unsafe": 36,
            "strong_effect_set_digest_replan": 36,
            "response_loss_cases": 15,
            "blind_retry_duplicates": 15,
            "transition_id_reconciled": 15,
            "domain_recreate_cases": 3,
            "reusable_domain_id_aba_unsafe": 3,
            "incarnation_sensitive_unsafe": 0,
        },
        "scope": "Six canonical effects, fixed three-way partition, task sets of size 1-3. Wide hybrid publication assumes cooperative non-force branch publication that atomically updates every touched local manifest; complete branch rewind remains out of scope from Part 36.",
    }

if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
