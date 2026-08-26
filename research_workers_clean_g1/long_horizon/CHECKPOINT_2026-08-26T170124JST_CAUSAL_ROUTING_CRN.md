# Long Horizon clean_g1 — causal routing / CRN checkpoint

## Frozen semantic control tuple
- invocation started at: `2026-08-26T16:59:13+09:00`
- frozen note main SHA: `456111f88cd26b8ad796866aaf64a6c44a176908`
- root control revision: `10`
- root blob: `025d0efc635aca01e0e25d293f40004d90dc663b`
- role config revision: `5`
- role config blob: `268523da20c78ce3091344c492ad3d51f6f9e667`
- role: `long_horizon`; `enabled_desired=true`
- pre-semantic second SHA-only lookup matched the frozen SHA.
- semantic boundary preserved: only this role's clean state plus public sources were used. No O/O-derived state, other worker state, downstream/index/feed/audit state, legacy/pre_independence research, shared aggregate ledger, other-role receipts/configs, or commit-message/diff payload was used semantically.

## New primary-source findings

### 1. A very recent executed-replay audit is strong negative evidence against confidence/judge/fluency as rollback-target proxies
`Credit Without Ground Truth: Auditing Step-Level Credit Assignment in LLM Agents Against Executed Replay` (arXiv:2608.19760v2; revised 2026-08-25) constructs policy-conditional causal ground truth in ALFWorld by replaying each factual action and `K=4` distinct policy-supported alternatives, with each arm rolled to terminal at least three times. It reports:
- 30.5% of defined Qwen decision points have a nonzero replay contrast at the achieved sampling resolution;
- policy-supported counterfactuals are undefined at 13.1% of Qwen turns versus 26.8% of Llama turns under the same environment / K=4 / 15-rollout budget, while the fraction pivotal among defined turns reverses (30.5% vs 38.3%);
- implicit credit, an LLM-judge signal, and policy confidence do not show reliable incremental fidelity beyond matched controls for identifying causal contribution; the confidence-only router recovers 11.9% of pivotal turns while routing 13.1% of turns, i.e. chance-level pivotal recall;
- step `correctness` and step `contribution` are explicitly different objects: a nominally wrong action may be causally inert or later repaired, while a plausible/high-confidence action may be pivotal.

The v2 revision additionally corrects fidelity for replay-target reliability: implicit fidelity remains bounded near zero and judge fidelity becomes inconclusive at achieved target reliability, rather than being promoted by its positive raw point estimate.

Operational implication for rollback target selection: **do not use model confidence, fluency, or judge correctness score as a default target selector without executed causal calibration.** A target selector needs its own replay-ground-truth audit, coverage/undefined accounting, and an abstention path when policy-supported counterfactuals are not measurable.

Primary source: https://arxiv.org/abs/2608.19760v2

### 2. The same paper exposes a second confound: matched nominal budget is not matched effective training/intervention dose
Its seven-arm pre-registered training experiment used common random numbers and identical nominal budgets, yet credit sparsity changed how many examples survived and produced an order-of-magnitude range in optimizer steps (112 to 8 per round). The paper therefore requires reporting surviving examples, optimizer steps, tokens updated and realized parameter displacement; otherwise a comparison can measure `dose`, not credit content.

For rollback-selector experiments, the analogous rule is stronger than the previous `same post-intervention token/action budget` rule: report both **allocated** and **realized** post-rollback opportunity. A selector that often lands in states where tools reject actions, the policy has no admissible alternative, or recovery terminates early can receive the same nominal limit but much less effective decision/replay dose.

This suggests adding `realized_model_calls`, `realized_admissible_actions`, `realized_environment_steps`, `successful_tool_calls`, and `unused_budget_reason` to selector-arm receipts.

### 3. AgentLocate gives a useful target definition, but its exact-step results and refinement ablations argue against forced single-point confidence
`Who Broke the System? Failure Localization in LLM-Based Multi-Agent Systems` (arXiv:2607.07989) defines its decisive failure step as the **earliest step at which a single corrected action would reverse the failure outcome**. This is closer to a `first sufficient intervention point` than to the earliest causal origin, and should be labeled separately in the target taxonomy.

AgentLocate improves localization over baselines, but exact step localization remains difficult. On the Algorithm-Generated subset, full AgentLocate reaches 38.10% exact step accuracy (all-at-once) / 33.33% (step-by-step) in the reported Qwen configuration; on the Hand-Crafted subset, exact-step accuracy is substantially lower in several model/mode cells. Its error analysis explicitly notes visibility bias: late verification/retrieval agents can be blamed because upstream errors first become visible there.

More refinement is not monotonically better. In the reported refinement-round ablation, Qwen step accuracy goes 37.50% -> 33.33% -> 33.33% from one to three rounds in one setting, while Mistral goes 16.67% -> 25.00% -> 20.83%. The method aggregates self-reported evaluator confidence, but the paper does not establish calibration of that confidence as a probability that a target is causally correct.

Operational implication: use AgentLocate-like output as a **candidate distribution / top-k proposal**, not as proof that one checkpoint is safe to restore. Separate `visibility point`, `first sufficient intervention point`, and `earliest cause`, and require executed validation or abstention for high-stakes rollback.

Primary source: https://arxiv.org/html/2607.07989v1

### 4. BranchPoint-Latent is a promising replay-budget allocator, not a rollback target oracle
`Knowledge-Based Zero-Replay Debugging of Multi-Agent LLM Traces` (arXiv:2606.14805) predicts which trace events a deterministic replay oracle would mark high-effect before paying replay cost. Across 37 trace families, its learning-to-rank model raises held-out per-trace Branch Recall@5 from 0.73 to 0.93 at zero oracle-replay cost.

This is valuable for the current frontier because it supplies a **candidate/probe allocator** under a scarce replay budget. It does not establish that the top-ranked event is the best historical restore point, and it evaluates localization against a replay oracle rather than final live task success after rollback.

Operational implication: split the controller into `candidate generator / probe allocator` and `historical restore selector`. A BranchPoint-like ranker can cheaply narrow a candidate set; a held-out live branch then evaluates recovery utility without using the same probe samples for final outcome estimation.

Primary source: https://arxiv.org/abs/2606.14805

### 5. Common-random-number coupling is useful, but `same seed` is not a causally valid general solution after branches change control flow
Two primary sources sharpen the replay-noise problem.

`Aborted but Not Forgotten` (arXiv:2608.15939) runs a stochastic paired audit with **common random numbers**: stale/fresh arms use identical RNG seeds and identical finalize tokens. On Phi-3.5-mini, stale cache causes the protected effect in 180/180 samples at temperature 0.3 and 178/180 at temperature 0.7, versus 0/180 fresh in both. This shows CRN pairing is practically useful when the two arms retain a token/control structure that permits aligned randomness.

But `Realizing Common Random Numbers: Event-Keyed Hashing for Causally Valid Stochastic Models` (arXiv:2603.11084) formalizes why simply reusing one base seed fails when an intervention changes execution path. Stateful PRNGs assign randomness by draw index; a branch that consumes a different number of draws shifts all downstream noise. The proposed remedy is counter-based RNG plus stable **event identifiers**, making each draw a function of `(seed, event_id)` rather than execution order.

`Causal Agent Replay` independently states the same limitation for LLM-agent replay: direct-effect isolation would need common random numbers across divergent LLM contexts, which is hard once branches change the stochastic continuation.

Operational implication for the strict selector factorial:
- separate **environment/tool randomness coupling** from **model-sampling coupling**;
- for controllable environments, key randomness by stable semantic event identity rather than a single mutable PRNG stream;
- record an `event_identity_map` and report where identity ceases to be well-defined after branch divergence;
- do not claim paired causal isolation merely because two arms share a numeric seed;
- for hosted/model sampling where stable event-keyed coupling is unavailable, use same-model control branches and confidence intervals, and treat residual continuation noise as part of the estimand.

Primary sources:
- https://arxiv.org/abs/2608.15939
- https://arxiv.org/abs/2603.11084
- https://arxiv.org/abs/2606.08275

## Synthesis delta
The historical-target benchmark now needs **three independently controlled resources** rather than one:
1. `candidate-generation/probe budget` — how much evidence a selector may spend before choosing;
2. `allocated recovery budget` — the nominal post-rollback calls/actions/tokens/retries available to every arm;
3. `realized recovery dose` — how much usable decision opportunity each arm actually receives after tool rejection, absorbing states, unavailable counterfactuals and early termination.

And the stochastic-control contract must distinguish:
- `environment_CRN`: event-keyed where stable event identity exists;
- `model_CRN`: only claimed when the model sampler supports a causally meaningful coupling after divergence;
- `control_branch_noise`: same-model branch variance when model CRN is unavailable.

This prevents two new false conclusions: (a) a target selector looks better because it effectively gets more usable recovery work, or (b) a target selector looks causal because both arms happened to start from the same PRNG seed even though the intervention shifted the downstream draw sequence.

## Strict selector-only gap status
Still open. I did not locate a software/tool/GUI-agent study that simultaneously fixes:
- target objective,
- alarm / intervention eligibility,
- admissible checkpoint candidate set,
- restore and failed-branch carry-forward policy,
- model and verifier,
- probe budget,
- allocated **and realized** recovery opportunity,
- stochastic coupling / replay-noise treatment,
while varying only the historical target selector and measuring final live task success.

## Exact continuation
1. Search for selector studies that report **realized** post-rollback model/tool/action counts, not only nominal limits, and test whether rollback depth changes effective opportunity.
2. Search state-only failure localizers that output calibrated top-k distributions / conformal sets / abstention, then audit them against executed replay rather than annotated correctness.
3. Search software/tool-agent systems using event-keyed or counter-based RNG for counterfactual branch coupling; distinguish environment coupling from LLM-sampler coupling.
4. Search local/open-model inference stacks for a practical token/event-keyed sampler or reproducible sampler-state checkpoint that could couple branches after the historical target while allowing control-flow divergence.
5. Add to the Replay Gap/Shepherd blueprint: `realized_model_calls`, `realized_admissible_actions`, `successful_tool_calls`, `unused_budget_reason`, `environment_CRN_method`, `model_CRN_method`, `event_identity_map`, and same-model control-branch variance.
6. Treat AgentLocate/BranchPoint-like methods as candidate/probe allocators unless held-out live rollback outcomes establish target utility.
7. Preserve the target-semantics split: earliest causal origin, first sufficient intervention point, latest rescue/point-of-commitment, latest admissible/safe checkpoint, and intended semantic version are different labels.
8. Preserve the strict selector-only gap unless all non-target variables are genuinely controlled.
9. Maintain a nonempty frontier; findings/checkpoints are never global completion.
