#!/usr/bin/env python3
"""
Fail-closed adapter for public repeated-inference summaries that report output
nondeterminism without publishing the full per-run outputs or frozen scorer
results.

The adapter deliberately separates three layers:
  1. raw/output divergence evidence (e.g. distinct_outputs > 1),
  2. a process/workload-level raw-divergence cluster score,
  3. protected decision-statistic / paired-sign divergence.

Layer (1) may be present in a summary artifact. Layer (2) can be constructed
retrospectively for descriptive process-level analysis when one record identifies
one process/workload cluster. Layer (3) remains UNKNOWN unless the source record
explicitly supplies a frozen protected statistic for every compared run. Token or
text divergence is never converted into score/sign divergence by proxy.

The emitted cluster records are marked retrospective and are NOT automatically
eligible for a prospective anytime certificate: a valid sequential certificate
requires the cluster definition, reveal order, tolerance, and score contract to
be fixed before outcomes are observed.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def load_json(path: str) -> dict[str, Any]:
    obj = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(obj, dict):
        raise ValueError("expected a top-level JSON object")
    return obj


def process_id(cell: dict[str, Any], idx: int) -> str:
    fields = [
        str(cell.get("model", "unknown-model")),
        str(cell.get("kernel_state", "unknown-kernel")),
        str(cell.get("process", f"cell-{idx}")),
        f"depth-{cell.get('depth', 'unknown')}",
    ]
    return "|".join(fields)


def adapt_gfx1100_summary(obj: dict[str, Any]) -> dict[str, Any]:
    within = obj.get("within_process")
    if not isinstance(within, dict) or not isinstance(within.get("cells"), list):
        raise ValueError("expected within_process.cells in gfx1100-style summary")

    clusters: list[dict[str, Any]] = []
    protected_unknown = 0
    raw_divergent = 0
    for i, cell in enumerate(within["cells"]):
        if not isinstance(cell, dict):
            raise ValueError(f"within_process.cells[{i}] is not an object")
        generations = int(cell.get("generations", 0))
        distinct = int(cell.get("distinct_outputs", 0))
        if generations <= 0 or distinct <= 0 or distinct > generations:
            raise ValueError(f"invalid generations/distinct_outputs in cell {i}")

        raw_any = int(distinct > 1)
        raw_divergent += raw_any
        protected_unknown += 1
        clusters.append({
            "cluster_id": process_id(cell, i),
            "score": raw_any,
            "cluster_size": generations,
            "score_contract": "any raw generated-output divergence within this warmed process cell",
            "raw_distinct_outputs": distinct,
            "first_divergence_vs_first_run": cell.get("first_divergence_vs_first_run"),
            "protected_statistic_status": "unknown",
            "paired_oriented_sign_status": "unknown",
            "retrospective": True,
            "prospective_certificate_eligible": False,
            "reason_not_certificate_eligible": (
                "This public summary was located after outcomes were reported; the "
                "cluster sequence and tolerance were not predeclared by this adapter."
            ),
            "fingerprint_fields": {
                "model": cell.get("model"),
                "kernel_state": cell.get("kernel_state"),
                "process": cell.get("process"),
                "depth": cell.get("depth"),
            },
        })

    return {
        "schema_version": 1,
        "source_kind": "gfx1100_greedy_nondeterminism_summary",
        "source_measurement": obj.get("what"),
        "source_method": obj.get("method"),
        "raw_output_divergence": {
            "process_cells": len(clusters),
            "cells_with_any_raw_divergence": raw_divergent,
            "fraction_cells_with_any_raw_divergence": raw_divergent / len(clusters) if clusters else None,
        },
        "protected_decision_statistic": {
            "status": "unknown",
            "unknown_cells": protected_unknown,
            "guard": (
                "Raw/token/text divergence is not a proxy for a frozen task score or paired oriented sign. "
                "A score/sign claim requires explicit source labels or the full outputs plus a frozen deterministic scorer."
            ),
        },
        "retrospective_cluster_records": {
            "estimand": "equal-process probability of any raw generated-output divergence under these reported cells",
            "clusters": clusters,
            "inference_guard": (
                "These records may be used for descriptive or separately justified retrospective analysis only. "
                "Do not feed them into a prospective anytime certificate as if reveal order/tolerance were predeclared."
            ),
        },
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument(
        "--format",
        choices=("gfx1100-summary",),
        default="gfx1100-summary",
    )
    args = ap.parse_args()

    obj = load_json(args.input)
    if args.format == "gfx1100-summary":
        out = adapt_gfx1100_summary(obj)
    else:
        raise AssertionError("unreachable")
    print(json.dumps(out, indent=2, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
