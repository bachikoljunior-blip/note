# Continual Learning — clean_g1 latest

Latest checkpoint: `RUN_20260827T1801_JST.md`

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

Current key refinement: the direct runtime dependency delta is localized to `pyext` removal and `pandas<2.0.0 -> pandas`. Track A must keep both dependency dimensions identical: use one Python 3.10 lock, pin the same `pandas<2` build and keep `pyext==0.7` present on both source anchors. The DeMix nine benchmark modules inspected at the 0.5.1 anchor do not directly import pandas, DefaultSummarizer writes CSV without pandas, and the role-local v3 score adapter uses stdlib `csv`; therefore any pandas sensitivity should be localized rather than assumed. For package-native Track B on fresh Python 3.10, public release constraints predict pandas 1.5.3 for 0.5.1 versus 2.3.3 for 0.5.2, but this remains a prediction until resolver locks are actually captured.

Exact next action: construct and hash the shared Track A environment, run the identical real nine-benchmark fixture under both anchors, and persist raw inference/result hashes, summary CSV/schema/hash, v3 parser output/hash and score deltas. Then resolve Track B in separate clean package-native environments, freeze the locks before evaluation, and confirm or reject the predicted pandas split. HumanEval `humaneval_pass@1` remains an explicit reconstruction choice unless a public DeMix execution artifact proves author intent.

Nonempty frontier after the paired environment test:
1. complete remaining DeMix checkpoint metadata byte-identity classes;
2. continue orphan `mix_16` lineage resolution;
3. run matched merging-vs-retraining displacement sweep only after evaluator identity and environment sensitivity are locked;
4. continue SAFE-Merge implementation/reconstruction audit;
5. resume earlier continual-learning branches while preserving exact tested scope and clean independence.
