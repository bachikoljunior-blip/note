from __future__ import annotations

import itertools
import json
import math
from pathlib import Path

PREMISES = {
    "a_P": ("fact", "P"),
    "b_P_implies_R": ("rule", "P", "R"),
    "c_Q": ("fact", "Q"),
    "d_Q_implies_R": ("rule", "Q", "R"),
    "e_P_implies_Q": ("rule", "P", "Q"),
}
TARGET = "R"


def derives(selected: set[str]) -> bool:
    facts: set[str] = set()
    rules: list[tuple[str, str]] = []
    for name in selected:
        item = PREMISES[name]
        if item[0] == "fact":
            facts.add(item[1])
        else:
            rules.append((item[1], item[2]))
    changed = True
    while changed:
        changed = False
        for antecedent, consequent in rules:
            if antecedent in facts and consequent not in facts:
                facts.add(consequent)
                changed = True
    return TARGET in facts


def minimal_supports() -> list[list[str]]:
    names = sorted(PREMISES)
    supports: list[set[str]] = []
    for size in range(1, len(names) + 1):
        for combo in itertools.combinations(names, size):
            candidate = set(combo)
            if derives(candidate) and not any(s.issubset(candidate) for s in supports):
                supports.append(candidate)
    return [sorted(s) for s in supports]


def exact_shapley() -> dict[str, float]:
    names = sorted(PREMISES)
    n = len(names)
    result = {name: 0.0 for name in names}
    for name in names:
        others = [x for x in names if x != name]
        for size in range(len(others) + 1):
            for combo in itertools.combinations(others, size):
                coalition = set(combo)
                marginal = int(derives(coalition | {name})) - int(derives(coalition))
                weight = (
                    math.factorial(len(coalition))
                    * math.factorial(n - len(coalition) - 1)
                    / math.factorial(n)
                )
                result[name] += weight * marginal
    return result


def main() -> None:
    supports = minimal_supports()
    support_counts = {
        name: sum(name in support for support in supports) for name in sorted(PREMISES)
    }
    output = {
        "schema_version": "SupportFamilyFixtureV0",
        "target": TARGET,
        "premises": PREMISES,
        "minimal_supports": supports,
        "support_frequency": {
            name: support_counts[name] / len(supports) for name in support_counts
        },
        "exact_shapley": exact_shapley(),
        "notes": [
            "The oracle is deterministic forward chaining over five frozen Horn premises.",
            "Support frequency and exact Shapley credit are intentionally different: membership in observed minimal supports is not identical to marginal coalition value.",
            "This fixture validates event/credit plumbing only; it is not evidence about Lean or Isabelle theorem-prover utility."
        ],
    }
    print(json.dumps(output, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
