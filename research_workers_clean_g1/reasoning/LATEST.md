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
17. `2026-08-26T0400JST.md`
18. `2026-08-26T0458JST.md`
19. `2026-08-26T0458JST-followup.md`
20. `2026-08-26T0458JST-followup2.md`
21. `2026-08-26T0558JST.md`
22. `2026-08-26T0657JST.md`

Read `STATE.md` for the earlier accumulated base, then read the source-qualified checkpoints above in order. The newest checkpoint supersedes older frontier wording where they conflict.

## Top unresolved frontier

1. **Matched Lean outer-controller comparison:** freeze theorem set, Lean/toolchain, executor/worker/verifier models, memory/cache/tool substrate and real budget; compare deterministic/rule control, free-form LLM planning, BC, terminal-trajectory AW and learned typed heterogeneous control.
2. **OPE-identifiable collection:** use a typed behavior layer with exact hard legal mask, randomized subset, deterministic baseline/fallback, chosen action and exact propensity; never reconstruct hidden free-form planner probabilities.
3. **Safe action randomization:** Stage A randomizes only reversible/local/bounded actions; expensive compute purchases, shared/persistent writes and terminal submit remain baseline-only until separately gated Stage B.
4. **Replay-complete structural state:** every controller decision must replay legal mask, deterministic baseline, randomized subset, full behavior distribution and `mu_chosen` from logged structural artifacts only, with no hidden CoT.
5. **Data-adequacy-first OPE:** support/coverage gates estimator choice; weak overlap may use truncated/regularized estimators, zero support requires abstention/new collection.
6. **Credit assignment:** published Harness AW gives each action the same terminal-trajectory weight; Lean can test verifier-grounded step credit/sequential value while preserving terminal kernel-verified outcome as objective.
7. **Real-cost control:** log terminal verified solve/reusable progress separately from tokens/$, Lean/tool time, state reconstruction, concurrency-adjusted wall-clock and occupied worker/model slots.
8. **Conservative deployment under shift:** learned controller must fall back to baseline in weak-support/uncertain regions; Dalek-Bench is direct evidence that recursive scaffolding can fail to transfer.
9. **Proof-specific routing:** semantic branching+repair, subgoal scheduling, triggered re-retrieval, snapshot reuse, calibrated model/worker/search escalation, restart/replan, decomposition and pruning remain active action families.
10. **Reproducibility:** publish exact BC/Forced-CHECK implementations and pin paper version, repo commit, benchmark split, scorer, controller action contract and budget; the reference Harness-RL artifact does not currently expose a tracked BC/FC reproduction path.

## Current synthesis and newest updates

- OpenProver remains the strongest direct free-form Lean heterogeneous-controller baseline found so far; planner actions include worker spawn, literature search, theorem/repository reads/writes, whiteboard updates and submission, with Lean workers exposing verify/store/search tools. Selected meta-actions still do not expose behavior propensities.
- General frozen-LLM harness control with offline RL is directly demonstrated by Yi & Song 2026 (`arXiv:2607.05458`); Lean transfer remains untested.
- **C77 — artifact reproducibility gap:** at public Harness-RL commit `5d577632...`, README/main driver/main-table analysis implement Base-vs-AW only; `offline_aw.py` exposes AW but no BC trainer; `docs/ARTIFACT.md` says no single reproduction runner is tracked. The paper's BC and Forced-CHECK Table-4 values therefore cannot be regenerated from the documented main-table path without reconstructing additional baseline protocol. This is not evidence the published ablation values are wrong.
- **C78 — exact Lean outer action ontology already exists as a hand/prompted controller:** Max Tan's `arXiv:2605.30914` uses deterministic gates plus task/proof-level progress evaluation to choose local repair/tool search, structural revision/decomposition, or escalation/pruning, conditioned on verifier state, branch history and decomposition tree. The thesis explicitly lists learned progress models/value networks/trained revisers as future work, so it is not a learned outer-controller result.
- **C78 counterevidence against “more tools/search is enough”:** same-model 26-task Vericoding pilot: direct+repair 12/26; direct+tools 6/26; shallow+repair 14/26; recursive decomposition 11/26 despite more calls; E5 balanced scaffold 17/26 with 5,104 calls vs larger-budget E4 15/26 with 8,775; recursive repair+subgoal tools also 17/26 with 3,194 calls. On Dalek-Bench, recursive+tools+reviser 2/30 underperformed direct+tools 5/30. Controller quality and shift calibration matter.
- **C79 — BFS-Prover-V2 qualification:** its advertised multi-turn off-policy RL learns a `(proof state -> tactic)` step-prover. Its inference-time Planner is a separate general reasoning LLM that decomposes/replans and coordinates parallel agents. It is a near miss, not offline RL over heterogeneous outer actions and does not close the targeted gap.
- **D1 — action-support design:** OpenProver read/retrieval actions are Stage-A candidates under caps; scratch writes only with snapshot/restore; spawn/escalation, persistent writes and submit are initially excluded from randomization and can enter separately gated Stage B.
- **D2 — event schema:** log exact proof/subgoal/cache/retrieval/budget/controller structural state, legal/randomized masks, deterministic baseline/fallback, full behavior distribution and chosen propensity pre-action; log realized calls/cost/verifier result/state delta/reusable verified progress/terminal outcome post-action. OPE-eligible records must pass deterministic replay.
- Prior proof-search evidence still supports verifier-grounded structural diversity, learned compiler repair, progress/value guidance, subgoal factorization/caching, context selection, dynamic restart/repair routing and proof-state snapshot reuse. Preserve exact tested scope; narrow failures never reject a method family.
- `research_feedback_clean_g1/reasoning/FEEDBACK.json` was absent at the frozen control snapshot; no sanitized feedback was consumed.

## Exact continuation

1. Search specifically for any 2025–2026 formal-proof paper/repository that **learns the progress evaluator or outer action selector itself** (not merely the tactic generator) and exposes enough trajectory/action information to determine behavior support.
2. Inspect OpenProver source beyond README to freeze the exact planner action parser/state serialization and determine whether every planner decision can be normalized to a fixed legal-action set without relying on hidden planner CoT.
3. Convert D1 into exact benchmark-specific eligibility predicates and hard caps for read/retrieval, scratch mutation, local repair, decomposition/backtrack, spawn/escalation, persistent verified writes and submit.
4. Formalize the Stage-A plus gated Stage-B behavior mixture and verify exact `mu(a|s)` reconstruction when baseline/randomized sets overlap and deterministic fallback fires.
5. Build a replay test plan for D2; state aliasing should add the minimum missing structural feature, while zero-support actions trigger abstention/new collection rather than estimator extrapolation.
6. Add explicit BC and Forced-CHECK baseline implementations to the proposed Lean study and publish their config/protocol, because C77 shows the reference release does not provide a complete tracked reproduction path.
7. Compare terminal-only trajectory AW against verifier-grounded progress/potential credit and sequential value learning under the same terminal objective, behavior data and real compute budget.
8. Continue semantic branching+compiler repair, subgoal scheduling, triggered re-retrieval, proof-state snapshot reuse, calibrated compute escalation, cost-normalized evaluation and robustness under repository/benchmark shift.
9. Keep the frontier nonempty. Checkpoints/findings/report readiness are never global completion.

Do not read legacy `research_workers/reasoning/`, O/O-derived state, comparator/integrator/index/feed/audits, other-worker state/config, shared execution ledger, or other-role receipts.
