#!/usr/bin/env python3
"""CAL-WILSON-3ARM-v2: confidence-aware staged calibration study.
No model timing occurs at import time. Runtime thresholds remain CAL-LEX-v1 first-8 formulas.
"""
from __future__ import annotations
import argparse,json,math,os,platform,statistics,sys,time
from pathlib import Path
import numpy as np, sklearn, statsmodels
import statsmodels.api as sm
from sklearn.datasets import load_iris,load_wine,load_digits
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import balanced_accuracy_score
from sklearn.model_selection import StratifiedKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

BASELINE_VERSION="CAL-LEX-3ARM-v1"; SELECTOR_VERSION="CAL-WILSON-3ARM-v2"; STUDY_VERSION="CAL-WILSON-3ARM-V2-STUDY-v1"
STAGE1=list(range(22000,22008)); EXT=list(range(22008,22012)); CONF=list(range(23000,23024))
FIXED=.5; CONDITIONAL=1.5; ALT_P90=1.05; Z=1.6448536269514722; FLOOR=.80; P90="higher"
SCENARIOS={
 "fair_alt_needed_v2":{"dataset":"statsmodels.fair","target":.60},
 "spector_rare_v2":{"dataset":"statsmodels.spector","target":.55},
 "iris_direct_v2":{"dataset":"sklearn.iris","target":.90},
 "wine_direct_v2":{"dataset":"sklearn.wine","target":.95},
 "digits_mixed_v2":{"dataset":"sklearn.digits","target":.95},
}

def canon(x):return json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=False)
def fsync_new(p:Path,text:str):
 p.parent.mkdir(parents=True,exist_ok=True)
 with p.open("x",encoding="utf-8") as f:f.write(text);f.flush();os.fsync(f.fileno())
def append(p:Path,r):
 p.parent.mkdir(parents=True,exist_ok=True)
 with p.open("a",encoding="utf-8") as f:f.write(canon(r)+"\n");f.flush();os.fsync(f.fileno())
def rows(p:Path):return [json.loads(x) for x in p.read_text().splitlines() if x.strip()]
def env():return {"schema_version":1,"baseline_version":BASELINE_VERSION,"selector_version":SELECTOR_VERSION,"study_version":STUDY_VERSION,"python":sys.version,"platform":platform.platform(),"machine":platform.machine(),"sklearn":sklearn.__version__,"numpy":np.__version__,"statsmodels":statsmodels.__version__,"timing":"time.perf_counter_ns around fit+predict per fold; sum 3 folds","cv":"StratifiedKFold(3,shuffle=True,random_state=seed)","threading":"RF n_jobs=1; others sklearn defaults"}
def load(name):
 if name.startswith("fair_"):
  d=sm.datasets.fair.load_pandas().data.copy();y=(d.pop("affairs").to_numpy()>0).astype(int);return d.to_numpy(float),y
 if name.startswith("spector_"):
  d=sm.datasets.spector.load_pandas().data.copy();y=d.pop("GRADE").to_numpy(int);return d.to_numpy(float),y
 if name.startswith("iris_"):return load_iris(return_X_y=True)
 if name.startswith("wine_"):return load_wine(return_X_y=True)
 if name.startswith("digits_"):return load_digits(return_X_y=True)
 raise ValueError(name)
def models(name,seed):
 if name.startswith("fair_"):return DummyClassifier(strategy="most_frequent"),make_pipeline(StandardScaler(),LogisticRegression(C=1,max_iter=2000,solver="lbfgs"))
 if name.startswith("digits_"):return make_pipeline(StandardScaler(),LogisticRegression(C=1,max_iter=3000,solver="lbfgs")),make_pipeline(StandardScaler(),SVC(C=10,gamma="scale"))
 return make_pipeline(StandardScaler(),LogisticRegression(C=1,max_iter=2000,solver="lbfgs")),RandomForestClassifier(n_estimators=400,max_features="sqrt",random_state=seed,n_jobs=1)
def eval_model(m,X,y,sp):
 rt=[];sc=[]
 for tr,te in sp:
  t=time.perf_counter_ns();m.fit(X[tr],y[tr]);p=m.predict(X[te]);rt.append((time.perf_counter_ns()-t)/1e9);sc.append(float(balanced_accuracy_score(y[te],p)))
 return float(sum(rt)),float(statistics.fmean(sc))
def measure(name,seed,phase):
 X,y=load(name);sp=list(StratifiedKFold(3,shuffle=True,random_state=seed).split(X,y));d,a=models(name,seed);dr,ds=eval_model(d,X,y,sp);ar,aas=eval_model(a,X,y,sp);target=SCENARIOS[name]["target"]
 return {"schema_version":1,"study_version":STUDY_VERSION,"phase":phase,"scenario":name,"seed":seed,"target":target,"direct_runtime_s":dr,"direct_score":ds,"direct_success":ds>=target,"alternative_runtime_s":ar,"alternative_score":aas,"alternative_success":aas>=target}
def sim(r,s,p):
 dr,ar=float(r["direct_runtime_s"]),float(r["alternative_runtime_s"]);ds,aa=bool(r["direct_success"]),bool(r["alternative_success"]);deadline=s["deadline_s"]
 if p=="direct":return {"success":bool(dr<=deadline and ds),"time_s":dr if dr<=deadline and ds else deadline,"switched":False}
 cap=s["fixed_cap_s"] if p=="fixed" else s["conditional_cap_s"]
 if dr<=cap:
  if ds:return {"success":True,"time_s":dr,"switched":False}
  start=dr
 else:start=cap
 total=start+ar;return {"success":bool(total<=deadline and aa),"time_s":total if total<=deadline and aa else deadline,"switched":True}
def summ(v):
 ts=[x["time_s"] for x in v];return {"count":len(v),"success_count":sum(bool(x["success"]) for x in v),"success_rate":float(np.mean([x["success"] for x in v])),"mean_capped_time_s":float(np.mean(ts)),"p90_capped_time_s":float(np.quantile(np.array(ts),.9,method=P90)),"switch_rate":float(np.mean([x["switched"] for x in v]))}
def lcb(k,n):
 if n==0:return 0.0
 p=k/n;den=1+Z*Z/n;return float(max(0,(p+Z*Z/(2*n))/den-Z*math.sqrt(p*(1-p)/n+Z*Z/(4*n*n))/den))
def base(q):
 dr=np.array([r["direct_runtime_s"] for r in q]);ar=np.array([r["alternative_runtime_s"] for r in q]);d50=float(np.median(dr));ap90=float(np.quantile(ar,.9,method=P90));return {"direct_runtime_median_s":d50,"alternative_runtime_p90_s":ap90,"fixed_cap_s":FIXED*d50,"conditional_cap_s":CONDITIONAL*d50,"deadline_s":FIXED*d50+ALT_P90*ap90}
def lex(pm):
 pri={"direct":0,"fixed":1,"conditional":2};return min(pri,key=lambda p:(-pm[p]["success_rate"],pm[p]["mean_capped_time_s"],pri[p]))
def confchoice(pm):
 pri={"direct":0,"fixed":1,"conditional":2};return min(pri,key=lambda p:(-lcb(pm[p]["success_count"],pm[p]["count"]),-pm[p]["success_rate"],pm[p]["mean_capped_time_s"],pri[p]))
def make_plan(rs):
 out={"schema_version":1,"study_version":STUDY_VERSION,"selector_version":SELECTOR_VERSION,"scenarios":{}}
 for n in SCENARIOS:
  q=[r for r in rs if r["scenario"]==n]
  if sorted(r["seed"] for r in q)!=STAGE1:raise ValueError(n)
  b=base(q);pm={p:summ([sim(r,b,p) for r in q]) for p in ("direct","fixed","conditional")};bc=lex(pm);dl=lcb(pm["direct"]["success_count"],8);ext=bool(bc=="direct" and dl<FLOOR)
  out["scenarios"][n]={**b,"stage1_policy_metrics":pm,"callex_choice":bc,"direct_wilson_lcb":dl,"extension_required":ext}
 return out
def snapshot(stage,ext,plan):
 out={"schema_version":1,"study_version":STUDY_VERSION,"selector_version":SELECTOR_VERSION,"baseline_version":BASELINE_VERSION,"constants":{"wilson_one_sided_confidence":.95,"wilson_z":Z,"reliability_floor":FLOOR,"fixed_cap_multiplier":FIXED,"conditional_cap_multiplier":CONDITIONAL,"deadline_alt_p90_multiplier":ALT_P90,"p90_method":P90},"scenarios":{}}
 for n in SCENARIOS:
  s=plan["scenarios"][n];q=[r for r in stage if r["scenario"]==n];e=[r for r in ext if r["scenario"]==n]
  if s["extension_required"]:
   if sorted(r["seed"] for r in e)!=EXT:raise ValueError(n+" extension")
   used=q+e
  else:
   if e:raise ValueError(n+" unexpected extension")
   used=q
  pm={p:summ([sim(r,s,p) for r in used]) for p in ("direct","fixed","conditional")};choice=confchoice(pm)
  out["scenarios"][n]={**s,"used_calibration_count":len(used),"used_policy_metrics":pm,"policy_wilson_lcb":{p:lcb(pm[p]["success_count"],pm[p]["count"]) for p in pm},"selector_choice":choice}
 return out
def confirm(snap,rs):
 pools={p:[] for p in ("direct","fixed","conditional","callex","wilson2")};sc={};rare_any=False;rare_guard=[];choices=[]
 for n in SCENARIOS:
  q=[r for r in rs if r["scenario"]==n]
  if sorted(r["seed"] for r in q)!=CONF:raise ValueError(n)
  s=snap["scenarios"][n];pr={p:[sim(r,s,p) for r in q] for p in ("direct","fixed","conditional")};pr["callex"]=pr[s["callex_choice"]];pr["wilson2"]=pr[s["selector_choice"]];m={p:summ(v) for p,v in pr.items()};
  for p,v in pr.items():pools[p]+=v
  d8=s["stage1_policy_metrics"]["direct"];rare=bool(d8["success_count"]==8 and m["direct"]["success_rate"]<1-1e-12);rare_any=rare_any or rare;guard=(not rare) or (s["selector_choice"]!="direct" and m["wilson2"]["success_rate"]+1e-12>=m["callex"]["success_rate"]);rare_guard.append(guard);choices.append(s["selector_choice"])
  sc[n]={"callex_choice":s["callex_choice"],"wilson2_choice":s["selector_choice"],"extension_required":s["extension_required"],"used_calibration_count":s["used_calibration_count"],"rare_8_of_8_confirmation_failure_case":rare,"rare_case_guarded":guard,"metrics":m}
 pool={p:summ(v) for p,v in pools.items()};nw=pool["wilson2"];bl=pool["callex"];uc=pool["conditional"]
 gates={"nonvacuity_rare_8_of_8_case_observed":rare_any,"every_rare_case_guarded":all(rare_guard),"extension_trigger_exact":all(snap["scenarios"][n]["extension_required"]==(snap["scenarios"][n]["callex_choice"]=="direct" and snap["scenarios"][n]["direct_wilson_lcb"]<FLOOR) for n in SCENARIOS),"selector_uses_at_least_two_arms":len(set(choices))>=2,"pooled_success_gte_callex":nw["success_rate"]+1e-12>=bl["success_rate"],"mean_lte_universal_conditional":nw["mean_capped_time_s"]<=uc["mean_capped_time_s"]+1e-12,"mean_lte_1_5x_callex":nw["mean_capped_time_s"]<=1.5*bl["mean_capped_time_s"]+1e-12,"calibration_budget_lte_12":all(snap["scenarios"][n]["used_calibration_count"]<=12 for n in SCENARIOS)}
 status="INCONCLUSIVE" if not rare_any else ("PASS" if all(gates.values()) else "FAIL")
 return {"schema_version":1,"study_version":STUDY_VERSION,"selector_version":SELECTOR_VERSION,"scenarios":sc,"pooled":pool,"candidate_gates":gates,"status":status}
def measure_cmd(names,seeds,phase,out):
 existing=rows(out) if out.exists() else []
 for n in names:
  for seed in seeds:
   if any(r["scenario"]==n and r["seed"]==seed for r in existing):raise RuntimeError("duplicate")
   r=measure(n,seed,phase);append(out,r);existing.append(r)
def main():
 ap=argparse.ArgumentParser();sub=ap.add_subparsers(dest="cmd",required=True)
 for cmd in ("stage1","extension","confirmation"):
  p=sub.add_parser(cmd);p.add_argument("--output",required=True);p.add_argument("--plan")
 p=sub.add_parser("plan");p.add_argument("--input",required=True);p.add_argument("--output",required=True)
 p=sub.add_parser("snapshot");p.add_argument("--stage1",required=True);p.add_argument("--extension",required=True);p.add_argument("--plan",required=True);p.add_argument("--output",required=True)
 p=sub.add_parser("confirm");p.add_argument("--snapshot",required=True);p.add_argument("--input",required=True);p.add_argument("--output",required=True)
 p=sub.add_parser("environment");p.add_argument("--output",required=True)
 a=ap.parse_args()
 if a.cmd=="environment":fsync_new(Path(a.output),canon(env())+"\n");return
 if a.cmd=="stage1":measure_cmd(SCENARIOS,STAGE1,"calibration_stage1",Path(a.output));return
 if a.cmd=="plan":fsync_new(Path(a.output),canon(make_plan(rows(Path(a.input))))+"\n");return
 if a.cmd=="extension":
  pl=json.loads(Path(a.plan).read_text());names=[n for n in SCENARIOS if pl["scenarios"][n]["extension_required"]];measure_cmd(names,EXT,"calibration_extension",Path(a.output));return
 if a.cmd=="snapshot":fsync_new(Path(a.output),canon(snapshot(rows(Path(a.stage1)),rows(Path(a.extension)) if Path(a.extension).exists() else [],json.loads(Path(a.plan).read_text())))+"\n");return
 if a.cmd=="confirmation":measure_cmd(SCENARIOS,CONF,"confirmation",Path(a.output));return
 if a.cmd=="confirm":fsync_new(Path(a.output),canon(confirm(json.loads(Path(a.snapshot).read_text()),rows(Path(a.input))))+"\n");return
if __name__=="__main__":main()
