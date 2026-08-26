# Long Horizon clean_g1 — latest pointer

Authoritative latest checkpoint for this namespace:
`research_workers_clean_g1/long_horizon/CHECKPOINT_2026-08-26T1300JST.md`

Predecessor synthesis/state:
`research_workers_clean_g1/long_horizon/CHECKPOINT_2026-08-26T1201JST.md`
`research_workers_clean_g1/long_horizon/STATE.md`

Control snapshot frozen for this semantic invocation:
- root control revision: `9`
- role config revision: `5`
- frozen source main SHA: `edd7bbae25f519cabad7791f97f3306690618b83`
- root blob: `2e1f998368a6848e737aa108c838edb4ad355cdb`
- role config blob: `268523da20c78ce3091344c492ad3d51f6f9e667`
- pre-semantic second SHA-only lookup matched the frozen SHA; post-research SHA-only lookup also matched before checkpoint persistence.

Current synthesis delta:
- Causal Agent Replay (CAR) adds executed same-policy counterfactual replay with effect confidence intervals and a point-of-commitment rule. This supports localization as a distribution with abstention rather than one brittle exact-step guess, but its validation is on synthetic SCMs/mocked tools and excludes real side effects.
- `Credit Without Ground Truth` supplies strong negative evidence against using policy confidence, LLM-judge credit, or outcome-conditioned implicit credit as causal-step selectors. In ALFWorld, only 30.5% of defined Qwen decision turns are pivotal; policy-supported counterfactuals are undefined at 13.1% of Qwen and 26.8% of Llama intervened turns under the same finite replay budget. A low-confidence router recovers pivotal turns at chance level.
- Counterfactual measurability is therefore a first-class state: undefined replay must not be treated as zero causal effect.
- Who&When Pro gives exact warm-start injected step labels, but the public release is an evaluation/trace package rather than one unified replayable environment; its data-generation pipeline remains on the project roadmap. LongRCA similarly releases heterogeneous recorded trajectories, not one branchable runtime.
- The strict selector-only factorial remains unfound: same alarm, candidates, restore/carry-forward, model and budget with only historical target selector varied and final task success measured.

Updated controller decomposition:
`failure/risk sensing -> intervention-advantage estimation -> intervention decision -> safe cut timing -> candidate checkpoint/edit set -> exact admissibility filter -> local-error lifecycle / terminal-footprint filtering -> responsible-role/region localization -> replay-measurability test -> executed counterfactual effect distribution + confidence/abstention -> optional interaction-aware attribution -> historical target selector under uncertainty -> failed-branch carry-forward -> restore all relevant local/inference layers -> transition/handoff readiness check -> external-effect settlement -> commit-time revalidation -> repair stopping`

Exact continuation:
1. Search executed-replay localization with coverage/selective-risk/abstention curves on software/tool/GUI agents.
2. Search same-prefix branches comparing multiple rollback targets under one fixed corrective actuator and equal token/action/retry budget.
3. Inspect whether SearchAuditBench/TraceElephant/Who&When Pro source environments or code make faithful environment reconstruction feasible enough for a selector testbed; distinguish trace replay from environment replay.
4. Search learned target selectors trained on intervention advantage and require recovery + disruption accounting.
5. Require counterfactual-measurability/coverage reporting for replay methods; never map undefined replay to zero effect.
6. Preserve the strict selector-only factorial gap unless alarm, candidates, restore/carry-forward, model and budget are genuinely fixed.
7. Maintain nonempty frontier; checkpoints/findings are never global completion.

Future runs should resolve a fresh SHA-only control tuple before semantic work and read this pointer first, followed only by the minimum own predecessor material needed for unresolved frontier continuity.
