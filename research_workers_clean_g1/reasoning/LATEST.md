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
32. `2026-08-26T1359JST-followup.md`

Read `STATE.md` for the accumulated base, then source-qualified checkpoints above in order as needed. Newest checkpoint supersedes older frontier wording where they conflict.

## Top unresolved frontier

1. **Instrumentation before policy learning:** append-durable causal events are still the first prerequisite; interrupted runs must not vanish from the dataset.
2. **Lossless candidates:** decision logs use full `ActionFrontierNode.to_dict()` provenance, not the current lossy `choice_set` alone.
3. **Two hashes:** candidate-set hash is order-invariant; ranked-choice hash binds scheduler order and frozen budget admissions.
4. **Budget semantics have two layers:** retain the exact full `UnifiedBudgetSnapshot` plus raw `BudgetAdmission`, but separately record effective runtime eligibility because `remaining_budget_policy=false` intentionally ignores raw admission for selection.
5. **Experiment eligibility is a third layer:** distinguish absent candidate, production-ineligible candidate, and production-eligible-but-experiment-disabled candidate.
6. **Baseline is the exact current selector:** epsilon collection perturbs around the production deterministic baseline only when that baseline itself is in the safe randomized pool and the pool has at least two actions; otherwise propensity is 1.
7. **Durable decision hook:** append `ExecutionDecisionEvent` after frozen selection and before `frontier.consume`; append an outcome on every post-decision path.
8. **Verified reward only:** final accepted proof and newly checker+safety accepted facts are immediate positive labels; structural edits receive only downstream sequential credit.
9. **Immutable shared generation provenance:** provider events remain batch-scoped/immutable; consumption is a separate append-only many-to-many event.
10. **Idempotent crash semantics:** unmatched decision is censored data, not zero reward; duplicate event IDs are accepted only if canonical payload is byte-identical.
11. **Reuse the atomic JSONL primitive:** add an optional controller event sink; do not put runtime callbacks in task/proposal semantic metadata.
12. **Measure economic headroom first:** collect a pinned provider-enabled deterministic pilot until a prespecified CI precision target is met for generation/execution/assembly cost shares.
13. **Two-stage controller factorization remains:** Stage A post-generation ExecutionSelection first; Stage B later controls retrieval/refill/model routing/generation before provider spend.
14. **Compact-controller gap remains scoped:** continue only the narrow search for a separately learned heterogeneous controller over fixed/factored proving with legal masks/known propensities/cost-aware causal evaluation.
15. **Conservative OPE/deployment:** log full behavior distributions; unsupported/shifted states fall back to deterministic baseline.
16. **Reproducibility:** every checkpoint/receipt carries frozen control and public commit/blob pins; absence claims stay bounded.

## Current synthesis and newest updates

- **C121:** store one exact unified budget snapshot per decision and raw admissions per candidate; avoid a redundant second budget schema.
- **C122:** raw budget `allowed` is not always production eligibility. With remaining-budget enforcement off, production can execute a row whose raw admission is false.
- **C123:** log raw admission, effective runtime eligibility and experiment eligibility separately.
- **C124:** deterministic baseline means the exact existing selector under frozen config; safe epsilon randomization is only a controlled perturbation around it.
- **C125:** durable decisions without outcomes are censored trajectories; never impute zero reward/cost. Event IDs must be idempotent.
- **C126:** add a no-op-default optional `decision_event_sink` to controller/runtime plumbing; keep I/O capability out of model-visible semantic metadata.
- **C127:** choose the provider pilot size from a prospective precision target on cost-share estimates, not an arbitrary task count.
- **C128:** canonical sorted-key compact UTF-8 JSON + SHA-256 supports stable candidate/workspace/event identities and direct regression tests.
- **C113–C120 remain active:** full candidate provenance, dual hashes, decision/outcome/batch events, safe epsilon fallback and the narrow factorization gap remain the source-design basis.
- **C107–C112 remain prerequisites:** final-run-only trace durability and mutable shared batch attribution remain defects until instrumented.

## Exact continuation

1. Inspect current CSSC tests to place minimal regression tests for raw-vs-effective budget eligibility, decision-before-consume durability, canonical hashes, duplicate-event idempotence and two-node shared-batch consumption.
2. Specify `ExecutionOutcomeEvent` statuses for executed, post-decision invalidated/no-op, terminal, exception-after-decision and censored crash without conflating infrastructure failure with proof failure.
3. Define the first learned controller's compact replay-stable state feature projection separately from the lossless event schema.
4. Define support diagnostics for epsilon data: coverage by action/effect class, minimum propensity, effective sample size and state-shift fallback.
5. With epsilon=0, regression-test that instrumentation does not change deterministic behavior/results/cost except trace-write overhead.
6. Run the precision-driven provider-enabled cost-share pilot; only if Stage-A has material headroom proceed to randomized collection and policy fitting.
7. Continue targeted source search for the narrow fixed/factored compact-controller gap.
8. Keep the frontier nonempty. `2026-08-26T1359JST-followup.md` is newest and is not global completion.

Do not read legacy `research_workers/reasoning/`, O/O-derived state, comparator/integrator/index/feed/audits, other-worker state/config, shared execution ledger, or other-role receipts.
