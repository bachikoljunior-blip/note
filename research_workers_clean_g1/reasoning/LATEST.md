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

Read `STATE.md` for the earlier accumulated base, then read the source-qualified checkpoints above in order. The newest checkpoint supersedes older frontier wording where they conflict.

## Top unresolved frontier

1. **Matched Lean controller comparison:** freeze theorem set, Lean/toolchain, executor/worker/verifier models, memory/cache/tool substrate and real budget; compare deterministic/rule control, free-form LLM planning and learned typed heterogeneous control.
2. **OPE-identifiable collection:** use a typed behavior layer with exact legal mask, randomized subset, deterministic baseline/fallback, chosen action and exact propensity; never rely on reconstructing hidden free-form planner probabilities.
3. **Safe action randomization:** Stage A randomizes only reversible/bounded actions; terminal/destructive/unbounded-expensive actions remain baseline-only until a separately bounded Stage-B exploration protocol is justified.
4. **Data-adequacy-first OPE:** support/coverage gates estimator choice; weak overlap may use truncated/regularized estimators, zero-support requires abstention/new collection.
5. **Credit assignment:** published harness AW gives every action the same terminal-trajectory weight; Lean can test verifier-grounded step credit while keeping terminal kernel-verified outcome as the objective.
6. **Real-cost control:** log terminal verified solve/reusable progress separately from tokens/$, Lean/tool time, state reconstruction, concurrency-adjusted wall-clock and occupied worker/model slots.
7. **Compact state sufficiency:** structural logged state only, no unlogged hidden CoT; detect state aliasing and add only the minimum feature needed.
8. **Conservative deployment:** learned controller falls back to baseline in weak-support/uncertain regions under verifier-enforced hard masks.
9. **Proof-specific routing:** semantic branching+repair, subgoal scheduling, triggered re-retrieval, snapshot reuse, calibrated model/worker/search escalation and restart/replan remain active branches.
10. **Reproducibility:** distinguish final paper protocol from quick artifact commands and pin paper version, repo commit, benchmark split, scorer and budget.

## Current synthesis and newest updates

- OpenProver remains the strongest direct free-form Lean heterogeneous-controller baseline found so far; it exposes planner actions and rich worker/verifier/tool artifacts, but selected meta-actions do not expose behavior propensities.
- General frozen-LLM harness control with offline RL is directly demonstrated by Yi & Song 2026 (`arXiv:2607.05458`). This closes the broad “can an outer harness policy be learned?” gap; Lean transfer remains untested.
- **C73 — exact ablation/protocol qualification:** paper Table 4 reports AW/BC/Forced-CHECK lift (pp) respectively: knowledge-work `+1.4/-0.4/+0.1`, coding `+10.0/-8.3/+0.0`, research `-0.3/-4.2/-0.2`, multi-tool `-1.3/-6.8/+0.3`, long-memory `-0.3/-5.8/+0.0`, planning `+2.6/+0.0/-2.3`, adapted tau-bench retail `+18.2/+8.2/+0.1`, adapted DB-Bench `+13.2/+5.8/-0.5`. AW beats BC in all eight but Forced CHECK only in five; verification frequency is therefore a process diagnostic, not sufficient reward. Final adapter rows use 16 train / 20 held-out tasks and adapted scoring, not official upstream scores.
- **C73 reproducibility warning:** current public README still shows four explicit held-out IDs for each adapter, matching the paper's reference to an earlier four-task estimate rather than the final 20-task result. Do not assume the quick README command reproduces the final paper row without reconstructing the final split/config.
- **C74 — reward-objective resolution:** release code computes a rich rubric/verifier/format/task/error/cost/early-submit aggregate, but `running_main_driver.py` sets `return_G = rubric_score_norm`, and `offline_aw.py` trains from that terminal rubric return. The published AW policy is not directly cost-aware despite cost diagnostics existing in the harness.
- **C74 training details:** per-task advantage `G_i - mean_task_G`; trajectory weight `clip(exp(A/beta),0.1,10)` with beta=0.2; every step in the trajectory inherits the same weight; 64-hidden-unit MLP, Adam 1e-3, 20 epochs, batch 256, entropy coefficient 0.01.
- **C75 — exact behavior propensity:** released epsilon-perturbed Base policy selects uniformly among legal actions with probability epsilon (default 0.25), otherwise deterministic Base. For legal-set size L and legal Base action b: `mu(b|s)=1-eps+eps/L`, other legal actions `eps/L`, masked actions 0. However the ordinary trajectory records do not make mask/base/epsilon/full propensity vector first-class logged fields; Lean should log them explicitly.
- **C75 safe generalization:** choose deterministic legal baseline `b(s)` plus a separately defined randomized subset `R(s)`. Use `mu(a|s)=(1-eps)1[a=b]+eps/|R| 1[a in R]` when `R` is nonempty, else deterministic baseline. This remains exact even when the baseline action is terminal/baseline-only and not in the randomized subset.
- **C76 — targeted absence:** targeted public search found AlphaProof tactic-level RL, OpenProver free-form outer planning, and MerLean-Prover hand-designed recursive outer control with no custom RL, but no public Lean outer-loop offline-RL heterogeneous meta-controller with logged meta-action propensities. This is a search gap, not a nonexistence claim.
- Prior proof-search evidence still supports verifier-grounded structural diversity, learned compiler repair, progress/value guidance, subgoal factorization/caching, context selection, dynamic restart/repair routing and proof-state snapshot reuse. Preserve exact tested scope; narrow failures never reject a method family.
- `research_feedback_clean_g1/reasoning/FEEDBACK.json` was absent at the current control snapshot; no sanitized feedback was consumed.

## Exact continuation

1. Find the explicit artifact path/script that reproduces Behavior Cloning and Forced CHECK; paper values are verified, but the tracked reproduction entry point remains unidentified in the inspected README/main driver.
2. Convert the safe mixture into an OpenProver/Lean action eligibility matrix: reversible-local, bounded epistemic, expensive-but-reversible, write/mutation, terminal; specify which classes enter Stage-A randomization.
3. Define a replay-complete compact controller state and event schema containing proof/subgoal snapshot id, progress/value summary, latest compiler result/error class, verified cache/DAG delta, retrieval state, real cost/budget vector, model/worker tier, previous meta-action, baseline version, legal/randomized masks and exact propensity.
4. Test deterministic replay: every logged controller decision must reproduce its mask, baseline, probability vector and selected-action propensity from logged artifacts only; add the minimum missing state when it fails.
5. Search specifically for formal-proof outer-loop RL/OPE choosing among planner/retrieval/repair/restart/escalation actions rather than tactics.
6. Compare terminal-only trajectory AW with verifier-grounded potential/progress credit and sequential value learning under the same terminal objective and same behavior data.
7. Continue data-coverage/OPE estimator work, baseline-bootstrap deployment, mid-trajectory compute purchase, semantic branching+repair, subgoal scheduling, triggered re-retrieval, snapshot reuse, calibration under shift and benchmark/harness robustness.
8. Keep the frontier nonempty. Checkpoints/findings/report readiness are never global completion.

Do not read legacy `research_workers/reasoning/`, O/O-derived state, comparator/integrator/index/feed/audits, other-worker state/config, shared execution ledger, or other-role receipts.
