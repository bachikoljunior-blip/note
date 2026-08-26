# Long Horizon clean_g1 — value-weighted maintenance control

Checkpointed: 2026-08-27T08:02:43+09:00

## Frozen semantic control tuple
- note main SHA: `64b03acca1c5d9290975fe82a252d4f0ab2aa235`
- root control revision: `11`
- role config revision: `5`
- root blob: `bf7b8c7f6971c0ec2f3fa7a8d53dca1f88ac50a3`
- role config blob: `268523da20c78ce3091344c492ad3d51f6f9e667`
- Both pre-semantic SHA-only ref lookups matched. This tuple remained frozen after the first role-local semantic read.

## Clean-boundary declaration
Semantic inputs in this invocation were limited to this worker's own `LATEST.md`, own sanitized feedback, the sanitized root manifest, own role-local config, and public sources. No O/O-derived state, other worker state, downstream comparator/integrator/index/feed/audit state, legacy/pre_independence research, shared `EXECUTION_LEDGER.json`, other-role receipts, or other-role configs were read or used semantically.

## New evidence delta

### 1. Drift hazard and current downstream value are distinct maintenance signals
`Skill Drift Is Contract Violation` (arXiv:2605.10990, May 2026) provides a precision-first trigger for operationally meaningful drift: role-bearing contracts rather than arbitrary changed values. Contract-free probes produce 40% false positives; the reported strongest configuration has 0 false alarms across 599 no-drift/hard-negative cases, 100% precision / 76% recall on known drift, and 86% conservative precision in a 49-real-skill study. Localization raises one-round repair success from 10% to 78%. However, open-world recall is incomplete, so this cannot serve as a complete maintenance scheduler by itself.

Public source: https://arxiv.org/abs/2605.10990

`SkillsBench 1.1` supplies the complementary value-at-risk signal. Across 87 tasks, curated skills improve aggregate results but 13/87 tasks have negative Skill Lift. Benefit also depends on skill count and detail level, so a skill being present, valid, or frequently invoked is not evidence that it currently adds marginal outcome value.

Public source: https://www.thebenchmark.company/blogs/skillsbench-1-1

NVIDIA's `SkillEvaluator` makes this marginal-value measurement operational: Tier 3 executes matched with-skill and without-skill arms under the same prompt/model/task/grading in isolated sandboxes. In the Aug. 12 catalog snapshot covering >300 verified skills across >30 products, macro average lift was +41 correctness, +40 discoverability, +39 effectiveness, +35 efficiency, +1 security. The blog also reports large per-skill cost heterogeneity and warns that 85% of published skills had only one attempt, with no catalog-wide confidence intervals. The documentation explicitly treats small lift as noisy and recommends more attempts before concluding.

Public sources:
- https://developer.nvidia.com/blog/evaluating-ai-agent-skill-performance-with-nvidia-skillevaluator/
- https://docs.nvidia.com/skills/skillevaluator
- https://docs.nvidia.com/skills/skillevaluator/reports

### 2. Explicit skill maintenance is not automatically worth its cost
`ContinualSkillBench` (arXiv:2608.03874, Aug. 4 2026) directly separates retained context/feedback from explicit skill maintenance. Across the three GPT-5.3-Codex domains in its ablation, pure in-context learning averages 0.605 normalized reward versus 0.602 for skill-maintaining sequential execution. Skills still help selectively on exact-match/programmatic tasks, but they do not provide a consistent aggregate advantage. The same paper finds weaker models can accumulate larger, less reused, lower-quality skill pools (GPT-4o 384 skills versus GPT-5.3-Codex 205 across five domains). This is negative evidence against a policy of maintaining every stored skill merely because it exists.

Public source: https://arxiv.org/abs/2608.03874

### 3. Affected-set replay can bound blast radius, but it is not yet a cost-optimal scheduler
`Learning Globally Reusable Skills for Coding Agents` (GSE, arXiv:2608.06153, Aug. 6 2026) maintains a Skill Relation Graph, propagates related updates, consolidates local changes, and replay-verifies relevant historical cases where modified skills were previously used before integration. It reports gains on two software-engineering tasks and an internal agent. This supports an affected-set/relevant-history replay pattern rather than replaying the entire library after every change. The current public paper does not establish an optimal maintenance trigger or end-to-end cost-aware scheduling rule, and original-author public code was not verified in this run.

Public source: https://arxiv.org/abs/2608.06153

### 4. Release governance needs a separate candidate lifecycle and explicit resource/tail-risk gate
`OpenLoopEvolve` (OLE, arXiv:2608.09380, Aug. 10 2026) externalizes observation/planning/memory/action/verification/recovery/stopping/budget rules as versioned Loop Policy assets. Candidate generation is separated from release. Champion and Challenger are paired under shared conditions; release eligibility is the conjunction of benefit, evidence quality, tail risk, and resource-cost constraints. Online updates activate only at a subsequent task boundary; later feedback can trigger rollback to the parent version, and triggering traces are quarantined from the current update batch.

On YC-Bench with deepseek-v4-flash, medium config, seeds 1/2/3, and 20-turn context, Fixed initial policy has 73.89% task success, OLE-online 87.87%, and OLE-offline 91.80%. Mean final funds are 365,976.30 / 878,601.79 / 974,627.52 respectively, and annual survival improves from 1/3 to 2/3 and 3/3. But evolution is expensive: OLE-online uses 34.70M main-task tokens plus 29.82M evolution-validation tokens (64.52M observable total), and OLE-offline 35.61M + 24.02M (59.63M). Online mode makes 12 candidate-update attempts. The paper explicitly says the update trigger may depend on feedback amount, update period, or task stage; the trigger only starts evolution and does not replace the release gate. Therefore OLE supports governed release/monitor/rollback, but does not validate a cost-optimal value-weighted skill-maintenance trigger.

Primary public source: https://arxiv.org/html/2608.09380v1
Official code link reported in the primary paper: https://github.com/yoyoshikc/OpenLoopEvolve

### 5. The previous Repo2Skill-Evo conclusion is strengthened but its public artifact status remains unresolved
`Repo2Skill-Evo` (arXiv:2608.21964, Aug. 22 2026) remains the strongest direct evidence that release-conditioned staleness is silent and difficult: 57 repositories, 105 release transitions, 1,158 skills; every selected transition invalidates part of V1 skill content; six frontier agents achieve only 29.9%–69.7% avg@3 macro F1 under a patch-grounded metric balancing stale recall against over-editing precision. Exact-title public searches in this invocation did not locate a verified original-author code/data repository. Do not infer that code is unavailable permanently; current artifact availability is `unverified/not found in this run`.

Public source: https://arxiv.org/abs/2608.21964

## Synthesis — hypothesis, not an observed end-to-end result
The evidence now supports separating maintenance control into at least four independent quantities:

1. **Drift hazard / invalidation evidence** — has an operational contract, release, API, dependency, schema, or configuration changed? (`SkillGuard`, `Repo2Skill-Evo`).
2. **Current marginal value at risk** — does the skill still improve the target model/harness/task distribution compared with an otherwise matched no-skill arm? (`SkillsBench`, NVIDIA `SkillEvaluator`, and the negative `ContinualSkillBench` result).
3. **Blast radius / replay set** — which related skills/tasks are actually structurally or behaviorally affected and need replay, rather than replaying everything? (GSE's relation graph and relevant-history replay).
4. **Intervention cost and release risk** — how much compute/time does maintenance consume, what is the false-edit/tail-risk exposure, and does the candidate beat the current version under paired conditions before task-boundary activation? (`SkillProx`/OLE-style gating and rollback).

A candidate priority rule such as `expected invalidation probability × current marginal skill lift × failure consequence / (maintenance compute + false-edit risk)` is therefore a plausible scheduler hypothesis. It is **not** directly validated by any one study found so far. Do not present it as established evidence.

## Negative evidence and scope guards
- A zero-false-positive known-drift detector does not imply high open-world recall; unseen drift can remain silent.
- A valid/retrievable skill can have zero or negative marginal downstream value.
- Explicit skill maintenance may fail to beat retained-context adaptation on average in some domains/models.
- Candidate evaluation and rollback governance can materially improve long-horizon outcomes while still consuming very large validation budgets; maintenance is not free.
- OLE results are on a simulated business benchmark with three official seeds, not software/API skill maintenance.
- GSE relevant-case replay is evidence for affected-set verification, not a proof that its replay set is minimal or cost-optimal.
- The exact common-replicate `admission gate ON/OFF × post-admission maintenance ON/OFF` four-cell interaction remains unresolved. SkillProx defines the architecture and complementary components, but the previously observed public evidence does not yet provide one common-replicate four-cell interaction estimate under identical model/stream/seeds/compute.

## Exact continuation / nonempty frontier
1. Inspect OLE official code and paper configuration for explicit `Trig`, CanaryMonitor degradation thresholds, candidate-validation batch sizes, and whether release/rollback thresholds have ablations; separate specified mechanism from empirically tuned/validated scheduler behavior.
2. Search for controlled software/API-agent studies that jointly vary drift-hazard sensing, current marginal skill value, maintenance cost, and false-edit/tail risk. If none exist, keep the value-weighted scheduler as an explicit research gap/hypothesis.
3. Continue searching Repo2Skill-Evo author artifacts/data for per-transition traces enabling localization-vs-edit-selection decomposition and empirical maintenance-cost estimation.
4. Search GSE primary tables/appendices for replay-set ablations and replay compute so that affected-set verification can be compared with full-history replay under matched budgets.
5. Continue the common-replicate four-cell admission-gate × post-admission-maintenance interaction search.
6. Continue multi-generation hidden semantic-lineage discovery/repair, rollback-target selector comparisons, and decision-influence audits under fixed controls.
7. Preserve exact tested scope and this nonempty frontier; this checkpoint is not global completion.
