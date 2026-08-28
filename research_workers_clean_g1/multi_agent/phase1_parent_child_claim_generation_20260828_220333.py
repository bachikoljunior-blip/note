#!/usr/bin/env python3
"""
Finite parent/child claim-generation stress test for the Phase-1 multi-agent
concurrency assignment.

Scope:
- two required children A/B under one parent;
- optional parent supersession from generation 1 to generation 2;
- per-child current/stale completion patterns around lease takeover;
- all interleavings preserving each child's local completion order;
- overlapping-vs-disjoint exclusive effect declarations;
- deterministic-vs-nondeterministic merge declarations;
- a serialized single-CAS canonical integrator (so there are no lost-update
  races inside the model).

This is a mechanism enumerator, not an incidence estimator.
"""
from itertools import product
from collections import Counter
import json

PATTERNS = {
    "current_only": ["current"],
    "stale_then_current": ["stale", "current"],
    "current_then_stale": ["current", "stale"],
    "stale_only": ["stale"],
}

PROTOCOLS = [
    "coarse_parent_claim",
    "leaf_lease_only",
    "leaf_epoch_fenced",
]

def interleave(seq_a, seq_b):
    out = []
    def rec(i, j, acc):
        if i == len(seq_a) and j == len(seq_b):
            out.append(tuple(acc))
            return
        if i < len(seq_a):
            rec(i + 1, j, acc + [("A", seq_a[i], i)])
        if j < len(seq_b):
            rec(i, j + 1, acc + [("B", seq_b[j], j)])
    rec(0, 0, [])
    return out

def event_tag(child, kind, pattern, parent_is_generation_2):
    if parent_is_generation_2:
        if kind == "current":
            generation, epoch, strong = 2, 1, True
        else:
            generation, epoch, strong = 1, 1, False
    else:
        generation = 1
        if pattern == "current_only":
            epoch = 1
            strong = (kind == "current")
        else:
            epoch = 2 if kind == "current" else 1
            strong = (kind == "current")
    return {
        "child": child,
        "kind": kind,
        "generation": generation,
        "claim_epoch": epoch,
        "strong": strong,
        "digest": f"{child}:{kind}:g{generation}:e{epoch}:{pattern}",
    }

def simulate(protocol, pattern_a, pattern_b, events, supersede_pos,
             effect_overlap, deterministic_merge):
    current_generation = 1
    canonical = {"A": None, "B": None}
    pending = {"A": [], "B": []}
    out = Counter()
    flags = {
        "terminal_ever": False,
        "false_terminal": False,
        "duplicate_trace": False,
        "terminal_at_end": False,
        "strong_terminal_at_end": False,
    }

    def maybe_finalize():
        if canonical["A"] is None or canonical["B"] is None:
            return
        flags["terminal_ever"] = True
        strong = all(
            slot["generation"] == current_generation and slot["strong"]
            for slot in canonical.values()
        )
        if strong:
            out["safe_terminal_events"] += 1
        else:
            flags["false_terminal"] = True
            out["false_terminal_events"] += 1

    def coarse_drain():
        for child in ("A", "B"):
            if canonical[child] is None:
                idx = None
                for k, result in enumerate(pending[child]):
                    if result["generation"] == current_generation and result["strong"]:
                        idx = k
                        break
                if idx is not None:
                    canonical[child] = pending[child].pop(idx)
                    out["accepted_integrations"] += 1
            if child == "A" and canonical["A"] is None:
                break
        maybe_finalize()

    n = len(events)
    for pos in range(n + 1):
        if supersede_pos is not None and pos == supersede_pos:
            current_generation = 2
            canonical = {"A": None, "B": None}
            pending = {"A": [], "B": []}
            out["parent_supersessions"] += 1
        if pos == n:
            break

        child, kind, _local_index = events[pos]
        pattern = pattern_a if child == "A" else pattern_b
        result = event_tag(
            child, kind, pattern, parent_is_generation_2=(current_generation == 2)
        )

        if protocol == "coarse_parent_claim":
            pending[child].append(result)
            coarse_drain()
            continue

        if result["generation"] != current_generation:
            out["rejected_generation"] += 1
            continue

        if protocol == "leaf_epoch_fenced" and not result["strong"]:
            out["rejected_stale_epoch"] += 1
            continue

        if canonical[child] is not None and canonical[child]["digest"] != result["digest"]:
            flags["duplicate_trace"] = True
            out["duplicate_authoritative_integration_events"] += 1
        canonical[child] = result
        out["accepted_integrations"] += 1
        maybe_finalize()

    flags["terminal_at_end"] = (
        canonical["A"] is not None and canonical["B"] is not None
    )
    flags["strong_terminal_at_end"] = (
        flags["terminal_at_end"]
        and all(
            slot["generation"] == current_generation and slot["strong"]
            for slot in canonical.values()
        )
    )

    parallel_candidate = (
        protocol != "coarse_parent_claim"
        and "current" in PATTERNS[pattern_a]
        and "current" in PATTERNS[pattern_b]
    )
    parallel_admitted = (
        parallel_candidate and (not effect_overlap) and deterministic_merge
    )
    out["parallel_candidate"] += int(parallel_candidate)
    out["parallel_admitted"] += int(parallel_admitted)
    out["parallel_denied_any"] += int(
        parallel_candidate and not ((not effect_overlap) and deterministic_merge)
    )
    out["parallel_denied_effect_overlap"] += int(
        parallel_candidate and effect_overlap
    )
    out["parallel_denied_nondeterministic_merge"] += int(
        parallel_candidate and (not deterministic_merge)
    )
    out["epoch_fenced_ungated_unsafe_parallel_admission"] += int(
        protocol == "leaf_epoch_fenced"
        and parallel_candidate
        and (effect_overlap or not deterministic_merge)
    )
    return out, flags

def main():
    aggregates = {protocol: Counter() for protocol in PROTOCOLS}
    slices = {
        protocol: {"no_supersession": Counter(), "with_supersession": Counter()}
        for protocol in PROTOCOLS
    }
    examples = {protocol: {"false_terminal": None, "duplicate": None}
                for protocol in PROTOCOLS}
    total_scenarios = 0

    for pattern_a, pattern_b, effect_overlap, deterministic_merge in product(
        PATTERNS, PATTERNS, [False, True], [False, True]
    ):
        for events in interleave(PATTERNS[pattern_a], PATTERNS[pattern_b]):
            for supersede_pos in [None] + list(range(len(events) + 1)):
                total_scenarios += 1
                for protocol in PROTOCOLS:
                    counts, flags = simulate(
                        protocol, pattern_a, pattern_b, events, supersede_pos,
                        effect_overlap, deterministic_merge
                    )
                    agg = aggregates[protocol]
                    agg["scenarios"] += 1
                    agg.update(counts)
                    for name, value in flags.items():
                        agg[name] += int(value)

                    slice_name = (
                        "no_supersession" if supersede_pos is None
                        else "with_supersession"
                    )
                    sl = slices[protocol][slice_name]
                    sl["scenarios"] += 1
                    sl["terminal_ever"] += int(flags["terminal_ever"])
                    sl["false_terminal"] += int(flags["false_terminal"])
                    sl["duplicate_trace"] += int(flags["duplicate_trace"])
                    sl["terminal_at_end"] += int(flags["terminal_at_end"])
                    sl["strong_terminal_at_end"] += int(
                        flags["strong_terminal_at_end"]
                    )

                    scenario = {
                        "pattern_a": pattern_a,
                        "pattern_b": pattern_b,
                        "events": list(events),
                        "supersede_pos": supersede_pos,
                        "effect_overlap": effect_overlap,
                        "deterministic_merge": deterministic_merge,
                    }
                    if flags["false_terminal"] and examples[protocol]["false_terminal"] is None:
                        examples[protocol]["false_terminal"] = scenario
                    if flags["duplicate_trace"] and examples[protocol]["duplicate"] is None:
                        examples[protocol]["duplicate"] = scenario

    result = {
        "schema_version": 1,
        "model": "two-child parent claim-generation finite mechanism lattice",
        "scope": {
            "children": ["A", "B"],
            "required_children": 2,
            "parent_generations": [1, 2],
            "completion_patterns": list(PATTERNS),
            "effect_overlap": [False, True],
            "deterministic_merge": [False, True],
            "integrator": "single serialized CAS; no lost-update race modeled",
            "supersession": "none or inserted at every completion-boundary position",
            "interpretation": "equal-enumeration mechanism test; not real-world incidence",
        },
        "total_scenarios_per_protocol": total_scenarios,
        "protocols": {p: dict(aggregates[p]) for p in PROTOCOLS},
        "supersession_slices": {
            p: {k: dict(v) for k, v in slices[p].items()}
            for p in PROTOCOLS
        },
        "examples": examples,
        "derived": {
            "leaf_lease_only_false_terminal_among_terminal_ever": (
                aggregates["leaf_lease_only"]["false_terminal"]
                / aggregates["leaf_lease_only"]["terminal_ever"]
            ),
            "leaf_lease_only_duplicate_trace_among_terminal_ever": (
                aggregates["leaf_lease_only"]["duplicate_trace"]
                / aggregates["leaf_lease_only"]["terminal_ever"]
            ),
            "leaf_epoch_fenced_false_terminal": aggregates["leaf_epoch_fenced"]["false_terminal"],
            "leaf_epoch_fenced_duplicate_trace": aggregates["leaf_epoch_fenced"]["duplicate_trace"],
            "leaf_parallel_candidate": aggregates["leaf_epoch_fenced"]["parallel_candidate"],
            "leaf_parallel_admitted_after_effect_merge_gates": aggregates["leaf_epoch_fenced"]["parallel_admitted"],
            "leaf_parallel_denied_after_effect_merge_gates": aggregates["leaf_epoch_fenced"]["parallel_denied_any"],
            "epoch_fenced_without_parallel_gate_unsafe_admission": (
                aggregates["leaf_epoch_fenced"]["epoch_fenced_ungated_unsafe_parallel_admission"]
            ),
        },
    }
    print(json.dumps(result, indent=2, sort_keys=True))

if __name__ == "__main__":
    main()
