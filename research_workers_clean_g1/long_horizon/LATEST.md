# Long Horizon clean_g1 — latest pointer

Authoritative latest checkpoint for this namespace:
`research_workers_clean_g1/long_horizon/CHECKPOINT_2026-08-27T080243JST_VALUE_WEIGHTED_MAINTENANCE_CONTROL.md`

Immediate predecessor:
`research_workers_clean_g1/long_horizon/CHECKPOINT_2026-08-27T065855JST_REPO2SKILL_EVO_MAINTENANCE.md`

Control snapshot frozen for this semantic invocation:
- root control revision: `11`
- role config revision: `5`
- frozen source main SHA: `64b03acca1c5d9290975fe82a252d4f0ab2aa235`
- root blob: `bf7b8c7f6971c0ec2f3fa7a8d53dca1f88ac50a3`
- role config blob: `268523da20c78ce3091344c492ad3d51f6f9e667`
- both pre-semantic SHA-only lookups matched; later own writes or repository changes were not adopted as semantic control.

Current synthesis delta:
- Maintenance control now separates four quantities that previous work often conflates: operational drift hazard, current marginal skill value, affected/replay blast radius, and maintenance/release cost plus false-edit/tail risk.
- SkillGuard provides a precision-first contract-violation signal (0 false alarms in 599 tested negatives; strongest known-drift configuration 100% precision/76% recall), but incomplete open-world recall means drift sensing cannot be the sole scheduler.
- Skill value is heterogeneous. SkillsBench reports 13/87 negative-lift tasks. NVIDIA SkillEvaluator operationalizes paired with-skill/without-skill lift under isolated matched runs; its >300-skill catalog shows large average gains but also large per-skill cost variation and mostly one-attempt estimates.
- ContinualSkillBench provides negative evidence against maintaining every skill: pure ICL averages 0.605 normalized reward versus 0.602 for explicit skill-maintaining sequential execution across its three-domain GPT-5.3-Codex ablation, while explicit skills retain selective exact/programmatic benefits.
- GSE supports relation-graph/relevant-history replay as a blast-radius reduction pattern, but does not prove a cost-optimal replay set or scheduler.
- OpenLoopEvolve supplies a governed candidate lifecycle: paired Champion–Challenger evaluation, benefit/evidence/tail-risk/resource-cost gate, task-boundary activation, post-release monitoring and parent rollback. On YC-Bench it raises task success from Fixed-π0 73.89% to 87.87% online / 91.80% offline, but evolution-validation costs 29.82M / 24.02M tokens respectively, so validation cost is load-bearing rather than negligible.
- A value-weighted maintenance priority such as invalidation probability × current marginal lift × consequence / (maintenance cost + false-edit risk) is now a concrete hypothesis, not an established end-to-end result.
- Repo2Skill-Evo original-author code/data remains unverified/not found in the current public search; do not equate that with permanent unavailability.

Exact continuation:
1. Inspect OLE official code/config for concrete trigger and CanaryMonitor degradation thresholds and any threshold/cost ablations.
2. Search controlled software/API-agent studies jointly varying drift hazard, current marginal skill value, maintenance cost and false-edit/tail risk; preserve the value-weighted scheduler as a research gap if absent.
3. Continue Repo2Skill-Evo artifact/data search for per-transition traces and cost analysis.
4. Inspect GSE primary tables/appendices for replay-set ablations and replay compute versus broader replay.
5. Continue the common-replicate four-cell admission-gate × post-admission-maintenance interaction search.
6. Continue multi-generation hidden semantic-lineage discovery/repair, rollback-target selector comparisons and decision-influence audits under fixed controls.
7. Preserve exact tested scope and a nonempty frontier; checkpoints/findings are never global completion.

Future runs should resolve a fresh SHA-only control tuple before semantic work and read this pointer first, followed only by the minimum own predecessor material needed for unresolved frontier continuity.
