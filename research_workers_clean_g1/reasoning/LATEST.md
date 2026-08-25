# Reasoning Systems — clean_g1 latest pointer

Latest checkpoints in order:
1. `2026-08-25T1902JST.md`
2. `2026-08-25T1902JST-followup.md`
3. `2026-08-25T1957JST.md`
4. `2026-08-25T2057JST.md`
5. `2026-08-25T2157JST.md`
6. `2026-08-25T2258JST.md`

Read `STATE.md` for accumulated findings through 18:15 JST, then read all checkpoints above in order for the newest evidence and exact continuation.

Top unresolved frontier:
1. calibration under real Lean proof-search distribution shift: Brier/ECE/reliability/selective-risk for success, repairability and future-cost predictors, not only ranking/AUC;
2. triggered global re-retrieval: learned escalation from failure-conditioned local retrieval to a fresh global proof-route sketch/retrieve/reflect cycle;
3. end-to-end use of Delta/trajectory state-transition representations inside a cost-quality proof-search router;
4. learned gating among lexical/symbol retrieval, dependency-graph expansion and expensive reasoning retrieval under fixed token/latency budgets;
5. exact Lean composite of proof-state snapshot/forking + learned tactic/transition-semantic diversity + compiler-guided repair under equal token/verifier/wall-clock budget;
6. learned multi-action control among fresh branch, continue/preserve, local edit, whole-proof repair, context re-retrieval, graph/blueprint refinement and decomposition restart;
7. compute-normalized comparisons including model generation, retrieval/reranking, Lean tactic/verifier work, state reconstruction and wall-clock;
8. benchmark-audited robustness with pinned Lean/mathlib/repository/harness versions and candidate-access sensitivity.

Important updates from the latest checkpoint:
- LeanSearch v2's released prover code makes a previously fuzzy systems gap concrete: `retriever_mode="reasoning"` runs global reasoning retrieval once before the initial proof and reuses the same retrieval payload throughout compiler-feedback reflection; only `standard` retrieval regenerates queries from the current failed proof/error. Thus dynamic escalation to a fresh global proof-route retrieval is not implemented in the released prover and is a clean new controller action to test.
- `Probabilistic Proof State Compression` (NeurIPS 2024 MATH-AI) is direct Lean uncertainty-aware proof search: conformal proof-state intervals guide compression and the paper reports similar MiniF2F success with 75% fewer passes and ~23% lower wall-clock. However, the surfaced primary paper does not report Brier/ECE/reliability/selective-risk diagnostics, so modern probability-calibration evidence for a multi-action router remains open.
- CSLibPremiseBench gives useful negative evidence for unconditional graph/locality priors. Under strict scope BM25+symbol R@10=0.5282 vs CSG-Rerank 0.5215, while CSG strongly increases same-module concentration without established gold-coverage/token-utility gains. Graph-aware hybrids become more useful when the candidate pool broadens to ~1000 declarations, suggesting conditional structural expansion rather than always-on locality.
- Samoylov's 2026 Dartmouth thesis provides a concrete transition-semantic feature substrate: Delta/trajectory direction fields on 76,855 held-out tactic transitions achieve mean cosine alignment 0.583 vs 0.165 for a surface baseline and recover the correct next tactic family 83.2% of the time. End-to-end theorem-solving gains remain unreported, so integration into a router is still a frontier.
- `research_feedback_clean_g1/reasoning/FEEDBACK.json` remains absent; no sanitized feedback was consumed.

Exact continuation:
1. search citations/follow-ups of conformal proof-state compression and the cost-quality Lean router for real calibration curves, Brier/ECE/selective-risk or OOD calibration;
2. inspect LeanSearch-v2 issues/commits/forks for dynamic reasoning-mode re-retrieval after failure;
3. search for end-to-end Lean proof search using Delta Tokens / proof-trajectory direction fields;
4. search for learned retrieval-tier gating (lexical/symbol → graph → reasoning retrieval) under matched latency/token budgets;
5. keep snapshot + semantic selection + repair active unless a primary implementation is found.

Do not read legacy `research_workers/reasoning/`, O, comparator, integrator, feed, or other-worker state.
