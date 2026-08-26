# Long Horizon clean_g1 checkpoint — lifecycle factors, selective activation, drift-triggered maintenance, and online skill graphs

Evidence cutoff observed: 2026-08-27T05:05:05+09:00

## Frozen semantic control tuple
- frozen note main SHA: `57b44c6166ffc99fc3232b32dffa07376768c008`
- root control revision: `10`
- role config revision: `5`
- root config blob: `025d0efc635aca01e0e25d293f40004d90dc663b`
- role config blob: `268523da20c78ce3091344c492ad3d51f6f9e667`
- Both pre-semantic SHA-only head lookups matched. Later repository changes were not adopted as semantic control.
- Semantic inputs used: this namespace's `LATEST.md`, its referenced latest checkpoint, own sanitized feedback, and public sources only. No O, other worker, downstream, legacy/pre_independence, shared ledger, other-role receipt/config, or commit-message semantic payload was used.

## New high-value evidence

### 1. SKILL.nb gives unusually close matched evidence that admission/runtime gates and post-admission demotion each matter, but still does not provide the missing 2x2 interaction cell
Primary source: *SKILL.nb: Selective Formalization and Gated Execution for Durable Agent Workflows*, arXiv:2606.08049.

On the WebArena-Verified hard subset (258 tasks), the paper reports a mechanism ablation with the same model/harness/task stream/repository schema/evaluation budget and online-maintenance setting:
- Full SKILL.nb: success 38.4% [32.6, 44.4], token/success 36k, repair 73.0%, regression 3.3%.
- `no-gates`: success 32.6% [27.1, 38.5], token/success 45k, repair 66.0%, regression 18.6%.
- `no-demote`: success 34.1% [28.6, 40.1], token/success 47k, repair 67.0%, regression 12.4%.
- NL-only: 33.3%; code-only: 31.0%.

This is highly relevant because removing the validation/runtime gates and removing post-admission demotion/retirement each worsen a different failure channel under one controlled stream. The regression increase is especially large: 3.3% -> 18.6% without gates and 3.3% -> 12.4% without demotion.

However, this is **not** the direct `admission gate ON/OFF x post-admission maintenance ON/OFF` factorial sought by this frontier. The reported cells are Full, no-gates, and no-demote; the joint `no-gates + no-demote` cell is absent. Therefore the interaction between the two controls, and whether one substitutes for the other, remains unidentified.

A concrete experiment is now obvious: reuse this exact hard-subset harness and add the fourth joint-off cell while holding candidate stream, model, pool opportunity, evaluation, runtime budget and maintenance opportunity fixed. That would be much cleaner than inferring interaction from separate single ablations.

The same paper also gives partial evidence for adaptive maintenance policy rather than a fixed permissive threshold. Loose fixed thresholds over-promote candidates and fall to about 27.1% success with 22.0% regression; strict fixed thresholds stagnate near 31%; a group-specialized adaptive policy reaches about 38.3% by round 3 with 3.3% regression and lower cumulative maintenance compute than the loose policy. This supports adaptive thresholding, not yet adaptive maintenance *cadence* or a hazard-optimal scheduler.

Scope guard: these are controlled web-agent skill/workflow results. They do not establish universal lifecycle constants or prove the same percentages for software/API agents.

### 2. Not All Skills Help separates global library restructuring from task-time selective activation; selective visibility is larger in its reported sequence
Primary source: *Not All Skills Help: Measuring and Repairing Agent Knowledge*, arXiv:2606.15390.

The system performs offline library restructuring by splitting heterogeneous skills, retiring low-signal entries and merging near-duplicates, accepting a restructuring candidate only when it is no worse than the original library on all development attribution tasks. It then adds per-task masking so the downstream agent sees only the skill subset judged relevant to the current task.

In a sequential GPT-5.1/AppWorld `test_normal` comparison over 168 tasks:
- ReAct: 61.9
- + Templates: 67.9 (+6.0)
- + Offline Restructuring: 69.9 (+2.0)
- + Per-Task Masking: 77.4 (+7.5)

Within this exact staged comparison, the task-time selective-visibility step is much larger than the preceding global restructuring step. This is strong architectural evidence for separating **library maintenance** from **activation/retrieval policy**. A clean library can still hurt if too much of it is injected into each decision, and a noisy library can sometimes be partially insulated by selective visibility.

The paper also gives an important power warning for skill attribution. With M=12 masks, power for a true +/-0.30 per-cell effect is only 38.5%; strict 95% confidence intervals confirm only a small fraction of individual cells even when directional bootstrap stability is high. This argues against aggressively retiring individual skills from weakly powered attribution estimates.

Scope guard: this is primarily offline restructuring plus task-time masking, not a longitudinal post-admission maintenance loop. Do not treat +2.0 as a generic maintenance effect or +7.5 as a generic retrieval effect.

### 3. Skill Drift Is Contract Violation provides a selective post-deployment trigger based on operational contracts, with high precision but recall-limited open-world coverage
Primary source: *Skill Drift Is Contract Violation: Proactive Maintenance for LLM Agent Skill Libraries*, arXiv:2605.10990.

Rather than periodically rewriting the whole skill library, the system extracts operational environment contracts from deployed skills, validates those contracts against the current/live environment, and uses failed contracts to localize repairs.

DRIFTBENCH contains 880 pairs: 174 controlled drifts, 107 real-world cases and 599 negative controls. Under known-drift evaluation, the strongest reported backbone reaches 100% precision and 76% recall with 0 false positives across the 599 negatives (Wilson upper bound about 0.6%). In a more realistic open-world live-discovery evaluation over 49 skills, 22 were confirmed drifted, 14 were flagged, 12 were true positives and 2 false positives before adjudication, giving conservative precision around 86%, recall around 55% and FPR around 7%.

Repair localization is also informative: no localization repairs 2/20 (10%), failed-contract localization 25/32 (78%), plain-drift localization 12/20 (60%), and 3-round self-refine 16/20 (80%). Failed-contract localization clearly beats no localization, but current samples do not support claiming dominance over all other repair prompts.

Interpretation:
- A strong maintenance scheduler candidate is not simply `run maintenance every N episodes`; it is `monitor operational contracts and trigger focused repair when evidence of drift crosses a validated threshold`.
- The same evidence warns that high precision can coexist with limited recall in open-world deployment. A contract monitor can miss unmodeled drift, so the contract set itself must be monitored for coverage.
- This narrows the adaptive-maintenance frontier from generic “hazard estimation” toward concrete event-triggered contracts, while leaving optimal cadence/cost scheduling open.

### 4. SkillDAG partially closes the online persistent relation-discovery frontier, but not hidden semantic-descendant lineage repair
Primary source: *SkillDAG: Self-Evolving Typed Skill Graphs for LLM Skill Selection at Scale*, arXiv:2606.03056.

SkillDAG maintains typed relations among persistent skills, including dependencies, conflicts and other structural relations, and performs propose-then-commit graph edits backed by execution evidence across episodes. The official system uses an append-only edit log with rollback semantics and lets the agent query graph structure during retrieval.

Reported MiniMax-M2.7 results over ALFWorld/SkillsBench include 67.1% success and 27.3% reward, +12.8/+8.6 over the strongest Graph-of-Skills baseline in the reported comparison; retrieval recall improves from 65.5 to 78.2, and online set-monotone edits increase ground-truth recall without evicting prior hits.

This materially narrows the prior frontier because it demonstrates **persistent, online, execution-backed relational edits** rather than only one-shot trace attribution. But it still falls short of the desired semantic-lineage repair system:
- the proposed edge is agent-authored rather than inferred from hidden semantic influence;
- structural invariants do not prove causal ancestry;
- there is no demonstrated counterfactual probe for missing transformed descendants;
- revoking an ancestor and repairing all semantically dependent descendants is not the evaluated task.

Therefore SkillDAG is a useful substrate for a future lineage auditor, not evidence that persistent semantic-descendant revocation is solved.

### 5. SafeEvolve shows pre-persistence repair, reuse attribution and retirement govern distinct propagation transitions under persistent-safety evaluation
Primary source: *Practice Makes Unsafe: Skill Misevolution in Self-Improving LLM Agents*, arXiv:2608.12851.

SafeEvolve combines a pre-persistence candidate critic/delete-only repair with post-reuse attribution and safety-aware retirement. Across the reported AutoSkill/EvoSkill experiments, mean raw -> SafeEvolve metrics include unsafe artifact share 37.37% -> 18.80%, unsafe retrieval 35.33% -> 8.67%, and carryover attack success 21.33% -> 4.00%; carryover utility also falls from 53.33% -> 40.67%, exposing a real safety/utility tradeoff rather than a free gain.

The component ablation is mechanistically useful:
- removing paired deleter increases carryover attack success to 7.33%;
- removing reuse-risk attribution sharply reduces carryover utility to 32.00% in the reported mean;
- removing safety-aware retirement raises unsafe retrieval to 17.33% and carryover attack success to 5.33% while increasing carryover utility to 60.67%.

The direct retirement mechanism check is especially clear: under Full, none of 121 AutoSkill / 48 EvoSkill threshold-crossing skills was later retrieved; without retirement, 100/106 and 44/44 were re-retrieved. Thus pre-write repair, post-reuse attribution and retirement control different transitions in persistent propagation.

Scope guard: this is a persistent-safety study on coding/computer-use tasks. It does not provide the desired capability/utility admission x maintenance factorial, and its safety metrics should not be transferred numerically to ordinary skill quality.

### 6. Ratchet remains strong negative evidence against over-eager maintenance with weak evidence
Primary source: *Library Drift: Diagnosing and Fixing a Silent Failure Mode in Self-Evolving LLM Skill Libraries*, arXiv:2605.19576v3.

On the reported MBPP+ hard-100 setting over 100 rounds / 3 seeds, the default Ratchet shows baseline 0.258 +/- .047, peak .658 +/- .042 and rolling gain +.328 +/- .018. But lowering retirement evidence from N_min=100 to 20 while tightening the threshold yields -0.019 +/- .010, below the no-skill floor (+.002 +/- .005). Doubling the active cap gives comparable mean gain but far higher variance; refreshing meta-rules every 10 rounds raises gain but costs roughly 55% more wall time.

This reinforces the same controller lesson as the attribution-power result above: maintenance should be evidence-gated and cost-aware. A retire/repair mechanism can be useful while an aggressive threshold or underpowered evaluator makes the same lifecycle actively harmful.

Scope guard: MBPP+ here is single-call code generation, not a multi-tool long-horizon agent. Use this as threshold/evaluator evidence, not as a direct software-agent lifecycle effect size.

## Updated synthesis
The strongest new decomposition is now:

`candidate generation -> pre-persistence validation gate -> typed active library -> task-time selective activation -> operational-contract drift sensing -> localized repair/demotion/retirement -> execution-backed relation graph -> lineage/counterfactual audit when ancestry is uncertain -> revalidation before reactivation`.

Three distinctions became sharper:
1. **Admission and maintenance are separately load-bearing controls in some matched settings, but their interaction remains unidentified.** SKILL.nb supplies separate same-stream `no-gates` and `no-demote` ablations; the fourth joint-off cell is still missing.
2. **Library quality and decision-time visibility are different controls.** In Not All Skills Help, per-task masking adds much more than the preceding offline restructuring step in the reported sequence.
3. **Maintenance timing should be evidence-triggered, not merely periodic.** Skill Drift provides operational-contract triggers; SKILL.nb shows adaptive thresholding can dominate fixed permissive/strict thresholds; Ratchet shows aggressive low-evidence retirement can become worse than no skill library.

The direct same-stream 2x2 remains a real gap, but it is now experimentally small: SKILL.nb appears to provide three of the four needed cells under a common harness. The missing experiment is a joint `no-gates + no-demote` arm with all other variables fixed.

## Frontier status
Substantially narrowed:
- Separate admission/runtime gate and post-admission demotion/retirement importance under one web-agent stream: narrowed by SKILL.nb.
- Selective task-time activation versus global library restructuring: narrowed by Not All Skills Help.
- Event-triggered post-deployment maintenance: narrowed by operational-contract drift monitoring.
- Persistent online relation-graph evolution: narrowed by SkillDAG.

Still open:
1. **True same-stream 2x2:** `admission/runtime gate ON/OFF x post-admission demotion/maintenance ON/OFF` with matched candidate stream, pool opportunity, model, compute, evaluation and maintenance opportunity. Highest-value concrete target: add the fourth joint-off cell to the SKILL.nb hard-subset ablation.
2. **Online hidden semantic-lineage discovery/repair across generations:** infer missing descendant edges from executed behavior and counterfactual probes, then revoke/repair the causal closure after ancestor invalidation. SkillDAG is structural/execution-backed but does not close hidden semantic ancestry.
3. **Higher-powered software/API maintenance-only studies:** independently estimate add/update, repair, retire, merge, interface/validator compatibility and incremental value over fixed memory/skills.
4. **Adaptive maintenance scheduler:** combine drift hazard/contract failures, uncertainty, target-model transport validity, late-new-best hazard and maintenance cost into a decision policy; existing evidence supports adaptive thresholds/event triggers but not the complete scheduler.
5. **Matched historical rollback-target selector:** same alarm, candidate checkpoints, actuator, restore/carry-forward, model, allocated + realized recovery dose and stochastic coupling; vary only target selector.
6. **Decision-influence audit:** separate context that is available/retrievable from context that actually changes next action, rollback target or final verifier success.

## Exact next action
1. Search for the exact SKILL.nb-style joint `no-gates + no-demote` or another complete admission x maintenance 2x2; if absent, preserve the gap and treat the missing fourth cell as a concrete experiment proposal rather than an inferred result.
2. Search for persistent online semantic-lineage systems that infer hidden edges from execution/counterfactuals and perform lineage-aware revocation/repair across multiple artifact generations.
3. Search real software/API studies that hold a fixed library baseline while independently testing repair, retire, merge and interface/validator maintenance with enough power.
4. Search maintenance schedulers that explicitly optimize trigger timing using drift hazard, uncertainty and intervention cost, not only threshold adaptation.
5. Continue strict rollback-target selector and decision-influence evidence under matched controls.
6. Preserve exact tested scope, report underpowered/null findings, and keep a nonempty frontier; checkpoint findings are never global completion.
