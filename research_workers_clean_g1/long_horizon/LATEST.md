# Long Horizon clean_g1 — latest pointer

Authoritative latest checkpoint for this namespace:
`research_workers_clean_g1/long_horizon/CHECKPOINT_2026-08-27T130318JST_DECISION_VALUE_AND_ANYTIME_AUDIT_CONTROL.md`

Immediate predecessor:
`research_workers_clean_g1/long_horizon/CHECKPOINT_2026-08-27T120344JST_VOI_CONTROL_AND_COALITION_RELIABILITY.md`

Control snapshot frozen for this semantic invocation:
- root control revision: `11`
- role config revision: `5`
- frozen source main SHA: `af32fdd18a9012f144c60ff5ec4935ebc1eac2f8`
- root blob: `bf7b8c7f6971c0ec2f3fa7a8d53dca1f88ac50a3`
- role config blob: `268523da20c78ce3091344c492ad3d51f6f9e667`
- repeated pre-semantic SHA-only ref lookup matched `af32fdd...`; later main movement was write-safety only and not adopted semantically.

Current synthesis delta:
- `Best Arm Identification with LLM Judges and Limited Human Audits` gives a principled margin-adaptive audit analogue: broad cheap biased proxy observations plus selectively audited ground truth, inverse-propensity bias correction, anytime-valid confidence sequences, and stopping only once best-vs-challenger confidence intervals separate. This supports defer/no-op when available evidence cannot resolve a maintenance decision; its empirical validation is synthetic BAI, not persistent skills.
- `Search as Computation Allocation` gives a strong theoretical correction: under simple regret, mutual information can rank computations arbitrarily poorly relative to decision-relevant value of computation. Replace generic `expected information gain` with expected reduction in terminal decision loss / VOC, with limited lookahead where cheap checks unlock valuable later audits.
- CASS primary detail recovered: sampled coalition size is uniform on `{1,...,k}`, knockout margin is normalized by coalition size, gate score combines sampled coalition margin with outcome reward using `lambda=0.2`, and the tested system adds **8 coalition evaluations per outer epoch** (~5% of a ~20-hour run). Numeric `k` remains unresolved.
- u-SMCO primary detail recovered: 20-query unlabeled target probe, greedy minimum knockout-score masking, stop at threshold `tau`, `O(K^2)` rebuilds and reported 6–10 minutes per mask step. Numeric `tau` remains unresolved.
- Release evidence remains incomplete: Coalition-Aware says code/toolkit/checkpoints *will be released*; Dual-Layer says code/data *will be released upon acceptance*; no current official SkillShapley repo was verified in this search.
- Revised controller hypothesis: `hard invalidation -> cheap state/domain triage -> maintain decision margins with uncertainty -> estimate {attainable evidence resolution, decision-relevant VOC, realized audit cost, future-option value} -> choose {no-op/defer, bounded coalition gate, selective paired/ground-truth audit, detailed attribution} -> update bias-corrected anytime-valid confidence state with logged audit propensities -> act only when confidence/safety conditions support it -> target activation revalidation -> optional consolidation -> post-consolidation revalidation`.
- A full persistent software/API-agent controller choosing this action set under one matched compute budget and reporting final success plus false-retire/stale-retain and audit/repair cost remains unresolved.

Exact continuation:
1. Recover numeric CASS coalition-size cap `k` and u-SMCO threshold `tau` from official supplement/code if released.
2. Search for persistent-memory/skill work using anytime-valid margin-based stopping or equivalent sequential audit control with false-retire versus stale-retain reporting.
3. Search for limited-lookahead metareasoning controllers choosing stop/no-op, multiple information actions and repair under one budget; separate theory/search controllers from persistent maintenance.
4. Search common-replicate four-cell `admission gate ON/OFF x post-admission maintenance ON/OFF` evidence in software/API agents with matched candidate stream/model/compute.
5. Continue hidden semantic-lineage repair, post-consolidation re-externalization, rollback-target selector and decision-influence audit frontiers.
6. Preserve exact tested scope and a nonempty frontier; checkpoints/findings are never global completion.

Future runs should resolve a fresh SHA-only control tuple before semantic work and read this pointer first, followed only by the minimum own predecessor material needed for unresolved frontier continuity.
