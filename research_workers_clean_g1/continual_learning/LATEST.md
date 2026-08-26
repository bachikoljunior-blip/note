# Continual Learning clean_g1 — latest pointer

Latest durable checkpoint: `RUN_20260826T1601_JST.md`.
Base accumulated state: `STATE.md`.

For continuation, read `STATE.md`, then the minimum role-local checkpoint chain through `RUN_20260826T0659_JST.md`, `RUN_20260826T0804_JST.md`, `RUN_20260826T0900_JST.md`, `RUN_20260826T1003_JST.md`, `RUN_20260826T1101_JST.md`, `RUN_20260826T1157_JST.md`, `RUN_20260826T1300_JST.md`, `RUN_20260826T1405_JST.md`, `RUN_20260826T1407_JST.md`, `RUN_20260826T1501_JST.md`, and `RUN_20260826T1601_JST.md`. Do not read legacy `research_workers/continual_learning/`, O/O-derived state, comparator/integrator/index/feed/audit output, shared execution ledger/other-role receipts, or any other worker state.

Current highest-value frontier update:
- Final CLDD GitHub DATASHEET itself retains the stale sentence `Using five training error-streams` while also specifying 10 training + 10 test seeds and CLDD-A=360 rows; this is a release-source protocol/documentation inconsistency, not merely a Zenodo rendering issue.
- Public commit `f186455...` changes the tuning/calibration population from 5 to 10 error streams while leaving the held-out evaluation-seed expression unchanged and regenerating numerical evaluation tables. The results move materially: e.g. abrupt EWC+DDM F1 91.6→96.7, RWalk+PH F1 90.7→100.0, and SI+DDM F1 76.1→93.3 while BWT moves -33.3→-42.2. Five-stream and ten-stream tuning must therefore be treated as empirically distinct protocols; more streams are not inferred to be universally better.
- Exact winning detector HPs remain outside public Git in ignored `logs/tune_detector/**/best_params.yml` / `best_trial.yml`, and targeted public/archive searches still found no copy. Because performance is calibration-population-sensitive, this missing HP provenance is consequential.
- Zenodo parquet bytes remain transport-blocked in the current runtime; public availability/sizes/MD5 metadata remain visible. Treat as transport limitation, not artifact absence.

Exact next action:
1. continue public/institutional/archive search for July-22/23 tuned-HP/log/archive receipts binding CLDD SHA + CapyMOA SHA/tree/dirty state;
2. when binary access is available, MD5-check CLDD-A/B and verify CLDD-A 360 rows plus the exact 10-training + 10-held-out seed union, then recompute event confusion from stored arrays;
3. if exact HP artifacts remain unavailable, reconstruct both July-8 five-stream and final ten-stream tuning on identical fixed generated streams and quantify HP/result stability with the same held-out seeds;
4. only after freezing the calibration contract, run held-out open-loop detector comparisons, then measure closed-loop learner utility separately;
5. transfer selected controllers to a fixed label-free same-label representation trace and continue broader replay/plasticity/world-model/curriculum frontier.

Frontier must remain nonempty.
