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
23. `2026-08-26T0657JST-followup.md`
24. `2026-08-26T0657JST-followup2.md`
25. `2026-08-26T0802JST.md`
26. `2026-08-26T0903JST.md`
27. `2026-08-26T1000JST.md`
28. `2026-08-26T1101JST.md`

Read `STATE.md` for the accumulated base, then source-qualified checkpoints above in order as needed. Newest checkpoint supersedes older frontier wording where they conflict.

## Top unresolved frontier

1. **Policy-replacement experiment on a mature typed Lean substrate:** freeze theorem split, Lean/Mathlib, low-level models/prompts, retrieval, workspace/action executors, checker/SafeVerify, cost estimator and actual budget. Replace only deterministic action selection/value with BC, terminal-AW, sequential value/advantage, contextual bandit and conservative cost-aware typed policies; retain free-form/full-model agentic RL only as distinct unfactored references.
2. **Canonical legal-action mask:** CSSC-like structured runtimes already enforce mutation-scope validation, proposal validity, workspace/version/readiness checks and budget admission, but these constraints are distributed. Project one authoritative pre-decision `legal_action_mask(s)` plus reason-per-illegal-action over the version-pinned choice set before any randomized/learned selection.
3. **OPE-identifiable collection:** log structural state, workspace/config/executor versions, full choice set, legal mask, budget admission, deterministic baseline/fallback, randomized safe subset, full behavior distribution, chosen action and exact propensity. Never reconstruct hidden free-form planner probabilities.
4. **Learn value while freezing cost:** CSSC already has frozen/fingerprinted completed-action cost histories and held-out cost MAE/coverage. Keep that estimator fixed initially and learn only verified-success/progress value/advantage so numerator and denominator effects are not confounded.
5. **Effect-classed atomic actions:** keep P0 pure-local, E1 bounded read/compute, E2 persistent write/cache and E3 terminal/resource commitment distinct. `FORK_STATE != LAUNCH_BRANCH`; `BACKTRACK_LOCAL != CANCEL_OR_ABANDON_BRANCH`. Stage-A randomization stays P0 + bounded deterministic E1 until effect semantics are explicit.
6. **Compact-controller gap, not broad RL gap:** full autoregressive formal-proof agents already learn tool behavior under RL. Continue searching only for a separate compact/high-level policy trained by RL/bandit/value/offline RL with low-level proof/tool execution fixed/factored. Another targeted pass still did not find an exact match.
7. **Real-cost utility:** optimize kernel-verified terminal solve and reusable verified progress against generated/input/billed tokens, model tier/$, checker/tool/retrieval time, state reconstruction, concurrency-adjusted wall-clock and occupied slots. Selector accuracy or information gain are features/diagnostics, not objectives.
8. **External matched evaluation:** CSSC's public miniF2F preparation/runner is close to usable but formal arms/model/task ids/repeats are not frozen. Use explicit action-mask ablations to separate richer action-space gains, cost-aware selection gains and cheap/strong routing gains.
9. **Data-adequacy-first OPE:** third-party Leanstral trajectories include attempt budgets/outcomes/compiler/SafeVerify metadata, but targeted rescue is adaptive and no authoritative action propensities/legal mask are established. Use primary fixed-budget attempts separately for supervised representation/error/cost modeling; zero support means abstain/new collection.
10. **Conservative deployment under shift:** learned control falls back to deterministic baseline in weak-support/uncertain regions; test theorem-family, repository, Lean/Mathlib and low-level-prover shifts.
11. **Proof-specific action families:** semantic branching+compiler repair, subgoal scheduling, triggered re-retrieval, snapshot reuse, calibrated model/search escalation, restart/replan, decomposition, context compaction and pruning remain active ontology candidates where executor contracts support them.
12. **Reproducibility/provenance:** continue checking official Mistral/Leanstral surfaces for an inference/CISPO environment or official trajectory logger; never upgrade third-party preserved evaluation artifacts to official training data.

## Current synthesis and newest updates

- **C93 — mature heuristic substrate:** source-level audit of public `anetigone/cssc` shows versioned typed search actions, mutation scopes, structured workspace/obligation/branch state, action-level proposal cache/frontier, unified budget admission, cheap/strong routing, append-only cost ledger, frozen historical cost estimation and rich result traces. A compact learned controller can be tested as a policy-replacement layer rather than a new harness.
- **C94 — mask gap is precise:** the action runtime already materializes a pre-selection `choice_set` with action identity, estimated cost and budget admission, while validity is separately enforced by mutation-scope/proposal/workspace/readiness/budget checks. Its roadmap explicitly lists `allowed_action_kinds` or equivalent action mask as unfinished. Canonicalize these constraints before policy/OPE work; do not pretend current actions are unconstrained.
- **C95 — cost/value asymmetry:** completed action costs are bucketed, frozen/fingerprinted, explicit about missing data/cold-start fallback and evaluated with held-out coverage/MAE. Selection value remains hand-coded (`unlock_value * progress_likelihood * information_gain / cost` plus deterministic rules). Freeze cost and learn only value/advantage first.
- **C96 — evaluation readiness, not outcome evidence:** CSSC reports pinned public miniF2F preparation, real Lean eligibility and a tiny live-server pilot, but formal experimental arms/model/task ids/repeats remain unfrozen. Its roadmap already asks for matched action-mask ablations and non-inferiority/matched-cost reporting; do not treat engineering readiness as controller success.
- **C97 — Leanstral preserved traces:** third-party `yidannwang/Leanstral-1-5-results` exposes per-attempt token budget, timeout/exit, compile/verdict/reason and trajectory/compiler/SafeVerify artifacts. Fixed-budget primary attempts and targeted higher-budget rescue are mixed by design; useful for supervised feature/cost models, unsafe for naïve OPE without known behavior policy/mask.
- **C98 — exact factorization gap remains bounded-open:** another targeted search found full-agent RL, tactic/decomposition policies, heuristic orchestrators and supervised/LLM selectors, but no public primary result satisfying separate compact heterogeneous controller + RL/bandit/value/offline-RL + fixed/factored low-level prover/tool execution. This is not proof of global nonexistence.
- **C84/C85 remain important controls:** Adapt's high supervised selector CV accuracy did not translate to best end-to-end proof success; verified utility per real cost must be the objective rather than action imitation accuracy.
- **C86/C89 remain broad positive controls:** Seed-Prover shows terminal verifier reward can make a full agent more selective about tool use while improving performance, but it does not isolate a compact controller.
- **D4 execution-effect ontology remains:** P0 pure-local; E1 bounded read/compute; E2 persistent writes/caches; E3 terminal/external commitments/resource acquisition. Replay should deterministically re-execute only pure-local transitions and consume recorded receipts/outcomes for effectful operations rather than reissuing them.
- No sanitized reasoning feedback was available/consumed in this frozen semantic snapshot.

## Exact continuation

1. Inspect CSSC `action_runtime` and trace serialization to specify the smallest canonical `DecisionEvent` and the exact insertion point where stochastic/learned selection can replace deterministic `select_admissible_action` without changing action generation/execution.
2. Check whether explicit `allowed_action_kinds`/mask support lands in public source; otherwise define a deterministic mask projection over action/proposal validation, workspace/version/readiness, budget admission and effect-safety gates.
3. Classify current structured action kinds and executor steps into P0/E1/E2/E3. Separate local workspace graph mutation from external model/checker/retrieval/tool effects even when one high-level action triggers both.
4. Define compact structural state from already logged fields: workspace/obligation/branch status/version, proof/error/progress summaries, failure hypotheses, retrieval state, proposal provenance/model tier, frozen cost estimate, budget vector, cache state and recent verified progress; exclude raw planner CoT.
5. Pre-register a Stage-A randomized safe subset and exact propensities around the deterministic heuristic baseline; persistent/terminal actions stay gated until exact-once/idempotency/authorization rules are explicit.
6. Define reward/utility: terminal kernel-verified solve and source-qualified reusable verified progress, minus or constrained by real cost. Evaluate probability/value calibration separately from cost-estimator calibration.
7. Use CSSC's fair-baseline plan for the matched benchmark: same generator/workspace/frontier/budget, paired repeats, explicit action-space masks, non-inferiority plus matched-cost success curves.
8. Continue targeted search for the exact compact-controller factorization and inspect public source artifacts rather than rediscovering full-model RL.
9. Re-check official Leanstral/Mistral releases for official environment/trainer/trajectory logging; preserve third-party evaluation provenance separately.
10. Keep the frontier nonempty. `2026-08-26T1101JST.md` is the newest checkpoint and is not global completion.

Do not read legacy `research_workers/reasoning/`, O/O-derived state, comparator/integrator/index/feed/audits, other-worker state/config, shared execution ledger, or other-role receipts.
