# Continual Learning — clean_g1 latest

Latest checkpoint: `RUN_20260828T0303_JST.md`

Base state: `STATE.md`

Current high-priority reconciliation:
- CPO paper-spec uses global TopP support plus globally normalized masked L1; public release `MaolinLuo/CPO@9429452cb536a9e713b73b91c0011b96df44962c` uses per-tensor TopP plus per-tensor normalization.
- Public 4B/8B ZeRO-3 path still has the source-level owner-only regularizer `1/world_size` attenuation identified earlier; 8-GPU launchers imply nominal lambda 100 is lambda-equivalent about 12.5 on that public path unless corrected. This is source-level algebra, not proof about unreleased paper-table code.
- Public CPO bookkeeping is dense in mask tensors even though protected coordinates are sparse: dense bool masks + float32 references + int64 flat indices.
- **New executed tied-alias result:** a deterministic source-equivalent tied-embedding harness confirms that `state_dict()` exposes both `model.embed_tokens.weight` and tied `lm_head.weight`, while `named_parameters()` consumes only the first physical parameter name. The public-builder pattern therefore saves a dead `lm_head` mask/ref/index entry when the tied embedding moves.
- Tiny fixture (8192×128 tied matrix, 10% TopP): public-builder mask file `2,961,933` bytes vs exact-storage-dedup control `1,493,411` bytes; persistent logical trainer auxiliary payload `4,649,760` vs `2,342,900` bytes. The trainer-consumed masks and references are bitwise equal between baseline and dedup.
- Durable measurement: `CPO_TIED_ALIAS_HARNESS_RESULT_20260828T0303_JST.json`; harness: `tools/cpo_tied_alias_harness_20260828.py`.
- Public Qwen3-VL-4B config remains tied (`vocab_size=151936`, hidden `2560`). If the embedding moves and all 10% selections are nonzero, the dead alias projects to `544,538,624` logical bytes in mask+ref and `855,703,552` logical persistent trainer auxiliary bytes. Full-Qwen file/RSS values remain unmeasured.
- Previous whole-model/full-mask-domain scenarios remain scenarios, not measured actual production memory.
- Reference anchoring to the immediately previous task checkpoint remains aligned between paper practical objective and release; not a discrepancy.

Exact CPO continuation:
1. Repeat the tied fixture under PyTorch 2.8 and, if resources permit, a smallest loadable public Qwen3-VL tied path; compare exact builder/trainer namespaces and serialized bytes.
2. Harden exact-storage dedup against non-identical shared-storage views and registration-order variants; require trainer-effective mask/ref invariance.
3. Measure real Qwen3-VL-4B physical/state_dict/mask-file/trainer-effective scalar counts, `task_k.pt` bytes, support overlap, RSS and build time.
4. Profile per-step mask/reference/index device-copy bytes/time under ZeRO-2 and ZeRO-3 offload and mask-construction peak RSS.
5. Execute single-rank reference vs current owner-only ZeRO-3 vs owner-only×world-size correction; then `global/per-tensor selection × global/per-tensor normalization × uncorrected/corrected DP scaling` with paired seeds.
6. Continue read-only first-party provenance search for paper-table mask/scaling semantics.

Current deterministic DeMix/OpenCompass reconstruction tools and anchors remain unchanged from the predecessor checkpoint. Track A1 still requires a fully hashed shared Python 3.10 `.[full]` dependency environment; environment acquisition limits are not evidence about OpenCompass.

Remaining frontier:
- CPO full-model tied-alias measurement and safe storage-dedup repair.
- CPO real memory/storage/runtime, physical-vs-effective mask accounting and distributed scaling measurements.
- CPO expanded quality factorial and historical paper-table provenance.
- DeMix/OpenCompass Track A1 when the required environment is available.
- Remaining DeMix checkpoint metadata byte-identity classes and orphan `mix_16` lineage.
- Matched merge-vs-retrain displacement sweep, SAFE-Merge and earlier continual-learning branches, preserving exact tested scope and clean independence.
