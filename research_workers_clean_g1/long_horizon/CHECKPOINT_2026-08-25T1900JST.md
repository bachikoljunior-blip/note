# Long Horizon clean_g1 checkpoint — 2026-08-25 19:00 JST

## Boundary / provenance
- Worker: `long_horizon`; generation: `clean_g1`.
- Continuation inputs used in this run: only `research_workers_clean_g1/long_horizon/STATE.md` plus public external sources.
- Did not inspect O, O-derived state, comparator/integrator output, other workers, or legacy `research_workers/long_horizon/`.
- Search bias remained failure-case-first / longitudinal: online intervention harm, rollback side effects, and compression/subgoal failure modes.

## New primary-source findings

### A. Accurate failure prediction can make agents worse when intervention is enabled
Primary: https://arxiv.org/abs/2602.03338 — *Accurate Failure Prediction in Agents Does Not Imply Effective Failure Prevention*.

The paper evaluates a 0.6B Qwen3 critic trained on 7,636 trajectory steps. Across 1,372 held-out samples the critic reaches AUROC 0.936 and F1 0.963, yet deployment-time interventions can reduce final task success substantially.

Core causal accounting:
- baseline failure rate `p`
- recovery rate `r`: baseline failures converted to success
- disruption rate `d`: baseline successes converted to failure
- `ΔSuccess = p*r - (1-p)*d`
- intervention helps only when `p > d/(r+d)`.

Matched final-outcome results retained from the primary paper:
- HotPotQA: Qwen3-8B 57.0% baseline -> best intervention 54.7% (-2.3 pp); GLM-4.7 70.3% -> 70.3% (0); MiniMax-M2.1 64.0% -> 38.5% (-25.5 pp).
- GAIA: all three tested backbones degraded under the best intervention condition; the largest reported drop is MiniMax-M2.1 46.7% -> 16.7% (-30.0 pp).
- ALFWorld, where baseline failure prevalence is much higher: Qwen improves 5.8% -> 8.6% (+2.8 pp, p=0.014); GLM +1.1 pp; MiniMax +0.5 pp.
- A 50-task Qwen ALFWorld pilot estimated failure prevalence ~89%, recovery ~12%, disruption ~56%, giving a threshold near 82%; the observed prevalence exceeds it and the pilot correctly predicts a positive intervention effect.
- Scaling the critic from 0.6B to 14B did not solve the problem: overall AUROC 0.936 for the baseline critic versus best 14B result 0.927.
- On Qwen/HotPotQA, threshold sweeps and simple heuristic intervention policies remained below the 57% baseline; calibration alone did not remove intervention harm.
- Early-step interventions are especially destabilizing in the reported HotPotQA analysis: a rollback can make an otherwise-correct trajectory abandon the answer, re-search, and exhaust later intervention budget.

Scope-bounded takeaway: offline monitor accuracy is not a deployment criterion. A critic/intervention pair must be evaluated by matched final-task A/B outcomes for each backbone/domain, with explicit recovery and disruption estimates. In high-success regimes the correct policy may be *do not intervene*.

### B. Checkpoint restore does not roll back external reality

#### Atomix
Primary: https://arxiv.org/abs/2602.14849 — *Atomix: Timely, Transactional Tool Use for Reliable Agentic Workflows*.

Mechanism-level result: external effects need explicit settlement semantics rather than assuming checkpoint replay is equivalent to rollback. Atomix distinguishes bufferable effects, reversible externalized effects that can be compensated, and irreversible effects that must be held behind a commit/frontier gate. Its abstract reports fault-injection improvements, isolation under speculative/concurrent execution, and prevention of correctly classified irreversible actions from leaking. This supports separating reversible agent/environment state from irreversible effect state.

Important scope: the runtime can only protect effects that are mediated and correctly classified; compensation is not true reversal of an irreversible external effect.

#### ACRFence attack validation
Primary: https://arxiv.org/abs/2603.20625 — *ACRFence: Preventing Semantic Rollback Attacks in Agent Checkpoint-Restore*.

The paper validates a concrete semantic rollback failure mode using Claude Code CLI backed by Qwen3-32B and simulated external services:
- Action Replay: all 10/10 checkpoint-restore trials produced duplicate commits; no-checkpoint baseline produced 0/10.
- Authority Resurrection: stateless single-use-token validation allowed 2/2 reuse attempts after restore; stateful server-side revocation rejected all.

Root cause: after restore an LLM can re-synthesize a semantically equivalent external action with a different request ID/arguments, bypassing server idempotency keyed to the original request. Internal checkpoint state and external-world effect state therefore cannot be treated as one rollback domain.

Critical negative scope: the paper validates the attacks but explicitly says it does **not** yet implement/evaluate the proposed ACRFence mitigation. Keep ACRFence as attack evidence, not as a proven defense.

#### MemTX
Primary: https://arxiv.org/abs/2607.23929 — *MemTX: Transactional Belief Commit for Stateful Agent Memory*.

Relevant mechanism: a memory write is separated from a belief commit. Records carry evidence/permissions/provenance/validity; writes are staged under snapshot isolation; irreversible tool calls are gated on committed belief state; retractions trigger typed cascading repair. The paper machine-checks action-safety and cascade-repair invariants over 5.5M protocol states with zero violations and reports zero downstream harm for MemTX across all five evaluated backbones, while statistically leading baselines on four and tying the best baseline on the strongest fifth.

Scope caution: the controlled main suite is short (1–4 turns, median 2) and is a conformance-style evaluation, not direct evidence of long-horizon single-agent gains. Treat it as state/effect governance evidence, not a longitudinal benchmark result.

### C. Compression can preserve completion while silently increasing interaction cost
Primary: https://arxiv.org/abs/2608.16370 — *What Does Context Compression Cost an Agent? Interaction Costs Unrevealed by Task-Completion Metrics* (submitted 2026-08-17).

Controlled deterministic planning environment, fixed 24-turn horizon, three models x two regimes:
- retrieval calls increase in all six model/regime comparisons and account for almost all added interaction; 5/6 remain significant after Holm correction.
- at the prespecified 5x compression point, completion change is not significant in any cell.
- GPT-5.5: completion 80% -> 85% (p=1.0), while retrieval calls 21.0 -> 63.9 (p=.002).
- replacing retained queryable D-state with semantically irrelevant content increases retrieval by 57% (p<.001) without significant completion change.
- ALFWorld sliding compression does not show the same retrieval surge, so the effect is environment-dependent rather than an intrinsic property of shorter context.

Takeaway: completion alone can hide a reacquisition tax. Context policies should measure retrieval/tool calls, elapsed steps and budget exhaustion in addition to terminal success.

### D. Recurrent summarization can mislocalize execution state; boundary-local verification helps
Primary: https://arxiv.org/abs/2608.06503 — *Toward Reliable Context Compression for Long-Horizon Agents: An Empirical Study of Execution Instability* (TRACE; submitted 2026-08-06).

Failure evidence in AppWorld:
- at 16K/8K/4K budgets, FIFO matches or slightly exceeds summary-based compaction; summary only clearly wins under the tightest 2K budget (72.8% vs FIFO 42.2%). Both remain below full context.
- paired pre/post-compaction continuations cover 590 boundaries / 4,640 rollouts. Immediately after compaction, POST produces +0.108 blocked/error actions versus PRE on the first action; refetch/replay starts +0.031 and rises after the second action.
- failure mode is not simply missing facts: summaries can retain globally relevant information while weakening the local action-observation continuity needed to know what has already happened and where execution currently is.

TRACE optimizes only the natural-language compression template with the downstream model/tools frozen, using paired closed-loop continuations from the same environment state. AppWorld test-normal, MiniMax-M3:
- no compression: accuracy 85.7 / Pass2 77.4 / Pass@2 94.0.
- best prior compressed baseline Prompting-O: 71.4 / 59.5 / 83.3.
- TRACE: 77.1 / 67.3 / 86.9, improving Prompting-O by +5.7 accuracy, +7.8 Pass2, +3.6 Pass@2, but still below no compression overall.
- on hard tasks TRACE reaches 63.5 / 52.4 / 74.6 versus no-compression 75.4 / 65.1 / 85.7, so the remaining gap is substantial.
- transferred unchanged to Kimi-K2.7-Code, TRACE reaches overall accuracy 84.5 and Pass2 79.2 versus no compression 82.7 / 73.8, while Pass@2 is slightly lower 89.9 vs 91.7. On medium tasks Pass2 rises 60.4 -> 81.2.

Takeaway: compression quality is partly a control problem at the transition boundary. Verify whether compression changes the *next actions* and multi-run reliability, not only whether a summary contains the right facts.

## Updated cross-source synthesis
1. `detect failure` and `intervene` are separate capabilities. High critic AUROC can coexist with severe final-success regressions; deployment depends on recovery-versus-disruption economics.
2. `rollback internal state` and `rollback external effects` are separate operations. External tool effects need a durable effect ledger plus delay/gating, compensation where valid, and explicit fork semantics for post-restore divergence.
3. `compress context` and `reduce effective execution cost` are separate objectives. Compression can lower tokens while causing blocked actions, replay/refetch, or triple retrieval calls with unchanged headline completion.
4. Context compression should preserve *execution position / local continuity*, not just facts. Boundary-local paired continuations expose failures that terminal metrics miss.
5. These mechanisms are strongly environment- and backbone-dependent. A policy that helps a high-failure domain can hurt a high-success domain; an interaction-cost signature present in one environment can disappear in another.

## Rejected / tempered leads from this run
- `A high-AUROC critic should always be enabled`: directly contradicted by matched deployment A/B.
- `Tune the critic threshold until intervention is safe`: not sufficient in the reported HotPotQA sweep.
- `Checkpoint restore makes tool actions safe to retry`: directly contradicted by 10/10 duplicate commits in ACRFence's restore test.
- `Server idempotency by request ID solves replay`: insufficient when an LLM re-synthesizes a new ID after restore.
- `Compression is good if completion is unchanged`: contradicted by large, statistically significant retrieval-cost increases with unchanged completion.
- `Summaries always beat FIFO because they preserve more information`: contradicted at moderate AppWorld budgets in TRACE; local recency/action continuity can matter more until compression is severe.
- `TRACE proves compression can match full context universally`: rejected; its own MiniMax-M3 table retains a substantial overall/hard-task gap and the paper is a preliminary preprint.

## Nonempty frontier
1. **AgentRewind primary-table verification remains unresolved**: verify exact 62.2/78.0/87.8 and component ablations from the primary PDF/author artifact before promoting those values.
2. **Checkpoint frequency / rewind-depth policy**: find controlled ablations for placement frequency, rewind depth, checkpoint cost, and recovery quality; distinguish environment-state checkpointing from context-only reset.
3. **Irreversible-effect defense evaluation**: extract Atomix primary tables (fault level, irreversible-send leakage, recovery vs checkpoint-replay) and find independent evaluations of semantic replay/fork or transactional tool-effect gating.
4. **Compression negative evidence beyond AppWorld**: inspect the 2026-08-17 interaction-cost paper's full tables and causal oracle restoration breakdown; search for wrong/stale summaries and false-current-state errors in other real agent benchmarks.
5. **Subgoal decomposition failure**: seek controlled LLM-agent cases where wrong decomposition or rigid milestones reduce success, separating decomposition quality from context compression.
6. **Active memory intervention by memory demand**: test/search whether selective reminders improve online update, interference resistance, source binding and hypothesis revision separately rather than aggregate success.
7. **UltraHorizon CRNR numeric extraction** remains unresolved.
8. **LongDS per-pattern recovery** remains unresolved: inspect inheritance/update/rollback/multi-state-composition breakdown and any intervention experiments.
9. **Post-hoc selection vs mid-trajectory intervention**: investigate whether sampling multiple completed trajectories + verifier selection is systematically safer than online rollback in high-success domains, accounting for cost.

## Exact continuation
Next run first action: **extract primary quantitative Atomix tables and ablations for transactional retry, checkpoint-replay, irreversible-effect gating, and fault rates**, specifically checking whether its advantage comes from recoverable-state retry or from effect isolation/gating. Then branch to checkpoint-frequency/rewind-depth ablations and keep at least one unresolved compression/subgoal-negative-evidence branch after checkpointing.