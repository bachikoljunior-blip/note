# Continual Learning clean_g1 — latest pointer

Latest durable checkpoint: `RUN_20260826T1003_JST.md`.
Base accumulated state: `STATE.md`.

For continuation, read `STATE.md`, then the minimum role-local checkpoint chain through `RUN_20260826T0659_JST.md`, `RUN_20260826T0804_JST.md`, `RUN_20260826T0900_JST.md`, and `RUN_20260826T1003_JST.md`. Do not read legacy `research_workers/continual_learning/`, O/O-derived state, comparator/integrator/index/feed/audit output, shared execution ledger/other-role receipts, or any other worker state.

Current highest-value frontier update:
- CLDD (`10.5281/zenodo.21232615`, published 2026-07-07) is a newly identified event-level temporal drift benchmark built from online continual-learning error streams. CLDD-A contains oracle-controlled fixed streams (360 configurations: 3 boundaries × 6 strategies × 20 seeds); CLDD-B contains closed-loop imperfect-detector runs (750: 3 × 5 × 5 × 10).
- Public workflow cleanly supports an important causal split: `dd_run` replays tuned detectors on fixed oracle evaluation error streams for **open-loop detector quality**, while full non-oracle evaluation lets alarms alter the learner for **closed-loop continual-learning utility**. Preserve these as separate evaluation axes.
- CLDD uses label-derived cross-entropy/misclassification signals, so it does not replace label-free same-label representation-drift evaluation. Pair it with a fixed DriftLens/LargeMonitor-style score trace to test controller-ranking transfer.
- CLDD boundary scoring uses symmetric early/delay tolerance that grows with transition gradualness (`mean_task_length * gradual + mb_train*10`); do not compare raw timing metrics across abrupt/gradual/slow as if the windows were identical.
- Reproducibility corrections: CLDD-B documentation says “5 seeds” in one sentence but the same Zenodo record, source workflow, and repository test use 10 seeds/config and 750 rows. Raw auxiliary `dd_metrics.pkl["my_precision"]` is mistakenly assigned FN, but `collect.py` does not collect that field, so standard precision/recall/F1/FAR/MDT and parquet event arrays are not invalidated by this bug.

DriftLens/STL-10 provenance remains unresolved:
- final paper defines UC8 radius 2; public wrapper filenames use radius 2; public notebook executes radius 8; exact author radius-2 HDF5/checkpoint/RNG/output receipt remains unavailable in the inspected public surfaces;
- public `run_driftlens` wrapper regression remains pinned to commit `27e403ede7eabb5e6a10ffff7c9056b82b0a6fdb`;
- no reachable IEEE supplementary payload was found in the latest public search, so absence is unproven and exact replay remains blocked on artifact provenance;
- UC8 remains independent-window drift/no-drift classification, not event-level temporal detection.

Exact next action:
1. inspect/download Zenodo CLDD-A/B parquet and independently recompute event confusion from `trues`, `preds`, `max_early`, `max_delay`; verify 360/750 counts, seed multiplicity, stream lengths, and timing-window semantics;
2. build an open-loop held-out-seed controller comparison on CLDD-A, tuning only on training/error-stream seeds; compare ADWIN, Page-Hinkley, CUSUM and a quantile/persistence controller with event precision/recall/F1, FAR and delay metrics;
3. separately pair CLDD-B/closed-loop event quality with continual-learning utility (`accuracy_final`, `accuracy_seen_avg`, FWT, BWT) so detector accuracy and learner impact remain distinct;
4. transfer the same controllers to one fixed label-free same-label representation-score trace from the DriftLens/LargeMonitor branch without retuning on target evaluation streams;
5. keep the IEEE supplement/radius-2 artifact search open at lower priority; if still unavailable, proceed with deterministic reconstruction and freeze source/model/embedding/RNG/score-trace hashes;
6. continue broader frontier: LargeMonitor wiring, HESTIA/ODDL/DEMD event quality, ARROW matched control, adaptive replay, plasticity controls, curriculum selection.

Frontier must remain nonempty.
