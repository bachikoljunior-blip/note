# Continual Learning — clean_g1 latest

Latest checkpoint: `RUN_20260828T110305_JST.md`

Base state: `STATE.md`

Current high-priority reconciliation:
- CPO paper-spec uses global TopP support plus globally normalized masked L1; public release `MaolinLuo/CPO@9429452cb536a9e713b73b91c0011b96df44962c` uses per-tensor TopP plus per-tensor normalization.
- Public 4B/8B ZeRO-3 owner-only regularizer path retains the previously established `1/world_size` attenuation unless explicitly corrected; keep this separate from transport/state optimization.
- Public mask bookkeeping is dense/global by default: dense bool masks + global int64 flat indices + fp32 refs are retained on every rank; tied state-dict aliases can add dead state/build work.
- **New end-to-end sparse-canonical prototype:** release-format masks are converted only for duplicate-free trainer-visible `named_parameters`; state-dict-only tied aliases and floating buffers are dropped, while distinct Parameters sharing storage remain distinct. Dense masks can then be released.
- **New fail-closed runtime contract:** canonical namespace digest, name/shape/numel/dtype, idx/ref alignment, rank/world-size, and optional `ds_numel` are checked before rank-local use.
- **New equivalence result:** searchsorted+clone rank partitioning and global-denominator regularizer algebra produced 544/544 matching partition cases, 544/544 bitwise pending-gradient matches, and 544/544 partial-loss matches under the available torch 2.10 CPU runtime.
- `global_n_masked` must remain global. Replacing it with rank-local support changes coordinate scaling under support imbalance.
- **New persistence correction:** sparse runtime state and sparse disk persistence must be separated. Global int64 idx+fp32 refs beats the current dense-bool+fp32-ref file only below 12.5% support; int32 sparse only below 25%. With bit-packed mask+fp32 refs, sparse loses above 1.5625%/3.125% respectively.
- A 5M-scalar `torch.save` test confirmed the crossover: at 10% support release/int64/int32/bitpacked were 7.00/6.00/4.00/2.63 MB; at 19% they were 8.80/11.40/7.60/4.43 MB; at 34.39% they were 11.88/20.64/13.76/7.50 MB.
- Therefore the strongest current repair candidate is **bit-packed global persistence + fp32 refs on disk, then one-time conversion to canonical rank-local sparse idx/ref at load**, subject to measured real support and PyTorch 2.8/DeepSpeed 0.16.4 validation.

New durable artifacts:
- `CPO_SPARSE_CANONICAL_RANKLOCAL_PROTOTYPE_20260828T110122_JST.py`
- `CPO_SPARSE_CANONICAL_RANKLOCAL_RESULT_20260828T110122_JST.json`
- `CPO_PERSISTENCE_CROSSOVER_RESULT_20260828T110250_JST.json`
- `RUN_20260828T110305_JST.md`

Exact CPO continuation:
1. Integrate the sparse-canonical loader into a source-equivalent trainer shim while preserving public-code scaling.
2. Run under PyTorch 2.8.0, then DeepSpeed 0.16.4; compare hook-input and post-reduce-scatter gradients for current global-filter vs rank-local prepartition paths.
3. Measure real support per parameter/rank and real `task_k.pt` bytes; choose persistence per tensor from measured support instead of globally adopting int64 sparse storage.
4. Profile current vs rank-local H2D/D2H, CPU RSS, GPU peak, build/conversion time and per-step runtime; then separately test CPU-local masked drift.
5. Execute world-size scaling correction only as a separate correctness/quality axis after transport/state equivalence.
6. Measure real Qwen3-VL storage/runtime and continue historical paper-table provenance, DeMix/OpenCompass Track A1, SAFE-Merge and earlier branches.

Remaining frontier:
- Public-runtime rank-local ZeRO-3 state/hook validation under the pinned versions.
- Real support imbalance/persistence measurement and per-tensor hybrid-format selection.
- Current-vs-ranklocal bus/RSS/runtime profiling and CPU-local masked drift.
- Distributed scaling quality factorial.
- Real Qwen3-VL storage/runtime measurement.
- Historical paper-table provenance.
- DeMix/OpenCompass Track A1, orphan `mix_16`, merge-vs-retrain displacement, SAFE-Merge and earlier branches.
