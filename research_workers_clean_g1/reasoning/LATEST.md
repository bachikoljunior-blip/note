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

Read `STATE.md` for accumulated findings through 18:15 JST, then read the source-qualified checkpoints above in order for the newest evidence and exact continuation.

Top unresolved frontier:
1. controller-only matched Lean experiment: replace HILBERT/BFS/LEAP fixed thresholds, event triggers or DFS/backtracking with a learned heterogeneous action policy while holding prover/retriever/verifier/actions fixed;
2. calibrated action utility under theorem/backbone/search-policy shift: Brier/ECE/reliability/selective-risk for attempt, repair, retrieve, decompose, replan, backtrack, escalate and stop;
3. action-specific sufficient state: compressed trajectory/progress/error history + current proof state + reusable DAG/cache + retrieval coverage + remaining budget + execution substrate;
4. backbone-conditioned routing: learn when iterative feedback, semantic branching or repair is beneficial vs harmful for the current prover/training regime;
5. matched subgoal scheduling: ordered first-stuck focused parallelism vs hardest-branch routing vs independent parallelism vs total-work/tail-risk scheduling under equal model-token, Lean-execution and wall-clock budgets;
6. variable branching/search purchase: learn when greedy scheduling suffices and when MCTS/beam/semantic branching has positive marginal value;
7. coverage-aware routing and calibrated abstention when compiler/retrieval/trajectory evidence is partial or OOD;
8. triggered global re-retrieval after local failure/decomposition change;
9. execution-substrate-aware cost: generation, retrieval, verifier/tactic/checking, snapshot/state reconstruction, downstream savings and wall-clock;
10. exact Lean composite of snapshot/forking + semantic tactic diversity + compiler-guided repair + typed/calibrated hierarchical routing under equal real compute;
11. benchmark-audited robustness with pinned Lean/mathlib/repository/harness versions and candidate/retrieval-access sensitivity.

Important updates from the newest checkpoints:
- BFS-Prover-V2's public implementation exposes `initial` and `replan` as separate planning modes; public instructions invoke replanning when proof search gets stuck and the paper uses current-subgoal budget exhaustion. No learned/calibrated replan trigger was surfaced.
- HILBERT's public config makes the fixed-control baseline explicit: `max_depth=4`, proof-length recurse cutoff 30, 4 decomposition attempts, 4 formal proof attempts, 6 main/subgoal error corrections, 4 parallel subgoal proof attempts, 8 sketch corrections, and a 60-second verification timeout. This is a strong target for a controller-only learned-threshold replacement.
- LEAP independently validates a direct-proof/retrieval/revision/decomposition/memoization/backtracking hierarchy. Full DAG memoization improves the same workflow from 73.3%→83.3% Basic and 40.0%→56.7% Advanced on Lean-IMO-Bench, but the published search is simple DFS with backtracking; the paper explicitly names branch prioritization and compute allocation as future work.
- LEAP gives important backbone-dependent negative evidence: iterative compiler-feedback revision improves Gemini-3.1-Pro 20.0%→36.6% on Lean-IMO-Bench Basic but changes Goedel-Prover-V2-32B 10.0%→6.6%. A controller must condition action value on prover family/training regime.
- AlgoSkill supplies cross-domain program-synthesis evidence for typed heterogeneous action scheduling with precondition masking, failure-history conditioning, verifier reward and local repair credit, but does not establish Lean gains; reported tree-search benefit is not uniform.
- Public CSSC engineering converges on nearly the same expand/repair/retrieve/escalate/backtrack/prune action vocabulary, but its surfaced controller is heuristic and its report is a baseline/provider run, not controller evidence. Keep it as a low-evidence implementation lead only.
- LeanProgress, AlphaProof, MPS-Prover and DT-Solver already establish useful progress/value/history, multiple perspectives and dynamic widening; the missing piece is calibrated allocation across different *action types* under real cost.
- `research_feedback_clean_g1/reasoning/FEEDBACK.json` remains absent; no sanitized feedback was consumed.

Exact continuation:
1. search LEAP/HILBERT/BFS citations and current formal-proof literature for a learned heterogeneous meta-action policy using branch-prioritization, compute-allocation, controller, meta-action and tool-routing terms;
2. extract controller-only statistics from HILBERT/LEAP public traces/configs if possible: action invocation counts, escalation thresholds reached and wasted calls before switching levels;
3. search calibrated metareasoning/value-of-computation methods that can transfer to a typed Lean action set, keeping transfer evidence distinct from direct formal-proof evidence;
4. continue matched subgoal scheduling, backbone-conditioned action-value, triggered global re-retrieval, online trajectory compression and snapshot+semantic-selection+repair searches;
5. keep the frontier nonempty and preserve exact source/version/tested-scope caveats.

Do not read legacy `research_workers/reasoning/`, O, comparator, integrator, feed, other-worker state, shared execution ledger, or other-role receipts.
