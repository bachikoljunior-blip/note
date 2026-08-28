# Phase-1 cyclic retry/redrive horizons and recursive sink-witness GC

- role: `multi_agent`
- phase: `phase_1_chat_parity`
- root_problem_id: `o-chat-parity-root-v2-active-pool`
- assignment_task_id: `phase1-clean-multi-agent-concurrency-claims`
- bootstrap_valid: `true`
- frozen semantic tuple remains note main `9c76f42557b6dee420c8ff1f424f66b619465b5f`, root control revision `22`, root blob `e4f6d24c137284d002941ac04254e3dbeca2cfcb`, role config revision `6`, role blob `9a3edbe40ee5cbf3a94fe3206606aa58841c955c`.
- semantic inputs: own Phase-1 graph-quiescence checkpoint, official AWS documentation, and this finite synthetic model only. CLEAN boundary preserved.

## Leaf objective

The acyclic graph leaf derived a max-over-path-sums rule for bounded residual stale-authority propagation. This leaf tests the boundary where the authority graph contains a retry/redrive cycle or a transition that resets the relevant age/identity domain.

The question is whether witness GC can use:

- a one-pass acyclic projection;
- `max_attempts * per_attempt_bound`;
- a true source-wide absolute deadline;
- an explicit loop-termination proof;
- or a durable sink identity whose own retention survives every reachable replay.

## Public mechanism evidence

Amazon EventBridge retry policy exposes both `MaximumEventAgeInSeconds` and `MaximumRetryAttempts`: retries continue until either the configured attempt count or the maximum event age is reached. This is an example of a source contract with a shared event-age bound, rather than blindly giving every retry a fresh lifetime.

- https://docs.aws.amazon.com/eventbridge/latest/APIReference/API_RetryPolicy.html

Amazon SQS dead-letter behavior demonstrates why retry age semantics cannot be generalized across transitions. For **standard** queues, moving a message to a DLQ preserves the original enqueue timestamp for expiration; for **FIFO** queues, the enqueue timestamp resets when moved to the DLQ. SQS DLQ **redrive** then explicitly resets retention and assigns redriven messages a new `messageID` and `enqueueTime`.

- https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/setting-up-dead-letter-queue-retention.html
- https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-configure-dead-letter-queue-redrive.html

Therefore `message age`, `attempt age`, `DLQ age`, and `redriven message age` may belong to different authority/retention domains. GC must bind to the exact source transition semantics.

## Finite model

The executed model enumerates **82,944 equal-weight synthetic scenarios** over:

- retry clock semantics: one absolute deadline / per-attempt reset / unbounded;
- bound: 30 / 100;
- maximum attempts: 2 / 4 / unbounded;
- redrive: none / once while preserving age / once resetting age / repeated reset-age redrive;
- explicit loop-termination acknowledgement present/absent;
- root witness TTL: 14 / 30 / 90;
- sink durable identity TTL: 14 / 30 / 90;
- stale descendant age: 20 / 50 / 120 / 250;
- no sink identity vs all-authority identity;
- unique vs reused attempt identity;
- current vs stale coordinator epoch;
- canonical-result vs external-effect stale action.

Compared policies:

1. `acyclic_projection` — use one nominal bound and ignore retry/redrive loops.
2. `attempt_count_times_bound` — multiply a per-attempt bound by finite retry count, but ignore redrive age reset.
3. `absolute_deadline_certificate` — reclaim only when the source contract is explicitly one absolute age domain and redrive does not reset it, or when loop termination is explicitly acknowledged.
4. `loop_termination_certificate` — use the exact modeled reachable loop horizon; unbounded/reset cycles remain retained unless explicitly terminated.
5. `neg_sink_ttl_only` — delete the root witness whenever a sink identity exists, without proving that the sink identity outlives the loop.
6. `sink_identity_graph_gated` — use sink identity only if it is unique for the current incarnation/action and its own retention dominates the reachable loop horizon; otherwise use the loop certificate.
7. `permanent_witness` — retain the root witness indefinitely.

## Main results

| policy | reclamation coverage | unsafe scenarios | over-retained vs exact loop proof | synthetic storage |
|---|---:|---:|---:|---:|
| acyclic projection | 33.33% | **5,856 (7.06%)** | 13,824 | 1 |
| attempts × bound | 28.24% | **504 (0.61%)** | 0 | 2.5 |
| absolute-deadline certificate | 26.39% | **0** | 480 | 2.5 |
| explicit/exact loop certificate | **26.97%** | **0** | **0** | 3 |
| sink TTL only | 25.00% | **4,980 (6.00%)** | 16,776 | 2 |
| graph-gated sink identity | **27.18%** | **0** | **0** | 2.93 average |
| permanent witness | 0% | **0** | 22,368 | 5 |

These are finite mechanism counts, not production incident rates.

## Result 1: a bounded acyclic projection is unsafe once a retry transition can extend the age domain

In the **20,736-scenario** `redrive_resets_age` slice, the one-pass acyclic heuristic is unsafe in **3,552** cases. Even `attempt_count_times_bound` is unsafe in **504** because it accounts for retries inside the first loop but not a redrive that creates a fresh age domain.

The explicit `attempt_count_undercounts_redrive` slice contains 384 cases where finite attempts×bound says the TTL is sufficient while a reset-age redrive makes the reachable horizon longer. The attempts×bound policy reclaims 192 and is unsafe in **72**; the exact loop and graph-gated sink policies reclaim 0 and remain unsafe 0.

## Result 2: an unbounded reset-age redrive cycle has no finite time-only GC proof

The `unbounded_redrive_cycle` slice contains **10,368** scenarios. The exact loop certificate and graph-gated sink policy reclaim **0** unless a separate loop-termination proof exists. The acyclic heuristic reclaims 3,456 and is unsafe in 2,160; attempts×bound reclaims 672 and is unsafe in 408.

This is the cyclic analogue of the prior `unknown edge` result: no finite local TTL proves quiescence when the source can legally recreate a fresh retry/replay age domain indefinitely.

## Result 3: a true source-wide absolute deadline is a strong, narrow positive contract

In the **6,912-scenario** `absolute_deadline_supported` slice (absolute source deadline, no age-resetting redrive), `absolute_deadline_certificate`, the exact loop certificate, and graph-gated sink identity all have unsafe 0. The absolute-deadline policy is slightly more conservative overall because it deliberately refuses per-attempt and reset-age semantics it cannot prove.

EventBridge's `MaximumEventAgeInSeconds` plus maximum attempts is a public example of this kind of source-qualified retry envelope. It should not be copied onto systems whose retries create a new message/age domain.

## Result 4: SQS documents both preserve-age and reset-age transitions

The source audit matters directly here:

- SQS Standard queue -> DLQ expiration keeps the original enqueue timestamp;
- SQS FIFO queue -> DLQ resets the enqueue timestamp;
- SQS DLQ redrive creates a new message ID and enqueue time and resets retention.

So a controller that stores one Boolean like `retry_window=30d` or one timestamp like `first_enqueue_at` cannot safely infer every future replay horizon. The transition type/source version must be part of the proof graph.

## Result 5: a sink idempotency/consumption record has the same recursive GC problem

In the **20,736-scenario** exact-sink-identity slice, `neg_sink_ttl_only` reclaims every scenario but is unsafe in **4,980** because the stale descendant can arrive after the sink's own durable identity TTL. `sink_identity_graph_gated` reclaims only 5,768 supported cases and is unsafe 0.

This closes the recursion: moving the fence from the root/claim store to the effect sink improves architecture only if the sink witness itself is retained through the entire reachable replay horizon or can prove loop termination. A short idempotency record is not a permanent authority fence.

## Result 6: per-attempt identity must be non-reused

The model gives sink-side protection only when the attempt/incarnation identity is unique. In the 20,736 `reused_attempt_id_sink_collision` scenarios, the graph-gated policy refuses to treat the sink record as a durable discriminator and falls back to loop proof. This follows the previous ABA result: metadata that can collide across incarnations cannot be the final stale-writer fence.

## Current candidate protocol

1. Extend the source-quiescence DAG into a retry state machine/graph that can contain cycles and age-domain transitions.
2. For each retry edge, record whether its deadline is absolute from the original effect, per-attempt, reset on replay/redrive, or unknown.
3. A finite retry count only bounds lifetime if each attempt's delay bound and every replay/redrive transition are also bounded under the same identity domain.
4. If any reachable cycle can reset the age domain without a bounded cycle count/absolute deadline, finite time-only witness GC is invalid.
5. Explicit loop termination/drain can collapse the remaining horizon to zero, but must be source-qualified and current-epoch.
6. Sink-side durable identity may replace upstream witness retention only when `{current incarnation, effect/trigger identity}` is non-reused and the sink witness outlives the full reachable retry/replay graph.
7. DLQ/archive/redrive transition type belongs in the authority proof metadata; do not generalize one provider/queue mode's timestamp semantics to another.

## Scope limits

- Synthetic finite retry grammar only.
- The model intentionally simplifies retry timing to bounded envelopes; it does not fit probability distributions or actual backoff schedules.
- `repeat_reset_age` is a generic unbounded-cycle negative capability, not a claim about default SQS redrive configuration.
- SQS Standard/FIFO/DLQ details are cited only for their documented retention/identity transition semantics.
- The sink identity remains a modeled strong authority primitive when its uniqueness and lifetime gates hold.

## Persistence note

The repository result is a compact summary of the executed 82,944-scenario lattice and the repository contains an inspectable executable script. Byte-identical executed-source binding is not claimed; durable evidence binds the persisted Git blobs and stated mechanism counts.

## Exact Phase-1 continuation

Continue with **multi-effect retry cycles plus parent terminality and recovery-policy selection**.

Next finite grammar:

- two original effects with independent retry graphs, one bounded and one cyclic/unknown;
- one effect may already be irreversibly applied while another remains retry-reachable;
- compensation itself can enter a bounded/unbounded retry loop;
- root forward-complete, rollback-complete, manual/fail-closed, and mixed terminal dispositions;
- effect-vector certificate merge under different loop finality proofs;
- shared exclusive effect key across two retry loops;
- safe Pareto/QD archive over latency/witness-retention/irreversible issuance/compensation depth;
- compare root Boolean, per-effect loop certificates, global worst-case TTL, and behavior-diverse safe archive;
- measure false terminality, duplicate effect/compensation, blocked-but-safe scenarios, witness storage, and safe recovery coverage.

Public-source audit target: no new provider assumptions unless necessary; prioritize integrating the already source-qualified retry/finality mechanisms into the parent certificate. Keep a nonempty Phase-1 frontier afterward.
