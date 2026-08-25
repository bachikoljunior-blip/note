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

Read `STATE.md` for the earlier accumulated base, then read the source-qualified checkpoints above in order for exact evidence, version/model/budget caveats, negative evidence and continuation. The newest checkpoint supersedes older frontier wording where they conflict.

## Top unresolved frontier

1. **Matched Lean controller comparison:** freeze the same action/tool/verifier/memory substrate and real budget, then compare fixed/rule control, free-form LLM planning and a learned typed heterogeneous policy.
2. **Lean-specific learned harness policy:** general frozen-LLM harness control with offline RL is now demonstrated (C65); the open problem is adapting it to proof-specific state/actions, deterministic kernel feedback, persistent verified DAG/cache, and proof costs.
3. **OPE-identifiable data collection:** free-form OpenProver planner traces do not expose behavior meta-action propensities; use a typed outer policy with reconstructable randomized behavior, exact masks/propensities and coverage diagnostics.
4. **Data-adequacy-first offline evaluation:** support/coverage must gate estimator choice; weak overlap may permit truncated estimators, while unsupported target action regions require abstention/new collection rather than a precise policy ranking.
5. **Conservative/baseline-bootstrap deployment:** learned policy should defer to the baseline in weak-support/uncertain state-action regions, with verifier-enforced hard constraints.
6. **Hierarchical controller-of-controllers:** decide local proof action plus whether to buy more thinking, stronger model, workers, specialized prover, retrieval, population/evolution or replan.
7. **Calibrated prospective action/value-of-computation:** Brier/ECE/reliability/selective-risk under theorem/backbone/search-policy shift, especially near expensive-action boundaries.
8. **Compact OPE-sufficient state/context isolation:** use a deliberately logged structural state rather than hidden/full reasoning history; test state aliasing and downstream solve/cost.
9. **Credit assignment and scheduling:** terminal-only trajectory AW versus verifier-grounded progress/value, plus matched first-stuck/hardest-branch/parallel scheduling and variable semantic branching.
10. **Execution-aware retrieval/repair:** triggered global re-retrieval, snapshot+semantic-selection+compiler repair, proof-state reconstruction cost and benchmark/harness robustness remain open.

## Current synthesis and newest updates

- **OpenProver is the strongest direct free-form Lean controller baseline found so far.** On 185 ProofNet formal theorems with a 100k output-token budget/problem, the published comparison reports Kimi-K2.5 57.3% vs linear rollout 36.8%, and Leanstral 28.1% vs 21.1%. Its Planner chooses heterogeneous actions while Workers/Verifiers are context-isolated. The comparison matches output-token budget, not every real cost dimension.
- OpenProver's implementation provides most logging substrate required for controller learning: typed Planner actions; `planner.toml`/`plans.json`; worker tasks/results/verifiers/tool calls; Lean outcomes; and per-call tokens/cache/cost/elapsed metadata.
- **C60 — deterministic event schema:** normalize run artifacts into `run_start -> state_before -> planner_call -> action_proposed -> action_result/tool_result -> state_after -> run_end`, with deterministic IDs/artifact hashes and vector outcome/cost. Avoid raw hidden reasoning when compact state/artifact references suffice.
- **C61 — free-form OPE blocker:** OpenProver's selected meta-actions lack behavior-policy propensities, so IPS/sequential DR are not identified without propensity estimation plus sufficient support. Estimated logging policy does not create support for unseen actions.
- **C62 — conservative deployment:** SPIBB-style baseline bootstrapping gives a useful controller rule: override the baseline only with sufficient evidence/support; otherwise reproduce baseline behavior. Its formal guarantees do not automatically transfer to neural partially observed Lean control.
- **C63 — mid-trajectory compute purchase:** recent non-Lean dynamic-help/stepwise-routing/MCTS work supports `escalate_model`, `spawn_more_workers`, and `buy_search` as evolving-state actions rather than only first-token decisions. Transfer only, not Lean evidence.
- **C64 — targeted absence:** one focused search did not find a public raw OpenProver ProofNet trajectory archive; rerun/instrumentation is the practical path. No direct Lean full heterogeneous learned planner policy surfaced in targeted search. These are search gaps, not nonexistence claims.
- **C65 — direct general learned-harness evidence:** Yi & Song 2026 (`arXiv:2607.05458`) train a lightweight outer Harness-MDP controller over a frozen LLM with offline advantage-weighted regression. It improves verification behavior across tested domains and selectively improves final quality; public paper summaries report about +18.2 pp on adapted tau-bench retail and +13.2 pp on adapted AgentBench DB-Bench. Behavior cloning and Forced CHECK ablations do not explain the gains. This closes the broad general-agent 'can harness control be learned?' gap; Lean transfer remains untested.
- **C66 — reconstructable behavior policy:** the released `Agentic-RL-harness` main driver collects with an epsilon-perturbed structural baseline (`eps=0.25` default) over an explicit legal-action mask. Exact behavior propensities are reconstructable from epsilon, mask and deterministic base/fallback rule. This is a directly reusable template for OPE-identifiable Lean data collection.
- **C67 — credit-assignment opportunity:** released offline-AW code assigns the same terminal trajectory advantage to every action step. Lean's deterministic compiler/kernel signals make finer verifier-grounded step credit possible. Compare terminal-only AW, verifier-grounded potential/progress targets and sequential value/OPE rather than assuming dense shaping helps.
- **C68 — partial-observability warning:** history-dependent POMDP OPE can be statistically difficult, and estimated history-dependent behavior policies trade finite-sample bias against asymptotic variance. Define the learned controller as explicitly observation-Markov over a logged compact state and record exact propensities; do not let unlogged hidden CoT silently become control state.
- **C69 — minimal Lean Harness-MDP starting point:** begin with a small structural controller over progress/error/cache/retrieval/cost/model-tier/last-action features and hard action masks over local continue, repair, retrieval, decompose/replan, spawn, escalation, backtrack/restart and submit. Increase controller capacity only after state-aliasing/nonlinearity ablations justify it.
- **New C70 — coverage before estimator:** DataCOPE-style coverage analysis should gate OPE. Mehrabi & Wager's weak-overlap work (`arXiv:2402.08201v2`) shows truncated doubly robust estimation can remain useful under weaker distributional overlap, but zero-support actions remain unevaluable. The Lean benchmark should abstain/fallback or recollect when the learned policy leaves support.
- **New C71 — optimize the logging policy too:** uniform safe epsilon is the auditable first collector, not necessarily the efficient final one. Logging-policy-design work (`arXiv:2605.15108`) motivates a second phase that trades immediate reward against coverage of decision-relevant state-action regions while maintaining minimum support.
- **New C72 — escalation reward should use real service cost:** LQM-ContextRoute (`arXiv:2605.14241`) provides transfer evidence against naive additive quality-minus-latency routing. For Lean, model/worker/search escalation should be valued by expected verified terminal/reusable-progress gain against the real cost vector (tokens/$, Lean/tool/state-reconstruction time, concurrency-adjusted wall-clock and occupied service slots), not latency or uncertainty alone.
- **Meta-Reasoner / AxProverBase / LeanFlow / AlphaProof Nexus / BFS-Prover-V2 / LEAP / Numina-Lean-Agent** remain useful supporting baselines for compact state, heterogeneous actions, backbone-conditioned compute and orchestration cost, but none replaces the matched Lean test above.
- Prior proof-search evidence still supports verifier-grounded structural diversity, learned repair, progress/value guidance, subgoal caching/factorization, context selection and state snapshot reuse. Preserve exact tested scope: narrow adaptation failures never reject the whole method family.
- `research_feedback_clean_g1/reasoning/FEEDBACK.json` remains absent; no sanitized feedback was consumed.

## Exact continuation

1. **Lean Harness-MDP mapping:** map OpenProver Planner/Worker/Lean tools into a typed outer action policy while preserving released free-form Planner and fixed/rule controllers as matched baselines.
2. **Behavior logging design:** specify epsilon/mixed randomized exploration over a safe eligible Lean action subset; log mask and exact propensity. Compare uniform epsilon with coverage/OPE-aware logging-policy allocation.
3. **Agentic-RL-harness verification:** inspect exact behavior-cloning/Forced-CHECK ablations, held-out benchmark protocols and reward terms before reusing effect sizes beyond the current qualified summary.
4. **Compact-state sufficiency:** define structural state without hidden CoT, then ablate error class, progress/value, retrieval, verified cache/DAG, cost/budget, model tier and previous action for aliasing/coverage and solve/cost.
5. **Sequential evaluation:** compare DR/TDR/WDR, fitted-Q/model-based estimates and DataCOPE/coverage diagnostics; abstain from ranking where overlap/support is inadequate.
6. **Credit assignment:** terminal trajectory AW vs verifier-grounded progress/potential targets vs sequential value learning, keeping process metrics diagnostic rather than direct reward unless causal benefit is demonstrated.
7. **Conservative deployment:** baseline-bootstrap learned actions in well-supported regions only; report fallback/abstention frequency and verifier constraint violations.
8. **Mid-trajectory compute purchase:** search/prototype model/worker/search escalation after observed proof progress/failure and measure marginal terminal value per real cost.
9. Continue prior proof-specific branches: matched subgoal scheduling, semantic branching+repair, triggered re-retrieval, snapshot reuse, calibration under shift and benchmark/harness robustness.
10. Keep the frontier nonempty. Checkpoints/findings/report readiness are never global completion.

Do not read legacy `research_workers/reasoning/`, O/O-derived state, comparator/integrator/index/feed/audits, other-worker state/config, shared execution ledger, or other-role receipts.
