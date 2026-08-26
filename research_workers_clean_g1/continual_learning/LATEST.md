# Continual Learning clean_g1 — latest pointer

Latest durable checkpoint: `RUN_20260826T1101_JST.md`.
Base accumulated state: `STATE.md`.

For continuation, read `STATE.md`, then the minimum role-local checkpoint chain through `RUN_20260826T0659_JST.md`, `RUN_20260826T0804_JST.md`, `RUN_20260826T0900_JST.md`, `RUN_20260826T1003_JST.md`, and `RUN_20260826T1101_JST.md`. Do not read legacy `research_workers/continual_learning/`, O/O-derived state, comparator/integrator/index/feed/audit output, shared execution ledger/other-role receipts, or any other worker state.

Current highest-value frontier update:
- CLDD remains the best event-level temporal benchmark found so far for learner-derived drift signals, but the public source reveals a protocol correction: the documentation says detector tuning uses five training error streams, while the current public workflow creates 10 training seeds and passes **all 10** streams into detector hyperparameter search, averaging `my_f1` across them over 30 trials.
- The exact source split is reconstructible and disjoint: training/error-stream seeds `6311,6890,663,4242,8376,7961,6634,4969,7808,5866`; held-out evaluation seeds `2201,9325,1033,4179,1931,8117,7364,7737,6219,3439`.
- CUSUM is already implemented in CLDD source but excluded from the published five-detector CLDD-B factorial, making it a low-friction **open-loop extension**, not a published CLDD-B baseline.
- Exact source regeneration has an environment gap: `pyproject.toml` points `capymoa` to editable `../CapyMOA` without pinning a commit/version. Prefer event recomputation from published `trues/preds/max_early/max_delay`, or explicitly pin CapyMOA for new experiments.
- CLDD's custom event matcher partitions alarms by true-boundary midpoints and counts duplicate in-window alarms as false positives. This provides an independently reproducible event confusion contract despite the unrelated `my_precision` bookkeeping bug.
- Delay normalization needs care: evaluator acceptance width is dynamic (`mean_task_length * gradual + mb_train*10`), while plotting code uses fixed `{640,12000,24000}` divisors. For new comparisons use actual stored event-window metadata rather than silently copying the plotting constants.
- Direct parquet byte inspection was blocked in this run only by tool transport: Zenodo exposes `CLDD_A.parquet` (13.5 MB, md5 `750b254eed809a38bd14dc80eb4dff81`) and `CLDD_B.parquet` (28.0 MB, md5 `445b8f87afd61d42c72a3af9edbde626`), but the available web path rejects large binary responses and the local runtime has no external network. Do not treat this as dataset unavailability.

DriftLens/STL-10 provenance remains unresolved and lower priority:
- final paper defines UC8 radius 2; public wrapper filenames use radius 2; public notebook executes radius 8; exact author radius-2 HDF5/checkpoint/RNG/output receipt remains unavailable in inspected public surfaces;
- UC8 remains independent-window drift/no-drift classification, not event-level temporal detection.

Exact next action:
1. retry byte-level CLDD-A/B download via an accessible file transport; verify checksums, 360/750 rows, actual seed multiplicity, stream lengths, event arrays, and `max_early/max_delay` values;
2. independently recompute event confusion from `trues/preds/max_early/max_delay` and compare against CapyMOA metrics where available;
3. identify the CapyMOA revision used for Zenodo generation if discoverable, otherwise explicitly pin a version for extensions;
4. run an open-loop held-out-seed comparison using the five published detectors plus source-available CUSUM and a preregistered quantile/persistence controller, tuning only on the 10 training seeds;
5. report event precision/recall/F1, FAR, raw delay and normalized delay using stored window metadata;
6. separately pair event quality with CLDD-B closed-loop continual-learning utility, then transfer the same controllers to one frozen label-free same-label representation-score trace without target retuning;
7. continue broader frontier: DriftLens/LargeMonitor label-free trace, ARROW matched control, adaptive replay, plasticity controls, curriculum selection.

Frontier must remain nonempty.
