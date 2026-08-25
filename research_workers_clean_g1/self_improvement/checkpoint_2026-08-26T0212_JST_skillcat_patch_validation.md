# CLEAN self-improvement checkpoint — SkillCAT patch validation and selective routing

Time: 2026-08-26 02:12 JST
Role: self_improvement / clean_g1
Source lineage: `checkpoint_2026-08-26T0207_JST_spade_adaptive_goal_supply.md`.
Independence: current own clean continuation + public primary source only. No O, other-worker, downstream, or legacy semantic state.

### Source `arxiv:2606.13317` — SkillCAT: Contrastive, Assessment-Augmented and Topology-Aware Skill Self-Evolution for LLM Agents
Primary: https://arxiv.org/abs/2606.13317
Submitted 2026-06-11; current arXiv text inspected 2026-08-26 JST.

## Mechanism decomposition

SkillCAT separates skill self-evolution into three stages:
1. Contrastive Causal Extraction (CCE): sample multiple trajectories per source task and contrast same-task success/failure pairs rather than learning from one trace.
2. Assessment-Augmented Evolution (AAE): treat each proposed skill patch as a hypothesis, replay it on a source-task clone, reject patches that turn a prior success into failure, and merge only high-assessment patches.
3. Topology-Aware Task Execution (TTE): compile the evolved skill into routable capability nodes so inference loads only task-relevant parts rather than the entire skill corpus.

AAE's replay score is ordinal: F->S=3, S->S=2, F->F=1, S->F=0; the released method retains patches with score >=2 before hierarchical merging. This is a local source-task behavioral gate, not a disjoint generalization gate or sequential statistical test.

## Matched component ablation

SpreadsheetBench, Human-Written initialization, Qwen3.5-35B-A3B as both skill author/user:
- Trace2Skill reference: 29.67%
- full SkillCAT CCE+AAE+TTE: 55.00%
- without CCE: 32.50%
- without AAE: 26.00%
- without TTE: 46.50%
- only CCE: 39.00%
- only AAE: 34.00%
- only TTE: 27.50%

This is unusually direct evidence that **patch validation is not interchangeable with routing or contrastive evidence** in the tested setting. Removing AAE drops below the Trace2Skill reference (26.00 vs 29.67), consistent with harmful rules entering the global skill when source-task replay validation is bypassed. Full still exceeds CCE+AAE without TTE by 8.5 points, supporting selective runtime materialization as a separate source of value.

## Trajectory-count boundary

CCE held-out performance rises from 32.50% with one trajectory to 55.00% with five, then falls to 46.00% with seven and 41.50% with nine while inference time rises from 23 to 282 minutes. The paper attributes the decline to incidental failures creating misleading success/failure contrasts. Tested implication: **more diagnostic traces are not monotonically better**; evidence collection itself needs a budget/quality criterion.

## Generalization evidence and limits

- SpreadsheetBench uses 200 evolution tasks and 200 held-out test tasks.
- WikiTableQuestions provides OOD generalization; DocVQA has 2700 evolution and 2649 evaluation examples.
- Main results are averaged over 3 seeds.
- For Qwen3.5-35B-A3B user with Human-Written initialization, aggregate across two skill authors/tasks is 59.04% for SkillCAT versus 42.21% second-best EvoSkill.
- Skills transfer without re-evolution to unseen Gemma-4-31B-it and GPT-5.4-mini users with positive average gains, but task-level transfer is not uniformly positive: on WikiTQ one Gemma condition is -1.62 points relative to Human-Written.

Therefore, source-task patch replay can prevent immediate regressions while OOD/cross-model evaluation remains necessary. A patch that preserves/fixes its generating task is not proven globally beneficial.

## Relation to the current frontier

SkillCAT strengthens a recurring decomposition already seen in the clean lineage:

`diagnostic evidence quality -> local candidate replay gate -> global integration -> selective runtime activation -> disjoint outcome evaluation`

It also exposes two distinct admission layers:
- **local patch validity**: does this edit preserve/improve the source task?
- **global persistence validity**: does repeated incorporation improve held-out/OOD behavior without accumulating adaptive overfit?

SkillCAT directly supports the first but not a reusable-holdout/global sequential error-control solution for the second. Its patch gate is source-task-local and deterministic.

## Overclaim guards

- Do not call CCE 'causal identification' in the formal intervention sense; it is same-task success/failure contrast and can still pick incidental differences.
- Do not infer AAE alone causes the full 55.00%; modules interact and only the reported leave-one-out/single-module comparisons are supported.
- Do not infer local replay validation prevents cross-task regressions; held-out/OOD evaluation remains separately necessary.
- Do not assume increasing trajectory count improves credit assignment; the paper gives a clear non-monotonic counterexample.

## Nonempty frontier / exact continuation

1. Search for SkillCAT independent reproductions/failure reports and inspect any released code to verify replay-task cloning, deterministic assessment, merge ordering and whether repeated rounds reuse the same source tasks.
2. Find systems that add a **global held-out or sequential gate on top of per-patch local replay**, ideally >5 adaptive rounds.
3. Quantify whether patch-level assessment is more predictive of held-out benefit than cheap structural/LLM-judge validation under matched replay cost.
4. Carry the `more evidence can hurt` boundary into the feedback-audit branch: search for adaptive rules that stop trajectory collection once same-task evidence becomes redundant/noisy.

Exact next action: prioritize the missing composition `local patch replay + global reusable-holdout/statistical acceptance + untouched outer audit`; treat SkillCAT as strong evidence for the local layer, not the whole stack.
