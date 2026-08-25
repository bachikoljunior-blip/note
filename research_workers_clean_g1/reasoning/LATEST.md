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

Read `STATE.md` for the earlier accumulated base, then read the source-qualified checkpoints above in order. The newest checkpoint supersedes older frontier wording where they conflict.

## Top unresolved frontier

1. **Matched Lean outer-controller comparison:** freeze theorem set, Lean/toolchain, executor/worker/verifier models, memory/cache/tool substrate and real budget; compare deterministic/rule control, free-form LLM planning, BC, terminal-trajectory AW and learned typed heterogeneous control.
2. **One-decision/one-action typed boundary:** current OpenProver planner steps can emit ordered action bundles; learned/OPE policies should instead choose one normalized meta-action per decision with deterministic executor expansion.
3. **OPE-identifiable collection:** exact structural state, hard legal mask, randomized subset, deterministic baseline/fallback, chosen action and exact propensity; never reconstruct hidden free-form planner probabilities.
4. **Safe action randomization:** Stage A randomizes only reversible/local/bounded actions; expensive compute purchases, persistent writes and terminal submit remain baseline-only until separately gated Stage B.
5. **Replay-complete state:** replay must reconstruct legal mask, baseline/fallback, randomized set, full behavior distribution, `mu_chosen`, chosen action and deterministic executor expansion from logged structural artifacts only, without raw planner CoT.
6. **Data-adequacy-first OPE:** support/coverage gates estimator choice; weak overlap may use truncated/regularized estimators, zero support requires abstention/new collection.
7. **Credit assignment:** published Harness AW gives each action the same terminal-trajectory weight; Lean can test verifier-grounded step credit/sequential value while preserving terminal kernel-verified outcome as objective.
8. **Real-cost control:** log terminal verified solve/reusable progress separately from tokens/$, Lean/tool time, state reconstruction, concurrency-adjusted wall-clock and occupied worker/model slots; expose the full remaining budget vector to the controller.
9. **Conservative deployment under shift:** learned controller must fall back to baseline in weak-support/uncertain regions; Dalek-Bench is direct evidence that recursive scaffolding can fail to transfer.
10. **Proof-specific routing:** semantic branching+repair, subgoal scheduling, triggered re-retrieval, snapshot reuse, calibrated model/worker/search escalation, restart/replan, decomposition and pruning remain active action families.
11. **Reproducibility:** publish exact BC/Forced-CHECK implementations and pin paper version, repo commit, benchmark split, scorer, controller action contract and budget; the reference Harness-RL artifact does not currently expose a tracked BC/FC reproduction path.

## Current synthesis and newest updates

- OpenProver remains the strongest direct free-form Lean heterogeneous-controller baseline found so far. Public source audit is now pinned at commit `e200251b34349ab6c34548d30319abde86cb6bc6`.
- **C80 — parseable but bundled decisions:** OpenProver has a fixed TOML planner vocabulary and a strict parser, but a single physical planner step may contain multiple sequential action blocks; `plans.json` preserves the full bundle while `planner.toml`/step metadata can reduce it to a primary/last action. OPE must not treat the step-level `action` field as the full policy decision.
- **C81 — no centralized legal mask:** planner documentation varies by mode/isolation, but the parser validates against the global action list and unavailable actions may be rejected later by handlers. Exact propensity collection therefore needs a new authoritative pre-sampling `legal_action_mask(s)` rather than reconstructing legality from prompt text/runtime rejection.
- **C81 budget gap:** `_do_step` passes `budget_status` to `format_planner_prompt`, but the inspected formatter does not insert it. The free-form planner sees coarse >80%/>95% budget interventions, not the full continuous remaining-budget vector. A cost-aware typed controller must log/expose budget structurally.
- **C82 — rich traces but raw planner history:** OpenProver persists planner output/action outputs and feeds recent planner output back into future prompts; planner output can include free-form reasoning. Current metadata already logs planner/worker cost, duration and token usage, but lacks legal/randomized masks, behavior distribution/propensity and replay hashes. Learned typed state should exclude raw planner prose and use canonical structural artifacts instead.
- **D3 — preferred boundary:** normalized actions such as `READ_CONTEXT`, `RETRIEVE`, `UPDATE_SCRATCH`, `SPAWN_BRANCH`, `LOCAL_REPAIR`, `DECOMPOSE_OR_REPLAN`, `STORE_VERIFIED`, `BACKTRACK_OR_PRUNE`, `ESCALATE_COMPUTE`, `SUBMIT`; each label requires a fixed replayable executor procedure. This is a proposed abstraction, not a claim that OpenProver currently names all actions this way.
- General frozen-LLM harness control with offline RL is directly demonstrated by Yi & Song 2026 (`arXiv:2607.05458`); Lean transfer remains untested.
- **C77 — artifact reproducibility gap:** at public Harness-RL commit `5d577632...`, README/main driver/main-table analysis implement Base-vs-AW only; `offline_aw.py` exposes AW but no BC trainer; `docs/ARTIFACT.md` says no single reproduction runner is tracked. Paper BC/Forced-CHECK Table-4 values cannot currently be regenerated from the documented main-table path without reconstructing additional protocol. This does not show the paper values are wrong.
- **C78 — Lean heterogeneous action ontology exists as hand/prompted control:** Max Tan's `arXiv:2605.30914` uses deterministic gates plus task/proof-level progress evaluation to choose local repair/tool search, structural revision/decomposition, or escalation/pruning. The thesis explicitly lists learned progress models/value networks/trained revisers as future work.
- **C78 counterevidence against “more tools/search is enough”:** same-model Vericoding pilot shows direct+tools can underperform direct+repair, recursive decomposition can underperform shallow+repair despite more calls, and balanced E5 allocates budget more efficiently; on Dalek-Bench the recursive scaffold underperforms direct+tools. Controller quality and shift calibration matter.
- **C79 — BFS-Prover-V2 qualification:** its off-policy RL learns the tactic step-prover; its inference Planner is a separate reasoning LLM. It is not RL over heterogeneous outer actions and does not close the targeted gap.
- Prior proof-search evidence still supports verifier-grounded structural diversity, learned compiler repair, progress/value guidance, subgoal factorization/caching, context selection, dynamic restart/repair routing and proof-state snapshot reuse. Preserve exact tested scope; narrow failures never reject a method family.
- `research_feedback_clean_g1/reasoning/FEEDBACK.json` was absent at the frozen control snapshot; no sanitized feedback was consumed.

## Exact continuation

1. Search specifically for any 2025–2026 formal-proof paper/repository that **learns the progress evaluator or outer action selector itself** (not tactic generation) and exposes enough trajectory/action information to determine behavior support.
2. Use the pinned OpenProver source to define a **canonical structural snapshot** (theorem/proof status, whiteboard/repo digests, parsed prior actions/outputs, verifier/proof/subgoal/cache state, exact budget) that excludes raw planner prose; identify missing digest/version hooks.
3. Formalize `legal_action_mask(s)` for D3 with exact mode/isolation/proof-status/memory/budget predicates; do not equate parser-global `ACTIONS` with legality.
4. Define one-decision/one-action executor contracts and deterministic expansion rules. Current OpenProver multi-action bundles remain a free-form baseline, not the learned policy's atomic action space.
5. Formalize the Stage-A plus gated Stage-B behavior mixture and verify exact `mu(a|s)` reconstruction when baseline/randomized sets overlap and deterministic fallback fires.
6. Build deterministic replay tests for state/mask/baseline/randomized-set/propensity/executor expansion; state aliasing adds minimal structural features, zero support causes abstention/new collection.
7. Treat historical OpenProver free-form traces as descriptive/supervised data only; never manufacture propensities for them. New randomized typed collection is required for OPE/causal claims.
8. Add explicit BC and Forced-CHECK baseline implementations to the proposed Lean study and publish their config/protocol.
9. Compare terminal-only trajectory AW against verifier-grounded progress/potential credit and sequential value learning under the same terminal objective, behavior data and real compute budget.
10. Continue semantic branching+compiler repair, subgoal scheduling, triggered re-retrieval, proof-state snapshot reuse, calibrated compute escalation, cost-normalized evaluation and robustness under repository/benchmark shift.
11. Keep the frontier nonempty. Checkpoints/findings/report readiness are never global completion.

Do not read legacy `research_workers/reasoning/`, O/O-derived state, comparator/integrator/index/feed/audits, other-worker state/config, shared execution ledger, or other-role receipts.
