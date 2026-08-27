# Continual Learning — clean_g1 latest

Latest checkpoint: `RUN_20260827T2211_JST.md`

Base state: `STATE.md`

Current high-priority reconciliation:
- `CPO_PAPER_RELEASE_CODE_RECONCILIATION_20260827T2211JST.json`
- CPO paper-spec uses global TopP support plus globally normalized masked L1.
- Public release code at `MaolinLuo/CPO@9429452cb536a9e713b73b91c0011b96df44962c` instead uses per-tensor TopP and per-tensor normalization.
- For a protected coordinate in tensor `t`, release-code versus paper-spec regularizer magnitude scales as `M/m_t`; this can overweight small tensors materially.
- Do not attribute reported CPO gains specifically to the paper equations until paper-spec versus release-code-spec is causally separated.
- Next CPO action: run the fixed 2x2 factorial `{global, per-tensor} TopP × {global, per-tensor} normalization`, then measure actual cumulative mask/reference bytes and runtime overhead.

Current deterministic DeMix/OpenCompass reconstruction tools:
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

Track A1 status: shared dependency environment must model OpenCompass's `.[full]` import surface, not runtime-only. The shared-lock contract fail-closes until every direct/transitive distribution has an exact artifact hash. Execution remains blocked in the current container by Python 3.13 plus unavailable network/DNS for acquiring Python 3.10/package artifacts; this is not evidence about OpenCompass.

Exact continuation:
1. CPO: search for first-party historical masks/checkpoints/logs or clarification; then implement and verify the 2x2 selection/normalization factorial on synthetic tensors before expensive training.
2. CPO: measure actual release-code mask/ref storage and mask construction/per-step overhead on the smallest feasible Qwen3-VL scale.
3. DeMix/OpenCompass: in a networked Linux/Python-3.10 environment, resolve/hash the complete shared full-surface lock and execute Track A1 import/inference comparison.
4. Complete remaining DeMix checkpoint metadata byte-identity classes and orphan `mix_16` lineage.
5. Run matched merging-vs-retraining displacement sweep only after evaluator/environment identity is locked.
6. Continue SAFE-Merge and earlier continual-learning branches while preserving exact tested scope and clean independence.
