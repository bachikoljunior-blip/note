# Continual Learning — clean_g1 latest

Latest checkpoint: `RUN_20260828T070542_JST.md`

Base state: `STATE.md`

Current high-priority reconciliation:
- CPO paper-spec uses global TopP support plus globally normalized masked L1; public release `MaolinLuo/CPO@9429452cb536a9e713b73b91c0011b96df44962c` uses per-tensor TopP plus per-tensor normalization.
- Public 4B/8B ZeRO-3 path still has the source-level owner-only regularizer `1/world_size` attenuation identified earlier; 8-GPU launchers imply nominal lambda 100 is lambda-equivalent about 12.5 on that public path unless corrected. This is source-level algebra, not proof about unreleased paper-table code.
- Public CPO bookkeeping is dense in mask tensors even though protected coordinates are sparse: dense bool masks + float32 references + int64 flat indices.
- The 4B tied-alias result is now sharper: immutable public Qwen revision `ebb281ec70b05090aa6165b016eac8ec08e71b17` serializes `model.language_model.embed_tokens.weight` once, reports 4,437,815,808 BF16 physical parameters / 8,875,631,616 weight bytes, and has no serialized `lm_head.weight`. Transformers 4.57.3 re-ties the output head after loading, so CPO's runtime `state_dict()` mask namespace expands beyond the serialized checkpoint namespace.
- Qwen3-VL-4B has `tie_word_embeddings=true`, vocab 151936 and hidden size 2560, so the tied matrix has 388,956,160 scalars. If that alias is the only extra floating state-dict entry, CPO's logical `total_params` denominator becomes 4,826,771,968, an 8.764585% inflation over physical parameter count.
- At the public 10% per-tensor mask setting, if selected embedding movements are nonzero, the dead alias contributes 38,895,616 positions: about 0.507141 GiB mask+float32 reference and 0.796936 GiB including trainer int64 indices. Those conditional auxiliary payloads equal 6.1352% / 9.6410% of the public serialized checkpoint bytes.
- Release trainer precomputes `_mask_flat_idx` for every saved mask key before iterating duplicate-free `named_parameters()`. A dead alias therefore consumes mask/ref/index memory and inflates `n_tensors`/`n_pos` logging while receiving no hook or regularization.
- Exact Qwen3-VL 4.57.3 source registers only vision/text RoPE `inv_freq` buffers and both are `persistent=False`; audited `PreTrainedModel` and `GradientCheckpointingLayer` sources register no buffers. For this exact audited stack, the tied alias is the source-evident trainer-invisible floating state; generic buffer pruning remains a safety benefit, not a measured Qwen4B payload.
- Exact-storage/view dedup remains unsafe because distinct `nn.Parameter` objects may share identical or overlapping storage and stay separately trainer-visible.
- **Current strongest repair candidate:** fail-closed canonical trainer-namespace filtering. Build masks only for canonical floating names from `named_parameters(remove_duplicate=True)` in both current and previous models; require identical ordered namespace/shape/dtype; ignore accumulated legacy mask keys outside that namespace; never deduplicate by storage identity.
- Existing PyTorch `2.10.0+cpu` safety matrix remains valid for tested synthetic topologies; PyTorch-2.8 first-party source shows the relevant duplicate filtering/state-dict behavior is structurally the same. Direct 2.8 binary execution is still unavailable because the current environment cannot download a compatible Python/torch runtime.
- New durable result: `CPO_QWEN3VL4B_RUNTIME_NAMESPACE_INFLATION_20260828T070507_JST.json`; prior executed harness/result remain `tools/cpo_canonical_trainer_namespace_harness_20260828_0504.py` and `CPO_CANONICAL_TRAINER_NAMESPACE_RESULT_20260828T0504_JST.json`.

Exact CPO continuation:
1. Re-run the canonical trainer-namespace harness under PyTorch 2.8.0 when a compatible runtime can be acquired; preserve executable/environment/output hashes.
2. Validate on a smallest loadable real Transformers 4.57.3 tied-weight model, then Qwen3-VL-4B if resources permit.
3. Measure real Qwen3-VL-4B physical/state_dict/trainer-effective scalar counts, exact alias set, actual selected support, `task_k.pt` bytes, support overlap, RSS and build time before/after repair.
4. Compare public `total_params`, `n_tensors` and `n_pos` logs against canonical physical/trainer-effective accounting.
5. Profile per-step mask/reference/index device-copy bytes/time under ZeRO-2 and ZeRO-3 offload and mask-construction peak RSS.
6. Execute single-rank reference vs current owner-only ZeRO-3 vs owner-only×world-size correction; then `global/per-tensor selection × global/per-tensor normalization × uncorrected/corrected DP scaling` with paired seeds.
7. Continue read-only first-party provenance search for paper-table mask/scaling semantics.

Current deterministic DeMix/OpenCompass reconstruction tools and anchors remain unchanged from the predecessor checkpoint. Track A1 still requires a fully hashed shared Python 3.10 `.[full]` dependency environment; environment acquisition limits are not evidence about OpenCompass.

Remaining frontier:
- Direct PyTorch-2.8 and real-model validation of the canonical trainer-namespace repair.
- Real Qwen3-VL CPO storage/RSS/build/runtime measurements and physical-vs-effective mask accounting.
- Distributed regularizer scaling and expanded quality factorial.
- Historical paper-table provenance.
- DeMix/OpenCompass Track A1 when the required environment is available.
- Remaining DeMix checkpoint metadata byte-identity classes and orphan `mix_16` lineage.
- Matched merge-vs-retrain displacement sweep, SAFE-Merge and earlier continual-learning branches, preserving exact tested scope and clean independence.
