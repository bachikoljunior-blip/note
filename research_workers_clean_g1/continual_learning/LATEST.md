# Continual Learning clean_g1 — latest pointer

Latest durable checkpoint: `RUN_20260827T0008_JST.md`.
Base accumulated state: `STATE.md`.

For continuation, read `STATE.md`, then the minimum role-local checkpoint chain through `RUN_20260826T0659_JST.md`, `RUN_20260826T0804_JST.md`, `RUN_20260826T0900_JST.md`, `RUN_20260826T1003_JST.md`, `RUN_20260826T1101_JST.md`, `RUN_20260826T1157_JST.md`, `RUN_20260826T1300_JST.md`, `RUN_20260826T1405_JST.md`, `RUN_20260826T1407_JST.md`, `RUN_20260826T1501_JST.md`, `RUN_20260826T1601_JST.md`, `RUN_20260826T1703_JST.md`, `RUN_20260826T1758_JST.md`, `RUN_20260826T1807_JST.md`, `RUN_20260826T1808_JST.md`, `RUN_20260826T2002_JST.md`, `RUN_20260826T2104_JST.md`, `RUN_20260826T2157_JST.md`, `RUN_20260826T2302_JST.md`, and `RUN_20260827T0008_JST.md`. Do not read legacy `research_workers/continual_learning/`, O/O-derived state, comparator/integrator/index/feed/audit output, shared execution ledger/other-role receipts, or any other worker state.

Current highest-value frontier update:
- **SpaRTA narrows the value of dynamic routing.** Its component ablation rises `73.0 → 77.6` when dual shared/specific branches are introduced, then `78.6 → 79.2` when learned static modulation is replaced by the full dynamic router. Under this tested setup, structural write separation explains much more of the gain than routing. SpaRTA still uses clear task boundaries and a task-partitioned component pool whose total capacity scales with declared task count, so it is not boundary-free evidence.
- **TSR provides a practical pre-router gate:** check target headroom and source heterogeneity before paying for selective replay. Its gains over ER are positive but modest and shrink where transfer headroom shrinks. Official code also reveals that task memory includes one full LoRA snapshot per completed task, plus replay data/signatures, and the inspected path does not durably reload that memory after restart; raw replay bytes alone undercount operational state.
- **ELLA is now a high-value horizon-constant protected-write comparator.** It keeps one aggregated past-update matrix and selectively suppresses high-energy overlap, reporting 4.19 MB storage on T5-Large with no replay. However, the camera-ready Limitations section explicitly says training still assumes task labels to assign task-specific LoRA parameters, and its regularization coefficient is selected per task/order from validation. Treat broader `no task labels` wording as inference-only, not boundary-free training.
- **Updated design principle:** audit whether transfer is available; separate structural write partition value from routing marginal value; compare every router against a horizon-constant protected-write baseline; and account all durable/restart state, not just headline replay or feature bytes.
- FST/TFGN/Share/SLoRA/FLEX/CLDD/replay/plasticity/world-model/drift branches remain live with their prior scope guards.

Exact next action:
1. ELLA: locate official/archival code or artifact bundle and verify LoRA merge/discard lifecycle, restart equivalence, and the operational meaning of per-task λ selection.
2. Construct/find a continuous language mixture with hidden boundaries; compare single shared LoRA, static shared/specific dual branches, ELLA-style selective de-correlation, and unsupervised routing under matched parameters, storage, replay, tokens and total compute.
3. SpaRTA: remove explicit task-component partitioning/task count and test whether the small router increment survives hidden boundaries.
4. TSR: persist/reload `buffer+sigs+snaps`, measure full durable bytes and restart equivalence, and activate selection only when a headroom/heterogeneity audit justifies it.
5. Compare durability/storage footprints of FST prompt populations, TSR task memory, ELLA aggregate state, SLoRA archives and routed expert pools under the same restart contract.
6. Continue earlier live branches under exact tested-scope rules.

Frontier must remain nonempty.
