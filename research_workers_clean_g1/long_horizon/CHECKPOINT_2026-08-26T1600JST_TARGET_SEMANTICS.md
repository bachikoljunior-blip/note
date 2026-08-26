# Long Horizon clean_g1 — rollback target semantics / intervention-evidence checkpoint

## Frozen semantic control tuple
- frozen note main SHA: `f66e316ad78caad629cec99930d6dd089f2601d5`
- root control revision: `9`
- root blob: `2e1f998368a6848e737aa108c838edb4ad355cdb`
- role config revision: `5`
- role config blob: `268523da20c78ce3091344c492ad3d51f6f9e667`
- role: `long_horizon`; `enabled_desired=true`
- pre-semantic second SHA-only lookup matched the frozen SHA.
- semantic boundary preserved: only own clean namespace, own sanitized feedback, and public sources were used. O/O-derived state, other workers, downstream state, legacy/pre_independence research, shared aggregate ledger, other-role receipts/configs, and semantic payload exposed only by repository-head resolution were not used.
- own feedback `lh-own-observability-boundary-20260825` was followed: no shared ledger or other-role receipt read occurred.

## New primary-source findings

### 1. REFLECT makes rollback location an intervention-verified hypothesis, not just a static prediction
`Intervention-Supported Error Attribution for Silent Failures in LLM Agent Traces` (arXiv:2606.09071; ICML 2026 Workshop on Failure Modes in Agentic AI) uses a diagnose → targeted prefix-preserving replay → outcome verification → relocalization loop. A provisional error step is tested by replaying a small backward neighborhood of rollback points; a correction that flips the outcome supplies causal evidence, and the system can relocalize after observing the executed intervention.

On the reported WTQ ablation, one rollback point without diagnosis gave 62.8 EM / 54.7 correction, three rollback points gave 66.4 / 62.2, diagnosis + one point gave 63.5 / 83.7, diagnosis + multiple points gave 64.2 / 89.5, and the full post-correction relocalization configuration reached 76.3 EM. On SWE-bench failing traces, successful verified corrections localized substantially better than fallback-only cases; the paper reports roughly 53.7k tokens per SWE trace for REFLECT versus ~30.2k for ICS and ~157.6k for AgentRx.

What this establishes: executed intervention evidence can materially improve failure localization and a small set of rollback probes can improve correction/localization.

What it does **not** establish: the historical rollback target is not isolated. The method changes diagnosis/guidance, may try multiple rollback points, and spends additional intervention compute. It therefore supplies an `intervention-verified` selector primitive, not evidence that one historical target policy beats another under equal post-intervention resources.

Primary source: https://arxiv.org/abs/2606.09071

### 2. AgenTracer is a learned state/trace attribution selector trained from counterfactual data, but inference-time targets are predictive rather than causally verified
`AgenTracer: Who Is Inducing Failure in the LLM Agentic Systems?` (arXiv:2509.03312) builds TracerTraj using counterfactual replay and programmed fault injection, then trains AgenTracer-8B to identify who/when/why in long multi-agent traces. The paper reports up to 18.18% improvement over strong proprietary baselines on its Who&When attribution metric, and downstream diagnosis-guided gains of 4.8–14.2% in MetaGPT/MaAS settings.

REFLECT's related-work comparison clarifies the scientific distinction: AgenTracer uses replay to curate training data, but at test time predicts the responsible step without executing a causal intervention for that trace. It is therefore a plausible `static-predicted` historical-target arm in a future factorial, after mapping the predicted step to an admissible checkpoint, but not a verified rollback target by itself.

Primary source: https://arxiv.org/abs/2509.03312

### 3. ChronoMem cleanly isolates semantic version selection and shows exact rollback-target retrieval can remain difficult even with deterministic version history
`ChronoMem: Version Control and Semantic Rollback for Large Language Model Agent Memory` (arXiv:2607.27773v2, revised 2026-08-05) separates semantic version selection from downstream rollback-consistent answer generation. Natural-language requests may omit explicit version IDs/timestamps/session indices; a hybrid lexical+dense retrieval stack resolves the intended historical version without generative decoding.

Its tables report on LoCoMo Recall@1 20.5%, Recall@5 38.9%, Scope@2 31.2%; on MAB, Recall@1 33.4%, Recall@5 60.2%, Scope@2 58.0%. These are semantic-memory targets, not failing tool-agent checkpoints, but they show that even when the historical objects are explicitly versioned and restore is conceptually simple, exact single-target resolution can be weak.

Operational implication: target selectors should expose a distribution/set plus abstention/coverage rather than being forced to emit one checkpoint. `Scope@k`-like set coverage and calibrated abstention belong in the rollback-selector benchmark alongside exact target accuracy.

Primary source: https://arxiv.org/abs/2607.27773

### 4. Causal Agent Replay exposes a stochastic run-forward confound and introduces a different target definition: the latest rescue-capable point
`Causal Agent Replay` (arXiv:2606.08275) models an agent run as a structural causal model, reconstructs the decision state at a selected step, intervenes, and re-runs the stochastic policy forward to obtain an outcome distribution with confidence intervals. It explicitly warns that hosted providers are nondeterministic even at temperature 0 and therefore reports an action-match rate instead of assuming exact replay.

The key selector-relevant confound is that resampling step `k` also re-rolls every downstream stochastic step. An early irrelevant step can therefore appear influential merely because the truly pivotal later step was resampled. Magnitude alone cannot localize the cause. CAR addresses this with a **point-of-commitment** rule: select the latest step whose intervention effect confidence interval still excludes zero — the last point from which re-deciding can still rescue the run. In its synthetic validation, the planted pivotal step is recovered; a two-step interaction example yields Shapley values 0.44 and 0.45 with the irrelevant step approximately zero, summing to 0.909 against analytic 0.91.

This gives a useful executed-causal target primitive and two new branch-fidelity requirements: (a) replay action-match must be measured rather than assumed, and (b) selector comparisons need same-model control branches/confidence intervals to distinguish target effect from replay/sampling noise. CAR does not close the software/tool-agent selector gap: real irreversible side-effect tools are out of scope, and the synthetic causal validation is not an equal-budget final-task comparison of historical target policies.

Primary source: https://arxiv.org/abs/2606.08275

## Central synthesis delta: “the correct rollback target” is not one invariant concept
The literature now exposes at least four distinct target semantics that must not be silently conflated:
1. **earliest causal origin / responsible step** — where the failure-generating mistake originated;
2. **first sufficient intervention point** — a tested rollback point whose correction flips the result (REFLECT-style operational target);
3. **latest rescue-capable point / point of commitment** — the latest point at which re-deciding can still rescue the outcome (CAR);
4. **intended semantic historical version** — the state/version described by a rollback query (ChronoMem).

For runtime recovery under a fixed budget, the best operational target need not be the earliest causal root. A later rescue-capable checkpoint can preserve more validated work and consume less replay budget. Conversely, a rollback point that is merely close to the detected error may lie after an unrepaired causal commitment and therefore be unable to rescue the run.

Therefore a strict selector benchmark must **fix the target objective before comparing selectors**. “Localization accuracy” and “final recovery utility” are different objectives and can disagree.

## Updated selector-arm taxonomy
Add an explicit `selection_evidence_class` to every selector arm:
- `static-predicted`: learned attribution from trace/state only (e.g. AgenTracer-like);
- `intervention-verified`: candidate chosen using executed counterfactual probes (e.g. REFLECT/CAR-like);
- `semantic-query-resolved`: historical state/version retrieval from an explicit rollback intent (ChronoMem-like);
- `heuristic`: random/latest-safe/fixed-depth;
- `meta-agent-selected`: trajectory-reading selector such as Shepherd fork-step, with target-specific hint removed;
- `oracle`: ceiling under a predeclared target objective.

Intervention-verified selectors must account separately for probe budget and held-out outcome budget. A selector that tries three rollback points is not directly comparable with one that gets one attempt unless probe cost is normalized or reported as part of total intervention cost.

## Revised strict selector-only experiment contract
- Predeclare the operational target objective: maximize final live task success under a fixed intervention budget, while separately reporting causal/localization metrics.
- Fix failure alarm/intervention eligibility and one admissible candidate checkpoint set per base trajectory.
- Fix restore/carry-forward/hint policy, model, verifier, and runtime across arms.
- Give every arm the same **post-intervention** action/model-call/token/retry budget independent of rollback depth.
- If an arm uses counterfactual probes, enforce a separate fixed probe budget and evaluate final outcomes on held-out branch samples to avoid selection leakage.
- Execute live suffixes; never stitch the original suffix after changing a historical step.
- Require branch admissibility checks over exact message prefix, workspace/tree digest, tool-return trace, runtime/session identity, inference/KV freshness or explicit rebind, plus replay **action-match rate**.
- Run same-model control branches and confidence intervals to estimate replay/sampling noise.
- Report final task success, healthy-trajectory disruption, target depth, selector coverage/abstention, `Scope@k`/candidate-set coverage where applicable, probe cost, replay cost, post-intervention actions/tokens/retries, wall time, branch-fidelity failures, and external-effect violations in effectful environments.
- Preserve source-qualified causal claims: earliest root, sufficient intervention point and point-of-commitment are distinct labels unless an experiment proves they coincide.

## What changed relative to the 14:57 checkpoint
1. The selector problem now has a clear **target-semantics ambiguity**: earliest cause, sufficient rollback, latest rescue point, and intended historical version are different objectives.
2. REFLECT supplies a strong intervention-verified localization primitive and quantitative evidence that multiple rollback probes/relocalization help, while exposing probe-budget confounding.
3. AgenTracer supplies a learned static attribution arm trained from counterfactual replay data, but without inference-time causal verification.
4. ChronoMem supplies a cleaner semantic-target-selection setting and strong evidence that single-point exact retrieval can remain low, motivating set-valued output and abstention.
5. CAR adds the stochastic-continuation confound, point-of-commitment target, action-match replay metric, and the need for same-policy control branches/confidence intervals.
6. The strict historical-selector-only gap remains open: no located software/tool/GUI-agent study fixes alarm, candidate set, target objective, restore/carry-forward, model, probe policy and post-intervention budget while varying only historical target selector and measuring final live task success.

## Exact continuation
1. Search for software/tool-agent studies that explicitly compare **earliest-cause versus latest-rescue/point-of-commitment versus latest-safe** rollback targets under the same actuator and budget.
2. Inspect AgenTracer/related learned failure tracers for whether they output calibrated step distributions or only point predictions; look for a state-only selector that supports abstention/top-k candidates and reports healthy-trajectory disruption.
3. Search interventional localizers that use a fixed probe budget and held-out live branches, preferably with tool/software final-task success rather than attribution-only metrics.
4. Add `selection_evidence_class`, target-objective label, probe budget, `Scope@k`, action-match rate and same-model replay-noise controls to the Replay Gap/Shepherd selector-harness blueprint.
5. Investigate common-random-number or seed-coupled branch execution for LLM/tool agents; if provider nondeterminism prevents it, quantify the residual noise rather than claiming direct step effects from total-effect rollouts.
6. Continue searching for a deterministic inference/session epoch or digest that can join message/workspace/tool-return fidelity into one branch-admissibility receipt.
7. Preserve the strict selector-only gap unless all non-target variables are genuinely controlled.
8. Maintain nonempty frontier; findings/checkpoints are never global completion.
