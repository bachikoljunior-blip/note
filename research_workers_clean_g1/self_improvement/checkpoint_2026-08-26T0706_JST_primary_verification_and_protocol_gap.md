# CLEAN self-improvement checkpoint — primary verification, evaluation separation, and protocol reproducibility

Run timestamp: 2026-08-26 07:06 JST
Role: self_improvement / clean_g1
Frozen semantic control tuple: note main `b9352a1b52d5ffda8ab0d7c8344247dda22418cc`; sanitized root `automation_control/DESIRED_STATE.json` control_revision=9 blob `2e1f998368a6848e737aa108c838edb4ad355cdb`; own role config_revision=5 blob `e887cc0b81760e87fc04d80d3e7ee63cc6cb6fe6`.
Continuation source: own `LATEST.json` -> `research_workers_clean_g1/self_improvement/checkpoint_2026-08-26T0559_JST_feedback_gradient_and_skill_attribution.md`; own sanitized feedback item was already acknowledged and only reinforces source-qualified IDs. No O/O-derived state, other worker state/config, downstream comparator/integrator/index/feed/audit state, legacy/pre_independence research, shared aggregate ledger, or other-role receipt/config was used semantically. Control freshness was resolved with a SHA-only Git ref lookup and rechecked immediately before the first substantive semantic read; the frozen tuple above remained unchanged.

## SIG-SKILLEVO-PRIMARY-SPLIT-AND-GOVERNANCE

Primary: Qianxi Yan, Chunrong Chen, Jiuzhou Zhao, Min Zhang, Yongzhou Xu, Xiaochuan Xu, *SkillEvo: Self-Renewing Evolution Gradients from Multi-Turn Interaction Feedback*, arXiv:2608.13120, 13 Aug 2026.
Primary source: https://arxiv.org/abs/2608.13120

### Primary-verified experiment structure

The full paper, not merely a secondary extraction, confirms that the production benchmark covers six Tencent Cloud categories, nine production Skills, 98 skill-reference files, and 2,000 real support tickets. Within each Skill, tickets are ordered chronologically and divided into four equal partitions. The first three quarters form the development side that drives scenario synthesis, simulated interactions, failure attribution, revision, and version selection. The final quarter is a held-out evaluation set that does not feed any stage of the evolution loop and is used only for measurement/reporting.

This materially strengthens the evidence boundary from the prior checkpoint: SkillEvo does have an untouched outer evaluation partition for the reported four-round experiment. It therefore separates development-loop optimization from final measurement more cleanly than systems that repeatedly recycle the same evaluation set as their gate.

### Primary-verified quantitative results

Table 2 reports Task Success Rate (TSR):

- Initial hand-authored Skill: **30.0%**.
- Self-Reflection: R1 **59.2**, R2 **58.7**, R3 **57.4**, R4 **58.8**.
- Single-turn QA feedback: R1 **58.9**, R2 **64.5**, R3 **65.7**, R4 **66.4**.
- SkillEvo multi-turn interaction feedback: R1 **59.4**, R2 **71.3**, R3 **77.9**, R4 **81.8**.

For Single-turn QA and SkillEvo, the reported round value is the best version selected on the development set up to that round. Thus the increasing SkillEvo curve is partly a **best-so-far selection curve**, not proof that every newly produced current revision is monotonic.

Table 3 directly verifies the matched headline ablation at R4: full SkillEvo **81.8**, Single-turn QA **66.4**, and SkillEvo without Governance **78.6**. Under the paper's held-fixed attribution/revision/governance comparison, changing the feedback source from single-turn QA to multi-turn interaction corresponds to the reported **+15.4-point** gain. The primary abstract's +23.0-point gain over self-reflection is also consistent with 81.8 versus 58.8.

The primary paper further verifies cross-round regression rates of **28.2% -> 24.4% -> 21.1%** for R1→R2, R2→R3, R3→R4, a 7.1-point first-to-last reduction, and cumulative knowledge bloat of **+2.8% with governance versus +16.2% without governance**. Simulator diagnostics report **98.9%** intent coverage, **95.3%** human-rated fidelity/similarity on a 200-dialogue blinded expert sample, and **71.1%** exposed-intent agent accuracy.

### Admission semantics and scope boundary

The algorithm distinguishes hard factual consistency from softer structural recommendations. Candidate versions that violate factual anchors are repaired/rejected; structural-consistency signals can guide subsequent repair. The system then selects a development-best version and evaluates only that selected version on the untouched evaluation partition. This is stronger than an ungated streaming overwrite, but it is **not an anytime-valid or multiplicity-controlled statistical acceptance rule across arbitrarily many proposals**.

The experiment spans four evolution rounds, so it still does not resolve the prior >10-round adaptive-reuse frontier. Also, because development-best selection is adaptive, the untouched final partition is essential: the dev curve itself should not be treated as unbiased final generalization evidence.

### Mechanism implication within tested scope

The prior distinction between **gradient starvation** and **promotion error** becomes sharper. SkillEvo gives primary evidence that richer multi-turn probes can keep surfacing actionable defects after single-turn feedback saturates, while its governance layer reduces structural bloat and cross-round regressions. But its four-round design does not establish long-horizon statistical safety under repeated adaptive proposals.

## SIG-SKILLSHAPLEY-PRIMARY-ATTRIBUTION

Primary: Chang Liu, Yuqi Zhang, Yiman Zhong, Boyi Liu, Hengjun Wang, Shuyue Wei, *SkillShapley: Boundary-Adaptive Shapley Valuation for Skill Step Attribution in LLM Agents*, arXiv:2608.13173, 13 Aug 2026.
Primary source: https://arxiv.org/abs/2608.13173

### Primary-verified setup

The primary full text verifies that the unit of attribution is a semantically coherent instruction block inside a fixed `skill.md`. Frontmatter is preserved, auxiliary files/scripts stay unchanged, and task prompts, system prompt, output format, benchmark instances, scoring, and OpenHands execution harness are held fixed. The exact-reference validation uses three low-step-count SkillsBench skills: offer-letter-generator, manufacturing-FJSP-optimization, and dialogue parser, with temperature 0.

The paper compares exact Shapley attribution against Individual evaluation, Leave-One-Out, Random Removal, and LeastCore. Removing the top-ranked blocks according to full Shapley causes the fastest utility degradation across the three exact-reference tasks, providing direct behavioral validation that the ranking identifies consequential blocks under this fixed-skill protocol.

### Primary-verified approximation result

For a 10-player SkillsBench pilot under a matched budget of **99 unique evaluated configurations**, Boundary-Adaptive Edge Shapley (BAES) yields **206 reusable one-flip marginal edges**. Monte Carlo permutation sampling under the same unique-configuration budget yields **130 marginal observations / 115 unique marginal edges**. The reported error curves show BAES reaching lower mean absolute error under small evaluation budgets than the compared Monte Carlo, quasi-Monte-Carlo, antithetic, and truncated alternatives in the surfaced experiments.

The paper explicitly cautions that the finite adaptive-budget BAES estimator is a **biased approximation optimized for low-budget ranking recovery**, not a finite-sample unbiased estimator of exact Shapley values.

### Boundary conditions

The exact-reference experiments are intentionally limited to low-step-count fixed skills. The method assumes a stable player set and a sufficiently stable benchmark signal. In strongly coupled assembly-line workflows, a step can receive high Shapley value because it is structurally necessary rather than because its content is intrinsically well-written. Dynamic-length workflows make the cooperative game itself less well defined.

The paper also reports that coalition size is not strongly predictive of total token cost. Therefore a low-value instruction block is not automatically a proportional token-cost saving opportunity. No direct length-neutral deletion/padding control was verified in this run; content value and prompt-length cost should remain distinct.

### Implication within tested scope

SkillShapley now has primary support as a fixed-version, within-skill counterfactual attribution mechanism. It still does **not** solve cross-version or cross-descendant causal credit: once one skill version creates another artifact or changes downstream routing, the fixed-player game no longer captures the lineage graph.

## SIG-MINDMEMOS-PAPER-CODE-PROTOCOL-GAP

Primary: Kaichao Liang et al., *MindMemOS: A Portable and Self-Evolving Memory Operating Layer for AI Agents*, arXiv:2608.12428, 12 Aug 2026.
Primary source: https://arxiv.org/abs/2608.12428
Public repository pinned for artifact inspection: `mindscale-noah/MindMemOS@c1befcb73646b54f7a96724ea5463edb21c03ee0`.

### Paper-reported SpreadsheetBench protocol and results

The full paper reports SpreadsheetBench-Verified with **400 tasks**: 275 cell-level and 125 sheet-level. Results are mean ± standard deviation over three runs:

- No-skill: **51.3 ± 0.8**, about **10.4M agent tokens**.
- Init-skill: **48.0 ± 1.4**, about **16.9M agent tokens**.
- MindSkillEvolve-Unsup.: **55.3 ± 0.9**, about **27.3M agent + 5.8M evolution tokens**.
- MindSkillEvolve-Sup.: **57.2 ± 2.4**, about **25.2M agent + 5.5M evolution tokens**.

The paper states that an evolution cycle is triggered every **40 executed tasks**, with trajectories grouped into **batches of eight tasks**. The unsupervised protocol uses execution traces; the supervised protocol additionally uses task scores. The evolved skill is synchronized for subsequent tasks.

These numbers preserve the previously reported gain over the initial-skill baseline, but they also expose a large compute difference. The evolved conditions consume substantially more total agent/evolution tokens than the no-skill or initial-skill controls. Without a matched-total-compute baseline, the entire score gain should not be causally assigned to persistence/evolution architecture alone.

### Public artifact reproducibility boundary

The current public CLI code exposes `--evolve` and `--evolve-every`, with `--evolve-every` defaulting to **1 task**. The current public evaluation guide likewise illustrates online SpreadsheetBench evolution with `--evolve-every 1` and explicitly says that the CLI can run No-skill, Init-skill, and a generic online-evolution path but **does not expose the complete Unsup./Sup. experimental protocols from the paper as separate reproducible switches**.

No searched public code/config path in this run surfaced the paper's exact `40 tasks per evolution cycle / batches of 8 trajectories / supervised-vs-unsupervised` experiment configuration. This is an artifact-level reproduction gap, not proof that the authors lack such a script privately or on another branch/commit.

The generic public runner previously inspected records trajectories, calls skill evolution, and stages any returned evolved version for subsequent tasks. No separate held-out behavioral A/B gate is visible on that generic path between minting and staging. The exact paper run may have additional orchestration not represented by the generic runner, so the correct conclusion is narrower: **the currently documented public path does not establish the exact admission/checkpoint-selection semantics of the published Table 4 experiment**.

### Implication within tested scope

MindMemOS remains evidence that trajectory-driven online skill evolution can improve SpreadsheetBench under the paper's reported protocol. It is weaker evidence for any specific safety/admission mechanism because the exact published orchestration is not directly reconstructible from the currently documented CLI, and it is weaker evidence for algorithmic efficiency because the evolved conditions use much more total compute.

## SEARCH-LONG-HORIZON-STAT-GATE-20260826

A fresh public-source search again failed to identify a real LLM-agent system that simultaneously demonstrates all of the following in one matched experiment:

1. more than 10 persistent self-improvement rounds;
2. repair/retirement or another explicit lifecycle for previously promoted artifacts;
3. reusable-holdout or anytime-valid/e-process acceptance;
4. proposal/round-global multiplicity or error spending; and
5. an untouched final task-level lockbox.

Partial matches remain split across systems: PACE/SEA provide anytime-valid or spending-style acceptance components; Ratchet-like systems provide very long lifecycle loops; other recent frameworks provide held-out organizer-only evaluation or persistent skills. No surfaced system closes the full conjunction. This is a negative search result, not a proof of nonexistence.

## Synthesis update

Three evaluation layers should now be kept distinct:

1. **Diagnostic feedback generation** — whether the system can expose new failure modes (SkillEvo's multi-turn simulation is direct evidence here).
2. **Promotion / admission** — whether a newly generated artifact should become persistent, including factual checks, behavioral replay, statistical acceptance, and rollback.
3. **Experimental reporting / model selection** — whether a reported gain survives dev-best selection, multiple candidates, compute matching, and an untouched outer test.

SkillEvo is a relatively strong four-round example because it has an untouched chronological outer evaluation split, but its plotted improvement is development-best selection and it does not address long-horizon multiplicity. SkillShapley provides fixed-skill step attribution but not lineage-level causal credit. MindMemOS provides a positive online-evolution benchmark result while leaving an exact public-protocol reproducibility gap and a substantial matched-compute confound.

A stricter evidence-aligned self-improvement evaluation stack is therefore:

`diagnostic probe generation`
-> `trajectory/failure attribution`
-> `bounded proposal`
-> `local/factual/behavioral gate`
-> `statistical admission with multiplicity accounting`
-> `versioned promotion`
-> `cross-version provenance and reuse monitoring`
-> `repair/retirement/rollback`
-> `matched-compute control`
-> `untouched outer evaluation`.

## Nonempty frontier / exact continuation

1. Find official SkillEvo code or an independent reproduction; verify whether the fact-consistency inspector only sees frozen factual anchors and whether held-out evaluation identities/solutions can leak indirectly through prompts, tools, caches, or simulation infrastructure.
2. Find SkillShapley code/artifacts; test or recover whether step rankings remain stable under task-resampled and model-resampled evaluation, and search explicitly for a length-neutral deletion/padding control that separates content utility from context-length cost.
3. Locate the exact MindMemOS paper experiment script/commit/config for the **40-task evolution cycle, eight-trajectory batches, and Sup./Unsup. modes**. Determine whether multiple candidate versions, hidden validation, checkpoint selection, or rollback occurred. If no public artifact exists, preserve this as a reproducibility gap rather than inferring semantics from the generic CLI.
4. Continue the exact missing-system search for a **>10-round real LLM-agent persistent loop + lifecycle repair/retirement + reusable-holdout/e-process acceptance + global proposal/round spending + untouched final lockbox**. Prioritize post-SEA/PACE citations and systems that report explicit proposal counts.
5. Extend attribution from fixed-step Shapley to **cross-version/cross-descendant provenance-aware utility**: search for systems that retain causal dependency edges between promoted artifacts and can estimate downstream marginal contribution by selective replay rather than only an LLM judge.
6. Add a **matched-total-compute control** to the evidence checklist for self-evolution papers. When the evolved condition uses materially more inference/evolution tokens or candidate evaluations, search for equal-budget resampling/search baselines before attributing the gain to persistent adaptation itself.
