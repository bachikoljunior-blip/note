# Continual Learning — clean_g1 latest

Latest checkpoint: `RUN_20260827T2013_JST.md`

Base state: `STATE.md`

Current deterministic reconstruction tools:
- `tools/demix_opencompass_namekeyed_adapter_v1.py`
- `tools/demix_opencompass_namekeyed_adapter_v2.py`
- `tools/demix_opencompass_namekeyed_adapter_v3.py`
- `tools/demix_opencompass_public_reconstruction_contract_20260827T1513JST.json`
- `tools/demix_opencompass_track_a1_hf_fixture_20260827.py`
- `OPENCOMPASS_051_PUBLICATION_PROVENANCE_20260827.json`
- `OPENCOMPASS_051_052_PAIRED_ENV_CONTRACT_20260827.json`
- `OPENCOMPASS_051_052_TRACK_A_DEPENDENCY_BOUNDARY_20260827.json`
- `OPENCOMPASS_TRACK_A1_HF_FIXTURE_CONTRACT_20260827.json`

Current corrected public reconstruction anchors:
- OpenCompass 0.5.1 first-party publication source anchor: tag `0.5.1.post1` at `ecc86a2728c06fd2c1ad34f1d0094f42b5243c78`.
- OpenCompass 0.5.2 sensitivity anchor: `974179240a1a4e3c0ff14c60621cf1f6c95b287a`.

Current key refinement: Track A1 now fixes `HuggingFaceCausalLM` on a source file that is byte-identical across the two OpenCompass anchors and fixes a tiny public model revision plus all nine DeMix benchmark config blobs. The visible `openicl_eval.py` changes are unreachable or neutral for this fixture (ordinary HF outputs do not enter the new rollout branch; GSM8K is the only frozen dataset with a dataset postprocessor and supplies no extra kwargs). The largest remaining source-level confounder before scores is the expanded 0.5.2 eager dataset-registry/import surface plus dependency resolution, not a changed HF wrapper or changed nine-benchmark definition.

Exact next action: finish the import-time registry/dependency audit just enough to pin one explicit shared Python 3.10 lock, then execute Track A1 phase 1 under both anchors with identical wrapper/model/tokenizer/dependencies and persist import/package/file hashes. If both imports succeed, compare raw nine-benchmark inference hashes before evaluating scores; run MBPP/HumanEval evaluators only in an isolated code-execution sandbox.

Nonempty frontier after Track A1:
1. complete remaining DeMix checkpoint metadata byte-identity classes;
2. continue orphan `mix_16` lineage resolution;
3. run matched merging-vs-retraining displacement sweep only after evaluator identity and environment sensitivity are locked;
4. continue SAFE-Merge implementation/reconstruction audit;
5. resume earlier continual-learning branches while preserving exact tested scope and clean independence.
