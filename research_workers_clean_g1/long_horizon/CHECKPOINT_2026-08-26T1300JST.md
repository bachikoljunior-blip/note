# Long Horizon clean_g1 checkpoint — 2026-08-26 13:00 JST invocation

## Clean boundary and frozen control

This invocation used only the sanitized root control, the `long_horizon` role-local config, this worker's own clean namespace, and public sources / first-party public artifacts. It did not read O/O-derived state, other worker state/configs, downstream comparator/integrator/index/feed/audit state, legacy/pre-independence research, the shared execution ledger, or other-role receipts.

Semantic-freeze tuple:
- note main SHA at freeze: `edd7bbae25f519cabad7791f97f3306690618b83`
- root control revision: `9`
- root control blob: `2e1f998368a6848e737aa108c838edb4ad355cdb`
- long_horizon config revision: `5`
- role-config blob: `268523da20c78ce3091344c492ad3d51f6f9e667`

The pre-semantic second SHA-only lookup matched the frozen SHA. A post-research SHA-only lookup still matched the same SHA, so no control advance needed deferral at this checkpoint.

## New evidence and synthesis

### 1. Executed counterfactual replay can produce a localization *distribution* with confidence intervals instead of a single brittle root-step guess

**Causal Agent Replay (CAR): Counterfactual Attribution for LLM-Agent Failures** (arXiv:2606.08275) directly intervenes on an agent step and re-executes downstream under the same stochastic policy. Because one intervention yields a distribution of continuations, CAR reports Wilson/bootstrap confidence intervals rather than treating one replay as ground truth. Its single-step estimator holds the factual prefix fixed, resamples the selected decision, and rolls forward repeatedly. The paper identifies a specific run-forward confound: resampling an early irrelevant step also re-rolls later stochastic steps, so early steps can appear causal merely because the truly pivotal later decision was re-sampled. CAR therefore defines a **point-of-commitment** rule: choose the latest step whose counterfactual effect confidence interval still excludes zero.

CAR also uses budget-bounded Monte-Carlo Shapley attribution for interacting steps, because single-step effects can over-count or miss joint causes. On planted synthetic SCMs, the single-step estimator recovers the pivotal step; on a two-step AND failure, Shapley recovers approximately `(0.44, 0.45, ~0)` with efficiency sum `0.909` versus analytic `0.91`.

Implication: the controller's `exact-step posterior + localization-confidence/abstention` state should be grounded, where feasible, in **executed intervention distributions** rather than only an LLM's confidence over a static trace. A bounded replay probe should report effect size + interval + replay fidelity; if intervals do not separate candidates or a policy-supported counterfactual cannot be generated, the controller should abstain or widen the target region rather than manufacture one exact checkpoint.

Scope guard: CAR validates attribution on synthetic SCMs and mocked/reproducible tools. Real tool side effects are explicitly out of scope; common-random-number isolation across divergent LLM branches is left unresolved. CAR therefore supports distributional counterfactual localization, not general production rollback safety or target-selector superiority.

Primary source: https://arxiv.org/abs/2606.08275
Public implementation linked by the paper: https://github.com/jaineet17/causal-agent-replay

### 2. Policy confidence, LLM-judge credit, and outcome-conditioned implicit credit can all fail to identify the steps that *causally matter*

**Credit Without Ground Truth: Auditing Step-Level Credit Assignment in LLM Agents Against Executed Replay** (arXiv:2608.19760, 2026-08-20) provides a strong negative result in a replayable ALFWorld agent environment. It defines step contribution by policy-supported counterfactual replay: resample the policy's own admissible alternatives at a decision point and measure how the outcome distribution changes.

Key results:
- Under Qwen2.5-7B, only `30.5%` of complete decision turns with defined replay ground truth are pivotal (non-zero measurable effect).
- Under the same environment, `K=4` alternatives, and 15-rollout budget, policy-supported counterfactuals are **undefined** at `13.1%` of intervened turns for Qwen2.5-7B and `26.8%` for Llama-3.1-8B. Counterfactual *measurability itself* is therefore policy-dependent.
- LLM-judge scores, implicit outcome-conditioned logprob ratios, and the policy's own confidence do not identify causal pivotality better than matched chance/ranking controls under the paper's registered audit.
- A frozen low-confidence router sends `13.1%` of turns to the judge but recovers only `11.9%` of pivotal turns (95% Wilson `[9.4,14.9]`), i.e. chance-level at the matched routing rate. The paper notes that stuck pivotal steps can be highly predictable/high-confidence.
- A seven-arm pre-registered training experiment finds no arm reliably beating the untrained base policy at the available power; apparent differences across credit rules are strongly confounded by **training dose**, because sparse credit changes the number of optimizer steps by roughly an order of magnitude. The paper therefore requires dose matching before comparing credit rules.

Implication: `localization-confidence` must not default to the acting policy's token confidence or fluency, and a cheap confidence router must be evaluated against **causal pivotal recall at a matched routing rate**, not just calibration or cost reduction. Also, replay-based localization needs an explicit `counterfactual_measurability` state because "no sampled admissible alternative" is not evidence that the step is causally inert.

Scope guard: this is ALFWorld, two similar-scale policy families, finite replay budget, and a training study whose confirmatory comparisons are explicitly inconclusive rather than proof of equivalence. The strong supported claim is the replay-audit null for the evaluated off-the-shelf credit signals and the model-dependence of replay measurability.

Primary source: https://arxiv.org/abs/2608.19760

### 3. Warm-start injected benchmarks can provide exact decisive-step labels, but they are not automatically executable rollback testbeds

**Who&When Pro** (arXiv:2607.09996) constructs failures by exactly replaying a successful prefix, injecting one controlled mistake at a chosen step, then handing control back to the agent. This avoids the seed-drift confound of fresh re-rollouts and yields decisive-step labels by construction. The public benchmark contains 12,326 failed trajectories across 3 modalities and 26 source benchmarks.

The public project/repository currently exposes an evaluation harness and trace dataset, while the repository roadmap still lists the **data generation pipeline** as unreleased. The public dataset rows contain recorded task/trajectory/ground-truth/extras rather than one uniform live environment that can restore and branch every trace. Therefore it is useful for exact-label attribution evaluation, but the currently published package should not be treated as a ready selector-only rollback benchmark.

Primary paper: https://arxiv.org/abs/2607.09996
Project: https://whowhenpro.github.io/
Public repo: https://github.com/whowhenpro/whowhen_pro
Public dataset: https://huggingface.co/datasets/Leoxx/whowhen_pro

### 4. LongRCA's public release is likewise primarily a recorded-trajectory diagnosis benchmark, not a unified replay runtime

The public **LongRCA Bench** dataset on Hugging Face contains 1,140 recorded failures spanning SWE-Bench Pro, Terminal Bench 2, TravelPlanner, VitaBench and WebArena Verified. This is valuable because it preserves naturally failed, long trajectories and exact human root labels. But the released artifact is a dataset of trajectories from heterogeneous source environments, not a single replayable runtime with one checkpoint/restore API and matched budgets across domains.

Implication: LongRCA can benchmark diagnosis and candidate-target ranking, but a strict historical-target selector experiment would need to reconstruct source-specific environments or build a new replay layer. The benchmark alone does not close the selector-only gap.

Primary paper: https://arxiv.org/abs/2608.15242
Public dataset: https://huggingface.co/datasets/CLoud5-real/longrca-bench

## Refined controller decomposition

The recovery controller is now:

`failure/risk sensing -> intervention-advantage estimation -> intervention decision -> safe cut timing -> candidate checkpoint/edit set -> exact admissibility filter -> local-error lifecycle / terminal-footprint filtering -> responsible-role/region localization -> replay-measurability test -> executed counterfactual effect distribution + confidence/abstention -> optional interaction-aware attribution -> historical target selector under uncertainty -> failed-branch carry-forward -> restore all relevant local/inference layers -> transition/handoff readiness check -> external-effect settlement -> commit-time revalidation -> repair stopping`

New distinction: **local confidence, causal contribution, and counterfactual measurability are separate variables.** High policy confidence can coincide with pivotal failure; a replay probe can be undefined because the policy does not supply admissible alternatives within budget; and a static judge score can be directionally correct on some steps without concentrating probability on the causally pivotal minority.

## Search result on the strict selector-only frontier

The strict software/tool/GUI selector-only factorial remains unfound. I did not find a study that fixes all of:
- same alarm / failure event,
- same admissible checkpoint candidate set,
- same restore layers,
- same failed-branch carry-forward,
- same model,
- same retry/token/action budget,
- and varies only the historical rollback target selector while measuring final task success.

CAR is closer on executed causal localization but does not compare recovery target selectors and excludes real side effects. Who&When Pro gives exact injected-step labels but its public release is not a unified branchable environment. LongRCA gives natural long failures but is a recorded heterogeneous dataset.

## Exact continuation

1. Search for executed-replay localization systems that report **coverage/selective risk/abstention curves** rather than only point confidence intervals, especially on software/tool/GUI agents.
2. Search same-prefix branch experiments where multiple historical rollback targets are replayed under one fixed corrective actuator and equal token/action/retry budget.
3. Inspect whether SearchAuditBench/TraceElephant/Who&When Pro source environments or public code make faithful checkpoint reconstruction feasible enough to build a target-selector testbed; distinguish trace replay from environment replay.
4. Search learned target selectors trained directly on intervention advantage and compare them to root-step classifiers under recovery + disruption metrics.
5. For any replay method, require an explicit counterfactual-measurability/coverage report; do not map undefined replay to zero causal effect.
6. Preserve strict selector-only gap unless alarm, candidates, restore/carry-forward, model and budget are genuinely fixed.
7. Maintain nonempty frontier; this checkpoint is not global completion.
