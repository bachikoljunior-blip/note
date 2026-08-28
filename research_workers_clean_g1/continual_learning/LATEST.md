# Continual Learning — clean_g1 latest

Latest checkpoint: `RUN_20260828T100410_JST.md`

Base state: `STATE.md`

Current high-priority reconciliation:
- CPO paper-spec uses global TopP support plus globally normalized masked L1; public release `MaolinLuo/CPO@9429452cb536a9e713b73b91c0011b96df44962c` uses per-tensor TopP plus per-tensor normalization.
- Public CPO main remains at the same release SHA; no upstream repair was present in this run.
- Public 4B/8B ZeRO-3 owner-only regularizer path still has the previously established `1/world_size` attenuation unless explicitly corrected; treat this separately from transport/state optimization.
- Public mask bookkeeping remains dense/global by default: dense bool masks + global int64 flat indices + fp32 refs are retained on every rank; 4B tied aliases can add dead state/build work.
- Streaming derive-index-and-release-mask previously reduced synthetic peak RSS and final auxiliary tensor bytes without changing tested algebra.
- Public ZeRO-3 CPU-offload path still copies full global idx/ref to every rank before filtering and copies the local BF16 partition to the compute device for masked drift.
- **New rank-local equivalence result:** source-equivalent randomized harness, 1,000 trials / 8,529 rank cases, produced **0 bitwise pending-gradient failures, 0 partial-loss failures, 0 partition-coverage failures** when idx/ref were prepartitioned once by rank while preserving the **global masked-count denominator**.
- **Do not use local support count as the denominator.** It changes semantics and creates rank-dependent coordinate scaling under support imbalance; distributed `world_size` correction must remain a separate explicit axis.
- **New searchsorted result:** because `_mask_flat_idx` is sorted and refs are aligned in the same mask order, rank partitioning can use two CPU `searchsorted` bounds plus `clone()` rather than an O(s) partition boolean. 5,000 randomized trials / 82,760 rank cases produced **0 idx/ref mismatches**. Cloning is required so rank slices do not pin global storage.
- Conditional Qwen3-VL-4B / 10% / W=8 steady-state auxiliary capacity changes from about **9.093 GiB/rank** for current dense-mask+global-idx/ref state to about **0.620 GiB/rank** after canonical namespace + dense-mask release + balanced rank-local sparse idx/ref, a **93.18% conditional reduction**. This is not measured RSS and support balance must be profiled.
- Current safest repair order: (1) fail-closed canonical trainer namespace; (2) derive indices and release dense masks; (3) searchsorted+clone rank-local idx/ref while retaining `global_n_masked`; (4) validate hooks/reduce-scatter under PyTorch 2.8 + DeepSpeed 0.16.4; (5) profile current-vs-ranklocal transfers; (6) evaluate CPU-local masked drift; (7) choose packed/sparse/hybrid persistence from measured support; (8) separately correct distributed scaling and run paired-seed quality factorial.

New durable artifacts:
- `CPO_ZERO3_RANKLOCAL_EQUIVALENCE_HARNESS_20260828T100121_JST.py`
- `CPO_ZERO3_RANKLOCAL_EQUIVALENCE_RESULT_20260828T100121_JST.json`
- `CPO_ZERO3_SEARCHSORTED_PREPARTITION_RESULT_20260828T100345_JST.json`
- `RUN_20260828T100410_JST.md`

Exact CPO continuation:
1. Implement the source-equivalent rank-local load prototype combining canonical namespace, `searchsorted+clone`, dense-mask release, stored `global_n_masked`, and runtime tuple checks.
2. Run under PyTorch 2.8.0, then DeepSpeed 0.16.4; compare actual hook/reduce-scatter pending gradients before changing compute placement.
3. Instrument real per-parameter support by rank and persistence. Do not assume balanced `s/W` in measured capacity.
4. Profile current H2D/D2H vs rank-local idx/ref while leaving partition compute placement unchanged; then separately test CPU-local masked drift on offloaded partitions.
5. Execute explicit world-size scaling correction only as a separate correctness/quality axis.
6. Measure real Qwen3-VL mask files, RSS, GPU peak, bus bytes, build/conversion time and steady runtime.
7. Continue read-only paper-table provenance search, then DeMix/OpenCompass Track A1 and earlier continual-learning branches.

Remaining frontier:
- Public-runtime rank-local ZeRO-3 state/hook validation.
- Actual support imbalance/persistence measurement.
- Current-vs-ranklocal bus/RSS/runtime profiling and CPU-local masked drift.
- Distributed scaling quality factorial.
- Real Qwen3-VL storage/runtime measurement.
- Historical paper-table provenance.
- DeMix/OpenCompass Track A1, orphan `mix_16`, merge-vs-retrain displacement, SAFE-Merge and earlier branches.
