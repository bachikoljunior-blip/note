"""Stress V3 under predictable past-dependent exposure weights spanning 1/256..1.

The next planned block size is a deterministic function of the prior CLOSED block and
prior planned size only. Current completion count/outcomes never alter the current
weight. Live and JSON-roundtripped immutable CLOSED rows are replayed at audited
prefixes and must reproduce e-values, endpoints and reporting-alpha monotonicity.
"""
from __future__ import annotations

import argparse
from importlib.util import module_from_spec, spec_from_file_location
import json
from math import log
from pathlib import Path
import random
import statistics
import sys
from typing import Any


def _load(filename: str, name: str) -> Any:
    p = Path(__file__).resolve().with_name(filename)
    s = spec_from_file_location(name, p)
    if s is None or s.loader is None: raise ImportError(p)
    m = module_from_spec(s); sys.modules[name] = m; s.loader.exec_module(m); return m

_A = _load("v3_simultaneous_reporting_adapter_2026-08-27.py", "_evaluation_extreme_v3")


def _replay(rows: list[dict[str,Any]], alpha: float, channel: str) -> Any:
    s = _A.production_v3_stream_factory(alpha)
    for r in rows:
        s.append(1.0 if channel == "process" else r["exposure_weight"], r["block_score"])
    return s


def main() -> None:
    ap=argparse.ArgumentParser(); ap.add_argument("--output",type=Path); args=ap.parse_args()
    campaigns=30; blocks=220; audited={1,17,53,109,167,220}; rows_out=[]
    max_e=max_ub=0.0; monotonicity_violations=0; audited_prefixes=0; decision_resolved=report_resolved=0; total_weights=[]
    min_weight=1.0; max_weight=0.0
    for c in range(campaigns):
        rng=random.Random(8272318+c*99173); B=1; b_cap=256; rows=[]
        live=[_A.production_v3_stream_factory(.05),_A.production_v3_stream_factory(.05),_A.production_v3_stream_factory(.025),_A.production_v3_stream_factory(.025)]
        first_dec=first_rep=None
        for j in range(1,blocks+1):
            vals=[]; completed=0
            for _ in range(B):
                if rng.random()<.002: vals.append(1.0)
                else:
                    completed+=1; vals.append(1.0 if rng.random()<.01 else 0.0)
            y=sum(vals)/B; w=B/b_cap
            row={"block_id":f"c{c:03d}-b{j:04d}","planned_size":B,"completed_canonical":completed,"missing_or_failed":B-completed,"block_score":y,"exposure_weight":w}
            rows.append(row); min_weight=min(min_weight,w); max_weight=max(max_weight,w)
            for s,ww in ((live[0],1.0),(live[1],w),(live[2],1.0),(live[3],w)): s.append(ww,y)
            le,lx,lr,lrx=(live[0].log_e(.05),live[1].log_e(.05),live[2].log_e(.05),live[3].log_e(.05))
            if first_dec is None and le>=log(20) and lx>=log(20): first_dec=j
            if first_rep is None and lr>=log(40) and lrx>=log(40): first_rep=j
            if j in audited:
                rr=json.loads(json.dumps(rows,separators=(",",":")))
                rp=_replay(rr,.05,"process"); rx=_replay(rr,.05,"exposure"); rrp=_replay(rr,.025,"process"); rrx=_replay(rr,.025,"exposure")
                max_e=max(max_e,abs(rp.log_e(.05)-le),abs(rx.log_e(.05)-lx),abs(rrp.log_e(.05)-lr),abs(rrx.log_e(.05)-lrx))
                live_ub=[s.upper_endpoint() for s in live]; replay_ub=[rp.upper_endpoint(),rx.upper_endpoint(),rrp.upper_endpoint(),rrx.upper_endpoint()]
                max_ub=max(max_ub,max(abs(a-b) for a,b in zip(live_ub,replay_ub)))
                if live_ub[2]+1e-12<live_ub[0] or live_ub[3]+1e-12<live_ub[1]: monotonicity_violations+=1
                audited_prefixes+=1
            # next B is predictable: only prior CLOSED score and prior B are used
            if y < .05: B=256 if B==1 else 1
            else: B=4 if B>4 else 128
        decision_resolved += first_dec is not None; report_resolved += first_rep is not None; total_weights.append(sum(r["exposure_weight"] for r in rows))
    out={"schema_version":1,"campaigns":campaigns,"blocks_per_campaign":blocks,"audited_prefixes":audited_prefixes,"b_cap":256,"min_exposure_weight":min_weight,"max_exposure_weight":max_weight,"mean_total_exposure_weight":statistics.mean(total_weights),"min_total_exposure_weight":min(total_weights),"max_total_exposure_weight":max(total_weights),"decision_resolved_by_220":decision_resolved,"reporting_resolved_by_220":report_resolved,"max_replay_log_e_diff":max_e,"max_replay_endpoint_diff":max_ub,"reporting_alpha_monotonicity_violations":monotonicity_violations,"predictable_rule":"if prior CLOSED score < .05, next B=256 when prior B=1 else B=1; otherwise next B=4 when prior B>4 else B=128","scope_guard":"Synthetic numerical/replay stress. Non-resolution by 220 is not a claim of invalidity; it is evidence that extreme predictable weighting can make effective information and estimand behavior materially different."}
    text=json.dumps(out,indent=2,sort_keys=True)+"\n"; (args.output.write_text(text,encoding="utf-8") if args.output else print(text,end=""))

if __name__=="__main__": main()
