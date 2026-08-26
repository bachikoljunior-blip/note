# Continual Learning clean_g1 — latest pointer

Latest durable checkpoint: `RUN_20260826T2002_JST.md`.
Base accumulated state: `STATE.md`.

For continuation, read `STATE.md`, then the minimum role-local checkpoint chain through `RUN_20260826T0659_JST.md`, `RUN_20260826T0804_JST.md`, `RUN_20260826T0900_JST.md`, `RUN_20260826T1003_JST.md`, `RUN_20260826T1101_JST.md`, `RUN_20260826T1157_JST.md`, `RUN_20260826T1300_JST.md`, `RUN_20260826T1405_JST.md`, `RUN_20260826T1407_JST.md`, `RUN_20260826T1501_JST.md`, `RUN_20260826T1601_JST.md`, `RUN_20260826T1703_JST.md`, `RUN_20260826T1758_JST.md`, `RUN_20260826T1807_JST.md`, `RUN_20260826T1808_JST.md`, and `RUN_20260826T2002_JST.md`. Do not read legacy `research_workers/continual_learning/`, O/O-derived state, comparator/integrator/index/feed/audit output, shared execution ledger/other-role receipts, or any other worker state.

Current highest-value frontier update:
- The shared-vs-routed question now decomposes into independent axes: shared vs task-specific persistent storage, persistent state growth, inference router/task selector, and train-time boundary assumptions. Current papers change several of these at once, so headline comparisons are not causal.
- **SLoRA (ACL 2026)** is a strong non-routed LLM control: on TRACE, SLoRA-Pre reaches 60.19 average with Llama3.1-8B vs Seq-LoRA 52.81, and 59.20 with Qwen2.5-7B vs 51.54. It stores no replay data/historical gradients, but SLoRA-Pre denoises after each task, so training still assumes task boundaries. Official code pinned at `alina1031/SLoRA@0faf15fd6562ed3e146e8733205f59ef9742ba0f`.
- **Share / Shared LoRA Subspaces** is extremely parameter-efficient but needs a strict scope split: strict Share averages 78.69 on its sequential GLUE table with 0.012M adapter parameters, while the near-non-CL 83.44 is `Share-full`, which may use previous-task data to fine-tune task-specific coefficients. Share also retains `t` lightweight task-specific coefficient sets, so a shared basis is not the same as a single task-agnostic coefficient state. Official code pinned at `ankit-vaidya19/Share@ed4bc9c261f4389b1c2abd639e4f55ae81a1028b`.
- **ASO-LoRA (ACL 2026)** is a useful routing-free-inference control with task-specific growth: one frozen LoRA block per task, all blocks merged/summed at inference. Reported T5 averages are 77.0 on 4 tasks and 72.8 on 15 tasks, but some baselines are borrowed from prior papers and LLaMA2-7B SeqLoRA slightly beats ASO-LoRA, so it is not uniformly dominant.
- **MoBLoRA (ACL 2026)** does not eliminate routing: it uses globally shared bases plus task-specific mixing matrices and semantic nearest-neighbor routing at inference. CoIN reports 65.34 Avg.ACC / 0.00 Forgetting, but the correct interpretation is cheap shared-basis routing, not “routing unnecessary”.
- This reconciles prior SinglePrompt and PASs-MoE evidence: local/selective interference control can outperform unnecessary selection in some streams, while heterogeneous multimodal streams can benefit greatly from routing. The next fair test must independently control storage, growth, routing, boundaries and compute.
- CLDD provenance correction remains: any 5-vs-10 tuning-stream reconstruction must use identical `my_f1`, fixed streams and explicit matched `TPESampler(seed=s)` values; no new archive channel was found this run.
- DRIFT remains a provisional smooth-transition negative-control candidate; do not assume crisp task boundaries without a separate boundary-free test.

Exact next action:
1. Share: inspect strict evaluation/inference code to determine exactly how task-specific coefficient sets are selected and whether GLUE evaluation gets oracle task identity.
2. SLoRA: pin adapter lifecycle and per-task denoising code; quantify whether persistent state stays constant or task snapshots accumulate.
3. Build a source-qualified matched-comparison matrix for SLoRA / strict Share / Share-full / ASO-LoRA / MoBLoRA / PASs-MoE across replay, old-data access, train-time task boundaries, inference task identity, router, persistent growth, active parameters and borrowed-vs-rerun baselines.
4. Search for genuinely boundary-free continual-language streams directly comparing shared/selective-update control against routing; do not transfer task-sequence evidence by analogy.
5. DRIFT: verify public code/final artifact and extract a minimal smooth-transition matched protocol.
6. CLDD: when reconstructing, pair the five- vs ten-stream calibration under fixed sampler seeds; when binary transport becomes available, MD5-check parquet and independently recompute event metrics.
7. Continue broader replay/plasticity/world-model/curriculum frontier with matched-compute emphasis.

Frontier must remain nonempty.
