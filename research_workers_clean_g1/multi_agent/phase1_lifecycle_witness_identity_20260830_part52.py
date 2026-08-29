#!/usr/bin/env python3
"""Finite lifecycle-witness identity lattice for Phase-1 multi_agent Part 52.

The model separates:
1) conflating two distinct concurrent physical invocations into one durable witness; and
2) producing two durable receipts for one logical invocation after an ambiguous applied
   write followed by process loss/recovery.

The current role has no allowed scheduler-provided stable invocation ID semantic input.
Counts are mechanism-lattice counts, not production rates.
"""
from itertools import product
import json

DIMS = [
    "first_write_applied",
    "response_lost",
    "process_lost_after_response",
    "recovery_same_logical_invocation",
    "concurrent_distinct_invocation",
    "same_start_head",
    "same_clock_bucket",
    "scheduler_id_available",
]

STRATEGIES = [
    "random_nonce_path",
    "frozen_tuple_head_path",
    "tuple_content_hash_path",
    "wallclock_bucket_path",
    "scheduler_invocation_id_path",
]

def metrics(strategy, x):
    if strategy == "random_nonce_path":
        distinct_same_key = False
        recovery_same_key = not x["process_lost_after_response"]
        available = True
    elif strategy == "frozen_tuple_head_path":
        distinct_same_key = x["same_start_head"]
        recovery_same_key = not (x["process_lost_after_response"] and x["first_write_applied"])
        available = True
    elif strategy == "tuple_content_hash_path":
        distinct_same_key = True
        recovery_same_key = True
        available = True
    elif strategy == "wallclock_bucket_path":
        distinct_same_key = x["same_clock_bucket"]
        recovery_same_key = x["same_clock_bucket"] if x["process_lost_after_response"] else True
        available = True
    elif strategy == "scheduler_invocation_id_path":
        distinct_same_key = False
        recovery_same_key = True
        available = x["scheduler_id_available"]
    else:
        raise KeyError(strategy)

    conflation = available and x["concurrent_distinct_invocation"] and distinct_same_key
    ambiguous_crash_recovery = (
        x["first_write_applied"]
        and x["response_lost"]
        and x["process_lost_after_response"]
        and x["recovery_same_logical_invocation"]
    )
    duplicate_same_logical = available and ambiguous_crash_recovery and not recovery_same_key
    return available, conflation, duplicate_same_logical

def main():
    scenarios = [dict(zip(DIMS, bits)) for bits in product([False, True], repeat=len(DIMS))]
    out = {
        "schema_version": 1,
        "scope": "presemantic immutable lifecycle witness identity under concurrency/response loss",
        "scenario_count": len(scenarios),
        "strategy_evaluations": len(scenarios) * len(STRATEGIES),
        "dimensions": DIMS,
        "summary": {},
        "acceptance_scope": (
            "Without an allowed stable scheduler invocation ID, random nonce paths are suitable "
            "for immutable at-least-one repository-reaching attempt evidence when retries reuse "
            "the same in-memory nonce and existing-path is reconciled by exact readback. They are "
            "not an exactly-once scheduler invocation counter across process loss. Content-hash "
            "paths prove at-least-once per content/config but intentionally conflate distinct runs."
        ),
    }
    for strategy in STRATEGIES:
        vals = [metrics(strategy, x) for x in scenarios]
        out["summary"][strategy] = {
            "scenario_count": len(vals),
            "unavailable": sum(not a for a, _, _ in vals),
            "distinct_invocation_conflation": sum(c for _, c, _ in vals),
            "duplicate_same_logical_after_ambiguous_crash_recovery": sum(d for _, _, d in vals),
        }
    print(json.dumps(out, indent=2, sort_keys=True))

if __name__ == "__main__":
    main()
