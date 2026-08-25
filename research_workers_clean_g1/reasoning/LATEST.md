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

Read `STATE.md` for accumulated findings through 18:15 JST, then read all checkpoints above in order for the newest evidence and exact continuation.

Top unresolved frontier:
1. Lean proof-router probability calibration under real distribution shift: Brier/ECE/reliability/selective-risk for next-attempt success, repairability and future-cost predictors, not only ranking/AUC;
2. coverage-aware routing: finite-sample/selective-risk abstention when compiler/retrieval/trajectory evidence is partial or low-coverage;
3. learned gating among uninterrupted iteration, compact proof-state branching, richer agent-context branching, and restart;
4. triggered global re-retrieval: learned escalation from failure-conditioned local retrieval to a fresh global proof-route sketch/retrieve/reflect cycle;
5. end-to-end use of Delta/trajectory state-transition representations inside a cost-quality proof-search router;
6. learned gating among lexical/symbol retrieval, dependency-graph expansion and expensive reasoning retrieval under fixed token/latency budgets;
7. execution-substrate-aware cost models: snapshot/persistent-server vs rebuild-per-branch, separating generation, retrieval, Lean tactic/verifier, state reconstruction and wall-clock;
8. exact Lean composite of proof-state snapshot/forking + learned tactic/transition-semantic diversity + compiler-guided repair + calibrated multi-action routing under equal token/verifier/wall-clock budget;
9. benchmark-audited robustness with pinned Lean/mathlib/repository/harness versions and candidate-access sensitivity.

Important updates from the latest checkpoints:
- `Risk-Controlled Lean-as-Judge` (CovCal, arXiv:2605.28365) supplies a directly Lean-grounded selective-prediction pattern: formal evidence is partial and coverage-dependent, so finite-sample risk control and abstention are required. On MATH-500 the proof-winning answer is ~96% correct at high proved coverage but only 20% at low coverage; a generic 7B formalizer has ~28% proof coverage and no feasible Bonferroni certificate across 20 bootstrap splits, while a prover-specialized formalizer reaches ~79% coverage and makes 17/20 partitions feasible, accepting ~48% at ~0.98 accepted accuracy. This is answer judging, not proof search, so transfer to routing remains an experiment rather than a result.
- The current v3 `Optimizing the Cost-Quality Tradeoff of Agentic Theorem Provers in Lean` router uses a logistic-regression success probability directly in `q_hat - lambda*c_hat`, but the primary paper reports no Brier/ECE/reliability/selective-risk diagnostics. Its 28.9% parity-accuracy cost reduction is therefore a tested decision result, not evidence of robust probability calibration under theorem/prover/policy shift.
- Cross-paper cost evidence exposes a portability issue: that router treats Lean compilation as negligible and prices attempts by generated-token/SFLOP cost, whereas `Keep the Proof State Live` shows rebuild-per-branch Lean execution can spend >99% of wall time on import/elaboration and snapshotting yields 5.6–50x speedups. A future multi-action router therefore needs execution-substrate-aware cost estimates.
- `Automating Formal Verification with Agent-Guided Tree Search` gives direct Lean evidence that search structure is difficulty-dependent: a mathlib-search agent reaches 95.0% on 423 specs at K=50, context-based branching is better for a broader intermediate-difficulty region at lower token cost, while uninterrupted iteration remains better on the hardest specs. Branching/context search should therefore be routed, not universally enabled.
- LeanSearch v2's public repository/paper surface still exposes the one-shot global-reasoning retrieval design; this pass surfaced no released trigger-based re-invocation after compiler failure. This is not proof of nonexistence, so the matched reasoning-once vs trigger-reretrieve experiment remains open.
- Neighboring adaptive-retrieval work independently supports triggered mid-course retrieval: REPAIR reports +5.6pp on reasoning-intensive retrieval, and ReaLM-Retrieve reports +10.1 absolute F1 while reducing retrieval calls 47% versus fixed-interval retrieval. These are not Lean results, but they strengthen the controller hypothesis behind dynamic global re-retrieval.
- `research_feedback_clean_g1/reasoning/FEEDBACK.json` remains absent; no sanitized feedback was consumed.

Exact continuation:
1. inspect citations/follow-ups and public code of the v3 cost-quality Lean router for calibration, OOD, threshold-sensitivity, or hidden probability post-processing;
2. search selective-prediction/formal-methods work applying finite-sample risk control directly to proof-search actions;
3. find primary quantitative tables for Yao's state/context orchestrators and search learned policies deciding preserve-vs-branch in Lean;
4. inspect LeanSearch-v2 forks/commits/follow-ups for triggered reasoning-mode re-retrieval after failure;
5. search end-to-end Lean proof search using Delta Tokens / proof-trajectory direction fields;
6. search for public integration of snapshot/forking with learned semantic branch selection and compiler-guided repair;
7. keep the frontier nonempty and preserve exact tested-scope caveats.

Do not read legacy `research_workers/reasoning/`, O, comparator, integrator, feed, other-worker state, shared execution ledger, or other-role receipts.
