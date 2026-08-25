# Reasoning Systems — clean_g1 latest pointer

Latest checkpoints in order:
1. `2026-08-25T1902JST.md`
2. `2026-08-25T1902JST-followup.md`
3. `2026-08-25T1957JST.md`
4. `2026-08-25T2057JST.md`
5. `2026-08-25T2157JST.md`

Read `STATE.md` for accumulated findings through 18:15 JST, then read all checkpoints above in order for the newest evidence and exact continuation.

Top unresolved frontier:
1. exact Lean composite of proof-state snapshot/forking + CARTS/3D-Prover-style learned tactic/transition-semantic diversity + compiler-guided repair under equal token/verifier/wall-clock budget;
2. calibrated hierarchical router with real probability-calibration evidence (Brier/ECE/reliability/selective prediction) for success, repairability and future cost, compared against LLM pairwise judging;
3. context as an explicit action: reuse current context vs graph-first expansion vs global premise re-retrieval vs proof-route change vs repair/restart;
4. learned multi-action control among fresh branch, preserve, local edit, whole-proof repair, context re-retrieval, graph/blueprint refinement and decomposition restart;
5. proof-state snapshot/forking integrated with dynamic learned semantic tactic selection, including persistent-server composition;
6. compute-normalized comparisons including generated tokens/model calls, retrieval/reranking overhead, Lean tactic/verifier work, state reconstruction and wall-clock;
7. failure attribution at multiple scopes (tactic/premise/local lemma/decomposition/global route) before choosing repair granularity;
8. benchmark-audited robustness with pinned Lean/mathlib/harness versions and mutated/audited variants;
9. execution-guided program-repair systems with actual calibration curves and search-vs-repair component ablations before cross-domain transfer.

Important updates from the latest checkpoint:
- LeanSearch v2 (arXiv:2605.13137v2) provides strong evidence for proof-strategy-scale context retrieval: on FATE-H, no retrieval / standard retrieval / reasoning retrieval solves 4% / 14% / 20% with the same Sonnet prover; the ordering remains 1% / 8% / 12% with Kimi. Its reflection ablation improves 16%→20% with other components fixed, supporting context/proof-route revision as a distinct action.
- TheoremGraph/LeanGraph (arXiv:2606.25363) extracts 388,105 Lean declarations and 11.3M typed edges across 25 projects; name+signature plus graph expansion reaches Recall@10 0.775 vs LeanSearch v2 reranked 0.780 on formal concept retrieval without an LM reranker. End-to-end proof impact remains untested.
- VeriSpecGen (arXiv:2604.10392) adds same-ITP evidence for failure attribution before repair: atomic requirements + traceability maps localize failed validation to contract clauses, enabling targeted repair; VERINA SpecGen reaches 86.6%, with trajectory training gains also reported. Do not transfer the score to theorem proving.
- Citation-forward search still did not locate a public primary implementation combining the snapshot paper's state forking with learned semantic tactic selection; this remains a real systems-composition gap.
- CodePilot's execution-guided MCTS + “confidence-calibrated” repair is retained only as a lead because the surfaced primary source did not expose calibration metrics or enough component ablations.

Do not read legacy `research_workers/reasoning/`, O, comparator, integrator, feed, or other-worker state.
