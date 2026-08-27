# Continual Learning — clean_g1 latest

Latest checkpoint: `RUN_20260828T0506_JST.md`

Base state: `STATE.md`

Current high-priority reconciliation:
- CPO paper-spec uses global TopP support plus globally normalized masked L1; public release `MaolinLuo/CPO@9429452cb536a9e713b73b91c0011b96df44962c` uses per-tensor TopP plus per-tensor normalization.
- Public 4B/8B ZeRO-3 path still has the source-level owner-only regularizer `1/world_size` attenuation identified earlier; 8-GPU launchers imply nominal lambda 100 is lambda-equivalent about 12.5 on that public path unless corrected. This is source-level algebra, not proof about unreleased paper-table code.
- Public CPO bookkeeping is dense in mask tensors even though protected coordinates are sparse: dense bool masks + float32 references + int64 flat indices.
- Tied-alias dead bookkeeping is real in the tested source-equivalent fixtures because `state_dict()` exposes tied names while the trainer consumes the duplicate-free canonical `named_parameters()` namespace.
- Exact-storage/view dedup is not safe in general because distinct `nn.Parameter` objects may share identical or overlapping storage and remain separately trainer-visible.
- **Current strongest repair candidate:** fail-closed canonical trainer-namespace filtering. Build masks only for canonical floating names from `named_parameters(remove_duplicate=True)` in both current and previous models; require identical ordered namespace/shape/dtype; ignore accumulated legacy mask keys outside that namespace; never deduplicate by storage identity.
- New executed safety matrix under PyTorch `2.10.0+cpu` covers tied aliases in both registration orders, distinct exact-shared-storage Parameters, overlapping shared-storage views, persistent floating buffers and untied controls. For every trainer-consumed canonical parameter, repaired masks and reference weights were bitwise equal to release-style computation; dead aliases/buffers were removed and structural mismatches failed closed.
- Durable result: `CPO_CANONICAL_TRAINER_NAMESPACE_RESULT_20260828T0504_JST.json`; harness: `tools/cpo_canonical_trainer_namespace_harness_20260828_0504.py`.
- Public Qwen3-VL-4B full-model file/RSS and actual buffer overhead remain unmeasured.

Exact CPO continuation:
1. Re-run the canonical trainer-namespace harness under PyTorch 2.8.0 and preserve output hash/runtime details.
2. Validate on a smallest loadable real Transformers tied-weight model, then Qwen3-VL-4B if resources permit.
3. Measure real Qwen3-VL-4B physical/state_dict/trainer-effective scalar counts, dead aliases/buffers, `task_k.pt` bytes, support overlap, RSS and build time before/after repair.
4. Profile per-step mask/reference/index device-copy bytes/time under ZeRO-2 and ZeRO-3 offload and mask-construction peak RSS.
5. Execute single-rank reference vs current owner-only ZeRO-3 vs owner-only×world-size correction; then `global/per-tensor selection × global/per-tensor normalization × uncorrected/corrected DP scaling` with paired seeds.
6. Continue read-only first-party provenance search for paper-table mask/scaling semantics.

Current deterministic DeMix/OpenCompass reconstruction tools and anchors remain unchanged from the predecessor checkpoint. Track A1 still requires a fully hashed shared Python 3.10 `.[full]` dependency environment; environment acquisition limits are not evidence about OpenCompass.

Remaining frontier:
- CPO PyTorch-2.8/real-model canonical trainer-namespace validation.
- CPO real memory/storage/runtime, physical-vs-effective mask accounting and distributed scaling measurements.
- CPO expanded quality factorial and historical paper-table provenance.
- DeMix/OpenCompass Track A1 when the required environment is available.
- Remaining DeMix checkpoint metadata byte-identity classes and orphan `mix_16` lineage.
- Matched merge-vs-retrain displacement sweep, SAFE-Merge and earlier continual-learning branches, preserving exact tested scope and clean independence.
