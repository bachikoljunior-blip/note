#!/usr/bin/env python3
"""Deterministic, fail-closed parser for OpenCompass summary CSV files.

This utility is intentionally independent of OpenCompass internals. It consumes the
CSV format emitted by OpenCompass DefaultSummarizer (0.5.1.post1-compatible schema):

    dataset,version,metric,mode,<one or more model columns>

Unlike DeMix's released positional parser, it keys by dataset + metric names and
fails closed on ambiguous model columns, duplicate dataset/metric rows, missing
benchmarks, non-numeric scores, or unexpected duplicate aliases.

It does not claim to reproduce the DeMix authors' hidden environment. It is a
reconstruction adapter for deterministic score extraction once an exact OpenCompass
summary CSV has been produced.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Mapping, MutableMapping, Optional, Sequence, Tuple

SCHEMA_PREFIX = ("dataset", "version", "metric", "mode")

BENCHMARK_ALIASES: Mapping[str, Sequence[str]] = {
    "ARC-E": ("ARC-E", "ARC-e", "ARC_E", "ARC Easy", "ARC-Easy"),
    "HellaSwag": ("HellaSwag", "hellaswag", "hella_swag"),
    "PIQA": ("PIQA", "piqa"),
    "SIQA": ("SIQA", "siqa", "SocialIQA", "social_iqa"),
    "WinoGrande": ("WinoGrande", "winogrande", "wino_grande"),
    "MBPP": ("MBPP", "mbpp"),
    "HumanEval": ("HumanEval", "HUMANEVAL", "human_eval", "humaneval"),
    "GSM8K": ("GSM8K", "gsm8k", "gsm_8k"),
    "MATH": ("MATH", "math"),
}

CATEGORIES: Mapping[str, Sequence[str]] = {
    "general": ("ARC-E", "HellaSwag", "PIQA", "SIQA", "WinoGrande"),
    "code": ("MBPP", "HumanEval"),
    "math": ("GSM8K", "MATH"),
}


class SummaryParseError(ValueError):
    pass


def _norm(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", s.strip().lower())


@dataclass(frozen=True)
class Row:
    dataset: str
    version: str
    metric: str
    mode: str
    model: str
    score: float
    row_number: int


@dataclass(frozen=True)
class ExtractedScore:
    canonical_dataset: str
    source_dataset: str
    metric: str
    mode: str
    model: str
    score: float
    row_number: int


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def schema_fingerprint(header: Sequence[str]) -> str:
    material = json.dumps(list(header), ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(material.encode("utf-8")).hexdigest()


def parse_metric_overrides(items: Sequence[str]) -> Dict[str, str]:
    out: Dict[str, str] = {}
    for item in items:
        if "=" not in item:
            raise SummaryParseError(f"metric override must be DATASET=METRIC, got {item!r}")
        dataset, metric = item.split("=", 1)
        dataset, metric = dataset.strip(), metric.strip()
        if dataset not in BENCHMARK_ALIASES:
            raise SummaryParseError(
                f"unknown canonical dataset in metric override: {dataset!r}; "
                f"expected one of {sorted(BENCHMARK_ALIASES)}"
            )
        if not metric:
            raise SummaryParseError(f"empty metric for {dataset!r}")
        if dataset in out and out[dataset] != metric:
            raise SummaryParseError(f"conflicting metric overrides for {dataset!r}")
        out[dataset] = metric
    return out


def load_rows(path: Path, model_column: Optional[str]) -> Tuple[List[str], str, List[Row]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.reader(f)
        try:
            header = next(reader)
        except StopIteration as exc:
            raise SummaryParseError("summary CSV is empty") from exc

        header = [h.strip() for h in header]
        if tuple(header[:4]) != SCHEMA_PREFIX:
            raise SummaryParseError(
                f"unexpected OpenCompass CSV schema prefix {header[:4]!r}; expected {SCHEMA_PREFIX!r}"
            )
        model_columns = header[4:]
        if not model_columns:
            raise SummaryParseError("summary CSV has no model score columns")

        if model_column is None:
            if len(model_columns) != 1:
                raise SummaryParseError(
                    "multiple model columns present; pass --model-column explicitly: "
                    + ", ".join(model_columns)
                )
            selected_model = model_columns[0]
        else:
            if model_column not in model_columns:
                raise SummaryParseError(
                    f"requested model column {model_column!r} not found; available: {model_columns!r}"
                )
            selected_model = model_column

        model_idx = header.index(selected_model)
        rows: List[Row] = []
        for row_number, raw in enumerate(reader, start=2):
            if not raw or all(not cell.strip() for cell in raw):
                continue
            if len(raw) != len(header):
                raise SummaryParseError(
                    f"row {row_number} has {len(raw)} columns, expected {len(header)}"
                )
            dataset, version, metric, mode = (raw[i].strip() for i in range(4))
            score_text = raw[model_idx].strip()
            if score_text in {"", "-", "nan", "NaN", "NAN"}:
                continue
            try:
                score = float(score_text)
            except ValueError as exc:
                raise SummaryParseError(
                    f"non-numeric score at row {row_number}, model {selected_model!r}: {score_text!r}"
                ) from exc
            if not math.isfinite(score):
                raise SummaryParseError(
                    f"non-finite score at row {row_number}, model {selected_model!r}: {score_text!r}"
                )
            rows.append(
                Row(
                    dataset=dataset,
                    version=version,
                    metric=metric,
                    mode=mode,
                    model=selected_model,
                    score=score,
                    row_number=row_number,
                )
            )
    return header, selected_model, rows


def _canonical_alias_map() -> Dict[str, str]:
    out: Dict[str, str] = {}
    for canonical, aliases in BENCHMARK_ALIASES.items():
        for alias in (canonical, *aliases):
            key = _norm(alias)
            prev = out.get(key)
            if prev is not None and prev != canonical:
                raise RuntimeError(f"internal alias collision: {alias!r} -> {prev!r}/{canonical!r}")
            out[key] = canonical
    return out


ALIAS_MAP = _canonical_alias_map()


def extract_demix_scores(
    rows: Sequence[Row], metric_overrides: Mapping[str, str]
) -> Tuple[Dict[str, ExtractedScore], List[Dict[str, object]]]:
    by_canonical: MutableMapping[str, List[Row]] = {k: [] for k in BENCHMARK_ALIASES}
    ignored: List[Dict[str, object]] = []
    for row in rows:
        canonical = ALIAS_MAP.get(_norm(row.dataset))
        if canonical is None:
            ignored.append(
                {
                    "dataset": row.dataset,
                    "metric": row.metric,
                    "row_number": row.row_number,
                    "reason": "not a required DeMix benchmark alias",
                }
            )
            continue
        by_canonical[canonical].append(row)

    out: Dict[str, ExtractedScore] = {}
    for canonical in BENCHMARK_ALIASES:
        candidates = by_canonical[canonical]
        if not candidates:
            raise SummaryParseError(f"required benchmark {canonical!r} is missing")

        override = metric_overrides.get(canonical)
        if override is not None:
            filtered = [r for r in candidates if _norm(r.metric) == _norm(override)]
            if not filtered:
                available = sorted({r.metric for r in candidates})
                raise SummaryParseError(
                    f"metric override {canonical}={override!r} did not match; available metrics: {available}"
                )
            candidates = filtered

        metrics = sorted({_norm(r.metric) for r in candidates})
        if len(metrics) > 1:
            human = sorted({r.metric for r in candidates})
            raise SummaryParseError(
                f"benchmark {canonical!r} has multiple metrics {human}; pass --metric {canonical}=METRIC"
            )

        if len(candidates) != 1:
            details = [
                {
                    "dataset": r.dataset,
                    "metric": r.metric,
                    "version": r.version,
                    "mode": r.mode,
                    "row_number": r.row_number,
                }
                for r in candidates
            ]
            raise SummaryParseError(
                f"benchmark {canonical!r} is duplicated after alias/metric resolution: {details}"
            )

        r = candidates[0]
        out[canonical] = ExtractedScore(
            canonical_dataset=canonical,
            source_dataset=r.dataset,
            metric=r.metric,
            mode=r.mode,
            model=r.model,
            score=r.score,
            row_number=r.row_number,
        )
    return out, ignored


def build_report(
    path: Path,
    header: Sequence[str],
    model: str,
    scores: Mapping[str, ExtractedScore],
    ignored: Sequence[Mapping[str, object]],
    opencompass_commit: Optional[str],
) -> Dict[str, object]:
    categories: Dict[str, float] = {}
    for category, datasets in CATEGORIES.items():
        categories[f"{category}_avg"] = sum(scores[d].score for d in datasets) / len(datasets)

    return {
        "schema_version": 1,
        "source_csv": str(path),
        "source_csv_sha256": sha256_file(path),
        "opencompass_commit": opencompass_commit,
        "csv_header": list(header),
        "csv_schema_fingerprint_sha256": schema_fingerprint(header),
        "selected_model_column": model,
        "benchmarks": {
            k: {
                "source_dataset": v.source_dataset,
                "metric": v.metric,
                "mode": v.mode,
                "score": v.score,
                "row_number": v.row_number,
            }
            for k, v in scores.items()
        },
        "category_averages": categories,
        "ignored_rows": list(ignored),
        "parser_contract": {
            "dataset_keyed": True,
            "metric_keyed": True,
            "fails_on_missing_required_benchmark": True,
            "fails_on_duplicate_alias_or_metric": True,
            "fails_on_ambiguous_model_column": True,
            "positional_iloc_parser_used": False,
        },
    }


def _self_test() -> None:
    import tempfile

    good = """dataset,version,metric,mode,modelA
ARC-e,v1,accuracy,ppl,70.0
hellaswag,v1,accuracy,ppl,80.0
piqa,v1,accuracy,ppl,75.0
siqa,v1,accuracy,ppl,60.0
winogrande,v1,accuracy,ppl,65.0
MBPP,v1,score,gen,40.0
HUMANEVAL,v1,humaneval_pass@1,gen,30.0
GSM8K,v1,accuracy,gen,50.0
MATH,v1,accuracy,gen,20.0
extra,v1,accuracy,ppl,99.0
"""
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "summary.csv"
        p.write_text(good, encoding="utf-8")
        header, model, rows = load_rows(p, None)
        scores, ignored = extract_demix_scores(rows, {})
        report = build_report(p, header, model, scores, ignored, "test-commit")
        assert report["category_averages"]["general_avg"] == 70.0
        assert report["category_averages"]["code_avg"] == 35.0
        assert report["category_averages"]["math_avg"] == 35.0

        p.write_text(good + "ARC-E,v2,accuracy,ppl,71.0\n", encoding="utf-8")
        try:
            header, model, rows = load_rows(p, None)
            extract_demix_scores(rows, {})
        except SummaryParseError:
            pass
        else:
            raise AssertionError("duplicate benchmark did not fail closed")

        multi = """dataset,version,metric,mode,modelA,modelB
ARC-e,v1,accuracy,ppl,70.0,71.0
"""
        p.write_text(multi, encoding="utf-8")
        try:
            load_rows(p, None)
        except SummaryParseError:
            pass
        else:
            raise AssertionError("multi-model fixture did not fail closed")
        header, selected, rows = load_rows(p, "modelB")
        assert selected == "modelB" and rows[0].score == 71.0

        multi_metric = good.replace(
            "ARC-e,v1,accuracy,ppl,70.0\n",
            "ARC-e,v1,accuracy,ppl,70.0\nARC-e,v1,score,ppl,69.0\n",
        )
        p.write_text(multi_metric, encoding="utf-8")
        header, model, rows = load_rows(p, None)
        try:
            extract_demix_scores(rows, {})
        except SummaryParseError:
            pass
        else:
            raise AssertionError("multi-metric fixture did not fail closed")
        scores, _ignored = extract_demix_scores(rows, {"ARC-E": "accuracy"})
        assert scores["ARC-E"].score == 70.0


def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("summary_csv", nargs="?", type=Path)
    ap.add_argument("--model-column")
    ap.add_argument("--metric", action="append", default=[], metavar="DATASET=METRIC")
    ap.add_argument("--opencompass-commit")
    ap.add_argument("--output-json", type=Path)
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args(argv)

    try:
        if args.self_test:
            _self_test()
            print("SELF_TEST_OK")
            return 0
        if args.summary_csv is None:
            raise SummaryParseError("summary_csv is required unless --self-test is used")
        metric_overrides = parse_metric_overrides(args.metric)
        header, model, rows = load_rows(args.summary_csv, args.model_column)
        scores, ignored = extract_demix_scores(rows, metric_overrides)
        report = build_report(
            args.summary_csv,
            header,
            model,
            scores,
            ignored,
            args.opencompass_commit,
        )
        text = json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True) + "\n"
        if args.output_json:
            args.output_json.write_text(text, encoding="utf-8")
        else:
            sys.stdout.write(text)
        return 0
    except (OSError, SummaryParseError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
