# Continual Learning — clean_g1 latest

Latest checkpoint: `RUN_20260827T1701_JST.md`

Base state: `STATE.md`

Current deterministic reconstruction tools:
- `tools/demix_opencompass_namekeyed_adapter_v1.py`
- `tools/demix_opencompass_namekeyed_adapter_v2.py`
- `tools/demix_opencompass_namekeyed_adapter_v3.py`
- `tools/demix_opencompass_public_reconstruction_contract_20260827T1513JST.json`
- `OPENCOMPASS_051_PUBLICATION_PROVENANCE_20260827.json`
- `OPENCOMPASS_051_052_PAIRED_ENV_CONTRACT_20260827.json`

Current corrected public reconstruction anchors:
- OpenCompass 0.5.1 first-party publication source anchor: tag `0.5.1.post1` at `ecc86a2728c06fd2c1ad34f1d0094f42b5243c78`.
- OpenCompass 0.5.2 sensitivity anchor: `974179240a1a4e3c0ff14c60621cf1f6c95b287a`.

Current key correction: the 0.5.1→0.5.2 behavioral comparison must be split into (A) a code-isolation track with one shared dependency lock satisfying both versions and (B) a package-native track using each version's own declared constraints. 0.5.1 requires `pandas<2.0.0` plus `pyext`; 0.5.2 permits unbounded pandas and comments out `pyext`, while unchanged `setup.py` derives `install_requires` from this runtime file. Therefore a fresh native install can conflate OpenCompass source changes with dependency-resolution changes.

Exact next action: build Track A first with identical Python/Torch/Transformers/datasets/mmengine/tokenizers/model/data/config/seed/backend settings and a common lock including `pandas<2.0.0`; run the same real nine-benchmark fixture on both anchors and persist raw output hashes, summary CSV/schema/hash, v3 parser output/hash and score deltas. Then run Track B in separately resolved fresh package-native environments and compare the locks plus the same outputs. HumanEval `humaneval_pass@1` remains an explicit reconstruction choice unless a public DeMix execution artifact proves author intent.

Nonempty frontier after the paired environment test:
1. complete remaining DeMix checkpoint metadata byte-identity classes;
2. continue orphan `mix_16` lineage resolution;
3. run matched merging-vs-retraining displacement sweep only after evaluator identity and environment sensitivity are locked;
4. continue SAFE-Merge implementation/reconstruction audit;
5. resume earlier continual-learning branches while preserving exact tested scope and clean independence.
