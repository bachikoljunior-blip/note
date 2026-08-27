"""Held-out comparison of precommitted joint-report alpha allocations for V3.

This script does NOT adapt alpha on the evaluated reliability history. A fixed grid is
predeclared; campaigns 0..19 are independent meta-data used to choose one allocation
by mean joint reporting time, and campaigns 20..59 are held out for evaluation.
Every allocation satisfies alpha_equal + alpha_exposure = .05.
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
        raise ImportError(f"cannot load {path}")
    mod = module_from_spec(spec)
    sys.modules[module_name] = mod
    spec.loader.exec_module(mod)
    return mod


_ADAPTER = _load_sibling("v3_simultaneous_reporting_adapter_2026-08-27.py", "_evaluation_v3_alpha_adapter")
_JOURNAL = _load_sibling("atomic_dual_channel_journal_2026-08-27T2107_JST.py", "_evaluation_atomic_journal_alpha")


def _quantile(xs: list[float], p: float) -> float:
    ys = sorted(float(x) for x in xs)
    x = (len(ys) - 1) * p
    i = int(x)
    f = x - i
    return ys[i] if i == len(ys) - 1 else ys[i] * (1.0 - f) + ys[i + 1] * f


def _campaign_series(seed: int, campaign: int, horizon: int = 600) -> list[tuple[float, float]]:
    rng = random.Random(seed + campaign * 100003)
    equal = _ADAPTER.production_v3_stream_factory(0.05)
    exposure = _ADAPTER.production_v3_stream_factory(0.05)
    journal = _JOURNAL.AtomicDualChannelJournal()
    b_cap = 16
    B = 8
    series: list[tuple[float, float]] = []
    tau = 0.05
    for j in range(1, horizon + 1):
        block_id = f"c{campaign:03d}-b{j:04d}"
        slots = [f"s{k:02d}" for k in range(B)]
        t0 = campaign * 1_000_000.0 + j * 10.0
        admit = journal.admit_event(block_id, slots, t0, t0 + 1.0, b_cap)
        journal.apply(admit)
        for sid in slots:
            if rng.random() < 0.002:
                continue
            score = 1.0 if rng.random() < 0.01 else 0.0
            journal.apply(journal.slot_event(block_id, sid, score, t0 + 0.5))
        journal.apply(journal.close_event(block_id, t0 + 1.1))
        row = journal.closed_rows[-1]
        equal.append(1.0, row["block_score"])
        exposure.append(row["exposure_weight"], row["block_score"])
        series.append((equal.log_e(tau), exposure.log_e(tau)))
        B = 16 if row["block_score"] < 0.05 else 4
    return series


def _stops(series: list[tuple[float, float]], alpha_equal: float, alpha_exposure: float) -> tuple[int, int, int]:
    te = log(1.0 / alpha_equal)
    tx = log(1.0 / alpha_exposure)
    se = sx = None
    for j, (le, lx) in enumerate(series, 1):
        if se is None and le >= te:
            se = j
        if sx is None and lx >= tx:
            sx = j
        if se is not None and sx is not None:
            return se, sx, max(se, sx)
    n = len(series)
    return se or n, sx or n, n


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    seed = 20260827
    grid = [(0.005, 0.045), (0.01, 0.04), (0.015, 0.035), (0.02, 0.03), (0.025, 0.025), (0.03, 0.02), (0.035, 0.015), (0.04, 0.01), (0.045, 0.005)]
    series = [_campaign_series(seed, c) for c in range(60)]
    table = []
    for ae, ax in grid:
        meta = [_stops(series[i], ae, ax) for i in range(20)]
        hold = [_stops(series[i], ae, ax) for i in range(20, 60)]
        table.append({
            "alpha_equal": ae,
            "alpha_exposure": ax,
            "meta_joint_mean": statistics.mean(x[2] for x in meta),
            "meta_joint_median": _quantile([x[2] for x in meta], 0.5),
            "meta_joint_p95": _quantile([x[2] for x in meta], 0.95),
            "heldout_joint_mean": statistics.mean(x[2] for x in hold),
            "heldout_joint_median": _quantile([x[2] for x in hold], 0.5),
            "heldout_joint_p95": _quantile([x[2] for x in hold], 0.95),
            "heldout_equal_mean": statistics.mean(x[0] for x in hold),
            "heldout_exposure_mean": statistics.mean(x[1] for x in hold),
        })
    selected = min(table, key=lambda r: r["meta_joint_mean"])
    equal = next(r for r in table if r["alpha_equal"] == 0.025)
    out = {
        "schema_version": 1,
        "seed": seed,
        "predeclared_grid": grid,
        "meta_campaigns": [0, 19],
        "heldout_campaigns": [20, 59],
        "selection_objective": "minimum mean joint reporting-safe prefix on independent meta campaigns",
        "table": table,
        "selected": selected,
        "equal_split_baseline": equal,
        "heldout_selected_minus_equal": {
            "joint_mean": selected["heldout_joint_mean"] - equal["heldout_joint_mean"],
            "joint_median": selected["heldout_joint_median"] - equal["heldout_joint_median"],
            "joint_p95": selected["heldout_joint_p95"] - equal["heldout_joint_p95"],
        },
        "scope_guard": "Synthetic held-out allocation stress. Selection used disjoint meta campaigns; do not retune alpha from the same live reliability history without a separately valid construction.",
    }
    text = json.dumps(out, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(text, encoding="utf-8")
    else:
        print(text, end="")


if __name__ == "__main__":
    main()
