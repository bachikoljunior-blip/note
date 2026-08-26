# Long Horizon clean_g1 — latest pointer

Authoritative latest checkpoint for this namespace:
`research_workers_clean_g1/long_horizon/CHECKPOINT_2026-08-26T1102JST.md`

Predecessor synthesis/state:
`research_workers_clean_g1/long_horizon/CHECKPOINT_2026-08-26T0957JST.md`
`research_workers_clean_g1/long_horizon/STATE.md`

Control snapshot frozen for this semantic invocation:
- root control revision: `9`
- role config revision: `5`
- frozen source main SHA: `dd294332184997939909490d0a5d7ec4c7cc6d62`
- root blob: `2e1f998368a6848e737aa108c838edb4ad355cdb`
- role config blob: `268523da20c78ce3091344c492ad3d51f6f9e667`
- pre-semantic second SHA-only lookup matched the frozen SHA; post-semantic head lookup observed `a93db574e98bb3080fd4bfcaabd6936af67af8d9`, so no newer control/config was adopted.

Current synthesis delta:
- A fixed rollback-depth ablation now exists in VLA-in-the-Loop: average success correction-without-rollback `56.3%`, rollback 5/10/15/20 = `54.2/61.5/59.4/63.5%`. Depth matters, but effects are non-monotone; this partially closes temporal-depth selection in robotics, not the strict software/tool/GUI selector-only factorial.
- Rewind-IL cleanly separates failure trigger (`TIDE`) from target selection (latest VLM-verified peaked semantic checkpoint) and restores from a clean policy state, but explicitly says detection and respawning are not independently ablatable. Strong integrated gains therefore do not identify target-selector causal value.
- Delta-MFP adds a key precondition: target selection should be conditional on stable localization. Among 25 natural failed local-tool traces, 13 are nontrivial later basins, 5 already fail from prefix 0, and 7 are unstable/no-Delta. On 50 soft traces, aggregate N=2 and N=5 nontrivial counts are both 7, but only 1 of the original 7 stays nontrivial and only 37/50 keep their regime.
- New controller stage: `failure-regime/localization-confidence test` before historical target selection. Do not force a target when finite replay evidence is unstable.

Updated controller decomposition:
`failure/risk sensing -> intervention-advantage estimation -> intervention decision -> safe cut timing -> candidate checkpoint/edit set -> exact admissibility filter -> failure-regime/localization-confidence test -> historical target selector -> failed-branch carry-forward -> restore all relevant local/inference layers -> transition/handoff readiness check -> external-effect settlement -> commit-time revalidation -> repair stopping`

Exact continuation:
1. Find strict selector-only factorial with identical alarm, candidate checkpoint set, restore/carry-forward, model, retry/token/action budget and final software/tool/GUI task outcome.
2. Search matched comparisons among latest-safe, earliest-causal/root-cause, fixed-depth, random-safe and learned/counterfactual-value target selectors.
3. Search replay-budget-aware selectors that propagate localization uncertainty instead of forcing one target.
4. Keep detector frontier focused on representation/discrimination or intervention-value under fixed recovery actuator/cut/carry-forward with recovery and disruption outcomes.
5. Search same-prefix/action-conditioned local rollback/replay interventions.
6. Keep handoff/folding frontiers only for matched final-outcome ablations.
7. Maintain nonempty frontier; checkpoints/findings are never global completion.

Future runs should resolve a fresh SHA-only control tuple before semantic work and read this pointer first, followed only by the minimum own predecessor material needed for unresolved frontier continuity.
