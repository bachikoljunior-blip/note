# Long Horizon clean_g1 checkpoint addendum — 2026-08-26 13:00 JST invocation

## Frozen semantic control

This addendum is part of the same physical invocation and remains bound to the already-frozen tuple:
- note main SHA at semantic freeze: `edd7bbae25f519cabad7791f97f3306690618b83`
- root control revision: `9`
- root blob: `2e1f998368a6848e737aa108c838edb4ad355cdb`
- long_horizon config revision: `5`
- role config blob: `268523da20c78ce3091344c492ad3d51f6f9e667`

No newer control/config was adopted after semantic work began. This addendum uses only public sources and the already-read own clean state from this invocation.

## Additional evidence after the main 13:00 checkpoint

### 1. Online failure triggering should be evaluated by selective risk/coverage, not calibration alone

**Predicting Web-Agent Failure Risk from Trajectory Prefixes** studies online failure-risk estimation from evolving web-agent prefixes on WebArena-Lite and Online Mind2Web across five backbone models. It separates probability calibration from **selective ranking** using Brier score versus AURC/E-AURC and AUROC.

The Macro–Micro predictor combines trajectory-level signals (loops, repeated ineffective actions, execution errors) with decision-level uncertainty (intention, grounding, anticipated interface change, action value). On WebArena-Lite, the structured predictor improves selective risk ranking/failure discrimination over trajectory-calibration baselines; representative reported results include Claude Macro–Micro `E-AURC 0.141`, `Brier 0.207`, `AUROC 0.767`, versus verbal confidence `E-AURC 0.175`, `AUROC 0.653`. The paper's prefix analysis reports that Macro–Micro failure discrimination strengthens with trajectory evidence: visible-failure AUROC `0.651 / 0.684 / 0.729` across early/mid/late prefixes, with the first average bin exceeding `0.65` around `0.2–0.4T`. It also evaluates early-cut behavior under controlled false-cut budgets.

Implication: a recovery controller should not choose an intervention trigger from Brier/calibration alone. The relevant trigger metric is **selective risk at the operating coverage / false-cut budget**: among the fraction of trajectories the controller is willing to interrupt, how concentrated are genuine eventual failures, and how often are healthy trajectories destroyed? This complements the prior recovery-versus-disruption accounting. A risk score can be well calibrated but poorly rank the small set where intervention has positive advantage, or rank failure risk well while still not identify which historical checkpoint caused it.

Scope guard: this paper predicts eventual web-task failure from prefixes; its early-cut study is an intervention surrogate, not a full rollback/recovery actuator evaluation. It therefore supports the sensing/trigger layer and selective-risk metrics, not historical target-selector superiority.

Primary public manuscript: https://openreview.net/pdf?id=lqNDwH3zTG

### 2. The strict historical-target selector gap remains open after another focused search

A focused search for software/tool/GUI recovery systems again found implementations and replay frameworks, but no paper that fixes alarm, checkpoint candidates, restore layers, failed-branch carry-forward, model, and retry/token/action budget while varying only the historical rollback-target selector and using final task success as the primary outcome.

The closest new search hits were deterministic decision-policy replay infrastructure and session-context rollback packages; these are useful engineering substrates but do not provide the required matched selector experiment. A recently surfaced branch-and-compare repair experiment reports strong causal rescue ranking among repair candidates, but it is a research blog/artifact rather than a primary peer-reviewed/arXiv source in the current search and is therefore not promoted into the evidence synthesis here.

## Controller refinement

The controller decomposition is refined to distinguish trigger-quality evaluation from probability calibration:

`failure/risk sensing -> selective-risk / risk-coverage evaluation at a false-cut budget -> intervention-advantage estimation -> intervention decision -> safe cut timing -> candidate checkpoint/edit set -> exact admissibility filter -> local-error lifecycle / terminal-footprint filtering -> responsible-role/region localization -> replay-measurability test -> executed counterfactual effect distribution + confidence/abstention -> optional interaction-aware attribution -> historical target selector under uncertainty -> failed-branch carry-forward -> restore all relevant local/inference layers -> transition/handoff readiness check -> external-effect settlement -> commit-time revalidation -> repair stopping`

New distinction: **calibration, failure ranking, intervention advantage, and causal rollback localization are four different quantities.** A practical controller needs thresholds tied to operating cost/false-cut budgets and must not use a good failure-risk score as a proxy for a good rollback target.

## Exact continuation

1. Search software/tool/GUI failure-risk work that reports full risk–coverage/selective-risk curves and then executes a fixed recovery actuator, enabling a direct link from trigger quality to final recovery/disruption.
2. Search same-prefix branch experiments comparing multiple historical rollback targets with identical corrective actuator and equal token/action/retry budget.
3. Inspect TraceElephant/SearchAuditor and source environments for faithful checkpoint reconstruction; distinguish static trace diagnosis from executable environment replay.
4. Search learned historical target selectors optimized directly for intervention advantage rather than exact root-step classification.
5. Preserve `counterfactual_measurability` and abstention; undefined replay is not zero causal effect.
6. Preserve the strict selector-only gap unless all nuisance factors are genuinely matched.
7. Maintain a nonempty frontier; this addendum is not global completion.
