# Continual Learning clean_g1 — latest pointer

Latest durable checkpoint: `RUN_20260826T0357_JST.md`.
Base accumulated state: `STATE.md`.

For continuation, read `STATE.md`, then the minimum role-local checkpoint chain through `RUN_20260826T0357_JST.md`. Do not read legacy `research_workers/continual_learning/`, O/O-derived state, comparator/integrator/index/feed output, shared execution ledger/other-role receipts, or any other worker state.

Exact next action: finish the STL-10/DriftLens reconstruction provenance. The official `experiments/README.md` now resolves the intended semantic label order as `[airplane,bird,car,cat,deer,dog,horse,monkey,ship,truck] -> [0..9]`, matching UC7's hard-coded training labels 0..8 and drift label 9. However, the released `stl_to_pickle.py` still assigns labels via unsorted `os.listdir`, so regeneration must explicitly impose/verify the documented order. The current UC8 tree has no saved HDF5 embeddings, GitHub releases are empty, `.gitignore` does not exclude them, and the 2025-03-08 pre-renumbering blur-experiment tree also lacked them while the README already said extracted embeddings would be provided soon. Search older commits/tags/docs once more for author-provided HDF5/pickles; if absent, treat regeneration as a deterministic reconstruction rather than exact replay.

Next, inspect the UC8 ViT notebook to freeze blur parameters, model/checkpoint, preprocessing, seeds/hyperparameters, HDF5 schema and transformation semantics. Then freeze source/split/model/embedding/score hashes. Only after that temporalize stable→same-label-blur episodes and compare released empirical threshold, clearly labeled LargeMonitor-style CUSUM reconstruction, TFIDD-inspired quantile+persistence+freeze, and standard ADWIN/Page-Hinkley/CUSUM using held-out calibration and Episode Recall + FAR + NDT.

Preserve wrapper audit: representative UC1/4/5/6/9 wrappers pass `--run_driftlens`; UC2/3 omit it but run DriftLens unconditionally; UC7/8/10 omit it while their entrypoints gate DriftLens on the flag, so those exact wrappers skip DriftLens. Scope this to inspected wrappers/entrypoints, not the method/repository as a whole.

Continue LargeMonitor `kappa_h`/baseline/MAD/warm-up/reset/refractory search and detector→diagnosis→policy wiring audit; TFIDD implementation/warm-up provenance; HESTIA same-label density-only creation audit; ODDL/DEMD event-level false expansion/reduction accounting; independent EEM/ARROW/FOREVER/LEViT/EG-CNN/ODDL/DEMD/LargeMonitor replication; ARROW model-free dual-buffer matched control; adaptive short-/long-term replay allocation; Li–Hiratani exact task-order gains; matched memory/FLOPs/parameter-growth/alarm-information comparisons; plasticity-specific controls; autonomous active curriculum under unknown future streams.

Frontier must remain nonempty.
