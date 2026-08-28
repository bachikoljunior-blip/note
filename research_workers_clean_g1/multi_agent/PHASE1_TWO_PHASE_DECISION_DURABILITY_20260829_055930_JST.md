# Phase-1 two-phase decision durability and coordinator takeover

- role: `multi_agent`
- phase: `phase_1_chat_parity`
- root_problem_id: `o-chat-parity-root-v2-active-pool`
- assignment_task_id: `phase1-clean-multi-agent-concurrency-claims`
- bootstrap_valid: `true`
- frozen semantic main SHA: `9aecbfd72ebddea92de34792a4587f81e58a744c`
- frozen DESIRED_STATE: control revision `22`, blob `e4f6d24c137284d002941ac04254e3dbeca2cfcb`
- frozen role config: config revision `6`, blob `9a3edbe40ee5cbf3a94fe3206606aa58841c955c`
- post-freeze authority identity verified: `true`
- predecessor leaf: `PHASE1_ATOMIC_SCOPE_MIXED_SINK_20260829_055930_JST.md`
- semantic inputs: own role-local Phase-1 state, finite synthetic mechanism model, and public primary documentation only.

## Leaf objective

The mixed-sink leaf requires source-qualified transaction status before dependent effects. This leaf asks what the transaction coordinator itself must persist so takeover cannot split participants after a crash.

The model has two transactional participants and a coordinator. Participants may prepare, then the coordinator can crash:

- before a global decision;
- after a decision but before notification;
- after participant 1 is notified but before participant 2.

It also varies takeover, participant decision-query capability, heuristic timeout rollback, late old-coordinator notification, and parent/objective supersession.

Compared mechanisms:

1. `durable_decision_2pc` — persist one immutable global `COMMIT`/`ABORT` decision before any participant notification; recovery/takeover applies only that decision.
2. `timeout_heuristic` — same durable decision, but an uninformed participant may independently abort on timeout.
3. `coordinator_memory_only` — global decision is only in coordinator memory; takeover guesses abort when the coordinator disappears.
4. `manual_prepared_reconciliation` — no guessed automatic recovery after crash; surface prepared/partial state for explicit reconciliation.

## Public mechanism scope

PostgreSQL documents two-phase transactions as `PREPARE TRANSACTION` followed by exactly one of `COMMIT PREPARED` or `ROLLBACK PREPARED`, intended for an external transaction manager coordinating transactional resources. Prepared transactions are durable across sessions/crashes, appear in `pg_prepared_xacts`, hold locks/resources, and should normally be resolved promptly.

Sources:
- https://www.postgresql.org/docs/current/two-phase.html
- https://www.postgresql.org/docs/16/sql-prepare-transaction.html
- https://www.postgresql.org/docs/18/view-pg-prepared-xacts.html

These documents establish prepared-state and external-coordinator semantics. The coordinator decision-log protocol and finite counts below are a synthetic mechanism test, not a claim about PostgreSQL's internal implementation.

## Finite model

The script enumerates **704 equal-weight synthetic scenarios** after removing impossible phase combinations.

### Aggregate comparison

| policy | unsafe | split commit/abort | durable-decision violation | stale memory decision | orphan prepared | manual | objective-resolved |
|---|---:|---:|---:|---:|---:|---:|---:|
| durable-decision 2PC | **0** | 0 | 0 | 0 | 100 | 94 | **610** |
| timeout heuristic | **8** | 4 | **8** | 0 | 50 | 51 | 649 |
| coordinator memory only | **44** | **16** | 0 | **36** | 136 | 152 | 528 |
| manual prepared reconciliation | **0** | 0 | 0 | 0 | **432** | **512** | 192 |

The higher nominal coverage of `timeout_heuristic` is not admissible as a fixed safe policy because eight scenarios violate the already-durable global decision.

## Result 1: commit/abort decision must be durable before the first irreversible participant notification

In the targeted slice with both participants prepared, global commit intended, coordinator crash after participant 1 commit, takeover present, and no participant decision query:

- `coordinator_memory_only` splits participants in **4/4** scenarios;
- `durable_decision_2pc` splits 0/4 because takeover replays the durable commit decision;
- manual reconciliation does not invent an abort for participant 2.

The problem is not participant preparation; it is loss of the **global decision identity** between participant notifications.

## Result 2: timeout-based unilateral rollback can violate an already durable commit

In the slice with both participants prepared, durable commit intended, participant 1 already committed, no takeover/query, and heuristic timeout enabled:

- `timeout_heuristic` produces split commit/rollback in **2/2** and violates the durable decision in 2/2;
- `durable_decision_2pc` leaves one participant prepared/in-doubt instead of guessing;
- manual reconciliation leaves both unresolved as explicit manual state.

This makes the blocking trade-off explicit: a correct 2PC-style protocol can prefer temporary unavailability/locks over unilateral contradiction of a durable commit decision.

## Result 3: a memory-only decision is not an irrevocable authorization point

Across 48 scenarios where both participants prepared and the parent/objective supersedes after a coordinator memory decision:

- `coordinator_memory_only` applies a stale commit decision in **36** and is unsafe in 36;
- `durable_decision_2pc` has stale-decision application 0 because its durable decision is the explicit irrevocable point;
- manual reconciliation has stale application 0 by refusing to infer final authority after the crash.

The distinction is semantic, not merely persistence for performance: once participant effects can become irreversible, the protocol needs one durable, takeover-visible decision that defines whether later parent change can still revoke the transaction.

## Result 4: safe recovery trades liveness for prepared-state burden

`durable_decision_2pc` is unsafe in 0/704 and autonomously resolves 610/704, but leaves an aggregate 100 prepared-participant instances across unresolved scenarios. `manual_prepared_reconciliation` is also unsafe in 0/704 but leaves 432 prepared instances and 512 manual dispositions.

PostgreSQL's warning that prepared transactions retain locks/resources is therefore directly relevant to the liveness side of the protocol: fail-closed prepared state is safe from split decisions, but it is not free.

## Candidate protocol

1. Every transaction has a stable global transaction ID and participant set.
2. Participants can enter `PREPARED`, but no participant receives `COMMIT` until the coordinator durably persists exactly one global decision.
3. The global decision is immutable and readable by takeover/recovery; coordinator epoch controls who may notify, not what decision may be invented.
4. Before a durable decision exists, recovery may safely choose abort only if no participant could already have been told commit.
5. After durable `COMMIT`, no timeout path may unilaterally roll back a participant. If the decision cannot be read, remain prepared/manual.
6. Parent/objective supersession before the durable decision may force abort; supersession after durable commit is a new post-commit recovery/compensation problem, not authority to rewrite the transaction decision.
7. Surface and monitor prepared-state age/lock burden separately from correctness.

## Exact scope limits

- Two participants only.
- Participant notification is modeled as irreversible final commit/abort.
- Network partitions, Byzantine participants, transaction-manager consensus replication, and heuristic mixed outcomes from real XA stacks are outside this leaf.
- Query capability is an abstract authoritative read of the global decision.
- Counts are synthetic equal-weight mechanism counts, not incident probabilities.

## Exact Phase-1 continuation

Continue with **global-decision witness retention and late-participant recovery**.

Next finite grammar:

- durable decision retained permanently / TTL / ack-count GC / compact tombstone;
- both participant ACKs received vs one lost;
- participant crash/restart before or after decision-record GC;
- coordinator generation reuse and transaction-ID reuse;
- backup/archive replay of a prepared participant;
- late old-coordinator notification after GC;
- compare `TTL decision deletion`, `all-acks then delete`, `compact immutable decision witness`, `generation lower-bound watermark`, and `manual forever`;
- measure wrong late commit/abort, orphan prepared state, false exclusion from transaction-ID reuse, recovery reads, storage burden, and safe terminal coverage.

Keep a nonempty Phase-1 frontier; do not restore unrelated base research while the Phase-1 overlay remains active.
