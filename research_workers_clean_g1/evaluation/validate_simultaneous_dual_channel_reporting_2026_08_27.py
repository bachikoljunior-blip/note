"""Synthetic contract-validation stress for simultaneous_dual_channel_reporting_v1.

This intentionally uses a self-contained conservative weighted Hoeffding family rather
than the role's production V3 water-filling CS. The purpose is to validate contract
wiring, alpha monotonicity, stop ordering, and replay identity. The resulting stopping
numbers are NOT performance estimates for V3 or for a deployment.
"""
from __future__ import annotations
import json
from math import log, pi, sqrt
import random
from statistics import mean, median
from typing import Any
from simultaneous_dual_channel_reporting_v1_2026_08_27 import DualChannelReportingContract, SimultaneousDualChannelReporter

class WeightedHoeffdingValidationStream:
    def __init__(self, alpha: float, lam: float = 0.36) -> None:
        self.alpha=float(alpha); self.lam=float(lam); self.t=0; self.w_sum=0.0; self.wy_sum=0.0; self.w2_sum=0.0
    def append(self, weight: float, score: float) -> None:
        w=float(weight); y=float(score); self.t+=1; self.w_sum+=w; self.wy_sum+=w*y; self.w2_sum+=w*w
    def log_e(self, mu0: float) -> float:
        return self.lam*(float(mu0)*self.w_sum-self.wy_sum)-(self.lam**2)*self.w2_sum/8.0
    def upper_endpoint(self) -> float:
        if self.w_sum<=0: return 1.0
        alpha_t=self.alpha*6.0/(pi*pi*self.t*self.t)
        radius=sqrt(self.w2_sum*log(1.0/alpha_t)/(2.0*self.w_sum*self.w_sum))
        return min(1.0,self.wy_sum/self.w_sum+radius)

def quantile(values: list[float], q: float) -> float:
    x=sorted(values); pos=(len(x)-1)*q; lo=int(pos); hi=min(lo+1,len(x)-1); f=pos-lo
    return x[lo]*(1.0-f)+x[hi]*f

def run_validation(runs: int=500, horizon: int=2000) -> dict[str,Any]:
    contract=DualChannelReportingContract(alpha_decision=.05,alpha_joint_report=.05,alpha_report_equal=.025,alpha_report_exposure=.025,tau_equal=.10,tau_exposure=.10)
    factory=lambda alpha: WeightedHoeffdingValidationStream(alpha)
    dt=[]; mt=[]; rt=[]; delays=[]; we=[]; wx=[]
    mono=early=decision_mismatch=replay_mismatch=digest_mismatch=0
    for seed in range(runs):
        rng=random.Random(seed); reporter=SimultaneousDualChannelReporter(factory,contract); rows=[]; td=tm=tr=None; recorded=False
        for t in range(1,horizon+1):
            y=1.0 if rng.random()<.01 else 0.0; w=(1.0,.75,.50,.875)[(t-1)%4]
            row={"block_id":f"{seed}:{t}","planned_size":int(round(w*8)),"completed_canonical":int(round(w*8)),"missing_or_failed":0,"block_score":y,"exposure_weight":w}
            rows.append(row); reporter.append_closed_row(row); s=reporter.snapshot(); d=s["decision_contract"]; m=s["marginal_numeric_bounds"]; r=s["simultaneous_reporting_contract"]
            direct=bool(d["equal_log_e"]>=d["log_e_threshold_per_channel"] and d["exposure_log_e"]>=d["log_e_threshold_per_channel"])
            if direct!=d["joint_safe_decision"]: decision_mismatch+=1
            if r["equal_upper"]+1e-12<m["equal_upper"] or r["exposure_upper"]+1e-12<m["exposure_upper"]: mono+=1
            ms=bool(m["equal_upper"]<=contract.tau_equal and m["exposure_upper"]<=contract.tau_exposure); rs=bool(r["simultaneous_report_safe"])
            if rs and not ms: early+=1
            if td is None and d["joint_safe_decision"]: td=t
            if tm is None and ms:
                tm=t
                if not recorded: we.append(r["equal_upper_widening_vs_marginal"]); wx.append(r["exposure_upper_widening_vs_marginal"]); recorded=True
            if tr is None and rs: tr=t
        dt.append(td or horizon+1); mt.append(tm or horizon+1); rt.append(tr or horizon+1)
        if tm is not None and tr is not None: delays.append(tr-tm)
        replay=SimultaneousDualChannelReporter.replay(factory,rows,contract)
        if replay.rows_digest()!=reporter.rows_digest(): digest_mismatch+=1
        if replay.snapshot()!=reporter.snapshot(): replay_mismatch+=1
    def stop(xs):
        return {"median":median(xs),"p90":quantile([float(v) for v in xs],.90),"p95":quantile([float(v) for v in xs],.95),"mean":mean(xs),"unresolved_fraction_at_horizon":sum(v==horizon+1 for v in xs)/len(xs)}
    return {"schema_version":1,"validation_kind":"synthetic_contract_validation_not_production_v3_performance","runs":runs,"horizon":horizon,"true_score_probability":.01,"predictable_exposure_weight_pattern":[1.0,.75,.50,.875],"contract":{"decision_alpha_each":.05,"joint_reporting_alpha":.05,"reporting_alpha_equal":.025,"reporting_alpha_exposure":.025,"tolerance_each":.10},"stopping":{"decision_iut":stop(dt),"marginal_numeric_alpha_0_05_each":stop(mt),"simultaneous_numeric_bonferroni_0_025_each":stop(rt),"report_minus_marginal_delay":{"median":median(delays),"p90":quantile([float(v) for v in delays],.90),"p95":quantile([float(v) for v in delays],.95),"mean":mean(delays)}},"bound_widening_at_first_marginal_safe_prefix":{"equal_mean":mean(we),"equal_p95":quantile(we,.95),"exposure_mean":mean(wx),"exposure_p95":quantile(wx,.95)},"invariants":{"alpha_monotonicity_violations":mono,"simultaneous_report_earlier_than_marginal_violations":early,"decision_formula_mismatches":decision_mismatch,"replay_snapshot_mismatches":replay_mismatch,"rows_digest_mismatches":digest_mismatch},"scope":["Validation CS is conservative union-over-time weighted Hoeffding, not production V3 water-filling CS.","Fixed-lambda decision e-process here tests a stronger pointwise conditional-mean null; stopping time is wiring stress only.","Numerical stopping-time results are synthetic and not deployment/V3 performance.","Joint reporting coverage uses union bound only; no channel independence is assumed."]}
if __name__=="__main__": print(json.dumps(run_validation(),indent=2,sort_keys=True))
