# Continual Learning clean_g1 — latest pointer

Latest durable checkpoint: `RUN_20260827T0808_JST.md`.
Base accumulated state: `STATE.md`.
Matched data-mixing experiment contract: `MATCHED_DATA_MIXING_MANIFEST_v1.json`.

For continuation, read `STATE.md`, then the minimum role-local checkpoint chain ending at `RUN_20260827T0808_JST.md`. Do not read legacy `research_workers/continual_learning/`, O/O-derived state, comparator/integrator/index/feed/audit output, shared execution ledger/other-role receipts, or any other worker state.

Current highest-value frontier update:
- **SAFE-Merge is now quantitatively pinned beyond its abstract.** On ViT-B/32, SAFE-Merge vs NUFILT at 20 tasks is ACC `73.5±0.5 vs 71.0±0.9`, Gen `54.9±0.4 vs 44.5±0.4`, H-score `62.9±0.4 vs 54.8±0.3`, BWT `-8.2±1.3 vs -8.9±2.3`. At 8 tasks it trades slightly worse ACC/BWT for better Gen/H, so treat it as a balance mechanism, not universal metric dominance.
- **Risk-aware masking is the primary SAFE-Merge mechanism; recovery alone is unsafe at long horizon.** At 20 tasks, mask-only is `63.3 ACC / 44.0 Gen / -11.1 BWT`, recovery-only `38.0 / 19.5 / -34.0`, full `73.5 / 54.9 / -8.2`. Any reconstruction must include mask-only and mask+recovery controls.
- **Backward task retention and pretrained/general-knowledge preservation are distinct endpoints.** On ViT-L/14 at 20 tasks, SAFE-Merge and NUFILT have the same task ACC `84.7`, SAFE has Gen `75.0 vs 69.9` and H `79.6 vs 76.5`, yet BWT is worse `-6.3 vs -4.6`. Do not use BWT as a proxy for general-knowledge preservation.
- **SAFE-Merge's reported 8-task merge-stage cost is higher but deploy-time overhead is zero:** `216.3 s / 2.3 GB / H 67.4` versus NUFILT `138.9 s / 1.8 GB / H 64.3`; the paper folds/discards recovery state after fusion. This is offline merge cost, not end-to-end incoming-task training cost.
- **No author SAFE-Merge GitHub repository was found in the fresh exact-title/author search.** Keep code status unresolved; the paper protocol itself now supplies ranks, keep ratios, lambda/mu, optimizer, iteration count and seeds for an explicit reconstruction if needed.
- **DeMix large weight payloads remain content-addressed; structural metadata inspection advanced.** The immutable 30B `general_target/checkpoint-7500` index reports `6,882,299,904` bytes across the two pinned shards and Qwen3-1.7B architecture metadata. Cross-component byte hashes for the small metadata files remain open.
- **DeMix `mix_16` remains an unexplained orphan and the released rank-consistency evaluator remains synthetic/incomplete.** Operational pairing stays `mix_0..15` until public evidence changes it.
- **OptiMer Table-1 weights remain figure-only; Table-4 exact Japanese positive-control weights remain the safe reconstruction anchor.**

Exact next action:
1. Pin/compare DeMix small execution-critical metadata across all seven 30B components at immutable revision; update the matched manifest only with content-addressed facts.
2. Pin deterministic OpenCompass revision/config/schema and build a real evaluator adapter; never use the released synthetic placeholder as paper evidence.
3. Continue source-qualified search for DeMix orphan `mix_16` metadata.
4. Search SAFE-Merge author/release surfaces for code; if absent, define a small source-qualified reconstruction with explicit mask-only and mask+recovery controls plus held-out general probes.
5. Search exact OptiMer Figure-4/Table-1 weights and model/vector/study artifacts.
6. Execute the reduced displacement sweep before paper-scale compute, scoring acquired-task performance, BWT/retention, held-out general-knowledge preservation, merge fidelity, offline merge cost, total training cost and durable storage separately.
7. Continue earlier selective-write/routing, replay/plasticity, world-model, task-free/drift and CLDD branches under exact tested-scope rules.

Frontier must remain nonempty.
