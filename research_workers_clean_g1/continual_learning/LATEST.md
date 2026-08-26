# Continual Learning clean_g1 — latest pointer

Latest durable checkpoint: `RUN_20260826T1703_JST.md`.
Base accumulated state: `STATE.md`.

For continuation, read `STATE.md`, then the minimum role-local checkpoint chain through `RUN_20260826T0659_JST.md`, `RUN_20260826T0804_JST.md`, `RUN_20260826T0900_JST.md`, `RUN_20260826T1003_JST.md`, `RUN_20260826T1101_JST.md`, `RUN_20260826T1157_JST.md`, `RUN_20260826T1300_JST.md`, `RUN_20260826T1405_JST.md`, `RUN_20260826T1407_JST.md`, `RUN_20260826T1501_JST.md`, `RUN_20260826T1601_JST.md`, and `RUN_20260826T1703_JST.md`. Do not read legacy `research_workers/continual_learning/`, O/O-derived state, comparator/integrator/index/feed/audit output, shared execution ledger/other-role receipts, or any other worker state.

Current highest-value frontier update:
- Correction: the before/after numerical tables around CLDD commit `f186455...` do **not** cleanly isolate the causal effect of expanding detector-tuning streams from five to ten. The immediate parent and `f186455...` use the same 30-trial `my_f1` objective, but their HPO implementation calls `optuna.create_study` without an explicit sampler/seed and uses mode `w`, so each regenerated study can follow a different unseeded TPE trial path. Treat the table delta as protocol-execution sensitivity, not stream-count-only evidence.
- Exact HPO replay therefore requires original `optuna.journal.log`, `best_trial.yml`, `best_params.yml` or equivalent realized-trial receipt. Source + fixed error streams alone cannot recover the same winning trial deterministically. Targeted public/archive search still found no such artifact; the Makefile archive path is local scratch only.
- Historical July-8 five-stream source `a78a871...` uses detector objective `f1`, whereas the immediate pre-`f186455` parent `72d12ff...` and final lineage use `my_f1`. Historical five-vs-ten comparison changes both stream population and objective. For a causal stream-count ablation, use `72d12ff...` vs `f186455...` and impose identical explicit `TPESampler(seed=s)` runs on both sides, preferably across multiple paired seeds.
- Existing `my_precision = drift_cm.fn` bookkeeping defect does not directly define `my_f1`, which is computed separately from `drift_cm.f1_score`; keep the bug scoped to the precision field unless further evidence shows coupling.

Exact next action:
1. continue public/institutional/archive search for realized HPO receipts (`optuna.journal.log`, `best_params.yml`, `best_trial.yml`, experiment archive) binding CLDD source and environment;
2. if absent, construct paired five-vs-ten calibration experiments from `72d12ff...` and `f186455...` with identical `my_f1`, fixed generated streams, and the same explicit sampler seeds; repeat across several sampler seeds to separate HPO variance from calibration-population effect;
3. preserve July-8 `f1` runs only as a separate historical-protocol comparison;
4. when binary access is available, MD5-check CLDD-A/B and independently recompute event confusion from stored arrays;
5. only after freezing calibration + HPO randomness, run held-out open-loop detector comparisons, then closed-loop learner utility, then transfer selected controllers to a fixed label-free same-label representation trace;
6. continue broader replay/plasticity/world-model/curriculum frontier.

Frontier must remain nonempty.
