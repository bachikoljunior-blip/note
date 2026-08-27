#!/usr/bin/env python3
"""
Anytime-valid mismatch certification with an explicit trial-unit guard.

This utility is intended for repeated-inference verification where the protected
observable is a deterministic score/sign/statistic, not necessarily the raw
model text.

Core bound
----------
For Bernoulli mismatch indicators X_1,...,X_n and a fixed candidate parameter p,

  M_n(p) = B(s+a, n-s+b) / (B(a,b) p^s (1-p)^(n-s))

is a nonnegative beta-binomial mixture martingale under the contract
P(X_t=1 | F_{t-1}) = p. Ville's inequality therefore yields a time-uniform
confidence set {p : M_t(p) < 1/alpha for every observed t}.  We report its upper
endpoint using the Jeffreys mixture a=b=1/2 by default.

Important: the input `trials` must be the predeclared top-level statistical
trial unit. Do NOT pass the number of all-pairs comparisons formed from a small
number of repeated outputs: those comparisons share outputs and are dependent.
Likewise, requests from the same concurrent workload/server lifetime may be a
cluster rather than independent trial units. If `--all-pairs-repeat-count` is
supplied, the tool fails closed and reports no Bernoulli confidence bound.

The fixed-sample zero-failure bound is printed only for comparison. It is not
valid if data collection can stop after peeking at the bound.
"""
from __future__ import annotations

import argparse
import json
import math


def log_beta(x: float, y: float) -> float:
    return math.lgamma(x) + math.lgamma(y) - math.lgamma(x + y)


def log_mixture_martingale(
    p: float, n: int, s: int, a: float = 0.5, b: float = 0.5
) -> float:
    if not (0 <= s <= n):
        raise ValueError("require 0 <= mismatches <= trials")
    log_marginal = log_beta(s + a, n - s + b) - log_beta(a, b)
    if p <= 0:
        return math.inf if s else log_marginal
    if p >= 1:
        return math.inf if (n - s) else log_marginal
    return log_marginal - s * math.log(p) - (n - s) * math.log1p(-p)


def anytime_upper(
    n: int, s: int, alpha: float = 0.05, a: float = 0.5, b: float = 0.5
) -> float:
    if n <= 0:
        return 1.0
    if not (0 < alpha < 1):
        raise ValueError("alpha must be in (0,1)")
    target = math.log(1.0 / alpha)
    phat = s / n
    lo = max(phat, 1e-15)
    hi = 1.0 - 1e-15

    def f(p: float) -> float:
        return log_mixture_martingale(p, n, s, a, b) - target

    if f(hi) < 0:
        return 1.0
    if f(lo) > 0:
        return phat
    for _ in range(120):
        mid = (lo + hi) / 2
        if f(mid) > 0:
            hi = mid
        else:
            lo = mid
    return hi


def fixed_zero_upper(n: int, alpha: float) -> float | None:
    if n <= 0:
        return None
    return 1.0 - alpha ** (1.0 / n)


def zero_trials_needed_fixed(tolerance: float, alpha: float) -> int:
    if not (0 < tolerance < 1):
        raise ValueError("tolerance must be in (0,1)")
    return math.ceil(math.log(alpha) / math.log1p(-tolerance))


def zero_trials_needed_anytime(tolerance: float, alpha: float) -> int:
    # Monotone in n for the zero-mismatch path. Exponential search then bisection.
    hi = 1
    while anytime_upper(hi, 0, alpha) > tolerance:
        hi *= 2
    lo = hi // 2
    while lo + 1 < hi:
        mid = (lo + hi) // 2
        if anytime_upper(mid, 0, alpha) <= tolerance:
            hi = mid
        else:
            lo = mid
    return hi


def channel(n: int, s: int, alpha: float, tolerance: float | None) -> dict:
    u = anytime_upper(n, s, alpha)
    return {
        "trials": n,
        "mismatches": s,
        "empirical_rate": (s / n) if n else None,
        "anytime_upper": u,
        "tolerance": tolerance,
        "passes_tolerance": (u <= tolerance) if tolerance is not None else None,
        "fixed_zero_failure_upper_comparison_only":
            fixed_zero_upper(n, alpha) if s == 0 else None,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--trials", type=int, required=True)
    ap.add_argument("--mismatches", type=int, required=True)
    ap.add_argument("--trial-unit-contract", required=True)
    ap.add_argument("--fingerprint", required=True)
    ap.add_argument("--alpha", type=float, default=0.05)
    ap.add_argument("--tolerance", type=float)
    ap.add_argument("--canonical-trials", type=int, default=0)
    ap.add_argument("--canonical-mismatches", type=int, default=0)
    ap.add_argument("--canonical-tolerance", type=float)
    ap.add_argument(
        "--all-pairs-repeat-count",
        type=int,
        default=0,
        help="If >0, inputs came from all-pairs of this many repeats; fail closed.",
    )
    args = ap.parse_args()

    if args.all_pairs_repeat_count:
        r = args.all_pairs_repeat_count
        print(json.dumps({
            "schema_version": 1,
            "status": "invalid_trial_unit_pseudoreplication",
            "fingerprint": args.fingerprint,
            "trial_unit_contract": args.trial_unit_contract,
            "reason": (
                f"Counts derived from all-pairs of {r} repeats reuse the same "
                f"outputs across {r*(r-1)//2} pair comparisons; pair count is "
                "not an independent Bernoulli trial count. Re-aggregate to a "
                "predeclared top-level cluster/trial unit before inference."
            ),
            "confidence_bound": None,
        }, indent=2, sort_keys=True))
        return

    fast = channel(args.trials, args.mismatches, args.alpha, args.tolerance)
    canon = channel(
        args.canonical_trials,
        args.canonical_mismatches,
        args.alpha,
        args.canonical_tolerance,
    )

    if args.canonical_mismatches > 0:
        status = "canonical_unstable_fail_closed"
    elif (
        args.canonical_tolerance is not None
        and not canon["passes_tolerance"]
    ):
        status = "canonical_not_certified"
    elif args.tolerance is not None and not fast["passes_tolerance"]:
        status = "fast_path_not_certified"
    else:
        status = "certified_within_configured_bounds"

    planning = {}
    for label, tol in (
        ("fast_vs_canonical", args.tolerance),
        ("canonical_repeat_stability", args.canonical_tolerance),
    ):
        if tol is not None:
            planning[label] = {
                "zero_mismatch_trials_needed_fixed_sample":
                    zero_trials_needed_fixed(tol, args.alpha),
                "zero_mismatch_trials_needed_anytime_jeffreys_mixture":
                    zero_trials_needed_anytime(tol, args.alpha),
            }

    print(json.dumps({
        "schema_version": 1,
        "status": status,
        "fingerprint": args.fingerprint,
        "trial_unit_contract": args.trial_unit_contract,
        "alpha": args.alpha,
        "fast_vs_canonical": fast,
        "canonical_repeat_stability": canon,
        "zero_mismatch_planning": planning,
        "validity_notes": [
            "The Bernoulli bound requires the declared top-level trial-unit contract.",
            "Do not substitute all-pairs repeat comparisons for independent trial units.",
            "Do not pool runtime/model/hardware/batching fingerprints without a justified common parameter contract.",
            "anytime_upper supports continuous peeking/optional stopping under the stated martingale contract.",
            "fixed_zero_failure_upper_comparison_only requires a pre-fixed sample size.",
            "Any protected-statistic mismatch in canonical repeats is fail-closed.",
        ],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
