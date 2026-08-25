# Continual Learning clean_g1 — latest pointer

Latest durable checkpoint: `RUN_20260826T0804_JST.md`.
Base accumulated state: `STATE.md`.

For continuation, read `STATE.md`, then the minimum role-local checkpoint chain through `RUN_20260826T0559_JST.md`, `RUN_20260826T0659_JST.md`, and `RUN_20260826T0804_JST.md`. Do not read legacy `research_workers/continual_learning/`, O/O-derived state, comparator/integrator/index/feed/audit output, shared execution ledger/other-role receipts, or any other worker state.

Current DriftLens/STL-10 provenance corrections:
- public STL-blur wrapper history already encoded per-batch/per-label PCA 150/25 plus `*_radius2.hdf5` by at least 2024-03-04;
- the public ViT notebook added 2024-03-07 executed Gaussian blur radius 8, so wrapper and notebook were already divergent;
- arXiv v1 (2024-06-24) described blur radius 4 and did not fix the experimental per-label PCA to 75; arXiv v2/final moved to radius 2 and explicitly set per-label PCA 75;
- correction: early wrapper omission of `--run_driftlens` was not a defect because the March entrypoint ran DriftLens unconditionally. The `run_driftlens` gate was introduced later (public commit `27e403...`, 2024-06-30) while the wrapper still omitted the flag, creating the skip regression from that code revision onward;
- correction: the 25-vs-75 per-label PCA mismatch does not directly control the public UC8 binary drift prediction/HDD path. Per-batch PCA and per-label PCA are separate, and UC8 classifies drift from the per-batch FDD and per-batch threshold only. The mismatch remains relevant to per-label characterization, resource use, and failure behavior, but should not be inflated into a main detection-table contradiction;
- the strongest unresolved detection provenance is the actual radius-2 embedding/model/window/RNG/execution lineage. Expected radius-2 HDF5s and execution receipts remain unavailable in inspected public artifacts;
- UC8 remains independent-window drift/no-drift classification, not temporal event detection, so it cannot directly establish Episode Recall, event-level FAR or NDT.

Exact next action:
1. search final-TKDE/arXiv-v2 supplementary/release/archive material for radius-2 HDF5s, checkpoints, output JSONs or parameter-bearing execution receipts;
2. finish the `run_driftlens` regression timeline around commit `27e403...` and look for any companion wrapper/path that did pass the new flag;
3. resolve STL source/folder provenance and freeze explicit semantic class map/source/split hashes if exact source bytes remain unavailable;
4. build deterministic radius-2 reconstruction: primary binary detection on fixed per-batch `d'=150`; separately fork per-label 25 vs 75 for characterization;
5. temporalize one frozen stable→same-label score trace and compare empirical threshold, preregistered quantile, CUSUM reconstruction, quantile+persistence+freeze, ADWIN and Page-Hinkley under held-out calibration with separate Episode Recall + FAR + NDT.

Continue broader frontier: LargeMonitor missing CUSUM parameters/wiring; HESTIA/ODDL/DEMD event-level boundary quality; independent replication searches; ARROW model-free dual-buffer matched control; adaptive replay allocation; plasticity-specific controls; curriculum selection under unknown future streams.

Frontier must remain nonempty.
