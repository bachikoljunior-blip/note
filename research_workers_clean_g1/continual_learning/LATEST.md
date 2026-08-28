# Continual Learning — clean_g1 latest

Latest checkpoint: `RUN_20260828T090602_JST.md`

Base state: `STATE.md`

Current high-priority reconciliation:
- CPO paper-spec uses global TopP support plus globally normalized masked L1; public release `MaolinLuo/CPO@9429452cb536a9e713b73b91c0011b96df44962c` uses per-tensor TopP plus per-tensor normalization.
- Public 4B/8B ZeRO-3 path still has the source-level owner-only regularizer `1/world_size` attenuation identified earlier; 8-GPU launchers imply nominal lambda 100 is lambda-equivalent about 12.5 on that public path unless corrected. This is source-level algebra, not proof about unreleased paper-table code.
- Public CPO bookkeeping is dense in mask tensors even though protected coordinates are sparse: dense bool masks + float32 references + int64 flat indices.
- Qwen3-VL-4B public immutable revision `ebb281ec70b05090aa6165b016eac8ec08e71b17` serializes the tied text matrix once, while Transformers 4.57.3 re-ties the output head after load. CPO then expands the runtime `state_dict()` mask namespace beyond the serialized checkpoint namespace.
- The tied matrix is `151936 × 2560 = 388,956,160` scalars. If the alias is the only extra floating runtime key, public CPO's logical scalar denominator is 4,826,771,968 vs 4,437,815,808 physical parameters, an 8.764585% inflation.
- Source-equivalent tied fixture established that canonical and dead-alias masks/refs are value-identical but separately allocated/serialized; the alias therefore duplicates real payload and top-k build work.
- **Mask-lifetime source result:** after public trainer derives `_mask_flat_idx = mask.nonzero()`, dense bool mask values are never used again. `importance_mask` is retained only for key membership and `len()` logging; the regularizer uses indices + refs. A keyset/index-only repair can release dense masks without changing the tested regularizer algebra.
- **Executed 10%-support equivalence:** on a 760k-scalar source-equivalent fixture, dropping dense masks reduced logical trainer auxiliary tensor bytes from 1,672,000 to 912,000 (**45.45%**) while ZeRO-2-style and simulated world-size-8 ZeRO-3 masked algebra remained exactly equal under torch 2.10.0+cpu.
- **New process-level streaming result:** on 100M synthetic scalars at 10% support, release-like index materialization peaked at **503.90 MB RSS** with 220,000,000 final logical aux bytes; converting masks smallest-first and releasing each dense bool immediately peaked at **446.73 MB** with 120,000,000 final logical aux bytes, a measured **57.16 MB / 11.34% peak-RSS reduction** and exact **45.45% steady tensor-byte reduction**. No explicit `gc.collect()` was needed and conversion was not slower in this CPU run.
- At ~33.3% support over 50M scalars, the same streaming repair reduced peak RSS **532.22→506.08 MB** and final logical aux bytes **250,000,040→200,000,040**. High support remains dominated by indices+refs.
- **Representation frontier:** with 2M scalars, dense mask+refs and int64-index+refs archives break even at 12.5% support exactly as raw-byte algebra predicts. Int32 local-index+refs breaks even against dense at 25%; local torch 2.10 indexing/partition tests matched int64 at tested 10% and 35%, but PyTorch 2.8 + DeepSpeed compatibility is unverified. Bit-packed mask+refs was smallest at the public 10% regime in the storage benchmark.
- **Conditional Qwen3-VL-4B 10%-support projection:** over the canonical physical namespace, current dense-mask+fp32-ref+int64-index trainer auxiliary payload would be ~9.093 GiB; canonical filtering + mask-drop with int64 indices would be ~4.960 GiB; int32 indices, if later validated, ~3.306 GiB. These are representation projections, not RSS measurements; real mask-domain/support remains unmeasured.
- The public 4B GRPO path sets vision tower, LLM and merger all unfrozen, making broad movement plausible but not proving full 10% nonzero support per tensor.
- Direct Qwen3-VL `v4.57.3` model source registers the observed rotary `inv_freq` buffers with `persistent=False`; inherited/base-module runtime state still needs verification.
- Exact-storage/view dedup remains unsafe because distinct `nn.Parameter` objects may share identical or overlapping storage and stay separately trainer-visible.
- **Current safest repair order:** (1) fail-closed canonical trainer-namespace filtering; (2) streaming derive-indices-and-release-dense-mask lifetime repair; (3) measure real support before choosing packed/sparse/hybrid persistent format; (4) test int32 local indices only under PyTorch 2.8 + DeepSpeed with fail-closed range checks; (5) separately correct/validate distributed regularizer scaling.
- New durable results: `CPO_MASK_STREAMING_LOAD_RESULT_20260828T090540_JST.json` and `CPO_MASK_REPRESENTATION_RESULT_20260828T090326_JST.json`.

Exact CPO continuation:
1. Re-run canonical namespace + streaming mask-drop + int32-index fixtures under PyTorch 2.8.0 when a compatible runtime can be acquired; preserve executable/environment/output hashes.
2. Validate the streaming loader on public trainer dependencies/ZeRO-2/3, then on a smallest loadable Transformers 4.57.3 tied-weight model and Qwen3-VL-4B if resources permit.
3. Measure real Qwen3-VL physical/state_dict/trainer-effective scalar counts, canonical mask-domain size, actual support/overlap, `task_k.pt` bytes, initial/conversion/steady RSS, index-conversion time and mask-build wall time.
4. Choose/test dense-packed vs sparse-index vs per-tensor hybrid persistence from measured cumulative support; separately test int32 local-index compatibility.
5. Profile per-step index/ref device-copy overhead under ZeRO-2/3 and execute single-rank reference vs current owner-only ZeRO-3 vs world-size-corrected regularization; then the full selection × normalization × DP-scaling paired-seed factorial.
6. Continue read-only first-party provenance search for paper-table mask/scaling semantics.

Current deterministic DeMix/OpenCompass reconstruction tools and anchors remain unchanged from the predecessor checkpoint. Track A1 still requires a fully hashed shared Python 3.10 `.[full]` dependency environment; environment acquisition limits are not evidence about OpenCompass.

Remaining frontier:
- PyTorch-2.8/DeepSpeed and real-model validation of canonical namespace + streaming mask-drop + optional int32 local indices.
- Real Qwen3-VL CPO support/file/RSS/build/runtime measurements and physical-vs-effective accounting.
- Packed/sparse/hybrid mask representation after real support is known.
- Distributed regularizer scaling and expanded quality factorial.
- Historical paper-table provenance.
- DeMix/OpenCompass Track A1 when the required environment is available.
- Remaining DeMix checkpoint metadata byte-identity classes and orphan `mix_16` lineage.
- Matched merge-vs-retrain displacement sweep, SAFE-Merge and earlier continual-learning branches, preserving exact tested scope and clean independence.
