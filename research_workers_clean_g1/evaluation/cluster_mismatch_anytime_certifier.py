#!/usr/bin/env python3
"""
Cluster-aware anytime-valid rare-mismatch certification.

This utility is for repeated-inference verification when lower-level requests
inside one workload/server lifetime may be arbitrarily dependent.

Statistical contract
--------------------
Each predeclared top-level cluster contributes exactly one bounded score
Y_t in [0,1]. Examples:

* any-mismatch indicator for a server lifetime/workload (0 or 1);
* mismatch fraction within a server lifetime, if the target parameter is the
  stable equal-cluster mean mismatch fraction.

The primary mode assumes a stable conditional-mean parameter p inside the
frozen fingerprint/lease:

    E[Y_t | F_{t-1}] = p  for every admitted top-level cluster t.

A weaker sufficient condition for testing the one-sided null p >= m is that the
next cluster score has conditional mean at least m whenever that null is true.
If cluster conditional means drift arbitrarily across t, this program must not be
read as estimating their simple time average; use a confidence sequence designed
for average conditional means instead.

For a predeclared tolerance m, test H0: p >= m with predictable one-step factors

    e_t(lambda, m) = 1 + lambda * (m - Y_t),

where 0 <= lambda <= 1/(1-m). Under H0 these factors have conditional
expectation at most one and are nonnegative, so their product is an e-process.
A fixed mixture over several predeclared lambda values is also an e-process and
therefore supports optional stopping / continuous peeking via Ville's inequality.

The same nested family can be inverted to an anytime-valid upper confidence
sequence for the stable p. Because the e-value is monotone nondecreasing in m for
the configured lambda parameterization, the upper endpoint is the first m at
which the mixture reaches 1/alpha. Importantly, obtaining that endpoint does NOT
require an additional multiplicity penalty beyond the fixed-tolerance test: at a
particular tolerance m0, U_t <= m0 exactly when the m0 test crosses.

This absorbs arbitrary within-cluster dependence into Y_t. It does NOT turn
requests inside a cluster into independent trials, and it does NOT by itself
justify request-weighted inference, pooling across fingerprints, a changing
cluster-score definition, or drift in the stable conditional-mean parameter.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Iterable


DEFAULT_BET_FRACTIONS = (0.25, 0.50, 0.75, 0.90, 0.99)


def logsumexp(values: list[float]) -> float:
    m = max(values)
    if math.isinf(m):
        return m
    return m + math.log(sum(math.exp(v - m) for v in values))


def parse_bet_fractions(raw: str) -> tuple[float, ...]:
    vals = tuple(float(x.strip()) for x in raw.split(",") if x.strip())
    if not vals:
        raise ValueError("at least one bet fraction is required")
    if any(not (0.0 < x < 1.0) for x in vals):
        raise ValueError("bet fractions must lie strictly in (0,1)")
    return vals


def validate_scores(scores: Iterable[float]) -> list[float]:
    out = [float(x) for x in scores]
    if not out:
        raise ValueError("at least one cluster score is required")
    if any((not math.isfinite(x)) or x < 0.0 or x > 1.0 for x in out):
        raise ValueError("every cluster score must be finite and in [0,1]")
    return out


def load_records(path: str) -> tuple[list[float], dict]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if isinstance(payload, dict):
        records = payload.get("clusters")
        if records is None:
            raise ValueError("JSON object must contain a 'clusters' array")
    elif isinstance(payload, list):
        records = payload
    else:
        raise ValueError("records JSON must be a list or {'clusters': [...]} object")

    ids: set[str] = set()
    scores: list[float] = []
    cluster_sizes: list[int] = []
    for i, rec in enumerate(records):
        if not isinstance(rec, dict):
            raise ValueError(f"cluster record {i} is not an object")
        cid = str(rec.get("cluster_id", "")).strip()
        if not cid:
            raise ValueError(f"cluster record {i} lacks nonempty cluster_id")
        if cid in ids:
            raise ValueError(f"duplicate cluster_id: {cid}")
        ids.add(cid)
        scores.append(float(rec["score"]))
        if "cluster_size" in rec:
            size = int(rec["cluster_size"])
            if size <= 0:
                raise ValueError(f"cluster_size must be positive for {cid}")
            cluster_sizes.append(size)

    scores = validate_scores(scores)
    metadata = {
        "cluster_count": len(scores),
        "cluster_ids_unique": True,
        "cluster_sizes_supplied_for_all": len(cluster_sizes) == len(scores),
        "total_lower_level_records_if_supplied":
            sum(cluster_sizes) if len(cluster_sizes) == len(scores) else None,
        "min_cluster_size_if_supplied":
            min(cluster_sizes) if len(cluster_sizes) == len(scores) else None,
        "max_cluster_size_if_supplied":
            max(cluster_sizes) if len(cluster_sizes) == len(scores) else None,
    }
    return scores, metadata


def log_mixture_e(
    scores: list[float],
    tolerance: float,
    bet_fractions: tuple[float, ...],
) -> float:
    if not (0.0 <= tolerance < 1.0):
        raise ValueError("tolerance must lie in [0,1)")
    component_logs: list[float] = []
    for g in bet_fractions:
        lam = g / (1.0 - tolerance)
        logw = 0.0
        for y in scores:
            factor = 1.0 + lam * (tolerance - y)
            if factor <= 0.0:
                raise AssertionError("bet construction produced nonpositive factor")
            logw += math.log(factor)
        component_logs.append(logw)
    return logsumexp(component_logs) - math.log(len(component_logs))


def anytime_upper_endpoint(
    scores: list[float],
    alpha: float,
    bet_fractions: tuple[float, ...],
) -> float:
    """Upper CS endpoint for the stable conditional-mean parameter p.

    The configured mixture e-value is monotone nondecreasing in the tested m.
    The confidence set is {m: E_t(m) < 1/alpha}; return its upper endpoint.
    """
    if not scores:
        return 1.0
    threshold_log = math.log(1.0 / alpha)

    # m=0 cannot produce evidence against the universal p>=0 null with Y in [0,1].
    if log_mixture_e(scores, 0.0, bet_fractions) >= threshold_log:
        return 0.0

    hi_probe = 1.0 - 1e-12
    if log_mixture_e(scores, hi_probe, bet_fractions) < threshold_log:
        return 1.0

    lo = 0.0
    hi = hi_probe
    for _ in range(90):
        mid = (lo + hi) / 2.0
        if log_mixture_e(scores, mid, bet_fractions) >= threshold_log:
            hi = mid
        else:
            lo = mid
    return hi


def mixture_path(
    scores: list[float],
    tolerance: float,
    alpha: float,
    bet_fractions: tuple[float, ...],
    emit_prefix_upper: bool = False,
) -> dict:
    if not (0.0 < tolerance < 1.0):
        raise ValueError("tolerance must lie strictly in (0,1)")
    if not (0.0 < alpha < 1.0):
        raise ValueError("alpha must lie strictly in (0,1)")

    # lambda = gamma/(1-m), gamma in (0,1), leaves factor >= 1-gamma > 0.
    lambdas = [g / (1.0 - tolerance) for g in bet_fractions]
    component_logs = [0.0 for _ in lambdas]
    threshold_log = math.log(1.0 / alpha)

    first_crossing = None
    final_log_mixture = 0.0
    max_log_mixture = 0.0
    prefix = []
    prefix_scores: list[float] = []

    for t, y in enumerate(scores, start=1):
        prefix_scores.append(y)
        for j, lam in enumerate(lambdas):
            factor = 1.0 + lam * (tolerance - y)
            if factor <= 0.0:
                raise AssertionError("bet construction produced nonpositive factor")
            component_logs[j] += math.log(factor)

        final_log_mixture = logsumexp(component_logs) - math.log(len(component_logs))
        max_log_mixture = max(max_log_mixture, final_log_mixture)
        if first_crossing is None and final_log_mixture >= threshold_log:
            first_crossing = t
        row = {
            "cluster_index": t,
            "score": y,
            "log_mixture_e": final_log_mixture,
            "mixture_e": math.exp(final_log_mixture)
                if final_log_mixture < 700 else math.inf,
            "crossed": final_log_mixture >= threshold_log,
        }
        if emit_prefix_upper:
            row["anytime_upper_endpoint"] = anytime_upper_endpoint(
                prefix_scores, alpha, bet_fractions
            )
        prefix.append(row)

    upper = anytime_upper_endpoint(scores, alpha, bet_fractions)
    return {
        "tolerance": tolerance,
        "alpha": alpha,
        "bet_fractions": list(bet_fractions),
        "lambdas": lambdas,
        "threshold_e": 1.0 / alpha,
        "first_crossing_cluster": first_crossing,
        "certified_below_tolerance": first_crossing is not None,
        "final_mixture_e":
            math.exp(final_log_mixture) if final_log_mixture < 700 else math.inf,
        "max_mixture_e":
            math.exp(max_log_mixture) if max_log_mixture < 700 else math.inf,
        "empirical_equal_cluster_mean": sum(scores) / len(scores),
        "anytime_upper_endpoint_stable_p": upper,
        "upper_endpoint_at_or_below_tolerance": upper <= tolerance + 1e-12,
        "prefix": prefix,
    }


def zero_score_clusters_needed(
    tolerance: float,
    alpha: float,
    bet_fractions: tuple[float, ...],
) -> int:
    component_logs = [0.0 for _ in bet_fractions]
    threshold_log = math.log(1.0 / alpha)
    n = 0
    while True:
        mix_log = logsumexp(component_logs) - math.log(len(component_logs))
        if mix_log >= threshold_log:
            return n
        n += 1
        for j, g in enumerate(bet_fractions):
            lam = g / (1.0 - tolerance)
            component_logs[j] += math.log(1.0 + lam * tolerance)


def main() -> None:
    ap = argparse.ArgumentParser()
    source = ap.add_mutually_exclusive_group(required=True)
    source.add_argument(
        "--scores",
        help="Comma-separated predeclared cluster scores in [0,1], reveal order.",
    )
    source.add_argument(
        "--records-json",
        help="JSON list (or {'clusters': [...]}) with cluster_id, score, optional cluster_size.",
    )
    ap.add_argument("--cluster-score-contract", required=True)
    ap.add_argument("--fingerprint", required=True)
    ap.add_argument("--tolerance", type=float, required=True)
    ap.add_argument("--alpha", type=float, default=0.05)
    ap.add_argument(
        "--bet-fractions",
        default=",".join(str(x) for x in DEFAULT_BET_FRACTIONS),
        help="Predeclared fractions gamma in (0,1); lambda=gamma/(1-tolerance).",
    )
    ap.add_argument(
        "--emit-prefix",
        action="store_true",
        help="Include every prefix e-value in output; omitted by default for compact receipts.",
    )
    ap.add_argument(
        "--emit-prefix-upper",
        action="store_true",
        help="Also invert the nested tests at every prefix; implies --emit-prefix and is computationally heavier.",
    )
    args = ap.parse_args()

    fractions = parse_bet_fractions(args.bet_fractions)
    if args.scores is not None:
        scores = validate_scores(
            float(x.strip()) for x in args.scores.split(",") if x.strip()
        )
        meta = {
            "cluster_count": len(scores),
            "cluster_ids_unique": None,
            "cluster_sizes_supplied_for_all": False,
            "total_lower_level_records_if_supplied": None,
            "min_cluster_size_if_supplied": None,
            "max_cluster_size_if_supplied": None,
        }
    else:
        scores, meta = load_records(args.records_json)

    result = mixture_path(
        scores,
        args.tolerance,
        args.alpha,
        fractions,
        emit_prefix_upper=args.emit_prefix_upper,
    )
    if not (args.emit_prefix or args.emit_prefix_upper):
        result.pop("prefix", None)
    n_zero = zero_score_clusters_needed(args.tolerance, args.alpha, fractions)

    if meta["total_lower_level_records_if_supplied"] is not None:
        lower_level_warning = (
            f"{meta['total_lower_level_records_if_supplied']} lower-level records "
            f"are nested inside {meta['cluster_count']} declared clusters. They are "
            "descriptive only here and are not treated as independent trials."
        )
    else:
        lower_level_warning = (
            "No lower-level record count was supplied. Inference uses exactly one "
            "bounded score per declared top-level cluster."
        )

    output = {
        "schema_version": 2,
        "status": (
            "certified_below_tolerance"
            if result["certified_below_tolerance"]
            else "not_yet_certified"
        ),
        "fingerprint": args.fingerprint,
        "cluster_score_contract": args.cluster_score_contract,
        "parameter_contract": (
            "stable conditional-mean parameter p within the frozen fingerprint/lease: "
            "E[Y_t|F_{t-1}]=p; one-sided threshold validity only needs conditional mean >= tolerance under H0"
        ),
        "cluster_metadata": meta,
        "inference": result,
        "zero_score_planning": {
            "clusters_needed_with_current_fixed_mixture": n_zero,
            "same_count_for_upper_endpoint_to_reach_tolerance": True,
            "note": (
                "Planning assumes every future cluster score is exactly zero and "
                "uses the configured nested mixture. Inverting the same tests into "
                "an upper CS adds no alpha penalty at the specified tolerance."
            ),
        },
        "lower_level_record_warning": lower_level_warning,
        "validity_notes": [
            "Each declared top-level cluster contributes exactly one score in [0,1].",
            "Within-cluster dependence may be arbitrary because only the final bounded cluster score enters the e-process.",
            "The upper endpoint estimates a stable conditional-mean parameter p inside the frozen fingerprint/lease; arbitrary cross-cluster drift requires a different average-conditional-mean CS or explicit lease invalidation.",
            "For the fixed-tolerance test, validity only needs E[Y_t|past] >= tolerance whenever H0 is true.",
            "Bet fractions and the cluster-score definition must be fixed before each score is revealed; changing them after seeing the current cluster outcome invalidates the guarantee.",
            "Optional stopping/continuous peeking is allowed because the reported mixture is an e-process under the stated contract.",
            "The nested-test inversion creates an anytime upper CS without an extra multiplicity penalty; U_t <= m iff the m test crosses for this monotone family.",
            "Equal-cluster mismatch fraction is not request-weighted mismatch when cluster sizes differ.",
            "Do not pool fingerprints or redefine cluster boundaries after seeing mismatch outcomes without a separate justified contract.",
            "All-pairs comparisons within a repeated workload are diagnostic edges, not additional top-level cluster trials.",
        ],
    }
    print(json.dumps(output, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
