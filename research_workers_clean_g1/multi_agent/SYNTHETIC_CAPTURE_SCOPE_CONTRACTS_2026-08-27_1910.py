#!/usr/bin/env python3
"""
Synthetic mechanism study: capture-scope contracts vs dependency-closure proof.

This is NOT a production benchmark and its numeric thresholds are not generalizable.
It compares rollback routing policies under fixed deterministic DAG/fault distributions.

Key distinction:
  - artifact/chain validity
  - capture-scope completeness
  - dependency-edge / descendant-closure completeness

Run:
  python SYNTHETIC_CAPTURE_SCOPE_CONTRACTS_2026-08-27_1910.py
"""

import random
from collections import defaultdict, Counter

SURFACES = [
    "handoff", "shared_memory", "reducer", "conditional_routing",
    "dynamic_tool", "custom_wrapper", "reflection",
    "runtime_tool", "topology_epoch",
]

RUNTIME_RECALL = {
    "handoff": 0.99,
    "shared_memory": 0.98,
    "reducer": 0.98,
    "conditional_routing": 0.92,
    "dynamic_tool": 0.88,
    "custom_wrapper": 0.72,
    "reflection": 0.68,
    "runtime_tool": 0.94,
    "topology_epoch": 0.95,
}

STATIC_RECALL = {
    "handoff": 0.98,
    "shared_memory": 0.97,
    "reducer": 0.97,
    "conditional_routing": 1.00,
    "dynamic_tool": 0.90,
    "custom_wrapper": 0.72,
    "reflection": 0.58,
    "runtime_tool": 0.70,
    "topology_epoch": 0.85,
}

# Surfaces for which the synthetic deployment can issue a positive
# dependency-edge / descendant-closure completeness contract.
CLOSURE_COMPLETE_SURFACE = {
    "handoff": True,
    "shared_memory": True,
    "reducer": True,
    "conditional_routing": True,
    "dynamic_tool": False,
    "custom_wrapper": False,
    "reflection": False,
    "runtime_tool": False,
    "topology_epoch": False,
}

STATIC_COMPLETE_SURFACE = {
    "handoff": True,
    "shared_memory": True,
    "reducer": True,
    "conditional_routing": True,
    "dynamic_tool": False,
    "custom_wrapper": False,
    "reflection": False,
    "runtime_tool": False,
    "topology_epoch": False,
}

SURFACE_WEIGHTS = [
    ("handoff", 0.25),
    ("shared_memory", 0.20),
    ("reducer", 0.15),
    ("conditional_routing", 0.12),
    ("dynamic_tool", 0.10),
    ("custom_wrapper", 0.08),
    ("reflection", 0.06),
    ("runtime_tool", 0.025),
    ("topology_epoch", 0.015),
]

POLICIES = [
    "absence_safe",
    "warning_only",
    "empirical_union",
    "manifest_pseudo",
    "capture_scope_only",
    "closure_proof_only",
    "conservative_enlargement",
    "whole",
]


def sample_surface(rng):
    x = rng.random()
    total = 0.0
    for name, weight in SURFACE_WEIGHTS:
        total += weight
        if x < total:
            return name
    return SURFACE_WEIGHTS[-1][0]


def closure_from(source, adjacency):
    seen = set()
    stack = [source]
    while stack:
        u = stack.pop()
        for v in adjacency.get(u, ()):
            if v not in seen:
                seen.add(v)
                stack.append(v)
    return seen


def make_graph(seed, n=30):
    rng = random.Random(seed)
    edges = []
    adjacency = defaultdict(set)

    # Short-range backbone.
    for i in range(n - 1):
        if rng.random() < 0.75:
            j = rng.randint(i + 1, min(n - 1, i + 4))
            surface = sample_surface(rng)
            edges.append((i, j, surface))
            adjacency[i].add(j)

    # Sparse longer-range dependency edges.
    for i in range(n):
        for j in range(i + 2, n):
            if rng.random() < 0.035:
                surface = sample_surface(rng)
                edges.append((i, j, surface))
                adjacency[i].add(j)

    source = rng.randint(0, min(7, n - 2))
    true_closure = closure_from(source, adjacency)

    if not true_closure:
        j = min(n - 1, source + 1)
        edges.append((source, j, "handoff"))
        adjacency[source].add(j)
        true_closure = closure_from(source, adjacency)

    return n, edges, source, true_closure


def simulate(seed, mediated_deployment):
    rng = random.Random(seed * 1_000_003 + 97)
    n, edges, source, true_closure = make_graph(seed)
    active_surfaces = {surface for _, _, surface in edges}

    declared = {s: True for s in (
        "handoff", "shared_memory", "reducer", "conditional_routing"
    )}
    mediated = {s: True for s in declared}
    known_unmediated = set()
    unknown = set()
    warnings = set()
    epoch_current = True

    # Dynamic surfaces. In the mediated deployment they must pass the
    # registration / capture boundary. In the weak deployment they may be
    # declared, known-unmediated, or silently absent from inventory.
    for surface in ("dynamic_tool", "custom_wrapper", "reflection"):
        if surface not in active_surfaces:
            continue
        if mediated_deployment:
            declared[surface] = True
            mediated[surface] = True
        else:
            p_declared = {
                "dynamic_tool": 0.86,
                "custom_wrapper": 0.68,
                "reflection": 0.62,
            }[surface]
            if rng.random() < p_declared:
                declared[surface] = True
                p_mediated = {
                    "dynamic_tool": 0.82,
                    "custom_wrapper": 0.58,
                    "reflection": 0.52,
                }[surface]
                if rng.random() < p_mediated:
                    mediated[surface] = True
                else:
                    mediated[surface] = False
                    known_unmediated.add(surface)
            else:
                declared[surface] = False
                mediated[surface] = False
                unknown.add(surface)

    if "runtime_tool" in active_surfaces:
        if mediated_deployment or rng.random() < 0.84:
            declared["runtime_tool"] = True
            mediated["runtime_tool"] = True
        else:
            declared["runtime_tool"] = False
            mediated["runtime_tool"] = False
            unknown.add("runtime_tool")

    if "topology_epoch" in active_surfaces:
        if mediated_deployment or rng.random() < 0.90:
            declared["topology_epoch"] = True
            mediated["topology_epoch"] = True
        else:
            if rng.random() < 0.60:
                declared["topology_epoch"] = True
                mediated["topology_epoch"] = False
                known_unmediated.add("topology_epoch")
                epoch_current = False
                warnings.add("epoch_stale")
            else:
                declared["topology_epoch"] = False
                mediated["topology_epoch"] = False
                unknown.add("topology_epoch")

    observed = defaultdict(set)
    static = defaultdict(set)
    captured_edges = []

    for u, v, surface in edges:
        if mediated.get(surface, False):
            # A truthful positive completeness contract means deterministic
            # capture for the surface. Other surfaces retain empirical recall.
            if mediated_deployment and CLOSURE_COMPLETE_SURFACE[surface]:
                runtime_p = 1.0
            else:
                runtime_p = RUNTIME_RECALL[surface]
        else:
            runtime_p = 0.0

        if rng.random() < runtime_p:
            observed[u].add(v)
            captured_edges.append((u, v, surface))

        if rng.random() < STATIC_RECALL[surface]:
            static[u].add(v)

    # Conservative static overcapture.
    true_pairs = {(u, v) for u, v, _ in edges}
    for u in range(n):
        for v in range(u + 1, n):
            if (u, v) not in true_pairs and rng.random() < 0.008:
                static[u].add(v)

    # Authenticated epoch-close checkpoint.
    close_checkpoint_present = rng.random() < 0.86

    # In-stream receipt / chain fault.
    fault = rng.choices(
        ["none", "omission", "duplicate", "out_of_order", "tail_truncation"],
        weights=[0.78, 0.07, 0.05, 0.04, 0.06],
        k=1,
    )[0]

    if fault == "omission" and captured_edges:
        u, v, _ = rng.choice(captured_edges)
        observed[u].discard(v)
        warnings.add("chain_sequence_gap")
    elif fault == "duplicate":
        warnings.add("chain_sequence_duplicate")
    elif fault == "out_of_order":
        warnings.add("chain_order_or_link")
    elif fault == "tail_truncation" and captured_edges:
        k = max(1, int(len(captured_edges) * 0.12))
        for u, v, _ in captured_edges[-k:]:
            observed[u].discard(v)
        # Without an authenticated checkpoint, presented-set validity cannot
        # establish that a withheld tail existed.
        if close_checkpoint_present:
            warnings.add("checkpoint_head_conflict")

    if known_unmediated:
        warnings.add("known_unmediated")

    # Coarse external activity sentinel in the weak deployment. This is only
    # a probabilistic detector, not a completeness proof.
    if unknown and rng.random() < 0.95:
        warnings.add("unregistered_activity")

    observed_closure = closure_from(source, observed)
    static_closure = closure_from(source, static)
    union_closure = observed_closure | static_closure

    affected_surfaces = {
        surface for u, _, surface in edges
        if u == source or u in true_closure
    }

    chain_structural_ok = not any(
        item in warnings for item in (
            "chain_sequence_gap",
            "chain_sequence_duplicate",
            "chain_order_or_link",
            "checkpoint_head_conflict",
        )
    )

    # Deliberately incorrect: absence of a warning is treated as proof.
    manifest_pseudo = (
        epoch_current
        and not known_unmediated
        and chain_structural_ok
    )

    # Positive capture-scope proof. This establishes that all allowed dynamic
    # surfaces must pass a mediated boundary and that the chain was closed,
    # but says nothing yet about descendant-closure completeness.
    capture_scope_proof = (
        mediated_deployment
        and close_checkpoint_present
        and epoch_current
        and not known_unmediated
        and chain_structural_ok
    )

    # Stronger positive proof: capture scope + every dependency surface in
    # the affected component has a complete edge/closure contract.
    descendant_closure_proof = (
        capture_scope_proof
        and all(
            CLOSURE_COMPLETE_SURFACE.get(surface, False)
            for surface in affected_surfaces
        )
    )

    conservative_union_allowed = (
        not unknown
        and chain_structural_ok
        and all(
            STATIC_COMPLETE_SURFACE.get(surface, False)
            for surface in affected_surfaces
        )
    )

    return {
        "n": n,
        "source": source,
        "true_closure": true_closure,
        "observed_closure": observed_closure,
        "static_closure": static_closure,
        "union_closure": union_closure,
        "warnings": warnings,
        "manifest_pseudo": manifest_pseudo,
        "capture_scope_proof": capture_scope_proof,
        "descendant_closure_proof": descendant_closure_proof,
        "conservative_union_allowed": conservative_union_allowed,
    }


def replay_set(run, policy):
    whole = set(range(run["n"])) - {run["source"]}

    if policy == "absence_safe":
        return set(run["observed_closure"])
    if policy == "warning_only":
        return whole if run["warnings"] else set(run["observed_closure"])
    if policy == "empirical_union":
        return set(run["union_closure"])
    if policy == "manifest_pseudo":
        return (
            set(run["union_closure"])
            if run["manifest_pseudo"]
            else whole
        )
    if policy == "capture_scope_only":
        return (
            set(run["union_closure"])
            if run["capture_scope_proof"]
            else whole
        )
    if policy == "closure_proof_only":
        return (
            set(run["union_closure"])
            if run["descendant_closure_proof"]
            else whole
        )
    if policy == "conservative_enlargement":
        if run["descendant_closure_proof"]:
            return set(run["union_closure"])
        if run["conservative_union_allowed"] and not run["warnings"]:
            return set(run["union_closure"])
        return whole
    if policy == "whole":
        return whole

    raise ValueError(policy)


def evaluate(n_runs=30_000, mediated_deployment=False):
    aggregate = {policy: [0, 0] for policy in POLICIES}
    proof_counts = Counter()

    for seed in range(n_runs):
        run = simulate(seed, mediated_deployment)

        proof_counts["manifest_pseudo"] += int(run["manifest_pseudo"])
        proof_counts["capture_scope"] += int(run["capture_scope_proof"])
        proof_counts["descendant_closure"] += int(
            run["descendant_closure_proof"]
        )

        for policy in POLICIES:
            replay = replay_set(run, policy)
            correct = run["true_closure"].issubset(replay)
            aggregate[policy][0] += int(correct)
            aggregate[policy][1] += len(replay)

    rows = []
    for policy in POLICIES:
        correct, cost = aggregate[policy]
        recovery = correct / n_runs
        mean_cost = cost / n_runs
        correct_per_100k = (correct / cost * 100_000) if cost else 0.0
        rows.append((policy, recovery, mean_cost, correct_per_100k))

    return rows, proof_counts


def print_table(name, rows, proofs, n_runs):
    print(f"\n{name}")
    print("policy,recovery,mean_replay_cost,correct_endpoints_per_100k_cost")
    for policy, recovery, cost, efficiency in rows:
        print(f"{policy},{recovery:.6f},{cost:.6f},{efficiency:.3f}")
    print("proof_counts", dict(proofs), "n_runs", n_runs)


if __name__ == "__main__":
    n_runs = 30_000
    weak_rows, weak_proofs = evaluate(n_runs, mediated_deployment=False)
    mediated_rows, mediated_proofs = evaluate(
        n_runs, mediated_deployment=True
    )

    print_table("WEAK / NON-COMPLETE CAPTURE BOUNDARY",
                weak_rows, weak_proofs, n_runs)
    print_table("MANDATORY MEDIATED SURFACE REGISTRY",
                mediated_rows, mediated_proofs, n_runs)
