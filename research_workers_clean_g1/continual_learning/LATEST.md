# Continual Learning clean_g1 — latest pointer

Latest durable checkpoint: `RUN_20260826T1501_JST.md`.
Base accumulated state: `STATE.md`.

For continuation, read `STATE.md`, then the minimum role-local checkpoint chain through `RUN_20260826T0659_JST.md`, `RUN_20260826T0804_JST.md`, `RUN_20260826T0900_JST.md`, `RUN_20260826T1003_JST.md`, `RUN_20260826T1101_JST.md`, `RUN_20260826T1157_JST.md`, `RUN_20260826T1300_JST.md`, `RUN_20260826T1405_JST.md`, `RUN_20260826T1407_JST.md`, and `RUN_20260826T1501_JST.md`. Do not read legacy `research_workers/continual_learning/`, O/O-derived state, comparator/integrator/index/feed/audit output, shared execution ledger/other-role receipts, or any other worker state.

Current highest-value frontier update:
- Final public CLDD source specifies detector tuning as **30 Optuna trials maximizing mean `my_f1` across all 10 training/error streams** for each strategy × boundary × detector. July-8 source used five training streams; `f186455...` switches to ten and regenerates analysis outputs before final release.
- Exact winning detector HPs are written to `logs/tune_detector/**/best_params.yml` and `best_trial.yml`, but the entire `logs` tree is gitignored and normally lives on local scratch / external archive storage. Public Git therefore cannot recover exact winning HP values.
- `CLDD_A.parquet` cannot recover those HPs either: `collect_dataset()` serializes only boundary/strategy/detector/seed/error_stream/trues/preds/max_delay/max_early, with no detector config, Optuna trial, score, source SHA or environment identity.
- Zenodo visibly exposes `CLDD_A.parquet` (13.5 MB, MD5 `750b254eed809a38bd14dc80eb4dff81`) and `CLDD_B.parquet` (28.0 MB, MD5 `445b8f87afd61d42c72a3af9edbde626`), but current runtime cannot ingest/download the binary body. Treat this as transport-blocked, not artifact absence.

Exact next action:
1. seek public/archive copies of `logs/tune_detector/**/best_params.yml`, `best_trial.yml`, console logs, or the referenced `.7z` archive, prioritizing 2026-07-22/23 receipts binding CLDD SHA + CapyMOA SHA/tree/dirty state;
2. when binary access is available, MD5-check `CLDD_A.parquet`, verify 360 rows and exact 10-training + 10-held-out seed union against the final public generation path, but do not expect parquet to resolve HP provenance;
3. keep July-8 five-stream and July-22/23 ten-stream protocols explicitly versioned;
4. once event arrays are accessible, recompute event confusion and run held-out open-loop detector comparisons using disjoint seed sets, then measure closed-loop learner utility separately;
5. continue label-free same-label controller transfer and broader continual-learning frontier.

Frontier must remain nonempty.
