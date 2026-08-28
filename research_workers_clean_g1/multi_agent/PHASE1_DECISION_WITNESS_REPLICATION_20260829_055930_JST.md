# Phase-1 decision-witness replication, quorum reads, and failover

- role: `multi_agent`
- phase: `phase_1_chat_parity`
- root_problem_id: `o-chat-parity-root-v2-active-pool`
- assignment_task_id: `phase1-clean-multi-agent-concurrency-claims`
- bootstrap_valid: `true`
- frozen semantic main SHA: `9aecbfd72ebddea92de34792a4587f81e58a744c`
- frozen DESIRED_STATE: control revision `22`, blob `e4f6d24c137284d002941ac04254e3dbeca2cfcb`
- frozen role config: config revision `6`, blob `9a3edbe40ee5cbf3a94fe3206606aa58841c955c`
- post-freeze authority identity verified: `true`
- predecessor leaf: `PHASE1_DECISION_WITNESS_RETENTION_20260829_055930_JST.md`
- semantic inputs: own role-local Phase-1 state, public etcd documentation, and one finite synthetic replication model.

## Leaf objective

The preceding leaf found that a compact immutable decision witness can safely replace bulky historical transaction state, provided it remains recoverable. This leaf tests the witness itself under replication lag, one replica loss, stale prior-generation values, and transaction-generation reuse.

The model uses three logical witness stores unless a protocol explicitly uses one or two fixed stores. A current witness is `{generation=G, decision}`; replicas not reached by the current write may contain no value or a prior-generation witness. One replica can be unavailable. Readers can use one store or a two-store quorum and may or may not compare generation/incarnation metadata.

Compared policies:

1. `single_default_abort` — one copy; absence/loss is treated as abort (negative control).
2. `single_failclosed` — one copy; absence/loss becomes manual.
3. `dual_all2` — write both fixed copies before acknowledgement; recover from either surviving copy.
4. `w2r1_accept_any` — any two-of-three written, but recovery accepts one arbitrary replica without generation proof (negative control).
5. `w2r1_versioned` — two-of-three written; one-replica recovery acts only if that replica has the current generation, else fails closed.
6. `w2r2_unversioned` — write and read quorums intersect, but values lack generation authority (negative control).
7. `w2r2_versioned` — two-of-three write acknowledgement plus two-replica read and highest/current generation selection.
8. `manual_any` — acknowledge very early but never infer authority from absent/stale state; unresolved cases become manual.

## Public mechanism boundary

The current etcd API guarantees page states that completed writes are committed through consensus and permanently stored, and that ordinary KV reads are linearizable by default. It also explicitly distinguishes faster `serializable` reads, which can be stale with respect to quorum. The etcd glossary defines quorum as the majority needed for consensus and revisions as a cluster-wide monotonically increasing counter.

Sources:
- https://etcd.io/docs/v3.7/learning/api_guarantees/
- https://etcd.io/docs/v3.7/learning/glossary/

This is only a public mechanism precedent for consensus-backed durable writes, linearizable versus stale member-local reads, and monotonic revisions. The synthetic W/R protocols below are not claims about etcd's internal implementation.

## Finite model

The script enumerates **504 equal-weight synthetic scenarios** over:

- which subset of three replicas received the current decision before the crash;
- no replica loss or one of three replicas unavailable;
- one-replica recovery target;
- current decision `COMMIT`/`ABORT`;
- no prior generation or transaction-ID reuse with an older generation;
- older generation carrying the same or opposite decision.

### Aggregate comparison

| policy | unsafe | write acknowledged | recovered current decision | lost/unavailable witness | manual | write-unavailable |
|---|---:|---:|---:|---:|---:|---:|
| single copy + default abort | **36** | 288 | 252 | 72 | 0 | 216 |
| single copy + fail closed | 0 | 288 | 216 | 72 | 72 | 216 |
| dual fixed copies, require both | 0 | 144 | 144 | 0 | 0 | **360** |
| W2/R1 accept any | **45** | 288 | 171 | 72 | 72 | 216 |
| W2/R1 current-generation only | 0 | 288 | 162 | 126 | 126 | 216 |
| W2/R2 unversioned | **96** | 288 | 192 | 0 | 0 | 216 |
| W2/R2 generation-aware | **0** | 288 | **288** | **0** | 0 | 216 |
| early ACK + fail closed | 0 | 504 | 216 | 288 | 288 | 0 |

Costs in the result JSON are synthetic operation-count weights only.

## Result 1: write quorum plus read-one is not enough when the read can be stale

There are **18** scenarios where:

- the current decision reached a two-replica write quorum;
- transaction ID was reused for a newer generation;
- the recovery read lands on the third, still-old replica;
- that old generation carries the opposite decision.

`w2r1_accept_any` is unsafe in **18/18**. The generation-aware R1 policy is unsafe in 0 but must fail closed/manual in **18/18** because a single stale replica cannot prove the current decision.

A successful write quorum therefore does not make every later member-local read authoritative. The reader's consistency/currentness contract remains a separate proof obligation.

## Result 2: quorum intersection needs version/incarnation semantics, not just multiple responses

The model contains **96** scenarios where a two-replica read observes one current witness and one old-generation witness.

- `w2r2_unversioned` is unsafe in **96/96** because it cannot distinguish a stale value from current authority;
- `w2r2_versioned` is unsafe in **0/96** because it selects the current generation and rejects the older incarnation.

Quorum intersection tells us that a current write is represented in the read set under the tested one-failure assumptions. It does **not** by itself say which conflicting response is current. A monotonic generation/revision is needed to identify the authoritative member of the intersection.

## Result 3: under the tested one-replica-loss model, W2/R2 + generation recovers every acknowledged decision

In the **108** scenarios where exactly two replicas had the current decision and one of those two later fails, `w2r2_versioned` recovers the decision in **108/108**, unsafe 0, lost 0.

Across all 504 scenarios it safely recovers all **288** cases in which its two-of-three write condition was met. In this narrow model it therefore has the best combination of safe recovery and non-fixed write placement.

This result is conditional on the model's assumptions: at most one replica is unavailable, the current generation is monotonic and authenticated by the protocol, and a quorum read can reach two surviving stores. It is not a general claim that arbitrary W=2/R=2 storage is linearizable.

## Result 4: fixed dual copies and fail-closed single copies occupy different safe availability niches

`dual_all2` is safe and recovers all 144 writes it acknowledges, including one copy loss, but it rejects 360 scenarios because both fixed stores were not reached before acknowledgement. `single_failclosed` accepts twice as many writes (288) but leaves 72 lost-copy cases manual.

This is a useful QD distinction: stronger synchronous replication buys recovery coverage after failure at the cost of write availability. A safe archive should preserve both behaviors when the required durability/latency contract is not yet fixed.

## Candidate protocol

1. A compact decision witness is keyed by `{logical_txn_id, generation}` and includes the immutable global decision plus participant-set digest.
2. Do not expose participant commit/abort authority until the witness write has reached the durability/consensus acknowledgement required by the chosen fault model.
3. Recovery reads must have a consistency guarantee matching that write acknowledgement. A member-local/stale read is not upgraded to authority merely because a prior quorum write succeeded.
4. When multiple replicas disagree, compare a monotonic generation/revision and reject older incarnations; content equality is not sufficient authority.
5. If the required read quorum/current-generation proof is unavailable, leave the participant prepared/manual rather than guessing a decision.
6. Transaction-ID reuse increments generation and all stale notifications/witnesses from prior generations are fenced.
7. Record write/read availability and replication cost separately from safety; a protocol can be safe by failing closed while still having poor recovery coverage.

## Exact scope limits

- Three-replica quorum model with at most one unavailable replica; dual-copy policy uses two fixed stores.
- No Byzantine replicas, witness corruption, network reordering after a successful read, or membership reconfiguration.
- Current-generation comparison is assumed trustworthy.
- Read quorum is modeled as able to collect two surviving stores; latency/timeouts are not modeled.
- Counts and operation costs are synthetic equal-weight mechanism measures, not production rates.

## Exact Phase-1 continuation

Continue with **replica membership change and witness quorum reconfiguration**.

Next finite grammar:

- old membership `ABC`, new membership `BCD`;
- witness written before/during/after reconfiguration;
- joint-consensus/overlapping configuration available vs naive cutover;
- old/new quorum acknowledgements;
- one node failure/partition;
- stale old-generation witness on removed member A;
- takeover reader using old config, new config, or configuration epoch;
- transaction-generation reuse concurrent with membership epoch change;
- compare `naive config switch`, `old+new joint quorum`, `single consensus-store abstraction`, `fail-closed epoch mismatch`, and behavior-indexed archive;
- measure lost decision, split authority between memberships, stale member acceptance, availability/cost, and safe recovery coverage.

Keep the Phase-1 frontier nonempty; do not restore unrelated base research while the overlay remains active.
