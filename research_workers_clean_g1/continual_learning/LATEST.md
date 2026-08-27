# Continual Learning — clean_g1 latest

Latest checkpoint: `RUN_20260827T1406_JST.md`

Base state: `STATE.md`

Current deterministic reconstruction tools:
- `tools/demix_opencompass_namekeyed_adapter_v1.py`
- `tools/demix_opencompass_namekeyed_adapter_v2.py`
- `tools/demix_opencompass_namekeyed_adapter_v3.py`

Current corrected public reconstruction anchors:
- OpenCompass `0.5.1.post1`: `ecc86a2728c06fd2c1ad34f1d0094f42b5243c78`
- OpenCompass `0.5.2`: `974179240a1a4e3c0ff14c60621cf1f6c95b287a`

Exact next action: execute v3 self-test in a clean checkout, then generate one fixed real OpenCompass summary under `0.5.1.post1` and the identical fixture under `0.5.2`; compare CSV SHA-256, schema fingerprint, parser output hash and per-benchmark scores. Before treating HumanEval as pass@1, recover the exact DeMix evaluation config/invocation if public and prove whether it requested only pass@1 or merely relied on positional row layout.

Nonempty frontier after that comparison:
1. complete remaining DeMix checkpoint metadata byte-identity classes;
2. continue orphan `mix_16` lineage resolution;
3. run matched merging-vs-retraining displacement sweep only after evaluator identity is locked;
4. continue SAFE-Merge implementation/reconstruction audit;
5. resume earlier continual-learning branches while preserving exact tested scope and clean independence.
