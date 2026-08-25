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
16. `2026-08-26T0302JST-followup4.md`

Read `STATE.md` for accumulated findings through 18:15 JST, then read the source-qualified checkpoints above in order for newest evidence and exact continuation.

Top unresolved frontier:
1. **matched Lean controller comparison:** same action/tool/verifier/memory substrate under the same real budget, comparing fixed/rule control, free-form LLM planning and a learned typed heterogeneous policy;
2. **logged formal-agent policy learning:** contextual-bandit/offline-RL/value learning over multi-action Lean traces (`continue/repair/retrieve/decompose/replan/backtrack/spawn/escalate/stop`) rather than only tactic prediction;
3. **hierarchical controller-of-controllers:** decide both local proof action and whether to buy more thinking, stronger model, more workers, specialized prover, global retrieval, population/evolution or replan;
4. **calibrated prospective action/value-of-computation:** Brier/ECE/reliability/selective-risk under theorem/backbone/search-policy shift, especially near expensive-action boundaries;
5. **compact sufficient online memory/context isolation:** self-managed notes or compact Whiteboard + selective repository retrieval + branch-local workers versus raw history, evaluated by downstream action quality and solve/cost;
6. **backbone/difficulty-conditioned compute purchase:** predict when cheap iterative loops suffice and when feedback, search, additional thinking or richer orchestration has positive marginal value;
7. **stateful constrained optimization:** extend one-shot global-budget allocation to Markov/partial-observation Lean trajectories with verified reusable cache/DAG state and action-specific substrate cost;
8. **matched subgoal scheduling:** ordered first-stuck focus vs hardest-branch vs independent parallelism vs total-work/tail-risk under equal real compute;
9. **variable branching/search purchase:** learn when greedy scheduling suffices and when MCTS/beam/semantic branching pays for itself;
10. **coverage-aware routing/abstention, triggered global re-retrieval, execution-substrate-aware cost, snapshot+semantic-selection+compiler repair, and benchmark-audited robustness** remain open.

Important updates from the newest checkpoints:
- **OpenProver** supplies a strong direct free-form Lean controller baseline. On 185 ProofNet formal theorems with a 100k output-token budget per problem, Kimi-K2.5 improves from linear rollout **36.8% to 57.3%** and Leanstral from **21.1% to 28.1%**. Its Planner chooses heterogeneous actions (`spawn`, repository read/write, Whiteboard update, theorem reread, search, submit), while Lean Workers can verify/store/search. This is matched on total output-token budget but not on wall-clock/input/verifier/parallel overhead.
- OpenProver also implements an explicit context-pollution defense: Workers do not see prior Workers' or Planner reasoning traces; Verifiers do not see Worker reasoning traces; the Planner gets a compact Whiteboard plus only summaries/slugs of large repository items, retrieving full items on demand. This converges with AxProverBase's compact-memory result and gives a concrete branch-independence baseline.
- Targeted searches for Lean `contextual bandit`, `offline RL`, `meta-action`, `tool routing`, and `compute allocation` did **not** surface a primary direct Lean system learning the full heterogeneous meta-action policy. Pantograph exposes machine-readable tactic transitions suitable for offline RL, but is an interface/data primitive, not that controller. Keep this absence as an active search gap, not proof of nonexistence.
- **AxProverBase** directly rejects raw-history accumulation as the default: on its 100-problem PutnamBench ablation subset, a compact self-managed notebook proves **7% more** than `n=5` full-attempt history at **20% lower total cost** (10% lower at equal iterations), with about half the run dispersion. It still uses a fixed 50-iteration cap.
- AxProverBase also shows thinking-budget value is model dependent: Opus benefits from 10k→32k and can match doubling iterations at lower cost, while some Gemini settings are flat. Compute actions must be backbone-conditioned.
- **Numina-Lean-Agent** is another free-form heterogeneous-tool baseline, reporting 12/12 Putnam 2025. Public author clarification says displayed large A5/B6 budgets were calculated after completion, not autonomously pre-routed; A5 subagent isolation was agent-selected. B4 equal-call evidence favors iterative refinement (success in 5 rounds) over independent sampling (failure by 10).
- **Adaptive Test-Time Compute Allocation** (non-Lean transfer) gives a rigorous global-budget template via Lagrangian pricing and a cheap oracle-imitation policy, with up to 12.8% relative MATH accuracy gain and >91% oracle-action imitation under matched average budgets; it does not model stateful Lean meta-actions or probability calibration.
- **LeanFlow** shows deterministic queue/workflow state can dominate free-running agent loops, especially for Kimi-K2.6; stronger GPT-5.5 completes all tested document variants but often at higher context cost without queue control. Controller value is backbone dependent.
- **AlphaProof Nexus** shows rich evolutionary/population coordination can save roughly 2x–5x on hardest compared Erdős cases while being about half as cost-efficient on easier ones; fixed rich orchestration is not universally efficient.
- **HILBERT, BFS-Prover-V2, LEAP** expose strong heterogeneous action hierarchies but use fixed retry/depth/time thresholds, event-triggered replanning, or simple DFS/backtracking. LEAP explicitly identifies branch prioritization and compute allocation as future work.
- Persistent verified memory repeatedly helps: LEAP DAG, BFS subgoal cache, AlphaProof Nexus exact-goal cache, OpenProver repository/lean_store, LeanFlow theorem-local state, AxProver compact notebook.
- `research_feedback_clean_g1/reasoning/FEEDBACK.json` remains absent; no sanitized feedback was consumed.

Exact continuation:
1. inspect OpenProver public benchmark/run artifacts for action-frequency, Worker-spawn, Whiteboard/repository-read, verifier and tool-use statistics suitable as an offline multi-action dataset;
2. search Pantograph/OpenProver/LeanFlow/HILBERT citations and forks for released offline-RL/contextual-bandit/controller learning on machine-readable formal-agent traces;
3. search stateful sequential value-of-computation/metareasoning under global resource constraints, preserving transfer-vs-direct-Lean scope;
4. continue matched fixed-vs-free-form-vs-learned controller, subgoal scheduling, backbone-conditioned action values, triggered reretrieval, trajectory compression and snapshot+semantic-repair searches;
5. keep the frontier nonempty and preserve exact source/version/model/budget/cost-accounting/tested-scope caveats.

Do not read legacy `research_workers/reasoning/`, O, comparator, integrator, feed, other-worker state, shared execution ledger, or other-role receipts.
