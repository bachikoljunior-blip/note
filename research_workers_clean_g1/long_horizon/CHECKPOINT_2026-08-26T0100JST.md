# Long Horizon external research — clean_g1 checkpoint — 2026-08-26 01:00 JST

## Boundary / provenance
- Generation: `clean_g1`.
- Worker: `long_horizon`.
- Effective repository control read first: `automation_control/DESIRED_STATE.json`, control_revision 4, role `long_horizon`, config_revision 3, enabled_desired=true, control blob `169764c050596c2ee9763916376e7a4314c6838b`.
- Continuation input was limited to this worker's own clean namespace, public sources, and own sanitized feedback.
- Own sanitized feedback `research_feedback_clean_g1/long_horizon/FEEDBACK.json` was read. Its sole item required avoiding shared `EXECUTION_LEDGER.json` and all other-role receipts after an earlier accidental observability-boundary exposure. This run complied: no shared ledger or other-role receipt was read, and no information from those locations was used semantically.
- Did not read O/O-derived state, other workers, comparator/integrator/index/feed, shared execution ledger, other-role receipts, or legacy/pre-independence research as semantic research context.
- Exact continuation input was the newest own source-qualified checkpoint chain: `CHECKPOINT_2026-08-25T2358JST.md` plus its same-run addendum `CHECKPOINT_2026-08-25T2358JST_B.md`.

## Search target this run
Primary target: a controlled study that holds alarm/checkpoint set/restoration mechanics/policy model/compute budget fixed while ablating only the **historical rewind target selector** (fixed-depth / latest-good / root-cause or dependency / semantic-admissible / random / learned or agent-selected).

No primary study located in this run cleanly isolates only that historical target-selection variable. Existing AgentRewind, DART, GA-Rollback and WebRollback evidence remains useful but confounded by trigger, admissibility, diagnosis horizon, search policy, or restoration differences. Do not infer a winner for historical target selection from those results.

## New primary-source finding A — BRA-Audit: recovery-boundary placement should prioritize cumulative unchecked causal exposure, not audit every step
Primary: `BRA-Audit: Budgeted Runtime Auditing for LLM Multi-Agent Systems via Cumulative-Exposure Audit-Point Placement`, arXiv:2608.14668v1, submitted 2026-08-02, https://arxiv.org/abs/2608.14668 .

### Mechanism
BRA-Audit maintains a dynamic dependency graph and scores candidate audit points using cumulative unchecked exposure. The score combines roughly:
- `AuditGap`: how long information has remained unverified;
- `TopoImpact`: how much downstream computation depends on that information.

Given a finite audit budget, a greedy marginal-gain policy chooses where to spend audits. A successful audit establishes a trusted point; an audit failure triggers local rollback/re-execution of the affected region rather than blindly restarting everything.

This is not the target historical-checkpoint selector experiment, but it is a direct placement-policy ablation for **where trusted recovery boundaries should be created** under a fixed budget.

### Primary quantitative results
AgentsNet main comparison:
- Clean score 0.8162 at 26.7K tokens.
- Attack score 0.4407 at 39.5K.
- PeerGuard 0.8362 at 65.8K.
- Multi-Agent Debate 0.8656 at 76.1K.
- BRA-Audit 0.8208 at 54.5K.

Thus BRA-Audit recovers near the clean score while using about 17.2% fewer tokens than PeerGuard and 28.4% fewer than Debate in the reported setup.

Other reported tasks:
- BBH attack 0.3933; BRA-Audit 0.8600, recovery 0.4667, 8.175K tokens.
- MultiAgentBench-Research BRA-Audit score 0.902, recovery 0.525, 38.5K tokens.
- Reported token savings versus PeerGuard / Debate are 19.3% / 40.6% on BBH and 18.5% / 36.3% on Research.

### Fixed-budget placement comparison: dependency/exposure-aware vs random
At audit budget `rho=0.4`:
- BBH: Random 0.820 vs BRA 0.860, with comparable total tokens (~8.01K vs 8.18K).
- Research: Random 0.821 vs BRA 0.902, with comparable total tokens (~37.4K vs 38.5K).

This is controlled evidence that **which states are selected for trusted audit/checkpointing matters even when the audit budget is held fixed**.

### Non-monotonic audit budget and false-positive disruption
BBH score across selected budgets:
- rho=.2: 0.760, total 6.90K tokens.
- rho=.4 BRA: 0.860, total 8.18K.
- rho=.6: 0.873, total 9.57K.
- rho=1.0: 0.893, total 11.31K.

Research:
- rho=.2: 0.757, total 33.2K.
- rho=.4 BRA: 0.902, total 38.5K.
- rho=.6: 0.906, total 42.9K.
- rho=1.0: 0.897, total 46.8K.

Clean-trajectory audit false-positive rates rise with audit density:
- rho=.2: 0% / 0% on BBH / Research.
- rho=.4: 4.67% / 6.00%.
- rho=1.0: 12.00% / 16.00%.

So `audit/checkpoint more often` is not monotonically safe: more auditing increases compute and can create false-positive disruptions; on Research full auditing is slightly worse than rho=.6.

Weight ablation further supports the causal-exposure mechanism: removing audit age reduces reported overall score from ~0.821 to ~0.758; removing downstream/closed impact reduces it to ~0.793, while increasing total token cost.

### Scope
- Multi-agent dependency graphs with a reported corruption/attack setup including malicious agents as a fault abstraction.
- This does not prove the same placement rule is optimal for single-agent benign long-horizon tasks or for semantic-only memory corruption.
- It addresses placement of trusted audit/recovery boundaries, not historical rewind-target selection after an alarm.

### New design implication
Checkpoint/recovery control should distinguish at least:
1. whether an underlying state transition is recovery-relevant (prior Crab-style OS/effect classification), and
2. whether leaving it unchecked creates large **cumulative causal exposure** because many downstream decisions depend on it (BRA-Audit).

A plausible controller should therefore spend verification/checkpoint budget at high `state-change × downstream-impact × verification-age` boundaries rather than uniformly per turn.

## New primary-source finding B — Graph rectification isolates causal repair target selection and shows rollback/history can hurt
Primary: `Constructing coherent spatial memory in LLM agents through graph rectification`, ACL 2026 long paper, arXiv:2510.04195v2, https://arxiv.org/abs/2510.04195 .

### Mechanism
The method maintains an incrementally built spatial graph plus edit/reasoning history. When structural contradictions appear, it:
1. finds a minimal conflicting path pair,
2. traces the reasoning-history DAG to a lowest common ancestor,
3. extracts candidate divergent edges,
4. ranks candidates with `Edge Impact` using downstream reachability, conflict count, and usage,
5. optionally uses version-control rollback/diff/recall tools during repair.

This separates two control variables that are often conflated:
- **which causal object/state element is likely wrong** (edge/root-cause prioritization), and
- **which historical time/checkpoint to restore** (version rollback).

### Controlled synthetic ablation — root-cause prioritization can help, version rollback is not uniformly beneficial
GPT-4.1, 60-node synthetic graphs, n=20 seeds/cell:
- 4 topology errors: Base 50%, Edge-Impact 95%, VC 50%, VC+EI 50%.
- 8 topology errors: Base 30%, EI 60%, VC 25%, VC+EI 40%.
- 4 direction errors: Base 70%, EI 75%, VC 55%, VC+EI 55%.
- 8 direction errors: Base 70%, EI 50%, VC 60%, VC+EI 25%.

Interpretation within tested scope:
- causal/impact ranking gives a very large gain on sparse topology cascades;
- the same ranking can hurt with dense local/directional conflicts;
- adding version-control rollback/history can materially degrade performance in some cells instead of helping.

The paper attributes some degradation to accumulating inconsistent histories and repair iterations spent undoing partial rewrites.

### Repair-budget ablation is strongly non-monotonic
On five cleaned-MANGO games with GPT-5.5 + Edge Impact, aggregate net-resolution across max repair iterations `{5,10,20,40}` is reported as approximately:
- -30.6%, -32.4%, +50.9%, -17.6%.

Too little budget fails to complete coherent repair; too much stochastic repair introduces new conflicts faster than it removes old ones. This is a strong negative result against `keep repairing until it works`.

### Cross-model/task heterogeneity
Selected before->after results from the paper's synthetic / TextWorld table:
- GPT-5.5: 25->75 / 20->20.
- GPT-5-mini: 20->35 / 16.7->16.7.
- o4-mini: 30->20 / 20->26.7.
- Claude-Sonnet-4.6: 30->40 / 20->33.3.
- Claude-Haiku-4.5: 10->30 / 16.7->33.3.
- Gemini-2.5-Flash: 25->10 / 20->26.7.
- Gemini-3.5-Flash: 20->50 / 20->33.3.

So the mechanism is model/task dependent, with explicit regressions in some synthetic settings.

Across all 42 cleaned-MANGO games / 534 conflicts, reported residual conflicts include:
- GPT-5.5: Base 609, EI 396, VC+EI 458.
- Claude-Haiku-4.5: 874 / 827 / 625.
- Gemini-3.5-Flash: 841 / 572 / 837.

Again, the value of versioned rollback is not uniform across models.

### Repair-vs-preservation trade-off
Non-LLM heuristics can remove more conflicts but destroy correct structure:
- heuristic_remove residual conflicts 98, but loses on average ~56 correct edges;
- heuristic_modify residual 438, but loses ~97 correct edges.

Natural-text DRC deployment similarly shows a precision/over-generation risk: baseline node/edge recall 85.7/32.4 versus MapRepair 94.3/88.2, but generated graph size grows to roughly 143 nodes / 144 edges versus ground-truth-scale baseline around 47 / 49 in the reported table.

Algorithmic validation reports:
- LCA filtering cuts the candidate search space ~24.6% on average, up to 75%.
- Priority inspection discovers high-impact errors about 2.3x faster than random and needs 56.5% fewer edge examinations in the reported controlled check.

### Scope
- Spatial/topological discrete graph memory, where contradictions and dependency paths are explicit enough to support graph algorithms.
- It is not a generic semantic-memory or arbitrary-action benchmark.
- It still does not isolate the historical checkpoint/time selector sought in the main frontier.

### New design implication
Recovery policy should not treat `rewind target` as a single variable. At minimum separate:
1. **causal object/state element to invalidate or repair**, and
2. **historical checkpoint/time to resume from**.

A root-cause/impact selector can be useful even when version rollback is harmful. This helps explain why historical-target comparisons may be missing or unstable: the correct intervention may be local graph/state invalidation rather than temporal rewind.

## Updated synthesis
Long-horizon recovery now appears to require at least seven independently testable controls:
1. **Checkpoint/audit placement** — recovery-relevant state change plus cumulative causal exposure, not uniform per-turn snapshots.
2. **Whether to intervene** — calibrated failure/state-quality signal with explicit false-positive/disruption accounting.
3. **When to cut after alarm** — respect atomic/semantic/effect-settled boundaries.
4. **Which causal object/state element is wrong** — dependency/root-cause/impact localization.
5. **Which historical checkpoint/time to resume from** — still lacks a clean matched selector-policy ablation.
6. **What to carry across recovery** — raw artifact/diff, compact lesson, selective dependency-local state, or none.
7. **How much repair/retry budget to spend** — non-monotonic; too little can under-repair, too much can create new errors/disruption.

The controller objective should measure final task success jointly with compute/latency/storage/effect risk and preservation of already-correct state. Audit/repair accuracy alone is not enough.

## Tempered / rejected hypotheses added this run
- `Checkpoint or audit every step for maximum safety`: rejected as a universal rule. BRA-Audit shows cost and false-positive disruption rise with density; Research score is non-monotonic.
- `Version control / rollback tools cannot hurt because they only add options`: rejected in the MapRepair synthetic ablations; VC and VC+EI sometimes underperform Base/EI.
- `More repair iterations monotonically improve consistency`: directly contradicted by the MANGO repair-budget curve.
- `Root-cause prioritization is universally beneficial`: rejected; EI helps sparse topology cascades but can hurt dense direction-error cases.
- `Historical rewind target is the same problem as causal-error localization`: rejected as a useful modeling simplification. The graph-rectification evidence cleanly separates object-level fault localization from temporal rollback.

## Direct historical rewind-target selector gap status
Still unresolved. No located primary study in this run holds alarm events, checkpoint set, restoration mechanics, policy model and compute budget fixed while changing only the historical target rule among fixed-depth/latest-good/value/root-cause/admissible/random/learned selectors.

Do not fill this gap by over-interpreting WebRollback, AgentRewind, DART, GA-Rollback, BRA-Audit, or graph rectification; each changes a different control variable or domain assumption.

## Nonempty frontier
1. **Direct historical target-selector ablation** remains highest value; search older systems/recovery literature plus agent-specific work, but require matched alarm/checkpoint/restoration budget before claiming selector superiority.
2. **Causal-object vs temporal-target factorial experiment**: find or design evidence that independently varies root-cause localization and rewind time. This is now a sharper missing experiment than a single selector leaderboard.
3. **Cross-domain cumulative-exposure checkpoint placement**: test whether BRA's verification-age × downstream-impact placement transfers from multi-agent graphs to single-agent tool trajectories and semantic memory.
4. **Automatic safe-cut boundary discovery**: immediate alarm vs fixed patience vs effect-settled vs learned semantic boundary under matched detector.
5. **Artifact carryover policy**: none / raw diff-state delta / compact lesson / dependency-local subset / full prompt under matched true- and false-alarm trajectories.
6. **Repair stopping rule**: learn a controller that detects when additional repair is likely to create more conflict than it removes; validate final task success, preservation, and cost.
7. **Subgoal/folding negative evidence**: continue seeking controlled wrong-decomposition/stale-summary cases.

## Exact continuation
Next run first action: search for a **factorial or matched experiment separating causal fault localization from temporal rewind target selection**, including classic agent recovery/planning/checkpoint papers and recent LLM runtime work. Required evidence: same alarm set, same checkpoint candidates, same restoration/replay mechanism and budget, with only localization or target-selection rule changed. In parallel, search for automatic safe-cut/effect-settled boundary discovery and repair-stopping policies with final-task A/B outcomes. If no direct historical-target study is found again, preserve the gap and prioritize the causal-object × temporal-target factorial design rather than inferring a selector winner from confounded systems.