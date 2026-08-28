"""Independent finite counterexample for AgentOpt's weighted quality-stage bound.

This checker does not import AgentOpt. It mirrors only the public formula at
vickykumar123/agentopt@a9bea3e3dfc329950f6061fb972d93496c2ed0f5:
  weighted mean delta for effect size,
  unweighted sample SD / sqrt(n) for the z=1.645 lower bound,
  1 percentage-point minimum effect floor,
  significance required at n >= 5.

Null construction: five independent per-case deltas are each +/-0.02 with
probability 1/2, and fixed allowed case weights are [100,1,1,1,1].  The
expected weighted gain is exactly zero.  Enumerating all 2^5 outcomes shows
that the quality stage accepts exactly 16/32 = 0.5 of null outcomes.  This is
a counterexample to interpreting the weighted calculation as a general 95%
confidence certification.  It is not a claim about AgentOpt's empirical
end-to-end false-promotion rate because earlier/later gate stages may reject.
"""

from itertools import product
from math import sqrt
from statistics import stdev

Z = 1.645
MIN_EFFECT_PP = 1.0
WEIGHTS = [100.0, 1.0, 1.0, 1.0, 1.0]
AMPLITUDE = 0.02


def weighted_mean(xs: list[float], ws: list[float]) -> float:
    return sum(x * w for x, w in zip(xs, ws, strict=True)) / sum(ws)


def quality_accepts(deltas: list[float]) -> tuple[bool, float, float]:
    mean_delta = weighted_mean(deltas, WEIGHTS)
    net_gain_pp = 100.0 * mean_delta
    if net_gain_pp < MIN_EFFECT_PP:
        return False, net_gain_pp, float("nan")
    se = stdev(deltas) / sqrt(len(deltas))
    lower_pp = 100.0 * (mean_delta - Z * se)
    return lower_pp > 0.0, net_gain_pp, lower_pp


def main() -> None:
    outcomes = []
    for signs in product((-1.0, 1.0), repeat=5):
        deltas = [AMPLITUDE * s for s in signs]
        accepted, gain_pp, lower_pp = quality_accepts(deltas)
        outcomes.append((signs, accepted, gain_pp, lower_pp))

    accepted = [o for o in outcomes if o[1]]
    assert len(outcomes) == 32
    assert len(accepted) == 16
    assert all(o[0][0] == 1.0 for o in accepted)
    assert all(o[3] > 0.0 for o in accepted)
    assert abs(sum(weighted_mean([AMPLITUDE * s for s in signs], WEIGHTS)
                   for signs in product((-1.0, 1.0), repeat=5)) / 32.0) < 1e-15

    print("outcomes=32")
    print(f"accepted={len(accepted)}")
    print(f"null_acceptance_probability={len(accepted)/32:.6f}")
    print(f"minimum_accepted_lower_bound_pp={min(o[3] for o in accepted):.12f}")


if __name__ == "__main__":
    main()
