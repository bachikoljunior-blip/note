# Continual Learning — clean_g1 latest

Latest checkpoint: `RUN_20260828T140430_JST.md`

Base state: `STATE.md`

Current high-priority reconciliation:
- CPO paper-spec uses global TopP support plus globally normalized masked L1; public release `MaolinLuo/CPO@9429452cb536a9e713b73b91c0011b96df44962c` uses per-tensor TopP plus per-tensor normalization.
- **Pinned-source ZeRO-3 scaling proof:** public CPO injects a protected coordinate only on its owner rank, while DeepSpeed 0.16.4 divides the coalesced gradient buffer by `world_sz` before reduce-scatter. Therefore this owner-only regularizer arrives as exactly `g/world_size`; with eight GPUs, released-path `lambda=100` behaves as 12.5 for this term unless explicitly corrected.
- **New exact logging contract:** released ZeRO-3 `mask_loss` is a rank-local partial but is gathered with `nanmean`; source-equivalent validation over 600 cases showed this equals full masked-L1 / world_size, while distributed `nansum` recovers the full metric in all 600 cases. ZeRO-2/unsharded ranks each hold the full metric, so mean remains correct there.
- **Cross-scale logging consequence:** released 2B GSPO/CPO uses ZeRO-2 on eight visible GPUs while 4B/8B use ZeRO-3 offload on eight visible GPUs. Current TensorBoard `mask_loss` is therefore full-scale for 2B but about 1/8-scale for 4B/8B at equal underlying masked drift; cross-scale curves are not directly comparable.
- Public mask bookkeeping is dense/global by default and can retain state-dict-only aliases/buffers that the trainer never consumes.
- `CPO_SPARSE_CANONICAL_TRAINER_SHIM_20260828T130249_JST.py` converts released masks once to duplicate-free trainer-visible canonical sparse state, prepartitions sorted idx/ref by rank with `searchsorted`, preserves the released per-tensor global denominator and owner-rank hook contract, and intentionally leaves world-size scaling unchanged.
- Shim equivalence on available `torch 2.10.0+cpu`: 228/228 source-equivalent cases and 394/394 hook comparisons matched with zero mismatches across ZeRO-2-like and simulated ZeRO-3 paths, world sizes 1/2/3/4/8, varying support densities, a tied alias and a persistent floating buffer.
- Repeated-filter CPU microbenchmark: for 2M scalar synthetic tensors, rank-local prepartitioning was 5.70×–70.65× faster per repeated filtering/indexing step than recreating the public-style global filter. This remains CPU algorithmic evidence only.
- Persistence remains separate from runtime sparsification: strongest current design is **bit-packed global persistence + fp32 refs on disk, converted once to canonical rank-local sparse idx/ref at load**, subject to real support measurements.
- Current execution environment is Python 3.13.5 + torch 2.10.0 CPU, no DeepSpeed, and no cached/installed PyTorch 2.8 + DeepSpeed 0.16.4 environment. Pinned-binary distributed validation is the current hard runtime blocker, not negative evidence.

New durable artifacts:
- `CPO_MASK_LOSS_LOGGING_VALIDATION_20260828T140341_JST.py`
- `CPO_MASK_LOSS_LOGGING_VALIDATION_RESULT_20260828T140341_JST.json`
- `RUN_20260828T140430_JST.md`

Exact CPO continuation:
1. Run the canonical rank-local shim under **PyTorch 2.8.0 + DeepSpeed 0.16.4** against released CPO; compare current global-filter vs rank-local tensors at hook input and after reduce-scatter, **without** scaling correction first.
2. In that pinned run, record rank-local partial `mask_loss`, released `nanmean`, and corrected ZeRO-3 distributed sum and verify against a tiny full-reference metric.
3. Then test owner-only `world_size` multiplication as a separate correctness/quality axis; keep paper-spec global TopP/global normalization out of that first distributed test.
4. Measure real support per parameter/rank and real `task_k.pt` bytes; choose persistence per tensor from measured support rather than globally adopting sparse indices.
5. Profile H2D/D2H, CPU RSS, GPU peak, build/conversion time and end-to-end step runtime on real Qwen3-VL; separately test CPU-local masked drift.
6. Continue historical paper-table provenance, DeMix/OpenCompass Track A1, SAFE-Merge and earlier role-local branches after the pinned-runtime CPO test.

Remaining frontier:
- Pinned PyTorch 2.8.0 + DeepSpeed 0.16.4 rank-local ZeRO-3 state/hook/reduce-scatter validation.
- Explicit world-size scaling quality factorial plus corrected logging validation.
- Real support imbalance/persistence measurement and per-tensor hybrid-format selection.
- Current-vs-ranklocal bus/RSS/runtime profiling and CPU-local masked drift.
- Real Qwen3-VL storage/runtime measurement.
- Historical paper-table provenance.
- DeMix/OpenCompass Track A1, orphan `mix_16`, merge-vs-retrain displacement, SAFE-Merge and earlier branches.
