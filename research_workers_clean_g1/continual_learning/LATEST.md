# Continual Learning — clean_g1 latest

Latest checkpoint: `RUN_20260828T091112_JST.md`

Base state: `STATE.md`

Current high-priority reconciliation:
- CPO paper-spec uses global TopP support plus globally normalized masked L1; public release `MaolinLuo/CPO@9429452cb536a9e713b73b91c0011b96df44962c` uses per-tensor TopP plus per-tensor normalization.
- Public 4B/8B ZeRO-3 path still has the source-level owner-only regularizer `1/world_size` attenuation identified earlier; 8-GPU launchers imply nominal lambda 100 is lambda-equivalent about 12.5 on that public path unless corrected. This is source-level algebra, not proof about unreleased paper-table code.
- Public CPO bookkeeping is dense in mask tensors even though protected coordinates are sparse: dense bool masks + float32 references + int64 flat indices.
- Qwen3-VL-4B public immutable revision `ebb281ec70b05090aa6165b016eac8ec08e71b17` serializes the tied text matrix once, while Transformers 4.57.3 re-ties the output head after load. CPO then expands the runtime `state_dict()` mask namespace beyond the serialized checkpoint namespace.
- The tied matrix is `151936 × 2560 = 388,956,160` scalars. If the alias is the only extra floating runtime key, public CPO's logical scalar denominator is 4,826,771,968 vs 4,437,815,808 physical parameters, an 8.764585% inflation.
- Source-equivalent tied fixture established that canonical and dead-alias masks/refs are value-identical but separately allocated/serialized; the alias therefore duplicates real payload and top-k build work.
- **Mask-lifetime result:** after public trainer derives `_mask_flat_idx = mask.nonzero()`, dense bool mask values are never used again. On a 100M-scalar synthetic 10%-support source-equivalent load, streaming derive-index-and-release-mask reduced peak RSS **503.90→446.73 MB** and final logical auxiliary tensor bytes **220M→120M** without changing tested mask algebra.
- **Representation frontier:** dense mask+refs vs int64-index+refs breaks even at 12.5% support; int32 local-index+refs has a 25% raw break-even against dense, and packed-bitmask+refs was smallest in the 10% storage benchmark. Int32 remains experimental until PyTorch 2.8 + DeepSpeed validation.
- **New ZeRO-3 offload source result:** public CPO copies the full global protected indices and full global fp32 references to `param.device` on every rank *before* rank-partition filtering; then it executes `param.ds_tensor.to(param.device).float()`, copies rank-local pending idx/grad back to CPU, and the gradient hook copies them back to the gradient device.
- Public `zero3_offload.json` sets parameter offload to CPU. DeepSpeed 0.16.4 propagates this into ZeRO Init's remote parameter device, so ordinary non-persistent `ds_tensor` partitions are CPU-resident while the local/parameter compute device is the accelerator. The public trainer comment that `ds_tensor` is always on the compute device is therefore not valid for those offloaded parameters.
- Transformers 4.57.3 resolves the public `stage3_param_persistence_threshold="auto"` to `10*hidden_size`; Qwen3-VL-4B hidden size 2560 gives **25,600 scalars**, so major matrices are non-persistent/offloaded while small tensors may remain persistent.
- **Conditional 4B/10%/8-rank transfer model:** treating the full canonical domain as non-persistent with exactly 10% support, current explicit tensor operations sum to about **7.233 GiB/rank per `_compute_loss`** of bidirectional tensor payload (~**57.86 GiB across 8 ranks**). This is source-level accounting, not measured PCIe/NVLink traffic; actual support/persistence must be measured.
- In that same conditional scenario, global idx+refs alone are ~4.960 GiB H2D/rank; BF16 local partition copy ~1.033 GiB; each pending idx+grad direction ~0.620 GiB. The post-cast fp32 local partition itself is ~2.067 GiB, so source-implied transient device payload can be large even before GRPO/model state.
- **Repair hypothesis:** prepartition mask indices/refs by ZeRO rank once and exploit CPU-offloaded `ds_tensor` to compute masked drift locally, transferring only rank-local pending contributions. Same conditional model gives ~0.620 GiB/rank/call if idx+grad are transferred, or ~0.207 GiB if rank-local indices can safely remain cached on accelerator. These are hypotheses requiring profiling, not performance claims.
- Exact-storage/view dedup remains unsafe because distinct `nn.Parameter` objects may share identical or overlapping storage and stay separately trainer-visible.
- **Current safest repair order:** (1) fail-closed canonical trainer-namespace filtering; (2) streaming derive-indices-and-release-dense-mask; (3) rank-localize ZeRO-3 mask/ref state and profile current transfers; (4) compare CPU-local masked drift against current full-partition device copy; (5) optimize persistent packed/sparse/hybrid format only after real support is known; (6) separately correct distributed regularizer scaling and run paired-seed quality factorial.
- New durable results: `CPO_ZERO3_OFFLOAD_TRANSFER_MODEL_20260828T090931_JST.json`, `CPO_MASK_STREAMING_LOAD_RESULT_20260828T090540_JST.json`, `CPO_MASK_REPRESENTATION_RESULT_20260828T090326_JST.json`.

Exact CPO continuation:
1. Under public PyTorch 2.8 / DeepSpeed 0.16.4, instrument H2D/D2H bytes/time around global idx/ref copies, `ds_tensor.to`, pending `.cpu()`, and hook `.to()` per parameter, also recording persistence and support.
2. Implement a rank-localization equivalence harness that prepartitions indices/refs once and reproduces current pending regularizer gradients bitwise before changing compute placement.
3. Benchmark CPU-local masked `diff/sign` on the CPU-offloaded ZeRO partition against current GPU-local full-partition copy, including pinning/vectorization and wall time.
4. Validate canonical namespace + streaming mask-drop + rank-localization on a small real Transformers 4.57.3 tied-weight model, then Qwen3-VL-4B if resources permit.
5. Measure real Qwen3-VL canonical mask-domain size, actual support/overlap, `task_k.pt` bytes, initial/conversion/steady RSS, GPU peak, bus traffic, index-conversion/mask-build/runtime overhead.
6. Select/test dense-packed vs sparse-index vs per-tensor hybrid persistence from measured cumulative support; separately validate any int32 local-index path under PyTorch 2.8 + DeepSpeed with fail-closed range checks.
7. Execute single-rank reference vs current owner-only ZeRO-3 vs world-size-corrected regularization, then full selection × normalization × DP-scaling paired-seed factorial.
8. Continue read-only first-party provenance search for paper-table mask/scaling semantics.

Current deterministic DeMix/OpenCompass reconstruction tools and anchors remain unchanged from the predecessor checkpoint. Track A1 still requires a fully hashed shared Python 3.10 `.[full]` dependency environment; environment acquisition limits are not evidence about OpenCompass.

Remaining frontier:
- Public-runtime transfer profiling and rank-local ZeRO-3 mask/ref implementation.
- PyTorch-2.8/DeepSpeed and real-model validation of canonical namespace + streaming mask-drop + optional int32 local indices.
- Real Qwen3-VL CPO support/file/RSS/GPU/bus/build/runtime measurements and physical-vs-effective accounting.
- Packed/sparse/hybrid mask representation after real support is known.
- Distributed regularizer scaling and expanded quality factorial.
- Historical paper-table provenance.
- DeMix/OpenCompass Track A1 when the required environment is available.
- Remaining DeMix checkpoint metadata byte-identity classes and orphan `mix_16` lineage.
- Matched merge-vs-retrain displacement sweep, SAFE-Merge and earlier continual-learning branches, preserving exact tested scope and clean independence.
