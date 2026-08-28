from dataclasses import dataclass
from itertools import combinations, product, permutations

def greedy_mis(n, edges):
    edge_set = {tuple(sorted(e)) for e in edges}
    selected = []
    for v in range(n):
        if all(tuple(sorted((v, u))) not in edge_set for u in selected):
            selected.append(v)
    return selected

@dataclass(frozen=True)
class Head:
    hid: str
    policy: int
    writes: tuple

def reconcile(heads):
    hs = sorted(heads, key=lambda h: h.hid)
    policies = {h.policy for h in hs}
    if len(policies) != 1:
        return ("AMBIGUOUS_POLICY", tuple(h.hid for h in hs))
    merged = {}
    for h in hs:
        for k, v in h.writes:
            if k in merged and merged[k] != v:
                return ("AMBIGUOUS_OVERLAP", k, merged[k], v, tuple(h.hid for h in hs))
            merged[k] = v
    return ("RESOLVED", tuple(sorted(merged.items())), tuple(h.hid for h in hs))

def mkhead(hid, policy, a, b):
    w = []
    if a is not None:
        w.append(("a", a))
    if b is not None:
        w.append(("b", b))
    return Head(hid, policy, tuple(w))

def minimal_hitting_sets(family):
    universe = sorted(set().union(*family)) if family else []
    hits = []
    for r in range(len(universe) + 1):
        for comb in combinations(universe, r):
            H = set(comb)
            if all(H & set(B) for B in family):
                if not any(set(prev).issubset(H) for prev in hits):
                    hits.append(tuple(comb))
    return tuple(hits)

def cas_update(current_token, expected_token, new_value):
    if current_token != expected_token:
        return current_token, False
    return new_value, True

def owner_cas(record, expected_owner, expected_generation, target_owner):
    owner, generation = record
    if (owner, generation) != (expected_owner, expected_generation):
        return record, False
    return (target_owner, generation + 1), True

def valid_transition(state, event):
    if state == "start":
        return {
            "direct_solved": "solved",
            "direct_blocked": "blocked",
            "direct_hardstop": "stopped",
        }.get(event)
    if state == "blocked":
        return {"decompose": "decomposed", "checkpoint": "stopped"}.get(event)
    if state == "solved":
        return {"complete": "completed", "checkpoint": "stopped"}.get(event)
    if state == "decomposed":
        return {"checkpoint": "stopped"}.get(event)
    return None

def main():
    counts = {}

    mis_cases = 0
    for n in range(1, 7):
        all_edges = list(combinations(range(n), 2))
        for mask in range(1 << len(all_edges)):
            edges = [all_edges[i] for i in range(len(all_edges)) if (mask >> i) & 1]
            selected = greedy_mis(n, edges)
            edge_set = {tuple(sorted(e)) for e in edges}
            assert all(tuple(sorted((a, b))) not in edge_set for a, b in combinations(selected, 2))
            for v in range(n):
                if v not in selected:
                    assert any(tuple(sorted((v, u))) in edge_set for u in selected)
            mis_cases += 1
    counts["conflict_graphs_n_le_6"] = mis_cases

    vals = [None, 0, 1]
    reconcile_cases = 0
    for p1, p2, p3 in product([1, 2], repeat=3):
        for a1, b1, a2, b2, a3, b3 in product(vals, repeat=6):
            heads = [
                mkhead("h1", p1, a1, b1),
                mkhead("h2", p2, a2, b2),
                mkhead("h3", p3, a3, b3),
            ]
            baseline = reconcile(heads)
            for perm in permutations(heads):
                assert reconcile(perm) == baseline
            if baseline[0] == "RESOLVED":
                assert len({h.policy for h in heads}) == 1
                for key in ("a", "b"):
                    assigned = [dict(h.writes)[key] for h in heads if key in dict(h.writes)]
                    assert len(set(assigned)) <= 1
            reconcile_cases += 1
    counts["three_head_reconciliation_cases"] = reconcile_cases

    universe = ["a", "b", "c", "d"]
    subsets = [
        frozenset(s)
        for r in range(1, len(universe) + 1)
        for s in combinations(universe, r)
    ]
    hyper_cases = 0
    for k in range(1, 5):
        for fam in combinations(subsets, k):
            out = minimal_hitting_sets(fam)
            assert out == minimal_hitting_sets(tuple(reversed(fam)))
            for Ht in out:
                H = set(Ht)
                assert all(H & set(B) for B in fam)
                for x in list(H):
                    H2 = H - {x}
                    assert not all(H2 & set(B) for B in fam)
            hyper_cases += 1
    counts["blocker_hypergraphs"] = hyper_cases

    events = [
        "direct_solved", "direct_blocked", "direct_hardstop",
        "decompose", "checkpoint", "complete",
    ]
    trace_cases = 0
    for length in range(1, 5):
        for trace in product(events, repeat=length):
            state = "start"
            history = []
            valid = True
            for event in trace:
                nxt = valid_transition(state, event)
                if nxt is None:
                    valid = False
                    break
                history.append(event)
                state = nxt
            if valid:
                if "decompose" in history:
                    i = history.index("decompose")
                    assert "direct_blocked" in history[:i]
                    assert "direct_solved" not in history[:i]
                trace_cases += 1
    counts["valid_direct_reasoning_traces_len_le_4"] = trace_cases

    cas_cases = 0
    tokens = ["A", "B", "C"]
    for initial, current, new in product(tokens, repeat=3):
        out, ok = cas_update(current, initial, new)
        if current != initial:
            assert not ok and out == current
        else:
            assert ok and out == new
        cas_cases += 1
    counts["pointer_cas_cases"] = cas_cases

    handoff_cases = 0
    recipients = ["T1", "T2", "T3"]
    for order in permutations(recipients):
        record = ("S", 7)
        successes = []
        for target in order:
            record, ok = owner_cas(record, "S", 7, target)
            if ok:
                successes.append(target)
        assert len(successes) == 1
        assert record == (order[0], 8)
        assert 7 < record[1]
        handoff_cases += 1
    counts["handoff_race_orders"] = handoff_cases

    print(counts)

if __name__ == "__main__":
    main()
