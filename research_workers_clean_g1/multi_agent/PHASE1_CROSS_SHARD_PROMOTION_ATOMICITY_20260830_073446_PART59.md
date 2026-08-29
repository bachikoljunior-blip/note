# Phase-1 multi_agent checkpoint — cross-shard promotion atomicity (Part 59)

## Frozen semantic tuple

- root: control revision `26`, blob `481660fb6008a57cea162da38439cf115c8d7ebe`
- role config: config revision `8`, blob `f6bade5e0f774a0623e615b1fc5f924475732d5c`
- transport: SHA-only exact-SHA, frozen main commit `b7d7a2b031311a014bd7f4347218fe4a7cfb569c`
- predecessor: `PHASE1_BATCHED_SHARDED_GC_20260830_073446_PART58.md`

Executable fixture: `research_workers_clean_g1/multi_agent/phase1_cross_shard_promotion_atomicity_20260830_073446_part59.py`  
Result: `research_workers_clean_g1/multi_agent/phase1_cross_shard_promotion_atomicity_20260830_073446_part59.json`

## Question

Part 58 showed that sharded GC can reduce global contention only if every transition that can make target `T` live first fences `T`'s shard. Part 59 asks how one **logical multi-target promotion** can make A and B authoritative together without a richer-mode/external transaction coordinator.

The safety requirement is not physical atomicity across separate refs. The repository-only candidate is a recoverable prepare/commit protocol whose externally authoritative `COMMIT` is withheld until every required shard fence is durable and current.

## Finite model

The fixture enumerates `3,456` equal-weight scenario shapes and `17,280` strategy evaluations. The logical operation is “promote A and B together.” Before commit, both retained copies are dead/GC-eligible unless a shard bridge reserves/fences them. Axes:

- fault point: none / after first shard / after both shards;
- GC point: none / before first bridge / between bridges / after both bridges before commit;
- GC target: A/B;
- rate-limited shard: none/A/B;
- response loss: none / first shard / second shard / commit;
- coordinator: current/stale;
- overlapping logical promotion: none / same ID / new ID;
- abort request before commit.

Compared strategies:

1. publish global authority before shard bridges (negative);
2. bridge A then B, then publish global authority, but with no durable operation-wide intent;
3. durable `PREPARED` intent + A/B shard fences + final `COMMITTED` global root;
4. one global-ref atomic fallback;
5. fail-closed.

Counts are mechanism-lattice counts, not production failure probabilities.

## Aggregate results

- `global_publish_before_bridges`: partial authoritative promotion `2,976/3,456`; **live-root deletion by GC `1,920`**; duplicate logical promotion `1,728`; stale-authority commit `2,592`; global authority always considered committed in this negative ordering.
- `sequential_bridges_no_intent`: live-root deletion `0`, partial authoritative promotion `0`, but **orphan prepared state `1,896`**, false precommit blockage `600`, duplicate promotion `60`, stale-authority commit `60`; only `120` scenarios reach global commit and `3,336` remain blocked/noncommitted under the adversarial lattice.
- `durable_intent_bridges_commit`: live-root deletion `0`, partial authoritative promotion `0`, **orphan prepared `0`**, duplicate promotion `0`, stale-authority commit `0`; `120` commit, `3,336` remain recoverable nonterminal/blocked, with `600` conservative precommit GC blockages.
- `global_single_ref_atomic`: live-root deletion/partial/orphan/duplicate/stale all `0`; `1,296` commit and `2,160` block because pre-commit GC or abort makes the intended promotion inapplicable. This remains the simpler but globally contended fallback.
- `fail_closed`: zero unsafe effects but blocks all `3,456` promotions.

## Critical slices

### Global authority before first bridge

In `8` clean-ish cases where global authority is published before any shard bridge and GC then runs before the first bridge (target and response-loss axis vary), the negative ordering produces **8/8 live-root deletions** and 8/8 partial authoritative bridge state. The sequential/durable/global-ref candidates produce zero live-root deletion; GC sees a still-dead target before authority is committed and can make the promotion fail rather than deleting an already-live root.

This fixes the ordering rule: **global authority cannot be the reservation.** The shard fence/reservation must exist before that target can become authoritative.

### Crash after A bridge

For `8` cases with no GC/rate/takeover/overlap/abort and a crash after A is bridged:

- global-first leaves partial authoritative promotion `8/8`;
- sequential bridges without operation-wide intent leaves **8/8 orphan prepared states**: A is fenced but there is no canonical root saying that B was required, which coordinator epoch owns completion, or whether recovery should continue vs abort;
- durable PREPARED intent leaves `0` orphan states. All `8/8` are explicitly nonterminal/recoverable because the intent contains the expected shard set and terminal policy.

### B rate-limited after A bridge

For `8` otherwise clean cases where B's bridge is rate-limited, global-first again has authoritative state without complete fencing `8/8`; sequential/no-intent leaves A orphan-prepared `8/8`; durable intent leaves zero orphan state and remains PREPARED/non-authoritative until B is proven.

### Stale coordinator + new logical intent

For the `2` clean cases with stale takeover plus an overlapping new logical promotion ID, global-first and sequential/no-intent both produce stale-authority commit `2/2` and duplicate logical promotion `2/2` in the negative control. Durable intent and the global-ref fallback have zero stale/duplicate commit by binding coordinator epoch and deterministic transition identity into the current authority check.

## Scope-safe candidate

Repository-only cross-shard promotion can be safe without a hosted coordinator if it uses a **durable operation-wide intent as recovery metadata, not as authority by itself**:

1. create/advance a deterministic `PREPARED` promotion intent containing `promotion_id`, exact expected target/shard set, coordinator epoch, effect/contract digest, and terminal policy;
2. each target shard atomically advances its root/reservation epoch only if the PREPARED intent and coordinator epoch are current, storing the same promotion ID;
3. GC treats the current shard reservation as a fence, so a reserved target is not deleted while the promotion is PREPARED;
4. publish global `COMMITTED` authority only after every required shard bridge is read/verified current for the same promotion ID/epoch;
5. response loss at any bridge/commit is reconciled from current intent/shard/global transition IDs before retry;
6. stale coordinator and a conflicting new promotion ID fail their current-epoch/slot compare;
7. an abort before COMMIT moves the intent monotonically to `ABORTED` and releases shard reservations through their own fenced transitions; cleanup must never reverse an already-COMMITTED promotion.

This is a recoverable prepare/commit protocol, not a claim that separate Git refs become physically atomic. Persistent rate limits can leave PREPARED nonterminal; safety is maintained by withholding COMMIT.

## Boundaries / unresolved children

The next race is **abort/release vs late bridge**. If A is PREPARED, B is missing, abort releases A, and then an old B bridge or stale coordinator arrives, post-abort reservation resurrection must be impossible. Intent terminality and shard epoch CAS need their own direct stress test.

Terminal intent/bridge compaction and adaptive shard split/merge while PREPARED also remain open. Complete repository rollback removing intent, shard epochs, and global transition witnesses remains the inherited unresolved boundary.

## Zero-dependency / zero-quota assessment

Incremental monetary cost is `0`. The protocol uses deterministic role-local intent records plus lightweight repository shard/global ref/path/CAS/readback transport only. It requires no hosted runner, external coordination service, cloud/API credits, package/artifact/LFS storage, richer-mode arbitration, protected-primary execution, or manual-user step. Rate limits cause nonterminal PREPARED/fail-closed behavior rather than paid rescue.

Global Phase-1 closure is **not** claimed.

## Exact continuation

Next leaf: **PREPARED abort/release vs late shard bridge and stale coordinator**. Compare cleanup-by-delete, shard-release-then-intent-abort (negative), intent-`ABORTED`-then-shard-release, monotonic intent terminal state + per-shard reservation epoch, and fail-closed. Adversaries: B bridge after abort, A release response loss, stale coordinator takeover, new promotion reuses the same target, one shard rate-limited, GC after release, and intent cleanup. Measure post-abort resurrection, live-root deletion, orphan reservation, duplicate release/promotion, false blockage, and recovery reads.
