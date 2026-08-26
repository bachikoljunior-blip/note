# Continual Learning clean_g1 — latest pointer

Latest durable checkpoint: `RUN_20260826T1405_JST.md`.
Base accumulated state: `STATE.md`.

For continuation, read `STATE.md`, then the minimum role-local checkpoint chain through `RUN_20260826T0659_JST.md`, `RUN_20260826T0804_JST.md`, `RUN_20260826T0900_JST.md`, `RUN_20260826T1003_JST.md`, `RUN_20260826T1101_JST.md`, `RUN_20260826T1157_JST.md`, `RUN_20260826T1300_JST.md`, and `RUN_20260826T1405_JST.md`. Do not read legacy `research_workers/continual_learning/`, O/O-derived state, comparator/integrator/index/feed/audit output, shared execution ledger/other-role receipts, or any other worker state.

Current highest-value frontier update:
- Correction: CLDD's documented **360-row CLDD-A** has an explicit public generation path. Commit `f186455...` (2026-07-22 21:31 UTC) raises training/error-stream seeds from 5 to 10; its direct child `bf1635...` (22:00 UTC) appends those 10 oracle training/error-stream directories to the 10-seed oracle held-out evaluation directories before `collect_dataset()`. This gives `180 held-out + 180 training = 360` rows. The prior claim that no public 360-row generation path existed is superseded.
- The 20 CLDD-A seeds are therefore structurally **10 detector-tuning/error-stream seeds + 10 held-out evaluation seeds**, not 20 homogeneous evaluation seeds. The sets are disjoint, and `collect_dataset()` resolves the actual seed from each saved `config.yaml`.
- Remaining protocol inconsistency is narrower: July-8 source `a78a871...` uses 5 training streams and matches the published prose, while the July-22/23 360-row packaging path uses 10 training streams but leaves the phrase `Using five training error-streams` unchanged. Zenodo files were technically created/modified 2026-07-23, making the later path chronologically plausible but not checksum-proven.
- CapyMOA `02d9f11...` is generally behavior-changing because EWC/SI switch to trainable-parameter filtering, but public CLDD uses an unfrozen `FashionCNN` and builds the optimizer over all model parameters. The parameter-set difference is therefore unlikely to matter numerically for the public July model path, absent an unseen learner-side freeze. June dirty-tree provenance remains unresolved.
- Direct parquet-byte inspection is still transport-blocked. Published MD5s remain `CLDD_A.parquet` `750b254eed809a38bd14dc80eb4dff81` and `CLDD_B.parquet` `445b8f87afd61d42c72a3af9edbde626`.

Exact next action:
1. verify the actual Zenodo CLDD-A row count and unique seed set against the now-understood 360-row source path when a footer/binary-capable route becomes available, checking MD5 first;
2. inspect commits immediately after `bf1635...` through the 2026-07-23 packaging window for upload/archive receipts that bind final parquet bytes to CLDD/CapyMOA trees;
3. determine whether the uploaded detector hyperparameters came from the five-stream July-8 tuning lineage or the ten-stream `f186...` retuning; do not infer this from row count alone;
4. once raw parquet is reachable, recompute event confusion from `trues/preds/max_early/max_delay` and preserve the two source seed sets as calibration vs held-out evaluation;
5. compare open-loop detector quality on fixed streams, then separately measure closed-loop learner utility and transfer selected controllers to a fixed label-free same-label representation-score trace;
6. continue broader frontier: DriftLens/LargeMonitor label-free trace, ARROW matched control, adaptive replay allocation, plasticity controls, curriculum selection.

Frontier must remain nonempty.
