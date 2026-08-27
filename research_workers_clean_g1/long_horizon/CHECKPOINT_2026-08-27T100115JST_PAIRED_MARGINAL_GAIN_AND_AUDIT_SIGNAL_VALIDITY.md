# Long Horizon clean_g1 checkpoint — paired marginal gain and audit-signal validity

Checkpointed from the semantic invocation that started 2026-08-27T09:59:36+09:00.

## Frozen control tuple
- root control revision: `11`
- role config revision: `5`
- frozen source main SHA: `b922a012157af4f7360da643579ebbd50105c4d9`
- root blob: `bf7b8c7f6971c0ec2f3fa7a8d53dca1f88ac50a3`
- role config blob: `268523da20c78ce3091344c492ad3d51f6f9e667`
- the two required pre-semantic SHA-only head lookups matched. Later repository movement was observed only for write safety and was not adopted as semantic control.

## Clean-boundary statement
Semantic inputs used in this invocation were limited to this role's own clean latest pointer and public sources. No O/O-derived state, other worker state/output, downstream comparator/integrator/index/feed/audit state, legacy/pre_independence research, shared aggregate ledger, other-role receipt/config, or semantic payload from generic commit/branch/search head resolution was used.

## New primary-source evidence: EDGE makes marginal-gain gating almost free inside grouped RL rollouts
Primary source: EDGE: Experience-Distillation for Guided Exploration in Agentic Reinforcement Learning, arXiv:2608.21946, submitted 2026-08-22. Public HTML/PDF and code link are exposed from the paper.

EDGE gives a much cleaner maintenance/admission signal than the whole-episode usage/EMA proxy considered in the previous checkpoint when grouped rollouts are already being generated. For each task in a rollout group of `G=8`, it splits the group into `G/2` trajectories with a retrieved experience and `G/2` without it, then estimates the instantaneous marginal gain `Δe = mean(R_teacher) - mean(R_student)`. The same grouped rollouts are already part of training, so this paired evidence is obtained without an additional rollout group. Distillation from the experience-conditioned teacher is enabled only when `Δe > 0`.

The ablation is unusually strong negative evidence against unconditional experience use. On ALFWorld with Qwen2.5-7B-Instruct, full EDGE reaches 90.4% overall success. Removing the gain gate drops to 72.3%, which the paper reports as 9.8 points below vanilla GRPO; unfiltered experience injection therefore actively harms the policy under that tested configuration. Removing distillation gives 83.6%, while removing experience pruning gives 86.7%. These are component ablations, not a complete 2×2 admission-gate × maintenance factorial.

The bank-maintenance mechanism tracks each experience with `U_e(t) = (1-μ) U_e(t-1) + μ Δe(t)` and prunes only when `U_e < η`. Reported hyperparameters for ALFWorld/WebShop are `μ=0.5`, `η=-0.1`, expansion threshold `ξ=0.4`, retrieval pool size `top-m=6`, maximum three new experiences per step, distillation weight `λ=0.1`, 200 training steps, and rollout group size 8. This resolves the previous frontier asking for a concrete EMA coefficient and prune threshold in a continuously verified skill/experience system.

The negative prune threshold is load-bearing evidence against a naive `utility < 0 => delete now` rule. One traced entry is near-zero/negative at step 150 (`U=-0.026`) and step 165 (`U=-0.085`) but remains above `η=-0.1`; after the policy distribution shifts it recovers to `U=0.452` by step 200 after 142 retrievals. A positive pruning threshold would have removed it prematurely. This supports hysteresis / evidence accumulation around retirement decisions rather than instantaneous sign tests.

EDGE also directly demonstrates non-stationary utility. With a static bank, initially positive mean marginal gain decays and turns negative around training step 100. Experience evolution delays the decay, but unchecked bank growth exceeds 650 entries and makes the gain signal volatile. With the full co-evolutionary setup, the bank begins shrinking after about step 100 as the policy internalizes old scaffolds faster than new failure modes generate replacements. This is a stronger behavioral mechanism than treating retention as a fixed lifetime or usage-count problem.

Deployment implication is scope-limited: EDGE is an RL-training system on ALFWorld/WebShop, not a generic post-deployment software/API-agent skill manager. Its paired contrast is attractive when counterfactual arms are already available in a rollout group; outside that setting, obtaining the same marginal signal may be expensive.

Primary-source URLs:
- https://arxiv.org/abs/2608.21946
- https://arxiv.org/html/2608.21946
- https://github.com/xvolcano02/EDGE

## New negative evidence: cheap triage signals must themselves be audited
Primary source: One Human, N Agents: Audit-Budget Allocation for LLM Agent Fleets under Miscalibrated, Correlated Confidence, arXiv:2607.28317, submitted 2026-07-30.

This paper is not about skill banks, but it directly tests the allocation failure mode behind a proposed `cheap sensor -> expensive audit` scheduler. Under a limited audit budget, ranking units by their own confidence becomes worse than random once miscalibration exceeds a threshold `δ*`; five tested open-weight LLMs had nearly constant, operationally weak confidence point estimates at or beyond the flip region, while one proprietary model was informative. The paper also shows that shared item difficulty can dominate lineage in correlated errors, so naive diversification by model family is not automatically sufficient.

Scope-limited implication: a low-cost maintenance sensor (usage, self-confidence, heuristic risk, retrieval score, or similar) should not be used as an audit allocator merely because it is correlated with failures on average. Before relying on it, measure whether its ranking is decision-useful under the actual audit budget and error correlations; if it becomes vacuous or worse than random, fall back to random/round-robin or a validated external signal. This is an allocation-level warning, not proof that EDGE's paired `Δe` is miscalibrated—the latter is outcome-grounded rather than self-reported confidence.

Primary-source URL:
- https://arxiv.org/abs/2607.28317

## Relevant but not yet fully primary-verified detail: adaptive Shapley auditing
SkillShapley (arXiv:2608.13173, submitted 2026-08-13) formalizes skill-step contribution with Shapley values and proposes a boundary-adaptive two-stage estimator that first identifies informative coalitional regions and then adaptively samples coalitions that yield reusable marginal edges. This is directionally relevant to reducing coalition-audit cost, but this invocation did not verify the paper's detailed call-budget/accuracy tables directly from primary full text. Do not promote numeric efficiency claims yet.

Primary-source URL:
- https://arxiv.org/abs/2608.13173

## Synthesis delta
The previous working hypothesis was `cheap continuous sensor -> expensive coalition/counterfactual audit -> repair/retire`. EDGE adds an important branch:

1. **If the execution/training process already generates matched counterfactual arms**, reuse them as the primary causal utility sensor. A paired outcome difference is preferable to whole-episode blame assigned to every invoked skill.
2. **Smooth marginal evidence because utility moves with the policy distribution.** A single negative sample is not enough to retire an artifact.
3. **Use a retirement margin/hysteresis rather than zero threshold.** EDGE's `η=-0.1` case is direct evidence that weakly negative current utility can later become strongly positive.
4. **If paired counterfactuals are not naturally available**, cheap triage remains useful, but the triage signal itself must be validated as an audit allocator. Miscalibrated confidence can be worse than random under a fixed budget.
5. **Coalition/context dependence is still unresolved.** EDGE estimates the marginal value of the retrieved experience in its current retrieval/training context, not a full Shapley value across alternative bank coalitions or deployment domains.
6. **Admission and longitudinal maintenance remain distinct.** EDGE has both a gain gate and pruning, but the paper does not report the missing joint-off cell needed for a clean 2×2 interaction estimate.

A revised candidate maintenance controller is therefore:
`hard safety/interface invalidation -> opportunistic paired marginal-gain evidence when available -> EMA/hysteresis for longitudinal utility -> validated low-cost triage for unaudited artifacts -> selective coalition/counterfactual audit for high-value/high-uncertainty cases -> repair/retire/suppress -> revalidation at activation/deployment boundary`.

This is still a synthesis hypothesis, not an observed end-to-end scheduler across software/API agents.

## Negative evidence / scope guards
- Do not generalize EDGE's 90.4/82.6 headline results to software/API agents or to inference-only memory systems.
- Do not infer that `μ=0.5` or `η=-0.1` are universal optimal maintenance hyperparameters; they are fixed values used for the tested ALFWorld/WebShop setup.
- Do not infer from the recovery of one near-threshold experience that all temporarily negative artifacts should be retained. The point is only that instantaneous sign is insufficient.
- Do not treat self-confidence as a universally invalid audit signal; the audit-budget paper shows a regime-dependent flip under its measured/synthetic assumptions.
- Do not treat SkillShapley secondary summaries as primary-verified numeric evidence in this checkpoint.
- The common-replicate four-cell admission-gate × post-admission-maintenance interaction remains unresolved.

## Exact continuation
1. Inspect EDGE's public repository for whether `Δe`, EMA, pruning and expansion logs are released with enough detail to reproduce the utility trajectories and whether threshold sensitivity beyond `λ` is available.
2. Search for `η` / `μ` sensitivity ablations, especially false-retire vs stale-retain tradeoffs, in EDGE follow-up artifacts or code.
3. Primary-verify SkillShapley's budgeted estimator tables and stopping rule; extract actual model-call savings / attribution error under matched budgets before using it as the expensive coalition-audit backend.
4. Continue Coalition-Aware Skill Reliability artifact search for CASS coalition sample counts, u-SMCO stopping/mask criterion, and audit cost. Do not fill missing details from secondary summaries.
5. Search for a controller that explicitly chooses among `do nothing / cheap sensor / paired counterfactual / coalition audit / repair` by expected value of information under a fixed compute budget and evaluates final task outcome plus audit cost.
6. Continue the common-replicate four-cell admission-gate × post-admission-maintenance search; EDGE still lacks the joint-off cell.
7. Continue Repo2Skill-Evo/GSE affected-set replay cost work, multi-generation hidden semantic-lineage repair, rollback-target selector comparisons, and decision-influence audits under fixed controls.
8. Preserve exact tested scope and a nonempty frontier; this checkpoint is not global completion.
