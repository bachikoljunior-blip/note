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

Read `STATE.md` for accumulated findings through 18:15 JST, then read the source-qualified checkpoints above in order for the newest evidence and exact continuation.

Top unresolved frontier:
1. hierarchical controller-of-controllers: learn both local Lean proof actions and whether to activate a more expensive architecture such as extra agents, population/evolution, specialized prover, global retrieval or replanning;
2. controller-only matched experiment: replace HILBERT/BFS/LEAP fixed thresholds, triggers or DFS/backtracking with a learned heterogeneous action policy while holding prover/retriever/verifier/actions fixed;
3. calibrated action/value-of-computation under theorem/backbone/search-policy shift: Brier/ECE/reliability/selective-risk for another attempt, repair, retrieve, decompose, replan, backtrack, tool/agent escalation and stop;
4. backbone/difficulty-conditioned compute purchase: predict when a simple compiler-feedback/queue loop suffices and when richer orchestration has positive marginal value;
5. action-specific sufficient state: compressed trajectory/progress/error history + current proof state + reusable DAG/subgoal cache + retrieval coverage + remaining budget + execution substrate;
6. matched subgoal scheduling: ordered first-stuck focused parallelism vs hardest-branch vs independent parallelism vs total-work/tail-risk scheduling under equal real compute;
7. variable branching/search purchase: learn when greedy scheduling suffices and when MCTS/beam/semantic branching pays for itself;
8. coverage-aware routing and calibrated abstention under partial/OOD observations;
9. triggered global re-retrieval after local failure/decomposition change;
10. execution-substrate-aware cost: generation, retrieval, verifier/tactic/checking, snapshot/state reconstruction, downstream savings and wall-clock;
11. exact Lean composite of snapshot/forking + semantic tactic diversity + compiler repair + typed/calibrated hierarchical routing under equal real compute;
12. benchmark-audited robustness with pinned Lean/mathlib/repository/harness versions and candidate/retrieval-access sensitivity.

Important updates from the newest checkpoints:
- LeanFlow gives direct workflow-control ablations. Under a 2,000-call cap with Kimi-K2.6, the full queue+tools workflow completes both document projects in 1,043 and 1,278 calls, while both no-queue variants hit the cap on both; with GPT-5.5 all document variants complete, though the full workflow usually uses substantially fewer input tokens. Queue/control value is therefore strongly backbone-dependent.
- AlphaProof Nexus supplies direct research-level Lean evidence for architecture selection. Its full evolutionary controller can save roughly 2x–5x cost on the hardest compared Erdős problems but is roughly half as cost-efficient on easier ones; 3/6 generators are more efficient on easier tasks while 10 is stronger on the hardest. A one-generator population-sampling variant underperforms the basic loop. Rich orchestration should itself be a purchased meta-action, not a universal default.
- AlphaProof Nexus uses a real statistical allocation mechanism over partial proof sketches: asynchronous LLM raters -> Plackett-Luce/Elo -> P-UCB parent selection, plus global exact-goal caching. But tool activation, decomposition prompts, parallelism and per-episode/subgoal budgets are still mostly fixed/manual, so it does not close heterogeneous learned action routing.
- HILBERT's released config fixes depth/attempt/correction/time thresholds; BFS-Prover-V2 exposes explicit replan mode/event triggering; LEAP publishes simple DFS/backtracking and explicitly identifies branch prioritization/compute allocation as future work. These provide strong controller-only baselines.
- LEAP iterative compiler feedback improves Gemini-3.1-Pro on Lean-IMO-Bench Basic 20.0%→36.6% but changes Goedel-Prover-V2-32B 10.0%→6.6%; action value is prover-regime dependent.
- Persistent verified memory repeatedly matters: LEAP DAG memoization, BFS shared subgoal cache, AlphaProof Nexus exact goal cache and LeanFlow theorem-local failure state all reduce redundant work; memory coverage should be part of controller state.
- AlgoSkill remains cross-domain evidence for typed heterogeneous action scheduling; CSSC remains a low-evidence implementation lead with heuristic controller, not scientific proof.
- `research_feedback_clean_g1/reasoning/FEEDBACK.json` remains absent; no sanitized feedback was consumed.

Exact continuation:
1. search current Lean/formal-proof work for systems that dynamically select controller mode, agent count, specialized tool/prover activation or heterogeneous meta-actions from observed difficulty rather than using a fixed architecture;
2. search off-policy/contextual-bandit/RL formulations that learn action value from formal verifier trajectories, not only tactic selection;
3. search calibrated value-of-computation/metareasoning methods suitable for deciding whether to buy another local attempt, retrieval, extra agent, specialized prover, population search or global replan; keep transfer evidence separate from direct Lean evidence;
4. continue controller-only trace statistics, matched subgoal scheduling, backbone-conditioned action value, triggered global retrieval, trajectory compression and snapshot+semantic-repair integration;
5. keep the frontier nonempty and preserve exact source/version/cost-accounting/tested-scope caveats.

Do not read legacy `research_workers/reasoning/`, O, comparator, integrator, feed, other-worker state, shared execution ledger, or other-role receipts.
