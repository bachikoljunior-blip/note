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

Read `STATE.md` for the earlier accumulated base, then read the source-qualified checkpoints above in order. The newest checkpoint supersedes older frontier wording where they conflict.

## Top unresolved frontier

1. **Matched Lean outer-controller comparison:** freeze theorem set, Lean/toolchain, executor/worker/verifier models, memory/cache/tool substrate and real budget; compare deterministic/rule control, free-form LLM planning, BC, terminal-trajectory AW and learned typed heterogeneous control.
2. **Sequential-reward selector gap:** Adapt (ASE 2026) closes the claim that no learned formal-proof outer selector exists, but its DNN is supervised human-action imitation and underperforms random end-to-end. Search for RL/bandit/value/offline-RL outer selectors trained on terminal/sequential verified utility rather than tactic-label imitation.
3. **Effect-classed one-decision/one-action boundary:** split pure proof-state edits from external compute, persistent writes and terminal commitments. In particular `FORK_STATE != LAUNCH_BRANCH` and `BACKTRACK_LOCAL != CANCEL_OR_ABANDON_BRANCH`.
4. **OPE-identifiable collection:** exact structural state, hard legal mask, randomized subset, deterministic baseline/fallback, chosen action and exact propensity; never reconstruct hidden free-form planner probabilities.
5. **Trusted execution-edit safety:** proof-state rollback alone is insufficient after workers/tools/search/persistent effects. Effectful actions need stable operation identity, call/authorization progress, result obligations and atomic rule epochs.
6. **Safe action randomization:** Stage A randomizes P0 pure-local plus bounded deterministic E1 read/compute actions; persistent E2 and terminal/resource-acquisition E3 stay baseline/gated until idempotency/exact-once/authorization conditions are explicit.
7. **Replay-complete state:** replay must reconstruct legal mask, baseline/fallback, randomized set, full behavior distribution, `mu_chosen`, chosen action, deterministic executor expansion and effect record from logged structural artifacts only, without raw planner CoT.
8. **Data-adequacy-first OPE:** support/coverage gates estimator choice; weak overlap may use truncated/regularized estimators, zero support requires abstention/new collection.
9. **Credit assignment:** compare behavior cloning/human-action imitation against terminal trajectory AW, verifier-grounded sequential value and cost-aware constrained policy under the same terminal kernel-verified objective.
10. **Real-cost control:** log terminal verified solve/reusable progress separately from tokens/$, Lean/tool time, state reconstruction, concurrency-adjusted wall-clock and occupied worker/model slots; expose the full remaining budget vector to the controller.
11. **Conservative deployment under shift:** learned controller must fall back to baseline in weak-support/uncertain regions; Dalek-Bench is direct evidence that recursive scaffolding can fail to transfer.
12. **Proof-specific routing:** semantic branching+repair, subgoal scheduling, triggered re-retrieval, snapshot reuse, calibrated model/worker/search escalation, restart/replan, decomposition and pruning remain active action families.
13. **Reproducibility:** inspect Adapt/CoqDev artifact availability; publish exact BC/Forced-CHECK implementations and pin paper version, repo commit, benchmark split, scorer, controller action contract and budget.

## Current synthesis and newest updates

- **C84 — direct learned outer-strategy selector exists, but imitation accuracy is misleading:** Adapt (`arXiv:2510.25103`, listed by authors as ASE 2026) dynamically selects `Lemma Discovery`, `Context Enrichment`, or `Regeneration` after Coq proof failure. Its learning-based selector trains on 18,628 human-written CoqDev proof states using six hand-engineered quantitative features. A 3-layer DNN reaches 82% 10-fold-CV classification accuracy / 0.78 F1, yet end-to-end proves only 595/1720 (34.77%), below random 605/1720 (35.17%) and the prompted LLM selector 651/1720 (37.85%). The paper attributes the DNN's weakness to insufficient proof-state semantics and sparse data, especially for lemma discovery. This is strong negative evidence against using human-action classification accuracy as the controller objective.
- **C85 — dynamic heterogeneous routing has real value, but strongest routing is still free-form:** full Adapt proves 651/1720; without lemma discovery 590, without context enrichment 622. The rule router nearly matches success (647) but consumes roughly 50% more tokens, because it over-invokes expensive lemma discovery. Random proves 7.07% fewer theorems and uses 19.26% more iterations than the LLM decision-maker. Costly proof operations should therefore be conditionally selected, not always-on.
- **D4 — execution-effect ontology:** normalize controller actions into P0 pure-local state transitions, E1 bounded read/compute effects, E2 persistent writes/caches, and E3 terminal/external commitments or resource acquisition. P0 replay re-executes deterministically; E1-E3 replay consumes recorded receipts/outcomes and must not reissue effects. Split `SPAWN_BRANCH` into `FORK_STATE` (P0) + `LAUNCH_BRANCH` (E1); split `BACKTRACK_OR_PRUNE` into local backtrack/prune (P0) + cancel/abandon in-flight work (E1). `UPDATE_SCRATCH` is P0 only if transaction-local, otherwise E2; `STORE_VERIFIED` is E2; `ESCALATE_COMPUTE` and `SUBMIT` are E3-like gated actions.
- OpenProver remains the strongest direct free-form Lean heterogeneous-controller baseline found so far. Public source audit is pinned at commit `e200251b34349ab6c34548d30319abde86cb6bc6`.
- **C80 — parseable but bundled decisions:** OpenProver has a fixed TOML planner vocabulary and strict parser, but one physical planner step may contain multiple sequential action blocks; `plans.json` preserves the full bundle while `planner.toml`/step metadata can reduce it to the primary/last action. OPE must not treat the step-level `action` field as the full policy decision.
- **C81 — no centralized legal mask:** planner documentation varies by mode/isolation, but parser validation uses the global action list and unavailable actions may be rejected later by handlers. Exact propensity collection needs a new authoritative pre-sampling `legal_action_mask(s)`.
- **C81 budget gap:** `_do_step` passes `budget_status` to `format_planner_prompt`, but the inspected formatter does not insert it. The free-form planner sees coarse >80%/>95% budget interventions, not the full continuous remaining-budget vector. A cost-aware typed controller must log/expose budget structurally.
- **C82 — rich traces but raw planner history:** OpenProver persists planner output/action outputs and feeds recent planner output back into future prompts; planner output can include free-form reasoning. Current metadata already logs planner/worker cost, duration and token usage, but lacks legal/randomized masks, behavior distribution/propensity and replay hashes. Learned typed state should exclude raw planner prose and use canonical structural artifacts instead.
- **C83 — execution edits require more than a snapshot:** Zheng et al. `arXiv:2608.22928` give an exact safety model for Checkpoint/Fork/Restore/Merge. Earlier authorization/tool requests cannot be undone; safe edits must preserve stable action/call identity, authorization and call progress, still-required results or authorized removals, and history-bound runtime rules. Before installation, edits are rechecked against the current record and rule changes take effect atomically. Thus a Lean proof-state restore is not a safe execution rollback once external or persistent actions are in flight.
- General frozen-LLM harness control with offline RL is directly demonstrated by Yi & Song 2026 (`arXiv:2607.05458`); Lean transfer remains untested.
- **C77 — artifact reproducibility gap:** at public Harness-RL commit `5d577632...`, README/main driver/main-table analysis implement Base-vs-AW only; `offline_aw.py` exposes AW but no BC trainer; `docs/ARTIFACT.md` says no single reproduction runner is tracked. Paper BC/Forced-CHECK Table-4 values cannot currently be regenerated from the documented main-table path without reconstructing additional protocol. This does not show the paper values are wrong.
- **C78 — Lean heterogeneous action ontology exists as hand/prompted control:** Max Tan's `arXiv:2605.30914` uses deterministic gates plus task/proof-level progress evaluation to choose local repair/tool search, structural revision/decomposition, or escalation/pruning. The thesis explicitly lists learned progress models/value networks/trained revisers as future work.
- **C79 — BFS-Prover-V2 qualification:** its off-policy RL learns the tactic step-prover; its inference Planner is a separate reasoning LLM. It is not RL over heterogeneous outer actions and does not close the targeted gap.
- Prior proof-search evidence still supports verifier-grounded structural diversity, learned compiler repair, progress/value guidance, subgoal factorization/caching, context selection, dynamic restart/repair routing and proof-state snapshot reuse. Preserve exact tested scope; narrow failures never reject a method family.
- `research_feedback_clean_g1/reasoning/FEEDBACK.json` was absent at the frozen control snapshot; no sanitized feedback was consumed.

## Exact continuation

1. Search specifically for another 2025–2026 formal-proof outer selector trained with sequential/terminal reward (RL, bandit, value learning or offline RL), not human-action imitation; Adapt closes only the supervised-classifier gap.
2. Inspect Adapt's public artifact/code and CoqDev release status if available with ASE 2026; determine whether the 18,628 state/action dataset, label derivation and exact decision traces are reproducible.
3. Formalize `legal_action_mask(s)` over P0/E1/E2/E3 atomic actions with exact proof-status, mode/isolation, memory/cache, budget, in-flight-child, result-obligation and edit-safety predicates.
4. Define canonical replay event: structural theorem/proof/subgoal/cache/retrieval/budget digest + effect state + mask + randomized set + baseline/fallback + full `mu` + chosen action + deterministic executor version + operation/result linkage.
5. Define one-decision/one-action executor contracts. Current OpenProver multi-action bundles remain a free-form baseline, not the learned policy's atomic action space.
6. Formalize Stage-A randomization as P0 plus bounded deterministic E1 only; E2/E3 stay baseline/gated until idempotency, authorization and exact-once semantics are explicit.
7. Test semantic state representations that may fix Adapt DNN's failure without raw planner CoT: proof-state embeddings, compact trajectory/progress/error summaries, retrieval state and remaining-budget features.
8. Compare objectives under one fixed substrate: BC on human/LLM actions; terminal trajectory AW; verifier-grounded sequential value/advantage; cost-aware constrained policy. Report verified solve/cost curves, not selector accuracy alone.
9. Build deterministic replay tests for state/mask/baseline/randomized-set/propensity/executor expansion/effect safety; state aliasing adds minimal structural features, zero support causes abstention/new collection.
10. Treat historical free-form OpenProver traces as descriptive/supervised data only; never manufacture propensities for them. New randomized typed collection is required for OPE/causal claims.
11. Continue semantic branching+compiler repair, subgoal scheduling, triggered re-retrieval, proof-state snapshot reuse, calibrated compute escalation, cost-normalized evaluation and robustness under repository/benchmark shift.
12. Keep the frontier nonempty. Checkpoints/findings/report readiness are never global completion.

Do not read legacy `research_workers/reasoning/`, O/O-derived state, comparator/integrator/index/feed/audits, other-worker state/config, shared execution ledger, or other-role receipts.
