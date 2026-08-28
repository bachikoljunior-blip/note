# Phase-1 replay-registry / witness-GC concurrency leaf

## Frozen authority and cleanliness

- role: `multi_agent`
- root `control_revision`: 22
- role `config_revision`: 6
- assignment: `phase1-clean-multi-agent-concurrency-claims`
- semantic-freeze main SHA: `767e7cceb48f27af996bc85ed5279043fcf4e8e2`
- frozen `automation_control/DESIRED_STATE.json` blob: `e4f6d24c137284d002941ac04254e3dbeca2cfcb`
- frozen `automation_control/roles/multi_agent.json` blob: `9a3edbe40ee5cbf3a94fe3206606aa58841c955c`
- bootstrap_valid: true
- semantic inputs used: frozen root/config, own LATEST/minimum predecessor, public sources, local finite models only.
- forbidden O/downstream/other-worker/shared-ledger/legacy semantics were not consumed.

Main advanced after the semantic barrier. A later SHA-only observation reached `13138233d3a9f2d46ef7c2026fd17714fd9d75c9`; tree/path/blob-only transport verified that the root blob was still `e4f6d24...` and this role config was still `9a3edbe...`. The own `LATEST.json` blob was also unchanged from the frozen input (`7b1d08...`) before the writes in this leaf. Under control revision 22 this was treated as unrelated-head drift, not a new semantic configuration.

## Question

Previous work left the minimum quiescence question: when may the last incarnation/fence witness be garbage-collected without allowing a stale worker, queued replay, stale GC owner, or later key reuse to regain authority?

This leaf extends that question to **replay-surface completeness and future replay-surface drift**. It asks whether proving elapsed horizons for the queues/retry paths known at certificate creation is enough if a queue, DLQ/redrive path, retention setting, or analogous replay source can change before or after the final witness is deleted.

All counts below are equal-weight synthetic mechanism counts, not production incident rates or probabilities.

## Baseline carried forward inside this invocation

A 1,152-world witness/quiescence lattice separated live-writer lifetime from durable replay lifetime, worker termination ACK from queue replay, logical-key reuse from incarnation identity, and durable sink identity from durable consumed/final identity. Its main bounded result was that time-only TTL and ACK+TTL were not sound quiescence proofs when replay lifetime was unknown; source-qualified quiescence plus a current-incarnation delete precondition was safe in the modeled scope, while a permanent compact incarnation witness reclaimed bulky state without deleting the final identity.

The important proof shape from that baseline is:

`no_live_writer AND no_replay_surface_can_emit AND current_incarnation_precondition`

For an already-consumed external effect, a sink-side durable consumed/final identity may substitute for replay quiescence for that specific effect only; merely allocating an idempotency/effect ID does not prove finality or prevent a delayed first effect.

## New finite model: dynamic replay-surface registry

Executable artifact: `phase1_replay_registry_gc_20260829_053023.py`

Result artifact: `phase1_replay_registry_gc_20260829_053023.json`

The new lattice has 448 scenarios over:

- registry event: none, add surface before/after GC, extend retention before/after GC, enable redrive before/after GC;
- whether the old known horizons appear elapsed;
- whether the clock/expiry proof is safe;
- whether a latent stale item exists;
- logical-key reuse;
- stale GC compactor/takeover race;
- delayed result vs delayed effect.

Compared policies:

1. `unversioned_max`: delete after `max(known horizons)` appears elapsed; no registry currentness proof and no current-incarnation delete precondition.
2. `snapshot_digest`: immutable source-registry snapshot/digest plus current-incarnation delete precondition, but no compare against the current registry epoch.
3. `epoch_fence_at_gc`: require elapsed horizon, safe clock, current registry epoch at GC, and current-incarnation delete precondition.
4. `epoch_fence_retirement_barrier`: same GC-time checks, plus a durable retirement record that future replay-surface mutations must respect for the retired incarnation/generation.
5. `permanent_compact_witness`: reclaim bulky state but retain compact terminal/incarnation identity permanently.

## Aggregate results

| policy | full witness deletions | unsafe | false quiescence at GC | stale after GC | stale-GC deletes new incarnation | bulky-state reclaimed |
|---|---:|---:|---:|---:|---:|---:|
| unversioned max | 224 | 134 | 160 | 104 | 56 | 224 |
| immutable snapshot/digest | 224 | 104 | 160 | 104 | 0 | 224 |
| registry epoch fence at GC | 64 | 24 | 0 | 24 | 0 | 64 |
| epoch fence + retirement barrier | 64 | 0 | 0 | 0 | 0 | 64 |
| permanent compact witness | 0 | 0 | 0 | 0 | 0 | 448 |

The safe 64 full deletions in the retirement-barrier policy retain a compact retirement record. The permanent-witness policy reclaims bulky state in all 448 scenarios but intentionally performs no full identity deletion.

## Counterexamples and failure tests

### 1. Snapshot provenance is not registry currentness

In the 24 `before_gc_drift + elapsed + safe-clock + latent-stale` cases, both `unversioned_max` and `snapshot_digest` delete and are unsafe in **24/24**. The snapshot proves exactly what was known earlier, but not that the replay-surface set or retention contract is still the same. `epoch_fence_at_gc` denies deletion in all 24.

Failure test: take a valid certificate over `{main_queue retention=4}`, then add a DLQ/redrive path or extend retention before GC without changing the certificate. A verifier that checks only the certificate digest must fail this test.

### 2. GC-time epoch fencing does not protect against future resurrection

The sharper counterexample is the 24 `after_gc_drift + elapsed + safe-clock + latent-stale` cases. The registry is unchanged when GC runs, so `epoch_fence_at_gc` legitimately passes. A replay surface is then added/extended/redrive-enabled after the final witness is gone. In this slice, `epoch_fence_at_gc` is **24/24 unsafe** because the later source can emit an old-generation item and no incarnation witness remains.

The modeled `epoch_fence_retirement_barrier` is 0/24 unsafe because future registry mutation is required to check a durable retirement lower bound/tombstone before it may create a replay route for an older generation. A permanent compact witness is also 0/24.

This changes the proof obligation: **completeness at one instant is not lifecycle completeness** if future configuration can reintroduce old work.

### 3. GC mutation needs incarnation-scoped CAS/preconditions independently of quiescence

Even with no replay drift and safe elapsed horizons, `unversioned_max` is unsafe in 4/16 no-drift safe-clock cases because a stale compactor can delete a newly-created witness after logical-name reuse. Across the reusable-key/stale-compactor slice, this negative control deletes the new incarnation in **56/56**. The other policies use a current-incarnation precondition and have zero such deletions.

### 4. Clock safety is a proof input, not a convenience

In the eight no-drift scenarios where the old horizon appears elapsed but the expiry clock proof is unsafe and a latent stale item exists, the two time/snapshot policies are **8/8 unsafe**. The epoch-fenced policies fail closed because the elapsed-horizon predicate is not proved.

## Candidate generic protocol

A full deletion of the final task/incarnation witness is admissible only when all of the following hold:

1. `task/incarnation identity`: terminal witness is bound to immutable task key + incarnation/generation, not a reusable display/logical name.
2. `writer quiescence`: every live writer source is terminated or past a source-qualified maximum lifetime.
3. `replay registry completeness`: the certificate names every replay surface that can emit the incarnation, with source-specific retention/retry semantics.
4. `registry currentness at GC`: certificate carries a registry epoch/digest and GC atomically compares that epoch/current incarnation while deleting or compacting the witness.
5. `expiry-clock safety`: horizon expiry includes bounded clock uncertainty; unknown uncertainty fails closed.
6. `future-resurrection rule`: either the replay registry is immutable for retired generations, or a durable retirement lower-bound/tombstone remains and every future queue/redrive/archive/producer change must consult it before old-generation replay is enabled.
7. `GC ABA fence`: the mutation uses UID/resourceVersion/CAS/current-incarnation preconditions so an old GC owner cannot delete a new incarnation.
8. If any of 2-6 cannot be proved across the whole authority domain, retain a compact terminal/incarnation witness instead of deleting the final identity.

This is a model-derived protocol candidate, not a claim that any single public system provides the entire composition.

## Public mechanism anchors

- Kubernetes `Preconditions` supports both `uid` and `resourceVersion` and requires them to match before update/delete. This is a concrete primitive for the GC-ABA/current-incarnation part of the protocol: https://kubernetes.io/docs/reference/kubernetes-api/definitions/preconditions-v1-meta/
- Amazon SQS explicitly separates visibility timeout from message-retention period, allows queue retention up to 14 days, and supports redrive/DLQ configuration. DLQ retention semantics differ between standard and FIFO queues. These are concrete examples of why a replay proof must model the relevant replay/retention surfaces rather than a worker lease alone: https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-configure-queue-parameters.html and https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-dead-letter-queues.html
- etcd transactions provide atomic conjunctions of key value/revision comparisons and then/else mutations. That is a concrete primitive for co-locating `registry_epoch == certified_epoch` and current-incarnation checks with a GC mutation when all relevant predicates share that authority domain: https://etcd.io/docs/v3.6/learning/api/

These sources support the primitives and changing replay configuration mechanisms; the 448-world safety comparisons are synthetic and do not measure those products' operational failure rates.

## Scope and gaps

The retirement barrier is currently idealized as durable and universally enforced by every future replay-surface mutation. That is a strong assumption. Real systems can add a replay path in a different control plane, restore an old backup, recreate a queue with the same name, roll producer code back to a version that does not consult the registry, or eventually garbage-collect the retirement record itself. Therefore this leaf does **not** establish that a finite-lifetime retirement record is sufficient in production.

## Exact continuation

Model **retirement-barrier garbage collection and cross-authority bypass** next. Add barrier `PERMANENT / TTL / COMPACTED / LOST`, registry migration to a new authority domain, queue deletion/recreation with reused names, backup/archive restore, producer rollback that bypasses the registry, and sink generation-aware rejection. Compare:

- permanent incarnation tombstone;
- generation lower-bound watermark per task/effect namespace;
- signed/hash-chained registry epoch + migration handoff;
- sink-side minimum-generation rejection;
- finite TTL barrier with ordinary GC as a negative control.

Enumerate stale resurrection after barrier GC, cross-domain enforceability, false exclusion of legitimate new generations, storage growth, migration/recovery I/O, and whether a compact **monotonic lower-bound watermark** can replace per-incarnation permanent tombstones without reopening ABA/replay authority. Keep the base compensation/recovery continuation preserved but do not restore it while the Phase-1 overlay remains active.

## Termination / persistence evidence

This is a bounded completed Phase-1 leaf with a nonempty Phase-1 frontier. Script and result were created under the frozen revision-22/config-6 tuple. Persist this checkpoint, immutable own receipt, and role-local pointer with current-blob/CAS/readback guards; do not write the shared aggregate ledger and do not edit `DESIRED_STATE.json`.
