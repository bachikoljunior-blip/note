# Phase-1 source-qualified quiescence before witness garbage collection

- role: `multi_agent`
- phase: `phase_1_chat_parity`
- root_problem_id: `o-chat-parity-root-v2-active-pool`
- assignment_task_id: `phase1-clean-multi-agent-concurrency-claims`
- bootstrap_valid: `true`
- frozen semantic tuple: note main `9c76f42557b6dee420c8ff1f424f66b619465b5f`, root control revision `22`, root blob `e4f6d24c137284d002941ac04254e3dbeca2cfcb`, role config revision `6`, role blob `9a3edbe40ee5cbf3a94fe3206606aa58841c955c`.
- post-freeze root/config identities remained unchanged under SHA/path/blob-only verification; no newer-head semantic content was adopted.
- semantic inputs: own immediately preceding Phase-1 claim-ABA checkpoint, public Kubernetes/Amazon SQS documentation, and this finite synthetic model only. No O/O-derived, other-worker, downstream, legacy, shared-ledger, or other-role semantics were used.

## Leaf objective

The prior ABA leaf showed that deleting the last incarnation/fence witness can make an old worker/result/effect indistinguishable from a later reuse of the same logical key. This leaf asks the narrower reclamation question:

**What proof is sufficient before the durable incarnation/fence witness itself can be deleted?**

The candidate answer is not a universal TTL. Reclamation requires either:

1. source-qualified quiescence over every channel that can still resurrect an old authority-bearing action, or
2. an independent durable single-use/current-incarnation identity at the actual authority sink, so local claim-witness deletion cannot re-authorize stale work.

## Public mechanism evidence

Kubernetes finalizers keep an object in a terminating state until the responsible controllers have completed the conditions represented by the finalizer and removed it. The object is not physically reclaimed merely because deletion was requested. This is a public example of **condition-gated garbage collection** rather than time-only deletion.

- https://kubernetes.io/docs/concepts/overview/working-with-objects/finalizers/

Amazon SQS Standard queues explicitly use at-least-once delivery: more than one copy can be delivered and messages can arrive out of order. AWS also notes that a stored copy can survive a receive/delete on another server and later be delivered again. Visibility timeout is not an absolute no-redelivery guarantee. Queue message retention is configurable up to 14 days.

- https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/standard-queues.html
- https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/standard-queues-at-least-once-delivery.html
- https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-visibility-timeout.html
- https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-configure-queue-parameters.html

The model uses a `q14` bounded-replay example only as an explicit source contract. It does **not** claim that every queue has a 14-day horizon, or that SQS retention alone is a business-state finality proof.

## Finite model

The executed model enumerates **233,280 equal-weight synthetic scenarios** across:

- worker stale-action lifetime: bounded 5 / 30 units or unknown;
- queue replay horizon: none / bounded 14 / unknown;
- stale action source: worker / queue / either;
- stale action type: result / external effect / claim release;
- delayed action age: 2 / 7 / 20 / 40 / 100;
- worker cancellation evidence: none / best-effort cancel / explicit termination acknowledgement;
- queue evidence: none / source-qualified drain acknowledgement;
- local witness TTL: 5 / 14 / 30 / 90;
- logical key retired vs reused;
- authority sink durable identity scope: none / effect-only / all authoritative actions;
- current vs stale GC epoch;
- clean GC vs crash after witness deletion before durable GC commit marker.

Compared policies:

1. `time_only_ttl` — delete witness at local TTL and assume old authority cannot reappear.
2. `cancel_ack_plus_ttl` — use explicit worker termination or known worker horizon, but deliberately ignore independent queue replay.
3. `source_qualified_quiescence` — reclaim only when every relevant worker/replay source is explicitly acknowledged quiet or its documented bound has elapsed; stale GC epochs fail closed and interrupted GC is recovered before deletion is final.
4. `permanent_compact_witness` — never delete the minimal incarnation/trigger witness.
5. `sink_durable_single_use` — permit more local reclamation when the exact authority sink durably rejects stale incarnation/action identity; otherwise fall back to the same quiescence proof.

## Main results

| policy | reclamation coverage | unsafe scenarios | stale-after-GC accepts | duplicate authoritative effects | synthetic storage units |
|---|---:|---:|---:|---:|---:|
| time-only TTL | 100% | **28,800 / 233,280 = 12.35%** | 34,560 | 11,520 | 1 |
| cancel-ack + worker TTL | 66.67% | **7,320 = 3.14%** | 8,784 | 2,928 | 2 |
| source-qualified quiescence | **16.59%** | **0** | 0 | 0 | 3 |
| permanent compact witness | 0% | **0** | 0 | 0 | 5 |
| sink durable single-use/current-incarnation | **31.44%** | **0** | 0 | 0 | 2.56 average |

These percentages are equal-weight mechanism coverage, not observed production incident rates. The lower reclamation coverage of proof-gated policies is deliberate: unknown writer/replay horizons remain retained rather than guessed away.

## Result 1: a local TTL is not a quiescence proof

The time-only policy deletes every witness and produces **28,800 unsafe scenarios**, including 11,520 stale-result false terminal/overwrite cases, 11,520 duplicate authoritative effects, and 5,760 stale releases that delete a reused new claim.

This is the same ABA mechanism as the prior leaf, now expressed as a GC rule: elapsed local time tells you nothing about a delayed writer or queue unless that time is actually a source-qualified upper bound for every authority-bearing path.

## Result 2: worker termination does not drain a durable queue

In the **25,920-scenario** `unknown_queue_replay_no_drain` slice:

- time-only TTL reclaims all and is unsafe in **10,800**;
- worker-oriented `cancel_ack_plus_ttl` still reclaims 17,280 and is unsafe in **6,720**;
- source-qualified quiescence reclaims **0** and is unsafe 0;
- sink durable identity reclaims 5,760 supported authority-sink cases and is unsafe 0.

An explicit process termination acknowledgement can prove that worker process A is no longer a writer. It cannot prove that a message, durable retry record, delayed webhook, or another queue copy carrying A's work cannot later reappear.

SQS's documented at-least-once/redelivery behavior is a public example of why those are separate sources.

## Result 3: a bounded queue horizon must dominate the local witness TTL

The explicit `q14` slice isolates a source contract where replay can occur through age 14 while the local witness TTL is shorter. It has 1,296 scenarios:

- time-only TTL accepts a stale action in **1,296 / 1,296**, with 1,080 scored unsafe;
- worker-only cancel/TTL accepts 720 stale actions and is unsafe in 600;
- source-qualified quiescence accepts 0;
- sink durable identity accepts 0.

The point is not the value 14. The proof rule is `witness lifetime >= every relevant replay/writer bound` unless an explicit drain/termination proof or independent sink identity supersedes that bound.

## Result 4: unknown horizons require proof or durable sink identity, not a larger guessed TTL

For unknown worker lifetime without explicit termination acknowledgement (34,560 scenarios):

- time-only TTL is unsafe in 14,400;
- worker-aware cancel/TTL correctly reclaims 0;
- source-qualified quiescence reclaims 0;
- sink durable identity safely reclaims 7,680 cases where the modeled sink independently preserves the exact authority identity.

For unknown queue replay without drain acknowledgement, source-qualified quiescence likewise reclaims 0.

Thus "make the TTL very large" is not a proof when the source contract is unbounded/unknown. Either obtain a stronger quiescence certificate or move a durable identity witness to the sink that must reject the stale action.

## Result 5: GC is itself a fenced, crash-recoverable authority transition

Half the lattice gives the compactor a stale epoch. Source-qualified quiescence and sink-durable policies reclaim **0** in all 116,640 stale-GC-epoch scenarios. Time-only and worker-only policies continue deleting witnesses and remain unsafe.

In 116,640 modeled crash-between-delete-and-commit-marker scenarios, source-qualified quiescence leaves the witness logically retained/recoverable rather than treating deletion as complete. Sink-durable identity can finish a subset safely when authority proof already lives at the sink; otherwise it also fails closed.

This is the same separation seen throughout Phase-1: proving that stale writers are quiescent does not authorize a stale compactor to delete the proof object.

## Result 6: durable single-use identity can trade storage location for reclamation coverage

A permanent compact witness is safe but reclaims nothing. Source-qualified quiescence safely reclaims **38,700 / 233,280 = 16.59%**. The sink-durable policy safely reclaims **73,340 = 31.44%**, because actions covered by an independent durable current-incarnation/single-use identity remain rejectable after the local claim witness is gone.

This does not eliminate durable identity storage; it **moves the proof to the authority sink**. The sink scope has to cover the action actually being fenced. An effect-only idempotency record cannot authorize deleting the result/claim-release witness unless those authority sinks have equivalent protection.

## Current candidate reclamation protocol

1. Keep a compact per-incarnation witness after raw claim/event payload GC. It contains immutable incarnation/reservation identity, last accepted epoch, terminal/trigger consumption identity, and source-contract version.
2. Enumerate every channel that can still emit an authority-bearing action for that incarnation: live worker, delayed RPC, durable queue, provider retry/webhook, manual replay, recovery job, and any external sink retry path.
3. For each channel, require one of:
   - explicit source-qualified quiescence/drain/termination acknowledgement;
   - a documented maximum writer/replay horizon that has elapsed;
   - an independent durable single-use/current-incarnation identity at the exact authority sink.
4. `best_effort_cancel`, empty-queue observation, local lease expiry, and process disappearance are not promoted to quiescence proof unless the underlying source contract says so.
5. Unknown/unbounded source horizon without a stronger proof means retain the witness or move the durable fence to the sink.
6. Reclamation itself requires the current GC/compactor epoch plus an atomic/recoverable commit marker. A stale compactor or crash cannot silently erase the final fence witness.
7. Logical key reuse is allowed only after this proof, and the new task still receives a fresh immutable incarnation/acquisition identity.

## Scope limits

- Finite synthetic mechanism lattice only.
- `explicit_termination_ack` and `source_qualified_drain_ack` are strong synthetic capabilities; real systems need exact source documentation for what they prove.
- `q14` is a bounded-replay stress dimension informed by SQS's configurable maximum message-retention setting, not a generic queue constant.
- Sink durable identity is modeled as collision-free and durable for the covered authority class. Sink retention/GC of that identity remains a recursive proof problem.
- This leaf does not yet model multiple nested queues/retry systems whose individual horizons compose through fan-out.

## Persistence note

The result is source-qualified and the repository contains an inspectable executable model. Because the executed local source and persisted compact script were not proven byte-identical, the receipt must bind persisted Git blobs and must not claim a byte-identical execution source.

## Exact Phase-1 continuation

Continue with **composed quiescence across fan-out/retry graphs and recursive sink-witness GC**.

Next finite grammar:

- worker -> queue A -> dispatcher -> queue B -> external sink chains;
- independent bounded/unknown horizons at every edge;
- retry fan-out that creates multiple descendants of one old incarnation;
- per-edge drain acknowledgements vs a root-level "all quiet" assertion;
- queue deletion/purge vs in-flight/redelivery copies;
- sink durable effect identity with its own retention/GC horizon;
- parent/key reuse after only a subset of branches is quiescent;
- concurrent compactor/integrator takeover;
- compare max-horizon heuristic, sum-horizon heuristic, per-edge quiescence certificate DAG, permanent root witness, and sink-chain durable identity propagation;
- measure stale descendant resurrection, duplicate authoritative effect, false safe-reclamation claim, witness/storage cost, recovery I/O, and safe reclamation coverage.

Public-source audit target: official guarantees for queue purge/delete/in-flight messages and retry chains, plus any standard mechanism for dependency-aware finalization. The objective is to derive whether quiescence composes by `max`, `sum`, or explicit graph proof; keep a nonempty Phase-1 frontier afterward.
