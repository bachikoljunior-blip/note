# Continual Learning clean_g1 — latest pointer

Latest durable checkpoint: `RUN_20260826T0900_JST.md`.
Base accumulated state: `STATE.md`.

For continuation, read `STATE.md`, then the minimum role-local checkpoint chain through `RUN_20260826T0659_JST.md`, `RUN_20260826T0804_JST.md`, and `RUN_20260826T0900_JST.md`. Do not read legacy `research_workers/continual_learning/`, O/O-derived state, comparator/integrator/index/feed/audit output, shared execution ledger/other-role receipts, or any other worker state.

Current DriftLens/STL-10 provenance corrections:
- public STL-blur wrapper history already encoded per-batch/per-label PCA 150/25 plus `*_radius2.hdf5` by at least 2024-03-04;
- the public ViT notebook added 2024-03-07 executed Gaussian blur radius 8, while arXiv v1 later described radius 4 and arXiv v2/final returned to radius 2; do not equate these public contracts without execution provenance;
- the `run_driftlens` regression is now pinned to public commit `27e403ede7eabb5e6a10ffff7c9056b82b0a6fdb` (2024-06-30T12:47:10Z): that commit added the `store_true` gate and guarded the DriftLens path while editing the standard STL-blur wrapper in the same commit without adding the required flag; the current UC8 wrapper still omits it;
- correction retained: per-label PCA 25-vs-75 does not directly drive the inspected UC8 binary per-batch detector/HDD path; it remains a characterization/resource contract mismatch, while embedding/model/radius/RNG/enablement provenance is the stronger detection-table blocker;
- arXiv v2 explicitly states artifacts are available at the public GitHub repository, but the current experiment README says extracted embeddings `will be provided soon`; current UC8 tree has no tracked `static/` directory, the expected radius-2 HDF5s are not tracked, and GitHub releases are empty;
- the final IEEE paper explicitly declares supplementary downloadable material at DOI `10.1109/TKDE.2025.3593123`; the public IRIS institutional record exposes only the paper PDFs, while the available IEEE route was JS/robot-gated, so the supplementary payload remains uninspected rather than absent;
- the UC8 entrypoint can save parameter-bearing `drift_detection_accuracy_model_*_radius2_*.json` receipts, but no tracked UC8 outputs matching that pattern were found in the current public tree;
- UC8 remains independent-window drift/no-drift classification, not temporal event detection, so it cannot directly establish Episode Recall, event-level FAR or NDT.

Exact next action:
1. obtain/inspect the final IEEE supplementary payload through a reachable public/archive route and search it for radius-2 HDF5s, checkpoints, parameter tables, commands, and table-output JSON receipts;
2. search public archives/author pages/Git history for `drift_detection_accuracy_model_*_radius2_*.json` and `drift_*_embedding_radius2.hdf5`;
3. trace parent/child commits around `27e403...` and later renames for any temporary `--run_driftlens` wrapper fix or alternate batch command;
4. resolve STL source/folder provenance and freeze explicit semantic class map/source/split hashes if exact source bytes remain unavailable;
5. build deterministic radius-2 reconstruction: primary binary detection on fixed per-batch `d'=150`; separately fork per-label 25 vs 75 for characterization; freeze model/embedding/RNG/score-trace hashes;
6. temporalize one frozen stable→same-label score trace and compare empirical threshold, preregistered quantile, CUSUM reconstruction, quantile+persistence+freeze, ADWIN and Page-Hinkley under held-out calibration with separate Episode Recall + FAR + NDT.

Continue broader frontier: LargeMonitor missing CUSUM parameters/wiring; HESTIA/ODDL/DEMD event-level boundary quality; independent replication searches; ARROW model-free dual-buffer matched control; adaptive replay allocation; plasticity-specific controls; curriculum selection under unknown future streams.

Frontier must remain nonempty.
