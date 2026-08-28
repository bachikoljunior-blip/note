# Phase-1 global-decision witness retention and late-participant recovery

- role: `multi_agent`
- phase: `phase_1_chat_parity`
- root_problem_id: `o-chat-parity-root-v2-active-pool`
- assignment_task_id: `phase1-clean-multi-agent-concurrency-claims`
- bootstrap_valid: `true`
- frozen semantic main SHA: `9aecbfd72ebddea92de34792a4587f81e58a744c`
- frozen DESIRED_STATE: control revision `22`, blob `e4f6d24c137284d002941ac04254e3dbeca2cfcb`
- frozen role config: config revision `6`, blob `9a3edbe40ee5cbf3a94fe3206606aa58841c955c`
- post-freeze authority identity verified: `true`
- predecessor leaf: `PHASE1_TWO_PHASE_DECISION_DURABILITY_20260829_055930_JST.md`
- semantic inputs: own role-local Phase-1 state and a finite synthetic mechanism model; public PostgreSQL documentation supplies the prepared-state lifecycle boundary.

## Leaf objective

The preceding 2PC leaf requires a durable global decision so a takeover can finish prepared participants consistently. This leaf asks when that decision may be deleted or compacted without making a late participant impossible to recover safely.

The model varies:

- global decision `COMMIT` / `ABORT`;
- whether participant 1/2 had already finalized before GC;
- ACK loss;
- TTL expiry;
- replay of an older prepared participant from backup/archive;
- transaction-ID reuse for a new generation;
- late old-coordinator notification after GC.

Compared retention mechanisms:

1. `ttl_delete` — delete full decision after a time horizon.
2. `all_acks_delete` — delete after both participant ACKs are observed.
3. `compact_witness` — replace bulky state with small immutable `{txn_id, generation, decision}` witness.
4. `generation_watermark` — keep only a lower-bound generation fence; old generation is rejected but the historical decision is not retained.
5. `manual_forever` — retain the full decision indefinitely.
6. `name_tombstone` negative control — retain a tombstone by logical transaction name without generation identity.

## Public mechanism boundary

PostgreSQL keeps prepared transactions durable and inspectable in `pg_prepared_xacts` until they are committed or rolled back; the row is then removed. The docs also state that prepared transactions are intended to be resolved by an external transaction manager and warn against leaving them prepared for long because locks/resources remain held.

Sources:
- https://www.postgresql.org/docs/current/two-phase.html
- https://www.postgresql.org/docs/16/sql-prepare-transaction.html
- https://www.postgresql.org/docs/18/view-pg-prepared-xacts.html

The retention policies below are repository-level synthetic protocol candidates; PostgreSQL does not specify them.

## Finite model

The script enumerates **256 equal-weight scenarios**.

### Aggregate comparison

| retention policy | unsafe | wrong old decision | stale gen-1 apply to reused ID | orphan prepared | false reuse exclusion | terminal old txn | storage units |
|---|---:|---:|---:|---:|---:|---:|---:|
| TTL delete | **60** | 42 scenarios / 60 participant decisions | **32** | 0 | 0 | 196 | 12,800 |
| all-ACKs delete | **12** | 6 / 6 | **8** | 0 | 0 | 244 | 22,400 |
| compact witness | **0** | 0 | 0 | 0 | 0 | **256** | **2,560** |
| generation watermark | 0 | 0 | 0 | **320** | 0 | 32 | **1,280** |
| manual forever | 0 | 0 | 0 | 0 | 0 | 256 | 25,600 |
| name tombstone | 0 | 0 | 0 | 320 | **128** | 32 | 1,280 |

Storage units are relative synthetic weights only.

## Result 1: TTL is not a proof that no prepared participant can reappear

There are 28 scenarios where:

- the old decision is `COMMIT`;
- TTL has expired;
- at least one old prepared participant exists or is replayed;
- no late coordinator notification rescues it.

`ttl_delete` is unsafe in **28/28**: without the historical decision it guesses abort for an old prepared participant that must commit. The compact witness and full-retention policies are unsafe in 0/28. The generation watermark is also unsafe in 0 but leaves 40 prepared-participant instances unresolved/manual rather than guessing.

A time horizon can bound ordinary replay, but it is not itself evidence against backup restore, delayed participant recovery, or another resurrection path.

## Result 2: all observed ACKs are not enough when old state can be restored

In the 16-scenario slice where both participant ACKs were observed and an older prepared participant is later replayed from backup:

- `all_acks_delete` is unsafe in **8/16** and makes the wrong historical decision in 6 scenarios;
- `compact_witness` and `manual_forever` are unsafe in 0;
- `generation_watermark` refuses the resurrected old generation rather than inventing its decision.

Therefore ACK-complete GC is safe only if the protocol can also prove that finalized participant state cannot later be replaced by a pre-decision/pre-finality snapshot. The ACK proof and resurrection proof are distinct.

## Result 3: transaction-ID reuse needs generation identity, not a name-only tombstone

In 64 scenarios with a new transaction generation reusing the logical ID while an old coordinator notification can arrive:

- TTL deletion admits **32** stale generation-1 applications;
- all-ACK deletion admits 8;
- compact witness, generation watermark, and generation-aware full retention admit 0;
- the `name_tombstone` negative control blocks **64/64** legitimate reuses in this slice.

The identity therefore needs at least `{logical_txn_id, generation/incarnation}`. Keeping only the logical name is safe against stale messages only by permanently denying legitimate reuse.

## Result 4: the compact witness dominates full history for this tested recovery contract

Within this finite model, `compact_witness` and `manual_forever` are both unsafe 0 and terminally resolve all 256 old transactions. The compact witness uses one tenth of the synthetic storage weight.

The generation watermark is smaller still, but it cannot tell a resurrected prepared participant whether the old decision was commit or abort; it therefore leaves 320 prepared instances and 224 manual scenarios. This is a useful distinction:

- **generation fence** answers “may this old authority act?”;
- **decision witness** answers “what exact final decision must this old prepared participant converge to?”

They are not interchangeable.

## Candidate protocol

1. The durable global decision has a stable transaction generation/incarnation as well as a logical ID.
2. After bulky transaction metadata can be GC'd, retain a compact immutable decision witness containing at least `{txn_id, generation, participant-set digest, COMMIT|ABORT}`.
3. Late participant recovery reads the witness before any default action; absence of the witness is not permission to guess abort.
4. A lower-bound generation watermark may additionally reject stale notifications, but it cannot replace the decision witness while a prepared participant can still be resurrected.
5. ACK-based deletion requires a separately proven no-resurrection condition covering backups, archives, delayed replicas, and other replay sources.
6. Logical transaction-ID reuse increments generation and must not be blocked by a name-only tombstone.
7. Full history may be deleted once the compact witness is durable; the witness itself remains until the no-resurrection condition is stronger than every supported restore/replay path.

## Exact scope limits

- One historical transaction generation and one possible reused generation.
- Backup replay resurrects a single prepared participant abstraction.
- Witness corruption/replication loss is outside this leaf.
- Storage/recovery units are synthetic comparative weights.
- Counts are equal-weight mechanism counts, not empirical probabilities.

## Exact Phase-1 continuation

Continue with **decision-witness replication, loss, and quorum/failover semantics**.

Next finite grammar:

- decision witness replicated to 1 / 2 / 3 stores;
- write acknowledged by local node only / quorum / all;
- coordinator crash after acknowledgement but before full replication;
- reader chooses local / any / quorum;
- replica lag, loss, and stale pre-decision snapshot;
- takeover region/partition placement;
- concurrent transaction-generation reuse;
- compare single-copy witness, quorum write+read, write-quorum/read-one, dual independent copies, fail-closed manual, and behavior-indexed safe archive;
- measure lost decision, contradictory read, stale generation acceptance, availability, write/read cost, and safe recovery coverage.

Keep the Phase-1 frontier nonempty; do not restore unrelated base research while the overlay remains active.
