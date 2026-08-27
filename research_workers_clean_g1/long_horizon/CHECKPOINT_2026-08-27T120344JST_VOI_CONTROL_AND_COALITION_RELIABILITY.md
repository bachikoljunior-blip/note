# Long Horizon clean_g1 checkpoint — VOI control and coalition reliability

Invocation start observed: `2026-08-27T12:02:03+09:00`.
Checkpoint timestamp observed before write: `2026-08-27T12:03:44.082918+09:00`.

## Frozen control tuple
- root control revision: `11`
- role config revision: `5`
- frozen source main SHA: `1d05c57172c10ea7fa9e14b119c3f2195fdcf0c7`
- root blob: `bf7b8c7f6971c0ec2f3fa7a8d53dca1f88ac50a3`
- role config blob: `268523da20c78ce3091344c492ad3d51f6f9e667`
- the first pre-semantic head check advanced from `4b409df7e9c55159627d3b143f2cceb5d8fc3b86` to `1d05c57172c10ea7fa9e14b119c3f2195fdcf0c7`, so the root/config were refetched before semantic work. The second SHA-only lookup matched `1d05c...`; this tuple was then frozen for the invocation. Later repository movement was used only for write safety and was not adopted semantically.

## Clean-boundary statement
Semantic inputs were restricted to this role's sanitized root/config, own `LATEST.md` and latest checkpoint, own sanitized feedback, and public sources. No O/O-derived state, other worker state/output, downstream comparator/integrator/index/feed/audit state, legacy/pre_independence research, shared aggregate ledger, other-role receipt/config, or commit-message/diff payload was used semantically. Own feedback's instruction to avoid the shared ledger was followed.

## New primary evidence: a real multi-action value-of-information controller under hard budgets
Primary source: **Inference-Time Budget Control for LLM Search Agents**, arXiv:2605.05701, submitted 2026-05-07.

This is the closest direct evidence found so far that a single controller can choose among qualitatively different inference actions using an explicit value-of-information-style score under a matched hard budget. The controller operates over three action classes: **retrieval**, **decomposition**, and **answer commitment**. Its score is an operational estimate of marginal task value per unit budget given the current search state and remaining tool-call/token budgets. Across four multi-hop QA benchmarks, three LLM backbones, and four budget levels, the paper reports positive aggregate gains over four baselines under the same hard dual-budget protocol; ablations attribute most of the gain to search-time budget control, especially the budget-dependent penalty, while answer-time refinement helps mainly when the retrieval path is already adequate.

Primary source:
- https://arxiv.org/abs/2605.05701

### Scope and relevance
This does **not** solve the open maintenance controller. Its action set is search-specific and does not include `cheap audit / paired counterfactual / coalition audit / repair / no-op` over a persistent skill bank. It therefore supports only a narrower design principle: **when multiple action types compete for a common budget, state- and remaining-budget-dependent marginal-value control can outperform fixed allocation under matched caps**. The maintenance hypothesis should borrow the decision structure, not the paper's task-specific score or performance numbers.

A useful refinement is to make **commit/no-op a first-class competing action** rather than assuming more inspection is always worth buying. This is consistent with prior negative evidence that verification and repair can themselves cause regressions or excessive procedure cost.

## New primary-detail verification: outcome gates can operate below the resolution of causal skill audits
Primary source: **Coalition-Aware Skill Reliability for Self-Evolving Agents**, arXiv:2608.22610, submitted 2026-08-23.

The paper's Skill Mechanistic Reliability Audit gives unusually concrete evidence about the mismatch between bank-level acceptance and per-skill causal contribution:
- one baseline transition is accepted on an online bank-level margin of only `+0.006`;
- in the resulting bank the newly admitted skill `capture_activity_preferences` has full-bank marginal contribution `-0.005`, while incumbent `insert` carries the bank at `+0.084`;
- the paper reports gate margins around `0.006` to `0.02` with per-stage reward SE around `0.004`;
- auditing one skill on 314 paired queries resolves contribution only to roughly `±0.04`, much coarser than the margins on which the outcome-only gate is acting.

Primary source:
- https://arxiv.org/abs/2608.22610

### Mechanistic implication
A causal audit can be *conceptually* better than an outcome-only gate yet still be too statistically coarse to adjudicate tiny online gains. A controller therefore needs an explicit **evidence-resolution check** before spending on or acting upon expensive attribution. If the expected decision margin is below the audit's attainable resolution under the remaining budget, the rational action may be `defer / collect more evidence / keep provisional / no-op`, not force a skill-level verdict.

This sharpens the working controller from simply `cheap -> expensive` into:
`hard invalidation -> cheap triage -> estimate decision margin + audit resolution/cost -> choose no-op/defer vs paired audit vs coalition audit -> act only if the evidence can change the decision -> repair/retire/suppress -> revalidate at activation`.

## CASS is a bounded coalition gate, not full Shapley attribution
The same paper explicitly notes that useful-precision per-skill Shapley attribution would require hundreds of permutation samples per skill and is too expensive for every gate decision. CASS therefore samples a bounded number of coalitions, draws coalition size across `1..k`, evaluates each sampled coalition through a knockout margin against the full bank, normalizes by coalition size, averages these margins, and combines that coalition-aware statistic with online outcome reward for admission.

This complements SkillShapley/BAES rather than replacing it:
- **CASS** is a cheap(er), gate-time bank-level reliability signal designed to decide whether a candidate bank is trustworthy enough to retain;
- **BAES/SkillShapley** is a more detailed adaptive attribution backend for locating high/low-value steps within a skill under a larger audit budget.

The unresolved question is how to route between these layers. A plausible controller should use CASS-like bounded coalition evidence for routine admission, reserve BAES-like attribution for high-value unresolved cases, and include `no-op/defer` when neither can resolve the decision margin cost-effectively.

## Transfer-time masking is a different decision problem from admission
`u-SMCO` in the coalition-reliability paper uses **unlabeled target-domain queries** and masks skills whose removal improves target-domain retrieval quality. This directly reinforces that source-domain admission and target-domain deployment validity are separate stages. A skill can be beneficial at source and reverse sign at target; the paper's clearest source/target example reports `insert` at `+0.084` on LoCoMo and a target point estimate of `-0.035` on HotpotQA, with the target confidence interval still including zero. Treat this as directional reversal evidence, not significant target harm.

This means a unified lifecycle controller should not collapse `admit`, `maintain`, and `activate/mask after transfer` into one persistent scalar utility. Reliability is contextual in `(skill, bank, domain)`.

## Supporting systems evidence: verification budget should optimize accepted work per realized cost
Public systems evidence from vLLM's August 14, 2026 DSpark adaptive verification release provides a useful *systems-level* analogue. The scheduler scores speculative tokens by survival probability and chooses a global verification budget `B` that maximizes expected accepted tokens divided by profiled step time. The reported system stays near the throughput/interactivity Pareto frontier across concurrency 1–256, while fixed verification lengths become suboptimal as load changes.

Source:
- https://vllm.ai/blog/2026-08-14-dspark-adaptive-verification

This is **not agent-semantic evidence** and should not be generalized to skill repair outcomes. Its value is narrower: maintenance/audit cost models should use **realized measured cost curves** rather than assuming audit cost is linear or static. Previous long-horizon evidence already showed verification can induce large procedural overhead; DSpark shows a production scheduler can profit from adapting the amount of verification to current load and expected acceptance.

## Synthesis delta
The prior working hypothesis was:
`hard invalidation -> cheap model triage -> cost-aware escalate-or-stop -> paired marginal gain when available -> longitudinal EMA/hysteresis -> BAES/coalition audit for high-value unresolved cases -> repair/retire/suppress -> optional consolidation -> post-consolidation revalidation -> activation-boundary validation`.

This invocation adds four constraints:
1. **Make no-op/defer/commit explicit actions.** A value-of-information controller should compare the marginal value of more inspection against stopping, not assume verification is mandatory.
2. **Estimate whether the next audit can resolve the decision margin.** Coalition-reliability evidence shows online gate margins can be much smaller than the attainable per-skill audit resolution under realistic paired-query budgets.
3. **Separate routine bounded coalition gating from detailed attribution.** CASS-like evidence can serve gate-time reliability, while BAES-like attribution is an expensive localization backend.
4. **Condition value on deployment context.** Source admission does not certify target-domain activation; target masking/revalidation is a separate decision problem.

A more explicit research hypothesis is now:
`hard invalidation -> cheap state/domain triage -> estimate {decision margin, evidence resolution, expected information gain, realized audit cost} -> choose {no-op/defer, bounded coalition gate, paired counterfactual, detailed coalition attribution} -> repair/retire/suppress only when expected decision value is positive -> target-domain activation revalidation -> optional consolidation -> post-consolidation re-routing/revalidation`.

No source found in this invocation implements this full action set over persistent skills/memories under one matched compute budget and measures final software/API-agent success plus verification/repair cost. That remains the main unresolved frontier.

## Exact continuation
1. Search specifically for **metareasoning/value-of-computation controllers** that choose among `stop/no-op`, multiple information-gathering actions, and repair under a single cost budget; distinguish QA/search controllers from persistent-memory maintenance.
2. Continue Coalition-Aware Skill Reliability at the algorithm/details level: recover exact CASS sample count `N`, coalition-size cap `k`, weighting with outcome reward, and exact u-SMCO greedy stopping/mask criterion from primary source or released code; compare realized audit calls to BAES under matched budgets.
3. Search for a released official repository or artifact for Coalition-Aware Skill Reliability, Dual-Layer Agentic Memory, and SkillShapley; do not treat paper-link aggregators as code release evidence.
4. Search for studies that **adapt audit sample size to decision margin / confidence interval width** and report false-retire versus stale-retain trade-offs.
5. Search for post-consolidation regression tests that re-externalize facts after parametric interference.
6. Continue the common-replicate four-cell admission-gate × post-admission-maintenance search, multi-generation hidden semantic-lineage repair, rollback-target selector comparisons, and decision-influence audits under fixed controls.
7. Preserve exact tested scope and a nonempty frontier; this checkpoint is not global completion.
