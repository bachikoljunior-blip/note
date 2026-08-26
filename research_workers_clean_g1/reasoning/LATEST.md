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

Read `STATE.md` for the accumulated base, then source-qualified checkpoints above in order as needed. Newest checkpoint supersedes older frontier wording where they conflict.

## Top unresolved frontier

1. **Matched Lean outer-controller comparison:** freeze theorem set, Lean/Mathlib, low-level proof model/executors, verifier, retrieval corpus, memory/cache/tool substrate and real budget; compare deterministic/rule control, free-form LLM planning, BC, terminal-trajectory AW, sequential verifier-grounded value/advantage, cost-aware constrained typed control, and full-model agentic RL only as an unfactored reference.
2. **Compact-controller gap, not broad RL gap:** Seed-Prover 1.5 and Leanstral 1.5 already show that full autoregressive formal-proof agents can learn tool interaction under terminal/sequential RL. Search only for a *separate compact/high-level controller* trained by RL/bandit/value/offline RL with proof generation/tool execution held fixed or clearly factored.
3. **Concrete heuristic baseline now exists:** `anetigone/cssc` independently exposes a Lean action space close to the target (`expand_cheap_tactic`, repair, retrieve, strong-proof/decompose escalation, backtrack, prune, stop), but its README deliberately starts with fixed costs/rules/thresholds and **no learned value model**. Inspect its source/roadmap as a matched heuristic baseline, not learned-policy evidence.
4. **OPE-identifiable collection:** exact structural state, hard legal mask, randomized safe subset, deterministic baseline/fallback, full behavior distribution, chosen action and exact propensity; never reconstruct hidden free-form planner probabilities.
5. **Effect-classed atomic actions:** keep P0 pure-local, E1 bounded read/compute, E2 persistent write/cache and E3 terminal/resource commitment distinct. `FORK_STATE != LAUNCH_BRANCH`; `BACKTRACK_LOCAL != CANCEL_OR_ABANDON_BRANCH`.
6. **Trusted execution-edit safety:** proof-state rollback is insufficient after workers/tools/search/persistent effects. Effectful actions need stable operation identity, call/authorization progress, result obligations, idempotency/exact-once rules and atomic rule epochs.
7. **Replay-complete state:** replay must reconstruct legal mask, baseline/fallback, randomized set, full `mu`, `mu_chosen`, deterministic executor expansion and effect record from structural artifacts only, without raw planner CoT.
8. **Data-adequacy-first OPE:** historical OpenProver/free-form traces and third-party Leanstral evaluation traces are useful for supervised representation/error/cost modeling but lack proven propensities/legal masks. Zero support requires abstention/new collection; adaptive rescue trajectories must not be naively pooled with fixed-budget primary attempts.
9. **Real-cost control:** log verified terminal solve/reusable verified progress separately from tokens/$, Lean/tool time, retrieval time, state reconstruction, concurrency-adjusted wall-clock and occupied model/worker slots; expose the full remaining budget vector structurally.
10. **Conservative deployment under shift:** learned control falls back to baseline in weak-support/uncertain regions; test transfer across theorem families, repositories, Lean/Mathlib versions and low-level provers.
11. **Proof-specific routing:** semantic branching+compiler repair, subgoal scheduling, triggered re-retrieval, snapshot reuse, calibrated model/worker/search escalation, restart/replan, decomposition, context compaction and pruning remain active action/state families.
12. **Reproducibility:** inspect official Leanstral/Mistral surfaces for released inference harness/CISPO environment/trajectory logging, inspect third-party Leanstral result schema carefully, and re-check Adapt final ASE 2026 artifact. Pin provenance and never upgrade third-party evaluation traces to official training data.

## Current synthesis and newest updates

- **C86 — broad sequential/terminal-reward formal-proof outer policy exists:** Seed-Prover 1.5 (`arXiv:2512.17260`) trains a single agentic Lean prover over interleaved reasoning, Lean verification, Mathlib search and Python with terminal verified/unverified reward. Training curves show average tool calls falling roughly 15→10 and sequence length roughly 28k→17k while performance rises; search usage is strongly dataset-dependent (about 10 searches/trajectory on FATE-H versus roughly 1–2 on Putnam). This strengthens evidence that terminal RL can implicitly learn resource allocation, but does not isolate a compact routing module or cost-aware reward.
- **C87 — independent open-weight confirmation:** Mistral Leanstral 1.5 is an Apache-2.0 119B/6.5B-active Lean model trained with CISPO in multiturn theorem-refinement and code-agent environments involving Lean feedback, filesystem/shell/LSP, auxiliary lemmas and context compaction. Official model/SafeVerify surfaces make it a plausible fixed low-level substrate, not a compact-controller ablation.
- **C88 — artifact asymmetry remains:** Seed-Prover's public 1.5 directory previously exposed paper/proofs but no trainer/controller/trajectory release; Adapt's exact paper-specific code/data release was not verified. Re-check final artifacts without inferring global nonexistence.
- **C89 — full-model RL efficiency evidence is stronger:** Seed-Prover's own tool-call/sequence reductions while success improves show that proof-success RL can learn interaction efficiency, but the whole policy changes jointly and exact action propensities/legal masks/real-cost reward are absent.
- **C90 — independent compact-control convergence without learning:** public `anetigone/cssc` formalizes almost exactly the target cost-sensitive Lean meta-action space and fixed-budget metrics. Its first controller is explicitly heuristic with fixed cost tables, error rules, progress-per-cost, budget phases and escalation thresholds, with no learned value model. Treat it as a concrete baseline/action ontology, not outcome evidence for learned control.
- **C91 — Leanstral evaluation trace opportunity with provenance limits:** a third-party `yidannwang/Leanstral-1-5-results` artifact preserves generated Lean/trajectory/compiler/SafeVerify/per-attempt metadata and budgets. It can seed descriptive state/error/cost modeling, but is not an official Mistral training release and does not establish a known randomized logging policy, exact propensity or authoritative legal mask; adaptive rescue phases are especially unsuitable for naive OPE.
- **C92 — exact factorization gap remains open in this targeted search:** no primary/public result found here simultaneously has a separate compact heterogeneous formal-proof controller, RL/bandit/value/offline-RL training, and fixed/factored low-level proof/tool execution. Full-model agentic RL, tactic/decomposition RL, Adapt-style supervised/LLM routing and CSSC-style heuristics are nearby but do not satisfy that exact contract. This is a bounded search conclusion, not proof of global nonexistence.
- **C84/C85 remain important negative/positive controls:** Adapt's supervised 3-action DNN reaches 82% CV accuracy yet proves fewer tasks than random, while dynamic routing itself is useful and a rule router nearly matches LLM-selector success at substantially higher token cost. Controller objectives must target verified solve/progress per real cost, not imitation accuracy.
- **D4 — execution-effect ontology:** P0 pure-local transitions; E1 bounded read/compute; E2 persistent writes/caches; E3 terminal/external commitments/resource acquisition. Replay re-executes P0 deterministically and consumes recorded outcomes/receipts for effectful actions rather than reissuing effects.
- OpenProver remains a strong free-form heterogeneous Lean-controller baseline from earlier checkpoints, but its public traces are descriptive/supervised unless authoritative masks/propensities/full budget vectors exist.
- General frozen-base controller learning outside formal proof remains useful methodological support, but the formal-proof compact-controller experiment is still untested.
- No sanitized reasoning feedback was consumed in the frozen semantic snapshot.

## Exact continuation

1. Inspect `anetigone/cssc` controller/state/trace interfaces and roadmap at source level for exact action identity, cost vector, state snapshots, legal-mask representation, branch/effect lifecycle, external benchmark results and any newly added policy-learning path.
2. Inspect the third-party Leanstral result schema enough to map `state -> action/tool interaction -> Lean/compiler outcome -> cost -> next state`; enumerate exactly which legal-mask/propensity/effect fields are missing. Separate fixed-budget primary attempts from adaptive rescue.
3. Continue targeted search for a **separate formal-proof high-level controller** trained via RL/bandit/value/offline RL with fixed/factored low-level prover. Prioritize `meta-controller`, `strategy selector`, `router`, `budget-aware`, `cost-sensitive theorem proving`, `metareasoning`, `value of computation`, `offline RL proof search`.
4. Re-check official Leanstral/Mistral repositories/docs for a separate inference harness, CISPO trainer, environment schema or official trajectory dataset. Current official model + SafeVerify surface is reproducible but not OPE-identifiable by itself.
5. Define the matched controller experiment on a frozen open Lean substrate. Compare heuristic CSSC-like routing, free-form planning, BC, terminal-AW, sequential value/advantage and cost-aware constrained typed policy; include full-model agentic RL only as a distinct unfactored reference.
6. Formalize `legal_action_mask(s)` over P0/E1/E2/E3 using proof status, branch state, cache/memory, remaining budget, in-flight effects, result obligations and edit-safety predicates.
7. Design OPE-ready collection with exact randomized safe subset and known propensity. Stage A randomizes P0 plus bounded deterministic E1 only; E2/E3 stay baseline/gated until authorization/idempotency/exact-once semantics are explicit.
8. Test compact structural state representations without raw planner CoT: proof-state embeddings, trajectory/progress/error summaries, retrieval/context state, branch history, cache state, effect state and full remaining-budget features.
9. Optimize/report verified solve and reusable verified progress against real-cost curves, not selector accuracy. Treat uncertainty/information gain only as features unless they predict terminal utility per cost.
10. Preserve semantic diversity+compiler repair, subgoal scheduling, triggered re-retrieval, snapshot reuse, calibrated compute escalation, restart/replan, decomposition, context compaction, pruning and robustness under repository/benchmark shift.
11. Keep the frontier nonempty. `2026-08-26T1000JST.md` is the newest checkpoint and is not global completion.

Do not read legacy `research_workers/reasoning/`, O/O-derived state, comparator/integrator/index/feed/audits, other-worker state/config, shared execution ledger, or other-role receipts.
