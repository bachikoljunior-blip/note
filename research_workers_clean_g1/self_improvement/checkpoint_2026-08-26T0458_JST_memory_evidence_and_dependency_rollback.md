# CLEAN self-improvement checkpoint — episodic evidence preservation and dependency-guided rollback

Run start: 2026-08-26 04:58 JST
Role: self_improvement / clean_g1
Frozen control snapshot: note main `df7718d792bb34632bbf97957383f4e539989bf2`; `automation_control/DESIRED_STATE.json` control_revision=7 blob `ae605e09eb3bcdc7aa18238d2c42218b0272d2e6`; own role config_revision=4 blob `538af4de09acd8a6ad70e66a2b550e7b92be7254`.
Continuation source: own `LATEST.json` -> `checkpoint_2026-08-26T0401_JST_scicd_severa.md`; public sources; own sanitized feedback only. No O/O-derived, other-worker, downstream comparator/integrator/index/feed/audit, legacy/pre_independence, shared-ledger, or other-role semantic state was read.
Feedback: own ID-stability feedback was already acknowledged; new IDs remain source-qualified.

## SIG-FAULTY-MEMORY-EPISODIC-GATE

Primary: Dylan Zhang, Yanshan Lin, Zhengkun Wu, Yihang Sun, Bingxuan Li, Dianqi Li, Hao Peng, *Useful Memories Become Faulty When Continuously Updated by LLMs*, arXiv:2605.12978, 13 May 2026.
Primary PDF: https://arxiv.org/pdf/2605.12978
Official project page: https://dylanzsz.github.io/faulty-memory/

### Main mechanism/evidence

The paper directly challenges the common self-improvement pattern `successful trajectory -> textual abstraction -> repeatedly rewrite the abstraction store`. The key controlled distinction is between preserving raw episodic evidence and repeatedly consolidating it into rewritten textual lessons.

On a 19-problem ARC-AGI slice that GPT-5.4 solves at 100% with no memory, all consolidation inputs are ground-truth solutions. Static consolidation of the full pool remains at 94.7% after both 10 and 50 refresh rounds, while streaming one-problem-at-a-time consolidation falls to 73.7% after the first pass and **52.6% by round 10**. The input experience is therefore useful by construction; the observed degradation occurs after repeated memory construction/maintenance under this tested stream schedule.

In the ARC-AGI Stream mitigation experiment, the agent can Retain, Delete, or Consolidate. Across 400 steps, policies that can preserve raw episodes outperform or match forced abstraction. The paper's component ablation reports that `Episodic Management Only` (retain/delete raw episodes; abstraction disabled) matches or exceeds the full Auto regime, while `Abstract Only` remains at or below the zero-shot baseline. At 200 steps, the plotted success values are approximately Auto+Episodic 62%, Auto(Episodic) 56%, Abstract Only 32%, Episodic Management Only 68%; at 400 steps approximately 54%, 48%, 38%, and 54%, respectively. These are figure values rather than a tabulated confidence-interval result and should not be over-precised.

The same paper reports a 15-task ScienceWorld task-switch sequence where cumulative consolidation finishes **203 cumulative-score points behind** a fresh-per-task abstraction control. The authors' memory-content diagnostic labels cumulative memory as accumulating over-generalized and garbage entries much faster than Fresh; this diagnostic uses an LLM judge and is mechanistic evidence, not a formal proof of causal labels.

### Self-improvement implication within tested scope

A persistent self-improvement system should treat raw trajectories / source evidence as a first-class, versioned substrate rather than overwrite them with each abstraction. `Consolidate` should be an explicit proposal with a gate and reversible lineage, not an automatic post-task action. An abstract skill should retain a provenance edge back to the episodes it summarizes so that later retirement/repair can be checked against evidence rather than against the current abstraction alone.

This source does **not** show that abstraction is useless in general; the paper explicitly notes that episodic accumulation is unbounded and compositional transfer ultimately needs abstraction. The narrower tested conclusion is that forced high-frequency rewriting is fragile for the evaluated models/tasks, and retaining/deleting episodes is a stronger default than mandatory consolidation in those settings.

## SIG-DGRR-DEPENDENCY-ROLLBACK

Primary: Caili Yu, Yiqi Wang, Jiaqi Zhang, Yiqun Duan, Mingkai Zheng, Zhangkai Wu, Kaize Shi, Taotao Cai, *From Faulty Memories to Corrected Actions: Dependency-Guided Rollback Repair for Memory-Augmented Agents*, arXiv:2608.10502, 11 Aug 2026.
Primary PDF: https://arxiv.org/pdf/2608.10502

### Mechanism

Given an upstream diagnosis of faulty persistent memories, Dependency-Guided Rollback Repair builds a typed graph spanning memory reads/writes, claims, plans, tool actions/observations, and answers. It traces downstream dependencies from the diagnosed fault, checks whether reachable nodes have independent trusted support, applies a deterministic rollback plan, and selectively replays only answer-relevant affected computation.

This is complementary to Keep/Rewrite/Remove skill curation: deleting the bad source artifact alone can leave copied claims, derived memories, tool plans, or later writes active. The mechanism adds a **descendant repair contract**: provenance-aware invalidation plus selective recomputation.

### Matched results and ablations

Controlled benchmark: 150 cases across shopping, travel, and customer-support tool use with four memory-failure types.

- Full method recovery **85.3%** versus LLM-judge repair **77.3%** and AgentTrace-style **60.7%**.
- Full method faulty-memory removal **100%**, benign-memory preservation **100%**, replay ratio **12.3%**, average LLM calls **5.70**.
- Removing the rollback planner lowers recovery **85.3 -> 71.3%**, raises recurrence **26.6 -> 43.0%**, replay ratio **12.3 -> 15.2%**, and LLM calls **5.70 -> 9.19**.
- Removing independent-support checking slightly raises raw recovery **85.3 -> 88.0%** but lowers benign preservation **100.0 -> 98.6%**, raises replay ratio **12.3 -> 15.4%**, and LLM calls **5.70 -> 6.51**. This shows a real recovery/selectivity tradeoff rather than a universally positive component.
- Removing selective replay leaves recovery close (**84.0%**) but raises replay ratio to **75.5%** and LLM calls to **24.01**, so the main contribution of selective replay in this ablation is cost containment, not higher recovery.

Transfer stress test: 50 procedural trajectories adapted from LongMemEval-V2. Full DGRR reaches **68.0%** recovery versus the next-best **54.0%**, with claim-invalidation F1 **0.669** versus **0.603** for AgentTrace-style. In this transfer table, DGRR does not have the absolute lowest recurrence, so it should be described as a recovery/cleanup/cost tradeoff rather than uniformly superior on every metric.

### Scope / boundary

Diagnosis is assumed and outside the paper's scope. The runtime must already capture provenance. Rollback concerns agent-maintained memory/trace state and cannot undo irreversible external side effects unless the domain offers a compensating action or resettable tool. These requirements are material constraints for any self-improvement adaptation.

### Self-improvement implication within tested scope

Persistent improvement artifacts should carry machine-readable dependency/provenance edges into downstream artifacts and decisions. A later regression should support `source diagnosis -> descendant slice -> independent-support test -> invalidate/quarantine -> selective replay`, rather than merely removing the original skill/memory. This makes rollback semantics closer to transactional state repair than to textual deletion.

## Synthesis update

The lifecycle frontier now separates two failure times that earlier Keep/Rewrite/Remove schemes can blur:

1. **before/at consolidation:** preserve source episodes; gate compression/abstraction instead of rewriting automatically;
2. **after a faulty artifact has already propagated:** repair descendants using provenance and selective replay rather than deleting only the source.

A stronger persistent self-improvement substrate therefore looks like:

`immutable/source-qualified episodes`
-> `optional bounded abstraction proposal`
-> `independent acceptance / versioned promotion`
-> `explicit dependency edges from abstraction to evidence and downstream uses`
-> `runtime outcome monitoring`
-> on regression: `fault diagnosis -> dependency slice -> support check -> selective rollback/replay`
-> `fresh outer evaluation`.

This does not fill the prior statistical frontier: neither paper combines this lifecycle with reusable-holdout/e-process/global spending across >10 rounds of a real self-modifying LLM agent.

## Negative / not promoted in this run

- SkeMex (arXiv:2606.09365) has a promising Read-Write-Assess-Govern lifecycle with context-dependent utility, promotion, merge, and removal. Publicly indexed material confirms the architecture and broad performance claims, but this run did not obtain a sufficiently inspectable primary full-text table/ablation establishing the causal effect of its governance/removal component. It remains a follow-up, not a quantified candidate here.
- A-Evolve public guidance describes up to 20 evolution cycles, git versioning, holdout splits, and skill/memory CRUD, but the surfaced material is framework documentation rather than a primary matched experiment combining long-run lifecycle governance with anytime-valid/global statistical gates. It does not close the key frontier.

## Nonempty frontier / exact continuation

1. Continue the exact missing-system search: a **real >10-round LLM agent** combining persistent lifecycle repair/retirement, untouched or reusable holdout control, anytime-valid acceptance/global spending, and a final lockbox.
2. Search for **provenance/dependency-aware utility attribution** for ordinary beneficial/harmful skills (not only fault recovery): can a skill's downstream contribution be traced deterministically enough to reduce LLM-judge reliance?
3. Find a primary inspectable SkeMex artifact/revision and extract matched ablations for value-aware retrieval, Assess, Govern/remove, online stream length, repository growth, and transfer; do not rely on secondary overview values.
4. Search for experiments that compare **immutable episodic evidence + derived abstractions** against rewrite-only memory under equal retrieval/context/token budgets, because raw-episode advantages can otherwise be confounded by information volume.
5. Search hierarchical multiplicity control spanning both `many candidate edits within a round` and `many accepted checkpoints across rounds`; require an untouched final audit after the adaptive loop.
