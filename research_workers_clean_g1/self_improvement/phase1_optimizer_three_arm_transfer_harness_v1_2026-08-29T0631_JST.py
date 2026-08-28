#!/usr/bin/env python3
"""Replay-complete transfer test for frozen CAL-LEX-3ARM-v1.

Selector rule, cap multipliers, tie priority, and pass logic are unchanged from
sequence 107. Only public non-synthetic workloads/model families and their
success metrics change. No workload measurement occurs at import time.
"""
from __future__ import annotations
import argparse,json,math,os,platform,statistics,sys,time
from pathlib import Path
import numpy as np, sklearn
from sklearn.datasets import load_diabetes,load_iris
from sklearn.dummy import DummyRegressor
from sklearn.ensemble import HistGradientBoostingRegressor,RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import balanced_accuracy_score,r2_score
from sklearn.model_selection import KFold,StratifiedKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

SCHEMA_VERSION=1
SELECTOR_VERSION="CAL-LEX-3ARM-v1"
TRANSFER_ADAPTER_VERSION="CAL-LEX-3ARM-XFER-v1"
CALIBRATION_SEEDS=list(range(16000,16008))
CONFIRMATION_SEEDS=list(range(17000,17012))
FIXED_CAP_MULTIPLIER=0.50
CONDITIONAL_CAP_MULTIPLIER=1.50
DEADLINE_ALT_P90_MULTIPLIER=1.05
P90_QUANTILE_METHOD="higher"
SCENARIOS={
 "iris_direct_good_transfer":{"dataset":"sklearn.datasets.load_iris","task":"classification","metric":"balanced_accuracy","target":0.90,"direct":"StandardScaler+LogisticRegression(C=1,max_iter=2000,solver=lbfgs)","alternative":"RandomForestClassifier(n_estimators=400,max_features=sqrt,n_jobs=1)"},
 "diabetes_alt_needed_transfer":{"dataset":"sklearn.datasets.load_diabetes","task":"regression","metric":"r2","target":0.25,"direct":"DummyRegressor(strategy=mean)","alternative":"HistGradientBoostingRegressor(max_iter=200,learning_rate=0.05,l2_regularization=0)"}}

def canon(x): return json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=False)
def fsync_new(path,text):
 path.parent.mkdir(parents=True,exist_ok=True)
 with path.open("x",encoding="utf-8") as f: f.write(text);f.flush();os.fsync(f.fileno())
def append(path,row):
 path.parent.mkdir(parents=True,exist_ok=True)
 with path.open("a",encoding="utf-8") as f: f.write(canon(row)+"\n");f.flush();os.fsync(f.fileno())
def env(): return {"schema_version":1,"selector_version":SELECTOR_VERSION,"transfer_adapter_version":TRANSFER_ADAPTER_VERSION,"python":sys.version,"platform":platform.platform(),"machine":platform.machine(),"sklearn":sklearn.__version__,"numpy":np.__version__,"timing":"time.perf_counter_ns around fit+predict per fold; sum 3 folds","cv_classification":"StratifiedKFold(3,shuffle=True,random_state=seed)","cv_regression":"KFold(3,shuffle=True,random_state=seed)","threading":"RandomForest n_jobs=1; others sklearn defaults"}
def load(name): return load_iris(return_X_y=True) if name.startswith("iris_") else load_diabetes(return_X_y=True)
def models(name,seed):
 if name.startswith("iris_"):
  return make_pipeline(StandardScaler(),LogisticRegression(C=1,max_iter=2000,solver="lbfgs")),RandomForestClassifier(n_estimators=400,max_features="sqrt",random_state=seed,n_jobs=1)
 return DummyRegressor(strategy="mean"),HistGradientBoostingRegressor(max_iter=200,learning_rate=.05,l2_regularization=0,random_state=seed)
def splits(name,X,y,seed):
 cv=StratifiedKFold(n_splits=3,shuffle=True,random_state=seed) if SCENARIOS[name]["task"]=="classification" else KFold(n_splits=3,shuffle=True,random_state=seed)
 return list(cv.split(X,y))
def score(name,y,p): return float(balanced_accuracy_score(y,p) if SCENARIOS[name]["metric"]=="balanced_accuracy" else r2_score(y,p))
def eval_model(name,m,X,y,sp):
 rt=[];sc=[]
 for tr,te in sp:
  t=time.perf_counter_ns();m.fit(X[tr],y[tr]);p=m.predict(X[te]);rt.append((time.perf_counter_ns()-t)/1e9);sc.append(score(name,y[te],p))
 return float(sum(rt)),float(statistics.fmean(sc))
def measure_one(name,seed,phase):
 X,y=load(name);sp=splits(name,X,y,seed);d,a=models(name,seed);dr,ds=eval_model(name,d,X,y,sp);ar,aas=eval_model(name,a,X,y,sp);target=float(SCENARIOS[name]["target"])
 return {"schema_version":1,"transfer_adapter_version":TRANSFER_ADAPTER_VERSION,"phase":phase,"scenario":name,"seed":int(seed),"task":SCENARIOS[name]["task"],"metric":SCENARIOS[name]["metric"],"target":target,"direct_runtime_s":dr,"direct_score":ds,"direct_success":bool(ds>=target),"alternative_runtime_s":ar,"alternative_score":aas,"alternative_success":bool(aas>=target)}
def rows(path): return [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]
def sim_policy(r,s,p):
 dr,ar=float(r["direct_runtime_s"]),float(r["alternative_runtime_s"]);ds,aas=bool(r["direct_success"]),bool(r["alternative_success"]);deadline=float(s["deadline_s"])
 if p=="direct": return {"success":bool(dr<=deadline and ds),"time_s":dr if dr<=deadline and ds else deadline,"switched":False}
 cap=float(s["fixed_cap_s"] if p=="fixed" else s["conditional_cap_s"])
 if dr<=cap:
  if ds:return {"success":True,"time_s":dr,"switched":False}
  start=dr
 else:start=cap
 total=start+ar
 return {"success":bool(total<=deadline and aas),"time_s":total if total<=deadline and aas else deadline,"switched":True}
def summary(rs):
 ts=[float(r["time_s"]) for r in rs]
 return {"count":len(rs),"success_rate":float(np.mean([bool(r["success"]) for r in rs])),"mean_capped_time_s":float(np.mean(ts)),"p90_capped_time_s":float(np.quantile(np.array(ts),.90,method=P90_QUANTILE_METHOD)),"switch_rate":float(np.mean([bool(r["switched"]) for r in rs]))}
def derive(rs):
 out={"schema_version":1,"selector_version":SELECTOR_VERSION,"transfer_adapter_version":TRANSFER_ADAPTER_VERSION,"selector_rule":{"policy_set":["direct","fixed","conditional"],"primary":"maximize calibration deadline-success rate","secondary":"minimize calibration mean capped time","exact_tie_priority":["direct","fixed","conditional"]},"constants":{"fixed_cap_multiplier":.5,"conditional_cap_multiplier":1.5,"deadline_alt_p90_multiplier":1.05,"p90_quantile_method":"higher"},"scenarios":{}}
 for name in SCENARIOS:
  q=[r for r in rs if r["scenario"]==name]
  if sorted(int(r["seed"]) for r in q)!=CALIBRATION_SEEDS:raise ValueError(name+": calibration seeds mismatch")
  dr=np.array([r["direct_runtime_s"] for r in q]);ar=np.array([r["alternative_runtime_s"] for r in q]);d50=float(np.median(dr));ap90=float(np.quantile(ar,.90,method="higher"));base={"target":SCENARIOS[name]["target"],"calibration_count":len(q),"direct_success_rate":float(np.mean([r["direct_success"] for r in q])),"alternative_success_rate":float(np.mean([r["alternative_success"] for r in q])),"direct_runtime_median_s":d50,"alternative_runtime_p90_s":ap90,"fixed_cap_s":.5*d50,"conditional_cap_s":1.5*d50,"deadline_s":.5*d50+1.05*ap90,"task":SCENARIOS[name]["task"],"metric":SCENARIOS[name]["metric"]};pm={p:summary([sim_policy(r,base,p) for r in q]) for p in ("direct","fixed","conditional")};priority={"direct":0,"fixed":1,"conditional":2};choice=min(("direct","fixed","conditional"),key=lambda p:(-pm[p]["success_rate"],pm[p]["mean_capped_time_s"],priority[p]));out["scenarios"][name]={**base,"calibration_policy_metrics":pm,"selector_choice":choice}
 return out
def simulate(snap,rs):
 out={"schema_version":1,"selector_version":SELECTOR_VERSION,"transfer_adapter_version":TRANSFER_ADAPTER_VERSION,"scenarios":{},"pooled":{},"candidate_rule":{}};pool={p:[] for p in ("direct","fixed","conditional","selector")};nd={};choices=[]
 for name in SCENARIOS:
  q=[r for r in rs if r["scenario"]==name]
  if sorted(int(r["seed"]) for r in q)!=CONFIRMATION_SEEDS:raise ValueError(name+": confirmation seeds mismatch")
  s=snap["scenarios"][name];choice=str(s["selector_choice"]);choices.append(choice);pr={p:[sim_policy(r,s,p) for r in q] for p in ("direct","fixed","conditional")};pr["selector"]=pr[choice];m={p:summary(v) for p,v in pr.items()}
  for p,v in pr.items():pool[p].extend(v)
  cm=m[choice];ok=True
  for other in ("direct","fixed","conditional"):
   if other==choice:continue
   om=m[other];ok=ok and (cm["success_rate"]>om["success_rate"] or (math.isclose(cm["success_rate"],om["success_rate"],rel_tol=0,abs_tol=1e-12) and cm["mean_capped_time_s"]<=1.05*om["mean_capped_time_s"]))
  nd[name]=bool(ok);out["scenarios"][name]={"selector_choice":choice,"metrics":m,"selected_policy_nondominated_vs_other":bool(ok)}
 out["pooled"]={p:summary(v) for p,v in pool.items()};sel=out["pooled"]["selector"];arms=[out["pooled"][p] for p in ("direct","fixed","conditional")];g1=all(snap["scenarios"][n]["alternative_success_rate"]>=.80 for n in SCENARIOS);g2=len(set(choices))>=2;g3=sel["success_rate"]+1e-12>=max(x["success_rate"] for x in arms);g4=sel["mean_capped_time_s"]<=min(x["mean_capped_time_s"] for x in arms)+1e-12;g5=all(nd.values());out["candidate_rule"]={"calibration_alternative_success_rate_gte_0_80_all":g1,"selector_uses_at_least_two_distinct_arms":g2,"selector_success_rate_gte_every_universal_arm":g3,"selector_mean_capped_time_lte_every_universal_arm":g4,"selected_policy_nondominated_each_scenario":g5,"pass":bool(g1 and g2 and g3 and g4 and g5)};return out
def main():
 ap=argparse.ArgumentParser();sub=ap.add_subparsers(dest="cmd",required=True);m=sub.add_parser("measure");m.add_argument("--phase",choices=["calibration","confirmation"],required=True);m.add_argument("--seeds",required=True);m.add_argument("--output",required=True);d=sub.add_parser("derive");d.add_argument("--input",required=True);d.add_argument("--output",required=True);s=sub.add_parser("simulate");s.add_argument("--snapshot",required=True);s.add_argument("--input",required=True);s.add_argument("--output",required=True);e=sub.add_parser("environment");e.add_argument("--output",required=True);a=ap.parse_args()
 if a.cmd=="environment":fsync_new(Path(a.output),canon(env())+"\n");return
 if a.cmd=="measure":
  seeds=[int(x) for x in a.seeds.split(":")];seeds=list(range(seeds[0],seeds[1]+1));exp=CALIBRATION_SEEDS if a.phase=="calibration" else CONFIRMATION_SEEDS
  if seeds!=exp:raise ValueError("seed range differs from preregistration")
  out=Path(a.output);existing=rows(out) if out.exists() else []
  for name in SCENARIOS:
   for seed in seeds:
    if any(r["scenario"]==name and int(r["seed"])==seed for r in existing):raise RuntimeError("duplicate measurement forbidden")
    r=measure_one(name,seed,a.phase);append(out,r);existing.append(r)
  return
 if a.cmd=="derive":fsync_new(Path(a.output),canon(derive(rows(Path(a.input))))+"\n");return
 if a.cmd=="simulate":fsync_new(Path(a.output),canon(simulate(json.loads(Path(a.snapshot).read_text()),rows(Path(a.input))))+"\n");return
if __name__=="__main__":main()
