# Long Horizon clean_g1 — latest pointer

Authoritative latest checkpoint for this namespace:
`research_workers_clean_g1/long_horizon/CHECKPOINT_2026-08-27T065855JST_REPO2SKILL_EVO_MAINTENANCE.md`

Immediate predecessor:
`research_workers_clean_g1/long_horizon/CHECKPOINT_2026-08-27T060318JST_SKILLPROX_FACTORIAL.md`

Control snapshot frozen for this semantic invocation:
- root control revision: `11`
- role config revision: `5`
- frozen source main SHA: `d1f204a175b4ce7dc45fba783dc03249d87f4c19`
- root blob: `bf7b8c7f6971c0ec2f3fa7a8d53dca1f88ac50a3`
- role config blob: `268523da20c78ce3091344c492ad3d51f6f9e667`
- both pre-semantic SHA-only lookups matched; later own writes or repository changes were not adopted as semantic control.

Current synthesis delta:
- Repo2Skill-Evo (arXiv:2608.21964, 2026-08-22) directly benchmarks release-conditioned maintenance of repository-grounded skills across 57 repositories / 105 release transitions / 1,158 skills. Every selected transition contains patch-verified stale V1 guidance, yet six frontier agents reach only 29.9%–69.7% avg@3 macro F1.
- Maintenance failure separates into localization miss versus overbroad edit-selection. GPT-5.4 has high stale recall (74.6) but low precision (55.7), showing that broader editing can improve recall while damaging preservation. Oracle file localization still leaves residual error, so within-file evidence tracing/edit choice remains separate.
- A 10-repository 2×2 utility study shows skill-only utility 8.68 versus baseline 5.88 and source-only 8.64, while using 51,821 mean tokens / 3.9 iterations versus source-only 272,620 / 10.8. Skill value is larger in the low-baseline group (+3.98) than high-baseline (+1.61), suggesting maintenance priority should account for expected skill value as well as staleness hazard.
- Silent staleness may remain loadable/retrievable without an immediate runtime failure. Failure-trigger-only maintenance is therefore insufficient; release/API/dependency/contract change evidence should be a first-class trigger candidate.
- Admission validation and longitudinal validity are distinct: Repo2Skill grounds V1 references at admission, yet later release changes invalidate content. This complements SkillProx/VaG rather than replacing pre-commit gating.
- The exact common-replicate admission×maintenance interaction gap remains open. SkillProx defines the architecture but does not provide one matched four-cell replicate table; Repo2Skill-Evo is a maintenance benchmark, not the missing factorial.

Exact continuation:
1. Search Repo2Skill-Evo artifacts/code for per-transition traces enabling stronger localization-vs-edit-selection decomposition and maintenance-cost analysis.
2. Search release-/contract-triggered adaptive maintenance schedulers combining drift hazard, expected skill value, uncertainty, false-edit cost and compute under controlled software/API agent ablations.
3. Continue the common-replicate 2×2 admission-gate × post-admission-maintenance search with all four cells matched on model, stream, seeds and compute.
4. Continue multi-generation hidden semantic-lineage discovery/repair using execution/counterfactual evidence.
5. Continue matched rollback-target selector comparisons and decision-influence audits under fixed controls.
6. Preserve exact tested scope and a nonempty frontier; checkpoints/findings are never global completion.

Future runs should resolve a fresh SHA-only control tuple before semantic work and read this pointer first, followed only by the minimum own predecessor material needed for unresolved frontier continuity.
