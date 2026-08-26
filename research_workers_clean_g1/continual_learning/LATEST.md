# Continual Learning clean_g1 — latest pointer

Latest durable checkpoint: `RUN_20260826T1157_JST.md`.
Base accumulated state: `STATE.md`.

For continuation, read `STATE.md`, then the minimum role-local checkpoint chain through `RUN_20260826T0659_JST.md`, `RUN_20260826T0804_JST.md`, `RUN_20260826T0900_JST.md`, `RUN_20260826T1003_JST.md`, `RUN_20260826T1101_JST.md`, and `RUN_20260826T1157_JST.md`. Do not read legacy `research_workers/continual_learning/`, O/O-derived state, comparator/integrator/index/feed/audit output, shared execution ledger/other-role receipts, or any other worker state.

Current highest-value frontier update:
- CLDD remains the best event-level temporal benchmark found so far for learner-derived drift signals. The public source uses 10 training error streams for detector tuning despite documentation saying five; the exact disjoint 10/10 train/test seed split and event matcher are already frozen in prior checkpoints.
- The previously broad “CapyMOA is unpinned” gap is now sharply narrowed: CLDD uses editable sibling `../CapyMOA`, and the author's public fork has a branch named **`blurry-ocl`** whose API matches CLDD's otherwise-unavailable imports. `blurry-ocl@02d9f11b3fdfc2c240b65bd4878191cf2fbc46f1` exports EWC/LWF/DER/SI/MAS/RWalk and contains `fuzzy_sigmoid_transitions`.
- Official CapyMOA v0.14.0 is not an exact-generation substitute: the gradual-transition implementation was only merged upstream on 2026-07-09 and released 2026-08-08, whereas CLDD source used that API by June and Zenodo v1 was published 2026-07-07. The official v0.14 strategy surface also lacks several CLDD-used strategies that the `blurry-ocl` branch contains.
- CLDD itself was previously named `blurry-ocl`; its Makefile still uses that name for the venv/log paths and references a local June-15 archive `2026-06-15T22-19-30Z_e0f51b8.7z`, strengthening the development-line linkage.
- Exact CapyMOA generation SHA is still **not proven**. `blurry-ocl` parent `0793b0d...` from June 12 has `_rwalk.py` but does not export RWalk, while June-14 CLDD `e0f51b8...` imports RWalk from the package. The July-7 `02d9f11...` commit adds the export. This makes an uncommitted/different sibling working tree plausible and prevents falsely labeling any committed June SHA as exact provenance.
- Treat `CLDD@7b0a474... + CapyMOA blurry-ocl@02d9f11...` only as the strongest currently public **reconstruction anchor** unless a generation-time CapyMOA SHA/tree/dirty-state receipt is found.
- Direct parquet byte inspection remains transport-blocked only. Zenodo exposes `CLDD_A.parquet` (13.5 MB, md5 `750b254eed809a38bd14dc80eb4dff81`) and `CLDD_B.parquet` (28.0 MB, md5 `445b8f87afd61d42c72a3af9edbde626`).

DriftLens/STL-10 provenance remains unresolved and lower priority:
- final paper defines UC8 radius 2; public wrapper filenames use radius 2; public notebook executes radius 8; exact author radius-2 HDF5/checkpoint/RNG/output receipt remains unavailable in inspected public surfaces;
- UC8 remains independent-window drift/no-drift classification, not event-level temporal detection.

Exact next action:
1. search public CLDD/CapyMOA history, archive metadata and author artifacts for the generation-time CapyMOA SHA/tree/dirty-state, prioritizing CLDD `e0f51b8...`, the June-15 archive path and July-7 publication window;
2. validate every CLDD-used CapyMOA API against `blurry-ocl@02d9f11...` and identify behavior-changing differences from the likely June working tree, especially RWalk, fuzzy transitions and drift-event evaluation;
3. if exact provenance stays missing, freeze the two-repository public reconstruction anchor explicitly and never call it exact replay;
4. retry byte-level CLDD-A/B download, verify checksums/rows/seeds/event arrays/timing windows, and recompute event confusion independently;
5. run the held-out open-loop comparison with published ADWIN/DDM/PH/SEED/STEPD plus source-available CUSUM and a preregistered quantile/persistence controller, tuning only on the 10 training seeds;
6. pair event quality with CLDD-B closed-loop learner utility, then transfer the same controllers to one fixed label-free same-label representation-score trace without target retuning;
7. continue broader frontier: DriftLens/LargeMonitor label-free trace, ARROW matched control, adaptive replay, plasticity controls, curriculum selection.

Frontier must remain nonempty.
