"""Stress precommitted V3 simultaneous-report alpha allocations across regime shifts.

A fixed nine-point allocation grid is evaluated over predeclared synthetic regimes that
change score rate, missingness, and predictable exposure-weight pattern. This is meta-
evaluation only: it does not retune a live certificate from its own evidence.
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


def _load_sibling(filename: str, module_name: str) -> Any:
    path = Path(__file__).resolve().with_name(filename)
    spec = spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise ImportError(path)
    mod = module_from_spec(spec)
    sys.modules[module_name] = mod
    spec.loader.exec_module(mod)
    return mod


_A = _load_sibling("v3_simultaneous_reporting_adapter_2026-08-27.py", "_evaluation_robust_alpha_v3")

GRID = [(0.005,0.045),(0.01,0.04),(0.015,0.035),(0.02,0.03),(0.025,0.025),(0.03,0.02),(0.035,0.015),(0.04,0.01),(0.045,0.005)]
REGIMES = [(p, miss, rule) for p in (0.005,0.01,0.02) for miss in (0.0,0.002) for rule in ("adaptive","fixed8")]


def _series(seed: int, p: float, missing: float, rule: str, campaign: int, horizon: int = 600) -> list[tuple[float,float]]:
    salt = int(p*1e6)*1009 + int(missing*1e6)*9176 + campaign*100003 + (0 if rule == "adaptive" else 70000019)
    rng = random.Random(seed + salt)
    eq = _A.production_v3_stream_factory(0.05)
    ex = _A.production_v3_stream_factory(0.05)
    B = 8
    out = []
    for _ in range(horizon):
        vals = []
        for _ in range(B):
            if rng.random() < missing:
                vals.append(1.0)
            else:
                vals.append(1.0 if rng.random() < p else 0.0)
        y = sum(vals)/B
        eq.append(1.0, y)
        ex.append(B/16.0, y)
        out.append((eq.log_e(0.05), ex.log_e(0.05)))
        if rule == "adaptive":
            B = 16 if y < 0.05 else 4
        else:
            B = 8
    return out


def _stop(series: list[tuple[float,float]], ae: float, ax: float) -> int:
    te, tx = log(1.0/ae), log(1.0/ax)
    se = sx = None
    for j, (le,lx) in enumerate(series,1):
        if se is None and le >= te: se = j
        if sx is None and lx >= tx: sx = j
        if se is not None and sx is not None: return j
    return len(series)


def main() -> None:
    ap = argparse.ArgumentParser(); ap.add_argument("--output", type=Path); args = ap.parse_args()
    seed = 20260827
    rows = []
    for p, missing, rule in REGIMES:
        streams = [_series(seed,p,missing,rule,c) for c in range(10)]
        means = {f"{ae:.3f}/{ax:.3f}": statistics.mean(_stop(s,ae,ax) for s in streams) for ae,ax in GRID}
        rows.append({"p":p,"missing":missing,"rule":rule,"mean_joint_stop":means})
    summary = []
    for ae,ax in GRID:
        key=f"{ae:.3f}/{ax:.3f}"; vals=[r["mean_joint_stop"][key] for r in rows]
        summary.append({"alpha_equal":ae,"alpha_exposure":ax,"across_regime_mean":statistics.mean(vals),"worst_regime_mean":max(vals)})
    minimax=min(summary,key=lambda r:r["worst_regime_mean"])
    average=min(summary,key=lambda r:r["across_regime_mean"])
    out={"schema_version":1,"seed":seed,"campaigns_per_regime":10,"horizon":600,"grid":GRID,"regimes":rows,"summary":summary,"minimax":minimax,"best_across_regime_mean":average,"scope_guard":"Synthetic robustness stress only. Allocation must still be frozen before live evidence; no live-history retuning is licensed."}
    text=json.dumps(out,indent=2,sort_keys=True)+"\n"
    if args.output: args.output.write_text(text,encoding="utf-8")
    else: print(text,end="")

if __name__ == "__main__": main()
