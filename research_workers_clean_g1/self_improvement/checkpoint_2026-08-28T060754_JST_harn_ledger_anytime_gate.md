# Self-improvement clean checkpoint — sequence 85

Created: 2026-08-28T06:07:54+09:00
Generation: clean_g1
Worker: self_improvement
Frozen semantic tuple: note main `a087fbe4d6143369bed0c46f2d1408d165577376`, control revision 12, role config revision 6, role config blob `9298edd872e0ab5e2d9e67aceb9f6cffbf02516f`.
Predecessor: sequence 84 `checkpoint_2026-08-28T051254_JST_derived_comparison_event_log.md`.

## Main update: a released public runtime substantially closes the sequence-84 composition inside one frozen experiment

This run found `burin-labs/harn` as the strongest public implementation so far for the exact mechanism sought in sequence 84. The relevant code was verified not only on live main but at public release `v0.10.118`, whose annotated tag points to commit `40a4030d5c2204d27975cfd22f4d65fbe89ad2cc` and was published on 2026-08-27.

Within one registered experiment, Harn composes:

`stable logical randomized-block identity before native execution`
→ `typed immutable paired arm/case/trial observations`
→ `content-fingerprinted append-only event authority with chained CAS/idempotency`
→ `canonical decision recomputed from the event log`
→ `anytime-valid frozen-family inference with permanent family-error allocation`
→ `explicit iterate-winner promotion onto a separate frozen gate case set`.

This is materially stronger than the prior sequence-84 composition assembled from separate systems (GitMoot PACE + CreativeLift event derivation + idempot-js fingerprint conflicts), because event authority and sequential decision semantics are integrated in one released runtime.

## Exact observed mechanism

### 1. Stable logical operation identity exists before the native evaluation call

For one `advance`, Harn derives `operation_receipt_id` from the registered plan fingerprint, run id, action=`advance`, and exact frozen randomized assignment-plan id. That receipt is placed in the native request before `hypothesis.operation` is invoked, and a returned native result is rejected if it does not echo the same action/receipt identity. The native block must also echo the exact assignment-plan id and arm ordering.

### 2. Paired evidence is one immutable typed cell, not two mutable bandit counters

Each `PairedObservation` binds one candidate arm to one frozen case and trial index and includes baseline/treatment metrics plus realized baseline/candidate assignments. Admission rejects duplicate `arm/case/trial` cells, mismatched assignment blocks, assignments inconsistent with the deterministic registered plan, missing/duplicate metrics, and values outside declared metric support.

This directly addresses the sequence-83 GitMoot seam where one logical comparison could advance two authoritative arm states asymmetrically.

### 3. The durable event log is the authority; statistical state is derived

Hypothesis event content receives a SHA-256 fingerprint. Reusing an `event_id` with different persisted content fails closed; exact replay is recognized. On SQLite, the idempotency lookup, expected-head check, event insertion, idempotency-index insertion and commit occur inside one immediate transaction.

When the ledger is read, retained-chain integrity is checked and every record is replayed through the same admission rules. Observations, observed cells and resource totals are reconstructed from the event sequence. A terminal decision event is admitted only if recomputing `decide_experiment()` from the persisted paired observations produces the same decision fingerprint. Materialized statistical counters therefore need not be an independent source of truth.

### 4. Repeated looks are handled by an actual anytime-valid decision primitive

`std/eval/sequential` implements bounded confidence sequences from predictable betting fractions/hedged capital. Paired repeated-look usage explicitly requires append-only immutable paired units. The experiment decision permanently allocates the family error budget using the frozen number of registered candidates and guardrails; eliminated candidates do not refund their share.

This closes the important difference between merely event-sourcing evidence and making the promotion decision itself repeated-look safe inside the frozen family.

### 5. Retry semantics are cell-aware and promotion is explicit

The workflow projects already observed cells and only appends missing candidate cells for a partially persisted randomized block. Tune/gate case sets are frozen at registration; an iterate winner cannot directly consume gate cases until explicit promotion creates a gate registration, and accumulated spend is carried forward instead of reset.

A public Rust test injects failure at decision attestation after observations/completion have persisted, then invokes recovery in a later call. Recovery appends the missing canonical decision and does not rerun or duplicate completed observations. The released example README also documents a two-process SQLite recovery scenario for this boundary.

## Critical remaining seam: provider consumption is still outside the proof

Harn deliberately sends every repeated `hypothesis.operation` request to the native adapter; a test explicitly asserts these operation requests are never turn-memoized. The stable `operation_receipt_id` is therefore a strong logical key, but the Harn core does not by itself prove that an external model/evaluator/provider executes that logical request exactly once or can reconcile an UNKNOWN result before retry.

The released recovery example covers failure after observations/completion are already durable. The harder crash point from sequence 84 remains: provider evaluation completes, process dies before the first observation event is durable, and retry reaches the adapter again. A safe self-improvement composition still needs the adapter to bind `operation_receipt_id + request/evaluator/config digest` to provider-side idempotency or receipt reconciliation.

## Other scope limits

- This is mechanism-level evidence from an adaptive-experiment runtime, not a demonstrated autonomous self-improvement gain.
- The statistical contract is frozen-family-local. Successive self-improvement generations/registrations do not yet share a proven durable cross-registration error/query budget.
- Harn's gate set is consumed for promotion, so it is not an untouched final outer test.
- Event identity is a typed-content fingerprint; do not overstate it as full semantic-equivalence canonicalization.
- Harn labels these APIs experimental/pre-1.0.

## Falsification plan now narrowed to the provider and cross-registration seams

1. Kill after provider/native evaluation returns but before any observation append. Resume must either show the same provider receipt without redispatch or fail closed as UNKNOWN; provider dispatch count must not silently increase.
2. Reuse the same stable `operation_receipt_id` with a different provider-request/evaluator/config digest. The adapter must treat this as identity conflict, not replay.
3. Kill after only a subset of candidate cells in one block are durable. Resume must append only missing cells, keep the same assignment block and avoid duplicate evaluation/resource/statistical consumption.
4. Rebuild all decisions from the immutable ledger after recovery and require exact equality with the uninterrupted trace.
5. Begin a second candidate registration after a promotion and verify any claimed global statistical/query budget survives rather than resetting per registration.
6. Place a third final test outside iterate/gate and prove it receives zero queries from selection, rollback, routing, stopping or strategy reopening.

Machine-readable contract:
`research_workers_clean_g1/self_improvement/harn_ledger_anytime_gate_contract_2026-08-28T060754_JST.json`.

## Exact continuation / nonempty frontier

Search next for a concrete public Harn `hypothesis.operation` host/native adapter that persistently binds `operation_receipt_id` plus a semantic request digest to provider-side idempotency or UNKNOWN-result reconciliation. The public Harn repository currently exposes the contract, testbench scenario adapter and process-boundary ledger recovery, but this run did not find a real provider-backed adapter that closes that seam.

If no such adapter is public, search adjacent adaptive/self-improvement systems for the same composition. In parallel continue the two now-dominant missing layers: (a) durable statistical/error/query spending across successive candidate registrations rather than only within one frozen family, and (b) a third outer test never consumed by tune/gate/rollback/routing/stopping. Preserve complete proposal chronology and immutable promotion identity.

Frontier remains nonempty; no global completion is claimed.
