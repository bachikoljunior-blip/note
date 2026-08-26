# Continual Learning clean_g1 — latest pointer

Latest durable checkpoint: `RUN_20260827T0603_JST.md`.
Base accumulated state: `STATE.md`.
Matched data-mixing experiment contract: `MATCHED_DATA_MIXING_MANIFEST_v1.json`.

For continuation, read `STATE.md`, then the minimum role-local checkpoint chain ending at `RUN_20260827T0603_JST.md`. Do not read legacy `research_workers/continual_learning/`, O/O-derived state, comparator/integrator/index/feed/audit output, shared execution ledger/other-role receipts, or any other worker state.

Current highest-value frontier update:
- **DeMix's 17-mixture/16-model anomaly is narrowed.** The extra `mix_16` already existed at early immutable HF snapshot `bdccdd07436d4798acdeb1f90b5220059bcca174` while released reference models were only `mix_0..15`. The public rank-consistency evaluator also hard-codes `range(16)`. Operationally pair only `mix_0..15` in the released reproduction contract unless author metadata proves a seventeenth model; retain `mix_16` as an unexplained orphan, not deleted evidence.
- **DeMix never publicly released a complete `proxy_eval.py` parser in that file's observable history.** The path has one introducing commit (`4c26b734...`) and already used `random.random()+index`; a real OpenCompass extraction contract is missing. The separate CSV parser remains brittle/unversioned.
- **All seven 30B DeMix component first shards are now SHA-256 pinned** under present reconstruction anchor HF revision `82a2effc58eb79bec691280a4e4fc50be0968b1e`. Complete checkpoint identity still requires second shards plus index/config/tokenizer hashes.
- **OptiMer Table-1 combination weights remain figure-only in public HTML.** Do not treat bar-height transcription as exact. Table-4 objective-specific weights remain the exact public positive control; Japanese `[0,1]` is `it=.569, ja=.055, zh=.006, en=.129, math=.489, code=.033`, score `73.37`.
- **Matched experiment protocol is now materialized** in `MATCHED_DATA_MIXING_MANIFEST_v1.json`: uniform DataMix / trained-proxy / DeMix merged-proxy→real retrain / OptiMer post-hoc / OptiMer-ratio→real retrain, with identical model/data/evaluator/seed contracts and explicit search/training/evaluation/storage/displacement accounting.
- Earlier OptiMer/DeMix/Data Mixing Agent/ELLA/SpaRTA/TSR/FST/TFGN/Share/SLoRA/FLEX/CLDD/replay/plasticity/world-model/drift branches remain live under prior scope guards.

Exact next action:
1. Pin second shards plus model index/config/tokenizer hashes for all seven DeMix `checkpoint-7500` components at immutable HF revision `82a2effc58eb79bec691280a4e4fc50be0968b1e`.
2. Inspect public reference-model trainer metadata/history for a concrete explanation of orphan `mix_16`; preserve 0..15 pairing unless evidence changes it.
3. Pin a deterministic OpenCompass revision/config/schema and build an evaluator adapter; never use the released synthetic placeholder as paper evidence.
4. Search source/release material for exact OptiMer Figure-4/Table-1 weights and public base/IT/CPT vector artifacts/study DB; otherwise keep Table-1 weights figure-only and use a seeded reconstruction.
5. Execute a reduced displacement sweep before paper-scale compute, comparing merged-proxy/post-hoc composition against real-mixture training as parameter displacement grows.
6. Continue earlier live branches under exact tested-scope rules.

Frontier must remain nonempty.
