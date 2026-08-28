# Phase-1 retirement barrier rollback/bypass and late path admission

- role: `multi_agent`
- phase: `phase_1_chat_parity`
- root_problem_id: `o-chat-parity-root-v2-active-pool`
- assignment_task_id: `phase1-clean-multi-agent-concurrency-claims`
- bootstrap_valid: `true`
- frozen semantic main SHA: `8837998c1952db5f043bf73900db96482b4932d3`
- frozen DESIRED_STATE: control revision `22`, blob `e4f6d24c137284d002941ac04254e3dbeca2cfcb`
- frozen role config: config revision `6`, blob `9a3edbe40ee5cbf3a94fe3206606aa58841c955c`
- predecessor checkpoint: `research_workers_clean_g1/multi_agent/PHASE1_REPAIR_QUIESCENCE_COMPACTION_20260829_062646_JST.md`
- post-freeze unrelated main advance observed: `be769a354c7385f57f589181233ed948ff5f6427`
- postfreeze_authoritative_identity_verified: `true`; empty-content path/blob reads at that later head returned the same frozen root/config blobs.
- semantic inputs: own frozen role-local LATEST/predecessor checkpoint, public Apache Kafka/TUF/Kubernetes documentation, and two finite synthetic models below.

Artifacts:
- `research_workers_clean_g1/multi_agent/phase1_retirement_barrier_bypass_20260829_065649.py`
  - SHA-256 `f98797d9b1e756efbe5a30a006f68b176e3e2e0496d25413294ca834a5c3f637`
- `research_workers_clean_g1/multi_agent/phase1_retirement_barrier_bypass_20260829_065649.json`
  - SHA-256 `664d561ef3ce7907d13c1d23ecf454bfdbe6e2da5b089955d2cb6b1fd78c3021`
- `research_workers_clean_g1/multi_agent/phase1_late_path_admission_20260829_065649.py`
  - SHA-256 `9abf9806dc021165d4686384777405844d4e759076e18d8db899c933cfd2f11e`
- `research_workers_clean_g1/multi_agent/phase1_late_path_admission_20260829_065649.json`
  - SHA-256 `3797e9952c0e0ff403e714a1d549768d73f25e8eab0bb9a1fbc8dbd2020fd5cd`

## Public mechanism boundary

Three public mechanisms help delimit the candidate protocol without being treated as identical to it.

1. Apache Kafka exposes broker-side epoch fencing: the protocol reports `INVALID_PRODUCER_EPOCH` when an operation uses an old producer epoch, and the transactional documentation describes producer-epoch changes as part of server-side duplicate/stale-writer defense. This is a concrete example of the **authoritative sink** rejecting a stale writer rather than trusting a coordinator-local lease.
   - https://kafka.apache.org/21/design/protocol/
   - https://kafka.apache.org/43/operations/transaction-protocol/
2. The Update Framework (TUF) signs metadata, but also has clients detect outdated metadata and refuse metadata older than what they have already seen. Its snapshot metadata supplies a consistent version/hash view. This is a public example that **signature authenticity is not freshness**; trusted version/floor state is a separate obligation.
   - https://theupdateframework.io/docs/metadata/
3. Kubernetes distinguishes reusable object names from unique UIDs, and exposes UID/resourceVersion operation preconditions. This is a public example that logical-name reuse requires incarnation/version-sensitive authority checks.
   - https://kubernetes.io/docs/concepts/overview/working-with-objects/names/
   - https://kubernetes.io/docs/reference/kubernetes-api/definitions/preconditions-v1-meta/

The retirement certificates, sink generation floors, compaction units and policies below are synthetic application-level protocols, not claims that Kafka/TUF/Kubernetes provide those exact primitives.

## Leaf A — barrier rollback/bypass across publication paths

The first script enumerates **1,536 equal-weight synthetic scenarios** over repair finality, current generation g3/g4, old/current publication, queue/direct-API/retry-worker/restore path, coordinator check present/absent, sink floor current/rolled-back/missing, current/old/invalid/missing certificate, and whether the authority root is protected from restore rollback.

Compared policies:

| policy | unsafe old-generation publications | safe compactions | retained-state units |
|---|---:|---:|---:|
| coordinator-only | **192** | 576 | 960 |
| sink-floor compact regardless of rollback protection | **272** | 496 | 960 |
| signed certificate only | **96** | 672 | 960 |
| signed certificate + rollbackable floor | **68** | 700 | 960 |
| safe certificate + protected floor, else tombstone | **0** | **384** | **1,248** |
| permanent tombstone | **0** | 0 | 1,536 |

`retained-state unit` is a synthetic comparison unit: detailed/per-incarnation witness = 1.0, compact floor+certificate root = 0.25. It is not a byte estimate.

### A1. Coordinator-only retirement does not cover bypass paths

In the targeted `FINAL + old g1 + coordinator check absent` slice, coordinator-only retirement permits stale publication in **192 / 192** cases. A direct API or restore path that never reaches the coordinator is outside that proof.

### A2. A valid signature can authenticate a stale certificate

In the targeted `FINAL + old g1 + old_valid certificate` slice, `signed_cert_only_compact` is unsafe in **96 / 96** cases. This is the same structural distinction illustrated by TUF: a signature proves who signed metadata, not that its version is fresh enough for the receiver.

Adding a local generation floor reduces but does not eliminate the problem if that floor can itself be missing or rolled back. In the exact susceptible `old_valid cert + effective floor <= g1` slice, certificate+floor is unsafe in **68 / 68** cases.

### A3. Compaction is safe only when the future publication authority cannot roll back the floor

The strong policy compacts only when a monotonic sink-local retirement authority is outside the restore/rollback domain. In the protected `FINAL + old g1` replay slice, it has **0 / 192 unsafe publications**. In the 384 final worlds where such a protected authority is unavailable, it refuses compaction and retains the per-incarnation tombstone instead of guessing that the barrier will survive.

This yields a conditional state-saving result in the model: retained-state cost 1,248 units versus 1,536 for permanent tombstones, with unsafe old-generation publication 0. The difference is a synthetic mechanism trade-off, not a storage benchmark.

## Leaf B — future path and sink admission after compaction

The second script enumerates **1,536 equal-weight post-finality scenarios** over queue/direct/restore path, old/new path, old/new sink instance, current/old/invalid/missing certificate, current/stale registry, current/missing local floor, global watermark available/unavailable, old/current publication, and enrollment bypass.

| policy | unsafe old publication | unsafe new-path/new-sink publication | blocked current publication | per-publication authority reads | retained units |
|---|---:|---:|---:|---:|---:|
| registry admission only | **672** | 480 | 0 | 0 | 384 |
| signed cert bootstrap, no remembered floor | **192** | 144 | 384 | 0 | 384 |
| inherited sink floor only | **576** | 480 | 0 | 0 | 384 |
| enrollment cert + pinned floor | **0** | **0** | 540 | 0 | 384 |
| shared watermark on every publish | **0** | **0** | 576 | 1,536 | 384 |
| permanent tombstone | **0** | **0** | **0** | 0 | 1,536 |

Again, counts are equal-weight synthetic mechanisms, not rates.

### B1. New authority domains are part of the retirement proof

A sink-local floor that is safe on an existing sink is not inherited by a new sink automatically. In the targeted `old g1 + new sink` slice, `inherited_sink_floor_only` accepts stale work in **384 / 384** cases.

Likewise, bootstrapping a new path/sink from any still-valid signed certificate is unsafe when the sink remembers no minimum accepted version: the `old_valid certificate + old g1` slice is **192 / 192 unsafe**.

### B2. Safe enrollment trades availability for retained-state reduction

The strong enrollment candidate requires a current certificate checked against a durable retirement watermark before a new/missing sink may serve, then pins the floor locally. Existing sinks with an already-current floor do not require a remote read. It has **0 / 768 unsafe old-generation publications** in the old-message half of the lattice, but fail-closes **540 / 768** current-publication scenarios where enrollment freshness cannot be established.

A shared watermark read on every publication also has unsafe 0, but performs 1,536 authority reads and blocks 576/768 current-publication scenarios under unavailable/bypassed authority. A permanent tombstone has neither safety nor liveness failures in this small model, at four times the synthetic retained-state unit cost of the compact certificate/floor approaches.

The model therefore does **not** support a blanket claim that compaction dominates tombstones. It supports a narrower candidate: compact only when every present and future authoritative sink must either (a) inherit/pin a monotonic retirement floor before serving, or (b) fail closed until it can prove a current floor.

## Candidate protocol after both leaves

1. Do not advance retirement while cancellation/compensation for that generation remains non-final.
2. Put the stale-generation rejection check in the authority domain that can actually commit the effect; coordinator-local barriers are advisory unless every effect path is structurally forced through them.
3. Persist a monotonic `minimum_generation` (and certificate/version floor if certificates distribute it) outside any restore/rollback domain that can re-enable old publication.
4. Treat signatures as provenance only. A receiver must compare certificate generation/version against trusted monotonic local or shared state; an older valid signature must not lower the floor.
5. Include direct API, retry worker, queue/redrive and restore/archive publication paths in the authority proof. A path that bypasses the sink fence invalidates compaction.
6. For a new or blank sink authority, require enrollment against a current retirement certificate/watermark and pin the resulting floor before serving. If that cannot be proved, keep the compacted generation unavailable on that sink rather than coming up permissive.
7. If the floor/certificate root itself is rollbackable or future sink admission can bypass enrollment, retain a compact per-incarnation tombstone; do not infer permanent quiescence from elapsed time, a registry snapshot, or a signature alone.
8. Keep current-generation liveness as a separate metric: safety can be achieved trivially by fail-closing everything, so candidate selection must report current-publication blockage and authority-read cost alongside stale-publication safety.

## Exact tested scope

- Leaf A: one historical generation g1, current generation g3/g4, one effect publication at a time, four publication paths and one boolean-protected sink authority root.
- Leaf B: post-finality only, one historical generation g1/current floor g3, one publication at a time, one old/new sink instance and one old/new path.
- No Byzantine signer, compromised signing key, quorum, multi-region consensus, network partition, partial-value compensation, or two simultaneous authoritative effects.
- Protected authority is modeled as truly monotonic. The implementation mechanism that makes it rollback-resistant is outside these finite models.
- Equal-weight counts are mechanism coverage counts, not production probabilities.

## Exact Phase-1 continuation

Continue with **authority-set membership change and multi-sink retirement certificates**.

Next grammar:
- 2-3 authoritative sinks, each with independent `minimum_generation` and authority epoch;
- membership epochs `m1/m2`, sink join/leave/re-add, and logical sink-name reuse;
- g1 retired while g3/g4 current effects route to one sink, any sink, or a quorum;
- asynchronous floor propagation, stale member, restore rollback, missing member, and partition;
- certificate binds `{membership_epoch, minimum_generation, repair-finality digest}` and may be current/old/partially installed;
- compare coordinator quorum ack, all-authoritative-sink ack, membership-versioned certificate + per-sink pin, shared authoritative floor, and permanent tombstone;
- explicitly test whether a quorum retirement certificate is safe **only when the external effect itself also requires the same quorum**, versus unsafe when any single stale sink can commit authoritatively;
- measure stale g1 publication, false exclusion/current-generation blockage, membership ABA, convergence messages/reads, safe compaction coverage and retained-state units.

Keep the Phase-1 frontier nonempty; do not restore unrelated base research while the overlay remains active.
