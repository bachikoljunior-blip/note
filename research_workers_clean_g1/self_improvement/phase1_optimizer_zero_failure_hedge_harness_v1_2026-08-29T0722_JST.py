#!/usr/bin/env python3
"""Fresh public-workload test of CAL-ZFH-3ARM-v1.

Imports the frozen CAL-LEX policy simulator/timing plumbing from the sequence-111
harness. Only the dataset adapter and calibration arm-selection rule differ.
No model measurement occurs at import time.
"""
from __future__ import annotations
import argparse, importlib.util, json, math, os, statistics, sys
from pathlib import Path
import numpy as np
import statsmodels.api as sm
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

HERE = Path(__file__).resolve().parent
BASE_PATH = HERE / "phase1_optimizer_three_arm_stability_harness_v1_2026-08-29T0712_JST.py"
if not BASE_PATH.exists():
    BASE_PATH = Path("/tmp/phase1_optimizer_three_arm_stability_harness_v1.py")
spec = importlib.util.spec_from_file_location("callex_base", BASE_PATH)
B = importlib.util.module_from_spec(spec); spec.loader.exec_module(B)

SELECTOR_VERSION = "CAL-ZFH-3ARM-v1"
ADAPTER_VERSION = "CAL-ZFH-3ARM-FRESH-v1"
PANELS = {"panel_a": list(range(20000,20008)), "panel_b": list(range(20100,20108)), "panel_c": list(range(20200,20208))}
CONFIRM = list(range(21000,21012))
SCENARIOS = {
  "anes96_alt_needed": {"target":0.70,"dataset":"statsmodels.datasets.anes96","target_definition":"vote (0=Clinton,1=Dole)"},
  "star98_direct_good": {"target":0.60,"dataset":"statsmodels.datasets.star98","target_definition":"NABOVE > NBELOW"},
}


def canon(x): return json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=False)
def new(path,text):
    with Path(path).open("x",encoding="utf-8") as f: f.write(text); f.flush(); os.fsync(f.fileno())
def append(path,row):
    with Path(path).open("a",encoding="utf-8") as f: f.write(canon(row)+"\n"); f.flush(); os.fsync(f.fileno())
def rows(path): return [json.loads(x) for x in Path(path).read_text().splitlines() if x.strip()]


def load(name):
    if name=="anes96_alt_needed":
        d=sm.datasets.anes96.load_pandas().data.copy(); y=d.pop("vote").to_numpy(dtype=int); return d.to_numpy(dtype=float),y
    d=sm.datasets.star98.load_pandas().data.copy(); y=(d.NABOVE.to_numpy()>d.NBELOW.to_numpy()).astype(int)
    return d.drop(columns=["NABOVE","NBELOW"]).to_numpy(dtype=float),y


def models(name,seed):
    logit=lambda: make_pipeline(StandardScaler(),LogisticRegression(C=1,max_iter=2000,solver="lbfgs"))
    if name=="anes96_alt_needed": return DummyClassifier(strategy="most_frequent"),logit()
    return logit(),RandomForestClassifier(n_estimators=400,max_features="sqrt",random_state=seed,n_jobs=1)


def measure(name,seed,phase,panel):
    X,y=load(name); cv=B.StratifiedKFold(n_splits=3,shuffle=True,random_state=seed); splits=list(cv.split(X,y))
    dm,am=models(name,seed); dr,ds=B.eval_model(dm,X,y,splits); ar,aas=B.eval_model(am,X,y,splits); t=SCENARIOS[name]["target"]
    return {"schema_version":1,"base_selector_version":"CAL-LEX-3ARM-v1","selector_version":SELECTOR_VERSION,"adapter_version":ADAPTER_VERSION,
            "phase":phase,"panel":panel,"scenario":name,"seed":seed,"metric":"balanced_accuracy","target":t,
            "direct_runtime_s":dr,"direct_score":ds,"direct_success":bool(ds>=t),"alternative_runtime_s":ar,"alternative_score":aas,"alternative_success":bool(aas>=t)}


def choices(pm):
    pr={"direct":0,"fixed":1,"conditional":2}
    callex=min(pm,key=lambda p:(-pm[p]["success_rate"],pm[p]["mean_capped_time_s"],pr[p]))
    mx=max(pm[p]["success_rate"] for p in pm); cand=[p for p in pm if math.isclose(pm[p]["success_rate"],mx,abs_tol=1e-12)]
    hedge=math.isclose(mx,1.0,abs_tol=1e-12) and "direct" in cand and "conditional" in cand
    if hedge: cand.remove("direct")
    zfh=min(cand,key=lambda p:(pm[p]["mean_capped_time_s"],{"fixed":0,"conditional":1,"direct":2}[p]))
    return callex,zfh,hedge


def derive(raw,panel):
    out={"schema_version":1,"base_selector_version":"CAL-LEX-3ARM-v1","selector_version":SELECTOR_VERSION,"adapter_version":ADAPTER_VERSION,"panel":panel,"scenarios":{}}
    for name in SCENARIOS:
        q=[r for r in raw if r["phase"]=="calibration" and r["panel"]==panel and r["scenario"]==name]
        if sorted(r["seed"] for r in q)!=PANELS[panel]: raise ValueError("seed mismatch")
        dr=np.array([r["direct_runtime_s"] for r in q]); ar=np.array([r["alternative_runtime_s"] for r in q]); d50=float(np.median(dr)); ap90=float(np.quantile(ar,.9,method="higher"))
        s={"target":SCENARIOS[name]["target"],"calibration_count":len(q),"direct_success_rate":float(np.mean([r["direct_success"] for r in q])),
           "alternative_success_rate":float(np.mean([r["alternative_success"] for r in q])),"direct_runtime_median_s":d50,"alternative_runtime_p90_s":ap90,
           "fixed_cap_s":.5*d50,"conditional_cap_s":1.5*d50,"deadline_s":.5*d50+1.05*ap90}
        pm={p:B.summary([B.sim_policy(r,s,p) for r in q]) for p in ("direct","fixed","conditional")}; cc,zc,h=choices(pm)
        out["scenarios"][name]={**s,"calibration_policy_metrics":pm,"callex_choice":cc,"zfh_choice":zc,"zero_failure_hedge_applied":h}
    return out


def confirm(snaps,raw):
    for name in SCENARIOS:
        if sorted(r["seed"] for r in raw if r["scenario"]==name)!=CONFIRM: raise ValueError("confirmation seed mismatch")
    out={"schema_version":1,"base_selector_version":"CAL-LEX-3ARM-v1","selector_version":SELECTOR_VERSION,"adapter_version":ADAPTER_VERSION,"panel_results":{},"choice_stability":{},"candidate_rule":{}}
    ch={k:{n:[] for n in SCENARIOS} for k in ("callex","zfh")}; gates=[]; distinct=[]
    for snap in snaps:
        pools={k:[] for k in ("callex","zfh")}; uni={p:[] for p in ("direct","fixed","conditional")}; sr={}
        for name,s in snap["scenarios"].items():
            q=[r for r in raw if r["scenario"]==name]; pr={p:[B.sim_policy(r,s,p) for r in q] for p in uni}
            for p in uni: uni[p]+=pr[p]
            cc,zc=s["callex_choice"],s["zfh_choice"]; ch["callex"][name].append(cc); ch["zfh"][name].append(zc); pools["callex"]+=pr[cc]; pools["zfh"]+=pr[zc]
            sr[name]={"callex_choice":cc,"zfh_choice":zc,"zero_failure_hedge_applied":s["zero_failure_hedge_applied"],"metrics":{p:B.summary(v) for p,v in pr.items()}}
        pu={p:B.summary(v) for p,v in uni.items()}; pc,pz=B.summary(pools["callex"]),B.summary(pools["zfh"])
        reliable=[m for m in pu.values() if m["success_rate"]+1e-12>=pz["success_rate"]]
        cost=(not reliable) or pz["mean_capped_time_s"]<=1.05*min(m["mean_capped_time_s"] for m in reliable)+1e-12
        succ=pz["success_rate"]+1e-12>=pc["success_rate"]; da=len({s["zfh_choice"] for s in snap["scenarios"].values()})>=2; distinct.append(da); pp=bool(cost and succ and da); gates.append(pp)
        out["panel_results"][snap["panel"]]={"scenarios":sr,"pooled_universal":pu,"pooled_callex":pc,"pooled_zfh":pz,"zfh_success_gte_callex":succ,"zfh_mean_lte_1_05x_best_universal_with_success_gte_zfh":bool(cost),"zfh_uses_at_least_two_distinct_arms":da,"panel_pass":pp}
    stab={k:{n:{"choices":v,"stable":len(set(v))==1} for n,v in ch[k].items()} for k in ch}; out["choice_stability"]=stab
    cg={"zfh_choice_stable_across_panels_each_scenario":all(x["stable"] for x in stab["zfh"].values()),"zfh_uses_at_least_two_distinct_arms_each_panel":all(distinct),"every_panel_success_and_cost_competitive":all(gates)}
    out["candidate_rule"]={**cg,"pass":all(cg.values())}; return out


def main():
    ap=argparse.ArgumentParser(); sp=ap.add_subparsers(dest="cmd",required=True)
    e=sp.add_parser("environment"); e.add_argument("--output",required=True)
    m=sp.add_parser("measure"); m.add_argument("--phase",choices=["calibration","confirmation"],required=True); m.add_argument("--panel"); m.add_argument("--seeds",required=True); m.add_argument("--output",required=True)
    d=sp.add_parser("derive"); d.add_argument("--panel",choices=PANELS,required=True); d.add_argument("--input",required=True); d.add_argument("--output",required=True)
    c=sp.add_parser("confirm"); c.add_argument("--snapshots",nargs=3,required=True); c.add_argument("--input",required=True); c.add_argument("--output",required=True); a=ap.parse_args()
    if a.cmd=="environment":
        env=B.environment(); env.update({"base_selector_version":"CAL-LEX-3ARM-v1","selector_version":SELECTOR_VERSION,"adapter_version":ADAPTER_VERSION}); new(a.output,canon(env)+"\n"); return
    if a.cmd=="measure":
        lo,hi=map(int,a.seeds.split(":")); seeds=list(range(lo,hi+1)); panel=a.panel if a.phase=="calibration" else None
        if a.phase=="calibration" and (panel not in PANELS or seeds!=PANELS[panel]): raise ValueError("calibration preregistration mismatch")
        if a.phase=="confirmation" and (a.panel is not None or seeds!=CONFIRM): raise ValueError("confirmation preregistration mismatch")
        prior=rows(a.output) if Path(a.output).exists() else []
        for name in SCENARIOS:
            for seed in seeds:
                if any(r["scenario"]==name and r["seed"]==seed and r.get("panel")==panel for r in prior): raise RuntimeError("duplicate forbidden")
                r=measure(name,seed,a.phase,panel); append(a.output,r); prior.append(r)
        return
    if a.cmd=="derive": new(a.output,canon(derive(rows(a.input),a.panel))+"\n"); return
    snaps=[json.loads(Path(x).read_text()) for x in a.snapshots]; new(a.output,canon(confirm(snaps,rows(a.input)))+"\n")
if __name__=="__main__": main()
