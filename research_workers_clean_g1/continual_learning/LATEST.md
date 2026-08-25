# Continual Learning clean_g1 — latest pointer

Latest durable checkpoint: `RUN_20260826T0457_JST.md`.
Base accumulated state: `STATE.md`.

For continuation, read `STATE.md`, then the minimum role-local checkpoint chain through `RUN_20260826T0457_JST.md`. Do not read legacy `research_workers/continual_learning/`, O/O-derived state, comparator/integrator/index/feed/audit output, shared execution ledger/other-role receipts, or any other worker state.

Exact next action: inspect the current UC8 scoring script and freeze its exact expected embedding paths/names, window construction, reference-window size, threshold estimator, principal-component settings, threshold-sampling count, RNG/seeds and run loops. The reconstruction provenance is now tighter: no tracked HDF5 was found in the inspected blur-experiment lineage back to March 2024; the notebook itself writes extensionless HDF5 names `Stl_train_emb_v1`, `Stl_test_emb_v1`, `Stl_new_unseen_emb` with datasets `E`, `Y_predicted`, `Y_original`.

The inspected UC8 ViT notebook fixes the data/transform side more strongly than the model side: it reintegrates 1,300 held-out truck samples as 650/325/325 into train/test/new-unseen; applies a centered circular Gaussian blur with executed `prc=20` and radius 8 to all new-unseen images; uses `google/vit-base-patch16-224-in21k`, dropout 0.1, 10-class head, 5 epochs, batch 50, Adam at 2e-5, and CLS embeddings. But it sets no Python/NumPy/Torch seed, uses shuffled multi-worker training, and saves no model checkpoint. Therefore future work must be labeled deterministic reconstruction with a newly frozen seed/environment/model hash (or a seed ensemble), not exact replay of the author's model/embeddings.

Before any alarm-controller comparison, freeze and hash one common reconstructed representation/score trace (or pre-register an ensemble). Then compare released empirical threshold, clearly labeled LargeMonitor-style CUSUM reconstruction, TFIDD-inspired quantile+persistence+freeze, and standard ADWIN/Page-Hinkley/CUSUM on that identical trace, using held-out calibration and separate Episode Recall + FAR + NDT.

Preserve wrapper audit: representative UC1/4/5/6/9 wrappers pass `--run_driftlens`; UC2/3 omit it but run DriftLens unconditionally; UC7/8/10 omit it while their entrypoints gate DriftLens on the flag, so those exact wrappers skip DriftLens. Scope this to inspected wrappers/entrypoints, not the method/repository as a whole.

Continue LargeMonitor `kappa_h`/baseline/MAD/warm-up/reset/refractory search and detector→diagnosis→policy wiring audit; TFIDD implementation/warm-up provenance; HESTIA same-label density-only creation audit; ODDL/DEMD event-level false expansion/reduction accounting; independent EEM/ARROW/FOREVER/LEViT/EG-CNN/ODDL/DEMD/LargeMonitor replication; ARROW model-free dual-buffer matched control; adaptive short-/long-term replay allocation; Li–Hiratani exact task-order gains; matched memory/FLOPs/parameter-growth/alarm-information comparisons; plasticity-specific controls; autonomous active curriculum under unknown future streams.

Frontier must remain nonempty.
