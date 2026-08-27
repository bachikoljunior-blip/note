# Continual Learning — clean_g1 latest

Latest checkpoint: `RUN_20260828T0605_JST.md`

Base state: `STATE.md`

Current high-priority reconciliation:
- CPO paper-spec uses global TopP support plus globally normalized masked L1; public release `MaolinLuo/CPO@9429452cb536a9e713b73b91c0011b96df44962c` uses per-tensor TopP plus per-tensor normalization.
- Public 4B/8B ZeRO-3 path still has the source-level owner-only regularizer `1/world_size` attenuation identified earlier; 8-GPU launchers imply nominal lambda 100 is lambda-equivalent about 12.5 on that public path unless corrected. This is source-level algebra, not proof about unreleased paper-table code.
- Public CPO bookkeeping is dense in mask tensors even though protected coordinates are sparse: dense bool masks + float32 references + int64 flat indices.
- Tied-alias dead bookkeeping is now supported by a first-party source chain for the exact public CPO 4B stack: CPO's mask builder uses `state_dict()`, PyTorch 2.8 `state_dict()` preserves registered aliases while duplicate-free `named_parameters()` suppresses repeated Parameter objects, and Transformers 4.57.3 explicitly re-ties input/output embeddings after `from_pretrained` loading when `tie_word_embeddings=true`.
- Public CPO 4B launcher names `Qwen/Qwen3-VL-4B-Instruct` and fixes a 10% mask. Public Qwen3-VL-4B-Instruct config reports `tie_word_embeddings=true`, vocab 151936 and hidden size 2560. Conditional 10%-support logical dead-alias payload is about 0.507 GiB for mask+float32 refs and 0.797 GiB including trainer int64 indices; these are not file/RSS measurements and support can be smaller if top movements are zero.
- Exact-storage/view dedup is not safe in general because distinct `nn.Parameter` objects may share identical or overlapping storage and remain separately trainer-visible.
- **Current strongest repair candidate:** fail-closed canonical trainer-namespace filtering. Build masks only for canonical floating names from `named_parameters(remove_duplicate=True)` in both current and previous models; require identical ordered namespace/shape/dtype; ignore accumulated legacy mask keys outside that namespace; never deduplicate by storage identity.
- The existing PyTorch `2.10.0+cpu` safety matrix remains valid for the tested synthetic topologies. Exact PyTorch-2.8 first-party source shows the relevant `_named_members` duplicate filtering and `_save_to_state_dict` behavior is structurally the same, narrowing version risk but not replacing a direct 2.8 runtime run.
- Durable source-chain result: `CPO_QWEN3VL4B_TIED_ALIAS_SOURCE_CHAIN_20260828T0605_JST.json`; prior executed harness/result remain `tools/cpo_canonical_trainer_namespace_harness_20260828_0504.py` and `CPO_CANONICAL_TRAINER_NAMESPACE_RESULT_20260828T0504_JST.json`.
- The public repository exposes no pre-release implementation history for `compute_importance_mask.py`: its public file history starts at the July 29 CPO release commit, so paper-table mask/scaling semantics still cannot be recovered from earlier public code there.

Exact CPO continuation:
1. Re-run the canonical trainer-namespace harness under PyTorch 2.8.0 when a compatible runtime can be acquired; preserve executable/environment/output hashes.
2. Validate on a smallest loadable real Transformers 4.57.3 tied-weight model, then Qwen3-VL-4B if resources permit.
3. Measure real Qwen3-VL-4B physical/state_dict/trainer-effective scalar counts, exact canonical embedding path, dead aliases/buffers, actual selected support, `task_k.pt` bytes, support overlap, RSS and build time before/after repair.
4. Profile per-step mask/reference/index device-copy bytes/time under ZeRO-2 and ZeRO-3 offload and mask-construction peak RSS.
5. Execute single-rank reference vs current owner-only ZeRO-3 vs owner-only×world-size correction; then `global/per-tensor selection × global/per-tensor normalization × uncorrected/corrected DP scaling` with paired seeds.
6. Continue read-only first-party provenance search for paper-table mask/scaling semantics.

Current deterministic DeMix/OpenCompass reconstruction tools and anchors remain unchanged from the predecessor checkpoint. Track A1 still requires a fully hashed shared Python 3.10 `.[full]` dependency environment; environment acquisition limits are not evidence about OpenCompass.

Remaining frontier:
- Direct PyTorch-2.8 and real-model validation of the canonical trainer-namespace repair.
- Real Qwen3-VL CPO storage/RSS/build/runtime measurements and physical-vs-effective mask accounting.
- Distributed regularizer scaling and expanded quality factorial.
- Historical paper-table provenance.
- DeMix/OpenCompass Track A1 when the required environment is available.
- Remaining DeMix checkpoint metadata byte-identity classes and orphan `mix_16` lineage.
- Matched merge-vs-retrain displacement sweep, SAFE-Merge and earlier continual-learning branches, preserving exact tested scope and clean independence.
