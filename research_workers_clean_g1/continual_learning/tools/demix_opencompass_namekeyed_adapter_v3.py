#!/usr/bin/env python3
"""Mode-guarded DeMix/OpenCompass score adapter.

This reconstruction wrapper builds on v2 (which adds OpenCompass's standard
`openai_humaneval` alias) and additionally checks the exact evaluation mode
emitted by OpenCompass DefaultSummarizer for the standard dataset configs used
by the 0.5.1.post1 and 0.5.2 `base_medium` collection.

It remains fail-closed and does not claim that the DeMix authors used either
reconstruction anchor.  In particular, metric ambiguity (notably HumanEval)
is still handled by the v1 core contract and requires an explicit metric
selection when multiple metrics are present.
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

import demix_opencompass_namekeyed_adapter_v2  # noqa: F401; installs verified alias
import demix_opencompass_namekeyed_adapter_v1 as core

# Source-verified from the exact standard configs imported by base_medium at
# OpenCompass 0.5.1.post1 and 0.5.2, combined with DefaultSummarizer's mapping:
# GenInferencer -> gen, PPLInferencer -> ppl, LLInferencer -> ll.
EXPECTED_MODES = {
    "ARC-E": "ppl",
    "HellaSwag": "ppl",
    "PIQA": "ppl",
    "SIQA": "ppl",
    "WinoGrande": "ll",
    "MBPP": "gen",
    "HumanEval": "gen",
    "GSM8K": "gen",
    "MATH": "gen",
}

_ORIGINAL_EXTRACT = core.extract_demix_scores


def _extract_with_mode_guard(rows, metric_overrides):
    scores, ignored = _ORIGINAL_EXTRACT(rows, metric_overrides)
    for canonical, item in scores.items():
        expected = EXPECTED_MODES[canonical]
        observed = item.mode.strip().lower()
        if observed != expected:
            raise core.SummaryParseError(
                f"benchmark {canonical!r} has OpenCompass mode {item.mode!r}; "
                f"expected {expected!r} for the source-verified standard config"
            )
    return scores, ignored


# Reuse the v1 CLI/reporting while strengthening extraction.
core.extract_demix_scores = _extract_with_mode_guard


def _self_test() -> None:
    fixture = """dataset,version,metric,mode,modelA
ARC-e,v1,accuracy,ppl,70.0
hellaswag,v1,accuracy,ppl,80.0
piqa,v1,accuracy,ppl,75.0
siqa,v1,accuracy,ppl,60.0
winogrande,v1,accuracy,ll,65.0
mbpp,v1,score,gen,40.0
openai_humaneval,v1,humaneval_pass@1,gen,30.0
gsm8k,v1,accuracy,gen,50.0
math,v1,accuracy,gen,20.0
"""
    with tempfile.TemporaryDirectory() as td:
        path = Path(td) / "summary.csv"
        path.write_text(fixture, encoding="utf-8")
        _header, _model, rows = core.load_rows(path, None)
        scores, _ignored = core.extract_demix_scores(rows, {})
        assert scores["HumanEval"].source_dataset == "openai_humaneval"
        assert scores["WinoGrande"].mode == "ll"

        bad = fixture.replace("winogrande,v1,accuracy,ll,65.0", "winogrande,v1,accuracy,ppl,65.0")
        path.write_text(bad, encoding="utf-8")
        _header, _model, rows = core.load_rows(path, None)
        try:
            core.extract_demix_scores(rows, {})
        except core.SummaryParseError:
            pass
        else:
            raise AssertionError("wrong WinoGrande mode did not fail closed")


def main() -> int:
    if "--self-test" in sys.argv:
        _self_test()
        print("SELF_TEST_OK")
        return 0
    return core.main()


if __name__ == "__main__":
    raise SystemExit(main())
