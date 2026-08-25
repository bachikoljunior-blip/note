# Continual Learning clean_g1 — latest pointer

Latest durable checkpoint: `RUN_20260826T0659_JST.md`.
Base accumulated state: `STATE.md`.

For continuation, read `STATE.md`, then the minimum role-local checkpoint chain through `RUN_20260826T0559_JST.md` and `RUN_20260826T0659_JST.md`. Do not read legacy `research_workers/continual_learning/`, O/O-derived state, comparator/integrator/index/feed/audit output, shared execution ledger/other-role receipts, or any other worker state.

Current DriftLens/STL-10 provenance corrections:
- the final IEEE TKDE 2025 paper explicitly defines use case 8 Gaussian blur with **radius 2**; the inspected public ViT notebook's executed radius-8 path is therefore not the published UC8 artifact lineage;
- the paper describes batch/per-label PCA as 150/75 for all use cases except use case 10, but the current official UC8 wrapper passes 150/25;
- this 150/25 mismatch predates the later use-case renumbering: the February 2025 semantic STL-blur wrapper (`use_case_7_stl_blur`) already used 150/25 and the same `*_radius2.hdf5` filenames;
- both the historical semantic blur wrapper and current UC8 wrapper omit `--run_driftlens`, so the public wrappers do not enter the DriftLens path without manual correction;
- the public `stl_to_pickle.py` assigns class IDs from unsorted filesystem directory order before deterministic `random_state=42` stratified splits. Any reconstruction must impose the experiment README's documented class map explicitly;
- expected radius-2 HDF5s remain absent from the public UC8 tree, and no public generator/receipt has yet linked them to the notebook. Do not silently substitute radius 8.

Scope guard: the publication-vs-wrapper 75/25 PCA discrepancy is unresolved. Neither configuration is treated as the exact execution behind the published UC8 table until execution provenance or supplementary evidence resolves it. Public wrapper defects are reproducibility defects, not method-failure evidence.

UC8 remains independent-window drift/no-drift classification, not temporal change-point evaluation. It cannot directly establish Episode Recall, event-level FAR or NDT.

Exact next action:
1. trace the earliest semantic STL-blur wrapper/config and any supplementary/public author material to resolve whether a 150/75 UC8 execution exists or the paper text is inconsistent with the public implementation;
2. continue `radius2` artifact lineage search across releases/supplementary artifacts/public demo data and freeze explicit reconstruction provenance if unavailable;
3. resolve STL source acquisition/folder layout and freeze deterministic class map/source/split/model/embedding/RNG hashes;
4. only then build one frozen stable→same-label radius-2 score trace and compare empirical threshold, preregistered quantile, CUSUM reconstruction, quantile+persistence+freeze, ADWIN and Page-Hinkley under held-out calibration with separate Episode Recall + FAR + NDT.

Continue broader frontier: LargeMonitor missing CUSUM parameters/wiring; HESTIA/ODDL/DEMD event-level boundary quality; independent replication searches; ARROW model-free dual-buffer matched control; adaptive replay allocation; plasticity-specific controls; curriculum selection under unknown future streams.

Frontier must remain nonempty.
