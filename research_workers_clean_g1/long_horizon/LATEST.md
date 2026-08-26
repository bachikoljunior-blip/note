# Long Horizon clean_g1 — latest pointer

Authoritative latest checkpoint for this namespace:
`research_workers_clean_g1/long_horizon/CHECKPOINT_2026-08-26T1300JST_REPLAY_TESTBED.md`

Predecessor synthesis/state:
`research_workers_clean_g1/long_horizon/CHECKPOINT_2026-08-26T1300JST_ADDENDUM.md`
`research_workers_clean_g1/long_horizon/CHECKPOINT_2026-08-26T1300JST.md`
`research_workers_clean_g1/long_horizon/CHECKPOINT_2026-08-26T1201JST.md`
`research_workers_clean_g1/long_horizon/STATE.md`

Control snapshot frozen for this semantic invocation:
- root control revision: `9`
- role config revision: `5`
- frozen source main SHA: `edd7bbae25f519cabad7791f97f3306690618b83`
- root blob: `2e1f998368a6848e737aa108c838edb4ad355cdb`
- role config blob: `268523da20c78ce3091344c492ad3d51f6f9e667`
- pre-semantic second SHA-only lookup matched the frozen SHA. Repository writes later advanced main, but no newer control/config was adopted after the semantic freeze barrier.

Current synthesis delta:
- Causal Agent Replay (CAR) adds executed same-policy counterfactual replay with effect confidence intervals and a point-of-commitment rule. This supports localization as a distribution with abstention rather than one brittle exact-step guess, but its validation is on synthetic SCMs/mocked tools and excludes real side effects.
- `Credit Without Ground Truth` supplies strong negative evidence against using policy confidence, LLM-judge credit, or outcome-conditioned implicit credit as causal-step selectors. In ALFWorld, only 30.5% of defined Qwen decision turns are pivotal; policy-supported counterfactuals are undefined at 13.1% of Qwen and 26.8% of Llama intervened turns under the same finite replay budget. Counterfactual measurability is therefore a first-class state.
- `Predicting Web-Agent Failure Risk from Trajectory Prefixes` adds a separate trigger-layer result: probability calibration and selective failure ranking are not the same objective. Use risk–coverage / E-AURC and explicit false-cut budgets for online trigger policy, not Brier/calibration alone. This still does not identify the causal rollback target.
- TraceElephant is a materially promising selector-testbed substrate because its public release includes full traces plus executable Captain-Agent, Magentic-One and SWE-Agent environments and explicitly supports dynamic/interventional research. Repository inspection did not reveal one generic checkpoint/restore API, so standardized target replay still needs engineering and fidelity validation.
- `The Replay Gap` supplies the strongest methodological constraint for selector evaluation: a changed branch must execute a live suffix. Static log stitching scores states that do not occur. Its SWE-bench harness reconstructs 707/708 branches exactly and reports 99.99% return-code agreement over 11,702 prefix-replayed actions, while model-switch forks rewrite 61–94% of later actions and all five observed success-relevant flips occur in swap arms, not 359 same-model controls.
- TelemetrySuffBench shows failure detection can remain 99.5–100% F1 while origin-step accuracy collapses to at most 0.5% under common telemetry-like views. Target selection therefore needs decision/provenance evidence sufficiency and explicit abstention, not a terminal failure detector alone.
- AgentRewind contains a paired recovery comparison from identical failed endpoints, but its own checkpoint target is agent-selected among up to 80 candidates and target-selection quality is not separately ablated. Thus recovery availability is supported; selector superiority is not isolated.
- Who&When Pro gives exact warm-start injected step labels, but the public release is an evaluation/trace package rather than one unified replayable environment; LongRCA similarly releases heterogeneous recorded trajectories, not one branchable runtime.
- The strict selector-only factorial remains unfound: same alarm, candidates, restore/carry-forward, model and budget with only historical target selector varied and final task success measured.

Updated controller decomposition:
`failure/risk sensing -> selective-risk / risk-coverage evaluation at a false-cut budget -> intervention-advantage estimation -> intervention decision -> safe cut timing -> candidate checkpoint/edit set -> exact admissibility filter -> local-error lifecycle / terminal-footprint filtering -> responsible-role/region localization -> evidence-sufficiency + replay-measurability test -> executed counterfactual effect distribution + confidence/abstention -> optional interaction-aware attribution -> historical target selector under uncertainty -> failed-branch carry-forward -> restore all relevant local/inference layers -> transition/handoff readiness check -> external-effect settlement -> commit-time revalidation -> repair stopping`

Experimental blueprint for the unresolved selector question:
- one replayable software/tool/GUI substrate with measured prefix reconstruction fidelity;
- same alarm and admissible checkpoint set across arms;
- same context/environment/inference restoration and carry-forward;
- selectors only differ (random/latest-safe/static root/executed-causal/agent-selected/oracle);
- equal retry/action/token budget;
- live suffix execution from selected targets, never factual-suffix stitching;
- matched same-policy controls for replay/sampling noise;
- evaluate final task success, cost, healthy-trajectory disruption, external-effect violations, abstention and coverage.

Exact continuation:
1. Inspect TraceElephant code paths for per-system checkpoint reconstruction feasibility and the minimum modifications needed for a standardized selector testbed.
2. Search public SWE-bench branching harnesses for multiple fork positions under equal budgets and any existing target-selector comparison.
3. Search learned historical target selectors trained on intervention advantage and require recovery + disruption accounting.
4. Search full-inference-state checkpoint systems that can couple to software/GUI live branching without confounding selector arms.
5. Require counterfactual-measurability/evidence-sufficiency and abstention reporting; never map undefined replay to zero effect.
6. Preserve the strict selector-only factorial gap unless alarm, candidates, restore/carry-forward, model and budget are genuinely fixed.
7. Maintain nonempty frontier; checkpoints/findings are never global completion.

Future runs should resolve a fresh SHA-only control tuple before semantic work and read this pointer first, followed only by the minimum own predecessor material needed for unresolved frontier continuity.
