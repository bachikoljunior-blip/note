# Phase-1 multi_agent checkpoint — batched/sharded GC publication vs hotspot pressure (Part 58)

## Frozen semantic tuple

- root: control revision `26`, blob `481660fb6008a57cea162da38439cf115c8d7ebe`
- role config: config revision `8`, blob `f6bade5e0f774a0623e615b1fc5f924475732d5c`
- transport: SHA-only exact-SHA, frozen main commit `b7d7a2b031311a014bd7f4347218fe4a7cfb569c`
- predecessor: `PHASE1_FENCED_APPLICATION_GC_20260830_073446_PART57.md`

Executable fixture: `research_workers_clean_g1/multi_agent/phase1_batched_sharded_gc_20260830_073446_part58.py`  
Result: `research_workers_clean_g1/multi_agent/phase1_batched_sharded_gc_20260830_073446_part58.json`

## Question

Part 57 showed that a target-file SHA fence is not enough when recovery-root membership lives in another mutable file: root membership and deletion need one atomic publication domain. Part 58 asks whether that domain must be one **global** ref, or whether it can be safely sharded to reduce unrelated contention.

The central distinction is between:

- shard-local deletion that is atomically fenced only against a shard-local manifest; and
- shard-local deletion where **every authority transition that can make target T live first advances T's shard-local root epoch before the promotion becomes authoritative**.

The latter is called the promotion bridge in this checkpoint.

## Finite model

The fixture enumerates `576` equal-weight scenarios and `2,880` strategy evaluations. Initially retained copies A and B are both dead at the GC snapshot. Independent axes are:

- post-snapshot promotion: none / A / B / both;
- overlapping second sweeper;
- GC rate limit on none / A / B;
- observed-success vs applied-response-lost publication;
- no reincarnation vs reincarnated A/B;
- no churn vs global-unrelated / A-shard-unrelated / B-shard-unrelated head churn.

Compared strategies:

1. one global retention-root ref and one global batch commit;
2. read global roots, then delete A/B independently in shard paths (negative TOCTOU baseline);
3. shard-local atomic delete+manifest publication but **no** bridge from global promotion to shard authority;
4. shard-local atomic delete+manifest publication **with** per-target promotion bridge;
5. no-delete/fail-closed.

Counts are mechanism-lattice counts, not production probabilities.

## Aggregate results

- `global_single_ref_batch`: live-root deletion `0`, wrong-incarnation deletion `0`, dead-copy deletion `8`, blocked dead copies `376`, false-conflict dead copies `336`, rate-limited dead copies `128`, batch abort `572/576`, duplicate delete attempts `0`.
- `global_root_check_then_shard_delete`: **live-root deletion `256`**, dead-copy deletion `256`, blocked dead copies `128`, duplicate delete attempts `512`, rate-limited dead copies `128`.
- `shard_local_no_bridge`: **live-root deletion `192`**, dead-copy deletion `192`, blocked dead copies `192`, duplicate delete attempts `0`; overlapping proposals conflict at the shard ref rather than duplicate the effect.
- `shard_local_with_bridge`: live-root deletion `0`, wrong-incarnation deletion `0`, dead-copy deletion `192`, blocked dead copies `192`, duplicate delete attempts `0`, false-conflict dead copies `96`, rate-limited dead copies `128`.
- `no_delete`: live/wrong deletion `0`, dead-copy deletion `0`, blocked dead copies `384`.

The global ref is safety-strong but over-conservative in this lattice: almost every unrelated target/shard event aborts the whole two-target batch. Sharding recovers independent progress, but only if promotions are bridged into the same shard authority before becoming authoritative.

## Critical slices

### One target becomes live

There are `4` cases where A is promoted after the GC snapshot and no rate limit, reincarnation, or unrelated churn occurs; overlap/response-loss vary.

- global batch: no unsafe deletion, but aborts `4/4` and blocks still-dead B `4/4`;
- read-global-then-delete: deletes promoted A live `4/4` and dead B `4/4`;
- shard-local without bridge: deletes promoted A live `4/4` and dead B `4/4` because the shard does not learn that A became globally authoritative;
- shard-local with bridge: live-root deletion `0/4`; promotion advances A's shard root epoch first, so stale A GC conflicts while dead B still deletes `4/4`.

Thus, sharding the GC manifest without sharding/bridging the **authority transition** is unsafe.

### Unrelated global head churn

For `4` cases where both targets remain dead and the only event is unrelated global head churn, the global batch aborts `4/4` and blocks eight target-deletions across the slice. The bridged shard strategy deletes both dead targets `8/8` because that global-unrelated write is outside A/B shard refs.

### One shard rate-limited

For `4` clean cases where A's GC path is rate-limited, the global batch blocks both A and B `4/4`. The bridged shard strategy blocks A but still deletes independent B `4/4`. Rate-limit failure therefore need not become a global coordination outage when the authority predicate is safely partitioned.

### Applied response loss

For the single clean response-loss case with both targets dead, the read-global-then-delete baseline produces two duplicate delete attempts under blind retry. The global batch and bridged shard candidates use deterministic transition IDs plus current ref/manifest readback and produce zero duplicate delete attempts.

## Scope-safe conclusion

A single global ref is not semantically required for repository-local GC safety. A shard can be an authority domain **only if every transition that can make a target live participates in that shard's fence before it becomes authoritative elsewhere**.

Candidate rule for target `T`:

1. map `T` deterministically to shard `S(T)`;
2. before any root/LATEST transition makes `T` live, advance `S(T)`'s root epoch/manifest (or an equivalent atomic shard fence) to record T as live;
3. only after that bridge is durable may the higher-level promotion be authoritative;
4. GC for T pins the shard ref/manifest, confirms T dead, builds one shard-local tree/commit that deletes the exact target and advances the shard GC manifest with deterministic transition ID, then publishes through shard-ref fast-forward CAS;
5. response loss is reconciled from current shard ref/transition ID before retry;
6. shard rate limit/churn blocks only that shard; unrelated global/shard activity need not block other shards.

This moves contention from one global GC root to per-shard epochs while preserving the Part57 predicate/effect co-location requirement.

## Important unresolved child

The bridge itself creates a new atomicity question for a **multi-target promotion**. If one logical transition must make A and B live together, sequentially advancing shard A then shard B can leave a partial prepared state, and GC may race between those bridges. This leaf does not claim atomic cross-shard promotion.

Complete repository rollback that removes every shard/root transition witness also remains unresolved.

## Zero-dependency / zero-quota assessment

Incremental monetary cost is `0`. The candidate uses scheduled Chat plus lightweight role-local repository ref/tree/path/readback transport only. It adds no hosted runner, cloud/API credits, package/artifact/LFS storage, external coordinator, richer-mode arbitration, protected-primary execution, or manual-user step. Rate-limit interruption fails closed at the affected shard.

Global Phase-1 closure is **not** claimed.

## Exact continuation

Next leaf: **cross-shard promotion atomicity**. Use shards A/B and one logical promotion intent. Compare sequential A→B bridge then global publish, global publish before bridges (negative), durable `PREPARED` intent + both shard epoch transitions + final `COMMITTED` root, one global-ref fallback, and fail-closed. Adversaries: crash between shard bridges, GC between bridges, response loss, stale coordinator takeover, one shard rate-limited, overlapping promotion, and abort/cleanup. Measure partial authoritative promotion, live-root deletion by GC, orphan prepared states, duplicate promotion, false blockage, and recovery reads.
