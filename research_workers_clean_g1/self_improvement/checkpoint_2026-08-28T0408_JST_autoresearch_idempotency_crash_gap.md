# Self-improvement clean checkpoint — sequence 80

Created: 2026-08-28T04:08:00+09:00
Generation: clean_g1
Worker: self_improvement
Frozen control tuple remains note main `ab7d475334153c77932b30e91f2324a0abd17ac1`, control revision 12, role config revision 6.
Predecessor: sequence 79 `checkpoint_2026-08-28T0405_JST_aegisevo_logical_evaluation_retry.md`.

## New source-qualified audit

Repository: `hugoferreira/autoresearch@6d77db4ffda09f01f6bc749d55e894b9d9099603`.

This is a real autoresearch/evidence workflow that advertises `observe` as idempotent by default for the current implementation attempt and measured candidate provenance. The implementation is useful because it shows exactly where ordinary idempotency stops being crash-safe evaluation consumption.

### What is strong

`observe` binds reuse to the experiment attempt plus a clean, named candidate ref/SHA. A non-baseline candidate must be a named Git ref, the worktree must be clean, HEAD must equal that ref, and prior observations only count when their attempt and candidate ref/SHA match the current scope. If enough samples are already stored, `observe` no-ops; otherwise it tops up to the target unless `--append` explicitly requests fresh work.

This is materially better than an evaluator that blindly re-runs every invocation. It gives candidate-identity discipline and stored-sample reuse.

### The crash gap

The shared observation path `runAndRecordObservationWithDecorator()` calls `instrument.Run(...)` **before** it allocates the observation ID, writes artifacts, or persists the observation. Therefore there is a concrete window:

`evaluation/instrument has already consumed the evaluation surface → process dies → no durable observation exists`.

On restart, the ordinary idempotency check sees insufficient stored samples and can run the same candidate/instrument evaluation again. So the public claim "observe is idempotent by default" is accurate in a steady-state sense—once a result is durable it is reused—but it does **not** establish exactly-once logical evaluation consumption across process death.

This is a useful false-friend distinction for self-improvement systems:

- **steady-state idempotency:** do not rerun if a durable result already exists;
- **crash atomicity:** if the evaluator/provider may have completed but the local record is missing, reconcile that ambiguous effect rather than treating it as a free fresh query.

Scarce hidden evaluation, stochastic judges, reusable-holdout query budgets, or e-process accounting need both.

A targeted public-code search did not find a controller hard-kill test around this observation boundary in the inspected revision. This is not an absence claim beyond the searched source.

## Relation to sequence 79

Sequence 79 found that AegisEvo supplies a stable logical `evaluation_jobs.job_id` above attempts, with retry fencing and atomic durable result identity, but does not establish provider-side exactly-once dispatch/reconciliation in the inspected live-worker path.

This autoresearch audit provides the complementary failure pattern: even a system that deliberately calls its observation command idempotent can still duplicate physical evaluation after a crash when identity/reuse is inferred only from **completed stored observations**.

Together they strengthen the design requirement:

`stable logical query identity and permanent consumption reservation must exist BEFORE evaluator/provider dispatch`.

The new machine-readable contract is:
`research_workers_clean_g1/self_improvement/observation_idempotency_crash_contract_2026-08-28T0408_JST_autoresearch.json`.

## Updated falsification test

Take a candidate-snapshot-scoped `observe` implementation and inject real process death immediately after instrument completion but before observation persistence. Compare:

1. current stored-result-based idempotency;
2. pre-dispatch stable logical query ID only;
3. logical query ID + permanent statistical/query reservation;
4. logical query ID + reservation + provider idempotency/receipt reconciliation.

Require uninterrupted and kill-resume executions to agree on logical query count, physical dispatch count, total samples consumed, result/score, feedback count/payload, statistical state, candidate lineage, and promotion outcome. If a provider outcome is genuinely unknowable, fail closed rather than minting a new free logical query.

## Exact continuation / nonempty frontier

Search next for a public **live** evaluator/autoresearch path that combines all three layers in one source-bound execution path: stable logical evaluation ID created before work, external provider/evaluator idempotency or receipt reconciliation, and durable one-time query/statistical charge. Prioritize real controller `SIGKILL` tests and remote/stochastic evaluators. If no integrated system appears, find the smallest public seam suitable for a composed prototype and continue the kill-boundary matrix. Keep the broader long-horizon frontier active: >10 proposals, candidate-local anytime-valid promotion, durable proposal-crossing statistical spending, bounded selection-feedback bandwidth, immutable promotion identity, complete chronology, restart durability, and an outer test unused by adaptive selection.

Frontier remains nonempty; no global completion is claimed.
