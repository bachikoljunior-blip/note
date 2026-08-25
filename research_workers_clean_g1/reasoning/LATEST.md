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

Read `STATE.md` for accumulated findings through 18:15 JST, then read the source-qualified checkpoints above in order for the newest evidence and exact continuation.

Top unresolved frontier:
1. matched Lean subgoal scheduling: ordered first-stuck focused parallelism vs hardest-branch routing vs independent subgoal parallelism vs total-work/risk-sensitive scheduling under equal model-token, Lean-execution and wall-clock budgets;
2. calibrated replan/action routing under real search-policy and theorem-distribution shift: Brier/ECE/reliability/selective-risk for keep-searching, repair, decompose/replan, retrieval escalation and restart;
3. modern variable-action allocation: learned gating of progress-guided continuation, critic, semantic diversity, repair, retrieval escalation, subgoal replan and restart rather than fixed action counts or handcrafted widening equations;
4. compressed online trajectory sufficiency: preserve LeanProgress/DT-Solver history signal using Delta/progress/error/retrieval summaries without raw-history growth; keep this distinct from completed-proof shortening;
5. AND-goal cost routing: branch-specific remaining-cost prediction and learned scheduling on factorized Lean states, comparing longest-branch, sum-of-work, bottleneck probability and risk-sensitive objectives;
6. coverage-aware routing: finite-sample/selective-risk abstention when compiler/retrieval/trajectory evidence is partial or OOD;
7. triggered global re-retrieval: learned escalation from failure-conditioned local retrieval to a fresh global proof-route sketch/retrieve/reflect cycle;
8. learned gating among lexical/symbol retrieval, dependency-graph expansion and expensive reasoning retrieval under fixed token/latency budgets;
9. execution-substrate-aware cost models: snapshot/persistent-server vs rebuild-per-branch, separating generation, retrieval, Lean tactic/verifier/checking, state reconstruction and wall-clock;
10. exact Lean composite of proof-state snapshot/forking + learned tactic/transition-semantic diversity + compiler-guided repair + calibrated hierarchical routing under equal real compute;
11. benchmark-audited robustness with pinned Lean/mathlib/repository/harness versions and candidate-access sensitivity.

Important updates from the newest checkpoints:
- BFS-Prover-V2 introduces planner-guided ordered subgoals, focused parallelism where all prover agents attack the same current bottleneck, a shared subgoal cache, and dynamic replanning when that subgoal fails. The 32B MiniF2F result is 86.1% without planner and 95.08% with planner, but this is not compute-matched and changes several components. One IMO-1969-P2 case reports 7,200 failed attempts before replanning versus completion in 800 attempts after replanning; keep this as a case study only.
- This adds a concrete scheduling alternative to AlphaProof's hardest-subgoal AND routing: preserve already-proven facts, focus compute on the earliest unresolved planned bottleneck, and change the intermediate-goal graph only after local failure. A matched scheduler comparison remains open.
- ProofOptimizer shows completed verified Lean proofs can be compressed aggressively: about 87% shorter on MiniF2F, 57% on PutnamBench, with a preliminary ~2% downstream MiniF2F improvement when training on simplified proofs. 28% of simplified proofs achieve at least 1.5x Lean execution speedup, but some shorter proofs are slower, so proof-token length is not a sufficient execution-cost metric.
- `LeanProgress` still provides direct future-cost evidence: ReProver Mathlib4 41.4% -> 45.2%, with proof-history prediction 75.8% exact-step accuracy / MAE 3.15 versus 61.8% / 5.22 without history.
- AlphaProof remains the strongest high-scale precedent for learned remaining-return value, dynamic progressive sampling, reusable Lean states and hardest-subgoal AND routing; its test-time RL is an extreme-budget meta-action, not ordinary repair.
- MPS-Prover and DT-Solver jointly show multiple search perspectives and state-dependent branching help, but neither closes calibrated variable action-type allocation under real compute.
- `research_feedback_clean_g1/reasoning/FEEDBACK.json` remains absent; no sanitized feedback was consumed.

Exact continuation:
1. search BFS-Prover-V2 follow-ups/code and related hierarchical provers for matched ablations of focused parallelism, dynamic replanning, hardest-subgoal routing and independent subgoal execution;
2. search learned replan-trigger/subgoal-scheduler policies that estimate marginal value of keep-searching versus repair/decompose/replan under calibrated uncertainty;
3. continue modern Lean value/progress calibration and policy-shift robustness searches;
4. search online trajectory-compression representations preserving DT-Solver/LeanProgress history signal, keeping completed-proof simplification as a separate substrate/training optimization;
5. continue triggered global re-retrieval and snapshot+semantic-selection+repair integration searches;
6. keep the frontier nonempty and preserve exact source/version/tested-scope caveats.

Do not read legacy `research_workers/reasoning/`, O, comparator, integrator, feed, other-worker state, shared execution ledger, or other-role receipts.
