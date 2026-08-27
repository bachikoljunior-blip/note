#!/usr/bin/env python3
"""OpenCompass-0.5.1-compatible alias patch for the DeMix score adapter.

Version 1 intentionally keyed DeMix benchmarks by dataset+metric names, but its
HumanEval alias set omitted OpenCompass's standard dataset abbreviation
`openai_humaneval`.  This wrapper keeps the v1 fail-closed parser contract and
adds only source-verified aliases.  It is a reconstruction utility; it does not
claim that the DeMix authors used a specific OpenCompass release/config.
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

import demix_opencompass_namekeyed_adapter_v1 as core

OFFICIAL_OPENCOMPASS_ALIASES = {
    "openai_humaneval": "HumanEval",
}

for alias, canonical in OFFICIAL_OPENCOMPASS_ALIASES.items():
    key = core._norm(alias)
    previous = core.ALIAS_MAP.get(key)
    if previous is not None and previous != canonical:
        raise RuntimeError(
            f"OpenCompass alias collision for {alias!r}: {previous!r} vs {canonical!r}"
        )
    core.ALIAS_MAP[key] = canonical


def _compatibility_self_test() -> None:
    core._self_test()
    fixture = """dataset,version,metric,mode,modelA
ARC-e,v1,accuracy,ppl,70.0
hellaswag,v1,accuracy,ppl,80.0
piqa,v1,accuracy,ppl,75.0
siqa,v1,accuracy,ppl,60.0
winogrande,v1,accuracy,ppl,65.0
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
        assert scores["HumanEval"].score == 30.0


def main() -> int:
    if "--self-test" in sys.argv:
        _compatibility_self_test()
        print("SELF_TEST_OK")
        return 0
    return core.main()


if __name__ == "__main__":
    raise SystemExit(main())
