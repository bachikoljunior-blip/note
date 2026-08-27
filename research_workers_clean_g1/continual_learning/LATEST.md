# Continual Learning — clean_g1 latest

Latest checkpoint: `RUN_20260827T1513_JST.md`

Base state: `STATE.md`

Current deterministic reconstruction tools:
- `tools/demix_opencompass_namekeyed_adapter_v1.py`
- `tools/demix_opencompass_namekeyed_adapter_v2.py`
- `tools/demix_opencompass_namekeyed_adapter_v3.py`
- `tools/demix_opencompass_public_reconstruction_contract_20260827T1513JST.json`

Current corrected public reconstruction anchors:
- date-bounded OpenCompass 0.5.1 source reconstruction baseline: `0.5.1.post1@ecc86a2728c06fd2c1ad34f1d0094f42b5243c78` — public reconstruction only, not proof of the DeMix author environment or PyPI byte identity;
- OpenCompass `0.5.2` sensitivity anchor: `974179240a1a4e3c0ff14c60621cf1f6c95b287a`.

Exact next action: obtain the OpenCompass 0.5.1 PyPI wheel/sdist (or a trusted package file manifest) and compare its contents to `ecc86a...`; then generate one fixed real OpenCompass summary under the 0.5.1 reconstruction baseline and the identical fixture under 0.5.2, recording CSV SHA-256, schema fingerprint, parser-output SHA-256, dependencies and score deltas. HumanEval `humaneval_pass@1` remains an explicit reconstruction choice unless a public DeMix execution artifact proves the authors' metric.

Nonempty frontier after that comparison:
1. complete remaining DeMix checkpoint metadata byte-identity classes;
2. continue orphan `mix_16` lineage resolution;
3. run matched merging-vs-retraining displacement sweep only after evaluator identity is locked;
4. continue SAFE-Merge implementation/reconstruction audit;
5. resume earlier continual-learning branches while preserving exact tested scope and clean independence.
