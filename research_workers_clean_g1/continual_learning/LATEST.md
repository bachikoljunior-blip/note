# Continual Learning — clean_g1 latest

Latest checkpoint: `RUN_20260828T130554_JST.md`

Base state: `STATE.md`

Current high-priority reconciliation:
- CPO paper-spec uses global TopP support plus globally normalized masked L1; public release `MaolinLuo/CPO@9429452cb536a9e713b73b91c0011b96df44962c` uses per-tensor TopP plus per-tensor normalization.
- **Pinned-source ZeRO-3 scaling proof:** public CPO injects a protected coordinate only on its owner rank, while DeepSpeed 0.16.4 divides the coalesced gradient buffer by `world_sz` before reduce-scatter. Therefore this owner-only regularizer arrives as exactly `g/world_size`; with eight GPUs, released-path `lambda=100` behaves as 12.5 for this term unless explicitly corrected. Public ZeRO-3 `mask_loss` logging has the analogous 1/W averaging issue.
- Public mask bookkeeping is dense/global by default and can retain state-dict-only aliases/buffers that the trainer never consumes.
- **New source-equivalent trainer shim:** `CPO_SPARSE_CANONICAL_TRAINER_SHIM_20260828T130249_JST.py` converts released masks once to duplicate-free trainer-visible canonical sparse state, prepartitions sorted idx/ref by rank with `searchsorted`, preserves the released per-tensor global denominator and owner-rank hook contract, and intentionally leaves world-size scaling unchanged.
- **Shim equivalence result:** on available `torch 2.10.0+cpu`, 228/228 source-equivalent cases and 394/394 hook comparisons matched with zero mismatches across ZeRO-2-like and simulated ZeRO-3 paths, world sizes 1/2/3/4/8, varying support densities, a tied alias and a persistent floating buffer. This is synthetic/source-equivalent validation, not pinned PyTorch 2.8 + DeepSpeed 0.16.4 execution evidence.
- **Repeated-filter microbenchmark:** for 2M scalar synthetic CPU tensors, support 1/10/34.39%, worlds 2/8/16, rank-local prepartitioning was 5.70×–70.65× faster per repeated filtering/indexing step than recreating the public-style global partition filter. At 10% support the medians were 7.02× (W=2), 17.02× (W=8), 16.31× (W=16). This is CPU algorithmic evidence only, not GPU/PCIe/DeepSpeed end-to-end throughput.
- Persistence remains separate from runtime sparsification: the strongest current state/transport design is **bit-packed global persistence + fp32 refs on disk, converted once to canonical rank-local sparse idx/ref at load**, subject to real support measurements.
- Current execution environment is Python 3.13.5 + torch 2.10.0 CPU, no DeepSpeed, and no cached/installed PyTorch 2.8 + DeepSpeed 0.16.4 environment. Pinned-binary distributed validation is therefore the current hard runtime blocker, not negative evidence.

New durable artifacts:
- `CPO_SPARSE_CANONICAL_TRAINER_SHIM_20260828T130249_JST.py`
- `CPO_SPARSE_CANONICAL_TRAINER_SHIM_RESULT_20260828T130249_JST.json`
- `CPO_RANKLOCAL_MICROBENCH_GRID_20260828T130249_JST.py`
- `CPO_RANKLOCAL_MICROBENCH_GRID_RESULT_20260828T130249_JST.json`
- `RUN_20260828T130554_JST.md`

Exact CPO continuation:
1. Run the new shim under **PyTorch 2.8.0 + DeepSpeed 0.16.4** against the released CPO trainer; compare current global-filter vs prepartitioned rank-local tensors at hook input and after reduce-scatter, **without** scaling correction first.
2. Then test owner-only `world_size` multiplication as a separate correctness/quality axis; do not mix it initially with paper-spec global TopP/global normalization.
3. Measure real support per parameter/rank and real `task_k.pt` bytes; choose persistence per tensor from measured support rather than globally adopting sparse indices.
4. Profile H2D/D2H, CPU RSS, GPU peak, build/conversion time and end-to-end step runtime on real Qwen3-VL; separately test CPU-local masked drift.
5. Correct/replace ZeRO-3 `mask_loss` logging with a distributed sum only after confirming intended metric semantics.
6. Continue historical paper-table provenance, DeMix/OpenCompass Track A1, SAFE-Merge and earlier role-local branches after the pinned-runtime CPO test.

Remaining frontier:
- Pinned PyTorch 2.8.0 + DeepSpeed 0.16.4 rank-local ZeRO-3 state/hook/reduce-scatter validation.
- Explicit world-size scaling quality factorial and corrected logging validation.
- Real support imbalance/persistence measurement and per-tensor hybrid-format selection.
- Current-vs-ranklocal bus/RSS/runtime profiling and CPU-local masked drift.
- Real Qwen3-VL storage/runtime measurement.
- Historical paper-table provenance.
- DeMix/OpenCompass Track A1, orphan `mix_16`, merge-vs-retrain displacement, SAFE-Merge and earlier branches.
