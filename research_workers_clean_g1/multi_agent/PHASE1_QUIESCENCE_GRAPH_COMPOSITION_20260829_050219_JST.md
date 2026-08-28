# Phase-1 quiescence composition across sequential/fan-out retry graphs

- role: `multi_agent`
- phase: `phase_1_chat_parity`
- root_problem_id: `o-chat-parity-root-v2-active-pool`
- assignment_task_id: `phase1-clean-multi-agent-concurrency-claims`
- bootstrap_valid: `true`
- frozen semantic tuple remains note main `9c76f42557b6dee420c8ff1f424f66b619465b5f`, root control revision `22`, root blob `e4f6d24c137284d002941ac04254e3dbeca2cfcb`, role config revision `6`, role blob `9a3edbe40ee5cbf3a94fe3206606aa58841c955c`.
- semantic inputs: own immediately preceding Phase-1 witness-quiescence artifact, official AWS/Kubernetes documentation, and this finite synthetic model only. CLEAN boundary preserved.

## Leaf objective

The preceding leaf reduced safe witness GC to source-qualified quiescence over every channel that can resurrect an old authority-bearing action. This leaf asks how those source horizons compose when work can move through a chain or fan out into multiple retry/queue branches.

The key distinction is:

- sequential residual horizons compose by **addition along a path**;
- parallel fan-out composes by the **maximum root-to-sink path**, not by adding every branch;
- a source-qualified drain acknowledgement can set that edge's residual horizon to zero;
- any unknown undrained edge makes that path unbounded unless an independent durable authority identity at the exact sink rejects stale descendants.

## Public mechanism evidence

Amazon SQS `PurgeQueue` is itself not instantaneous: AWS says the purge can take up to 60 seconds; messages sent before the purge can still be received during that period, and messages sent after the call can also be deleted while the purge is in progress. This is a concrete example of why a root-level "purge requested" or "queue looks empty" fact is not automatically an instantaneous downstream quiescence certificate.

- https://docs.aws.amazon.com/boto3/latest/reference/services/sqs/client/purge_queue.html

Amazon SQS Standard queues also remain at-least-once, so duplicate copies may be delivered and messages may arrive out of order. EventBridge retry policy exposes a separate bounded retry capability (`MaximumEventAgeInSeconds` plus retry attempts); those bounds are source-specific contract inputs rather than global defaults.

- https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/standard-queues-at-least-once-delivery.html
- https://docs.aws.amazon.com/eventbridge/latest/APIReference/API_RetryPolicy.html

Kubernetes finalizers remain a useful deletion analogy: an object stays in terminating state until each required cleanup condition is explicitly cleared, rather than assuming a root delete request implies all dependent work is gone.

- https://kubernetes.io/docs/concepts/overview/working-with-objects/finalizers/

## Finite model

The executed model enumerates **259,200 equal-weight synthetic scenarios** over two topologies:

- `chain3`: `e1 -> e2 -> e3`;
- `fanout2`: common `e1`, then parallel paths `e1 -> e2` and `e1 -> e3`.

Each edge has bounded or unknown residual stale-writer/replay horizon (`e1`: 5/20/unknown, `e2`: 5/14/unknown, `e3`: 5/30/unknown). Every subset of edges can have a strong drain acknowledgement. Candidate witness TTLs are 5/14/20/40/70 and delayed stale descendants are sampled at ages 7/15/25/45/80. The model also varies current vs stale GC epoch, canonical-result vs external-effect action, key reuse, and sink durable identity scope.

Compared policies:

1. `max_edge_heuristic` — use only the largest individual edge bound.
2. `sum_all_edges_heuristic` — add every unique active edge, even parallel branches.
3. `root_quiet_only` — if the root edge is drained, assume all descendants are quiet.
4. `graph_path_certificate` — sum sequential residual bounds per root-to-sink path, then take the maximum path; unknown undrained edge blocks reclamation; stale GC epoch fails closed.
5. `sink_chain_identity` — use the same graph proof unless the exact action class is independently fenced by a durable sink identity.
6. `permanent_root_witness` — retain the compact root/incarnation witness forever.

## Main results

| policy | reclamation coverage | unsafe scenarios | stale result/effect accepts | over-retained vs graph certificate | synthetic storage |
|---|---:|---:|---:|---:|---:|
| max edge only | **45.74%** | **1,512** | 1,512 | 0 | 2 |
| sum all edges | 21.06% | **0** | 0 | **720** | 3 |
| root quiet only | **50.00%** | **28,872** | 28,872 | 17,700 | 1 |
| graph path certificate | **21.34%** | **0** | 0 | **0** | 3 |
| sink-chain durable identity | **35.67%** | **0** | 0 | 0 | 2.25 average |
| permanent root witness | 0% | **0** | 0 | 55,320 | 5 |

These are mechanism counts, not operational rates.

## Result 1: `max(edge horizon)` is unsafe for sequential propagation

There are **7,920** scenarios where every individual edge bound is at or below the proposed TTL, but the residual root-to-sink path sum is larger. `max_edge_heuristic` reclaims in all 7,920 and becomes unsafe in **1,512** delayed-descendant cases. The graph certificate reclaims 0 in this false-quiescence slice and is unsafe 0.

For a simple chain, if an old action may spend up to 20 units before entering a queue and then another 14 plus 30 units in later stages, the end-to-end stale-descendant horizon is not 30 merely because 30 is the largest individual bound. Sequential authority propagation can consume the bounds one after another.

## Result 2: adding every edge is safe but can be unnecessarily conservative under fan-out

`sum_all_edges_heuristic` is safe throughout this deterministic lattice, but it under-reclaims a **720-scenario fan-out slice** where the graph path certificate proves safe reclamation. In those cases, parallel branches do not execute sequentially along one stale descendant path, so adding both branch horizons overstates the required wait.

The exact bounded-graph rule in this model is:

`required_quiescence_horizon = max_over_root_to_sink_paths(sum_of_residual_edge_horizons_on_path)`

with a drained edge contributing zero and an unknown undrained edge making its path unbounded.

## Result 3: root quiescence does not imply descendant quiescence

The `root_drained_descendants_remain` slice contains **97,200** scenarios. `root_quiet_only` reclaims every one and is unsafe in **28,872** because work already emitted before the root drain can still live in downstream queues/retry stages. The graph path certificate reclaims 21,420 supported cases and remains unsafe 0.

SQS purge's documented non-instantaneous behavior is a useful public reminder that even a direct cleanup operation can have an explicit completion interval; a root request or upstream stop signal cannot be promoted to a proof that every already-created downstream copy disappeared instantaneously.

## Result 4: unknown undrained edges require an explicit proof or a downstream fence

There are **109,200** scenarios with at least one unknown undrained edge on a live path. `graph_path_certificate` and `sum_all_edges_heuristic` reclaim 0. `root_quiet_only` still reclaims 39,600 and is unsafe in 23,760.

`sink_chain_identity` safely reclaims **27,300** of those unknown-horizon scenarios where the exact modeled action class is protected by a durable current-incarnation/single-use sink identity. Again, this does not eliminate the witness: it transfers the non-reuse proof to the sink.

## Result 5: graph proof dominates both heuristic extremes in the tested bounded domain

Against the graph certificate's safe-reclamation set:

- max-edge has no over-retention but admits 1,512 unsafe stale descendants;
- sum-all is safe but over-retains 720 cases;
- graph path has unsafe 0 and over-retention 0 by construction in this deterministic bounded-horizon model;
- sink identity safely expands reclamation to 35.67% when its stronger authority capability is available.

This gives a sharper generic rule than "wait the longest TTL" or "sum every timeout": **quiescence is a property of the authority propagation graph.**

## Current candidate protocol

1. Represent stale-authority sources as a DAG whose nodes/edges identify workers, durable queues, retry schedulers, provider callbacks, compensators, and authority sinks.
2. Every edge records one of: strong drained/quiescent acknowledgement, source-qualified maximum stale-propagation horizon, or `unknown`.
3. A root/incarnation witness can be time-reclaimed only if every live root-to-authority-sink path is bounded and the requested wait dominates the maximum residual path sum.
4. Do not add independent parallel branches as if they were sequential; take the maximum path after summing within each path.
5. A root/worker termination acknowledgement removes only future emissions from that edge. Already-created downstream descendants remain represented until their own edges are drained or expire by contract.
6. Unknown paths fail closed unless the final authority sink independently rejects the stale incarnation/action identity.
7. Reclamation remains a current-epoch, crash-recoverable transition; graph proof does not authorize a stale GC writer.

## Scope limits

- Deterministic bounded-propagation lattice only. Real queue/retry systems can have probabilistic latency, retry reset/extension, clock semantics, and fan-out created dynamically.
- The path-sum rule assumes each edge bound limits the residual time after a descendant enters that edge. If a retry resets upstream/downstream clocks or can recreate earlier stages, the graph needs cycles or a different bound proof.
- Drain acknowledgement is modeled as exact. Empty queue reads and best-effort purge/cancel are weaker unless source documentation proves equivalence.
- Sink durable identity still has its own retention/GC problem.

## Persistence note

The repository result is a compact source-qualified summary of the locally executed 259,200-scenario model and the repository contains an inspectable executable script. Byte-identical executed-source binding is not claimed; persisted blob identities should be used as the durable audit reference.

## Exact Phase-1 continuation

Continue with **cyclic retries / horizon reset and recursive sink-witness GC**.

Next finite grammar:

- graph cycles such as `queue -> retry scheduler -> queue` and compensation retry loops;
- bounded maximum retry count vs unbounded retry count;
- per-attempt maximum age that resets each retry vs absolute end-to-end deadline;
- exponential/backoff delay caps;
- dead-letter transition and replay from DLQ/archive;
- sink durable identity retention shorter/equal/longer than the loop's reachable replay horizon;
- retry-ID reuse vs per-attempt unique identity;
- current vs stale retry coordinator epoch;
- compare naive path-sum on an acyclic projection, `attempt_count * per_attempt_bound`, absolute deadline certificate, explicit loop-termination proof, permanent sink identity, and safe behavior/QD archive;
- measure stale resurrection after GC, duplicate authoritative effect, false terminality, reclamation/storage cost, and proof assumptions separately.

Public-source audit target: official bounded retry/dead-letter/archive semantics and whether retry age resets or is absolute. Keep a nonempty Phase-1 frontier afterward.
