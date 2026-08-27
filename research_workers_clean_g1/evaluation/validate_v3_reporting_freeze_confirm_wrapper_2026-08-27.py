"""Validate the exact V3 pilot-freeze-fresh-confirm wrapper in a checked-out repo.

This script imports persisted production V3 adapter/wrapper files. It verifies that the
pilot prefix is used only for allocation selection, never for the fresh certificate,
and compares stopping times against fixed and nine-pair simultaneously insured reports.
"""
from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import asdict
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


_A = _load("v3_simultaneous_reporting_adapter_2026-08-27.py", "_evaluation_fc_adapter")
_F = _load("v3_reporting_freeze_confirm_wrapper_2026-08-27.py", "_evaluation_fc_wrapper")


def _row(rng: random.Random, campaign: int, j: int, B: int, bcap: int = 128) -> dict[str, Any]:
    vals=[]; completed=0
    for _ in range(B):
        if rng.random() < .002:
            vals.append(1.0)  # fail-closed missing/canonical failure
        else:
            completed += 1
            vals.append(1.0 if rng.random() < .008 else 0.0)
    return {
        "block_id": f"c{campaign:03d}-b{j:04d}",
        "planned_size": B,
        "completed_canonical": completed,
        "missing_or_failed": B-completed,
        "block_score": sum(vals)/B,
        "exposure_weight": B/bcap,
    }


def _campaign(c: int, blocks: int = 600) -> list[dict[str, Any]]:
    rng=random.Random(8272333+c*104729)
    rows=[]; B=32
    for j in range(1,blocks+1):
        r=_row(rng,c,j,B); rows.append(r)
        # Predictable next size: current CLOSED row only affects future block size.
        if r["block_score"] == 0:
            B = 128 if B <= 32 else 32
        elif r["block_score"] < .03:
            B = 64
        else:
            B = 128
    return rows


def _fixed_stop(rows: list[dict[str,Any]], ae: float, ax: float, mu: float=.05) -> int | None:
    se=_A.production_v3_stream_factory(ae); sx=_A.production_v3_stream_factory(ax)
    for i,r in enumerate(rows,1):
        se.append(1.0,r["block_score"]); sx.append(r["exposure_weight"],r["block_score"])
        if se.log_e(mu)>=log(1/ae) and sx.log_e(mu)>=log(1/ax): return i
    return None


def _insured_stop(rows: list[dict[str,Any]], mu: float=.05) -> int | None:
    K=len(_F.DEFAULT_GRID); pairs=[]
    for ae,ax in _F.DEFAULT_GRID:
        pairs.append((_A.production_v3_stream_factory(ae/K),_A.production_v3_stream_factory(ax/K),ae/K,ax/K))
    for i,r in enumerate(rows,1):
        for se,sx,_,_ in pairs:
            se.append(1.0,r["block_score"]); sx.append(r["exposure_weight"],r["block_score"])
        for se,sx,ae,ax in pairs:
            if se.log_e(mu)>=log(1/ae) and sx.log_e(mu)>=log(1/ax): return i
    return None


def main() -> None:
    ap=argparse.ArgumentParser(); ap.add_argument("--output",type=Path); args=ap.parse_args()
    campaigns=60; pilots=(20,40,80,120); max_blocks=600
    fixed=[]; balanced=[]; insured=[]; by_pilot={p:[] for p in pilots}; selections={p:Counter() for p in pilots}
    replay_checks=0; tamper_rejections=0; max_log_e_diff=0.0; max_ub_diff=0.0
    for c in range(campaigns):
        rows=_campaign(c,max_blocks)
        fixed.append(_fixed_stop(rows,.02,.03)); balanced.append(_fixed_stop(rows,.025,.025)); insured.append(_insured_stop(rows))
        for p in pilots:
            frozen=_F.freeze_allocation(rows[:p]); frozen.assert_valid(); selections[p][frozen.grid_index]+=1
            stop=_F.first_fresh_resolution(rows,frozen); by_pilot[p].append(stop)
            rep=_F.replay_fresh(json.loads(json.dumps(rows,separators=(",",":"))),frozen)
            if rep.postpilot_rows != len(rows)-p: raise AssertionError("pilot row leaked into fresh reporter")
            live=_F.FreshConfirmReporter(frozen)
            for r in rows[p:]: live.append(r)
            ls,rs=live.snapshot(),rep.snapshot()
            max_log_e_diff=max(max_log_e_diff,abs(ls.get("log_e_equal",0)-rs.get("log_e_equal",0)),abs(ls.get("log_e_exposure",0)-rs.get("log_e_exposure",0)))
            max_ub_diff=max(max_ub_diff,abs(ls["upper_equal"]-rs["upper_equal"]),abs(ls["upper_exposure"]-rs["upper_exposure"]))
            replay_checks+=1
            bad=json.loads(json.dumps(rows)); bad[p//2]["block_score"]=min(1.0,bad[p//2]["block_score"]+.125)
            try:
                _F.replay_fresh(bad,frozen)
            except ValueError:
                tamper_rejections+=1
            else:
                raise AssertionError("tampered pilot prefix was accepted")

    def stats(xs):
        resolved=[x for x in xs if x is not None]
        return {"resolved":len(resolved),"unresolved":len(xs)-len(resolved),"mean":statistics.mean(resolved) if resolved else None,"median":statistics.median(resolved) if resolved else None,"p95":sorted(resolved)[min(len(resolved)-1,int(.95*len(resolved)))] if resolved else None,"max":max(resolved) if resolved else None}

    out={
        "schema_version":1,"campaigns":campaigns,"max_blocks":max_blocks,"pilots":list(pilots),
        "fixed_0_02_0_03":stats(fixed),"fixed_0_025_0_025":stats(balanced),"uniform_9_pair_insured":stats(insured),
        "fresh_confirm":{str(p):stats(by_pilot[p]) for p in pilots},
        "selected_grid_counts":{str(p):dict(sorted(selections[p].items())) for p in pilots},
        "replay_checks":replay_checks,"tamper_rejections":tamper_rejections,
        "max_replay_log_e_diff":max_log_e_diff,"max_replay_endpoint_diff":max_ub_diff,
        "contract":"Pilot rows select/freeze alpha only. Fresh V3 streams start empty after the frozen pilot digest. All baselines and fresh reporter use the exact persisted V3 adapter.",
        "scope_guard":"Synthetic campaign family only; stopping times are not production predictions. Checked-out execution of this persisted validator is required before treating the numeric output as repository-exact evidence."
    }
    text=json.dumps(out,indent=2,sort_keys=True)+"\n"; (args.output.write_text(text,encoding="utf-8") if args.output else print(text,end=""))


if __name__=="__main__": main()
