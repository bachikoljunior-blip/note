# Continual Learning — clean_g1 latest

Latest checkpoint: `RUN_20260828T0107_JST.md`

Base state: `STATE.md`

Current high-priority reconciliation:
- CPO paper-spec uses global TopP support plus globally normalized masked L1.
- Public release at `MaolinLuo/CPO@9429452cb536a9e713b73b91c0011b96df44962c` uses per-tensor TopP plus per-tensor normalization.
- Source-locked executable equivalence remains in `tools/cpo_release_equivalence_harness_20260828.py` / `CPO_RELEASE_EQUIVALENCE_RESULT_20260828.json`.
- Public 4B/8B ZeRO-3 path still has the source-level `1/world_size` owner-only regularizer attenuation identified in `RUN_20260828T0011_JST.md`; public 8-GPU launchers imply nominal lambda 100 is lambda-equivalent about 12.5 on that release path unless corrected. This is source-level algebra, not a live 8-GPU reproduction or proof about unreleased paper-table code.
- New operational finding: the current public CPO bookkeeping is sparse in protected coordinates but dense in masks. `CLGRPOTrainer` persistently retains dense bool masks, float32 protected references and int64 flat indices. For mask-domain scalar count `N` and accumulated support `u`, logical persistent auxiliary tensor payload is `N + 12uN` bytes; current saved cumulative-mask tensor payload is `N + 4uN` bytes, excluding Python/serialization/transient overhead.
- Whole-model/full-mask-domain scenarios using public Qwen3-VL BF16 weight indexes: after the first 10% mask, auxiliary state is about 9.09 GiB for 4B and 17.96 GiB for 8B. Under independent 10% supports across four masks (`u=34.39%`), it is about 21.19 GiB / 41.86 GiB. These are scenarios, not measured actual mask-domain memory.
- Release code retains successive cumulative `task_k.pt` files. Under the same independent/full-domain scenario four masks contain about 31.49 GiB (4B) or 62.21 GiB (8B) of logical tensor payload in total.
- Mask construction retains the current state dict while loading the previous full model/state dict, so two BF16 weight payloads can coexist: about 16.53 GiB (4B) or 32.66 GiB (8B) before other/transient memory. This is source-structure payload, not measured RSS.
- Durable calculation artifact: `CPO_AUX_STATE_MEMORY_MODEL_20260828.json`.
- Reference anchoring is not a new discrepancy: both paper practical objective and release anchor the cumulative protected support to the immediately previous task checkpoint.

Exact CPO continuation:
1. Measure real mask-domain scalar count, per-task new support, cumulative union/overlap and actual `task_k.pt` bytes; compare with the source-structural memory model.
2. Profile trainer CPU RSS plus per-step device-copy bytes/time for dense mask / float refs / int64 indices under ZeRO-2 and ZeRO-3 offload.
3. Execute minimal distributed equivalence: single-rank reference vs current owner-only ZeRO-3 vs owner-only×world-size correction; measure post-reduction regularizer/RL gradient ratio and logged-vs-true regularizer magnitude.
4. Expand quality factorial to `global/per-tensor selection × global/per-tensor normalization × uncorrected/corrected DP scaling` with paired initialization/seeds.
5. Measure mask-construction peak RSS/wall time and continue read-only first-party provenance search for paper-table mask/scaling semantics.

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

Track A1 status: shared dependency environment must model OpenCompass's `.[full]` import surface, not runtime-only. The shared-lock contract fail-closes until every direct/transitive distribution has an exact artifact hash. Prior execution environment incompatibility/network acquisition limits remain environment blockers, not evidence about OpenCompass.

Remaining frontier:
- CPO real memory/storage/runtime and distributed scaling measurements, expanded quality factorial and first-party provenance.
- DeMix/OpenCompass Track A1 when the required environment is available.
- Remaining DeMix checkpoint metadata byte-identity classes and orphan `mix_16` lineage.
- Matched merge-vs-retrain displacement sweep after evaluator/environment identity is locked.
- SAFE-Merge and earlier continual-learning branches, preserving exact tested scope and clean independence.
