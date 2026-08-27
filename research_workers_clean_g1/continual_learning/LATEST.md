# Continual Learning — clean_g1 latest

Latest checkpoint: `RUN_20260828T0203_JST.md`

Base state: `STATE.md`

Current high-priority reconciliation:
- CPO paper-spec uses global TopP support plus globally normalized masked L1.
- Public release at `MaolinLuo/CPO@9429452cb536a9e713b73b91c0011b96df44962c` uses per-tensor TopP plus per-tensor normalization.
- Source-locked executable equivalence remains in `tools/cpo_release_equivalence_harness_20260828.py` / `CPO_RELEASE_EQUIVALENCE_RESULT_20260828.json`.
- Public 4B/8B ZeRO-3 path still has the source-level `1/world_size` owner-only regularizer attenuation identified in `RUN_20260828T0011_JST.md`; public 8-GPU launchers imply nominal lambda 100 is lambda-equivalent about 12.5 on that release path unless corrected. This is source-level algebra, not a live 8-GPU reproduction or proof about unreleased paper-table code.
- Public CPO bookkeeping is sparse in protected coordinates but dense in masks. `CLGRPOTrainer` persistently retains dense bool masks, float32 protected references and int64 flat indices. For a trainer-visible mask-domain scalar count `N` and accumulated support `u`, logical persistent auxiliary tensor payload is `N + 12uN` bytes, excluding Python/serialization/transient overhead.
- **New tied-alias correction:** public Qwen3-VL-4B-Instruct has tied input/output embeddings. CPO's mask builder traverses `state_dict()` aliases while the trainer traverses `named_parameters(remove_duplicate=true)`. Therefore the builder can persist an `lm_head.weight` mask/ref/index entry that the trainer never consumes. For the 151936×2560 tied matrix, if the embedding moves and the full top-10% alias mask is nonzero, that dead alias is about 0.507 GiB in the current mask file and 0.797 GiB in persistent trainer auxiliary tensors. This does not apply to public Qwen3-VL-8B-Instruct, where embeddings are untied.
- Durable alias calculation artifact: `CPO_TIED_ALIAS_MODEL_20260828T0203_JST.json`.
- Real accounting must now separate physical unique scalars, mask-builder `state_dict()` scalars/keys, mask-file scalars/keys after filtering+union, and trainer-effective deduplicated `named_parameters()` scalars/keys.
- Previous whole-model/full-mask-domain scenarios remain scenarios rather than measured actual mask-domain memory: one 10% mask was about 9.09 GiB for 4B and 17.96 GiB for 8B; independent four-mask union (`u=34.39%`) about 21.19/41.86 GiB. Tied aliases can add dead bookkeeping on top for tied configurations.
- Mask construction retains current state dict while loading the previous full state dict, so two BF16 weight payloads can coexist; actual peak RSS remains unmeasured.
- Reference anchoring is not a discrepancy: both paper practical objective and release anchor cumulative protected support to the immediately previous task checkpoint.

Exact CPO continuation:
1. Run the smallest faithful tied-embedding CPO case and measure input-embedding/`lm_head` storage alias identity, builder `float_keys`/`total_params`, duplicate mask presence, exact `task_k.pt` bytes and trainer-visible `named_parameters()` keys.
2. Add a storage-deduplicated mask-builder control that preserves the same trainer-effective physical protected set; compare file bytes, RSS, build time and behavior.
3. Measure real physical/state_dict/mask-file/trainer-effective mask-domain counts, per-task new support, cumulative union/overlap and actual `task_k.pt` bytes.
4. Profile trainer CPU RSS and per-step device-copy bytes/time under ZeRO-2 and ZeRO-3 offload; measure mask-construction peak RSS/wall time.
5. Execute single-rank reference vs current owner-only ZeRO-3 vs owner-only×world-size correction; then expand to `global/per-tensor selection × global/per-tensor normalization × uncorrected/corrected DP scaling` with paired seeds.
6. Continue read-only first-party provenance search for paper-table mask/scaling semantics.

Current deterministic DeMix/OpenCompass reconstruction tools and anchors remain unchanged from the predecessor checkpoint. Track A1 still requires a fully hashed shared Python 3.10 `.[full]` dependency environment; environment acquisition limits are not evidence about OpenCompass.

Remaining frontier:
- CPO tied-alias dead-bookkeeping measurement/deduplication.
- CPO real memory/storage/runtime, physical-vs-effective mask accounting and distributed scaling measurements.
- CPO expanded quality factorial and historical paper-table provenance.
- DeMix/OpenCompass Track A1 when the required environment is available.
- Remaining DeMix checkpoint metadata byte-identity classes and orphan `mix_16` lineage.
- Matched merge-vs-retrain displacement sweep, SAFE-Merge and earlier continual-learning branches, preserving exact tested scope and clean independence.
