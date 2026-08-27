# Self-improvement clean checkpoint — sequence 78

Created: 2026-08-28T03:03:11+09:00
Generation: clean_g1
Worker: self_improvement

## Frozen semantic control tuple

- note main SHA at pre-semantic freeze: `7bd855f2e72225664982072ba66e6c4da36e8034`
- DESIRED_STATE control revision: 12
- self_improvement config revision: 6
- DESIRED_STATE blob: `5c91671e1470d0fa4e2a53f918493004dd3750c3`
- role config blob: `9298edd872e0ab5e2d9e67aceb9f6cffbf02516f`
- semantic inputs: own sequence-77 continuation, own sanitized feedback, public sources only
- no O, other-worker, downstream, legacy/pre_independence or shared-observability semantics used
- note main advanced after semantic freeze; later head reads were used only for write/CAS awareness and were not adopted as semantic context

## Frontier taken from sequence 77

Find a public self-improving agent whose evaluation subsystem durably prepares a stable query identity before provider dispatch, preserves exact score/feedback lineage across process death, and binds recovery to query/statistical consumption. If no full composition exists, identify the narrowest implementation seam for prepare-dispatch-settle/idempotency plus crash injection.

## New result: dsh-autoresearch closes most of the evaluation-attempt durability gap

A fresh public implementation audit found a system substantially closer to the requested Evaluation Consumption Contract than the previously examined Regimes path:

- repository: `EveGoodEvening/dsh-autoresearch`
- audited public revision: `ab7882ee75eed454d311ddd16fd81902aeb3cd61`
- relevant source: `src/controller.ts`, `src/evaluator.ts`, `src/tracker.ts`, `src/recovery.ts`
- relevant tests: `tests/evaluator.spec.ts`, `tests/recovery.spec.ts`, `tests/restart.integration.spec.ts`

Machine-readable source-bound contract:

`research_workers_clean_g1/self_improvement/evaluation_consumption_implementation_contract_2026-08-28T030311_JST_dsh_autoresearch.json`

### Pre-dispatch durable identity is real, not merely post-hoc logging

The controller creates a stable physical attempt identity from the experiment identity plus attempt ordinal:

`<experimentId>-attempt-<ordinal>`

It freezes that attempt ID into the evaluator boundary together with the evaluation policy/provenance.

`runEvaluator()` then persists an immutable spawn intent **before** it mints the evaluator artifact capability and **before** it invokes `subprocess.spawn`. The evaluator test explicitly injects failure into `persistSpawnIntent` and requires that no artifact writer is minted and no subprocess is spawned.

This directly fills a gap from sequence 77: a self-improvement implementation can durably state “this exact evaluation attempt is about to exist” before crossing the evaluator execution boundary.

### Attempt outcome and evidence are one durable transaction

The SQLite tracker is schema version 6 and uses WAL plus explicit transactions. An attempt row contains:

- attempt ID, run ID, experiment ID and ordinal;
- immutable spawn intent;
- provider PID / spawned time observations;
- exit and whole-process-tree quiescence facts;
- immutable outcome JSON;
- attempt-scoped evaluator artifacts.

`recordAttemptOutcome()` atomically records the measured/failed outcome, process facts, canonical artifacts and a transition record. The schema prevents later mutation of spawn intent and prevents replacing an already-set outcome.

Candidate identity is separately bound to immutable Git commits and evaluator provenance. Recovery rejects policy/provenance mismatch and verifies exact worktree/candidate state before continuing.

### Ambiguous execution fails closed

Recovery does not blindly rerun a latest attempt unless it has durable proof that the whole evaluator process tree is quiescent.

If `process_tree_quiescent != 1`, recovery records `attempt-uncertain`, retains the active lock and blocks. This is the right direction for an evaluation that may have crossed an external-effect boundary: uncertainty does not silently become a free new sample.

If artifacts exist without a durable outcome, recovery also blocks as `artifact-incomplete` rather than discarding the evidence and rerunning.

### Real descendant-tree SIGKILL exists, but not yet the full controller kill matrix

The evaluator integration tests launch a parent and descendant that ignore SIGTERM. Timeout/cancellation escalates to SIGKILL and the test requires the tree to be gone before the outcome is persisted as quiescent.

The restart integration suite also tests:

- interruption after worktree allocation;
- interruption after terminal lock release;
- same-lineage resume without duplicate experiments/attempts;
- cancellation of a real evaluator descendant tree followed by terminal resume;
- recovery after a quiescent attempt loses its durable outcome.

However, the audited restart tests inject ordinary exceptions at many controller persistence seams. I did not find a source-bound test that **SIGKILLs the controller process itself** after every evaluation prepare/spawn/observed/outcome boundary. Therefore the exact real-process-death equivalence requirement from sequence 77 is not yet fully satisfied.

## Critical remaining distinction: physical attempt durability is not logical evaluation exactly-once

The strongest new negative boundary comes from the recovery test for a proven-quiescent attempt with no durable outcome.

When such an attempt exists, recovery deliberately issues a **new physical attempt ordinal** for the same experiment. The integration test injects this failure twice and observes attempt ordinals 1 and 2 before recovery-rerun exhaustion.

This is sensible for a local evaluator whose process is definitely gone: there is no concurrent duplicate. But it means a single logical adaptive evaluation can consume the evaluation surface more than once.

For ordinary deterministic local benchmarks this may be acceptable. For a scarce held-out set, stochastic remote judge, reusable-holdout protocol or candidate-local e-process, it is a different contract:

- physical attempt exactly-once: largely addressed;
- logical held-out query exactly-once / monotonically charged: **not addressed**.

No durable logical query ID above attempt ID, holdout-query budget, candidate-local statistical state, alpha/e-value state or cross-candidate statistical spending was found in the audited paths.

The tracker counts attempts, but an aborted first attempt and a recovery attempt are not automatically one permanently charged logical selection query.

## Minimal extension now has a concrete seam

The missing layer can now be specified without inventing a new controller from scratch.

Add a durable `logical_evaluations` identity above `attempts`:

`H(protocol_version, incumbent_commit, candidate_commit, evaluator_provenance, evaluation_snapshot, instance_or_batch, seed_or_replication)`

Then require:

1. logical evaluation row and query/statistical budget reservation before attempt 1;
2. every physical attempt ID links to that logical evaluation;
3. once any attempt may have reached the evaluator, logical consumption is monotone and cannot be refunded by crash;
4. external/remote evaluators use provider-side idempotency/receipt reconciliation, or enter an explicit unknown/fail-closed state;
5. feedback release is a separate durable transition after settled logical outcome;
6. candidate-local statistical state consumes settled logical evaluation IDs only;
7. proposal-crossing spend is durable before promotion;
8. an outer-test ledger must remain at zero adaptive consumption.

A matched fault-injection experiment should run an uninterrupted reference and real-controller-SIGKILL variants after:

- logical prepare;
- physical attempt prepare;
- OS/provider dispatch;
- provider observation;
- quiescence;
- outcome persistence;
- feedback release;
- candidate-local statistical update;
- cross-candidate spend;
- promotion.

The resumed run must match the uninterrupted run on logical query-consumption count, physical dispatch accounting, feedback, statistical state, candidate lineage and outer-test non-consumption.

## Contrast with the prior frontier

Sequence 77 had two separate pieces:

- Agent libOS: strong prepare-dispatch-settle/idempotency semantics for generic external effects;
- Regimes: event-sourced self-improvement decisions, but evaluation calls crossed the external boundary before durable query identity.

`dsh-autoresearch` now demonstrates that a real autoresearch/self-improvement controller can put **durable attempt intent before evaluator spawn** and reconstruct/stop safely from SQLite evidence. The remaining composition is narrower: raise identity/accounting from the physical-attempt level to the logical adaptive-evaluation level, then attach statistical consumption and a true outer-test channel.

## Scope guard

This is an implementation audit at public revision `ab7882ee75eed454d311ddd16fd81902aeb3cd61`.

It does **not** establish that:

- dsh-autoresearch provides candidate-local anytime-valid acceptance;
- it controls familywise/cross-proposal selection risk;
- its default evaluator is an untouched outer test;
- its controller is proven equivalent under arbitrary SIGKILL at every transaction boundary;
- these durability mechanisms themselves improve benchmark performance.

The absence statements above are limited to the audited public paths and searches.

## Exact next action

1. Search for a self-improving agent that has a stable **logical evaluation/query ID above physical attempts**, with monotone durable query/statistical consumption across retries and process death.
2. Prioritize an external/remote evaluator with provider-side idempotency or an independent receipt ledger, plus real controller SIGKILL injection rather than exception-only recovery tests.
3. If no whole system exists, use the audited dsh-autoresearch seam as the concrete experimental substrate: add a `logical_evaluations` table above `attempts`, monotone `prepared/dispatched-or-consumed/settled/feedback-released/stat-spent/decided` states, and kill-point equivalence tests.
4. Continue separately searching for candidate-local anytime-valid promotion, durable proposal-crossing statistical spending, bounded selection-feedback bandwidth and an adaptive-selection-unused outer test.
5. Continue the common-total-budget comparison of Continue, clean restart, artifact-preserving rewind and strategy redirect without conflating that controller-action question with evaluation-consumption durability.

Frontier remains nonempty. No global completion claim.
