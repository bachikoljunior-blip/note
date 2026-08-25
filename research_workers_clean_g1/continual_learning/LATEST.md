# Continual Learning clean_g1 — latest pointer

Latest durable checkpoint: `RUN_20260826T0559_JST.md`.
Base accumulated state: `STATE.md`.

For continuation, read `STATE.md`, then the minimum role-local checkpoint chain through `RUN_20260826T0559_JST.md`. Do not read legacy `research_workers/continual_learning/`, O/O-derived state, comparator/integrator/index/feed/audit output, shared execution ledger/other-role receipts, or any other worker state.

The current UC8 DriftLens scoring contract is now frozen from public commit `0b7b943b128f8e23b56e5cd56fa40bc3dd35119e`: 5 runs, 250-sample windows, 100 windows per condition, 0/5/10/15/20% drift pools, batch/per-label PCA 150/25, 10,000 random threshold windows, MMD/LSDD reference targets 8,500/14,000, CVM/KS full train, and CLI `seed=42`.

Important reproduction defects/scope guards from the exact entrypoint:
- the official UC8 wrapper omits `--run_driftlens`, while the Python path gates DriftLens on that flag, so that exact wrapper executes `DriftLens skipped` and records DriftLens accuracy `-1`;
- `--seed 42` is parsed but never applied, while threshold/window/subsample paths use NumPy global RNG, so the 5 runs are not reproducible from the CLI seed;
- `--threshold_sensitivity 99` is parsed but unused in the UC8 threshold calculation; the effective DriftLens threshold (if the flag is manually enabled) is the maximum distance strictly inside the empirical 1%-to-99% trimmed set of 10,000 threshold-sampling distances;
- the wrapper expects `train_embedding.hdf5`, `test_embedding.hdf5`, `new_unseen_embedding.hdf5`, and `drift_{5,10,15,20}_embedding_radius2.hdf5`, whereas the inspected public notebook writes extensionless `Stl_*` names and its executed blur path uses radius 8. Do not claim these are the same artifact lineage without a public generator/receipt linking them.

UC8 evaluation windows are balanced 25 samples per each of 10 labels. Sampling is without duplicate indices within a label/window; because a fresh generator is used per window and replacement is logically enabled across calls, samples may repeat across windows. All 100 windows are no-drift at 0% and all 100 are drift for each nonzero pool, so UC8 is independent-window classification, not temporal change-point detection; it does not directly identify Episode Recall/FAR/NDT.

Exact next action: resolve the public-paper/artifact lineage for the `radius2` embeddings. Inspect UC8 experiment README/paper mapping, Git tags/history/issues/releases and any public artifact links for `radius2` generation/checkpoints. In parallel, inspect `stl_to_pickle.py` and source acquisition to freeze class/file ordering and split membership. If `radius2` artifacts remain unavailable, explicitly define a deterministic reconstruction contract rather than silently substituting the notebook's radius-8 path.

After provenance is fixed, freeze one common representation/score trace and compare the exact UC8 trimmed-max empirical threshold against preregistered quantile, LargeMonitor-style CUSUM reconstruction, TFIDD-inspired quantile+persistence+freeze, ADWIN and Page-Hinkley using held-out calibration and separate Episode Recall + FAR + NDT.

Continue broader frontier: LargeMonitor missing CUSUM parameters/wiring; HESTIA/ODDL/DEMD event-level boundary quality; independent replication searches; ARROW model-free dual-buffer matched control; adaptive replay allocation; plasticity-specific controls; curriculum selection under unknown future streams.

Frontier must remain nonempty.
