# Phase-1 atomic-capability scope mismatch and mixed-sink objective partitioning

- role: `multi_agent`
- phase: `phase_1_chat_parity`
- root_problem_id: `o-chat-parity-root-v2-active-pool`
- assignment_task_id: `phase1-clean-multi-agent-concurrency-claims`
- bootstrap_valid: `true`
- frozen semantic main SHA: `9aecbfd72ebddea92de34792a4587f81e58a744c`
- frozen DESIRED_STATE: control revision `22`, blob `e4f6d24c137284d002941ac04254e3dbeca2cfcb`
- frozen role config: config revision `6`, blob `9a3edbe40ee5cbf3a94fe3206606aa58841c955c`
- post-freeze authority identity verified: `true`
- predecessor leaf: `PHASE1_ATOMIC_OBJECTIVE_PRECOMMIT_COMPENSATION_20260829_055930_JST.md`
- semantic inputs: own role-local Phase-1 state, finite synthetic mechanism model, and public primary documentation only.

## Leaf objective

The prior leaf showed that a genuine shared transaction domain can prevent A-only exposure, while compensation can repair some reversible partial states. This leaf tests the scope boundary that appears when only part of the objective fits that transaction domain.

Model one atomic `core` plus one non-transactional external `tail`. The core can commit atomically inside its own service, but global objective success requires both core and tail.

Compared policies:

1. `pretend_global_atomic` — treats atomic core commit as if it made the cross-domain objective atomic;
2. `atomic_core_fenced_tail` — uses the atomic core only for its own scope, then independently fences/reconciles the tail;
3. `saga_partition` — same scoped core, but compensates the core only when the tail is authoritatively known absent and compensation is final;
4. `manual_after_core` — explicit manual disposition after any unresolved tail.

## Public mechanism boundary

DynamoDB `TransactWriteItems` completes up to 100 item actions atomically, but only within its documented same-account/Region transaction scope. It does not turn an unrelated external API call into the same transaction.

PostgreSQL documents two-phase commit as a mechanism for transactional resources under an external transaction manager. `PREPARE TRANSACTION` persists a prepared transaction for later `COMMIT PREPARED` or `ROLLBACK PREPARED`, but PostgreSQL also warns that prepared transactions hold resources/locks and should normally be resolved promptly.

Azure's Compensating Transaction pattern is the relevant cross-domain fallback when a later step cannot participate in the same atomic transaction: compensation is eventually consistent, can fail, should record resumable progress, and sometimes requires human intervention.

Sources:
- https://docs.aws.amazon.com/amazondynamodb/latest/APIReference/API_TransactWriteItems.html
- https://www.postgresql.org/docs/current/two-phase.html
- https://www.postgresql.org/docs/16/sql-prepare-transaction.html
- https://learn.microsoft.com/en-us/azure/architecture/patterns/compensating-transaction

## Finite model

The script enumerates **2,400 equal-weight synthetic scenarios** over:

- objective contract: global atomic / saga-allowed / manual-allowed;
- core transaction response clear vs ambiguous;
- authoritative core-status availability and possible actual commit;
- authority drift or integrator takeover between core and tail;
- tail response clear vs ambiguous;
- authoritative tail-status and idempotent retry availability;
- possible actual tail application under ambiguity;
- core compensation availability and finality success / failed / ambiguous.

Counts are finite mechanism counts, not production rates.

### Aggregate comparison

| policy | unsafe | false global-atomic | objective-resolved | autonomous terminal | core-only residual | manual |
|---|---:|---:|---:|---:|---:|---:|
| pretend global atomic | **2,184** | **2,184** | 216 | 2,400 | 1,224 | 0 |
| atomic core + fenced tail | 0 | 0 | 1,216 | 624 | 1,272 | 592 |
| saga partition | 0 | 0 | **1,344** | **816** | **1,080** | 528 |
| manual after core | 0 | 0 | 1,216 | 624 | 1,272 | 1,776 |

## Result 1: local atomicity is not global atomicity

In the 360-scenario slice where the core transaction is clearly committed and then drift/takeover occurs before the tail:

- `pretend_global_atomic` falsely claims global success in **360/360**;
- all three scoped policies have false-global claim 0;
- fenced-tail/manual leave 360 core-only residual states;
- saga partition reduces residuals to 270 by safely compensating the core in the subset where tail absence is known and compensation is final.

This is the key scope guard: **an atomic capability is only as large as its participant set**. A transaction over the core does not authorize a claim that an external tail is atomically included.

## Result 2: ambiguous core commit must be reconciled before touching the tail

There are 960 scenarios with ambiguous core response and no authoritative core-status read.

- `pretend_global_atomic` marks all 960 as success and is unsafe in **888/960**;
- `atomic_core_fenced_tail` and `saga_partition` are unsafe in 0, leaving 640 pending and 320 manual according to the objective contract;
- `manual_after_core` explicitly routes all 960 to manual.

A tail retry contract cannot repair uncertainty about whether the prerequisite core transaction happened. The coordinator first needs source-qualified core transaction status or a durable transaction decision identity.

## Result 3: Saga compensation is safe only after absence is proved

The `saga_partition` policy compensates the committed core only when the tail is **authoritatively known absent** (blocked before call, or status proves no application). It does not compensate while an ambiguous tail may already have applied.

This policy has unsafe 0 across the 2,400-scenario lattice and raises safe objective coverage to **1,344 / 2,400 = 56%**, versus 1,216 for the fenced-tail fixed policy. The benefit comes with more actions and compensation state.

The safe archive across scoped-tail, saga, and manual policies has:

- safe objective coverage: 1,344 / 2,400 = **56%**;
- safe autonomous terminal coverage: 816 / 2,400 = **34%**;
- safe terminal/explicit-manual coverage: 2,400 / 2,400 = **100%**.

Here the archive does not exceed Saga on objective coverage, but it preserves lower-action pending behavior and explicit-manual behavior as separate safe niches rather than forcing one recovery semantics.

## Candidate protocol

1. Attach an explicit `atomic_domain_id` and participant/effect set to every atomic capability.
2. Never let a local transaction success set a broader `global_atomic=true` flag unless every objective effect is inside that same proven domain.
3. After core commit, treat each external tail as a separately fenced effect with its own idempotency/status/finality contract.
4. If core commit is ambiguous, resolve that transaction identity before issuing dependent external effects.
5. If the tail is ambiguous and may have applied, do **not** compensate the core until tail status or a durable idempotent retry resolves the tail.
6. Use compensation only when the state being undone is known and compensation has its own finality proof.
7. Preserve `MANUAL_REQUIRED` as a distinct safe terminal disposition when cross-domain state cannot be resolved autonomously.

## Exact scope limits

- One atomic core plus one external tail; larger DAGs are not enumerated.
- Tail idempotent retry is modeled as durable and still within contract when enabled; real provider retention windows must be verified separately.
- Compensation is modeled only for the core; tail compensation ordering is left for a later leaf.
- No heuristic timeout rollback of prepared transactions is modeled here.
- The transaction-domain examples above are public mechanism precedents, not evidence that arbitrary external services support shared atomic commit.

## Exact Phase-1 continuation

Continue with **two-phase/prepared-state decision durability and coordinator takeover**.

Next finite grammar:

- two transactional participants prepared/not-prepared;
- durable global commit/abort decision written before vs after participant notification;
- coordinator crash before decision, after decision, or during notification;
- takeover with same/new coordinator epoch;
- participant status query available/unavailable;
- timeout heuristic rollback enabled/disabled;
- parent/objective supersession while participants remain prepared;
- compare `durable-decision 2PC`, `timeout heuristic`, `coordinator-memory-only`, `manual prepared-state reconciliation`, and a safe behavior archive;
- measure split commit/rollback, false abort, orphan prepared locks, stale decision application, takeover recovery I/O, manual burden, and safe objective coverage.

Keep the Phase-1 frontier nonempty; do not resume unrelated base research while the overlay remains active.
