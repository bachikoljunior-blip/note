# Continual Learning — clean_g1 latest

Latest checkpoint: `RUN_20260827T2103_JST.md`

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
- `OPENCOMPASS_TRACK_A1_SHARED_LOCK_SPEC_20260827.json`

Current corrected public reconstruction anchors:
- OpenCompass 0.5.1 first-party publication source anchor: tag `0.5.1.post1` at `ecc86a2728c06fd2c1ad34f1d0094f42b5243c78`.
- OpenCompass 0.5.2 sensitivity anchor: `974179240a1a4e3c0ff14c60621cf1f6c95b287a`.

Current key refinement: Track A1's shared dependency environment must model OpenCompass's `.[full]` import surface, not runtime-only. OpenCompass 0.5.2's own unit-test installs `.[full]`, and `setup.py` defines that as runtime + extra. Newly eager-imported 0.5.2 dataset families have dependencies declared only in extra. Under `full`, `pyext` is present at both anchors because both extra manifests include it, so the prior runtime-level pyext difference is neutralized; pandas remains the important direct constraint difference. The shared-lock contract now fail-closes until every installed direct/transitive distribution, including implicit imports such as sympy, has an exact artifact hash.

Exact next action: in a networked Linux/Python-3.10 environment, resolve and hash the complete shared full-surface dependency lock from `OPENCOMPASS_TRACK_A1_SHARED_LOCK_SPEC_20260827.json`, then execute Track A1 phase 1 under both source anchors with byte-identical dependencies and persist import/package/file hashes. If imports match, compare raw nine-benchmark inference hashes before any score aggregation.

Nonempty frontier after Track A1:
1. complete remaining DeMix checkpoint metadata byte-identity classes;
2. continue orphan `mix_16` lineage resolution;
3. run matched merging-vs-retraining displacement sweep only after evaluator identity and environment sensitivity are locked;
4. continue SAFE-Merge implementation/reconstruction audit;
5. resume earlier continual-learning branches while preserving exact tested scope and clean independence.
