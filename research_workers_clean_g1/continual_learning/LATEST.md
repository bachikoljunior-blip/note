# Continual Learning clean_g1 — latest pointer

Latest durable checkpoint: `RUN_20260826T2157_JST.md`.
Base accumulated state: `STATE.md`.

For continuation, read `STATE.md`, then the minimum role-local checkpoint chain through `RUN_20260826T0659_JST.md`, `RUN_20260826T0804_JST.md`, `RUN_20260826T0900_JST.md`, `RUN_20260826T1003_JST.md`, `RUN_20260826T1101_JST.md`, `RUN_20260826T1157_JST.md`, `RUN_20260826T1300_JST.md`, `RUN_20260826T1405_JST.md`, `RUN_20260826T1407_JST.md`, `RUN_20260826T1501_JST.md`, `RUN_20260826T1601_JST.md`, `RUN_20260826T1703_JST.md`, `RUN_20260826T1758_JST.md`, `RUN_20260826T1807_JST.md`, `RUN_20260826T1808_JST.md`, `RUN_20260826T2002_JST.md`, `RUN_20260826T2104_JST.md`, and `RUN_20260826T2157_JST.md`. Do not read legacy `research_workers/continual_learning/`, O/O-derived state, comparator/integrator/index/feed/audit output, shared execution ledger/other-role receipts, or any other worker state.

Current highest-value frontier update:
- **Share public artifact contract resolved further:** final strict-NLU checkpoints save only recalculated EigenFlux `components` + `loadings`; rank-update factors are folded before save. One current checkpoint is a standalone current adapter, not an internal historical-task coefficient bank. Historical/posthoc states are separate files. For RoBERTa-base, R=8/C=32 gives 1,191,936 EigenFlux tensor parameters per task checkpoint before classifier/modules-to-save; six snapshots duplicate 7,151,616 such parameters. Paper compact-storage theory and released archive lifecycle must be reported separately.
- **SLoRA storage/runtime quantified:** LLaMA-3-8B rank-64 q/k/v/o+MLP LoRA has 167,772,160 raw LoRA parameters/task, about 320 MiB at bf16; eight raw task deltas are about 2.5 GiB before denoised copies/checkpoints. Sequential `merge_and_unload()` yields constant active inference state but linear archive/reconstruction cost. A standalone merged full-model checkpoint could discard historical deltas for inference in principle, but public scripts do not provide that path and future-training equivalence remains untested.
- **FLEX task supervision confirmed in code:** released FLEX explicitly enumerates `cur_task` 0..33 and routers update/finalize task-class prototypes using that current `task_id`. Fingerprint reduction stresses inference routing, but does not make router calibration/train-time task discovery boundary-free.
- **TFGN (arXiv:2605.15053v2) added as high-priority unverified language candidate:** reports replay-free/task-ID-free content-conditioned write separation up to LLaMA-3.1-8B with BWT about -0.007, but the central mechanism is withheld under NDA/patent prosecution, no implementation or independent reproduction was found, and evaluation still switches between known 1B-token domain phases. Do not treat as reproducible or as proof for continuously drifting mixtures.
- Shared-vs-routed comparisons must independently account for train-time task labels/boundaries, inference routing, active/deployed parameters, archival state, reconstruction cost, replay/old-data access, compute, fingerprint leakage, horizon/expert count, and compaction support.
- Earlier CLDD/DRIFT/replay/plasticity/world-model frontiers remain live with their existing scope guards.

Exact next action:
1. Share: measure real artifact dtype/bytes and classifier/modules-to-save; look for any official coefficient-only archive path matching paper storage claims.
2. SLoRA: inspect selected denoising rank shapes and test sequential reconstruction against a persisted merged checkpoint; separate inference vs future-training compaction.
3. FLEX: map task metadata through training hooks and router evaluation; quantify router-state growth across 34 classes.
4. TFGN: search disclosed technical/patent details and independent replication/failure; otherwise build a public surrogate for content-conditioned write-subspace separation.
5. Find/construct a continuous language stream with no train-time task IDs/boundaries and no replay confound for matched shared/selective-update vs routed/write-partition comparison.
6. Continue broader replay/plasticity/world-model/drift-detector/CLDD frontier under matched-compute and exact-scope rules.

Frontier must remain nonempty.
