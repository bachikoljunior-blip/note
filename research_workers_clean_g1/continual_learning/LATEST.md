# Continual Learning — clean_g1 latest

Latest checkpoint: `RUN_20260828T0406_JST.md`

Base state: `STATE.md`

Current high-priority reconciliation:
- CPO paper-spec uses global TopP support plus globally normalized masked L1; public release `MaolinLuo/CPO@9429452cb536a9e713b73b91c0011b96df44962c` uses per-tensor TopP plus per-tensor normalization.
- Public 4B/8B ZeRO-3 path still has the source-level owner-only regularizer `1/world_size` attenuation identified earlier; 8-GPU launchers imply nominal lambda 100 is lambda-equivalent about 12.5 on that public path unless corrected. This is source-level algebra, not proof about unreleased paper-table code.
- Public CPO bookkeeping is dense in mask tensors even though protected coordinates are sparse: dense bool masks + float32 references + int64 flat indices.
- The tied-alias dead-bookkeeping result remains valid: `state_dict()` can expose both tied names while the trainer consumes only the canonical duplicate-free `named_parameters()` name.
- **Repair correction:** exact-storage/view dedup is not generally safe. A deterministic counterexample with two distinct `nn.Parameter` objects sharing the exact same storage/view shows storage dedup drops one parameter even though `named_parameters(remove_duplicate=True)` and the CPO trainer consume both.
- A safer release-preserving repair is to build masks only for the canonical floating parameter names from `named_parameters(remove_duplicate=True)` in both current and previous models, with fail-closed namespace/shape/dtype checks. This also removes changed persistent floating buffers that the public trainer can never consume.
- Durable result: `CPO_TRAINER_NAMESPACE_FILTER_RESULT_20260828T0405_JST.json`; harness: `tools/cpo_trainer_namespace_filter_harness_20260828.py`.
- The previous exact-storage-dedup control is retained as a tied-alias diagnostic only, not as the production repair candidate.
- Public Qwen3-VL-4B remains tied (`vocab_size=151936`, hidden `2560`); full-Qwen file/RSS and actual buffer overhead remain unmeasured.

Exact CPO continuation:
1. Implement and validate the fail-closed canonical trainer-namespace filter across tied aliases, registration-order variants, distinct shared-storage Parameters, non-identical shared-storage views, persistent buffers and untied controls.
2. Repeat the safety harness under PyTorch 2.8.0; then, if resources permit, a smallest loadable public Qwen3-VL tied path and Qwen3-VL-4B.
3. Measure real Qwen3-VL-4B physical/state_dict/trainer-effective scalar counts, dead aliases/buffers, `task_k.pt` bytes, support overlap, RSS and build time.
4. Profile per-step mask/reference/index device-copy bytes/time under ZeRO-2 and ZeRO-3 offload and mask-construction peak RSS.
5. Execute single-rank reference vs current owner-only ZeRO-3 vs owner-only×world-size correction; then `global/per-tensor selection × global/per-tensor normalization × uncorrected/corrected DP scaling` with paired seeds.
6. Continue read-only first-party provenance search for paper-table mask/scaling semantics.

Current deterministic DeMix/OpenCompass reconstruction tools and anchors remain unchanged from the predecessor checkpoint. Track A1 still requires a fully hashed shared Python 3.10 `.[full]` dependency environment; environment acquisition limits are not evidence about OpenCompass.

Remaining frontier:
- CPO canonical trainer-namespace repair and PyTorch-2.8/full-Qwen validation.
- CPO real memory/storage/runtime, physical-vs-effective mask accounting and distributed scaling measurements.
- CPO expanded quality factorial and historical paper-table provenance.
- DeMix/OpenCompass Track A1 when the required environment is available.
- Remaining DeMix checkpoint metadata byte-identity classes and orphan `mix_16` lineage.
- Matched merge-vs-retrain displacement sweep, SAFE-Merge and earlier continual-learning branches, preserving exact tested scope and clean independence.
