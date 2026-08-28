#!/usr/bin/env python3
"""Replay-complete Digits optimizer-switching harness.

The harness intentionally separates:
1) raw episode measurement,
2) calibration derivation,
3) policy simulation.

No confirmation row is allowed to influence calibration-derived thresholds or
the conditional estimator. Raw rows are JSON-serializable and include ordered
per-config timing/score observations for both fixed model families.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import platform
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Sequence

import numpy as np
import scipy
import sklearn
from sklearn.datasets import load_digits
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import make_scorer, balanced_accuracy_score
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

SCHEMA_VERSION = 1
SUCCESS_THRESHOLD = 0.97
CV_SPLITS = 3
CV_N_JOBS = 1
DIRECT_CONFIGS = (
    {"n_estimators": 10, "max_depth": None},
    {"n_estimators": 20, "max_depth": None},
    {"n_estimators": 40, "max_depth": None},
    {"n_estimators": 80, "max_depth": None},
    {"n_estimators": 40, "max_depth": 8},
)
TRANSVERSAL_CONFIGS = (
    {"C": 0.1, "gamma": "scale"},
    {"C": 1.0, "gamma": "scale"},
    {"C": 10.0, "gamma": "scale"},
    {"C": 100.0, "gamma": "scale"},
    {"C": 10.0, "gamma": 0.001},
)
LAMBDA_COST = 0.2
HYSTERESIS = 0.02
DEADLINE_SUCCESS_FLOOR = 0.35
TWO_CONSECUTIVE_ADVANTAGE_REQUIRED = True
CANDIDATE_RULE = (
    "Useful on this exact workload only if success improves with <=10% mean-time "
    "worsening OR mean time improves >=10% with success loss <=0.02; otherwise mixed/null."
)


def canonical_json_bytes(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha256_obj(obj: Any) -> str:
    return hashlib.sha256(canonical_json_bytes(obj)).hexdigest()


def dataset_manifest() -> dict[str, Any]:
    X, y = load_digits(return_X_y=True)
    hx = hashlib.sha256()
    hx.update(str(X.dtype).encode("utf-8"))
    hx.update(str(tuple(X.shape)).encode("utf-8"))
    hx.update(np.ascontiguousarray(X).tobytes())
    hy = hashlib.sha256()
    hy.update(str(y.dtype).encode("utf-8"))
    hy.update(str(tuple(y.shape)).encode("utf-8"))
    hy.update(np.ascontiguousarray(y).tobytes())
    return {
        "X_shape": list(X.shape),
        "y_shape": list(y.shape),
        "X_sha256": hx.hexdigest(),
        "y_sha256": hy.hexdigest(),
    }


def environment_manifest() -> dict[str, Any]:
    env_names = (
        "OMP_NUM_THREADS",
        "OPENBLAS_NUM_THREADS",
        "MKL_NUM_THREADS",
        "VECLIB_MAXIMUM_THREADS",
        "NUMEXPR_NUM_THREADS",
    )
    return {
        "python": sys.version,
        "python_executable": sys.executable,
        "platform": platform.platform(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "cpu_count": os.cpu_count(),
        "sklearn_version": sklearn.__version__,
        "numpy_version": np.__version__,
        "scipy_version": scipy.__version__,
        "timing_clock": "time.perf_counter",
        "thread_env": {k: os.environ.get(k) for k in env_names},
        "dataset": "sklearn.datasets.load_digits",
        "dataset_manifest": dataset_manifest(),
        "metric": "mean 3-fold stratified CV balanced_accuracy",
        "cv_n_jobs": CV_N_JOBS,
    }


def _score_model(model: Any, X: np.ndarray, y: np.ndarray, cv: StratifiedKFold) -> tuple[float, float]:
    start = time.perf_counter()
    scores = cross_val_score(
        model,
        X,
        y,
        cv=cv,
        scoring="balanced_accuracy",
        n_jobs=CV_N_JOBS,
        error_score="raise",
    )
    elapsed = time.perf_counter() - start
    return float(np.mean(scores)), float(elapsed)


def _run_family(
    family: str,
    seed: int,
    X: np.ndarray,
    y: np.ndarray,
) -> dict[str, Any]:
    observations: list[dict[str, Any]] = []
    cumulative = 0.0
    success = False
    success_index: int | None = None

    configs = DIRECT_CONFIGS if family == "direct" else TRANSVERSAL_CONFIGS
    for idx, cfg in enumerate(configs):
        cv = StratifiedKFold(n_splits=CV_SPLITS, shuffle=True, random_state=seed)
        if family == "direct":
            model = RandomForestClassifier(
                n_estimators=cfg["n_estimators"],
                max_depth=cfg["max_depth"],
                random_state=0,
                n_jobs=1,
            )
        else:
            model = make_pipeline(
                StandardScaler(),
                SVC(C=cfg["C"], gamma=cfg["gamma"]),
            )
        score, wall = _score_model(model, X, y, cv)
        cumulative += wall
        hit = bool(score >= SUCCESS_THRESHOLD)
        observations.append(
            {
                "index": idx,
                "config": cfg,
                "score": score,
                "wall_seconds": wall,
                "cumulative_seconds": cumulative,
                "success": hit,
            }
        )
        if hit:
            success = True
            success_index = idx
            break

    return {
        "family": family,
        "success": success,
        "success_index": success_index,
        "time_to_success_or_exhaustion_seconds": cumulative,
        "observations": observations,
    }


def measure_episode(seed: int) -> dict[str, Any]:
    X, y = load_digits(return_X_y=True)
    direct = _run_family("direct", seed, X, y)
    transversal = _run_family("transversal", seed, X, y)
    row = {
        "schema_version": SCHEMA_VERSION,
        "seed": int(seed),
        "direct": direct,
        "transversal": transversal,
    }
    row["row_sha256"] = sha256_obj(row)
    return row


def validate_row(row: dict[str, Any]) -> None:
    if row.get("schema_version") != SCHEMA_VERSION:
        raise ValueError("schema version mismatch")
    expected = dict(row)
    digest = expected.pop("row_sha256", None)
    if digest != sha256_obj(expected):
        raise ValueError("row digest mismatch")
    for family in ("direct", "transversal"):
        f = row[family]
        obs = f["observations"]
        if not obs:
            raise ValueError(f"{family}: no observations")
        prior = 0.0
        for i, o in enumerate(obs):
            if o["index"] != i:
                raise ValueError(f"{family}: non-contiguous index")
            if o["wall_seconds"] < 0 or o["cumulative_seconds"] < prior:
                raise ValueError(f"{family}: invalid timing")
            prior = o["cumulative_seconds"]
        if abs(prior - f["time_to_success_or_exhaustion_seconds"]) > 1e-9:
            raise ValueError(f"{family}: aggregate timing mismatch")
        hits = [o["index"] for o in obs if o["success"]]
        if f["success"] != bool(hits):
            raise ValueError(f"{family}: success mismatch")
        if f["success_index"] != (hits[0] if hits else None):
            raise ValueError(f"{family}: success index mismatch")


def derive_calibration(calibration_rows: Sequence[dict[str, Any]]) -> dict[str, Any]:
    if not calibration_rows:
        raise ValueError("empty calibration")
    for row in calibration_rows:
        validate_row(row)
    direct_times = np.asarray(
        [r["direct"]["time_to_success_or_exhaustion_seconds"] for r in calibration_rows],
        dtype=float,
    )
    deadline = float(np.clip(np.percentile(direct_times, 75), 0.50, 4.0))
    p50 = float(np.percentile(direct_times, 50))
    p90 = float(np.percentile(direct_times, 90))
    out = {
        "schema_version": 1,
        "calibration_row_digests": [r["row_sha256"] for r in calibration_rows],
        "calibration_rows_sha256": sha256_obj([r["row_sha256"] for r in calibration_rows]),
        "thresholds": {
            "deadline_seconds": deadline,
            "fixed_cap_seconds": 0.50 * deadline,
            "static_percentile_switch_seconds": min(p90, deadline),
            "direct_p50_seconds": p50,
            "direct_p90_seconds": p90,
            "lambda_cost": LAMBDA_COST,
            "hysteresis": HYSTERESIS,
            "deadline_success_floor": DEADLINE_SUCCESS_FLOOR,
            "two_consecutive_advantage_required": TWO_CONSECUTIVE_ADVANTAGE_REQUIRED,
        },
        "policy_spec": conditional_policy_spec(),
    }
    out["derived_sha256"] = sha256_obj(out)
    return out


def conditional_policy_spec() -> dict[str, Any]:
    return {
        "checkpoint": "after each completed failed direct configuration",
        "direct_conditioning": "calibration episodes still unsuccessful after same direct-config index k",
        "direct_success_before_deadline": (
            "among same-index calibration survivors, fraction with later direct success "
            "whose remaining time from checkpoint k is <= current evaluation remaining budget"
        ),
        "direct_remaining_cost": (
            "mean over survivors of min(later direct time-to-success-or-exhaustion minus cumulative "
            "time at k, evaluation remaining budget), clipped at zero"
        ),
        "alternative_success": (
            "fraction of calibration transversal traces successful within evaluation remaining budget"
        ),
        "alternative_cost": (
            "mean min(transversal time-to-success-or-exhaustion, evaluation remaining budget)"
        ),
        "utility": "P(success) - lambda_cost * E(capped remaining cost)/remaining_budget",
        "raw_advantage": (
            "alternative_utility > direct_utility + hysteresis OR "
            "(direct_success_probability < deadline_success_floor AND "
            "alternative_success_probability >= deadline_success_floor)"
        ),
        "switch": "two consecutive raw-advantage checkpoints; no mid-config interruption",
    }


def _survives_after_index(row: dict[str, Any], k: int) -> bool:
    obs = row["direct"]["observations"]
    return len(obs) > k and not bool(obs[k]["success"])


def _later_direct_from_checkpoint(row: dict[str, Any], k: int) -> tuple[bool, float]:
    obs = row["direct"]["observations"]
    at = float(obs[k]["cumulative_seconds"])
    later = obs[k + 1 :]
    later_hit = next((o for o in later if o["success"]), None)
    if later_hit is not None:
        return True, max(0.0, float(later_hit["cumulative_seconds"]) - at)
    return False, max(0.0, float(row["direct"]["time_to_success_or_exhaustion_seconds"]) - at)


def conditional_snapshot(
    calibration_rows: Sequence[dict[str, Any]],
    k: int,
    remaining_budget: float,
    thresholds: dict[str, Any],
) -> dict[str, Any]:
    if remaining_budget <= 0:
        return {
            "raw_advantage": False,
            "reason": "no_remaining_budget",
            "remaining_budget": remaining_budget,
        }
    survivors = [r for r in calibration_rows if _survives_after_index(r, k)]
    if not survivors:
        # No evidence for what happens after this checkpoint: do not switch on an empty conditioning set.
        return {
            "raw_advantage": False,
            "reason": "no_calibration_survivors",
            "remaining_budget": remaining_budget,
            "survivor_count": 0,
        }

    d_success_indicators: list[float] = []
    d_costs: list[float] = []
    for r in survivors:
        later_success, later_time = _later_direct_from_checkpoint(r, k)
        d_success_indicators.append(float(later_success and later_time <= remaining_budget))
        d_costs.append(min(max(0.0, later_time), remaining_budget))

    a_success_indicators: list[float] = []
    a_costs: list[float] = []
    for r in calibration_rows:
        t = float(r["transversal"]["time_to_success_or_exhaustion_seconds"])
        ok = bool(r["transversal"]["success"] and t <= remaining_budget)
        a_success_indicators.append(float(ok))
        a_costs.append(min(max(0.0, t), remaining_budget))

    dp = float(np.mean(d_success_indicators))
    dc = float(np.mean(d_costs))
    ap = float(np.mean(a_success_indicators))
    ac = float(np.mean(a_costs))
    lam = float(thresholds["lambda_cost"])
    du = dp - lam * dc / remaining_budget
    au = ap - lam * ac / remaining_budget
    raw = bool(
        au > du + float(thresholds["hysteresis"])
        or (
            dp < float(thresholds["deadline_success_floor"])
            and ap >= float(thresholds["deadline_success_floor"])
        )
    )
    return {
        "raw_advantage": raw,
        "reason": "computed",
        "remaining_budget": remaining_budget,
        "survivor_count": len(survivors),
        "direct_success_probability": dp,
        "direct_capped_remaining_cost": dc,
        "direct_utility": du,
        "alternative_success_probability": ap,
        "alternative_capped_remaining_cost": ac,
        "alternative_utility": au,
    }


def _alt_finish(row: dict[str, Any], elapsed: float, deadline: float) -> tuple[bool, float, int]:
    remaining = max(0.0, deadline - elapsed)
    alt = row["transversal"]
    alt_time = float(alt["time_to_success_or_exhaustion_seconds"])
    finish = elapsed + alt_time
    success = bool(alt["success"] and alt_time <= remaining)
    return success, min(finish, deadline), len(alt["observations"])


def simulate_policy(
    row: dict[str, Any],
    calibration_rows: Sequence[dict[str, Any]],
    derived: dict[str, Any],
    policy: str,
) -> dict[str, Any]:
    validate_row(row)
    t = derived["thresholds"]
    deadline = float(t["deadline_seconds"])
    elapsed = 0.0
    eval_count = 0
    prior_advantage = False
    switch_checkpoint_index: int | None = None
    snapshots: list[dict[str, Any]] = []

    for o in row["direct"]["observations"]:
        wall = float(o["wall_seconds"])
        if elapsed + wall > deadline:
            return {
                "success": False,
                "capped_wall_time": deadline,
                "evaluation_count": eval_count,
                "switched": False,
                "switch_checkpoint_index": None,
                "snapshots": snapshots,
            }
        elapsed += wall
        eval_count += 1
        if o["success"]:
            return {
                "success": True,
                "capped_wall_time": elapsed,
                "evaluation_count": eval_count,
                "switched": False,
                "switch_checkpoint_index": None,
                "snapshots": snapshots,
            }

        remaining = deadline - elapsed
        should_switch = False
        if policy == "direct_only":
            should_switch = False
        elif policy == "fixed_cap":
            should_switch = elapsed >= float(t["fixed_cap_seconds"]) and remaining > 0
        elif policy == "static_percentile":
            should_switch = elapsed >= float(t["static_percentile_switch_seconds"]) and remaining > 0
        elif policy == "conditional_reforecast":
            snap = conditional_snapshot(calibration_rows, int(o["index"]), remaining, t)
            snap = {"direct_checkpoint_index": int(o["index"]), **snap}
            snapshots.append(snap)
            raw = bool(snap["raw_advantage"])
            should_switch = bool(raw and prior_advantage)
            prior_advantage = raw
        else:
            raise ValueError(f"unknown policy: {policy}")

        if should_switch:
            switch_checkpoint_index = int(o["index"]) + 1  # 1-based completed-direct count
            ok, finish, alt_count = _alt_finish(row, elapsed, deadline)
            return {
                "success": ok,
                "capped_wall_time": finish,
                "evaluation_count": eval_count + alt_count,
                "switched": True,
                "switch_checkpoint_index": switch_checkpoint_index,
                "snapshots": snapshots,
            }

    # Direct exhausted without a success.
    return {
        "success": False,
        "capped_wall_time": min(elapsed, deadline),
        "evaluation_count": eval_count,
        "switched": False,
        "switch_checkpoint_index": None,
        "snapshots": snapshots,
    }


def aggregate_policy(results: Sequence[dict[str, Any]]) -> dict[str, Any]:
    if not results:
        raise ValueError("empty results")
    times = np.asarray([r["capped_wall_time"] for r in results], dtype=float)
    switch_idxs = [r["switch_checkpoint_index"] for r in results if r["switched"]]
    return {
        "episode_count": len(results),
        "success_by_deadline": float(np.mean([r["success"] for r in results])),
        "mean_capped_wall_time": float(np.mean(times)),
        "p90_capped_wall_time": float(np.percentile(times, 90)),
        "mean_number_of_evaluations": float(np.mean([r["evaluation_count"] for r in results])),
        "switch_rate": float(np.mean([r["switched"] for r in results])),
        "mean_switch_checkpoint_index": float(np.mean(switch_idxs)) if switch_idxs else None,
    }


def candidate_rule(candidate: dict[str, Any], baseline: dict[str, Any]) -> bool:
    cs = float(candidate["success_by_deadline"])
    bs = float(baseline["success_by_deadline"])
    ct = float(candidate["mean_capped_wall_time"])
    bt = float(baseline["mean_capped_wall_time"])
    # Clause 1: any positive success improvement, while mean time worsens by no more than 10%.
    success_clause = (cs > bs) and (ct <= 1.10 * bt)
    # Clause 2: >=10% mean-time improvement, while success loss is at most 0.02.
    speed_clause = (ct <= 0.90 * bt) and (cs >= bs - 0.02)
    return bool(success_clause or speed_clause)


def simulate_all(
    confirmation_rows: Sequence[dict[str, Any]],
    calibration_rows: Sequence[dict[str, Any]],
    derived: dict[str, Any],
) -> dict[str, Any]:
    policies = ("direct_only", "fixed_cap", "static_percentile", "conditional_reforecast")
    per_policy: dict[str, list[dict[str, Any]]] = {}
    aggregates: dict[str, dict[str, Any]] = {}
    for p in policies:
        rs = [simulate_policy(r, calibration_rows, derived, p) for r in confirmation_rows]
        per_policy[p] = rs
        aggregates[p] = aggregate_policy(rs)
    base = aggregates["direct_only"]
    for p in ("fixed_cap", "static_percentile", "conditional_reforecast"):
        aggregates[p]["meets_candidate_rule"] = candidate_rule(aggregates[p], base)
    report = {
        "schema_version": 1,
        "confirmation_row_digests": [r["row_sha256"] for r in confirmation_rows],
        "calibration_derived_sha256": derived["derived_sha256"],
        "policy_results": aggregates,
        "per_episode": per_policy,
        "candidate_rule": CANDIDATE_RULE,
    }
    report["report_sha256"] = sha256_obj(report)
    return report


def atomic_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    data = json.dumps(obj, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(data)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)
    # fsync containing directory for rename durability on POSIX.
    try:
        fd = os.open(path.parent, os.O_DIRECTORY)
    except (AttributeError, OSError):
        fd = None
    if fd is not None:
        try:
            os.fsync(fd)
        finally:
            os.close(fd)


def append_episode_jsonl(path: Path, row: dict[str, Any]) -> None:
    validate_row(row)
    path.parent.mkdir(parents=True, exist_ok=True)
    line = json.dumps(row, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n"
    with open(path, "a", encoding="utf-8") as f:
        f.write(line)
        f.flush()
        os.fsync(f.fileno())


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    seen: set[int] = set()
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            row = json.loads(line)
            validate_row(row)
            seed = int(row["seed"])
            if seed in seen:
                raise ValueError(f"duplicate seed in {path}: {seed}")
            seen.add(seed)
            rows.append(row)
    return rows


def cli() -> None:
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)

    pe = sub.add_parser("episode")
    pe.add_argument("--seed", type=int, required=True)
    pe.add_argument("--out-jsonl", type=Path, required=True)

    pd = sub.add_parser("derive")
    pd.add_argument("--calibration-jsonl", type=Path, required=True)
    pd.add_argument("--out-json", type=Path, required=True)

    ps = sub.add_parser("simulate")
    ps.add_argument("--calibration-jsonl", type=Path, required=True)
    ps.add_argument("--derived-json", type=Path, required=True)
    ps.add_argument("--confirmation-jsonl", type=Path, required=True)
    ps.add_argument("--out-json", type=Path, required=True)

    pm = sub.add_parser("manifest")
    pm.add_argument("--out-json", type=Path, required=True)

    args = p.parse_args()
    if args.cmd == "episode":
        row = measure_episode(args.seed)
        append_episode_jsonl(args.out_jsonl, row)
        print(json.dumps({"seed": args.seed, "row_sha256": row["row_sha256"]}, sort_keys=True))
    elif args.cmd == "derive":
        rows = read_jsonl(args.calibration_jsonl)
        derived = derive_calibration(rows)
        atomic_json(args.out_json, derived)
        print(json.dumps({"derived_sha256": derived["derived_sha256"]}, sort_keys=True))
    elif args.cmd == "simulate":
        c = read_jsonl(args.calibration_jsonl)
        with open(args.derived_json, "r", encoding="utf-8") as f:
            d = json.load(f)
        conf = read_jsonl(args.confirmation_jsonl)
        report = simulate_all(conf, c, d)
        atomic_json(args.out_json, report)
        print(json.dumps({"report_sha256": report["report_sha256"]}, sort_keys=True))
    elif args.cmd == "manifest":
        m = environment_manifest()
        m["manifest_sha256"] = sha256_obj(m)
        atomic_json(args.out_json, m)
        print(json.dumps({"manifest_sha256": m["manifest_sha256"]}, sort_keys=True))


if __name__ == "__main__":
    cli()
