# Phase-1 multi_agent checkpoint — terminal promotion-witness compaction (Part 61)

## Frozen semantic tuple

- root: control revision `26`, blob `481660fb6008a57cea162da38439cf115c8d7ebe`
- role config: config revision `8`, blob `f6bade5e0f774a0623e615b1fc5f924475732d5c`
- transport: SHA-only exact-SHA, frozen main commit `b7d7a2b031311a014bd7f4347218fe4a7cfb569c`
- predecessor: `PHASE1_ABORT_RELEASE_LATE_BRIDGE_20260830_073446_PART60.md`

Executable fixture: `research_workers_clean_g1/multi_agent/phase1_terminal_witness_compaction_20260830_073446_part61.py`  
Result: `research_workers_clean_g1/multi_agent/phase1_terminal_witness_compaction_20260830_073446_part61.json`

## Question

Part 60 required an absorbing terminal promotion witness so very late bridges/releases cannot resurrect an ABORTED promotion after target reuse. Part 61 asks whether one tombstone per promotion is necessary forever or whether those identities can be compressed into a bounded monotonic floor.

The key distinctions are:

- a local reservation epoch can suffer ABA when a target path is delete/recreated;
- a shard floor can be lowered accidentally by split/merge if topology migration does not preserve the maximum retired generation;
- a floor update that is lagged, rate-limited, or response-ambiguous cannot justify deletion of the stronger exact tombstone until current state is proven;
- complete rollback of the whole repository authority domain is still a different problem from application-level compaction.

## Finite model

The fixture enumerates `3,840` equal-weight scenarios and `26,880` strategy evaluations. Axes:

- old action: bridge vs release;
- current slot: free/dead vs occupied by a new live promotion;
- same target incarnation vs recreated local-epoch ABA;
- shard topology: stable / split-inherit / split-reset / merge-max / merge-min;
- current authority vs complete repository-domain rollback;
- floor update applied vs lagged;
- observed vs applied-response-lost floor write;
- floor read available vs rate-limited;
- old writer epoch 1/2;
- terminal history size `H ∈ {1,16,256}`.

Compared strategies:

1. delete all terminal records;
2. retain exact per-promotion tombstone;
3. per-target path-local epoch floor;
4. per-target floor keyed by stable logical identity + incarnation generation, with tombstone retained until floor CAS/readback succeeds;
5. per-shard floor with no topology fence;
6. per-shard floor with split-inherit/merge-max topology fencing and tombstone fallback;
7. fail-closed.

Counts are mechanism-lattice counts, not production probabilities. Retained-state units are synthetic record counts, not bytes or pricing.

## Current-authority scope (`1,920` scenarios)

- `delete_all_terminal`: old-writer acceptance `480`, stale release of new reservation `240`, modeled live-root deletion `240`, retained units `0`.
- `per_promotion_tombstone`: old/stale/live failures `0/0/0`; retained units `174,720` across the history-size lattice, which corresponds to synthetic mean `H=91` exact terminal records per scenario.
- `per_target_floor_path_local`: old-writer acceptance `180`, stale release/live-root deletion `120/120`; one nominal floor record, but unsafe under floor lag and incarnation reset.
- `per_target_floor_stable_incarnation`: old/stale/live failures `0/0/0`; `1,440` compactions remain blocked and keep the exact tombstone because floor update/read proof is unavailable; successful compaction reduces history to one stable target-floor record.
- `per_shard_floor_unfenced`: old-writer acceptance `168`, stale release/live-root deletion `84/84`; one nominal floor record but unsafe when split/merge lowers the floor or update lags.
- `per_shard_floor_topology_fenced`: old/stale/live failures `0/0/0`; `1,632` compactions remain blocked with tombstone retained when topology/floor proof is incomplete; successful compaction reduces history to one shard-floor record.
- `fail_closed`: zero unsafe effects but blocks all compaction/progress in the current-authority slice.

## Critical slices

### Free slot, current floor

For `6` current-authority cases with an old bridge into a free/dead slot, same incarnation, stable topology, current/readable floor, and varying old epoch/history size, deleting all terminal state accepts the old writer `6/6`. Stable target floor, topology-fenced shard floor, and exact tombstone reject `6/6` old bridges. Successful target/shard floor compaction needs one floor record rather than `H` exact promotion tombstones.

### Target reincarnation ABA

For `6` current-authority cases where an old release hits a new-live target after path/incarnation recreation has made the local reservation epoch ABA-equal, delete-all and path-local target floor each perform **6/6 stale releases of the new reservation**, followed by 6/6 modeled live-root deletion by GC. Stable logical target identity + incarnation generation rejects all six; a current topology-fenced shard floor also rejects them.

Thus a reservation epoch that resets with a recreatable path is not a fencing identity. The comparison must include a stable incarnation generation or a dominating floor outside that recreatable path.

### Shard split/merge lowers the floor

For `12` current-authority cases where the old bridge sees split-reset or merge-min topology, an unfenced shard floor accepts the old writer `12/12`. The topology-fenced strategy accepts `0/12`; instead it blocks all 12 compactions and retains the exact tombstone because the topology transition did not preserve the monotonic floor. The stable per-target floor remains safe because its authority does not move with the physical shard mapping.

Safe shard compaction therefore requires split children to inherit at least the parent floor and merges to take at least the **maximum** input floor under the same topology-generation fence.

### Floor update lag

For `12` current-authority old-bridge/free-slot cases where the floor update lags, path-local and unfenced-shard compaction each accept the old writer `12/12` if the exact tombstone is discarded anyway. The stable target and topology-fenced shard strategies accept `0/12`: floor lag keeps compaction blocked and the exact tombstone retained.

An applied-response-lost floor write is likewise read back before deleting the tombstone. Ambiguous or rate-limited floor state is not evidence that compaction succeeded.

## Complete repository rollback boundary

The other `1,920` scenarios explicitly model rollback of the **entire repository authority domain** to a state before the terminal/floor witness. All repository-local tombstone/floor strategies are marked unresolved across this axis. The fixture deliberately allows old authority replay in such states rather than smuggling current-authority guarantees into the rollback claim.

This leaf therefore does **not** solve the inherited indistinguishability boundary where every monotonic repository witness is rewound away. A reject-all policy is safe only by abandoning useful progress; it is not parity closure.

## Scope-safe compaction rules

A compact per-target floor can replace exact terminal tombstones only when:

1. it is keyed by stable logical target identity outside the recreatable path;
2. it carries an incarnation generation and minimum accepted reservation/promotion epoch greater than every retired writer;
3. the floor CAS is current and exact-readback-confirmed before exact tombstones are removed;
4. rate-limit/lag/ambiguous state retains the stronger tombstone rather than guessing.

A per-shard floor can compress more identities only when topology mutation itself preserves the floor monotonically: split children inherit `>= parent_floor`, merge output uses `>= max(input_floors)`, and a topology epoch prevents old writers from using a retired mapping. If that proof is missing, do not compact.

## Zero-dependency / zero-quota assessment

Incremental monetary cost is `0`. These candidates use scheduled Chat plus role-local floor/tombstone CAS/readback only. They add no hosted compute/coordinator, cloud/API credits, artifact/LFS/package storage, richer-mode arbitration, protected-primary execution, or manual-user step. Rate-limit interruption retains the stronger witness/fails closed.

Global Phase-1 closure is **not** claimed.

## Exact continuation

Next leaf: **adaptive shard split/merge with in-flight promotion/abort/GC**. Compare path-hash remap with no topology epoch, split-parent forwarding tombstone, topology `PREPARED→COMMITTED` generation with child floor inheritance, dual-read migration, and fail-closed. Adversaries: old writer to parent after split, child write before topology commit, merge using min instead of max floor, response loss, stale coordinator, one-child rate limit, target reincarnation, and GC. Measure cross-topology stale bridge/release, duplicate reservation, live-root deletion, stranded forwarding state, false blockage, and recovery reads.
