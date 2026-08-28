#!/usr/bin/env python3
"""Replay-complete Phase-1 replay-complete three-arm calibration-only meta-selector benchmark.

No workload measurement is performed at import time. The study is intentionally
split into measure -> derive -> confirmation-measure -> simulate so that the
selector rule and calibration-derived parameters can be frozen before holdout
simulation.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import platform
import statistics
import sys
import time
from pathlib import Path
from typing import Any

import numpy as np
import sklearn
from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import balanced_accuracy_score
from sklearn.model_selection import StratifiedKFold
from sklearn.dummy import DummyClassifier
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
import statsmodels.api as sm

SCHEMA_VERSION = 1
SELECTOR_VERSION = "CAL-LEX-3ARM-v1"
CALIBRATION_SEEDS = list(range(16000, 16008))
CONFIRMATION_SEEDS = list(range(17000, 17012))
FIXED_CAP_MULTIPLIER = 0.50
CONDITIONAL_CAP_MULTIPLIER = 1.50
DEADLINE_ALT_P90_MULTIPLIER = 1.05
P90_QUANTILE_METHOD = "higher"

SCENARIOS: dict[str, dict[str, Any]] = {
    "iris_direct_good": {
        "dataset": "sklearn.datasets.load_iris",
        "target_balanced_accuracy": 0.93,
        "direct": "StandardScaler + LogisticRegression(C=1.0,max_iter=2000,solver=lbfgs)",
        "alternative": "RandomForestClassifier(n_estimators=400,max_features=sqrt,n_jobs=1)",
    },
    "spector_alt_needed": {
        "dataset": "statsmodels.datasets.spector",
        "target_balanced_accuracy": 0.55,
        "direct": "DummyClassifier(strategy=most_frequent)",
        "alternative": "StandardScaler + LogisticRegression(C=1.0,max_iter=2000,solver=lbfgs)",
    },
}

def canonical(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)

def fsync_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        f.write(text)
        f.flush()
        os.fsync(f.fileno())

def append_fsync(path: Path, row: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(canonical(row) + "\n")
        f.flush()
        os.fsync(f.fileno())

def environment_manifest() -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "python": sys.version,
        "platform": platform.platform(),
        "machine": platform.machine(),
        "sklearn": sklearn.__version__,
        "numpy": np.__version__,
        "statsmodels": sm.__version__,
        "timing": "time.perf_counter_ns around fit+predict for each fold; summed across 3 folds",
        "cv": "StratifiedKFold(n_splits=3,shuffle=True,random_state=seed)",
        "threading": "RandomForest n_jobs=1; other estimators use sklearn defaults",
    }

def load_scenario(name: str):
    if name == "iris_direct_good":
        return load_iris(return_X_y=True)
    if name == "spector_alt_needed":
        d = sm.datasets.spector.load_pandas()
        return np.asarray(d.exog, dtype=float), np.asarray(d.endog, dtype=int)
    raise KeyError(name)

def models(name: str, seed: int):
    if name == "iris_direct_good":
        direct = make_pipeline(
            StandardScaler(),
            LogisticRegression(C=1.0, max_iter=2000, solver="lbfgs"),
        )
        alt = RandomForestClassifier(
            n_estimators=400,
            max_features="sqrt",
            random_state=seed,
            n_jobs=1,
        )
        return direct, alt
    if name == "spector_alt_needed":
        direct = DummyClassifier(strategy="most_frequent")
        alt = make_pipeline(
            StandardScaler(),
            LogisticRegression(C=1.0, max_iter=2000, solver="lbfgs"),
        )
        return direct, alt
    raise KeyError(name)

def evaluate_model(model, X, y, splits) -> tuple[float, float]:
    runtimes: list[float] = []
    scores: list[float] = []
    for train_idx, test_idx in splits:
        t0 = time.perf_counter_ns()
        model.fit(X[train_idx], y[train_idx])
        pred = model.predict(X[test_idx])
        t1 = time.perf_counter_ns()
        runtimes.append((t1 - t0) / 1e9)
        scores.append(float(balanced_accuracy_score(y[test_idx], pred)))
    return float(sum(runtimes)), float(statistics.fmean(scores))

def measure_one(scenario: str, seed: int, phase: str) -> dict[str, Any]:
    X, y = load_scenario(scenario)
    cv = StratifiedKFold(n_splits=3, shuffle=True, random_state=seed)
    splits = list(cv.split(X, y))
    direct, alt = models(scenario, seed)
    direct_runtime, direct_score = evaluate_model(direct, X, y, splits)
    alt_runtime, alt_score = evaluate_model(alt, X, y, splits)
    target = float(SCENARIOS[scenario]["target_balanced_accuracy"])
    return {
        "schema_version": SCHEMA_VERSION,
        "phase": phase,
        "scenario": scenario,
        "seed": int(seed),
        "target_balanced_accuracy": target,
        "direct_runtime_s": direct_runtime,
        "direct_score": direct_score,
        "direct_success": bool(direct_score >= target),
        "alternative_runtime_s": alt_runtime,
        "alternative_score": alt_score,
        "alternative_success": bool(alt_score >= target),
    }

def parse_seed_range(text: str) -> list[int]:
    if ":" in text:
        a, b = text.split(":", 1)
        return list(range(int(a), int(b) + 1))
    return [int(x) for x in text.split(",") if x]

def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows

def derive(rows: list[dict[str, Any]]) -> dict[str, Any]:
    out: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "selector_version": SELECTOR_VERSION,
        "selector_rule": {
            "policy_set": ["direct", "fixed", "conditional"],
            "primary": "maximize calibration deadline-success rate",
            "secondary": "minimize calibration mean capped time",
            "exact_tie_priority": ["direct", "fixed", "conditional"],
        },
        "constants": {
            "fixed_cap_multiplier": FIXED_CAP_MULTIPLIER,
            "conditional_cap_multiplier": CONDITIONAL_CAP_MULTIPLIER,
            "deadline_alt_p90_multiplier": DEADLINE_ALT_P90_MULTIPLIER,
            "p90_quantile_method": P90_QUANTILE_METHOD,
        },
        "scenarios": {},
    }
    for scenario in SCENARIOS:
        sr = [r for r in rows if r["scenario"] == scenario]
        if sorted(int(r["seed"]) for r in sr) != CALIBRATION_SEEDS:
            raise ValueError(f"{scenario}: calibration seeds mismatch")
        d_rt = np.array([r["direct_runtime_s"] for r in sr], dtype=float)
        a_rt = np.array([r["alternative_runtime_s"] for r in sr], dtype=float)
        direct_rate = float(np.mean([bool(r["direct_success"]) for r in sr]))
        alt_rate = float(np.mean([bool(r["alternative_success"]) for r in sr]))
        d50 = float(np.median(d_rt))
        alt_p90 = float(np.quantile(a_rt, 0.90, method=P90_QUANTILE_METHOD))
        fixed_cap = float(FIXED_CAP_MULTIPLIER * d50)
        conditional_cap = float(CONDITIONAL_CAP_MULTIPLIER * d50)
        deadline = float(fixed_cap + DEADLINE_ALT_P90_MULTIPLIER * alt_p90)
        preliminary = {
            "target_balanced_accuracy": SCENARIOS[scenario]["target_balanced_accuracy"],
            "calibration_count": len(sr),
            "direct_success_rate": direct_rate,
            "alternative_success_rate": alt_rate,
            "direct_runtime_median_s": d50,
            "alternative_runtime_p90_s": alt_p90,
            "fixed_cap_s": fixed_cap,
            "conditional_cap_s": conditional_cap,
            "deadline_s": deadline,
        }
        policy_metrics = {}
        tie_priority = {"direct": 0, "fixed": 1, "conditional": 2}
        for policy in ("direct", "fixed", "conditional"):
            recs = [simulate_policy(r, preliminary, policy) for r in sr]
            policy_metrics[policy] = summarize(recs)
        choice = min(
            ("direct", "fixed", "conditional"),
            key=lambda p: (-policy_metrics[p]["success_rate"], policy_metrics[p]["mean_capped_time_s"], tie_priority[p]),
        )
        out["scenarios"][scenario] = {
            "target_balanced_accuracy": SCENARIOS[scenario]["target_balanced_accuracy"],
            "calibration_count": len(sr),
            "direct_success_rate": direct_rate,
            "alternative_success_rate": alt_rate,
            "direct_runtime_median_s": d50,
            "alternative_runtime_p90_s": alt_p90,
            "fixed_cap_s": fixed_cap,
            "conditional_cap_s": conditional_cap,
            "deadline_s": deadline,
            "calibration_policy_metrics": policy_metrics,
            "selector_choice": choice,
        }
    return out

def simulate_policy(row: dict[str, Any], snap: dict[str, Any], policy: str) -> dict[str, Any]:
    dr = float(row["direct_runtime_s"])
    ar = float(row["alternative_runtime_s"])
    ds = bool(row["direct_success"])
    aas = bool(row["alternative_success"])
    deadline = float(snap["deadline_s"])
    if policy == "direct":
        if dr <= deadline and ds:
            return {"success": True, "time_s": dr, "switched": False}
        return {"success": False, "time_s": deadline, "switched": False}
    cap = float(snap["fixed_cap_s"] if policy == "fixed" else snap["conditional_cap_s"])
    if dr <= cap:
        if ds:
            return {"success": True, "time_s": dr, "switched": False}
        start_alt = dr
    else:
        start_alt = cap
    total = start_alt + ar
    if total <= deadline and aas:
        return {"success": True, "time_s": total, "switched": True}
    return {"success": False, "time_s": deadline, "switched": True}

def summarize(records: list[dict[str, Any]]) -> dict[str, Any]:
    times = [float(r["time_s"]) for r in records]
    return {
        "count": len(records),
        "success_rate": float(np.mean([bool(r["success"]) for r in records])),
        "mean_capped_time_s": float(np.mean(times)),
        "p90_capped_time_s": float(np.quantile(np.array(times), 0.90, method=P90_QUANTILE_METHOD)),
        "switch_rate": float(np.mean([bool(r["switched"]) for r in records])),
    }

def simulate(snapshot: dict[str, Any], rows: list[dict[str, Any]]) -> dict[str, Any]:
    all_result: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "selector_version": SELECTOR_VERSION,
        "scenarios": {},
        "pooled": {},
        "candidate_rule": {},
    }
    pooled: dict[str, list[dict[str, Any]]] = {"direct": [], "fixed": [], "conditional": [], "selector": []}
    scenario_nondominated: dict[str, bool] = {}
    choices: list[str] = []
    for scenario in SCENARIOS:
        sr = [r for r in rows if r["scenario"] == scenario]
        if sorted(int(r["seed"]) for r in sr) != CONFIRMATION_SEEDS:
            raise ValueError(f"{scenario}: confirmation seeds mismatch")
        snap = snapshot["scenarios"][scenario]
        choice = str(snap["selector_choice"])
        choices.append(choice)
        policy_rows: dict[str, list[dict[str, Any]]] = {}
        for policy in ("direct", "fixed", "conditional"):
            policy_rows[policy] = [simulate_policy(r, snap, policy) for r in sr]
        policy_rows["selector"] = policy_rows[choice]
        metrics = {p: summarize(v) for p, v in policy_rows.items()}
        for p, v in policy_rows.items():
            pooled[p].extend(v)
        chosen_m = metrics[choice]
        nondominated = True
        for other in ("direct", "fixed", "conditional"):
            if other == choice:
                continue
            other_m = metrics[other]
            pair_ok = (
                chosen_m["success_rate"] > other_m["success_rate"]
                or (
                    math.isclose(chosen_m["success_rate"], other_m["success_rate"], rel_tol=0.0, abs_tol=1e-12)
                    and chosen_m["mean_capped_time_s"] <= 1.05 * other_m["mean_capped_time_s"]
                )
            )
            nondominated = nondominated and pair_ok
        scenario_nondominated[scenario] = bool(nondominated)
        all_result["scenarios"][scenario] = {
            "selector_choice": choice,
            "metrics": metrics,
            "selected_policy_nondominated_vs_other": bool(nondominated),
        }
    all_result["pooled"] = {p: summarize(v) for p, v in pooled.items()}
    selector = all_result["pooled"]["selector"]
    arms = [all_result["pooled"][p] for p in ("direct", "fixed", "conditional")]
    alt_cal_ok = all(
        snapshot["scenarios"][s]["alternative_success_rate"] >= 0.80 for s in SCENARIOS
    )
    choices_differ = len(set(choices)) >= 2
    pooled_success_gate = selector["success_rate"] + 1e-12 >= max(m["success_rate"] for m in arms)
    pooled_time_gate = selector["mean_capped_time_s"] <= min(m["mean_capped_time_s"] for m in arms) + 1e-12
    per_scenario_gate = all(scenario_nondominated.values())
    all_result["candidate_rule"] = {
        "calibration_alternative_success_rate_gte_0_80_all": bool(alt_cal_ok),
        "selector_uses_at_least_two_distinct_arms": bool(choices_differ),
        "selector_success_rate_gte_every_universal_arm": bool(pooled_success_gate),
        "selector_mean_capped_time_lte_every_universal_arm": bool(pooled_time_gate),
        "selected_policy_nondominated_each_scenario": bool(per_scenario_gate),
        "pass": bool(alt_cal_ok and choices_differ and pooled_success_gate and pooled_time_gate and per_scenario_gate),
    }
    return all_result

def main() -> None:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    m = sub.add_parser("measure")
    m.add_argument("--phase", choices=["calibration", "confirmation"], required=True)
    m.add_argument("--seeds", required=True)
    m.add_argument("--output", required=True)
    d = sub.add_parser("derive")
    d.add_argument("--input", required=True)
    d.add_argument("--output", required=True)
    s = sub.add_parser("simulate")
    s.add_argument("--snapshot", required=True)
    s.add_argument("--confirmation", required=True)
    s.add_argument("--output", required=True)
    e = sub.add_parser("environment")
    e.add_argument("--output", required=True)
    args = ap.parse_args()

    if args.cmd == "environment":
        fsync_text(Path(args.output), canonical(environment_manifest()) + "\n")
        return
    if args.cmd == "measure":
        seeds = parse_seed_range(args.seeds)
        expected = CALIBRATION_SEEDS if args.phase == "calibration" else CONFIRMATION_SEEDS
        if seeds != expected:
            raise SystemExit(f"seed sequence must equal frozen {args.phase} seeds: {expected}")
        out = Path(args.output)
        if out.exists():
            raise SystemExit(f"refuse overwrite: {out}")
        for scenario in SCENARIOS:
            for seed in seeds:
                append_fsync(out, measure_one(scenario, seed, args.phase))
        return
    if args.cmd == "derive":
        out = Path(args.output)
        if out.exists():
            raise SystemExit(f"refuse overwrite: {out}")
        snap = derive(read_jsonl(Path(args.input)))
        fsync_text(out, canonical(snap) + "\n")
        return
    if args.cmd == "simulate":
        out = Path(args.output)
        if out.exists():
            raise SystemExit(f"refuse overwrite: {out}")
        snapshot = json.loads(Path(args.snapshot).read_text(encoding="utf-8"))
        result = simulate(snapshot, read_jsonl(Path(args.confirmation)))
        fsync_text(out, canonical(result) + "\n")
        return

if __name__ == "__main__":
    main()
