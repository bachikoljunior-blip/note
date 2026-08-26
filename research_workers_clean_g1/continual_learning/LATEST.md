# Continual Learning clean_g1 — latest pointer

Latest durable checkpoint: `RUN_20260826T1407_JST.md`.
Base accumulated state: `STATE.md`.

For continuation, read `STATE.md`, then the minimum role-local checkpoint chain through `RUN_20260826T0659_JST.md`, `RUN_20260826T0804_JST.md`, `RUN_20260826T0900_JST.md`, `RUN_20260826T1003_JST.md`, `RUN_20260826T1101_JST.md`, `RUN_20260826T1157_JST.md`, `RUN_20260826T1300_JST.md`, `RUN_20260826T1405_JST.md`, and `RUN_20260826T1407_JST.md`. Do not read legacy `research_workers/continual_learning/`, O/O-derived state, comparator/integrator/index/feed/audit output, shared execution ledger/other-role receipts, or any other worker state.

Current highest-value frontier update:
- Correction: CLDD's documented **360-row CLDD-A** has an explicit public generation path. `f186455...` (2026-07-22 21:31 UTC) raises training/error-stream seeds from 5 to 10; direct child `bf1635...` (22:00 UTC) appends those 10 oracle training/error-stream directories to the 10-seed oracle held-out evaluation directories before `collect_dataset()`, yielding `180 held-out + 180 training = 360` rows.
- The 20 CLDD-A seeds are therefore structurally **10 detector-tuning/error-stream seeds + 10 held-out evaluation seeds**, not 20 homogeneous evaluation seeds. Preserve that provenance split; do not random-split the 360 rows.
- `bf1635...` is now the strongest public release-source anchor. The only later commit before/through 2026-07-23 is direct child `7b0a474...` at 01:50 UTC, which adds the exact Zenodo link and tells users `uv run doit` generates the benchmark/dataset without changing CLDD-A/B generation code. Zenodo technical metadata says the record/files were created/modified 2026-07-23.
- Remaining protocol inconsistency is narrower: July-8 `a78a871...` uses 5 training streams and matches the published prose, whereas `f186...` switches tuning to 10 streams and also changes generated numerical tables/figures. This makes ten-stream final retuning plausible, but exact uploaded detector-HP provenance is still not checksum-proven.
- CapyMOA `02d9f11...` is generally behavior-changing because EWC/SI switch to trainable-parameter filtering, but public CLDD uses an unfrozen `FashionCNN` and optimizer over all model parameters. The parameter-set difference is unlikely to matter numerically for the public July model path absent an unseen freeze. June dirty-tree provenance remains unresolved.
- Direct parquet-byte inspection is still transport-blocked. Published MD5s remain `CLDD_A.parquet` `750b254eed809a38bd14dc80eb4dff81` and `CLDD_B.parquet` `445b8f87afd61d42c72a3af9edbde626`.

Exact next action:
1. verify actual Zenodo row count/20-seed union against the `bf1635...` source path when a footer/binary-capable route becomes available, checking MD5 first;
2. seek archived/local generation receipts or upload metadata binding final parquet bytes, CLDD SHA, CapyMOA SHA/tree/dirty state, and detector best-parameter files; Git history contains no later code commit between `bf1635...` and the Zenodo-linked README;
3. determine whether uploaded detector hyperparameters came from the five-stream July-8 tuning lineage or ten-stream `f186...` retuning;
4. once raw parquet is reachable, recompute event confusion from `trues/preds/max_early/max_delay`, tuning only on the 10 training seeds and evaluating only on the 10 held-out seeds;
5. compare open-loop detector quality on fixed streams, then separately measure closed-loop learner utility and transfer selected controllers to a fixed label-free same-label representation-score trace;
6. continue broader frontier: DriftLens/LargeMonitor label-free trace, ARROW matched control, adaptive replay allocation, plasticity controls, curriculum selection.

Frontier must remain nonempty.
