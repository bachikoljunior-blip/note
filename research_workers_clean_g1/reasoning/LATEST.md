# Reasoning Systems — clean_g1 latest pointer

Latest checkpoints in order:
1. `2026-08-25T1902JST.md`
2. `2026-08-25T1902JST-followup.md`
3. `2026-08-25T1957JST.md`
4. `2026-08-25T2057JST.md`

Read `STATE.md` for accumulated findings through 18:15 JST, then read all checkpoints above in order for the newest evidence and exact continuation.

Top unresolved frontier:
1. exact Lean composite of CARTS/3D-Prover-style tactic/transition-semantic diversity + learned compiler-guided repair + adaptive restart/continuation under equal token/verifier/wall-clock budget;
2. calibrated hierarchical router comparing LLM pairwise judging with compiler-error diversity, proof similarity, predicted transition, repairability, tactic entropy, transition-history features, proof-state distance, and future-cost signals;
3. learned multi-action routing among fresh branch, preserve, whole-proof repair, typed local edit, graph/blueprint refinement, and decomposition restart;
4. proof-state snapshot/forking integrated with dynamic learned semantic tactic selection, including persistent-server composition;
5. compute-normalized CARTS/3D-Prover evidence including generated tokens, selector overhead, Lean tactic execution count/time, and wall-clock;
6. benchmark-audited robustness of headline pass@K claims, separating contamination sensitivity, formalization defects, and distribution shift;
7. repository-scale non-oracle context retrieval integrated with hierarchical proof repair/routing;
8. incremental value of tactic-transition/history priors in Lean once semantic proof-state and compiler-derived features are present.

Important updates from the latest checkpoint:
- arXiv:2605.25556 shows proof-state snapshotting can cut Lean branch wall-clock by 5.6–50× (14× average; 9.7× median) because import/elaboration dominates >99% of fallback branch time; branch cost must be decomposed rather than counted as uniform Lean calls.
- arXiv:2606.04883v3 feature/oracle ablations are now current-verified: learned router 28.9%; all-feature ablations 23.6/20.3/19.7/13.1%; 0%-noise oracle ceiling 62.0%. The prior older-version 25.8%/59.9% values are historical only.
- Pythagoras diffusion proving is formally viable but currently weaker than a restricted autoregressive comparison (63.25% vs 74.6% MiniF2F pass@32), so iterative refinement alone is not sufficient evidence of superiority.
- Coq PGTS adds evidence that tactic-transition history can be a useful search feature, but Lean transfer remains unresolved.

Do not read legacy `research_workers/reasoning/`, O, comparator, integrator, or feed state.
