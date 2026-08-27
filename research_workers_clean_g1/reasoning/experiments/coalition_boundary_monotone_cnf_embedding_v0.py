#!/usr/bin/env python3
"""Sanity-check the exact embedding of subsumption-minimal monotone CNF into the upper-Shapley boundary CNF family.

For variable universe U and a positive clause S, set Z = U \\ S. Then
  OR_{j in S} x_j
is false exactly on assignments T subseteq Z, i.e. exactly the down-set excluded by an upper-slice zero boundary point Z. After subsumption reduction, positive clauses form an inclusion antichain and their complements are exactly a maximal-zero antichain.
"""
import json
import random

SEED = 9921
CASES_PER_M = 1000
MAX_M = 8

def reduce_positive_clauses(clauses):
    out = []
    for c in sorted(set(clauses), key=lambda x: (x.bit_count(), x)):
        if any((d & ~c) == 0 for d in out):
            continue
        out.append(c)
    return out

def reduce_maximal(masks):
    out = []
    for s in sorted(set(masks), key=lambda x: (-x.bit_count(), -x)):
        if any((s & ~t) == 0 for t in out):
            continue
        out.append(s)
    return out

def cnf_value(mask, clauses):
    return int(all(mask & c for c in clauses))

def boundary_value(mask, b0):
    return int(not any((mask & ~z) == 0 for z in b0))

def main():
    rng = random.Random(SEED)
    cases = 0
    assignments = 0
    mismatches = 0
    for m in range(1, MAX_M + 1):
        full = (1 << m) - 1
        for _ in range(CASES_PER_M):
            raw = [rng.randrange(1, 1 << m) for _ in range(rng.randint(1, 12))]
            clauses = reduce_positive_clauses(raw)
            b0 = [full ^ c for c in clauses]
            if set(b0) != set(reduce_maximal(b0)):
                mismatches += 1
            for mask in range(1 << m):
                assignments += 1
                if cnf_value(mask, clauses) != boundary_value(mask, b0):
                    mismatches += 1
            cases += 1
    print(json.dumps({
        "schema": "coalition_boundary_monotone_cnf_embedding_v0_results",
        "seed": SEED,
        "max_variables": MAX_M,
        "cases": cases,
        "assignments_checked": assignments,
        "mismatches": mismatches,
        "passed": mismatches == 0,
        "scope": "Exhaustive truth-table check within each generated case; random over clause families, not an exhaustive enumeration of all CNFs. The embedding itself follows algebraically from clause falsification = subset of complement."
    }, sort_keys=True, indent=2))

if __name__ == "__main__":
    main()
