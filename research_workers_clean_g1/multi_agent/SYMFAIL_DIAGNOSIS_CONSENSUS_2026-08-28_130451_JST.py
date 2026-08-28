#!/usr/bin/env python3
"""Aggregate-only reanalysis of SymFail annotation agreement reported in arXiv:2608.25920v1.

No individual-level artifact is used. Counts are copied from Appendix B Tables 5-6.
The goal is to separate (a) intervention-location agreement from (b) full repair-diagnosis
agreement/retention, and to compute conservative finite-sample lower bounds.
"""
from math import sqrt
from scipy.stats import beta
import json

SOURCE = "https://arxiv.org/html/2608.25920v1"
N = 536
COUNTS = {
    # Table 5: strict tuple = (exact category set, primary category, node ID, node type)
    "strict_unanimous_cases": 210,
    "strict_unanimous_retained": 187,
    "strict_2_1_cases": 214,
    "strict_2_1_majority_retained": 124,
    "strict_2_1_minority_retained": 48,
    "strict_2_1_new_tuple": 42,
    "strict_all_distinct_cases": 112,
    "strict_all_distinct_any_proposed_retained": 77,
    "strict_all_distinct_new_tuple": 35,
    "strict_final_supported_by_none": 100,
    # Table 6: node-id and strict-tuple agreement among three initial annotators
    "node_all3_same": 396,
    "node_atleast2_same": 514,
    "strict_atleast2_same": 424,
}


def wilson(k, n, z=1.959963984540054):
    p = k / n
    den = 1 + z*z/n
    center = (p + z*z/(2*n)) / den
    half = z * sqrt(p*(1-p)/n + z*z/(4*n*n)) / den
    return center-half, center+half


def jeffreys_lower(k, n, alpha=0.05):
    return float(beta.ppf(alpha/2, k + 0.5, n - k + 0.5))


def row(name, k, n):
    lo, hi = wilson(k, n)
    return {
        "name": name,
        "k": k,
        "n": n,
        "rate": k/n,
        "wilson95_lo": lo,
        "wilson95_hi": hi,
        "jeffreys95_lower": jeffreys_lower(k, n),
    }

rows = []
rows.append(row("strict_unanimous_retained_as_final", 187, 210))
rows.append(row("strict_2_1_majority_retained_as_final", 124, 214))
rows.append(row("strict_2_1_any_initial_tuple_retained_as_final", 124+48, 214))
rows.append(row("strict_all_distinct_any_initial_tuple_retained_as_final", 77, 112))
rows.append(row("strict_any_initial_tuple_retained_as_final_overall", 187+124+48+77, N))
rows.append(row("node_all3_same", 396, N))
rows.append(row("node_atleast2_same", 514, N))
rows.append(row("strict_atleast2_same", 424, N))
rows.append(row("final_strict_tuple_absent_from_all_initial", 100, N))

risk_thresholds = [0.80, 0.90, 0.95]
gates = {}
for r in rows:
    gates[r["name"]] = {
        f"passes_lower_bound_{t:.2f}": r["jeffreys95_lower"] >= t for t in risk_thresholds
    }

summary = {
    "source": SOURCE,
    "scope": "Aggregate-only descriptive reanalysis of the 536-case SymFail human annotation tables; not independent re-annotation and not a production threshold study.",
    "counts": COUNTS,
    "derived": rows,
    "risk_gate_examples": gates,
    "key_mechanism_observations": {
        "location_vs_semantics": (
            "At least two annotators chose the same node in 95.90% of cases, but consensus on the full intervention tuple is materially weaker; "
            "among 2-1 strict-tuple splits, the majority tuple became the adjudicated final tuple in only 57.94% of cases."
        ),
        "proposal_set_not_complete": (
            "The adjudicated final strict tuple was absent from all three initial strict tuples in 100/536=18.66% of cases. "
            "Therefore, widening only over already-proposed diagnosis tuples cannot by itself certify full intervention semantics."
        ),
        "high_risk_gate": (
            "Using a 95% Jeffreys lower bound, even the empirical 'at least two same node' rate has a lower bound below 0.95; "
            "a hypothetical 95% minimum-coverage destructive-repair gate would require escalation/adjudication rather than treating consensus as proof."
        ),
    },
}

print(json.dumps(summary, indent=2, sort_keys=True))
