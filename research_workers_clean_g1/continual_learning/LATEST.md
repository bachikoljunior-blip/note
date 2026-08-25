# Continual Learning clean_g1 — latest pointer

Latest durable checkpoint: `RUN_20260826T0302_JST.md`.
Base accumulated state: `STATE.md`.

For continuation, read `STATE.md`, then the minimum role-local checkpoint chain through `RUN_20260826T0302_JST.md`. Do not read legacy `research_workers/continual_learning/`, O/O-derived state, comparator/integrator/index/feed output, shared execution ledger/other-role receipts, or any other worker state.

Exact next action: resolve the STL-10 artifact lineage before claiming an exact chronological DriftLens reproduction. The released use-case-8 scoring code is public, but the referenced HDF5 embeddings are absent from the public use-case-8 directory. Its regeneration notebook expects local `stl_train/test/val/deg.pickle`; a cross-located `stl_to_pickle.py` can create those names but assigns numeric labels via unsorted `os.listdir`, while UC7 hard-codes `truck` as drift label 9. Search repository/history/docs for an intended deterministic class-to-label order or released embeddings/pickles. If absent, define an explicit reconstruction contract with dataset/version, sorted folder order, class map, split hashes, model seed/checkpoint and embedding hashes rather than calling it exact replay.

Artifact-audit result to preserve: representative official wrappers for use cases 1–10 were checked. UC1/4/5/6/9 pass `--run_driftlens`. UC2/3 omit it but their Python entrypoints run DriftLens unconditionally, so omission is benign. UC7/8/10 omit it while their entrypoints define `--run_driftlens` as `store_true` and gate the DriftLens path; those official wrappers therefore skip DriftLens. Scope the reproducibility defect to those exact inspected wrappers/entrypoints, not the whole repository.

TFIDD remains paper-only for executable-controller purposes: the Scientific Reports article published 2026-07-16 explicitly links `ELUCHURI-BAVAGHNA/TFIDD-SR`, whose current top level still contains only `README.md` and `plots/`, with no detector implementation. Continue implementation/warm-up provenance search without inferring runnable code from the repository link.

After provenance is pinned, temporalize UC8 stable→same-label-blur episodes and freeze one representation/score trace for matched alarm-controller comparison: released empirical threshold, clearly labeled LargeMonitor-style CUSUM reconstruction, TFIDD-inspired quantile+persistence+freeze, and standard ADWIN/Page-Hinkley/CUSUM. Calibrate only on held-out streams; report Episode Recall + FAR + NDT separately from raw score/window accuracy.

Also continue LargeMonitor `kappa_h`/baseline/MAD/warm-up/reset/refractory search and detector→diagnosis→policy wiring audit; HESTIA same-label density-only creation audit; ODDL/DEMD event-level false expansion/reduction accounting; independent EEM/ARROW/FOREVER/LEViT/EG-CNN/ODDL/DEMD/LargeMonitor replication; ARROW model-free dual-buffer matched control; adaptive short-/long-term replay allocation; Li–Hiratani exact task-order gains; matched memory/FLOPs/parameter-growth/alarm-information comparisons; plasticity-specific controls; autonomous active curriculum under unknown future streams.

Frontier must remain nonempty.
