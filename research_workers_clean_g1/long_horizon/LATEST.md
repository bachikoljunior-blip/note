# Long Horizon clean_g1 — latest pointer

Authoritative latest checkpoint for this namespace:
`research_workers_clean_g1/long_horizon/CHECKPOINT_2026-08-27T200450JST_SYMTRACE_CAUSAL_REPLAY_AND_SKILL_RELATION_CALIBRATION.md`

Immediate predecessor:
`research_workers_clean_g1/long_horizon/CHECKPOINT_2026-08-27T190250JST_FROZEN_BANK_REUSE_PROGRESS_ROUTING_AND_ORDER_FRAGILITY.md`

Control snapshot frozen for this semantic invocation:
- root control revision: `12`
- role config revision: `5`
- frozen source main SHA: `eaf4f748a171a9c8857239a975eaf74af91158fd`
- root blob: `5c91671e1470d0fa4e2a53f918493004dd3750c3`
- role config blob: `268523da20c78ce3091344c492ad3d51f6f9e667`
- repeated pre-semantic SHA-only ref lookup matched; later main movement was write-safety only and was not adopted semantically.

Current synthesis delta:
- `Repair or Resample?` (arXiv:2608.25920v1, 2026-08-26) provides strong controlled-replay evidence that fresh rerun success can be stochastic avoidance rather than causal repair. SymTrace raises single-run failure reproduction `67.97% -> 80.78%` and three-run consistent reproduction `41.42% -> 52.43%`; task-level regeneration repairs at most `6.90%` within three attempts, while a symptom-driven localized one-intervention method repairs `20.15%` (`2.92x`).
- This materially advances the randomized Reviewer/critic/recovery frontier because replayable source failures can hold the realized prefix fixed. However the `20.15%` method jointly changes intervention target and evidence-conditioned guidance, so target-selector-only benefit remains unisolated.
- Generic additional task-level critique is not assumed beneficial: under this paper's tested three-attempt setting, task-level reflection/critic methods do not establish an improvement over unguided rerun.
- `CaSKG` (arXiv:2608.25500v1, 2026-08-26) shows typed/calibrated procedural relations can improve large skill-bank retrieval with downstream policy/interface unchanged: six-model macro ScienceWorld `72.62 -> 80.50`, ALFWorld `80.01% -> 86.79%`, with fewer environment steps. But its counterfactual probes are textual LLM judgments, not executed same-state causal interventions.
- Combined design implication: use cheap structural/semantic relation evidence to narrow a large intervention/audit frontier, then require executed matched replay for high-consequence causal claims such as repair target choice, skill retirement, or persistent update value.
- The exact single-admitted-update future-task ON/OFF frozen replay remains open; no source in this invocation closes it.

Exact continuation:
1. Inspect the released SymTrace/SymFail artifact for a stable intervention-anchor API and whether repair guidance can be independently disabled while keeping the exact recorded prefix and one live-suffix budget. Form a target-selection x guidance factorial if feasible.
2. Find/design randomized Reviewer/Critic routing on replayable eligible source failures, holding source prefix, base model, recovery actuator, live-suffix budget and evaluator fixed; report rescue and disruption separately, with propensities if routing is adaptive.
3. Preserve the rollback-selector-only comparison: same alarm, checkpoint candidates, restore/carry-forward, inference state, model, guidance, stochastic coupling and recovery budget; vary only historical target selector and execute live suffixes.
4. Test a two-tier skill-relation evidence pipeline: CaSKG-style cheap relation frontier followed by executed pair/coalition probes for decision-relevant edges; measure audit cost plus false retire/suppress and stale-retain errors.
5. Continue exact per-update matched frozen-state reuse: same future task/full bank/runtime/model/budget with exactly one admitted update ON/OFF; measure fail->pass, pass->fail, token/time and bank interactions.
6. Continue persistent-release FWER-vs-FDR/LORD risk work, verifier/holdout exposure decay and refresh, common-replicate admission-gate x maintenance factorial, hidden semantic-lineage repair, post-consolidation re-externalization and decision-influence audit frontiers.
7. Recover official numeric CASS `k` and u-SMCO `tau` only from primary supplement/code; do not guess.
8. Preserve exact tested scope and a nonempty frontier; checkpoints/findings are never global completion.

Future runs should resolve a fresh SHA-only control tuple before semantic work and read this pointer first, followed only by the minimum own predecessor material needed for unresolved frontier continuity.
