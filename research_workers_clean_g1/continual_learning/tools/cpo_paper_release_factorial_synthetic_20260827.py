#!/usr/bin/env python3
"""Synthetic reconciliation for CPO paper-vs-release selection/normalization.

This is a role-local diagnostic. It does not claim training-quality equivalence.
It verifies that the two public formulations are mathematically distinct before
running expensive VLM experiments.
"""
from __future__ import annotations
import json
from dataclasses import dataclass
from typing import Dict, Literal
import torch

Selection = Literal["global", "per_tensor"]
Normalization = Literal["global", "per_tensor"]


def select_masks(movement: Dict[str, torch.Tensor], top_percent: float, mode: Selection):
    masks = {k: torch.zeros_like(v, dtype=torch.bool) for k, v in movement.items()}
    if mode == "per_tensor":
        for name, diff in movement.items():
            n = diff.numel()
            k = int(n * top_percent / 100.0)
            if k <= 0:
                continue
            vals, idx = torch.topk(diff.abs().reshape(-1), k, largest=True, sorted=False)
            idx = idx[vals > 0]
            masks[name].reshape(-1)[idx] = True
        return masks

    names = list(movement)
    flattened = [movement[n].abs().reshape(-1) for n in names]
    total = sum(x.numel() for x in flattened)
    k = int(total * top_percent / 100.0)
    if k <= 0:
        return masks
    all_diff = torch.cat(flattened)
    vals, global_idx = torch.topk(all_diff, k, largest=True, sorted=False)
    global_idx = global_idx[vals > 0]
    offsets = {}
    start = 0
    for name, flat in zip(names, flattened):
        offsets[name] = (start, start + flat.numel())
        start += flat.numel()
    for gi in global_idx.tolist():
        for name, (lo, hi) in offsets.items():
            if lo <= gi < hi:
                masks[name].reshape(-1)[gi - lo] = True
                break
    return masks


def masked_l1_loss(params, refs, masks, lam: float, normalization: Normalization):
    global_count = sum(int(m.sum()) for m in masks.values())
    loss = torch.zeros((), dtype=torch.float64)
    for name, p in params.items():
        idx = masks[name].reshape(-1).nonzero(as_tuple=True)[0]
        if idx.numel() == 0:
            continue
        denom = global_count if normalization == "global" else idx.numel()
        diff = p.reshape(-1)[idx] - refs[name].reshape(-1)[idx]
        loss = loss + lam / denom * diff.abs().sum()
    return loss


def run_case(name, movement, top_percent=10.0):
    params = {k: torch.ones_like(v, dtype=torch.float64, requires_grad=True) for k, v in movement.items()}
    refs = {k: torch.zeros_like(v, dtype=torch.float64) for k, v in movement.items()}
    rows = []
    for selection in ("global", "per_tensor"):
        masks = select_masks(movement, top_percent, selection)
        for normalization in ("global", "per_tensor"):
            for p in params.values():
                if p.grad is not None:
                    p.grad.zero_()
            loss = masked_l1_loss(params, refs, masks, 1.0, normalization)
            loss.backward()
            per_tensor = {}
            for k in params:
                g = params[k].grad
                if g is None:
                    g = torch.zeros_like(params[k])
                per_tensor[k] = {
                    "selected": int(masks[k].sum()),
                    "grad_l1": float(g.abs().sum()),
                    "max_abs_grad": float(g.abs().max()),
                }
            rows.append({
                "selection": selection,
                "normalization": normalization,
                "loss": float(loss),
                "total_grad_l1": sum(v["grad_l1"] for v in per_tensor.values()),
                "per_tensor": per_tensor,
            })
    return {"case": name, "top_percent": top_percent, "rows": rows}


def main():
    # Case 1 isolates selection topology: global TopP concentrates all support in
    # the high-movement large tensor; per-tensor TopP forces support everywhere.
    selection_case = {
        "small": torch.linspace(0.001, 0.010, 10, dtype=torch.float64),
        "medium": torch.linspace(0.001, 0.100, 100, dtype=torch.float64),
        "large": torch.linspace(0.001, 10.0, 1000, dtype=torch.float64),
    }

    # Case 2 isolates normalization topology: both selectors pick the same support
    # (1 of 10 + 9 of 90), while global-vs-per-tensor normalization differs.
    small = torch.zeros(10, dtype=torch.float64)
    large = torch.zeros(90, dtype=torch.float64)
    small[0] = 100.0
    large[:9] = torch.linspace(50.0, 42.0, 9, dtype=torch.float64)
    normalization_case = {"small": small, "large": large}

    out = {
        "schema_version": 1,
        "interpretation": {
            "paper_spec": "global TopP + global masked-L1 normalization",
            "release_code_spec": "per-tensor TopP + per-tensor masked-L1 normalization",
            "scope": "synthetic gradient/topology verification only; not a performance result",
        },
        "cases": [
            run_case("selection_topology", selection_case),
            run_case("normalization_topology", normalization_case),
        ],
    }

    # Hard assertions.
    c1 = out["cases"][0]["rows"]
    def row(rows, s, n):
        return next(r for r in rows if r["selection"] == s and r["normalization"] == n)

    r = row(c1, "global", "global")
    assert [r["per_tensor"][k]["selected"] for k in ("small", "medium", "large")] == [0, 0, 111]
    r = row(c1, "per_tensor", "global")
    assert [r["per_tensor"][k]["selected"] for k in ("small", "medium", "large")] == [1, 10, 100]

    c2 = out["cases"][1]["rows"]
    gg = row(c2, "global", "global")
    gp = row(c2, "global", "per_tensor")
    pg = row(c2, "per_tensor", "global")
    pp = row(c2, "per_tensor", "per_tensor")
    assert gg["per_tensor"]["small"]["selected"] == 1 and gg["per_tensor"]["large"]["selected"] == 9
    assert pg["per_tensor"]["small"]["selected"] == 1 and pg["per_tensor"]["large"]["selected"] == 9
    assert abs(gg["total_grad_l1"] - 1.0) < 1e-10
    assert abs(pg["total_grad_l1"] - 1.0) < 1e-10
    assert abs(gp["total_grad_l1"] - 2.0) < 1e-10
    assert abs(pp["total_grad_l1"] - 2.0) < 1e-10

    print(json.dumps(out, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
