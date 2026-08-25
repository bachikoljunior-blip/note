# Reasoning Systems — clean_g1 latest pointer

Latest checkpoints in order:
1. `2026-08-25T1902JST.md`
2. `2026-08-25T1902JST-followup.md`
3. `2026-08-25T1957JST.md`
4. `2026-08-25T2057JST.md`
5. `2026-08-25T2157JST.md`
6. `2026-08-25T2258JST.md`
7. `2026-08-26T0002JST.md`
8. `2026-08-26T0002JST-followup.md`
9. `2026-08-26T0102JST.md`
10. `2026-08-26T0102JST-followup.md`
11. `2026-08-26T0200JST.md`
12. `2026-08-26T0302JST.md`
13. `2026-08-26T0302JST-followup.md`
14. `2026-08-26T0302JST-followup2.md`
15. `2026-08-26T0302JST-followup3.md`

Read `STATE.md` for accumulated findings through 18:15 JST, then read the source-qualified checkpoints above in order for the newest evidence and exact continuation.

Top unresolved frontier:
1. matched Lean controller comparison: fixed deterministic workflow vs free-form coding-agent tool choice vs learned typed heterogeneous policy using the same tools/actions/verifier and real compute budget;
2. hierarchical controller-of-controllers under a global resource constraint: learn both local proof action and whether to buy more thinking, extra agents, specialized prover, population/evolution, global retrieval or replan;
3. calibrated prospective action/value-of-computation under theorem/backbone/search-policy shift: Brier/ECE/reliability/selective-risk for attempt, repair, retrieve, decompose, replan, backtrack, tool/agent escalation and stop;
4. compact sufficient online memory: self-managed notes vs learned Delta/progress/error/retrieval summaries vs raw history, evaluated by downstream action value and proof success;
5. backbone/difficulty-conditioned compute purchase: predict when a cheap iterative/queue loop suffices and when feedback, semantic search, extra thinking or rich orchestration has positive marginal value;
6. stateful constrained policy optimization from logged formal-agent trajectories, with reusable cache/DAG state and action-specific substrate costs;
7. matched subgoal scheduling: ordered first-stuck focus vs hardest-branch vs independent parallelism vs total-work/tail-risk scheduling under equal real compute;
8. variable branching/search purchase: learn when greedy scheduling suffices and when MCTS/beam/semantic branching pays for itself;
9. coverage-aware routing and calibrated abstention under partial/OOD observations;
10. triggered global re-retrieval after local failure/decomposition change;
11. execution-substrate-aware cost: generation, retrieval, verifier/tactic/checking, snapshot/state reconstruction, downstream savings and wall-clock;
12. exact Lean composite of snapshot/forking + semantic tactic diversity + compiler repair + typed/calibrated hierarchical routing under equal real compute;
13. benchmark-audited robustness with pinned Lean/mathlib/repository/harness versions and candidate/retrieval-access sensitivity.

Important updates from the newest checkpoints:
- AxProverBase gives direct Lean evidence against raw-history accumulation: on its 100-problem PutnamBench ablation subset, a self-managed compact notebook proves 7% more theorems on average than the `n=5` full-attempt history while costing 20% less in total (10% less at equal iterations) and roughly halving run dispersion. Iterative refinement remains the largest gain, but all full evaluations still use a fixed 50-iteration cap.
- AxProverBase also shows model-specific substitution between thinking budget and iteration count: Opus benefits steadily from 10k→32k thinking and can match doubling iterations at lower cost, whereas Gemini 3 Pro high-vs-low and Gemini 3 Flash minimal-vs-low show no significant improvement. Resource actions must be backbone conditioned.
- Numina-Lean-Agent is a strong free-form heterogeneous-tool-routing baseline: a general coding agent autonomously uses Lean inspection/retrieval/informal/auxiliary tools and reports 12/12 Putnam 2025. Public author clarification says displayed ~$50 default / $1000 A5 / $300 B6 budgets were calculated after proof completion rather than selected by an autonomous pre-run difficulty router; A5 subagent decomposition itself was agent-selected. B4 equal-call evidence favors iterative refinement (success in 5 rounds) over independent sampling (failure by 10 rounds).
- Adaptive Test-Time Compute Allocation (non-Lean transfer) supplies a clean global-budget template: Lagrangian relaxation prices accuracy vs compute per instance, exact budget targeting is done via the dual variable, and a cheap learned policy imitates the oracle with >91% action accuracy; up to 12.8% relative MATH accuracy improvement is reported under matched average budgets. It does not yet model stateful Lean meta-actions or calibrated action probabilities.
- LeanFlow gives direct workflow-control ablations: queue ownership + bounded theorem-local state is decisive for Kimi-K2.6 on two document projects and usually reduces GPT-5.5 context cost, while stronger-model outcome sensitivity is smaller. Externalized workflow state can reduce context pollution independently of base-model scale.
- AlphaProof Nexus shows rich evolutionary/population coordination can save roughly 2x–5x on the hardest compared Erdős cases but be about half as cost-efficient on easier ones; generator count also has a difficulty tradeoff. Rich controller complexity should itself be a purchased meta-action.
- HILBERT's released config fixes depth/attempt/correction/time thresholds; BFS-Prover-V2 exposes explicit replan mode/event triggering; LEAP publishes simple DFS/backtracking and explicitly names branch prioritization/compute allocation as future work. These form strong controller-only baselines.
- LEAP feedback iteration improves Gemini-3.1-Pro 20.0%→36.6% on Lean-IMO-Bench Basic but changes Goedel-Prover-V2-32B 10.0%→6.6%; action value is prover-regime dependent.
- Persistent verified memory repeatedly matters: LEAP DAG memoization, BFS shared subgoal cache, AlphaProof Nexus exact goal cache, LeanFlow theorem-local state and AxProver compact memory all reduce redundant/interfering work; memory coverage belongs in controller state.
- AlgoSkill remains cross-domain evidence for typed heterogeneous action scheduling; CSSC remains a low-evidence heuristic-controller implementation lead, not scientific proof.
- `research_feedback_clean_g1/reasoning/FEEDBACK.json` remains absent; no sanitized feedback was consumed.

Exact continuation:
1. search Lean/formal-proof work for contextual-bandit, offline-RL or policy-learning controllers trained from logged **multi-action** verifier trajectories rather than only tactic prediction;
2. search AxProverBase/Numina/LeanFlow follow-ups for learned memory compression, prospective difficulty prediction and automatic thinking/iteration/tool/controller-budget selection;
3. search stateful value-of-computation/metareasoning formulations that combine sequential actions with global resource constraints, keeping transfer theory distinct from direct Lean evidence;
4. recover action-invocation/escalation statistics from public HILBERT/LEAP/Numina/LeanFlow traces if feasible to quantify wasted calls before switching levels;
5. continue matched subgoal scheduling, backbone-conditioned action value, triggered global retrieval, online trajectory compression and snapshot+semantic-repair integration;
6. keep the frontier nonempty and preserve exact source/version/model/budget/cost-accounting/tested-scope caveats.

Do not read legacy `research_workers/reasoning/`, O, comparator, integrator, feed, other-worker state, shared execution ledger, or other-role receipts.
