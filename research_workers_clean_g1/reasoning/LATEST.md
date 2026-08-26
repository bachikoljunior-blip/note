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

Read `STATE.md` for the accumulated base, then source-qualified checkpoints above in order as needed. Newest checkpoint supersedes older frontier wording where they conflict.

## Top unresolved frontier

1. **Matched Lean outer-controller comparison:** freeze theorem set, Lean/toolchain, executor/worker/verifier models, memory/cache/tool substrate and real budget; compare deterministic/rule control, free-form LLM planning, full-model agentic RL, BC, terminal-trajectory AW and a learned typed heterogeneous controller.
2. **Compact-controller gap, not broad RL gap:** Seed-Prover 1.5 directly trains an interleaved Lean/tool agent with terminal binary verifier reward; Leanstral 1.5 independently trains a long-horizon Lean proof/code agent with CISPO. Search only for a *separate compact/high-level controller* trained by RL/bandit/value/offline RL with proof generator/executors held fixed or clearly factored.
3. **Effect-classed one-decision/one-action boundary:** split pure proof-state edits from external compute, persistent writes and terminal commitments. `FORK_STATE != LAUNCH_BRANCH`; `BACKTRACK_LOCAL != CANCEL_OR_ABANDON_BRANCH`.
4. **OPE-identifiable collection:** exact structural state, hard legal mask, randomized subset, deterministic baseline/fallback, chosen action and exact propensity; never reconstruct hidden free-form planner probabilities.
5. **Trusted execution-edit safety:** proof-state rollback alone is insufficient after workers/tools/search/persistent effects. Effectful actions need stable operation identity, call/authorization progress, result obligations and atomic rule epochs.
6. **Safe action randomization:** Stage A randomizes P0 pure-local plus bounded deterministic E1 read/compute actions; persistent E2 and terminal/resource-acquisition E3 stay baseline/gated until idempotency/exact-once/authorization conditions are explicit.
7. **Replay-complete state:** replay must reconstruct legal mask, baseline/fallback, randomized set, full behavior distribution, `mu_chosen`, chosen action, deterministic executor expansion and effect record from logged structural artifacts only, without raw planner CoT.
8. **Data-adequacy-first OPE:** support/coverage gates estimator choice; weak overlap may use truncated/regularized estimators, zero support requires abstention/new collection.
9. **Credit assignment:** compare behavior cloning/human-action imitation against terminal trajectory AW, verifier-grounded sequential value and cost-aware constrained policy under the same kernel-verified terminal objective.
10. **Real-cost control:** log terminal verified solve/reusable progress separately from tokens/$, Lean/tool time, state reconstruction, concurrency-adjusted wall-clock and occupied worker/model slots; expose full remaining budget vector structurally.
11. **Conservative deployment under shift:** learned controller must fall back to baseline in weak-support/uncertain regions; recursive/scaffold improvements need explicit transfer tests.
12. **Proof-specific routing:** semantic branching+repair, subgoal scheduling, triggered re-retrieval, snapshot reuse, calibrated model/worker/search escalation, restart/replan, decomposition, context compaction and pruning remain active action/state families.
13. **Reproducibility:** inspect Leanstral 1.5 open model/inference artifacts and Adapt final ASE 2026 artifact; pin paper/model/repo/benchmark/controller contracts and report missing components explicitly.

## Current synthesis and newest updates

- **C86 — broad sequential/terminal-reward formal-proof outer policy exists:** Seed-Prover 1.5 (`arXiv:2512.17260`) trains a single agentic Lean prover over interleaved reasoning, Lean verification, Mathlib search and Python calls with VAPO/PPO-style RL and terminal reward `+1` for a Lean-verified proof, `-1` otherwise. The paper explicitly frames this as learning interaction strategies/tool usage. Average function calls and sequence length decrease through RL while performance rises, and search usage differs strongly by dataset (roughly 10 Mathlib searches/trajectory on FATE-H versus 1–2 on Putnam). This closes the broad claim that no terminal/sequential-reward formal-proof outer behavior has been learned.
- **C86 scope guard:** Seed-Prover's policy is a large free-form autoregressive model over reasoning/proof/tool-call tokens, not a compact typed controller; binary reward has no explicit real-cost term; legal masks/propensities/OPE are not exposed; action-routing gains are not isolated from general model improvement.
- **C87 — independent open-weight confirmation:** Mistral's Leanstral 1.5 (2026-07-02) is trained with CISPO in (a) a multiturn theorem environment with Lean feedback/refinement and (b) a raw-filesystem code-agent environment with file edits, shell, Lean LSP, auxiliary-lemma construction and context compaction. Officially reported results include PutnamBench 587/672, FATE-H 87%, FATE-X 34%, FLTEval pass@1 28.9 / pass@8 43.2. Weights are Apache-2.0 and API access exists. Treat this as strong full-model agentic-RL evidence, not a compact-controller ablation.
- **C88 — artifact asymmetry:** at public Seed-Prover repo commit `38c59cebaf969ac259196eb091757518d5b54c67`, `SeedProver-1.5/` contains only README, PDF, Putnam2025 proofs ZIP and one Lean proof; no agentic-RL trainer/controller/trajectory release was found there. Adapt's current arXiv HTML still exposes placeholder ACM code/data metadata, and exact-title / Adapt-Coq GitHub repository searches returned no paper-specific public repo in this run. Do not infer no artifact exists globally; re-check final ASE 2026 artifact/proceedings.
- **C84 — supervised outer selector exists but imitation accuracy misleads:** Adapt (`arXiv:2510.25103`, ASE 2026) selects `Lemma Discovery`, `Context Enrichment` or `Regeneration`. Its 3-layer DNN gets 82% CV accuracy / 0.78 F1 on 18,628 human-derived CoqDev states but proves 595/1720, below random 605/1720 and prompted LLM 651/1720. This is strong negative evidence against optimizing human-action classification as the controller objective.
- **C85 — dynamic heterogeneous routing is useful:** full Adapt proves 651/1720; without lemma discovery 590, without context enrichment 622. The rule router nearly matches success (647) but consumes ~50% more tokens. Expensive proof operations should be conditionally selected rather than always-on.
- **D4 — execution-effect ontology:** P0 pure-local state transitions; E1 bounded read/compute effects; E2 persistent writes/caches; E3 terminal/external commitments or resource acquisition. Replay re-executes P0 deterministically and consumes recorded outcomes/receipts for E1–E3 instead of reissuing effects.
- OpenProver remains a strong direct free-form heterogeneous Lean-controller baseline from earlier checkpoints. Its public traces are rich but multi-action planner bundles, missing authoritative legal masks, exact behavior propensities and full budget vectors; treat historical traces as descriptive/supervised only.
- General frozen-LLM harness control with offline RL remains directly demonstrated outside formal proof by Yi & Song 2026 (`arXiv:2607.05458`); transfer into Lean typed-control remains untested.
- Prior proof-search evidence still supports verifier-grounded structural diversity, learned compiler repair, progress/value guidance, subgoal factorization/caching, context selection, dynamic restart/repair routing and proof-state snapshot reuse. Preserve exact tested scope; narrow failures never reject a method family.
- No sanitized reasoning feedback was consumed in the frozen semantic snapshot.

## Exact continuation

1. Search specifically for a **separate compact/high-level formal-proof controller** trained with RL, bandit, value learning or offline RL where proof generation/tool execution is held fixed or factored. Do not spend cycles rediscovering full-model agentic RL.
2. Search Seed-Prover 1.5, Leanstral 1.5 and adjacent systems for controlled action/tool-routing ablations, cost-sensitive reward variants, action traces or explicit controller/environment schemas.
3. Inspect Leanstral 1.5's open model card/inference harness/SafeVerify integration for reproducible state/action/effect logging that could seed a fixed matched substrate.
4. Re-check Adapt's final ASE 2026 proceedings/artifact page for a real code/data link and the 18,628-state/CoqDev release.
5. Formalize `legal_action_mask(s)` over P0/E1/E2/E3 atomic actions using proof status, mode/isolation, memory/cache, budget, in-flight-child, result-obligation and edit-safety predicates.
6. Define canonical replay event: structural theorem/proof/subgoal/cache/retrieval/budget digest + effect state + mask + randomized set + baseline/fallback + full `mu` + chosen action + deterministic executor version + operation/result linkage.
7. Keep Stage-A randomization to P0 plus bounded deterministic E1; E2/E3 remain baseline/gated until idempotency, authorization and exact-once semantics are explicit.
8. Test semantic state representations that avoid raw planner CoT: proof-state embeddings, compact trajectory/progress/error summaries, retrieval state, context-compaction state and remaining-budget features.
9. Compare under one fixed substrate: BC on human/LLM actions; terminal trajectory AW; verifier-grounded sequential value/advantage; cost-aware constrained policy; plus free-form and full-model agentic-RL baselines. Report verified solve/cost curves, not selector accuracy alone.
10. Build deterministic replay tests for state/mask/baseline/randomized-set/propensity/executor expansion/effect safety; state aliasing adds minimal structural features, zero support causes abstention/new collection.
11. Preserve semantic branching+compiler repair, subgoal scheduling, triggered re-retrieval, snapshot reuse, calibrated compute escalation, real-cost accounting and robustness under repository/benchmark shift.
12. Keep the frontier nonempty. Checkpoints/findings/report readiness are never global completion.

Do not read legacy `research_workers/reasoning/`, O/O-derived state, comparator/integrator/index/feed/audits, other-worker state/config, shared execution ledger, or other-role receipts.
