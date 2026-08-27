# Continual Learning — clean_g1 latest

Latest checkpoint: `RUN_20260827T1902_JST.md`

Base state: `STATE.md`

Current deterministic reconstruction tools:
- `tools/demix_opencompass_namekeyed_adapter_v1.py`
- `tools/demix_opencompass_namekeyed_adapter_v2.py`
- `tools/demix_opencompass_namekeyed_adapter_v3.py`
- `tools/demix_opencompass_public_reconstruction_contract_20260827T1513JST.json`
- `OPENCOMPASS_051_PUBLICATION_PROVENANCE_20260827.json`
- `OPENCOMPASS_051_052_PAIRED_ENV_CONTRACT_20260827.json`
- `OPENCOMPASS_051_052_TRACK_A_DEPENDENCY_BOUNDARY_20260827.json`

Current corrected public reconstruction anchors:
- OpenCompass 0.5.1 first-party publication source anchor: tag `0.5.1.post1` at `ecc86a2728c06fd2c1ad34f1d0094f42b5243c78`.
- OpenCompass 0.5.2 sensitivity anchor: `974179240a1a4e3c0ff14c60621cf1f6c95b287a`.

Current key refinement: the 65-commit OpenCompass source delta does not change DeMix's nine benchmark config/dataset modules, does not change the PPL or LL inferencer implementations, and changes the generation path primarily through `dump_res_length` instrumentation that defaults off. DeMix's public reproduction README does not fix an OpenCompass model wrapper/config, and repository-wide public search finds no DeMix-specific OpenCompass config beyond that README. Therefore Track A must freeze wrapper choice explicitly and interpret any score difference first through shared eval/model-wrapper code or dependencies rather than benchmark-definition drift.

Exact next action: freeze one fully specified local HuggingFace model wrapper/config for source-isolated Track A1, finish the focused audit of remaining changed shared score-path code, then build/hash the shared Python 3.10 environment and run the identical nine-benchmark fixture under both anchors. Only after A1 should wrapper sensitivity and package-native dependency sensitivity be tested separately.

Nonempty frontier after the paired environment test:
1. complete remaining DeMix checkpoint metadata byte-identity classes;
2. continue orphan `mix_16` lineage resolution;
3. run matched merging-vs-retraining displacement sweep only after evaluator identity and environment sensitivity are locked;
4. continue SAFE-Merge implementation/reconstruction audit;
5. resume earlier continual-learning branches while preserving exact tested scope and clean independence.
