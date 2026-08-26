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
29. `2026-08-26T1157JST.md`
30. `2026-08-26T1259JST.md`
31. `2026-08-26T1359JST.md`

Read `STATE.md` for the accumulated base, then source-qualified checkpoints above in order as needed. Newest checkpoint supersedes older frontier wording where they conflict.

## Top unresolved frontier

1. **Instrument before learning:** append-durable per-decision logging remains the first prerequisite; completed-run summaries are insufficient because interrupted high-cost trajectories would be preferentially lost.
2. **Canonical full candidate rows:** use `ActionFrontierNode.to_dict()` plus frozen rank, budget admission, effect class and experiment gate; do not train from the current lossy `choice_set` projection alone.
3. **Two identity hashes:** log a candidate-set hash independent of order and a ranked-choice hash that binds exact scheduler ordering and budget admissions.
4. **Decision event before mutation:** emit `ExecutionDecisionEvent` after the frozen selection snapshot but immediately before `frontier.consume`, with stable run/decision ids, workspace hash/version, complete candidates, exact legal pool, deterministic baseline, full behavior distribution, chosen propensity, budget and pre-ledger boundary.
5. **Outcome event on every path:** preserve post-workspace hash/version, verified progress, terminal acceptance and exact execution-ledger ids even for a post-decision no-op/invalidation path.
6. **No structural pseudo-reward:** immediate positive labels are kernel/checker+safety verified facts and final accepted proof; decomposition/argument/representation edits receive credit only through future verified return.
7. **Immutable shared generation cost:** provider ledger events stay batch-scoped and immutable; use append-only `ProposalBatchConsumptionEvent` joins for every node consumption.
8. **Safe known-propensity randomization:** epsilon-randomize only when the deterministic baseline itself is in the P0 low-effect legal pool and there are at least two pool actions; otherwise baseline propensity is 1 with an explicit skip reason.
9. **Reuse existing atomic trace primitive:** expose per-event atomic append/inject a decision sink rather than inventing a second persistence backend.
10. **Headroom requires fresh provider data:** no bounded public committed run corpus currently supports real cost-share estimation; collect a small pinned provider-enabled sample and measure generation/execution/assembly shares before expecting Stage-A savings.
11. **Two-stage controller factorization remains:** Stage A learns post-generation ExecutionSelection after instrumentation; Stage B later exposes retrieval/refill/model routing/generate-vs-skip before provider spend.
12. **Compact-controller gap remains narrow:** broad full-agent RL and LLM strategy selectors exist; continue searching only for a separate compact heterogeneous learned controller over fixed/factored low-level proving with legal masks/propensities/cost-aware causal evaluation.
13. **Conservative OPE/deployment:** exact propensities and support checks are mandatory; unsupported or shifted states fall back to the deterministic baseline.
14. **Reproducibility:** every checkpoint/receipt carries the frozen semantic-control tuple and pinned public source commit/blob ids; absence claims remain bounded.

## Current synthesis and newest updates

- **C113:** full candidate provenance is already serialized by `ActionFrontierNode.to_dict()`; current `choice_set` discards obligation/source/batch/model/proposal/priority details.
- **C114:** candidate identity and baseline ordering require separate canonical hashes.
- **C115:** exact decision hook is after frozen `select_admissible_action` and before `frontier.consume`; full workspace fingerprint is available from canonical `ProofWorkspace.to_dict()`.
- **C116:** outcome logs should use final accepted proof and newly checker+safety accepted facts as immediate verified labels; structural edits need sequential credit.
- **C117:** shared model-batch provenance should be an append-only many-to-many consumption relation, never latest-consumer metadata rewriting.
- **C118:** `JsonlTraceStore` already has an atomic fsync+replace append primitive; durability needs per-decision invocation, not a new storage mechanism.
- **C119:** epsilon collection must fall back to deterministic baseline when baseline is outside the safe randomized pool, even if two other safe actions exist.
- **C120:** a fresh bounded search still did not identify a compact separately learned heterogeneous formal-proof controller with fixed/factored substrate plus exact logged propensities; this remains a scoped evidence gap, not a universal nonexistence claim.
- **C107–C112 remain prerequisites:** final-run-only trace durability, incomplete causal event fields, strong execution-ledger join, mutable batch attribution and lack of public real-cost traces are still active.
- **C84/C85 remain important controls:** supervised strategy classification can look accurate while losing end-to-end; optimize verifier-grounded utility per real cost, not imitation accuracy.

## Exact continuation

1. Inspect `BudgetAdmission.to_dict()` and unified-budget serialization to freeze decision-event budget/exclusion schema without duplicating contradictory fields.
2. Define canonical JSON hashing and tests: candidate-set hash invariant to row reordering; ranked-choice hash sensitive to scheduler order/admission changes.
3. Locate the least invasive optional durable `decision_event_sink` plumbing and define crash/restart semantics for decisions without outcomes.
4. Specify replay/idempotence rules: duplicate `(decision_id,event_type)` must be rejected or byte-identical, never silently appended twice.
5. Define a precision-driven minimum provider-enabled collection for cost-share estimates (`proposal_generation / selected_execution / assembly / other`).
6. Regression-test deterministic baseline equivalence after instrumentation, then run epsilon logging; train policies only after trace integrity/support diagnostics pass.
7. Continue targeted source search for the narrow compact-controller factorization gap.
8. Keep the frontier nonempty. `2026-08-26T1359JST.md` is the newest checkpoint and is not global completion.

Do not read legacy `research_workers/reasoning/`, O/O-derived state, comparator/integrator/index/feed/audits, other-worker state/config, shared execution ledger, or other-role receipts.
