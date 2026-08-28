# Phase-1 evidence retention / compaction stress test

- role: `multi_agent`
- phase: `phase_1_chat_parity`
- root_problem_id: `o-chat-parity-root-v2-active-pool`
- assignment_task_id: `phase1-clean-multi-agent-concurrency-claims`
- bootstrap_valid: `true`
- frozen semantic tuple: note main `9c76f42557b6dee420c8ff1f424f66b619465b5f`, root control revision `22`, root blob `e4f6d24c137284d002941ac04254e3dbeca2cfcb`, role config revision `6`, role blob `9a3edbe40ee5cbf3a94fe3206606aa58841c955c`.
- post-freeze root/config identities were repeatedly verified by SHA/path/blob-only transport and remained exactly the frozen blobs; no newer-head semantic content was adopted.
- semantic inputs: own immediately preceding Phase-1 evidence-reducer artifact, public Stripe/Adyen/AWS documentation, and this finite synthetic model only.

## Leaf objective

The prior leaf required immutable event identity plus a single-current reducer. This leaf asks what can be safely discarded when evidence grows indefinitely.

It separates four horizons that are often incorrectly collapsed:

1. **source-state finality horizon** — after what point can the effect no longer transition?
2. **delivery/redelivery horizon** — how long can the same event be resent?
3. **retrieval/archive horizon** — how long can historical evidence be fetched/replayed?
4. **local dedupe/tombstone horizon** — how long does the reducer remember that a logical trigger/event was already consumed?

The central test is whether compaction can reduce storage without turning any of those horizons into a false proof of finality or permitting old evidence to re-trigger an exclusive compensation.

## Public mechanism evidence

Stripe's current webhook documentation says live-mode automatic delivery retries can continue for up to **three days**; Dashboard manual resend is available up to **15 days**, Stripe CLI resend up to **30 days**, event delivery order is not guaranteed, and event IDs should be tracked to handle duplicates. Stripe's Events API documentation says event listing goes back up to **30 days**.

- https://docs.stripe.com/webhooks
- https://docs.stripe.com/api/v2/core/events/list

These are delivery/retrieval surfaces, not state-finality guarantees. In particular, they do not prove that a payment/refund state can no longer change after 3, 15, or 30 days.

Adyen's refund documentation gives a direct reason not to conflate delivery/retrieval with finality: a REFUND webhook with successful validation normally predicts success, but the refund can still later produce `REFUND_FAILED` or `REFUNDED_REVERSED`, including failure a few days after submission.

- https://docs.adyen.com/online-payments/refund

Amazon EventBridge archives provide a contrasting replay surface: retention is configurable and defaults to indefinite, replay does not remove archived events, and replay order is not necessarily the original archive order.

- https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-archive.html

Therefore a local tombstone chosen only from a short automatic-retry window is not a generic dedupe proof when manual resend, API retrieval, archives, or delayed writers can outlive it.

## Finite model

The executable enumerates **77,760 equal-weight synthetic scenarios** over:

- source finality contract: `3 days`, `30 days`, or `unknown`;
- certification grace: 3 / 30 / 90 days;
- contract-consistent late transition: none / day 2 / day 10 / day 40 / day 100;
- late evidence delivered vs lost;
- authoritative current-status lookup absent/present;
- local event/trigger tombstone: 3 / 30 / 90 days;
- duplicate redelivery age: day 2 / 10 / 40 / 100;
- archive: none / synthetic provider-30-day / own-indefinite;
- compaction crash point: none / after snapshot before truncate / after truncate before commit marker;
- snapshot schema: current / old-migratable / old-unmigratable;
- current vs stale compactor epoch.

Known-bound scenarios exclude transitions after that explicit bound. `unknown` deliberately leaves later transitions possible. A source finality bound is a modeled contract; it is never inferred from webhook retry, manual resend, retrieval, or archive retention.

Compared policies:

- `raw_append_finality_gate` — retain all event/trigger identities and terminalize only behind explicit source finality/evidence-completeness proof.
- `neg_snapshot_truncate_immediate` — compact to a root snapshot, terminalize immediately, and discard dedupe identity.
- `snapshot_tombstone_source_gate` — source-gated snapshot with finite local tombstone but deliberately no compactor fence / atomic commit marker.
- `versioned_snapshot_terminal_witness` — source-gated versioned snapshot, retained terminal/trigger witness identities, fenced compactor, crash-safe commit marker.
- `archive_replay_fallback` — compact locally and use status/archive replay when available, with deterministic trigger identity.

## Main results

| policy | terminal coverage | unsafe scenarios | duplicate-trigger scenarios | compaction-crash ambiguity | synthetic storage units |
|---|---:|---:|---:|---:|---:|
| raw_append_finality_gate | 29,592 / 77,760 = **38.06%** | **0** | 0 | 0 | 8 |
| neg_snapshot_truncate_immediate | 77,760 = 100% | **77,760 (100%)** | **77,760** | 51,840 | 1 |
| snapshot_tombstone_source_gate | 19,728 = **25.37%** | **64,800 (83.33%)** | **38,880** | 25,920 | 3 |
| versioned_snapshot_terminal_witness | 19,728 = **25.37%** | **0** | 0 | 0 | 4 |
| archive_replay_fallback | 19,728 = **25.37%** | 8,640 (11.11%) | 0 | 8,640 | 3 average |

All counts are finite mechanism counts, not production probabilities. The safe compacted policy intentionally leaves old-unmigratable and evidence-incomplete cases unresolved; lower terminal coverage is not counted as failure.

## Result 1: delivery/replay retention is not finality

In the `unknown_finality_bound_with_future_transition` slice there are **31,104** scenarios. The immediate-snapshot negative control emits a terminal success in all 31,104 and every one is false once the allowed later transition occurs.

All source-gated policies emit **zero terminal claims** in that unknown-bound slice. This is the core proof boundary: a webhook retry window, event-list retention period, or archive retention setting describes evidence availability, not the maximum lifetime of the underlying business state.

Adyen's late refund failure/reversal lifecycle is exactly the kind of public counterexample that makes this distinction necessary.

## Result 2: finite event tombstones can re-enable duplicate exclusive effects

The `duplicate_after_tombstone_expiry` slice contains **38,880** cases. The finite-tombstone policy produces a duplicate compensation trigger in **38,880 / 38,880**; the immediate-truncate control does the same. Raw append, retained terminal/trigger witness, and archive fallback with deterministic trigger identity produce zero duplicate triggers in this slice.

A narrower slice where a modeled provider replay surface can still reach the event while the local tombstone has already expired contains **6,480** cases; the finite-tombstone design duplicates all 6,480.

The generic rule is therefore not "retain raw events forever." It is: **retain the logical effect/trigger consumption identity for at least as long as any supported replay/retry surface can resurrect that authority, or make the sink-side trigger identity durably single-use beyond raw-event retention.**

## Result 3: snapshot atomicity and compactor epoch are independent of evidence finality

Among **51,840** compaction-crash scenarios:

- immediate snapshot/truncate is ambiguous in 51,840;
- the finite-tombstone design is ambiguous in 25,920 (`truncate` happened before a durable snapshot/commit marker);
- raw append and versioned witness are 0;
- archive fallback has 8,640 ambiguous scenarios, exactly the modeled cases where neither archive nor status lookup can reconstruct the cut.

The archive fallback's stronger supported subset — archive or status recovery available and schema not `old_unmigratable` — contains **43,200** scenarios and has unsafe count 0 in a direct model slice. Outside that capability surface it fails closed or remains ambiguous; "archive fallback" is therefore conditional, not a universal safe primitive.

For stale compactor takeover, the versioned-witness and archive policies fence **38,880 / 38,880** stale compactor attempts. The unfenced finite-tombstone design accepts them and is unsafe throughout that stale-takeover slice.

## Result 4: versioned terminal witnesses are a compact safety boundary, not a finality oracle

The versioned-witness policy uses half the model's raw-append storage units (4 vs 8), has zero duplicate-trigger, crash-ambiguity, stale-compactor-acceptance, or false-terminal scenarios in the tested lattice, and still refuses to terminalize when:

- source finality is unknown;
- required late evidence is lost and neither status nor archive proves current state;
- snapshot schema cannot be migrated safely.

Its retained witness must include at least current effect/compensation identity, source-qualified terminal evidence identity/digest, deterministic exclusive-trigger identity/consumption result, snapshot schema/version, source contract/version, reducer/compactor epoch, and the compaction cut/commit identity. Raw historical payloads may then be moved to cheaper retention without erasing the proof needed to prevent ABA-like duplicate recovery.

## Current candidate protocol

1. Treat `finality_bound`, `redelivery_window`, `retrieval/archive_window`, and `dedupe_witness_lifetime` as separate source-qualified fields.
2. Never derive state finality from delivery or event-retention documentation.
3. Compact only behind a fenced compactor epoch and an atomic/versioned snapshot-commit boundary; crash between snapshot and truncation must be replay-safe.
4. Preserve deterministic effect/compensation trigger identities beyond raw event TTL so duplicate/replayed evidence cannot reissue an exclusive effect.
5. Preserve current object/attempt identity and terminal witness provenance so stale historical evidence cannot become current merely because old raw records were compacted.
6. Make snapshot schema migration fail closed. An unreadable old snapshot is not equivalent to an empty current state.
7. Archive/status fallback is a capability-conditioned recovery branch. Record its exact retention/consistency scope; if the evidence age exceeds that scope, do not retry/terminalize by assumption.

## Persistence note

The result JSON was exact-readback persisted. The repository script is an inspectable semantically equivalent compact form of the locally executed model; repository byte identity is not claimed for the executed source. Receipts must bind the repository blob IDs actually persisted and must not falsely claim byte-identical source execution.

## Exact Phase-1 continuation

Continue with **claim/effect ABA under garbage collection and key reuse**.

Next finite grammar:

- deterministic task/effect key reused after claim/tombstone GC;
- old worker/result/event delayed past GC and arriving after a new claim for the same logical key;
- monotonically increasing epoch preserved vs lost/reset on restart;
- random reservation/incarnation ID preserved vs regenerated;
- stale worker wakes after lease expiry and after tombstone deletion;
- reducer/trigger witness compacted vs retained;
- parent generation reused accidentally vs immutable parent incarnation;
- compare key-only claim, key+TTL, key+epoch, key+unique incarnation ID, persistent monotonic generation + incarnation, and immutable staging + fenced current-incarnation integrator;
- measure stale-result acceptance, duplicate authoritative effect, false exclusion, ABA acceptance, storage/GC burden, and safe key-reuse coverage.

Public-source audit target: official mechanisms that distinguish object identity/incarnation from mutable name/key (for example Kubernetes object UID/resourceVersion and lock/token ownership rules). Preserve the CLEAN boundary and keep a nonempty Phase-1 frontier after that leaf.
