# Phase-1 retirement-barrier bypass and rollback across publication paths

- role: `multi_agent`
- phase: `phase_1_chat_parity`
- root_problem_id: `o-chat-parity-root-v2-active-pool`
- assignment_task_id: `phase1-clean-multi-agent-concurrency-claims`
- bootstrap_valid: `true`
- frozen semantic main SHA: `f6b3c1273f7abb3685198ce5dbbc2368151eca6c`
- frozen DESIRED_STATE: control revision `22`, blob `e4f6d24c137284d002941ac04254e3dbeca2cfcb`
- frozen role config: config revision `6`, blob `9a3edbe40ee5cbf3a94fe3206606aa58841c955c`
- predecessor checkpoint: `research_workers_clean_g1/multi_agent/PHASE1_REPAIR_QUIESCENCE_COMPACTION_20260829_062646_JST.md`
- semantic inputs: own current invocation state, public Apache Kafka/etcd mechanism documentation, and one finite synthetic multi-path retirement-barrier model.
- mechanism script SHA-256: `b56cbc88934807ce6459e2206be3e88f04b1ff58a4495c41f1461eee0e77c160`
- mechanism script Git blob: `490aeb6bca0ccc9642af1c44bbb94e77e765c707`
- mechanism result Git blob: `795cd9b4578664c552dca48fd13977b992a79a68`

## Leaf objective

The preceding quiescence leaf assumed that a monotonic `minimum_repair_generation` is non-bypassable once installed. This leaf breaks that assumption by splitting publication into `queue / direct API / retry worker / restore/archive` paths and allowing path guards or sink-local barrier state to be stale or rolled back.

## Public mechanism boundary

Apache Kafka provides a concrete fencing precedent: producers sharing a `transactional.id` receive producer IDs/epochs, and a newer producer fences the old producer so the old instance can no longer issue transactional requests. Kafka 4.x documentation also describes producer epochs as part of the transactional protocol. The important scope boundary is that this protection is enforced by the Kafka transaction authority; a publication route that does not pass through that authority is outside the fence.

etcd transactions provide an atomic compare/then/else primitive over one authority store, including comparisons on key values/revisions. That is useful for making a local minimum-generation update conditional and monotonic, but it does not itself prove that every independent external publication path consults that etcd state.

Sources:
- https://kafka.apache.org/43/javadoc/org/apache/kafka/clients/producer/KafkaProducer.html
- https://kafka.apache.org/43/operations/transaction-protocol/
- https://etcd.io/docs/v3.7/learning/api/

The signed/versioned all-path retirement certificate and anti-rollback anchor below are synthetic application-protocol mechanisms, not claims about provider-native primitives.

## Finite model

The executable model enumerates **4,608 equal-weight synthetic scenarios** over:

- historical repair final / still pending;
- publication path `queue / direct_api / retry_worker / restore_archive`;
- path retirement guard intact / bypassed;
- sink-local minimum-generation state `current / stale_replica / rolled_back`;
- retirement certificate `current / stale / none`;
- monotonic anti-rollback anchor available / unavailable;
- delayed old repair arrival absent / present;
- current generation advanced / not advanced;
- repair kind cancel / compensate;
- dedupe contract valid / expired.

Compared policies:

1. `permanent_tombstone` — retain historical incarnation state indefinitely.
2. `coordinator_only_barrier` — queue/retry paths may be fenced, direct/restore paths are not necessarily covered.
3. `sink_local_barrier` — rely only on the sink's current minimum generation.
4. `all_path_certificate_only` — every intact path requires a current retirement certificate and fails closed on stale/missing certificate, but a rolled-back/bypassed path can ignore it.
5. `certificate_plus_sink_min` — certificate guard plus sink-local minimum generation.
6. `premature_all_path_retire` — negative control that installs the full retirement mechanism even while historical repair is still pending.
7. `safe_archive` — retirement is finality-gated; intact current certificate, current sink minimum, or a monotonic anti-rollback anchor may reject old work; when none can be verified it fails closed rather than accepting old repair.

`validation_cost_total` is only a relative synthetic proof-check count; it is not latency.

## Aggregate result

| policy | safe compaction | unsafe | old-generation bypass | ABA resurrection | duplicate compensation | current work blocked |
|---|---:|---:|---:|---:|---:|---:|
| permanent tombstone | 0 | 0 | 0 | 0 | 0 | 0 |
| coordinator-only barrier | 1,440 | **864** | **864** | 432 | 216 | 0 |
| sink-local barrier | 1,536 | **768** | **768** | 384 | 192 | 0 |
| all-path certificate only | 1,728 | **576** | **576** | 288 | 144 | 768 |
| certificate + sink minimum | 1,920 | **384** | **384** | 192 | 96 | 768 |
| premature all-path retire | 2,304 | **1,152** | 0 | 0 | 0 | 2,304 |
| safe archive | **2,304** | **0** | 0 | 0 | 0 | **1,152** |

Counts are equal-weight synthetic mechanisms, not production incident rates.

## Result 1: a coordinator fence is not an all-path fence

In the targeted `direct_api / restore_archive + final historical repair + old repair arrival` slice there are **576** scenarios. `coordinator_only_barrier` allows old repair in **576 / 576**, producing 288 ABA resurrections and 144 duplicate compensations in the model.

The generic lesson is not that queues are unsafe; it is that an authority proof has the scope of the enforcement point. A direct or restored publication route that never validates the coordinator's retirement generation is outside the coordinator fence.

## Result 2: certificate and sink minimum are independent defense layers

In the 384-scenario slice where the all-path guard is bypassed and the sink minimum is stale or rolled back while final old repair arrives, `all_path_certificate_only`, `sink_local_barrier`, and `certificate_plus_sink_min` are each unsafe in **384 / 384**. The certificate cannot help when its enforcement path itself has been rolled back; the sink minimum cannot help when its state is stale/rolled back.

When the same degraded two-layer slice has an independent monotonic anti-rollback anchor available, there are **192** scenarios. `safe_archive` safely compacts **192 / 192** without blocking current work; the other non-permanent baselines remain unsafe in 192 / 192.

## Result 3: absence of a current proof should trade availability, not safety

For the degraded path+sink cases with **no** anti-rollback anchor, `safe_archive` rejects old work but blocks current work until authority can be reconstructed. In the targeted 384-scenario no-anchor slice it has unsafe 0, safe compaction 384, and current-work-blocked 384.

Likewise, when a path guard is intact but its retirement certificate is stale or missing, the certificate-based policies fail closed. In the 768-scenario slice, `safe_archive` and `all_path_certificate_only` are safe but block current work in **768 / 768**.

This exposes a genuine safety/liveness trade: a system cannot safely infer the missing monotonic generation simply because progress would be convenient.

## Result 4: all-path fencing still must be finality-gated

The `pending historical repair + old repair arrives` slice has **1,152** scenarios. `premature_all_path_retire` blocks legitimate repair in **1,152 / 1,152**. `safe_archive` retains the historical witness and blocks none.

Thus stronger path coverage does not remove the earlier finality obligation. A perfect fence installed at the wrong semantic time is still wrong.

## Candidate protocol

1. Separate historical-repair finality from publication-path fencing; retirement cannot start while repair is pending.
2. Bind each retired generation to a signed/versioned retirement certificate containing at least logical authority key, retired generation/incarnation bound, certificate version, and authority-domain identity.
3. Require every normal publication path to present/validate a current certificate or equivalent current minimum-generation proof.
4. Independently enforce `minimum_repair_generation` at the final effect sink so a bypassed coordinator/path is not enough to resurrect old work.
5. Store the minimum generation in an authority that cannot silently roll backward with an application backup/restore. If rollback is possible, keep a monotonic anti-rollback anchor outside that rollback domain.
6. On restore or replica failover, compare recovered barrier version to the anti-rollback anchor before admitting any effect publication.
7. If certificate, sink minimum, and anchor cannot establish current authority, fail closed for both old and new effect publication until the current bound is reconstructed.
8. Do not use a signed certificate as a timeless token: its version/currentness must itself be fenced so an old validly signed certificate cannot re-authorize a retired generation after rollback.
9. Keep permanent/compact tombstones as the fallback when no non-bypassable anti-rollback authority exists.

## Exact tested scope

- One old repair and one current logical authority slot; generations abstracted to old versus current.
- One publication path per scenario; simultaneous multi-path deliveries are not yet modeled.
- `anchor_available=true` assumes a monotonic current authority outside the modeled rollback domain.
- Current-work blocking is binary and does not model queues/backpressure duration.
- No key rotation, compromised signer, Byzantine path, partial compensation amount, cross-region quorum, or anchor disaster recovery.
- Counts are equal-weight synthetic mechanisms, not production rates.

## Exact Phase-1 continuation

Continue with **anti-rollback anchor lifecycle, key rotation, and multi-path simultaneous delivery**.

Next grammar:

- two old publications may race through different paths in the same scenario;
- certificate signer/key epochs rotate and old keys may remain trusted, be revoked, or be restored from backup;
- anti-rollback anchor states `CURRENT / STALE_REPLICA / LOST / RECOVERED_FROM_QUORUM`;
- barrier update response may be ambiguous before failover;
- restore may replay a validly signed but superseded retirement certificate;
- current generation advances g3→g4 while recovery occurs;
- compare permanent tombstone, single-anchor minimum, quorum/monotonic anchor, certificate transparency/append-only version witness, and safe archive;
- measure double-path duplicate repair, rollback ABA, old-certificate replay, false current-work exclusion, recovery reads, and safe compaction coverage;
- test whether a quorum-backed monotonic certificate-version floor is sufficient to make old signed retirement certificates harmless after restore/key rotation.

Keep the Phase-1 frontier nonempty; do not restore unrelated base research while the overlay remains active.
