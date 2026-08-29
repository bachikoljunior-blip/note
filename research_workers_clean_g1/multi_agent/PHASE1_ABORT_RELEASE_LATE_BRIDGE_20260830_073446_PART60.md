# Phase-1 multi_agent checkpoint — PREPARED abort/release vs late shard bridge (Part 60)

## Frozen semantic tuple

- root: control revision `26`, blob `481660fb6008a57cea162da38439cf115c8d7ebe`
- role config: config revision `8`, blob `f6bade5e0f774a0623e615b1fc5f924475732d5c`
- transport: SHA-only exact-SHA, frozen main commit `b7d7a2b031311a014bd7f4347218fe4a7cfb569c`
- predecessor: `PHASE1_CROSS_SHARD_PROMOTION_ATOMICITY_20260830_073446_PART59.md`

Executable fixture: `research_workers_clean_g1/multi_agent/phase1_abort_release_late_bridge_20260830_073446_part60.py`  
Result: `research_workers_clean_g1/multi_agent/phase1_abort_release_late_bridge_20260830_073446_part60.json`

## Question

Part 59 made a durable `PREPARED` intent the recovery root for multi-shard promotion and required abort-before-COMMIT to become `ABORTED` before shard cleanup. Part 60 stress-tests that cleanup boundary under late old writers, ambiguous release responses, target reuse, rate limits, and terminal-record cleanup.

The starting state is promotion `P` PREPARED, shard A reserved by `P/A`, shard B unreserved, and an abort request before global COMMIT.

## Finite model

The fixture enumerates `648` equal-weight scenarios and `3,240` strategy evaluations. Axes:

- old late action: none / B bridge / A reacquire;
- stale coordinator present or not;
- new promotion reuses none/A/B;
- A release response observed / applied-response-lost / not-applied-response-lost;
- A release rate-limited or not;
- terminal intent kept vs deleted after abort;
- GC after release targets none/A/B.

Compared strategies:

1. delete the intent/cleanup record instead of writing a terminal state;
2. release A while intent is still PREPARED, then mark ABORTED;
3. mark ABORTED first but release A by name/path only;
4. monotonic ABORTED transition + exact promotion/reservation epoch release + compact terminal witness;
5. fail-closed.

Counts are mechanism-lattice counts, not production probabilities.

## Aggregate results

- `cleanup_by_delete`: post-abort resurrection `444/648`, late bridge accepted `444`, unreconstructible orphan `546`, stranded old reservation `546`, stale release of a new reservation `6`, live-root deletion by subsequent GC `2`, duplicate release attempts `54`.
- `release_then_abort`: post-abort resurrection `324`, late bridge accepted `324`, stranded old reservation `486`, unreconstructible orphan `243`, stale release of new reservation `18`, live-root deletion `6`, duplicate release attempts `108`.
- `abort_then_release_name_only`: abort ordering removes one reacquire window but still has post-abort resurrection `180` when the terminal witness is later deleted, stale release of a new reservation `36`, live-root deletion `12`, unreconstructible orphan `252`, duplicate release attempts `108`.
- `monotonic_abort_epoch_release`: post-abort resurrection `0`, late bridge accepted `0`, stale release of new reservation `0`, live-root deletion `0`, unreconstructible orphan `0`, duplicate release attempts `0`. It has `324` cleanup-pending old reservations and `108` false blockages under the rate-limit axis, but all are still reconstructible from the retained terminal witness/epoch.
- `fail_closed`: zero unsafe effects but blocks reuse/GC where A remains indefinitely reserved.

## Critical slices

### Release before ABORTED

In `3` cases where A is released, an old A writer reacquires while the intent is still PREPARED, and then the intent becomes ABORTED, `release_then_abort` accepts the reacquire `3/3`; the late P reservation survives the already-passed release step. Deleting the intent instead is worse: the same `3/3` are unreconstructible orphans. Both abort-first strategies reject this old writer while the terminal witness exists.

Ordering is therefore not cosmetic: **PREPARED → ABORTED must become current before any shard release that old PREPARED writers could race.**

### Ambiguous release + immediate target reuse

There is one clean counterexample where A release actually applies but its response is lost, a new promotion acquires A, the old abort path blindly retries release, and GC then targets A. All three name/path-based cleanup variants delete the **new** reservation on retry, and GC subsequently deletes the newly-live root. The exact-epoch candidate reads back current reservation state, sees that `P/A` is already gone / a newer epoch now exists, and performs zero stale release and zero live-root deletion.

Thus release idempotency needs an **effect identity plus incarnation/epoch**, not merely “delete path A again.”

### Deleting the terminal witness

In `3` cases with a late/stale B writer after abort and explicit terminal-record deletion, cleanup-by-delete, release-then-abort, and abort-then-name-only all accept stale B and leave `3/3` post-abort resurrection plus `3/3` unreconstructible orphan. The strong candidate permits bulky intent compaction only if a compact promotion-id/terminal-epoch witness remains; stale B is rejected `3/3`.

`ABORTED` therefore has to be an absorbing authority fact for as long as an old bridge/release can be replayed. Deleting the only witness is equivalent to forgetting the fence.

## Scope-safe candidate

1. CAS the intent monotonically from current `PREPARED` to `ABORTED` under the current coordinator epoch;
2. every bridge/reacquire must prove the intent is still current `PREPARED` for the exact promotion ID/epoch, so late writers fail after ABORTED;
3. release a shard only if the current reservation matches exact `promotion_id + reservation_epoch/incarnation`;
4. if release response is ambiguous, read the current shard reservation before retry; never perform a name-only blind retry;
5. a new promotion receives a strictly newer reservation epoch, so stale cleanup cannot match it;
6. GC consults the current shard root/reservation: ABORTED-but-cleanup-pending remains conservatively fenced until exact cleanup succeeds;
7. bulky intent may be compacted only while retaining a compact terminal promotion-id/epoch witness in the authority domain used by old writers and cleanup.

Persistent rate limits can leave ABORTED cleanup pending. That is a recoverable liveness cost, not an orphan or permission to forget the fence.

## Boundaries / unresolved children

The strong candidate still retains terminal information. The next question is whether one tombstone per promotion is necessary or can be compressed into a monotonic per-target/per-shard lower-bound watermark without accepting very late old bridges/releases after target reuse or shard topology change.

Complete repository rollback that erases both the terminal witness and reservation epochs remains unresolved.

## Zero-dependency / zero-quota assessment

Incremental monetary cost is `0`. The candidate uses scheduled Chat plus role-local monotonic intent records and shard reservation CAS/readback only. No external coordinator, hosted compute, cloud/API credit, package/artifact/LFS storage, richer-mode arbitration, protected-primary execution, or manual-user step is introduced. Rate-limit interruption stays nonterminal/fail-closed.

Global Phase-1 closure is **not** claimed.

## Exact continuation

Next leaf: **terminal promotion-witness compaction**. Compare delete-all terminal records, per-promotion tombstone, per-target minimum reservation-epoch watermark, per-shard monotonic promotion-generation floor, and fail-closed. Adversaries: very late old bridge/release, new target incarnation, shard split/merge, restore/replay of an old checkpoint, response loss, watermark update lag, and rate-limit interruption. Measure old-writer acceptance, stale release of a new reservation, retained-state growth, false blockage, and recovery reads.
