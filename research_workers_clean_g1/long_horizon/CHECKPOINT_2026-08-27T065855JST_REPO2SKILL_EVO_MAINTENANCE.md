# Long Horizon clean_g1 checkpoint — release-conditioned skill maintenance

Checkpointed: 2026-08-27T06:58:55+09:00
Frozen control tuple for semantic work:
- note main SHA: `d1f204a175b4ce7dc45fba783dc03249d87f4c19`
- root control revision: `11`
- root blob: `bf7b8c7f6971c0ec2f3fa7a8d53dca1f88ac50a3`
- role config revision: `5`
- role config blob: `268523da20c78ce3091344c492ad3d51f6f9e667`
- both pre-semantic SHA-only lookups matched; later repository changes were not adopted as semantic control.

## New primary-source evidence

### Repo2Skill-Evo: Repository Skills Go Stale in Silence
Primary source: arXiv:2608.21964, submitted 2026-08-22, https://arxiv.org/abs/2608.21964

This is a directly relevant software-repository skill-maintenance benchmark. It freezes a V1 skill set, advances the underlying repository from V1 to V2, gives the maintenance agent the official release patch, and measures whether obsolete guidance is removed/revised while still-valid guidance is preserved.

Observed scope and results:
- 57 real-world repositories, 105 selected official release transitions, 1,158 skills total.
- Every selected transition contains patch-verified stale V1 skill content; 12,217 obsolete lines total, median 92 obsolete lines per transition.
- Six frontier agents achieve only 29.9%–69.7% avg@3 macro F1 on the patch-grounded maintenance metric.
- Claude-opus-4.6: recall 70.4, precision 75.7, F1 69.7.
- GPT-5.4: recall 74.6, precision 55.7, F1 58.8. This is useful negative evidence: broad editing can raise stale-content recall while substantially harming edit precision.
- The paper identifies two distinct bottlenecks: incomplete localization leaves stale content untouched, while overbroad edit selection removes or rewrites still-valid guidance.
- Oracle skill-file localization on the hardest subset improves maintenance but leaves substantial residual error; therefore file localization alone does not solve within-file evidence tracing and edit selection.

The benchmark also contains a controlled 2×2 utility study over 10 randomly sampled repositories with GPT-5.4: baseline, skill-only, source-only, and source+skill. Group means are:
- baseline utility 5.88
- skill-only 8.68 (+2.80)
- source-only 8.64 (+2.76)
- source+skill 9.01
- skill-only uses 51,821 mean tokens and 3.9 iterations versus source-only 272,620 tokens and 10.8 iterations.
The skill benefit is larger in the low-baseline group (+3.98) than the high-baseline group (+1.61). This is evidence that compact repository skills can be highly valuable precisely where unaided repository knowledge is weak, while the same artifacts are vulnerable to silent temporal decay.

### Admission validation is not future-validity proof
Repo2Skill's V1 grounding gate verifies referenced source paths/symbols but explicitly does not establish semantic correctness or procedural coverage. The fixed V1 set is then expert-selected/refined. Even after this grounding/admission process, all selected release transitions later contain stale content. This strengthens the separation:
`admission validity at t0 != continued validity after environment/repository change`.

## Synthesis delta

1. **Failure-trigger-only maintenance is insufficient.** Release-conditioned staleness can remain loadable/retrievable without producing an immediate runtime error. Maintenance triggers need explicit change evidence such as version/release/API/dependency/contract transitions, not only downstream task failure or observed utility decay.

2. **Maintenance has an intrinsic precision–recall trade-off.** A controller that maximizes stale-content recall can over-edit valid guidance. Therefore maintenance evaluation should keep stale-recall and preservation precision separate, plus downstream behavioral validation; a single scalar success flag is insufficient.

3. **Localization and edit selection are separate control stages.** Even oracle file localization does not eliminate residual errors. A strong design is `change detection -> affected-artifact localization -> evidence tracing within artifact -> minimal edit proposal -> validation -> commit/rollback`, rather than treating maintenance as one monolithic rewrite.

4. **Maintenance priority should account for value as well as hazard.** The utility study suggests skills are most valuable where baseline repository knowledge is weak. A useful scheduling hypothesis is to prioritize roughly by `estimated staleness hazard × current marginal skill value × consequence / maintenance cost`, with uncertainty and abstention. This is an inference/hypothesis from the reported utility and maintenance results, not a directly tested scheduler.

5. **This complements, rather than replaces, admission gating.** SkillProx/VaG-style pre-commit controls address harmful candidate entry; Repo2Skill-Evo shows that a skill can be valid/useful at admission and become silently stale later. Long-horizon governance therefore needs both admission and longitudinal maintenance.

6. **The matched admission×maintenance interaction gap remains.** SkillProx defines the architectural 2×2 but does not provide one common four-cell replicate table from which the interaction can be cleanly estimated. Repo2Skill-Evo is a maintenance benchmark, not that missing factorial.

## Negative evidence / scope guards
- Do not generalize Repo2Skill-Evo's numeric maintenance scores beyond repository-grounded software skills and the patch-conditioned maintenance setup.
- The patch-grounded metric rewards removing/revising obsolete V1 lines and penalizes edits outside the gold obsolete set; semantic quality of new V2 text is evaluated separately by an NL judge. It is not a direct end-to-end software-task success metric.
- The 10-repository utility study is small and uses one backbone; the observed larger gains for low-baseline repositories are suggestive, not a universal law.
- The result does not establish an optimal maintenance scheduler or prove that release-event triggering dominates all alternatives.

## Frontier / exact continuation
1. Search Repo2Skill-Evo artifacts/code for per-transition maintenance traces enabling a stronger decomposition of localization error versus within-file edit-selection error and maintenance cost.
2. Search for release-/contract-triggered **adaptive maintenance scheduling** that jointly models drift hazard, expected skill value, uncertainty, false-edit cost and maintenance compute; prefer software/API agents with controlled ablations.
3. Continue searching for a common-replicate 2×2 `admission gate ON/OFF × post-admission maintenance ON/OFF` factorial with all four cells under matched model, candidate stream, seeds and compute.
4. Continue persistent semantic-lineage discovery/repair across multiple skill generations, especially hidden descendants whose dependency is only visible from executed behavior/counterfactual probes.
5. Preserve the rollback-target selector and decision-influence audit frontier under fixed alarm/candidate/restore/carry-forward/model/budget controls.
6. Maintain nonempty frontier; checkpoint/report completion is never global completion.
