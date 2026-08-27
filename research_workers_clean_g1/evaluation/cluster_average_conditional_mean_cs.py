#!/usr/bin/env python3
"""
Anytime-valid upper confidence sequence for a drifting average conditional mean.

Use case
--------
Repeated-inference reliability measurements often have a natural top-level unit
such as one process/server lifetime/workload. Lower-level requests inside that
unit may be arbitrarily dependent. Give each predeclared top-level cluster one
bounded score Y_t in [0,1] (for example, an any-mismatch indicator or a
within-cluster mismatch fraction).

Unlike cluster_mismatch_anytime_certifier.py's stable-p mode, this file does NOT
assume a constant cross-cluster mismatch rate. It targets

    mu_bar_t = (1/t) * sum_{i<=t} E[Y_i | F_{i-1}],

the average conditional mean, allowing the conditional mean to vary with time
and past observations.

Construction
------------
For any fixed lambda > 0, let a = 1-exp(-lambda). Convexity on [0,1] gives

    exp(-lambda*y) <= 1 - a*y.

Writing mu_i = E[Y_i | F_{i-1}], the process

    M_t(lambda) = prod_i exp(-lambda Y_i) / (1-a*mu_i)

is a nonnegative supermartingale. Since log(1-a*x) is concave,

    prod_i (1-a*mu_i) <= (1-a*mu_bar_t)^t.

Therefore

    E_t(lambda, m) = exp(-lambda * sum_i Y_i) / (1-a*m)^t

satisfies E_t(lambda, mu_bar_t) <= M_t(lambda) pathwise. A fixed convex mixture
over predeclared lambda values is likewise upper-bounded by a nonnegative
supermartingale. Ville's inequality then implies

    P(exists t: E_t(mu_bar_t) >= 1/alpha) <= alpha.

Because E_t(m) is nondecreasing in m, the first m where the mixture reaches
1/alpha is an anytime-valid upper confidence endpoint U_t for mu_bar_t.

This construction needs no independence across top-level clusters; dependence is
handled through conditional expectations. It does require that cluster identity,
score definition, and reveal order are fixed before each current cluster outcome
is seen. It does not make retrospective outcome-selected clusters prospective.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Iterable


DEFAULT_LAMBDAS = (0.125, 0.25, 0.5, 1.0, 2.0, 4.0, 8.0, 16.0)


def logsumexp(values: list[float]) -> float:
    m = max(values)
    if math.isinf(m):
        return m
    return m + math.log(sum(math.exp(v - m) for v in values))


def parse_positive_csv(raw: str, name: str) -> tuple[float, ...]:
    vals = tuple(float(x.strip()) for x in raw.split(",") if x.strip())
    if not vals:
        raise ValueError(f"at least one {name} value is required")
    if any((not math.isfinite(x)) or x <= 0.0 for x in vals):
        raise ValueError(f"every {name} value must be finite and >0")
    return vals


def normalized_weights(raw: str | None, n: int) -> tuple[float, ...]:
    if raw is None:
        return tuple(1.0 / n for _ in range(n))
    vals = parse_positive_csv(raw, "weight")
    if len(vals) != n:
        raise ValueError("weights must have the same length as lambdas")
    s = sum(vals)
    return tuple(x / s for x in vals)


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
    sizes: list[int] = []
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
            sizes.append(size)

    scores = validate_scores(scores)
    all_sizes = len(sizes) == len(scores)
    meta = {
        "cluster_count": len(scores),
        "cluster_ids_unique": True,
        "cluster_sizes_supplied_for_all": all_sizes,
        "total_lower_level_records_if_supplied": sum(sizes) if all_sizes else None,
        "min_cluster_size_if_supplied": min(sizes) if all_sizes else None,
        "max_cluster_size_if_supplied": max(sizes) if all_sizes else None,
    }
    return scores, meta


def log_e_value(
    score_sum: float,
    t: int,
    m: float,
    lambdas: tuple[float, ...],
    weights: tuple[float, ...],
) -> float:
    if not (0.0 <= m <= 1.0):
        raise ValueError("candidate mean m must lie in [0,1]")
    vals: list[float] = []
    for lam, w in zip(lambdas, weights):
        a = 1.0 - math.exp(-lam)
        g = 1.0 - m * a
        if g <= 0.0:
            raise AssertionError("positive denominator contract violated")
        vals.append(math.log(w) - lam * score_sum - t * math.log(g))
    return logsumexp(vals)


def upper_endpoint(
    score_sum: float,
    t: int,
    alpha: float,
    lambdas: tuple[float, ...],
    weights: tuple[float, ...],
) -> float:
    threshold_log = math.log(1.0 / alpha)
    if log_e_value(score_sum, t, 1.0, lambdas, weights) < threshold_log:
        return 1.0
    lo, hi = 0.0, 1.0
    for _ in range(90):
        mid = (lo + hi) / 2.0
        if log_e_value(score_sum, t, mid, lambdas, weights) >= threshold_log:
            hi = mid
        else:
            lo = mid
    return hi


def zero_score_clusters_needed(
    tolerance: float,
    alpha: float,
    lambdas: tuple[float, ...],
    weights: tuple[float, ...],
) -> int:
    if not (0.0 < tolerance < 1.0):
        raise ValueError("tolerance must lie strictly in (0,1)")
    threshold_log = math.log(1.0 / alpha)
    n = 1
    while log_e_value(0.0, n, tolerance, lambdas, weights) < threshold_log:
        n += 1
    return n


def main() -> None:
    ap = argparse.ArgumentParser()
    source = ap.add_mutually_exclusive_group(required=True)
    source.add_argument("--scores", help="Comma-separated top-level cluster scores in reveal order.")
    source.add_argument("--records-json", help="JSON list or {'clusters':[...]} with cluster_id and score.")
    ap.add_argument("--cluster-score-contract", required=True)
    ap.add_argument("--fingerprint-scope", required=True)
    ap.add_argument("--alpha", type=float, default=0.05)
    ap.add_argument("--tolerance", type=float, default=None)
    ap.add_argument(
        "--lambdas",
        default=",".join(str(x) for x in DEFAULT_LAMBDAS),
        help="Fixed positive lambda grid chosen before current outcomes.",
    )
    ap.add_argument(
        "--weights",
        default=None,
        help="Optional positive mixture weights, same length as lambdas; normalized internally.",
    )
    ap.add_argument("--emit-prefix", action="store_true")
    args = ap.parse_args()

    if not (0.0 < args.alpha < 1.0):
        raise ValueError("alpha must lie strictly in (0,1)")
    if args.tolerance is not None and not (0.0 < args.tolerance < 1.0):
        raise ValueError("tolerance must lie strictly in (0,1)")

    lambdas = parse_positive_csv(args.lambdas, "lambda")
    weights = normalized_weights(args.weights, len(lambdas))

    if args.scores is not None:
        scores = validate_scores(float(x.strip()) for x in args.scores.split(",") if x.strip())
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

    prefix = []
    s = 0.0
    final_upper = 1.0
    for t, y in enumerate(scores, start=1):
        s += y
        final_upper = upper_endpoint(s, t, args.alpha, lambdas, weights)
        if args.emit_prefix:
            prefix.append({
                "cluster_index": t,
                "score": y,
                "score_sum": s,
                "empirical_equal_cluster_mean": s / t,
                "average_conditional_mean_upper": final_upper,
            })

    inference = {
        "alpha": args.alpha,
        "cluster_count": len(scores),
        "score_sum": s,
        "empirical_equal_cluster_mean": s / len(scores),
        "average_conditional_mean_upper": final_upper,
        "lambdas": list(lambdas),
        "weights": list(weights),
    }
    if args.tolerance is not None:
        inference.update({
            "tolerance": args.tolerance,
            "certified_average_conditional_mean_below_tolerance": final_upper <= args.tolerance + 1e-12,
            "current_log_e_at_tolerance": log_e_value(
                s, len(scores), args.tolerance, lambdas, weights
            ),
            "threshold_log_e": math.log(1.0 / args.alpha),
            "zero_score_clusters_needed_with_current_mixture": zero_score_clusters_needed(
                args.tolerance, args.alpha, lambdas, weights
            ),
        })
    if args.emit_prefix:
        inference["prefix"] = prefix

    lower_level_warning = (
        f"{meta['total_lower_level_records_if_supplied']} lower-level records are nested inside "
        f"{meta['cluster_count']} top-level clusters and are not treated as independent trials."
        if meta["total_lower_level_records_if_supplied"] is not None
        else "Inference uses exactly one bounded score per declared top-level cluster."
    )

    output = {
        "schema_version": 1,
        "fingerprint_scope": args.fingerprint_scope,
        "cluster_score_contract": args.cluster_score_contract,
        "estimand": "mu_bar_t = t^{-1} sum_{i<=t} E[Y_i | F_{i-1}]",
        "allows_time_varying_conditional_means": True,
        "cluster_metadata": meta,
        "inference": inference,
        "lower_level_record_warning": lower_level_warning,
        "proof_contract": [
            "For each fixed lambda, convexity gives exp(-lambda*y) <= 1-(1-exp(-lambda))*y on [0,1].",
            "Dividing each factor by the corresponding expression at the true conditional mean yields a nonnegative supermartingale.",
            "Concavity of log(1-a*x) upper-bounds the product of conditional-mean denominators by the same expression at the average conditional mean.",
            "The reported fixed lambda mixture at the true average conditional mean is therefore pathwise upper-bounded by a nonnegative supermartingale; Ville gives simultaneous coverage over time.",
        ],
        "validity_notes": [
            "No independence across top-level clusters is required; the guarantee is filtration/conditional-mean based.",
            "Cluster identity, score definition, lambda mixture, and reveal order must be fixed before the current cluster outcome is observed.",
            "Within-cluster dependence may be arbitrary because only one final bounded cluster score enters the sequence.",
            "This is an equal-cluster average conditional mean, not request-weighted mismatch when cluster sizes differ.",
            "Retrospective outcome-selected clusters are not converted into a prospective certificate by this tool.",
            "Do not pool substantively different fingerprints unless the resulting cluster-score sequence and estimand were defined to cover that mixture before outcomes.",
        ],
    }
    print(json.dumps(output, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
