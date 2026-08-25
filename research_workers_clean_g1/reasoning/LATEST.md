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

Read `STATE.md` for accumulated findings through 18:15 JST, then read the source-qualified checkpoints above in order for the newest evidence and exact continuation.

Top unresolved frontier:
1. learned heterogeneous Lean meta-action scheduling: fixed HILBERT/BFS-style thresholds vs a policy over keep-searching, repair, retrieval, decomposition/replan, preserve/backtrack and model escalation with identical available tools and real compute;
2. calibrated replan/action utility under search-policy and theorem-distribution shift: Brier/ECE/reliability/selective-risk for one-more-attempt vs repair/decompose/retrieve/replan/restart;
3. typed action preconditions in Lean: safely mask inapplicable/low-value actions using error class, progress, retrieval/context support, attempt history and remaining budget;
4. matched subgoal scheduling: ordered first-stuck focused parallelism vs hardest-branch routing vs independent parallelism vs total-work/tail-risk scheduling under equal model-token, Lean-execution and wall-clock budgets;
5. compressed online trajectory sufficiency: preserve LeanProgress/DT-Solver history value using Delta/progress/error/retrieval summaries without raw-history growth;
6. variable branching/search purchase: learn when greedy scheduling suffices and when MCTS/beam/semantic branching has positive marginal value;
7. coverage-aware routing: finite-sample/selective-risk abstention when compiler/retrieval/trajectory evidence is partial or OOD;
8. triggered global re-retrieval: learned escalation from failure-conditioned local retrieval to a fresh global proof-route sketch/retrieve/reflect cycle;
9. execution-substrate-aware cost models: generation, retrieval, Lean tactic/verifier/checking, snapshot/state reconstruction, downstream savings and wall-clock;
10. exact Lean composite of proof-state snapshot/forking + learned tactic/transition-semantic diversity + compiler-guided repair + typed/calibrated hierarchical routing under equal real compute;
11. benchmark-audited robustness with pinned Lean/mathlib/repository/harness versions and candidate/retrieval-access sensitivity.

Important updates from the newest checkpoints:
- BFS-Prover-V2's released code sharpens the replanning gap: planning and replanning are separate explicit modes, and the README exposes replanning as an optional operation when proof search is stuck. The paper uses current-subgoal budget exhaustion as the trigger. No learned/calibrated replan trigger was surfaced in the public implementation.
- HILBERT provides a strong direct Lean hierarchy: cheap prover attempts -> reasoner correctness check -> retrieval + verifier-guided shallow repair -> recursive decomposition/restart. It reaches 99.2% MiniF2F and 70.0% PutnamBench in its strongest published configuration, but its action switches use fixed retry/length/depth thresholds rather than learned marginal-value control.
- HILBERT retrieval is a downstream-compute saver in its tested MiniF2F configuration: Goedel-Prover retrieval changes 97.9% -> 99.2% while reducing average reasoner calls 862 -> 548 and reasoner tokens about 4.0M -> 2.3M. Retrieval cost should therefore be evaluated net of downstream savings.
- AlgoSkill supplies a program-synthesis precedent for a learned typed heterogeneous action scheduler with precondition masking, failure-history conditioning, verifier reward, local repair credit and entropy regularization. Its reported search benefit is not uniform, and the main CP-275 table is explicitly filtered to positive-gain backbones; treat it as transfer evidence, not Lean proof-search evidence.
- BFS-Prover-V2 still provides planner-guided ordered subgoals, focused parallelism and shared subgoal caching, but the 86.1% -> 95.08% planner headline is not a compute-matched controller ablation.
- `LeanProgress` remains direct future-cost evidence: ReProver Mathlib4 41.4% -> 45.2%, with proof-history prediction 75.8% exact-step accuracy / MAE 3.15 versus 61.8% / 5.22 without history.
- AlphaProof, MPS-Prover and DT-Solver jointly establish value/progress guidance, multiple perspectives and state-dependent branching; the remaining gap is calibrated allocation across *different action types* under real cost.
- `research_feedback_clean_g1/reasoning/FEEDBACK.json` remains absent; no sanitized feedback was consumed.

Exact continuation:
1. search direct Lean/formal-proof work for a learned heterogeneous meta-action policy choosing among repair, retrieval, decomposition/replan, preserve/backtrack and model escalation rather than only value-guided tactic selection;
2. inspect HILBERT and BFS-Prover-V2 code/configs for exact fixed thresholds and any adaptive switch logic, and recover a controller-only matched baseline if available;
3. search program-synthesis/verified-code follow-ups to AlgoSkill for contamination-controlled and compute-matched action-scheduling ablations, preserving transfer scope;
4. continue modern Lean value/progress calibration, OOD and selective-risk searches;
5. continue matched subgoal scheduling, triggered global re-retrieval, online trajectory compression and snapshot+semantic-selection+repair integration searches;
6. keep the frontier nonempty and preserve exact source/version/tested-scope caveats.

Do not read legacy `research_workers/reasoning/`, O, comparator, integrator, feed, other-worker state, shared execution ledger, or other-role receipts.
