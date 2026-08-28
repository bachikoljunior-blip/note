#!/usr/bin/env python3
"""Replay-complete Digits optimizer-switching study.

Measurement and policy simulation are deliberately separated:
  measure -> raw JSONL
  derive  -> calibration snapshot only
  simulate -> confirmation policies using frozen calibration snapshot
"""
from __future__ import annotations
import argparse, hashlib, json, math, platform, sys, time
from pathlib import Path
import numpy as np
import sklearn
from sklearn.datasets import load_digits
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import balanced_accuracy_score
from sklearn.model_selection import StratifiedKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

QUALITY_THRESHOLD = 0.97
N_SPLITS = 3
RF_PARAMS = dict(
    n_estimators=140,
    max_depth=9,
    min_samples_leaf=1,
    max_features="sqrt",
    n_jobs=1,
)
SVC_PARAMS = dict(C=3.0, gamma="scale", kernel="rbf", cache_size=400)
DEADLINE_MULTIPLIER = 1.15
FIXED_CAP_FRACTION = 0.50
STATIC_PERCENTILE = 90.0
CHECKPOINT_FRACTIONS = (1.0/3.0, 2.0/3.0)
HYSTERESIS_REQUIRED = 2
UTILITY_MARGIN = 1.10
SWITCH_COST_FRACTION = 0.05
EPS = 1e-12

def canon(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)

def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()

def env_manifest():
    return {
        "python": sys.version.split()[0],
        "sklearn": sklearn.__version__,
        "numpy": np.__version__,
        "platform": platform.platform(),
    }

def parse_seed_spec(spec):
    if ".." in spec:
        a,b = map(int,spec.split("..",1))
        return list(range(a,b+1))
    return [int(x) for x in spec.split(",") if x.strip()]

def eval_family(X, y, seed, family):
    cv = StratifiedKFold(n_splits=N_SPLITS, shuffle=True, random_state=seed)
    fold_runtime, fold_score = [], []
    for fold_idx, (tr, te) in enumerate(cv.split(X, y)):
        if family == "direct_rf":
            model = RandomForestClassifier(random_state=seed, **RF_PARAMS)
        elif family == "alt_svc":
            model = make_pipeline(StandardScaler(), SVC(**SVC_PARAMS))
        else:
            raise ValueError(family)
        t0 = time.perf_counter()
        model.fit(X[tr], y[tr])
        pred = model.predict(X[te])
        elapsed = time.perf_counter() - t0
        fold_runtime.append(elapsed)
        fold_score.append(float(balanced_accuracy_score(y[te], pred)))
    return {
        "family": family,
        "fold_runtime_s": fold_runtime,
        "fold_balanced_accuracy": fold_score,
        "total_runtime_s": float(sum(fold_runtime)),
        "mean_balanced_accuracy": float(sum(fold_score)/len(fold_score)),
    }

def measure(seeds, output, stage):
    X,y = load_digits(return_X_y=True)
    rows=[]
    for seed in seeds:
        d=eval_family(X,y,seed,"direct_rf")
        a=eval_family(X,y,seed,"alt_svc")
        row={
            "schema_version":1,
            "dataset":"sklearn.load_digits",
            "stage":stage,
            "seed":seed,
            "quality_threshold":QUALITY_THRESHOLD,
            "direct":d,
            "alternative":a,
            "environment":env_manifest(),
        }
        rows.append(row)
        with open(output,"a",encoding="utf-8") as f:
            f.write(canon(row)+"\n")
            f.flush()
            import os
            os.fsync(f.fileno())
    return rows

def load_jsonl(path):
    rows=[]
    with open(path,"r",encoding="utf-8") as f:
        for line in f:
            if line.strip(): rows.append(json.loads(line))
    return rows

def percentile_nearest(values,p):
    vals=sorted(float(x) for x in values)
    if not vals: raise ValueError("empty")
    rank=int(math.ceil((p/100.0)*len(vals)))-1
    rank=min(max(rank,0),len(vals)-1)
    return vals[rank]

def derive(calibration_rows):
    direct_t=[r["direct"]["total_runtime_s"] for r in calibration_rows]
    alt_t=[r["alternative"]["total_runtime_s"] for r in calibration_rows]
    deadline=DEADLINE_MULTIPLIER*max(direct_t)
    fixed_cap=FIXED_CAP_FRACTION*deadline
    static_cap=min(percentile_nearest(direct_t,STATIC_PERCENTILE),deadline)
    checkpoints=[f*deadline for f in CHECKPOINT_FRACTIONS]
    alt_runtime=float(np.median(alt_t))
    alt_success=float(np.mean([
        r["alternative"]["mean_balanced_accuracy"]>=QUALITY_THRESHOLD
        for r in calibration_rows
    ]))
    switch_cost=SWITCH_COST_FRACTION*deadline
    forecasts=[]
    consecutive=0
    switch_at=None
    for t in checkpoints:
        eligible=[r for r in calibration_rows if r["direct"]["total_runtime_s"]>t]
        if eligible:
            remaining=float(np.median([
                r["direct"]["total_runtime_s"]-t for r in eligible
            ]))
            direct_success=float(np.mean([
                (r["direct"]["total_runtime_s"]<=deadline and
                 r["direct"]["mean_balanced_accuracy"]>=QUALITY_THRESHOLD)
                for r in eligible
            ]))
        else:
            remaining=0.0
            direct_success=1.0
        direct_utility=direct_success/max(remaining,EPS)
        alt_cost=alt_runtime+switch_cost
        alt_utility=alt_success/max(alt_cost,EPS)
        advantageous=(alt_utility>UTILITY_MARGIN*direct_utility and
                     t+alt_cost<=deadline)
        consecutive=consecutive+1 if advantageous else 0
        if switch_at is None and consecutive>=HYSTERESIS_REQUIRED:
            switch_at=t
        forecasts.append({
            "checkpoint_s":t,
            "eligible_count":len(eligible),
            "predicted_direct_remaining_s":remaining,
            "predicted_direct_success_probability":direct_success,
            "alternative_runtime_median_s":alt_runtime,
            "alternative_success_probability":alt_success,
            "switch_cost_s":switch_cost,
            "direct_utility":direct_utility,
            "alternative_utility":alt_utility,
            "advantageous":advantageous,
            "consecutive_advantage":consecutive,
        })
    return {
        "schema_version":1,
        "calibration_count":len(calibration_rows),
        "quality_threshold":QUALITY_THRESHOLD,
        "deadline_s":deadline,
        "fixed_cap_s":fixed_cap,
        "static_p90_cap_s":static_cap,
        "checkpoints_s":checkpoints,
        "hysteresis_required":HYSTERESIS_REQUIRED,
        "utility_margin":UTILITY_MARGIN,
        "switch_cost_fraction":SWITCH_COST_FRACTION,
        "switch_at_s":switch_at,
        "forecasts":forecasts,
        "calibration_direct_success_probability":float(np.mean([
            (r["direct"]["total_runtime_s"]<=deadline and
             r["direct"]["mean_balanced_accuracy"]>=QUALITY_THRESHOLD)
            for r in calibration_rows
        ])),
        "calibration_direct_p90_runtime_s":percentile_nearest(direct_t,90.0),
    }

def evaluate_policy(rows,snap,policy):
    deadline=snap["deadline_s"]; switch_cost=SWITCH_COST_FRACTION*deadline
    out=[]
    for r in rows:
        dt=r["direct"]["total_runtime_s"]; ds=r["direct"]["mean_balanced_accuracy"]
        at=r["alternative"]["total_runtime_s"]; ass=r["alternative"]["mean_balanced_accuracy"]
        switched=False
        if policy=="direct_only":
            elapsed=dt; quality=ds
        elif policy=="fixed_cap":
            cap=snap["fixed_cap_s"]
            if dt>cap and cap+switch_cost+at<=deadline:
                switched=True; elapsed=cap+switch_cost+at; quality=ass
            else:
                elapsed=dt; quality=ds
        elif policy=="static_percentile":
            cap=snap["static_p90_cap_s"]
            if dt>cap and cap+switch_cost+at<=deadline:
                switched=True; elapsed=cap+switch_cost+at; quality=ass
            else:
                elapsed=dt; quality=ds
        elif policy=="conditional_reforecast":
            cap=snap["switch_at_s"]
            if cap is not None and dt>cap and cap+switch_cost+at<=deadline:
                switched=True; elapsed=cap+switch_cost+at; quality=ass
            else:
                elapsed=dt; quality=ds
        else:
            raise ValueError(policy)
        out.append({
            "seed":r["seed"],
            "elapsed_s":float(elapsed),
            "quality":float(quality),
            "success":bool(elapsed<=deadline and quality>=QUALITY_THRESHOLD),
            "switched":switched,
        })
    return out

def summarize(out,deadline):
    vals=[min(x["elapsed_s"],deadline) for x in out]
    return {
        "n":len(out),
        "success_rate":float(np.mean([x["success"] for x in out])),
        "mean_capped_time_s":float(np.mean(vals)),
        "p90_capped_time_s":percentile_nearest(vals,90.0),
        "switch_rate":float(np.mean([x["switched"] for x in out])),
    }

def simulate(cal_rows, conf_rows, snap):
    policies=["direct_only","fixed_cap","static_percentile","conditional_reforecast"]
    episodes={p:evaluate_policy(conf_rows,snap,p) for p in policies}
    metrics={p:summarize(episodes[p],snap["deadline_s"]) for p in policies}
    empirical_direct_success=float(np.mean([
        (r["direct"]["total_runtime_s"]<=snap["deadline_s"] and
         r["direct"]["mean_balanced_accuracy"]>=QUALITY_THRESHOLD)
        for r in conf_rows
    ]))
    calibration_error=abs(empirical_direct_success-snap["calibration_direct_success_probability"])
    p90_coverage=float(np.mean([
        r["direct"]["total_runtime_s"]<=snap["calibration_direct_p90_runtime_s"]
        for r in conf_rows
    ]))
    cp2=snap["checkpoints_s"][-1]
    eligible=[r for r in conf_rows if r["direct"]["total_runtime_s"]>cp2]
    pred=snap["forecasts"][-1]["predicted_direct_remaining_s"]
    rem_mae=float(np.mean([abs((r["direct"]["total_runtime_s"]-cp2)-pred) for r in eligible])) if eligible else 0.0
    qc={
        "direct_success_probability_abs_error":calibration_error,
        "direct_p90_coverage":p90_coverage,
        "conditional_remaining_cost_mae_s":rem_mae,
        "conditional_remaining_cost_mae_fraction_deadline":rem_mae/max(snap["deadline_s"],EPS),
    }
    c=metrics["conditional_reforecast"]; f=metrics["fixed_cap"]; s=metrics["static_percentile"]
    perf=(c["success_rate"]>=max(f["success_rate"],s["success_rate"]) and
          c["mean_capped_time_s"]<=min(f["mean_capped_time_s"],s["mean_capped_time_s"]))
    qc_pass=(qc["direct_success_probability_abs_error"]<=0.20 and
             qc["direct_p90_coverage"]>=0.80 and
             qc["conditional_remaining_cost_mae_fraction_deadline"]<=0.35)
    return {
        "schema_version":1,
        "metrics":metrics,
        "qc":qc,
        "candidate_rule_performance_pass":perf,
        "candidate_rule_qc_pass":qc_pass,
        "candidate_rule_pass":bool(perf and qc_pass),
        "episodes":episodes,
    }

def main():
    ap=argparse.ArgumentParser()
    sp=ap.add_subparsers(dest="cmd",required=True)
    m=sp.add_parser("measure")
    m.add_argument("--stage",choices=["calibration","confirmation"],required=True)
    m.add_argument("--seeds",required=True)
    m.add_argument("--output",required=True)
    d=sp.add_parser("derive")
    d.add_argument("--calibration",required=True); d.add_argument("--output",required=True)
    s=sp.add_parser("simulate")
    s.add_argument("--calibration",required=True); s.add_argument("--snapshot",required=True)
    s.add_argument("--confirmation",required=True); s.add_argument("--output",required=True)
    a=ap.parse_args()
    if a.cmd=="measure":
        p=Path(a.output); p.parent.mkdir(parents=True,exist_ok=True)
        if p.exists(): raise SystemExit("output exists; refusing overwrite")
        measure(parse_seed_spec(a.seeds),str(p),a.stage)
    elif a.cmd=="derive":
        rows=load_jsonl(a.calibration); out=derive(rows)
        Path(a.output).write_text(canon(out)+"\n",encoding="utf-8")
    else:
        cal=load_jsonl(a.calibration); conf=load_jsonl(a.confirmation)
        snap=json.loads(Path(a.snapshot).read_text(encoding="utf-8"))
        out=simulate(cal,conf,snap)
        Path(a.output).write_text(canon(out)+"\n",encoding="utf-8")
if __name__=="__main__":
    main()
