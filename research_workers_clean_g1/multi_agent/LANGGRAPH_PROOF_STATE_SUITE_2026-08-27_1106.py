from dataclasses import dataclass
from typing import FrozenSet, Tuple
import collections, hashlib, json, random

Edge = Tuple[str, str]  # source -> dependent

@dataclass(frozen=True)
class Case:
    name: str
    nodes: Tuple[str, ...]
    true_edges: FrozenSet[Edge]
    captured_edges: FrozenSet[Edge]
    static_edges: FrozenSet[Edge]
    proof_state: str
    evidence: str

SOURCE_BLOBS = {
    "auditable_langgraph_py": "37d115d221e4cab04fbb965a9b90c5ef6e475944",
    "auditable_langgraph_tests": "d66a479df5db21fd42b2a379719d16db5aec99c3",
    "auditable_architecture_md": "e13483297b646b139e2348b08ea90a6a314b6f3b",
}

CASES = [
    Case(
        "keyed_read",
        ("fund", "spend", "audit"),
        frozenset({("fund", "spend"), ("spend", "audit")}),
        frozenset({("fund", "spend"), ("spend", "audit")}),
        frozenset({("fund", "spend"), ("spend", "audit")}),
        "proved_new_version",
        "Keyed state access records the exact channel and the public integration test confirms overwrite writer matching.",
    ),
    Case(
        "whole_state_overcapture",
        ("seed_x", "seed_y", "consumer", "final"),
        frozenset({("seed_x", "consumer"), ("consumer", "final")}),
        frozenset({("seed_x", "consumer"), ("seed_y", "consumer"), ("consumer", "final")}),
        frozenset({("seed_x", "consumer"), ("seed_y", "consumer"), ("consumer", "final")}),
        "proved_new_version",
        "Whole-state iteration/copy records every channel and explicitly marks them overcaptured; this is modeled as a safety superset with lower precision.",
    ),
    Case(
        "uncaptured_runnable",
        ("seed_runnable", "use", "final"),
        frozenset({("seed_runnable", "use"), ("use", "final")}),
        frozenset({("use", "final")}),
        frozenset({("seed_runnable", "use"), ("use", "final")}),
        "known_uncaptured",
        "Runnable nodes pass through uncaptured and to_steps warns that the dependency graph may be incomplete.",
    ),
    Case(
        "conditional_routing_read",
        ("seed_route", "branch", "final"),
        frozenset({("seed_route", "branch"), ("branch", "final")}),
        frozenset({("branch", "final")}),
        frozenset({("seed_route", "branch"), ("branch", "final")}),
        "unknown",
        "Conditional-edge/Command.goto routing reads are outside v1 capture; the adapter does not observe this control dependency.",
    ),
    Case(
        "reducer_fanin",
        ("a", "b", "reader", "final"),
        frozenset({("a", "reader"), ("b", "reader"), ("reader", "final")}),
        frozenset({("a", "reader"), ("b", "reader"), ("reader", "final")}),
        frozenset({("a", "reader"), ("b", "reader"), ("reader", "final")}),
        "proved_new_version",
        "Reducer channels bind a reader to every committed writer; the public integration test confirms the fan-in.",
    ),
    Case(
        "parallel_siblings",
        ("fund", "branch_a", "branch_b", "merge", "final"),
        frozenset({
            ("fund", "branch_a"), ("fund", "branch_b"),
            ("branch_a", "merge"), ("branch_b", "merge"),
            ("merge", "final"),
        }),
        frozenset({
            ("fund", "branch_a"), ("fund", "branch_b"),
            ("branch_a", "merge"), ("branch_b", "merge"),
            ("merge", "final"),
        }),
        frozenset({
            ("fund", "branch_a"), ("fund", "branch_b"),
            ("branch_a", "merge"), ("branch_b", "merge"),
            ("merge", "final"),
        }),
        "proved_new_version",
        "Superstep-aware matching does not fabricate sibling dependencies; merge reads both committed branch outputs.",
    ),
]


def transitive_pairs(nodes, edges):
    adj = {n: set() for n in nodes}
    for a, b in edges:
        adj[a].add(b)
    out = set()
    for src in nodes:
        seen, stack = set(), list(adj[src])
        while stack:
            node = stack.pop()
            if node in seen:
                continue
            seen.add(node)
            out.add((src, node))
            stack.extend(adj[node] - seen)
    return out


def closure(nodes, edges, src):
    return {b for a, b in transitive_pairs(nodes, edges) if a == src}


def counts(true_set, pred_set):
    tp = len(true_set & pred_set)
    fp = len(pred_set - true_set)
    fn = len(true_set - pred_set)
    return {
        "tp": tp, "fp": fp, "fn": fn,
        "recall": tp / (tp + fn) if tp + fn else 1.0,
        "precision": tp / (tp + fp) if tp + fp else 1.0,
    }


def coverage_suite():
    rows = []
    for case in CASES:
        edge = counts(set(case.true_edges), set(case.captured_edges))
        desc = counts(
            transitive_pairs(case.nodes, case.true_edges),
            transitive_pairs(case.nodes, case.captured_edges),
        )
        rows.append({
            "case": case.name,
            "proof_state": case.proof_state,
            "edge": edge,
            "descendant_closure": desc,
            "evidence": case.evidence,
        })
    return rows


def policy_row(case, src, policy):
    true_desc = closure(case.nodes, case.true_edges, src)
    captured_desc = closure(case.nodes, case.captured_edges, src)
    static_desc = closure(case.nodes, case.static_edges, src)
    whole = set(case.nodes) - {src}
    if policy == "silent_local":
        replay = captured_desc
    elif policy == "fail_closed":
        replay = whole if case.proof_state in {"known_uncaptured", "unknown"} else captured_desc
    elif policy == "static_enlarge":
        if case.proof_state == "known_uncaptured":
            replay = whole
        elif case.proof_state == "unknown":
            replay = static_desc
        else:
            replay = captured_desc
    else:
        raise ValueError(policy)
    missing = true_desc - replay
    extra = replay - true_desc
    return {
        "recovery": 0.0 if missing else 1.0,
        "recurrence_proxy": len(missing) / len(true_desc) if true_desc else 0.0,
        "calls": 1 + len(replay),
        "benign_overreplay": len(extra),
    }


def policy_comparison():
    event_types = []
    for case in CASES:
        for src in case.nodes:
            if closure(case.nodes, case.true_edges, src) or closure(case.nodes, case.captured_edges, src) or closure(case.nodes, case.static_edges, src):
                event_types.append((case, src))
    out = []
    for policy in ("silent_local", "fail_closed", "static_enlarge"):
        rows = [policy_row(case, src, policy) for case, src in event_types]
        calls = sum(r["calls"] for r in rows)
        correct = sum(r["recovery"] for r in rows)
        out.append({
            "policy": policy,
            "event_types": len(rows),
            "recovery_rate": correct / len(rows),
            "mean_recurrence_proxy": sum(r["recurrence_proxy"] for r in rows) / len(rows),
            "mean_calls": calls / len(rows),
            "mean_benign_overreplay": sum(r["benign_overreplay"] for r in rows) / len(rows),
            "correct_endpoints_per_100_calls": 100.0 * correct / calls,
        })
    return out


def fixed_budget_comparison(budget=100000):
    event_types = []
    for case in CASES:
        for src in case.nodes:
            if closure(case.nodes, case.true_edges, src) or closure(case.nodes, case.captured_edges, src) or closure(case.nodes, case.static_edges, src):
                event_types.append((case, src))
    out = []
    for policy in ("silent_local", "fail_closed", "static_enlarge"):
        calls = processed = 0
        correct = recurrence = over = 0.0
        i = 0
        while True:
            case, src = event_types[i % len(event_types)]
            row = policy_row(case, src, policy)
            if calls + row["calls"] > budget:
                break
            calls += row["calls"]
            processed += 1
            correct += row["recovery"]
            recurrence += row["recurrence_proxy"]
            over += row["benign_overreplay"]
            i += 1
        out.append({
            "policy": policy,
            "budget": budget,
            "calls_used": calls,
            "events_processed": processed,
            "correct_endpoints": int(correct),
            "recovery_rate": correct / processed,
            "mean_recurrence_proxy": recurrence / processed,
            "mean_benign_overreplay": over / processed,
            "correct_endpoints_per_100k_calls": 100000.0 * correct / calls,
        })
    return out


def seeded_rng(*parts):
    digest = hashlib.sha256("|".join(map(str, parts)).encode()).digest()
    return random.Random(int.from_bytes(digest[:8], "big"))


def perturb(case, q_fn=0.0, q_fp=0.0, rep=0):
    rng = seeded_rng("langgraph-proof-suite-v1", case.name, q_fn, q_fp, rep)
    true = set(case.true_edges)
    pred = set()
    for edge in sorted(true):
        if rng.random() >= q_fn:
            pred.add(edge)
    order = {node: i for i, node in enumerate(case.nodes)}
    possible = {(a, b) for a in case.nodes for b in case.nodes if order[a] < order[b]} - true
    for edge in sorted(possible):
        if rng.random() < q_fp:
            pred.add(edge)
    return frozenset(pred)


def noise_sweep(kind, reps=2000):
    precise = [c for c in CASES if c.name in {"keyed_read", "reducer_fanin", "parallel_siblings"}]
    rows = []
    for q in (0.0, 0.05, 0.10, 0.20, 0.40):
        tp_e = fp_e = fn_e = tp_c = fp_c = fn_c = 0
        sums = collections.defaultdict(float)
        events = 0
        for case in precise:
            for rep in range(reps):
                pred = perturb(case, q_fn=q if kind == "fn" else 0.0, q_fp=q if kind == "fp" else 0.0, rep=rep)
                true = set(case.true_edges)
                tp_e += len(true & pred); fp_e += len(pred - true); fn_e += len(true - pred)
                tc = transitive_pairs(case.nodes, case.true_edges)
                pc = transitive_pairs(case.nodes, pred)
                tp_c += len(tc & pc); fp_c += len(pc - tc); fn_c += len(tc - pc)
                for src in case.nodes:
                    true_desc = closure(case.nodes, case.true_edges, src)
                    if not true_desc:
                        continue
                    pred_desc = closure(case.nodes, pred, src)
                    missing = true_desc - pred_desc
                    extra = pred_desc - true_desc
                    events += 1
                    sums["failure"] += bool(missing)
                    sums["recovery"] += not missing
                    sums["recurrence"] += len(missing) / len(true_desc)
                    sums["over"] += len(extra)
                    sums["calls"] += 1 + len(pred_desc)
        rows.append({
            "q": q,
            "edge_recall": tp_e / (tp_e + fn_e),
            "edge_precision": tp_e / (tp_e + fp_e) if tp_e + fp_e else 1.0,
            "closure_recall": tp_c / (tp_c + fn_c),
            "closure_precision": tp_c / (tp_c + fp_c) if tp_c + fp_c else 1.0,
            "stale_event_rate": sums["failure"] / events,
            "mean_recurrence_proxy": sums["recurrence"] / events,
            "mean_benign_overreplay": sums["over"] / events,
            "mean_calls": sums["calls"] / events,
            "correct_endpoints_per_100_calls": 100.0 * sums["recovery"] / sums["calls"],
        })
    return rows


def main():
    output = {
        "schema_version": 1,
        "study": "deterministic implementation-level LangGraph proof-state suite",
        "scope": "The six public cases are encoded from the pinned auditable source/tests; this script does not execute LangGraph or auditable itself. The FN/FP sweeps are synthetic mechanism tests over the three public precise-capture graph shapes.",
        "source_blobs": SOURCE_BLOBS,
        "coverage_suite": coverage_suite(),
        "policy_comparison": policy_comparison(),
        "fixed_100k_call_comparison": fixed_budget_comparison(),
        "false_negative_sweep": noise_sweep("fn"),
        "false_positive_sweep": noise_sweep("fp"),
    }
    print(json.dumps(output, indent=2, sort_keys=True))

if __name__ == "__main__":
    main()
