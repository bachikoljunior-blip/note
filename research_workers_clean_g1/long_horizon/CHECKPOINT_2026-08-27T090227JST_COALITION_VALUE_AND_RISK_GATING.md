# Long Horizon clean_g1 — coalition-conditioned value and risk-gated maintenance

Checkpointed: 2026-08-27T09:02:27+09:00

## Frozen semantic control tuple
- note main SHA: `72c4b5abe2678e96c79ae2feae09cd0b02d97552`
- root control revision: `11`
- role config revision: `5`
- root blob: `bf7b8c7f6971c0ec2f3fa7a8d53dca1f88ac50a3`
- role config blob: `268523da20c78ce3091344c492ad3d51f6f9e667`
- Both pre-semantic SHA-only ref lookups matched. This tuple was frozen before the first role-local semantic read and later repository changes were not adopted as semantic control.

## Clean-boundary declaration
Semantic inputs in this invocation were limited to this worker's own clean `LATEST.md` and latest own checkpoint, the sanitized root manifest, this role's own config, and public sources. No O/O-derived state, other worker state/output/config, downstream comparator/integrator/index/feed/audit state, legacy/pre_independence research, shared `EXECUTION_LEDGER.json`, or other-role receipts were read or used semantically.

## New evidence delta

### 1. OLE defines governance semantics, but its concrete scheduler thresholds remain unavailable
The official `yoyoshikc/OpenLoopEvolve` repository currently contains only a README stating that source code and documentation are being prepared for release. The paper specifies a trigger `Trig` that can depend on feedback amount, update period, or task stage; trigger starts evolution but does not decide release. It also specifies a Champion–Challenger release gate combining benefit, evidence quality, tail risk, and resource-cost constraints, plus CanaryMonitor rollback after degradation. However, the public paper/repository inspected here did not expose concrete numeric trigger thresholds, CanaryMonitor degradation thresholds, or a threshold/cost ablation that validates a maintenance scheduler.

Primary/public sources:
- https://arxiv.org/abs/2608.09380
- https://github.com/yoyoshikc/OpenLoopEvolve

Scope: this narrows an unresolved mechanism detail; it does not weaken the previously observed paired release/rollback evidence.

### 2. Current skill value is coalition- and deployment-conditioned, not an intrinsic scalar
`Coalition-Aware Skill Reliability for Self-Evolving Agents` (arXiv:2608.22610, Aug. 23 2026) directly challenges isolation-only skill lift. Its audits find coalition pollution and cross-domain utility reversal. In a reported audit, an admitted candidate had only +0.006 aggregate admission margin while post-hoc paired analysis assigned the new `capture_activity_preferences` skill a −0.005 marginal contribution and an incumbent `insert` skill +0.084; removing a coalition partner reduced the latter marginal to +0.018. The same skill can also help in one source domain and harm after transfer.

CASS uses sampled coalitions/Shapley-style marginals during accumulation. Across 12 candidate proposals (4 epochs × 3 seeds), CASS accepted 1/12 while the MemSkill baseline accepted 6/12. Holding bank size fixed, the additional MemSkill skills were collectively −1.38 percentage points on average across the reported LoCoMo/LongMemEval/HotpotQA-50 evaluation. u-SMCO then performs label-free target-domain masking: across six banks, masking improved every bank; the reported average gain was 7.17 pp for MemSkill banks versus 3.59 pp for CASS banks. Its retrieval-quality proxy correlated with target label-based skill ranking at rho=+0.76, while a preferred-skill entropy proxy anti-correlated at rho=−0.18.

Cost is nonzero but bounded in the reported setup: CASS adds eight coalition evaluations per outer epoch, approximately 5% of a 20-hour run; u-SMCO is an O(K^2) one-time target-domain masking procedure, reported at roughly 6–10 minutes per mask step.

Primary source: https://arxiv.org/abs/2608.22610

Implication: a maintenance controller should not treat `current marginal skill value` as a context-free property. Bank composition and deployment domain are part of the value state. Isolation-based paired lift remains useful, but can miss interaction effects.

### 3. SkillForge provides a practical usage-triggered maintenance sensor, but its credit is not causal under skill interactions
`SkillForge: Evolving Verifiable Skills for Reinforcement Learning Agents` (arXiv:2608.24747, Aug. 25 2026) makes skill calls explicit and continuously updates a per-skill EMA success estimate from episode reward, tracks use count, and ranks underperformance using a usage-weighted score. High-scoring skills are reviewed against recent usage contexts and either kept or revised. The bank is updated every 5 training steps in the reported configuration, with multi-pathway induction from success, failure, or contrastive trajectories.

On Qwen3-4B, the reported ablation is:
- Full SkillForge: ALFWorld 87.9, AppWorld TGC 44.6
- without Effectiveness Tracking: 83.6 / 36.3
- without LLM Reflexion: 82.1 / 39.3
- without Multi-Pathway induction: 82.1 / 36.9
- without Deduplication: 86.4 / 38.7
- without Explicit Calling: 77.9 / 33.3
- without Skill Bank: 79.3 / 34.5

Reported skill-related overhead remains under 10% on all three environments: AppWorld 4.18%, ALFWorld 9.48%, WebShop 9.47%. The authors report final SkillForge results above the GRPO comparison while overall wall-clock is similar or lower in two of the three environments.

Primary source: https://arxiv.org/abs/2608.24747

Negative/scope evidence: the EMA assigns the whole episode outcome to each invoked skill. The coalition paper shows that outcome-only attribution can be structurally blind when skills interact. Therefore SkillForge's score is strong evidence for a cheap operational *sensor/triage heuristic*, not proof of clean causal marginal value. A plausible but unvalidated cascade is cheap usage/EMA sensing followed by expensive paired/coalition audit only for consequential revise/retire decisions.

### 4. Benefit and consequence can move in opposite directions; release/maintenance cannot optimize task utility alone
`Auditing Self-Evolution in Financial Agents` (arXiv:2608.17684, Aug. 18 2026) provides matched simulated-banking evidence that capability gain can co-occur with increased security exposure and unauthorized state changes. For Qwen 3.7 Flash, SkillOpt raises benign utility from 0.741 to 0.837 while injected-content exposure rises 0.820→0.943, aggregate ASR rises 0.496→0.530, and unauthorized financial state change rises to 0.685. Across three independent evolved lineages, utility, exposure, and unauthorized-state changes increase in all three; ASR increases in two of three.

A separate execution-interface sensitivity test shows another validity axis: a literal WebArena text-action envelope causes AWM utility 0.319 in a native function-calling executor, while removing only that envelope restores utility to 0.756. Thus a semantically useful artifact can be operationally invalid for a target executor/interface.

Primary source: https://arxiv.org/abs/2608.17684

Implication: `consequence` should not be compressed into a generic benefit scalar. Safety/state-harm constraints and executor/interface compatibility should be explicit release/maintenance gates or vector-valued objectives.

### 5. Decision-time applicability boundaries are a separate layer from bank maintenance
`When Not to Imitate: Boundary-Aware Skill Memory for Reliable Tool-Use LLM Agents` (arXiv:2608.22339, Aug. 23 2026) reports a Skill Imitation Trap: in lookalike tasks requiring different tools, success-derived procedure skills increase wrong-tool margin by 47% over a memory-free baseline. BASM augments skills with applicability conditions, risk cues, avoidance rules, and recovery notes; across its reported benchmarks it improves AppWorld task success by up to 23.8%, BFCL accuracy by up to 5.0%, reduces AgentDojo attack success by 4.6%, and can reduce AppWorld steps by up to 6.6% relative to memory-free.

Primary source: https://arxiv.org/abs/2608.22339

Scope: BASM is evidence that a validated skill still needs state-conditioned activation boundaries. It does not replace admission, drift detection, coalition audit, or longitudinal maintenance.

## Revised synthesis — hypothesis, not an observed end-to-end controller
The maintenance problem should now be separated into at least five quantities:
1. **Invalidation/drift hazard** — operational contract/release/API/dependency/schema change or observed failure evidence.
2. **Coalition-conditioned value at risk** — marginal contribution under the current bank composition, target model/harness, and deployment domain, not a context-free skill score.
3. **Consequence / constraint vector** — task utility, unauthorized state/exposure risk, tail risk, executor/interface validity, and other domain-specific hard constraints.
4. **Affected/replay blast radius** — the smallest support/behavior set needing verification or repair.
5. **Audit/repair/release cost and uncertainty** — compute, latency, sample uncertainty, and false-edit risk.

A conceptual audit priority such as
`invalidation hazard × coalition-conditioned value-at-risk × consequence / (audit + repair + release-validation cost)`
with hard safety/interface constraints and uncertainty-aware abstention is now more defensible than the earlier scalar isolated-skill-lift heuristic. It remains a research hypothesis: no study found in this run jointly optimizes all these terms end-to-end in a software/API/tool agent.

A potentially efficient two-tier controller is also only a hypothesis:
- cheap continuous sensor: usage/EMA, contract drift, or retrieval anomalies;
- expensive targeted audit: paired/coalition counterfactual evaluation under current bank/domain before consequential revise/retire/release;
- decision-time boundary gate: applicability/risk/avoidance constraints when the skill is actually retrieved.

## Negative evidence and exact scope guards
- CASS/u-SMCO is primarily skill-bank/memory reliability evidence across the reported agent benchmarks; it is not a validated software/API maintenance scheduler.
- Coalition marginals are more interaction-aware but costlier and still dependent on sampled coalitions/proxies.
- SkillForge is an RL-training framework using explicit skill calls and a teacher/reflection loop; its per-skill EMA is not a causal marginal estimator under interactions.
- The financial audit is a simulated banking domain; do not generalize its exact risk magnitudes to other agent classes.
- BASM shows activation-boundary benefit, not longitudinal bank-governance sufficiency.
- OLE's official code is not yet publicly released in the inspected repository; concrete trigger/degradation thresholds remain unresolved, not disproven.
- The exact common-replicate four-cell `admission gate ON/OFF × post-admission maintenance ON/OFF` interaction remains unresolved.
- No end-to-end controlled study was found that jointly varies drift hazard, coalition-conditioned marginal value, consequence/tail risk, maintenance cost, and false-edit risk under one fixed software/API-agent stream.

## Exact continuation / nonempty frontier
1. Search SkillForge author artifacts/code and appendix details for EMA alpha, usage half-life `h`, review-selection thresholds, and sensitivity/cost ablations; separate fixed engineering choices from validated scheduler behavior.
2. Search Coalition-Aware author artifacts/checkpoints and appendices for CASS sample count/threshold sensitivity, proxy failure cases, and u-SMCO masking-cost/stop criteria.
3. Search for a two-stage `cheap sensor → expensive coalition/counterfactual audit` scheduler, ideally framed as value-of-information or audit allocation, with matched final task outcome and audit cost.
4. Continue Repo2Skill-Evo artifact/data search and GSE affected-set replay cost/ablation search.
5. Continue the common-replicate four-cell admission-gate × post-admission-maintenance interaction search.
6. Continue multi-generation hidden semantic-lineage discovery/repair, rollback-target selector comparisons, and decision-influence audits under fixed controls.
7. Preserve exact tested scope and a nonempty frontier; this checkpoint is not global completion.
