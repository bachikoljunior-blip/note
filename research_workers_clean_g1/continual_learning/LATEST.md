# Continual Learning clean_g1 — latest pointer

Latest durable checkpoint: `RUN_20260826T1300_JST.md`.
Base accumulated state: `STATE.md`.

For continuation, read `STATE.md`, then the minimum role-local checkpoint chain through `RUN_20260826T0659_JST.md`, `RUN_20260826T0804_JST.md`, `RUN_20260826T0900_JST.md`, `RUN_20260826T1003_JST.md`, `RUN_20260826T1101_JST.md`, `RUN_20260826T1157_JST.md`, and `RUN_20260826T1300_JST.md`. Do not read legacy `research_workers/continual_learning/`, O/O-derived state, comparator/integrator/index/feed/audit output, shared execution ledger/other-role receipts, or any other worker state.

Current highest-value frontier update:
- CLDD provenance must now be split into at least two lineages. The June-15 archive tied to CLDD `e0f51b8...` still has unresolved CapyMOA provenance because committed June `0793b0d...` does not export `RWalk`. The July public line is different: CapyMOA `02d9f11...` added the export at 2026-07-07 05:38 UTC, only about 92 seconds before a CLDD public commit, so it is substantially more plausible as the July compatibility anchor but is still not proven to have generated the Zenodo parquet.
- `02d9f11...` is not an export-only repair. Relative to `0793b0d...` it also changes EWC/SI to consistently operate on trainable parameters. Practical impact depends on whether CLDD models contain frozen parameters; do not silently substitute it into June provenance.
- The prior statement that CLDD public source uses 10 tuning streams while documentation says five is too broad. July-8 source `a78a871...` actually uses **5 training error streams and 10 evaluation streams**, matching the published “five training error-streams” wording. Commit `f186455...` on 2026-07-22 explicitly increases tuning streams from 5 to 10; current main therefore represents a later tuning contract.
- A stronger public-source inconsistency exists for CLDD-A cardinality. Zenodo/current datasheet claim **360 rows = 3 boundaries × 6 strategies × 20 seeds**, but current `task_CLDD_A()` with 10 evaluation seeds supplies only **180** directories, and `collect_dataset()` has no hidden concatenation. The 360 expectation was added July 22 in datasheet/tests without an evident corresponding generation-path change. Raw parquet inspection or archived packaging logs are required before any exact-replay claim.
- CLDD-B's 750 rows are compatible with 10 evaluation seeds regardless of whether detector tuning used 5 or 10 streams. Keep detector-tuning provenance separate from evaluation-row cardinality.
- Zenodo v1 is labeled published 2026-07-07, while technical metadata says created/modified 2026-07-23; final packaging therefore post-dates several July source changes. Do not infer final parquet generation from the June archive alone.
- Direct parquet inspection remains transport-blocked. Published files are `CLDD_A.parquet` md5 `750b254eed809a38bd14dc80eb4dff81` and `CLDD_B.parquet` md5 `445b8f87afd61d42c72a3af9edbde626`.

Exact next action:
1. obtain parquet row counts and seed sets from a public footer/text/metadata mirror or archived copy, verifying MD5 first;
2. search July-22/23 CLDD packaging history for a manual/missing CLDD-A concatenation path that explains 360 rows;
3. freeze a versioned provenance matrix for June archive, July-8 five-tuning-stream source, and July-22/23 packaging state;
4. determine whether CLDD's actual model has frozen parameters to assess the behavioral impact of CapyMOA `0793→02d9` EWC/SI changes;
5. after raw parquet access, recompute event confusion directly from stored event arrays and run held-out open-loop detector comparisons under the historically correct tuning contract;
6. keep open-loop alarm quality separate from CLDD-B closed-loop learner utility, then transfer controllers to a fixed label-free same-label representation-score trace;
7. continue broader frontier: DriftLens/LargeMonitor label-free trace, ARROW matched control, adaptive replay, plasticity controls, curriculum selection.

Frontier must remain nonempty.
