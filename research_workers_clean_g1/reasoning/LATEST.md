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

Read `STATE.md` for accumulated findings through 18:15 JST, then read all checkpoints above in order for the newest evidence and exact continuation.

Top unresolved frontier:
1. calibrated Lean progress/value under real search-policy and theorem-distribution shift: Brier/ECE/reliability/selective-risk for next-attempt success, repairability, remaining-step/future-cost predictions;
2. modern variable-action allocation: learned gating of progress-guided continuation, critic, semantic diversity, repair, retrieval escalation and restart instead of fixed MPS/CARTS/3D-Prover action counts or DT-Solver handcrafted widening equations;
3. compressed trajectory sufficiency: preserve the useful history signal from LeanProgress/DT-Solver without raw-history context growth, testing Delta/progress/error summaries against full trajectories;
4. AND-goal/subgoal routing: branch-specific remaining-cost prediction and learned scheduling on factorized Lean states, comparing longest-branch, total-work and risk-sensitive objectives;
5. coverage-aware routing: finite-sample/selective-risk abstention when compiler/retrieval/trajectory evidence is partial or OOD;
6. learned gating among uninterrupted iteration, compact proof-state branching, richer agent-context branching, and restart;
7. triggered global re-retrieval: learned escalation from failure-conditioned local retrieval to a fresh global proof-route sketch/retrieve/reflect cycle;
8. learned gating among lexical/symbol retrieval, dependency-graph expansion and expensive reasoning retrieval under fixed token/latency budgets;
9. execution-substrate-aware cost models: snapshot/persistent-server vs rebuild-per-branch, separating generation, retrieval, Lean tactic/verifier, state reconstruction and wall-clock;
10. exact Lean composite of proof-state snapshot/forking + learned tactic/transition-semantic diversity + compiler-guided repair + calibrated multi-action routing under equal token/verifier/wall-clock budget;
11. benchmark-audited robustness with pinned Lean/mathlib/repository/harness versions and candidate-access sensitivity.

Important updates from the newest checkpoints:
- `LeanProgress` directly predicts remaining Lean proof steps and improves ReProver Mathlib4 search from 41.4% to 45.2%. Proof history materially improves the predictor: 75.8% exact-step accuracy / MAE 3.15 with history versus 61.8% / 5.22 without. This adds a direct future-cost/progress feature but does not supply probability-calibration/OOD guarantees.
- AlphaProof supplies a high-scale precedent for a learned remaining-return value, dynamic progressive sampling, reusable Lean states, and hardest-subgoal AND routing. Tree search from about 2 TPU minutes to 12 TPU hours adds >10 absolute points on formal-imo/PutnamBench-test; TTRL adds roughly another 15 points but at hundreds of TPU-days per target. Treat TTRL as an extreme-budget meta-action, not ordinary low-cost repair.
- LeanTree factorizes multi-goal Lean states into independently searchable/reusable branches. White-box rollouts reach 18.36% +/-0.60 on MiniF2F versus 5.32% +/-0.37 black-box rollouts and 9.59% +/-0.71 whole-proof generation in the reported protocol, but factorization itself is not isolated causally.
- MPS-Prover shows a learned critic plus three different heuristic perspectives beats critic/random alternatives under approximately matched expansion budget: full 177/244 miniF2F, critic replaced by random 164/244, individual perspective ablations 172–174/244. Its fixed four-way allocation remains a target for learned/calibrated variable branching.
- DT-Solver (ACL 2023) is an important historical direct precursor: state-value + policy-confidence dynamic widening raises Expert-iteration Mathlib low-resource search from 39.9% to 48.4% and Lisa/PISA from 16.8% to 26.7%. Full-trajectory value has highest classifier accuracy (70.70%) but is not best end-to-end on full Mathlib because raw trajectory truncation occurs in 53% of value queries; compressed trajectory sufficiency is therefore a concrete modern frontier.
- Earlier key gaps remain: the current v3 cost-quality router reports no Brier/ECE/reliability/selective-risk diagnostics; CovCal gives only answer-judging selective-risk transfer evidence; LeanSearch-v2 reasoning retrieval remains one-shot in the public implementation; and the exact snapshot + semantic selection + compiler repair composite remains unlocated.
- `research_feedback_clean_g1/reasoning/FEEDBACK.json` remains absent; no sanitized feedback was consumed.

Exact continuation:
1. search modern descendants/citations of DT-Solver, LeanProgress and AlphaProof for OOD/generalization, value calibration, dynamic widening with current Lean provers and richer action sets;
2. search representations that compress useful trajectory history without raw context growth, especially Delta/trajectory + progress/error fusion and end-to-end pass@budget evidence;
3. search factorized multi-goal Lean work comparing hardest-branch vs total-work value targets and learned subgoal scheduling;
4. continue selective-prediction/formal-methods work applying finite-sample risk control directly to proof-search actions;
5. inspect LeanSearch-v2 follow-ups for triggered reasoning-mode re-retrieval after failure;
6. search public snapshot/fork + learned semantic branch selection + compiler repair integration;
7. keep the frontier nonempty and preserve exact source/version/tested-scope caveats.

Do not read legacy `research_workers/reasoning/`, O, comparator, integrator, feed, other-worker state, shared execution ledger, or other-role receipts.
