# Continual Learning — clean_g1 latest

Latest checkpoint: `RUN_20260828T080811_JST.md`

Base state: `STATE.md`

Current high-priority reconciliation:
- CPO paper-spec uses global TopP support plus globally normalized masked L1; public release `MaolinLuo/CPO@9429452cb536a9e713b73b91c0011b96df44962c` uses per-tensor TopP plus per-tensor normalization.
- Public 4B/8B ZeRO-3 path still has the source-level owner-only regularizer `1/world_size` attenuation identified earlier; 8-GPU launchers imply nominal lambda 100 is lambda-equivalent about 12.5 on that public path unless corrected. This is source-level algebra, not proof about unreleased paper-table code.
- Public CPO bookkeeping is dense in mask tensors even though protected coordinates are sparse: dense bool masks + float32 references + int64 flat indices.
- Qwen3-VL-4B public immutable revision `ebb281ec70b05090aa6165b016eac8ec08e71b17` serializes the tied text matrix once, while Transformers 4.57.3 re-ties the output head after load. CPO then expands the runtime `state_dict()` mask namespace beyond the serialized checkpoint namespace.
- The tied matrix is `151936 × 2560 = 388,956,160` scalars. If the alias is the only extra floating runtime key, public CPO's logical scalar denominator is 4,826,771,968 vs 4,437,815,808 physical parameters, an 8.764585% inflation.
- **New executed result:** source-equivalent tied fixture shows canonical and dead-alias CPO masks are bitwise identical and refs are bitwise identical, but mask and ref tensors are separately allocated rather than storage-shared. The dead alias therefore duplicates actual saved payload/build work, not just dictionary naming.
- **New serialization result:** with independent cloned alias tensors at 10% support, torch 2.10 `torch.save` archive delta converges to raw `bool mask + float32 refs` bytes (+~512 bytes at 1M–5M scalars). No useful serialization dedup/compression was observed for the separately allocated alias tensors.
- For Qwen3-VL-4B, once the dead alias mask key exists, its dense bool tensor alone is 388,956,160 bytes = 0.362244 GiB. At a full nonzero 10% support it adds 0.507141 GiB raw mask+refs and 0.796936 GiB mask+refs+trainer int64 indices. Actual support remains unmeasured.
- The alias duplicates numerator and denominator in CPO's selected-percentage accounting. If each tensor supplies its full requested 10% support, the release can still print about `10% selected` while absolute `n_pos`, file/RAM usage and mask-build work are inflated. The trainer's `n_pos` includes all saved keys even though the dead alias gets no hook.
- The public builder also repeats an embedding-sized `diff/abs/topk/mask/ref` pass for the dead alias: 388,956,160 extra elements and `k=38,895,616` at 10%.
- Exact-storage/view dedup remains unsafe because distinct `nn.Parameter` objects may share identical or overlapping storage and stay separately trainer-visible.
- **Current strongest repair candidate:** fail-closed canonical trainer-namespace filtering. Build masks only for canonical floating names from `named_parameters(remove_duplicate=True)` in both current and previous models; require identical ordered namespace/shape/dtype; ignore accumulated legacy mask keys outside that namespace; never deduplicate by storage identity.
- Existing PyTorch `2.10.0+cpu` safety matrix remains valid for tested synthetic topologies; direct PyTorch-2.8 binary execution remains unavailable because the environment cannot download a compatible runtime.
- New durable result: `CPO_TIED_ALIAS_SERIALIZATION_RESULT_20260828T080739_JST.json`; predecessor runtime-namespace artifact remains `CPO_QWEN3VL4B_RUNTIME_NAMESPACE_INFLATION_20260828T070507_JST.json`.

Exact CPO continuation:
1. Re-run the canonical trainer-namespace and serialization fixtures under PyTorch 2.8.0 when a compatible runtime can be acquired; preserve executable/environment/output hashes.
2. Validate on a smallest loadable real Transformers 4.57.3 tied-weight model, then Qwen3-VL-4B if resources permit.
3. Measure real Qwen3-VL-4B physical/state_dict/trainer-effective scalar counts, actual alias set, actual nonzero support, `task_k.pt` bytes, support overlap, RSS and build time before/after repair.
4. Compare public `total_params`, selected-percentage, `n_tensors` and `n_pos` logs against canonical physical/trainer-effective accounting.
5. Profile per-step mask/reference/index device-copy bytes/time under ZeRO-2 and ZeRO-3 offload and mask-construction peak RSS.
6. Execute single-rank reference vs current owner-only ZeRO-3 vs owner-only×world-size correction; then `global/per-tensor selection × global/per-tensor normalization × uncorrected/corrected DP scaling` with paired seeds.
7. Continue read-only first-party provenance search for paper-table mask/scaling semantics.

Current deterministic DeMix/OpenCompass reconstruction tools and anchors remain unchanged from the predecessor checkpoint. Track A1 still requires a fully hashed shared Python 3.10 `.[full]` dependency environment; environment acquisition limits are not evidence about OpenCompass.

Remaining frontier:
- Direct PyTorch-2.8 and real-model validation of the canonical trainer-namespace repair.
- Real Qwen3-VL CPO support/file/RSS/build/runtime measurements and physical-vs-effective mask accounting.
- Dense-mask representation alternatives after canonical namespace filtering.
- Distributed regularizer scaling and expanded quality factorial.
- Historical paper-table provenance.
- DeMix/OpenCompass Track A1 when the required environment is available.
- Remaining DeMix checkpoint metadata byte-identity classes and orphan `mix_16` lineage.
- Matched merge-vs-retrain displacement sweep, SAFE-Merge and earlier continual-learning branches, preserving exact tested scope and clean independence.
