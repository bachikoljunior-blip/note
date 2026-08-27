#!/usr/bin/env python3
"""Locate token divergence relative to an exact score-certificate boundary.

Input is JSONL emitted by decision_stat_mismatch_microbenchmark.py collect.
The analyzer never treats token mismatch as score/sign mismatch by proxy: it reports
where divergence first occurs, whether it is before/after the canonical score
certificate, then separately compares deterministic scores and paired oriented sign.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from typing import Any


def load(path: str) -> list[dict[str, Any]]:
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            obj = json.loads(line)
            if obj.get("record_type") == "sample":
                rows.append(obj)
    return rows


def index(rows: list[dict[str, Any]]) -> dict[tuple[str, str, int], dict[str, Any]]:
    out = {}
    for r in rows:
        key = (str(r["case_id"]), str(r["side"]), int(r["repeat"]))
        if key in out:
            raise ValueError(f"duplicate key: {key}")
        out[key] = r
    return out


def first_diff(a: list[int], b: list[int]) -> int | None:
    """1-based first differing token position; append-point counts as divergence."""
    n = min(len(a), len(b))
    for i in range(n):
        if int(a[i]) != int(b[i]):
            return i + 1
    if len(a) != len(b):
        return n + 1
    return None


def bucket(diff_pos: int | None, cert_pos: int | None) -> str:
    if diff_pos is None:
        return "no_token_divergence"
    if cert_pos is None:
        return "divergence_certificate_missing"
    if diff_pos <= cert_pos:
        return "divergence_at_or_before_certificate"
    return "divergence_after_certificate"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--canonical", required=True)
    ap.add_argument("--fast", required=True)
    args = ap.parse_args()

    can = index(load(args.canonical))
    fast = index(load(args.fast))
    can_reps = sorted({k[2] for k in can})
    fast_reps = sorted({k[2] for k in fast})
    if not can_reps:
        raise SystemExit("canonical file has no sample records")
    cref = can_reps[0]

    side_counts = Counter()
    side_examples = defaultdict(list)
    pair_counts = Counter()

    case_ids = sorted({k[0] for k in fast})
    for rep in fast_reps:
        side_state: dict[str, tuple[dict[str, Any], dict[str, Any]]] = {}
        for case_id in case_ids:
            side_state.clear()
            complete_pair = True
            for side in ("candidate", "incumbent"):
                ck = (case_id, side, cref)
                fk = (case_id, side, rep)
                if ck not in can or fk not in fast:
                    complete_pair = False
                    break
                c = can[ck]
                f = fast[fk]
                side_state[side] = (c, f)
                d = first_diff([int(x) for x in c["token_ids"]], [int(x) for x in f["token_ids"]])
                cert = c.get("certificate_token")
                cert_i = int(cert) if cert is not None else None
                b = bucket(d, cert_i)
                side_counts[b] += 1
                side_counts["total"] += 1
                if int(c["score"]) != int(f["score"]):
                    side_counts["score_changed"] += 1
                    side_counts[b + "__score_changed"] += 1
                if d is not None and len(side_examples[b]) < 8:
                    side_examples[b].append({
                        "case_id": case_id,
                        "side": side,
                        "fast_repeat": rep,
                        "first_diff_token": d,
                        "canonical_certificate_token": cert_i,
                        "canonical_score": int(c["score"]),
                        "fast_score": int(f["score"]),
                    })
            if not complete_pair:
                continue
            cc, cf = side_state["candidate"]
            ic, inf = side_state["incumbent"]
            zc = int(cc["score"]) - int(ic["score"])
            zf = int(cf["score"]) - int(inf["score"])
            pair_counts["total"] += 1
            if (int(cc["score"]), int(ic["score"])) != (int(cf["score"]), int(inf["score"])):
                pair_counts["score_pair_changed"] += 1
            if zc != zf:
                pair_counts["oriented_sign_changed"] += 1

    total = side_counts["total"]
    ptot = pair_counts["total"]
    result = {
        "schema_version": 1,
        "canonical_repeat": cref,
        "side_counts": dict(side_counts),
        "side_rates": {
            k: (v / total if total else None)
            for k, v in side_counts.items()
            if k != "total"
        },
        "pair_counts": dict(pair_counts),
        "pair_rates": {
            "score_pair_changed": pair_counts["score_pair_changed"] / ptot if ptot else None,
            "oriented_sign_changed": pair_counts["oriented_sign_changed"] / ptot if ptot else None,
        },
        "examples": dict(side_examples),
        "interpretation_guard": (
            "Divergence after a canonical first-match score certificate is decision-irrelevant only for the frozen scorer/policy. "
            "Interactive state, alternate parsers, timing-dependent inclusion, or other downstream observers require a wider protected transcript."
        ),
    }
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
