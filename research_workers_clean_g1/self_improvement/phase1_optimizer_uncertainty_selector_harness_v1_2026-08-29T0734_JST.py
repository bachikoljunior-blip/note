#!/usr/bin/env python3
"""Preregistered uncertainty-aware calibration selector study.

CAL-WILSON-3ARM-v1 keeps CAL-LEX-3ARM-v1 policy semantics and first-8 runtime
thresholds. It changes only arm selection: a stage-1 direct choice with reliable
fallback available cannot be accepted from 8/8 empirical success alone when the
one-sided 95% Wilson lower bound is below the frozen 0.80 reliability floor.
Exactly four additional calibration seeds are then consumed. Thresholds are NOT
refit on the extension rows; they estimate success uncertainty only.
"""
from __future__ import annotations
import argparse, json, math, os, platform, statistics, sys, time
from pathlib import Path
import numpy as np, sklearn, statsmodels
import statsmodels.api as sm
from sklearn.datasets import load_iris
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import balanced_accuracy_score
from sklearn.model_selection import StratifiedKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

SCHEMA_VERSION=1
BASELINE_VERSION="CAL-LEX-3ARM-v1"
SELECTOR_VERSION="CAL-WILSON-3ARM-v1"
STUDY_VERSION="CAL-WILSON-3ARM-STUDY-v1"
STAGE1_SEEDS=list(range(20000,20008))
EXTENSION_SEEDS=list(range(20008,20012))
CALIBRATION_SEEDS=STAGE1_SEEDS+EXTENSION_SEEDS
CONFIRMATION_SEEDS=list(range(21000,21024))
FIXED_CAP_MULTIPLIER=.50
CONDITIONAL_CAP_MULTIPLIER=1.50
DEADLINE_ALT_P90_MULTIPLIER=1.05
P90_QUANTILE_METHOD="higher"
WILSON_ONE_SIDED_CONFIDENCE=.95
WILSON_Z=1.6448536269514722
DIRECT_RELIABILITY_FLOOR=.80
FALLBACK_ALT_SUCCESS_FLOOR=.80
SCENARIOS={
 "fair_alt_needed_fresh":{"dataset":"statsmodels.datasets.fair","target":.60,"direct":"DummyClassifier(most_frequent)","alternative":"StandardScaler+LogisticRegression(C=1,max_iter=2000,solver=lbfgs)"},
 "spector_direct_rare_fresh":{"dataset":"statsmodels.datasets.spector","target":.55,"direct":"StandardScaler+LogisticRegression(C=1,max_iter=2000,solver=lbfgs)","alternative":"RandomForestClassifier(n_estimators=400,max_features=sqrt,n_jobs=1)"},
 "iris_direct_good_fresh":{"dataset":"sklearn.datasets.load_iris","target":.90,"direct":"StandardScaler+LogisticRegression(C=1,max_iter=2000,solver=lbfgs)","alternative":"RandomForestClassifier(n_estimators=400,max_features=sqrt,n_jobs=1)"},
}

def canon(x): return json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=False)
def fsync_new(path,text):
 path.parent.mkdir(parents=True,exist_ok=True)
 with path.open("x",encoding="utf-8") as f: f.write(text); f.flush(); os.fsync(f.fileno())
def append(path,row):
 path.parent.mkdir(parents=True,exist_ok=True)
 with path.open("a",encoding="utf-8") as f: f.write(canon(row)+"\n"); f.flush(); os.fsync(f.fileno())
def rows(path): return [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]
def env(): return {"schema_version":1,"baseline_version":BASELINE_VERSION,"selector_version":SELECTOR_VERSION,"study_version":STUDY_VERSION,"python":sys.version,"platform":platform.platform(),"machine":platform.machine(),"sklearn":sklearn.__version__,"numpy":np.__version__,"statsmodels":statsmodels.__version__,"timing":"time.perf_counter_ns around fit+predict per fold; sum 3 folds","cv":"StratifiedKFold(3,shuffle=True,random_state=seed)","threading":"RandomForest n_jobs=1; others sklearn defaults"}
def load(name):
 if name.startswith("fair_"):
  df=sm.datasets.fair.load_pandas().data.copy(); y=(df.pop("affairs").to_numpy()>0).astype(int); return df.to_numpy(dtype=float),y
 if name.startswith("spector_"):
  df=sm.datasets.spector.load_pandas().data.copy(); y=df.pop("GRADE").to_numpy(dtype=int); return df.to_numpy(dtype=float),y
 if name.startswith("iris_"): return load_iris(return_X_y=True)
 raise ValueError(name)
def models(name,seed):
 if name.startswith("fair_"): return DummyClassifier(strategy="most_frequent"),make_pipeline(StandardScaler(),LogisticRegression(C=1,max_iter=2000,solver="lbfgs"))
 if name.startswith("spector_") or name.startswith("iris_"):
  return make_pipeline(StandardScaler(),LogisticRegression(C=1,max_iter=2000,solver="lbfgs")),RandomForestClassifier(n_estimators=400,max_features="sqrt",random_state=seed,n_jobs=1)
 raise ValueError(name)
def eval_model(m,X,y,sp):
 rt=[]; sc=[]
 for tr,te in sp:
  t=time.perf_counter_ns(); m.fit(X[tr],y[tr]); p=m.predict(X[te]); rt.append((time.perf_counter_ns()-t)/1e9); sc.append(float(balanced_accuracy_score(y[te],p)))
 return float(sum(rt)),float(statistics.fmean(sc))
def measure_one(name,seed,phase):
 X,y=load(name); sp=list(StratifiedKFold(n_splits=3,shuffle=True,random_state=seed).split(X,y)); d,a=models(name,seed); dr,ds=eval_model(d,X,y,sp); ar,aas=eval_model(a,X,y,sp); target=float(SCENARIOS[name]["target"])
 return {"schema_version":1,"study_version":STUDY_VERSION,"phase":phase,"scenario":name,"seed":int(seed),"metric":"balanced_accuracy","target":target,"direct_runtime_s":dr,"direct_score":ds,"direct_success":bool(ds>=target),"alternative_runtime_s":ar,"alternative_score":aas,"alternative_success":bool(aas>=target)}
def sim_policy(r,s,p):
 dr,ar=float(r["direct_runtime_s"]),float(r["alternative_runtime_s"]); ds,aas=bool(r["direct_success"]),bool(r["alternative_success"]); deadline=float(s["deadline_s"])
 if p=="direct": return {"success":bool(dr<=deadline and ds),"time_s":dr if dr<=deadline and ds else deadline,"switched":False}
 cap=float(s["fixed_cap_s"] if p=="fixed" else s["conditional_cap_s"])
 if dr<=cap:
  if ds:return {"success":True,"time_s":dr,"switched":False}
  start=dr
 else:start=cap
 total=start+ar
 return {"success":bool(total<=deadline and aas),"time_s":total if total<=deadline and aas else deadline,"switched":True}
def summary(v):
 ts=[float(r["time_s"]) for r in v]
 return {"count":len(v),"success_rate":float(np.mean([bool(r["success"]) for r in v])),"success_count":int(sum(bool(r["success"]) for r in v)),"mean_capped_time_s":float(np.mean(ts)),"p90_capped_time_s":float(np.quantile(np.array(ts),.90,method=P90_QUANTILE_METHOD)),"switch_rate":float(np.mean([bool(r["switched"]) for r in v]))}
def wilson_lower(k,n):
 if n<=0:return 0.0
 p=k/n; z=WILSON_Z; den=1+z*z/n; center=(p+z*z/(2*n))/den; half=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/den
 return float(max(0.0,center-half))
def stage1_base(q):
 dr=np.array([r["direct_runtime_s"] for r in q]); ar=np.array([r["alternative_runtime_s"] for r in q]); d50=float(np.median(dr)); ap90=float(np.quantile(ar,.90,method=P90_QUANTILE_METHOD))
 return {"direct_runtime_median_s":d50,"alternative_runtime_p90_s":ap90,"fixed_cap_s":FIXED_CAP_MULTIPLIER*d50,"conditional_cap_s":CONDITIONAL_CAP_MULTIPLIER*d50,"deadline_s":FIXED_CAP_MULTIPLIER*d50+DEADLINE_ALT_P90_MULTIPLIER*ap90}
def lex_choice(pm,candidates):
 priority={"direct":0,"fixed":1,"conditional":2}
 return min(candidates,key=lambda p:(-pm[p]["success_rate"],pm[p]["mean_capped_time_s"],priority[p]))
def derive(cal):
 out={"schema_version":1,"baseline_version":BASELINE_VERSION,"selector_version":SELECTOR_VERSION,"study_version":STUDY_VERSION,"constants":{"stage1_count":8,"extension_count":4,"direct_reliability_floor":DIRECT_RELIABILITY_FLOOR,"fallback_alt_success_floor":FALLBACK_ALT_SUCCESS_FLOOR,"wilson_one_sided_confidence":WILSON_ONE_SIDED_CONFIDENCE,"wilson_z":WILSON_Z,"fixed_cap_multiplier":FIXED_CAP_MULTIPLIER,"conditional_cap_multiplier":CONDITIONAL_CAP_MULTIPLIER,"deadline_alt_p90_multiplier":DEADLINE_ALT_P90_MULTIPLIER,"p90_quantile_method":P90_QUANTILE_METHOD},"scenarios":{}}
 for name in SCENARIOS:
  allq=[r for r in cal if r["scenario"]==name and r["phase"]=="calibration"]
  if sorted(int(r["seed"]) for r in allq)!=CALIBRATION_SEEDS: raise ValueError(name+": calibration seeds mismatch")
  q8=[r for r in allq if int(r["seed"]) in STAGE1_SEEDS]; base=stage1_base(q8)
  pm8={p:summary([sim_policy(r,base,p) for r in q8]) for p in ("direct","fixed","conditional")}; baseline=lex_choice(pm8,("direct","fixed","conditional"))
  alt8=float(np.mean([bool(r["alternative_success"]) for r in q8])); d8=pm8["direct"]; fb8=max(pm8["fixed"]["success_rate"],pm8["conditional"]["success_rate"])
  fallback8=bool(alt8>=FALLBACK_ALT_SUCCESS_FLOOR and fb8+1e-12>=d8["success_rate"])
  lcb8=wilson_lower(d8["success_count"],d8["count"])
  extend=bool(baseline=="direct" and fallback8 and lcb8+1e-12<DIRECT_RELIABILITY_FLOOR)
  used=allq if extend else q8
  pm={p:summary([sim_policy(r,base,p) for r in used]) for p in ("direct","fixed","conditional")}; alt=float(np.mean([bool(r["alternative_success"]) for r in used])); d=pm["direct"]; fb=max(pm["fixed"]["success_rate"],pm["conditional"]["success_rate"]); fallback=bool(alt>=FALLBACK_ALT_SUCCESS_FLOOR and fb+1e-12>=d["success_rate"]); lcb=wilson_lower(d["success_count"],d["count"])
  direct_eligible=bool((not fallback) or lcb+1e-12>=DIRECT_RELIABILITY_FLOOR or d["success_rate"]>fb+1e-12)
  candidates=("direct","fixed","conditional") if direct_eligible else ("fixed","conditional")
  choice=lex_choice(pm,candidates)
  out["scenarios"][name]={**base,"target":SCENARIOS[name]["target"],"stage1_policy_metrics":pm8,"stage1_alternative_success_rate":alt8,"stage1_direct_wilson_lcb":lcb8,"stage1_baseline_choice":baseline,"extension_required":extend,"used_calibration_count":len(used),"used_policy_metrics":pm,"used_alternative_success_rate":alt,"direct_wilson_lcb":lcb,"fallback_available":fallback,"direct_eligible":direct_eligible,"selector_choice":choice}
 return out
def confirm(snap,conf):
 out={"schema_version":1,"baseline_version":BASELINE_VERSION,"selector_version":SELECTOR_VERSION,"study_version":STUDY_VERSION,"scenarios":{},"pooled":{},"candidate_rule":{}}; pools={p:[] for p in ("direct","fixed","conditional","callex","wilson")}; rare=[]; choices=[]; ext_ok=[]
 for name in SCENARIOS:
  q=[r for r in conf if r["scenario"]==name and r["phase"]=="confirmation"]
  if sorted(int(r["seed"]) for r in q)!=CONFIRMATION_SEEDS: raise ValueError(name+": confirmation seeds mismatch")
  s=snap["scenarios"][name]; pr={p:[sim_policy(r,s,p) for r in q] for p in ("direct","fixed","conditional")}; bc=s["stage1_baseline_choice"]; wc=s["selector_choice"]; pr["callex"]=pr[bc]; pr["wilson"]=pr[wc]; metrics={p:summary(v) for p,v in pr.items()}; choices.append(wc)
  for p,v in pr.items(): pools[p].extend(v)
  d8=s["stage1_policy_metrics"]["direct"]; fallback8=bool(s["stage1_alternative_success_rate"]>=FALLBACK_ALT_SUCCESS_FLOOR and max(s["stage1_policy_metrics"]["fixed"]["success_rate"],s["stage1_policy_metrics"]["conditional"]["success_rate"])+1e-12>=d8["success_rate"])
  trigger=bool(s["stage1_baseline_choice"]=="direct" and fallback8 and s["stage1_direct_wilson_lcb"]+1e-12<DIRECT_RELIABILITY_FLOOR); ext_ok.append(trigger==bool(s["extension_required"]))
  rare_case=bool(d8["success_count"]==8 and metrics["direct"]["success_rate"]<1.0-1e-12 and fallback8); guarded=(not rare_case) or wc!="direct"; rare.append(guarded)
  out["scenarios"][name]={"callex_choice":bc,"wilson_choice":wc,"extension_required":bool(s["extension_required"]),"used_calibration_count":int(s["used_calibration_count"]),"direct_wilson_lcb":float(s["direct_wilson_lcb"]),"rare_8_of_8_confirmation_failure_case":rare_case,"rare_case_guarded":guarded,"metrics":metrics}
 out["pooled"]={p:summary(v) for p,v in pools.items()}; nw=out["pooled"]["wilson"]; bl=out["pooled"]["callex"]; uc=out["pooled"]["conditional"]
 gates={"extension_trigger_logic_exact":all(ext_ok),"rare_8_of_8_overconfidence_cases_guarded":all(rare),"wilson_selector_uses_at_least_two_distinct_arms":len(set(choices))>=2,"wilson_pooled_success_gte_callex":nw["success_rate"]+1e-12>=bl["success_rate"],"wilson_mean_capped_time_lte_universal_conditional":nw["mean_capped_time_s"]<=uc["mean_capped_time_s"]+1e-12,"calibration_budget_each_scenario_lte_12":all(int(snap["scenarios"][n]["used_calibration_count"])<=12 for n in SCENARIOS)}
 out["candidate_rule"]={**gates,"pass":bool(all(gates.values()))}; return out
def main():
 ap=argparse.ArgumentParser(); sub=ap.add_subparsers(dest="cmd",required=True)
 e=sub.add_parser("environment"); e.add_argument("--output",required=True)
 m=sub.add_parser("measure"); m.add_argument("--phase",choices=["calibration","confirmation"],required=True); m.add_argument("--seeds",required=True); m.add_argument("--output",required=True)
 d=sub.add_parser("derive"); d.add_argument("--input",required=True); d.add_argument("--output",required=True)
 c=sub.add_parser("confirm"); c.add_argument("--snapshot",required=True); c.add_argument("--input",required=True); c.add_argument("--output",required=True)
 a=ap.parse_args()
 if a.cmd=="environment": fsync_new(Path(a.output),canon(env())+"\n"); return
 if a.cmd=="measure":
  lo,hi=[int(x) for x in a.seeds.split(":")]; seeds=list(range(lo,hi+1)); exp=CALIBRATION_SEEDS if a.phase=="calibration" else CONFIRMATION_SEEDS
  if seeds!=exp: raise ValueError("seed range differs from preregistration")
  out=Path(a.output); existing=rows(out) if out.exists() else []
  for name in SCENARIOS:
   for seed in seeds:
    if any(r["scenario"]==name and int(r["seed"])==seed for r in existing): raise RuntimeError("duplicate measurement forbidden")
    r=measure_one(name,seed,a.phase); append(out,r); existing.append(r)
  return
 if a.cmd=="derive": fsync_new(Path(a.output),canon(derive(rows(Path(a.input))))+"\n"); return
 if a.cmd=="confirm": fsync_new(Path(a.output),canon(confirm(json.loads(Path(a.snapshot).read_text()),rows(Path(a.input))))+"\n"); return
if __name__=="__main__": main()
