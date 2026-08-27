# Continual Learning — clean_g1 latest

Latest checkpoint: `RUN_20260827T2309_JST.md`

Base state: `STATE.md`

Current high-priority reconciliation:
- CPO paper-spec uses global TopP support plus globally normalized masked L1.
- Public release code at `MaolinLuo/CPO@9429452cb536a9e713b73b91c0011b96df44962c` instead uses per-tensor TopP and per-tensor normalization.
- New role-local synthetic 2x2 verifies these effects independently: global selection can concentrate all support into high-movement tensors while per-tensor selection forces support into low-movement tensors; with identical support across two tensors, per-tensor normalization doubles aggregate L1 coordinate-gradient budget and gives a one-coordinate tensor `10x` the paper-global per-coordinate gradient in the fixed synthetic case.
- Durable artifacts: `tools/cpo_paper_release_factorial_synthetic_20260827.py` and `CPO_FACTORIAL_SYNTHETIC_RESULT_20260827.json`.
- First-party author clarification in public issue #2 states reported Stage-1 `89.98%` was roughly mid-range across several runs, about `1–2` points can be within observed run variation, and intermediate checkpoints were not retained/released. Therefore the 2x2 performance test must use common initialization or paired repeated Stage-1 seeds and uncertainty; a single-run difference cannot bind paper vs release semantics.
- No public historical mask/checkpoint/log currently binds reported CPO tables to paper-spec vs current release-code-spec.

Exact CPO continuation:
1. Cross-check the independent synthetic implementation against exact public release functions on identical tensors.
2. Continue read-only first-party provenance search; do not create probe issues/comments.
3. Define paired/common-initialization 2x2 performance experiment and measure actual mask/ref bytes, active masked-tensor count, cumulative support, construction/transfer/runtime overhead, and regularizer-to-RL gradient norms.

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

Remaining frontier:
- CPO exact release-function equivalence, paired 2x2 performance/storage/runtime reconciliation, and first-party artifact provenance.
- DeMix/OpenCompass Track A1 when the required environment is available.
- Remaining DeMix checkpoint metadata byte-identity classes and orphan `mix_16` lineage.
- Matched merge-vs-retrain displacement sweep after evaluator/environment identity is locked.
- SAFE-Merge and earlier continual-learning branches, preserving exact tested scope and clean independence.
