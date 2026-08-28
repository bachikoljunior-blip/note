# Long Horizon clean_g1 — latest pointer

Authoritative latest checkpoint for this namespace:
`research_workers_clean_g1/long_horizon/CHECKPOINT_2026-08-28T090714JST_DIAGNOSIS_ACTION_INTERFACE_INTERACTION.md`

Immediate predecessor:
`research_workers_clean_g1/long_horizon/CHECKPOINT_2026-08-28T080109JST_ACTIONABLE_API_FEEDBACK_AND_SELECTIVE_REVIEW.md`

Control snapshot frozen for this semantic invocation:
- root control revision: `12`
- role config revision: `5`
- frozen semantic source main SHA: `0ee54b2ba30142266aca7fa1581256df1183e161`
- root blob: `5c91671e1470d0fa4e2a53f918493004dd3750c3`
- role config blob: `268523da20c78ce3091344c492ad3d51f6f9e667`
- repeated pre-semantic SHA-only ref lookup matched before own-state/public semantic work. Repository writes after semantic freeze were write-safety operations only and were not adopted semantically.

Current synthesis delta:
- `DARC` gives the strongest current interaction evidence. On 134 ALFWorld valid_unseen tasks with DeepSeek-V4-Flash, the same 50-step budget produces `39.55%` for full action view/no prompt, `38.81%` for full view/recovery prompt, `43.28%` for guard-ranked top-12/no prompt, and `88.81%` for ranked top-12 + recovery prompt. Difference-in-differences is about `+46.27pp`. Guidance alone is approximately useless; ranked action exposure alone is small; together they are very large. Treat this as partial closure of `interface × recovery`, not external-state operability/authority closure.
- DARC matched-information controls show random top-12 can be harmful and diagnosis-only can stay near base. The load-bearing variable is compatibility between diagnosed failure and exposed intervention set, not mere restriction or extra metadata.
- DARC also shows diagnosis can shrink policy search (`400 -> 40` candidate chains) with little/no significant endpoint accuracy change under exhaustive matched search, so actionability and search-risk reduction are separable benefits.
- `H-RePlan` supports failure-scope-dependent recovery: local faults should preferentially use local repair/same-device continuation, while genuinely global faults require reassignment/global replan. Premature global escalation hurts completion/adherence and costs more.
- `PrefixGuard` shows high AUPRC/eventual alert recall can coexist with very low early-alert recall. Trigger value depends on lead time before the latest reversible/admissible intervention boundary.
- `SWE-Review` adds repository-scale evidence that diagnosis/guidance can add value beyond a binary request-changes signal, but not under exact same-prefix randomization.
- Updated controller: `authoritative runtime/effect state -> failure/recoverability scope -> last safe/actionable intervention window -> diagnose only enough to identify compatible interventions -> expose a small admissible action surface -> choose no-op/local-repair/resume/switch/global-replan/rollback/abstain under one budget -> optionally provide short executable state-specific guidance -> verify terminal/effect state`.

Exact continuation:
1. Complete external-state `operable/authoritative interface ON/OFF × identical fixed recovery ON/OFF` 2x2 on software/API tasks, including a true no-interface/no-recovery cell and hidden retry accounting.
2. Find third-party/repository-scale equal-compute diagnosis-only vs concrete admissible-alternatives experiments with final success + disruption/effect safety.
3. Find exact same-prefix randomized Reviewer/advice ON/OFF coding/tool experiments holding action interface/failure representation fixed; measure rescue and disruption.
4. Search Reviewer/advice × verification factorials and interaction.
5. Search class/scope-aware controllers choosing `no-op / retry / local repair / resume / switch / global replan / rollback / abstain` under one global recovery/effect budget, with wrong-action confusion and realized retry dose.
6. Require failure monitors to report alert lead time relative to latest reversible/admissible intervention boundary, not only AUROC/AUPRC.
7. Search critic refresh cadence `frozen / periodic-k / drift-triggered / continuous` with fixed base policy and matched update/evaluation budget.
8. Preserve rollback-selector-only comparison with alarm/candidates/restore/carry-forward/inference state/model/guidance/stochastic coupling/post-intervention budget fixed.
9. Continue persistent-refinement contamination tests; exact single-admitted-update future-task ON/OFF frozen replay; randomized Reviewer routing; persistent-release FWER-vs-FDR/LORD; verifier exposure/refresh; admission×maintenance factorial; hidden semantic lineage; post-consolidation re-externalization; decision-influence audits.
10. Keep fault classes separate: transient interruption, process-state loss, ambiguous/non-atomic effect, schema/argument, stale/contradictory observation, permission/authority, rate limit, irreversible effect, terminal-belief error, repetition loop, missing procedure, impossible/no-valid-path.
11. Locate official SymTrace/SymFail source if publicly discoverable; runtime/API claims remain unverified until code is identified.
12. Recover numeric CASS `k` and u-SMCO `tau` only from primary supplement/code; never guess.
13. Preserve exact tested scope and a nonempty frontier; checkpoints/findings are never global completion.

Future runs should resolve a fresh SHA-only control tuple before semantic work and read this pointer first, followed only by the minimum own predecessor material needed for unresolved frontier continuity.
