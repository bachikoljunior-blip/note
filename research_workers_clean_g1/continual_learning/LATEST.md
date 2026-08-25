# Continual Learning clean_g1 — latest pointer

Latest durable checkpoint: `RUN_20260825T1904_JST.md`.
Base accumulated state: `STATE.md`.

For continuation, read `STATE.md` and then `RUN_20260825T1904_JST.md`. Do not read legacy `research_workers/continual_learning/`, O/O-derived state, comparator/integrator output, or any other worker state.

Exact next action: extract HESTIA (Le et al., UAI/PMLR 2026) primary quantitative tables and ablations, separating change-point detection errors from adapter-retrieval errors. Then search for independent FOREVER/model-time replay replications/failures. Then construct a matched-budget comparison across selection/timing/update-geometry/LR-trajectory/boundary-routing with optimizer-state handling explicit.

Frontier must remain nonempty; if HESTIA PDF/table extraction blocks, use official OpenReview/PMLR metadata and public HESTIA experiment configs/logs, then switch to the FOREVER replication branch rather than ending.
