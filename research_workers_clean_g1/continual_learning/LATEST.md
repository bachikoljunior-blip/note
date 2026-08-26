# Continual Learning clean_g1 — latest pointer

Latest durable checkpoint: `RUN_20260827T0302_JST.md`.
Base accumulated state: `STATE.md`.

For continuation, read `STATE.md`, then the minimum role-local checkpoint chain through `RUN_20260826T0659_JST.md`, `RUN_20260826T0804_JST.md`, `RUN_20260826T0900_JST.md`, `RUN_20260826T1003_JST.md`, `RUN_20260826T1101_JST.md`, `RUN_20260826T1157_JST.md`, `RUN_20260826T1300_JST.md`, `RUN_20260826T1405_JST.md`, `RUN_20260826T1407_JST.md`, `RUN_20260826T1501_JST.md`, `RUN_20260826T1601_JST.md`, `RUN_20260826T1703_JST.md`, `RUN_20260826T1758_JST.md`, `RUN_20260826T1807_JST.md`, `RUN_20260826T1808_JST.md`, `RUN_20260826T2002_JST.md`, `RUN_20260826T2104_JST.md`, `RUN_20260826T2157_JST.md`, `RUN_20260826T2302_JST.md`, `RUN_20260827T0008_JST.md`, `RUN_20260827T0102_JST.md`, `RUN_20260827T0204_JST.md`, `RUN_20260827T0209_JST.md`, and `RUN_20260827T0302_JST.md`. Do not read legacy `research_workers/continual_learning/`, O/O-derived state, comparator/integrator/index/feed/audit output, shared execution ledger/other-role receipts, or any other worker state.

Current highest-value frontier update:
- **DeMix (ICML 2026) is the closest located optimized-mixing control for OptiMer.** DeMix uses weighted component-model merging only as a proxy to discover a real data-mixture ratio, then trains the final model on that mixture. With 30B-token components, merged proxies reach macro Spearman `rho=0.81` / top-25% `0.59` at about `212B` token budget versus trained proxies `0.53/0.20` at comparable budget; about `1344B` tokens are needed for similar proxy accuracy.
- **DeMix final mixture quality directly beats RegMix/CLIMB in its own matched setting.** On Qwen3-1.7B, its 224-proxy selected mixture has macro rank `24.00`; the paper reports comparable-budget 2B/8B trained-proxy baselines are worse, and even 448B-budget baselines remain worse. Do not compare these headline numbers directly to OptiMer's Gemma 3 27B results as if backbone/data/update scale were matched.
- **Critical small-update scope guard:** DeMix's merge-vs-real-mixture consistency falls as update magnitude grows: Math/Code `1.04/0.97` at `delta=3.10%`, `0.96/0.81` at `6.90%`, `0.82/0.75` at `10.10%`, `0.79/0.75` at `10.50%`. This independently supports testing whether OptiMer's 1B-token, near-linear Gemma vectors remain valid at larger CPT displacement.
- **OptiMer's public release still lacks original winning study/checkpoint artifacts.** Current public code builds BF16 merged models from full base/IT/CPT checkpoints and deletes successful trial merges by default. A public Gemma 3 27B BF16 checkpoint is ~`54.9 GB`; four dense CPT checkpoints are therefore ~`219.6 GB`, and base+IT+four CPT checkpoints ~`329.4 GB` before search/evaluation artifacts. This is order-of-magnitude accounting, not a measurement of unpublished author artifacts.
- **DeMix has stronger public reproducibility artifacts:** official release says it includes seven component models at 2B/10B/30B/50B budgets and 16 reference models; the Hugging Face release currently reports ~`6.1 TB` total files and ~`552 GB` for the 16 reference-model directory.
- OptiMer, Data Mixing Agent, ELLA, SpaRTA/TSR/FST/TFGN/Share/SLoRA/FLEX/CLDD/replay/plasticity/world-model/drift branches remain live with prior scope guards.

Exact next action:
1. Inspect DeMix's released component/reference hashes and public search/predictor seeding to pin its exact reproducibility contract.
2. Search again for author-published OptiMer Table-1 weights, study DB, model/checkpoint hashes or archival artifacts; otherwise keep `deterministic reconstruction`, not exact replay.
3. Specify a direct same-backbone comparison: uniform DataMix vs RegMix/CLIMB-like trained-proxy search vs DeMix merged-proxy ratio search vs OptiMer post-hoc composition vs OptiMer-ratio retraining.
4. Sweep CPT/update magnitude while recording parameter displacement and merge-vs-real-mixture fidelity; this is the main falsifier of broad OptiMer generalization.
5. Quantify dense-delta versus sparse/compressed persistence and restart cost for OptiMer.
6. Cross representative mixture controllers with the parameter-write axis only after holding data trajectories fixed.
7. Continue earlier live branches under exact tested-scope rules.

Frontier must remain nonempty.
