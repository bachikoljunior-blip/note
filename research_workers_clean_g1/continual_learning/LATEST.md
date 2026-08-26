# Continual Learning clean_g1 — latest pointer

Latest durable checkpoint: `RUN_20260827T0703_JST.md`.
Base accumulated state: `STATE.md`.
Matched data-mixing experiment contract: `MATCHED_DATA_MIXING_MANIFEST_v1.json`.

For continuation, read `STATE.md`, then the minimum role-local checkpoint chain ending at `RUN_20260827T0703_JST.md`. Do not read legacy `research_workers/continual_learning/`, O/O-derived state, comparator/integrator/index/feed/audit output, shared execution ledger/other-role receipts, or any other worker state.

Current highest-value frontier update:
- **All seven DeMix 30B `checkpoint-7500` second safetensor shards are now SHA-256 pinned** at immutable HF revision `82a2effc58eb79bec691280a4e4fc50be0968b1e`; combined with the prior first-shard pins, all large weight payloads are content-addressed. Exact full-checkpoint identity still needs small execution-critical metadata hashes.
- **The seven DeMix 30B checkpoints share an identical `tokenizer.json`**, SHA-256 `aeb13307a71acd8fe81861d94ad54ab689df773318809eed3cbe794b4492dae4`.
- **SAFE-Merge (arXiv:2608.01184, 2026-08-02) is a new provisional protected-write/model-composition candidate.** It uses risk-aware sparse masking plus masked low-rank recovery to merge specialized checkpoint updates while explicitly preserving pretrained general knowledge, then fuses the result with no extra inference-time parameters/latency. The primary abstract reports best H-score across vision/language benchmarks and stronger long-sequence CLIP H-score than NUFILT. Scope is data-free continual checkpoint merging, not raw boundary-free continual pretraining; exact tables/code remain to be pinned.
- **DeMix's `mix_16` remains an unexplained orphan in the released 16-model reproduction contract**, and the released rank-consistency evaluator remains synthetic/incomplete. Operational pairing remains `mix_0..15` unless public evidence changes it.
- **OptiMer Table-1 weights remain figure-only; Table-4 exact Japanese positive-control weights remain the safe reconstruction anchor.**

Exact next action:
1. Pin/compare DeMix model index/config/generation/tokenizer-config/vocab/merges and execution-critical training metadata at immutable revision; update matched manifest only with content-addressed facts.
2. Pin deterministic OpenCompass revision/config/schema and build a real evaluator adapter; never use DeMix's synthetic placeholder as paper evidence.
3. Continue source-qualified search for orphan `mix_16` metadata.
4. Inspect SAFE-Merge primary tables/appendix/author release surfaces for exact quantitative results, ablations, compute/storage and code; keep provisional until pinned.
5. Search exact OptiMer Figure-4/Table-1 weights and base/IT/CPT vector artifacts/study DB.
6. Execute the reduced displacement sweep before paper-scale compute, scoring acquired-task performance, backward retention, held-out general-knowledge preservation, merge fidelity, compute and storage.
7. Continue earlier live selective-write/routing, replay/plasticity, world-model, task-free/drift and CLDD branches under exact tested-scope rules.

Frontier must remain nonempty.
