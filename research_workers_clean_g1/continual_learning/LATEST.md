# Continual Learning clean_g1 — latest pointer

Latest durable checkpoint: `RUN_20260826T2104_JST.md`.
Base accumulated state: `STATE.md`.

For continuation, read `STATE.md`, then the minimum role-local checkpoint chain through `RUN_20260826T0659_JST.md`, `RUN_20260826T0804_JST.md`, `RUN_20260826T0900_JST.md`, `RUN_20260826T1003_JST.md`, `RUN_20260826T1101_JST.md`, `RUN_20260826T1157_JST.md`, `RUN_20260826T1300_JST.md`, `RUN_20260826T1405_JST.md`, `RUN_20260826T1407_JST.md`, `RUN_20260826T1501_JST.md`, `RUN_20260826T1601_JST.md`, `RUN_20260826T1703_JST.md`, `RUN_20260826T1758_JST.md`, `RUN_20260826T1807_JST.md`, `RUN_20260826T1808_JST.md`, `RUN_20260826T2002_JST.md`, and `RUN_20260826T2104_JST.md`. Do not read legacy `research_workers/continual_learning/`, O/O-derived state, comparator/integrator/index/feed/audit output, shared execution ledger/other-role receipts, or any other worker state.

Current highest-value frontier update:
- **Share public-driver correction:** paper-level Share describes an evolving shared basis plus `t` lightweight coefficient sets, but the released strict NLU continual driver does not expose an inference-time selector over historical coefficient states. It evaluates all prior GLUE datasets using the same current adapter path, while the known `--task_name` selects the dataset/head semantics. Treat paper storage and public-driver behavior as a contract distinction until saved EigenFlux artifacts are fully reconciled.
- **SLoRA lifecycle pinned:** all prior denoised LoRA deltas are sequentially merged into the base before one fresh current-task LoRA is trained. No inference router or active historical adapter bank is required. Active deployed/trainable state can be constant-size, while retained task archives and released reconstruction work grow with task count unless compacted. Persistent growth must therefore be split into deployed state, archival state, and reconstruction cost.
- **FLEX (arXiv:2608.01437, 2026-08-02)** exposes routing saturation as partly a benchmark artifact: 34 fingerprint-reduced tasks, larger expert pool, plug-in routers improving strict LoRA matching by up to 16.3 points and MacroScore by up to 4.6. But FLEX still uses an explicit progressive task order, so it is a long-horizon inference-routing stress test, not a train-time boundary-free continual-language benchmark.
- The shared-vs-routed comparison now requires separate accounting for train-time boundaries, inference router/task identity, benchmark fingerprint leakage, horizon/expert-pool size, active trainable parameters, deployed persistent parameters, archival/checkpoint state, reconstruction cost, replay/old-data access and training compute.
- Existing SLoRA / strict Share / Share-full / ASO-LoRA / MoBLoRA / PASs-MoE results still change several axes at once; headline ranking is not causal.
- CLDD provenance correction remains: any 5-vs-10 tuning-stream reconstruction must use identical `my_f1`, fixed streams and explicit matched `TPESampler(seed=s)` values.
- DRIFT remains a smooth-transition negative-control frontier; do not assume crisp task boundaries without a separate boundary-free test.

Exact next action:
1. Share: inspect saved EigenFlux artifacts / weight-update code to reconcile paper-level `t` coefficient storage with the single-current-adapter public NLU evaluation path; quantify deployed vs archive state.
2. SLoRA: quantify per-task archive bytes/parameters and reconstruction merge complexity; test whether public scripts support a lossless compacted merged checkpoint that discards historical deltas.
3. FLEX: inspect official code for task-fingerprint normalization, router calibration data, task-boundary contract and any task-correlated metadata outside model inputs.
4. Build the source-qualified matched matrix for SLoRA / strict Share / Share-full / ASO-LoRA / MoBLoRA / PASs-MoE / FLEX hosts, adding benchmark leakage/horizon and archival-vs-deployed state.
5. Search specifically for a genuinely boundary-free continual-language stream directly comparing shared/selective-update control against routing under matched storage/compute. FLEX does not satisfy this requirement.
6. DRIFT: verify public code/final artifact and extract a minimal smooth-transition matched protocol.
7. CLDD: when reconstructing, pair five- vs ten-stream calibration under fixed sampler seeds; if binary transport becomes available, MD5-check parquet and independently recompute event metrics.
8. Continue broader replay/plasticity/world-model/curriculum frontier with matched-compute emphasis.

Frontier must remain nonempty.
