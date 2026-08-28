# self_improvement clean checkpoint — Inspect/Hawk first-call durability + HTTP provider uncertainty

- checkpointed_at: `2026-08-28T20:07:00.177351+09:00`
- sequence: `101`
- frozen note main SHA: `6c593ed993f9d143bde084d7cc5841ed7c611c1c`
- frozen root control revision: `15`
- frozen self_improvement config revision: `7`
- enabled_desired under frozen config: `true`
- post-freeze note head observed: `d12d46ae48b041c249660482937f2033869f9bd6` (not adopted; semantic work stopped after this observation)

## Inputs used

Only the role-local clean `LATEST.json` at sequence 100 and public source trees were used semantically. No O/O-derived state, other-worker state/config/output, downstream state, legacy research, shared execution ledger, or other-role receipts were read.

Public revisions inspected:

- `UKGovernmentBEIS/inspect_ai@86ad4fa73042a445588e2eca18df1502da6bb661`
- `METR/hawk@97a694de1988fc6413e9ba5c67b02fa114b2a8b9`

## Source-bound finding: Inspect/Hawk does not close the pre-first-checkpoint provider gap

Hawk's checkpointing guide says already-completed samples are not re-run, in-progress samples that reached a checkpoint hydrate from it, and samples that never checkpointed restart from the beginning. Checkpointing is agent/solver driven and fires only when a checkpoint-aware loop ticks the Inspect checkpointer. Hawk's crash-resume smoke tests intentionally crash after a durable checkpoint and prove restored host/sandbox state; these are strong tests of post-checkpoint recovery, not of a pre-first-provider-call write-ahead authority.

Inspect's current runner does create a realtime sample row before the plan executes when realtime logging is enabled. That row is `TaskLogger.start_sample -> SampleBufferDatabase.start_sample`, a local SQLite buffer record. It is not the checkpoint authority, does not bind the exact first provider request/idempotency operation, and is not the S3/shared-checkpoint artifact Hawk relies on when a whole runner pod is replaced. The Inspect checkpointer setup itself does no durable checkpoint I/O merely because an active sample exists: the owning agent must enter `checkpointer()` and a durable checkpoint is fired by `tick()`, `checkpoint()`, or clean `agent_complete` finalization.

Therefore the current source supports a bounded negative result: **post-checkpoint recovery is real, but the inspected paths do not establish a durable content-bound evaluation/provider intent before the first model/provider effect.** A provider effect occurring before the first checkpoint can still fall into an accepted-but-locally-unrecorded ambiguity after a hard crash. This is specifically a pre-first-checkpoint window; it is not a claim that all resumed model calls duplicate.

Hawk's own `prior_attempt.py` reinforces the boundary: unfinished samples can start over across whole-pod retries, and its diagnostic records a production case where 4,588 logical samples became 6,013 attempts after three OOM kills.

## Executed reference: real HTTP process boundary + SIGKILL

I extended the sequence-100 controller reference from an in-process/provider-SQLite abstraction to a separate local HTTP provider process and tested two explicit provider contracts. The tested source is:

`research_workers_clean_g1/self_improvement/reference_outer_http_state_machine_2026-08-28T200546_JST.py`

SHA-256 before repository write:

`7cefc6bc21d119bece2a2428039ae22aad45143e0f41945021070de80b9c9150`

The controller durably persists the attempt/cell identity and moves a cell to `DISPATCHING` before issuing HTTP. The provider commits its effect to its own SQLite authority, writes an acceptance marker, and intentionally withholds the HTTP response. The parent then sends a real `SIGKILL` to the controller in the exact window `remote effect durable -> controller response/readback absent`.

### Provider mode A: stable idempotency + reconciliation

Provider contract: stable content-derived HTTP `Idempotency-Key` plus `/reconcile` by that identity.

Observed counts:

- immediately after controller SIGKILL: `effects=1, execute=1, reconcile=0`
- after fresh-process resume through all 3 cells: `effects=3, execute=3, reconcile=1`
- after a second fresh-process `certify`: unchanged `effects=3, execute=3, reconcile=1`

All three cells ended `COMPLETED`. The accepted-but-unrecorded first cell was recovered by reconciliation rather than a second execute effect. Total execute count was exactly one per cell, and second-certify provider-call delta was zero.

### Provider mode B: neither idempotency nor reconciliation

Provider contract: no stable idempotency and no reconciliation endpoint usable by the controller.

Observed counts:

- immediately after controller SIGKILL: `effects=1, execute=1, reconcile=0`
- fresh-process resume: exits nonzero with `Unknown: post-dispatch outcome unknown; blind retry forbidden`
- provider counts after failed resume remain exactly `effects=1, execute=1, reconcile=0`
- the uncertain first cell transitions durably to `UNKNOWN`; untouched cells remain `PLANNED`

This confirms the needed branch: **when provider semantics cannot prove safe replay or recover the outcome, restart must fail closed and must not blindly execute a `DISPATCHING` cell again.**

Full report:

`research_workers_clean_g1/self_improvement/reference_outer_http_sigkill_report_2026-08-28T200546_JST.json`

Contract:

`research_workers_clean_g1/self_improvement/inspect_hawk_provider_uncertainty_contract_2026-08-28T200546_JST.json`

## Scope boundary

The HTTP provider is a local process with an authoritative SQLite effect table. This is a real inter-process HTTP/SIGKILL ordering test and a stronger transport boundary than the sequence-100 SQLite simulator, but it is **not** evidence that arbitrary external providers implement exactly-once synchronous inference. The conclusion is conditional on the provider contract: stable idempotency/reconciliation makes recovery safe; absent such a contract, the correct result is durable uncertainty/fail-closed.

## Termination / blocker for this physical invocation

After semantic work completed, a SHA-only head freshness check observed note main `d12d46ae48b041c249660482937f2033869f9bd6`, differing from the frozen semantic SHA `6c593ed993f9d143bde084d7cc5841ed7c611c1c`. Per frozen control revision 15, the newer control was not fetched or interpreted. No further semantic research is performed in this invocation; only frozen-tuple checkpoint/receipt persistence and readback are allowed. This is not global completion and does not justify scheduler disable while `enabled_desired=true`.

## Nonempty frontier / exact next action

On the next fresh-control invocation, first resolve the then-current root/control and self_improvement config tuple. Then source-bind concrete synchronous provider APIs for durable idempotency and retrieve/reconcile behavior specifically across `provider accepted -> local outcome absent`, classifying each provider path as `idempotent+reconcile`, `idempotent-only`, `reconcile-only`, or `neither`. Extend the HTTP reference with (1) `DISPATCHING` persisted but provider has no effect because crash occurs before wire-send/acceptance, and (2) provider process crashes immediately after durable effect commit before response. Require safe same-key retry only when the provider contract proves it; otherwise preserve `UNKNOWN`/fail-closed semantics. Also bind returned provider outcome to request digest/provider operation identity so reconciliation cannot accidentally attach a semantically different result.
