#!/usr/bin/env python3
"""Multi-panel stability test for frozen CAL-LEX-3ARM-v1 on two fresh public datasets.

No model measurement occurs at import time. Selector rule and cap/deadline constants are
unchanged from CAL-LEX-3ARM-v1. This adapter adds independent calibration panels and a
single untouched confirmation panel to falsify small-calibration arm-choice stability.
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

import numpy as np
import sklearn
import statsmodels
import statsmodels.api as sm
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import balanced_accuracy_score
from sklearn.model_selection import StratifiedKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

SCHEMA_VERSION = 1
SELECTOR_VERSION = "CAL-LEX-3ARM-v1"
ADAPTER_VERSION = "CAL-LEX-3ARM-STABILITY-v1"
FIXED_CAP_MULTIPLIER = 0.50
CONDITIONAL_CAP_MULTIPLIER = 1.50
DEADLINE_ALT_P90_MULTIPLIER = 1.05
P90_QUANTILE_METHOD = "higher"
CALIBRATION_PANELS = {
    "panel_a": list(range(18000, 18008)),
    "panel_b": list(range(18100, 18108)),
    "panel_c": list(range(18200, 18208)),
}
CONFIRMATION_SEEDS = list(range(19000, 19012))
SCENARIOS = {
    "fair_alt_needed": {
        "dataset": "statsmodels.datasets.fair",
        "target_definition": "affairs > 0",
        "metric": "balanced_accuracy",
        "target": 0.60,
        "direct": "DummyClassifier(strategy=most_frequent)",
        "alternative": "StandardScaler+LogisticRegression(C=1,max_iter=2000,solver=lbfgs)",
    },
    "spector_direct_good": {
        "dataset": "statsmodels.datasets.spector",
        "target_definition": "GRADE",
        "metric": "balanced_accuracy",
        "target": 0.55,
        "direct": "StandardScaler+LogisticRegression(C=1,max_iter=2000,solver=lbfgs)",
        "alternative": "RandomForestClassifier(n_estimators=400,max_features=sqrt,n_jobs=1)",
    },
}


def canon(x):
    return json.dumps(x, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def fsync_new(path: Path, text: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as f:
        f.write(text)
        f.flush()
        os.fsync(f.fileno())


def append(path: Path, row: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(canon(row) + "\n")
        f.flush()
        os.fsync(f.fileno())


def rows(path: Path):
    return [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]


def environment():
    return {
        "schema_version": 1,
        "selector_version": SELECTOR_VERSION,
        "adapter_version": ADAPTER_VERSION,
        "python": sys.version,
        "platform": platform.platform(),
        "machine": platform.machine(),
        "sklearn": sklearn.__version__,
        "numpy": np.__version__,
        "statsmodels": statsmodels.__version__,
        "timing": "time.perf_counter_ns around fit+predict per fold; sum 3 folds",
        "cv": "StratifiedKFold(3,shuffle=True,random_state=seed)",
        "threading": "RandomForest n_jobs=1; LogisticRegression/Dummy sklearn defaults",
    }


def load_scenario(name: str):
    if name == "fair_alt_needed":
        df = sm.datasets.fair.load_pandas().data.copy()
        y = (df.pop("affairs").to_numpy() > 0).astype(int)
        X = df.to_numpy(dtype=float)
        return X, y
    if name == "spector_direct_good":
        df = sm.datasets.spector.load_pandas().data.copy()
        y = df.pop("GRADE").to_numpy(dtype=int)
        X = df.to_numpy(dtype=float)
        return X, y
    raise ValueError(name)


def models(name: str, seed: int):
    if name == "fair_alt_needed":
        return (
            DummyClassifier(strategy="most_frequent"),
            make_pipeline(StandardScaler(), LogisticRegression(C=1, max_iter=2000, solver="lbfgs")),
        )
    if name == "spector_direct_good":
        return (
            make_pipeline(StandardScaler(), LogisticRegression(C=1, max_iter=2000, solver="lbfgs")),
            RandomForestClassifier(
                n_estimators=400, max_features="sqrt", random_state=seed, n_jobs=1
            ),
        )
    raise ValueError(name)


def eval_model(model, X, y, splits):
    runtimes = []
    scores = []
    for tr, te in splits:
        t0 = time.perf_counter_ns()
        model.fit(X[tr], y[tr])
        pred = model.predict(X[te])
        runtimes.append((time.perf_counter_ns() - t0) / 1e9)
        scores.append(float(balanced_accuracy_score(y[te], pred)))
    return float(sum(runtimes)), float(statistics.fmean(scores))


def measure_one(name: str, seed: int, phase: str, panel: str | None):
    X, y = load_scenario(name)
    cv = StratifiedKFold(n_splits=3, shuffle=True, random_state=seed)
    splits = list(cv.split(X, y))
    direct, alternative = models(name, seed)
    dr, ds = eval_model(direct, X, y, splits)
    ar, aas = eval_model(alternative, X, y, splits)
    target = float(SCENARIOS[name]["target"])
    return {
        "schema_version": 1,
        "selector_version": SELECTOR_VERSION,
        "adapter_version": ADAPTER_VERSION,
        "phase": phase,
        "panel": panel,
        "scenario": name,
        "seed": int(seed),
        "metric": "balanced_accuracy",
        "target": target,
        "direct_runtime_s": dr,
        "direct_score": ds,
        "direct_success": bool(ds >= target),
        "alternative_runtime_s": ar,
        "alternative_score": aas,
        "alternative_success": bool(aas >= target),
    }


def sim_policy(r: dict, s: dict, policy: str):
    dr = float(r["direct_runtime_s"])
    ar = float(r["alternative_runtime_s"])
    ds = bool(r["direct_success"])
    aas = bool(r["alternative_success"])
    deadline = float(s["deadline_s"])
    if policy == "direct":
        return {
            "success": bool(dr <= deadline and ds),
            "time_s": dr if dr <= deadline and ds else deadline,
            "switched": False,
        }
    cap = float(s["fixed_cap_s"] if policy == "fixed" else s["conditional_cap_s"])
    if dr <= cap:
        if ds:
            return {"success": True, "time_s": dr, "switched": False}
        start = dr
    else:
        start = cap
    total = start + ar
    return {
        "success": bool(total <= deadline and aas),
        "time_s": total if total <= deadline and aas else deadline,
        "switched": True,
    }


def summary(v):
    ts = [float(r["time_s"]) for r in v]
    return {
        "count": len(v),
        "success_rate": float(np.mean([bool(r["success"]) for r in v])),
        "mean_capped_time_s": float(np.mean(ts)),
        "p90_capped_time_s": float(np.quantile(np.array(ts), 0.90, method=P90_QUANTILE_METHOD)),
        "switch_rate": float(np.mean([bool(r["switched"]) for r in v])),
    }


def derive_panel(all_rows: list[dict], panel: str):
    if panel not in CALIBRATION_PANELS:
        raise ValueError(panel)
    out = {
        "schema_version": 1,
        "selector_version": SELECTOR_VERSION,
        "adapter_version": ADAPTER_VERSION,
        "panel": panel,
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
    for name in SCENARIOS:
        q = [r for r in all_rows if r["phase"] == "calibration" and r["panel"] == panel and r["scenario"] == name]
        if sorted(int(r["seed"]) for r in q) != CALIBRATION_PANELS[panel]:
            raise ValueError(name + ": calibration seeds mismatch")
        dr = np.array([r["direct_runtime_s"] for r in q])
        ar = np.array([r["alternative_runtime_s"] for r in q])
        d50 = float(np.median(dr))
        ap90 = float(np.quantile(ar, 0.90, method=P90_QUANTILE_METHOD))
        base = {
            "target": SCENARIOS[name]["target"],
            "calibration_count": len(q),
            "direct_success_rate": float(np.mean([r["direct_success"] for r in q])),
            "alternative_success_rate": float(np.mean([r["alternative_success"] for r in q])),
            "direct_runtime_median_s": d50,
            "alternative_runtime_p90_s": ap90,
            "fixed_cap_s": FIXED_CAP_MULTIPLIER * d50,
            "conditional_cap_s": CONDITIONAL_CAP_MULTIPLIER * d50,
            "deadline_s": FIXED_CAP_MULTIPLIER * d50 + DEADLINE_ALT_P90_MULTIPLIER * ap90,
        }
        pm = {p: summary([sim_policy(r, base, p) for r in q]) for p in ("direct", "fixed", "conditional")}
        priority = {"direct": 0, "fixed": 1, "conditional": 2}
        choice = min(
            ("direct", "fixed", "conditional"),
            key=lambda p: (-pm[p]["success_rate"], pm[p]["mean_capped_time_s"], priority[p]),
        )
        out["scenarios"][name] = {**base, "calibration_policy_metrics": pm, "selector_choice": choice}
    return out


def confirm(snapshots: list[dict], conf_rows: list[dict]):
    expected = CONFIRMATION_SEEDS
    for name in SCENARIOS:
        q = [r for r in conf_rows if r["phase"] == "confirmation" and r["scenario"] == name]
        if sorted(int(r["seed"]) for r in q) != expected:
            raise ValueError(name + ": confirmation seeds mismatch")

    out = {
        "schema_version": 1,
        "selector_version": SELECTOR_VERSION,
        "adapter_version": ADAPTER_VERSION,
        "panel_results": {},
        "choice_stability": {},
        "candidate_rule": {},
    }
    choices_by_scenario = {name: [] for name in SCENARIOS}
    panel_gate = []
    alt_gate = []
    for snap in snapshots:
        panel = snap["panel"]
        pool = {p: [] for p in ("direct", "fixed", "conditional", "selector")}
        scenario_results = {}
        for name in SCENARIOS:
            s = snap["scenarios"][name]
            choice = str(s["selector_choice"])
            choices_by_scenario[name].append(choice)
            alt_gate.append(float(s["alternative_success_rate"]) >= 0.80)
            q = [r for r in conf_rows if r["scenario"] == name]
            pr = {p: [sim_policy(r, s, p) for r in q] for p in ("direct", "fixed", "conditional")}
            pr["selector"] = pr[choice]
            metrics = {p: summary(v) for p, v in pr.items()}
            for p, v in pr.items():
                pool[p].extend(v)
            cm = metrics[choice]
            nondominated = True
            for other in ("direct", "fixed", "conditional"):
                if other == choice:
                    continue
                om = metrics[other]
                nondominated = nondominated and (
                    cm["success_rate"] > om["success_rate"]
                    or (
                        math.isclose(cm["success_rate"], om["success_rate"], rel_tol=0, abs_tol=1e-12)
                        and cm["mean_capped_time_s"] <= 1.05 * om["mean_capped_time_s"]
                    )
                )
            scenario_results[name] = {
                "selector_choice": choice,
                "metrics": metrics,
                "selected_policy_nondominated_vs_other": bool(nondominated),
            }
        pooled = {p: summary(v) for p, v in pool.items()}
        sel = pooled["selector"]
        arms = [pooled[p] for p in ("direct", "fixed", "conditional")]
        pooled_success_gate = sel["success_rate"] + 1e-12 >= max(x["success_rate"] for x in arms)
        best_mean = min(x["mean_capped_time_s"] for x in arms)
        pooled_time_gate = sel["mean_capped_time_s"] <= 1.05 * best_mean + 1e-12
        scenario_gate = all(x["selected_policy_nondominated_vs_other"] for x in scenario_results.values())
        panel_pass = bool(pooled_success_gate and pooled_time_gate and scenario_gate)
        panel_gate.append(panel_pass)
        out["panel_results"][panel] = {
            "scenarios": scenario_results,
            "pooled": pooled,
            "pooled_success_gte_every_universal_arm": bool(pooled_success_gate),
            "pooled_mean_lte_1_05x_best_universal_arm": bool(pooled_time_gate),
            "selected_policy_nondominated_each_scenario": bool(scenario_gate),
            "panel_pass": panel_pass,
        }

    stability = {}
    for name, choices in choices_by_scenario.items():
        stability[name] = {
            "choices": choices,
            "stable": len(set(choices)) == 1,
        }
    out["choice_stability"] = stability
    gates = {
        "calibration_alternative_success_rate_gte_0_80_all_panels_scenarios": all(alt_gate),
        "selector_choice_stable_across_all_three_panels_each_scenario": all(v["stable"] for v in stability.values()),
        "every_panel_confirmation_competitive": all(panel_gate),
    }
    out["candidate_rule"] = {**gates, "pass": bool(all(gates.values()))}
    return out


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    e = sub.add_parser("environment")
    e.add_argument("--output", required=True)
    m = sub.add_parser("measure")
    m.add_argument("--phase", choices=["calibration", "confirmation"], required=True)
    m.add_argument("--panel")
    m.add_argument("--seeds", required=True)
    m.add_argument("--output", required=True)
    d = sub.add_parser("derive")
    d.add_argument("--panel", choices=sorted(CALIBRATION_PANELS), required=True)
    d.add_argument("--input", required=True)
    d.add_argument("--output", required=True)
    c = sub.add_parser("confirm")
    c.add_argument("--snapshots", nargs=3, required=True)
    c.add_argument("--input", required=True)
    c.add_argument("--output", required=True)
    args = ap.parse_args()

    if args.cmd == "environment":
        fsync_new(Path(args.output), canon(environment()) + "\n")
        return
    if args.cmd == "measure":
        lo, hi = [int(x) for x in args.seeds.split(":")]
        seeds = list(range(lo, hi + 1))
        if args.phase == "calibration":
            if args.panel not in CALIBRATION_PANELS or seeds != CALIBRATION_PANELS[args.panel]:
                raise ValueError("calibration panel/seeds differ from preregistration")
            panel = args.panel
        else:
            if args.panel is not None or seeds != CONFIRMATION_SEEDS:
                raise ValueError("confirmation seeds differ from preregistration")
            panel = None
        out = Path(args.output)
        existing = rows(out) if out.exists() else []
        for name in SCENARIOS:
            for seed in seeds:
                if any(r["scenario"] == name and int(r["seed"]) == seed and r.get("panel") == panel for r in existing):
                    raise RuntimeError("duplicate measurement forbidden")
                r = measure_one(name, seed, args.phase, panel)
                append(out, r)
                existing.append(r)
        return
    if args.cmd == "derive":
        fsync_new(Path(args.output), canon(derive_panel(rows(Path(args.input)), args.panel)) + "\n")
        return
    if args.cmd == "confirm":
        snaps = [json.loads(Path(x).read_text(encoding="utf-8")) for x in args.snapshots]
        fsync_new(Path(args.output), canon(confirm(snaps, rows(Path(args.input)))) + "\n")
        return


if __name__ == "__main__":
    main()
