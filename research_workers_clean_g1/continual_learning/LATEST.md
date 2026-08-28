# Continual Learning — clean_g1 latest

Latest checkpoint: `RUN_20260828T110534_JST.md`

Base state: `STATE.md`

Current high-priority reconciliation:
- CPO paper-spec uses global TopP support plus globally normalized masked L1; public release `MaolinLuo/CPO@9429452cb536a9e713b73b91c0011b96df44962c` uses per-tensor TopP plus per-tensor normalization.
- **Pinned-source ZeRO-3 scaling proof:** the CPO README specifies PyTorch 2.8.0, DeepSpeed 0.16.4 and eight GPUs for RL. DeepSpeed `v0.16.4@e2dc3eeb1923073e32739596a4fd051417d4ff92` explicitly divides the coalesced full gradient buffer by `world_sz` before reduce-scatter. Because public CPO injects each protected coordinate only on its owner rank, that regularizer arrives after reduce-scatter as exactly `g/world_size`; at W=8, `lambda=100` is 12.5 for this owner-only term unless corrected.
- The public ZeRO-3 `mask_loss` log has the same 1/W issue under exact partition coverage: rank-local partials are gathered with `nanmean`, so the displayed value is the full masked-L1 contribution divided by W. Do not compare this log directly with ZeRO-2 regularizer strength.
- Public mask bookkeeping is dense/global by default: dense bool masks + global int64 flat indices + fp32 refs are retained on every rank; tied state-dict aliases can add dead state/build work.
- **Sparse-canonical prototype:** release-format masks are converted only for duplicate-free trainer-visible `named_parameters`; state-dict-only tied aliases and floating buffers are dropped, while distinct Parameters sharing storage remain distinct. Dense masks can then be released.
- **Fail-closed runtime contract:** canonical namespace digest, name/shape/numel/dtype, idx/ref alignment, rank/world-size, and optional `ds_numel` are checked before rank-local use.
- **Equivalence result:** searchsorted+clone rank partitioning and global-denominator regularizer algebra produced 544/544 matching partition cases, 544/544 bitwise pending-gradient matches, and 544/544 partial-loss matches under the available torch 2.10 CPU runtime.
- `global_n_masked` must remain global. Replacing it with rank-local support changes coordinate scaling under support imbalance.
- **Persistence correction:** sparse runtime state and sparse disk persistence must be separated. Global int64 idx+fp32 refs beats the current dense-bool+fp32-ref file only below 12.5% support; int32 sparse only below 25%. With bit-packed mask+fp32 refs, sparse loses above 1.5625%/3.125% respectively.
- A 5M-scalar `torch.save` test confirmed the crossover: at 10% support release/int64/int32/bitpacked were 7.00/6.00/4.00/2.63 MB; at 19% they were 8.80/11.40/7.60/4.43 MB; at 34.39% they were 11.88/20.64/13.76/7.50 MB.
- Strongest current state/transport design: **bit-packed global persistence + fp32 refs on disk, converted once to canonical rank-local sparse idx/ref at load**, subject to measured real support and pinned-runtime validation. The world-size scaling fix remains a separate experimental axis.

New durable artifacts:
- `CPO_SPARSE_CANONICAL_RANKLOCAL_PROTOTYPE_20260828T110122_JST.py`
- `CPO_SPARSE_CANONICAL_RANKLOCAL_RESULT_20260828T110122_JST.json`
- `CPO_PERSISTENCE_CROSSOVER_RESULT_20260828T110250_JST.json`
- `CPO_ZERO3_PINNED_REDUCESCATTER_PROOF_20260828T110506_JST.json`
- `RUN_20260828T110305_JST.md`
- `RUN_20260828T110534_JST.md`

Exact CPO continuation:
1. Integrate the sparse-canonical loader into a source-equivalent trainer shim while preserving current public-code scaling.
2. Run under PyTorch 2.8.0 + DeepSpeed 0.16.4 and compare current global-filter vs rank-local prepartition tensors at hook input and after reduce-scatter with no scaling correction first.
3. Then test owner-only `world_size` multiplication as a separate correctness/quality axis; do not mix it initially with paper-spec global TopP/global normalization.
4. Measure real support per parameter/rank and real `task_k.pt` bytes; choose persistence per tensor from measured support instead of globally adopting int64 sparse storage.
5. Profile H2D/D2H, CPU RSS, GPU peak, build/conversion time and per-step runtime; then separately test CPU-local masked drift.
6. Correct/replace ZeRO-3 `mask_loss` logging with a distributed sum only after confirming intended metric semantics.
7. Continue real Qwen3-VL measurement, historical paper-table provenance, DeMix/OpenCompass Track A1, SAFE-Merge and earlier branches.

Remaining frontier:
- Public-runtime rank-local ZeRO-3 state/hook validation under pinned versions.
- Explicit world-size scaling quality factorial and corrected logging validation.
- Real support imbalance/persistence measurement and per-tensor hybrid-format selection.
- Current-vs-ranklocal bus/RSS/runtime profiling and CPU-local masked drift.
- Real Qwen3-VL storage/runtime measurement.
- Historical paper-table provenance.
- DeMix/OpenCompass Track A1, orphan `mix_16`, merge-vs-retrain displacement, SAFE-Merge and earlier branches.
