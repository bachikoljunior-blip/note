# Phase-1 multi_agent checkpoint — adaptive shard split/merge topology fencing (Part 62)

## Frozen semantic tuple

- root: control revision `26`, blob `481660fb6008a57cea162da38439cf115c8d7ebe`
- role config: config revision `8`, blob `f6bade5e0f774a0623e615b1fc5f924475732d5c`
- transport: SHA-only exact-SHA, frozen main commit `b7d7a2b031311a014bd7f4347218fe4a7cfb569c`
- predecessor: `PHASE1_TERMINAL_WITNESS_COMPACTION_20260830_073446_PART61.md`

Executable fixture: `research_workers_clean_g1/multi_agent/phase1_adaptive_shard_topology_20260830_073446_part62.py`  
Result: `research_workers_clean_g1/multi_agent/phase1_adaptive_shard_topology_20260830_073446_part62.json`

## Question

Part 61 showed that a shard-wide compact floor is safe only when split children inherit at least the parent floor and merges preserve at least the maximum input floor. Part 62 stress-tests the **topology transition itself** while promotion/abort/GC writers can still act.

A hash/path remap is only routing. Safety requires a current topology generation that decides which mapping is authoritative, preserves stale-writer floors, and prevents both old and new maps from being writable at the same time.

## Finite model

The fixture enumerates `1,728` equal-weight scenarios and `8,640` strategy evaluations. Axes:

- topology operation: split/merge;
- fault: none / crash after PREPARE / crash after one new domain;
- concurrent write: none / old mapping / new mapping;
- floor transition: correct vs reset-or-merge-min;
- publication response: observed vs applied-response-lost;
- stale coordinator absent/present;
- rate limit: none / left / right domain;
- same target incarnation vs recreated ABA;
- GC none/target.

Compared strategies:

1. immediate hash/path remap with no topology epoch;
2. install a forwarding tombstone but no complete prepare/commit authority protocol;
3. monotonic topology generation `PREPARED → COMMITTED` with child floor inheritance / merge-max;
4. dual-read migration where both maps remain writable;
5. fail-closed.

Counts are mechanism-lattice counts, not production probabilities.

## Aggregate results

- `hash_remap_no_epoch`: stale old-mapping write `864`, early new-mapping write `576`, duplicate reservation `1,152`, modeled live-root deletion by GC `576`, stale coordinator effect `864`; all 1,728 transitions are treated as committed regardless of partial state.
- `forwarding_tombstone`: stale old-mapping write `96`, early new-mapping write `576`, duplicate reservation `512`, live-root deletion `304`, **orphan/stranded forwarding `1,536`**, false blockage `1,536`; only 192 clean scenarios reach a completed transition.
- `topology_prepared_committed_inherit`: stale/early/duplicate/live-GC/orphan/stale-coordinator effects all `0`; 96 clean scenarios COMMIT, while `1,632` adversarial scenarios remain explicit recoverable PREPARED/nonterminal. New-map false blockage is `544` under those conservative cases.
- `dual_read_migration`: stale old-mapping write `576`, early new-map write `576`, duplicate reservation `1,152`, live-root deletion `720`, stale coordinator effect `864`; dual reads do not make concurrent writes single-authority.
- `fail_closed`: zero unsafe effects but blocks every topology transition.

## Critical slices

### Old writer after a clean topology transition

For `4` clean split/merge cases with an old-mapping writer and GC varying, immediate hash remap accepts stale old-map writes `4/4` and creates duplicate reservations `4/4`; the GC-target half deletes a modeled live root because authority is split across maps. Dual-read migration also accepts old writes and duplicates `4/4` because both maps remain writable.

A clean forwarding tombstone rejects/redirects the old map in this slice, and the topology-generation candidate rejects it by generation mismatch. The latter also carries the floor/topology proof required by Part61.

### Early new-map write while PREPARED crashes

For `4` split/merge cases where topology PREPARE exists, a crash occurs before commit, and a new-map writer arrives, forwarding-only and dual-read migration admit the new-map write `4/4`, creating a duplicate/non-authoritative reservation while the old map is still current. The topology-generation candidate admits `0/4`: new-map writes require current `COMMITTED` generation; the partial transition remains recoverable PREPARED.

### Floor reset / merge-min

For `4` otherwise clean old-writer cases where split resets the floor or merge uses the minimum input floor, forwarding-only commits the topology despite lowering the stale-writer fence; the stale old authority is accepted and the GC-target half can delete a live root. The topology-generation candidate accepts `0` unsafe effects and refuses COMMIT: split child floor must be `>= parent_floor`, merge output `>= max(input_floors)`.

### One new domain rate-limited

For `32` restricted rate-limit cases across operation/write/incarnation/GC dimensions, forwarding-only leaves `32/32` blocked/stranded forwarding state. The topology-generation candidate leaves `32/32` explicit recoverable PREPARED states: the old topology remains authoritative, the incomplete new topology never becomes current, and no stale/duplicate/live-GC effect is accepted.

## Scope-safe topology protocol

1. create deterministic topology transition ID and `G2=PREPARED` while `G1` remains authoritative;
2. provision every new child/merge domain with exact mapping identity and inherited floor (`split child >= parent`, `merge result >= max(inputs)`);
3. new-map writers and GC must prove `G2=COMMITTED`; while PREPARED they cannot treat the new map as authority;
4. old-map writers continue under G1 until COMMIT, then fail a topology-generation compare and optionally follow a forwarding tombstone;
5. publish `G2=COMMITTED` only after all new domains/floors are exact-readback verified and current coordinator/topology epoch still matches;
6. applied-response-lost COMMIT is reconciled by topology transition ID/current generation before retry;
7. a forwarding tombstone is post-COMMIT routing/fencing assistance, not the transaction coordinator itself;
8. target stable identity/incarnation generation from Part61 remains in reservation/floor comparisons across the move.

Persistent rate limits or crashes leave PREPARED recoverable. No partial topology is promoted to authority.

## Boundaries / unresolved children

The next race is topology **abort cleanup**: if G2 PREPARED already provisioned one child, abort must make G2 terminal before cleaning that child, and cleanup must not delete a later reused child reservation or allow late G2 writers to resurrect after ABORTED. This mirrors Part60 but adds generation routing and old G1 writers.

A promotion intent itself can also span a topology transition: a PREPARED promotion created under G1 must be explicitly remapped, aborted, or pinned; silently following G2 risks duplicate reservations. Complete repository rollback remains unresolved.

## Zero-dependency / zero-quota assessment

Incremental monetary cost is `0`. The candidate uses scheduled Chat plus role-local topology intent/generation, shard floor/ref/path CAS and readback only. It introduces no hosted compute/coordinator, cloud/API credits, artifact/LFS/package storage, richer-mode arbitration, protected-primary execution, or manual-user step. Rate-limit interruption remains nonterminal/fail-closed.

Global Phase-1 closure is **not** claimed.

## Exact continuation

Next leaf: **topology PREPARED abort cleanup**. Start G2 PREPARED with one child provisioned and inherited floor. Compare delete-child-then-abort, abort-generation-then-name-only child cleanup, forwarding-only rollback, monotonic topology `ABORTED` + exact child-generation cleanup, and fail-closed. Adversaries: late G2 child write, late G1 parent write, cleanup response loss, child reuse, stale coordinator, rate limit, GC, and concurrent promotion intent. Measure post-abort G2 resurrection, stale cleanup of reused child reservation, duplicate cross-generation reservation, live-root deletion, stranded child state, false blockage, and recovery reads.
