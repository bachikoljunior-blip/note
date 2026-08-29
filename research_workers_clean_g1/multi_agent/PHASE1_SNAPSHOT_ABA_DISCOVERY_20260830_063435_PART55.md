# Phase-1 multi_agent checkpoint — stable snapshot discovery vs moving-head / ABA discovery (Part 55)

## Frozen semantic tuple

- root: control revision `26`, blob `481660fb6008a57cea162da38439cf115c8d7ebe`
- role config: config revision `8`, blob `f6bade5e0f774a0623e615b1fc5f924475732d5c`
- transport: SHA-only exact-SHA, frozen main commit `9fc9d9bc6f31216fcead7ef4d365b02264796f9b`
- predecessor: `PHASE1_BRANCH_DISCOVERABILITY_20260830_063435_PART54.md`

Executable fixture: `research_workers_clean_g1/multi_agent/phase1_snapshot_aba_discovery_20260830_063435_part55.py`  
Result: `research_workers_clean_g1/multi_agent/phase1_snapshot_aba_discovery_20260830_063435_part55.json`

## Public transport observations

GitHub's Git Trees API permits fetching a tree by tree SHA or ref, and its recursive response has an explicit `truncated` signal. The documentation states that recursive tree retrieval is limited to `100,000` entries / `7 MB`; if truncated, callers should fetch the tree non-recursively and then fetch subtrees individually. Source: https://docs.github.com/en/rest/git/trees

The repository Contents API is path/ref oriented and is useful for direct file reads, but repeated directory/path reads against a moving branch are not documented as a transactionally consistent multi-call snapshot. Source: https://docs.github.com/en/rest/repos/contents

This leaf therefore distinguishes a **moving ref name** from a **content-addressed pinned tree identity**. The latter is used as the snapshot root in the strong candidate; semantic authority is still revalidated separately after discovery.

## Finite model

The fixture enumerates `640` equal-weight scenario shapes and `3,200` strategy evaluations. Mutation shapes are none plus create/delete/delete-recreate occurring before discovery, between reads, or after the snapshot. Independent axes include recursive-tree truncation, response-loss restart, semantic-authority change after the snapshot, application-level checkpoint deletion at a newer head, verified-summary lag, and head rewind/ABA.

Compared strategies:

1. repeated Contents/path enumeration against moving `main`;
2. one recursive Git tree pinned to the start snapshot;
3. non-recursive multi-subtree traversal where every child tree is reached from one pinned root tree SHA;
4. mixed-ref subtree traversal that refetches moving `main` between subtrees;
5. a checkpoint-prefix Merkle/summary cache that records its source tree SHA and falls back to the pinned tree whenever that source identity does not match.

The target snapshot is the repository head/tree observed at discovery start. A later branch mutation must not silently alter the discovered checkpoint set of a snapshot-consistent strategy. Strong selector rows always revalidate current semantic authority after discovery and before mutable `LATEST` selection.

## Aggregate results

- `moving_main_contents`: snapshot inconsistency `512/640`; phantom omission `448/640`; phantom addition `256/640`; duplicate discovery `80/640`. After excluding cases that fail closed because authority changed, it still falsely proceeds with omissions in `224/640`, additions in `128/640`, and duplicate selection in `40/640`.
- `mixed_ref_subtrees`: the same inconsistency/phantom counts as moving Contents, with greater modeled read cost (`8.0` average, `9` max).
- `recursive_pinned_tree`: snapshot inconsistency, phantom omission/addition and duplicate discovery are all `0/640`. It fails closed in `480/640`: semantic authority changed, the recursive response was truncated, or both. Truncation is treated as incompleteness, not as a partial success.
- `pinned_multisubtree`: snapshot inconsistency / phantom omission / phantom addition / duplicate discovery all `0/640`; fail-closed `320/640` only when semantic authority changed; modeled reads `5.5` average, `6` max.
- `verified_merkle_summary`: the same zero phantom/duplicate result as pinned traversal in this finite model. A lagging summary is detected by source-tree mismatch and causes fallback instead of becoming authority; fail-closed remains `320/640` from authority changes.

These are mechanism-lattice counts, not production failure probabilities.

## Critical slices

For `96` authority-stable scenarios with a create/delete/delete-recreate between discovery reads, moving `main` is inconsistent in `96/96`, with false omission `80/96`, false addition `64/96` and false duplicate selection `16/96`. Pinned multi-subtree traversal and verified summary have zero inconsistency/phantom/duplicate in that slice. The recursive single-call tree is also snapshot-safe but fails closed in the `48/96` cases where the response is modeled truncated.

For `144` authority-stable rewind/ABA scenarios with a repository mutation, moving/ref-mixed discovery is inconsistent in `144/144`, while pinned multi-subtree and verified summary remain snapshot-consistent. A simple “read head at start, read head again at end, accept if equal” ablation therefore misses `144` ABA-shaped inconsistencies in this lattice: ref equality after a rewind does not prove all intermediate subtree reads came from one snapshot.

For `160` authority-stable recursive-truncation scenarios, recursive single-call traversal fails closed `160/160` with no false phantom; pinned non-recursive subtree traversal restores progress without changing the root snapshot and has zero false phantom/fail-closed in the same slice.

For the `32` authority-stable delete/recreate + response-loss restart scenarios, moving Contents and mixed-ref traversal falsely omit, falsely add and duplicate-discover in `32/32`; pinned multi-subtree and verified summary are `0/32` on all three metrics because restart reuses the same root/subtree identities and dedupes by checkpoint identity.

For `160` authority-stable scenarios where a checkpoint path is deleted only in a newer application head while discovery is in progress, moving/ref-mixed discovery falsely omits `160/160`. The pinned candidates preserve the start-snapshot membership in the model. **Scope caveat:** this proves application-level snapshot semantics only; it does not prove GitHub will retain unreachable historical Git objects indefinitely after all refs are moved away. A fetch failure for an otherwise pinned unreachable object must remain fail-closed rather than being interpreted as absence from the historical snapshot.

## Required ablations

The strong result needs independent guards:

- removing post-discovery semantic-authority revalidation would stale-select `320` pinned multi-subtree scenarios, and `160` non-truncated recursive-tree scenarios, when authority changes after the snapshot;
- treating a lagging Merkle/summary cache as authority without verifying its `source_tree_sha` produces `48` authority-stable before-start mismatch scenarios in this lattice;
- moving-head delete/recreate plus response restart produces `40` duplicate-discovery scenarios under stable authority;
- start/end branch-ref equality alone does not detect the `144` authority-stable ABA-shaped inconsistent traversals above.

Snapshot identity, completeness, checkpoint identity, and semantic authority are therefore separate proof obligations.

## Scope-safe conclusion

The strongest tested repository-only discovery pattern is:

1. resolve a repository snapshot once and pin a root commit/tree identity;
2. enumerate the role-local checkpoint namespace only through that root tree and its child tree SHAs; never switch back to a moving ref halfway through traversal;
3. if recursive retrieval reports truncation, continue with non-recursive child-tree traversal under the same root; if any required subtree cannot be fetched because of interruption/rate limit, remain nonterminal/fail closed;
4. on response loss/restart, resume from the same root/subtree identities and dedupe by checkpoint/integration identity;
5. optional prefix/Merkle summaries must carry the exact source-tree SHA and are acceleration hints only; mismatch or missing summary falls back to pinned-tree discovery;
6. after discovery is complete, revalidate the **current semantic authority** and then perform the separate fenced/idempotent `LATEST` selection from Parts 53–54.

This removes moving-head phantom races without introducing a second mutable global coordination root. It does **not** solve historical-object retention after a force rewind/delete of every ref that kept the pinned object reachable; that is a distinct open child.

## Zero-dependency / zero-quota assessment

The candidate uses scheduled Chat plus lightweight repository ref/tree/path/CAS/readback transport only. Incremental monetary cost is `0`. It adds no hosted runner, external coordinator, protected-primary/manual-user execution, cloud/API credit, or finite monthly/trial/paid quota dependency. Repository rate-limit/object-fetch interruption is handled by checkpointing and fail-closed continuation, not by using repository APIs as compute.

## Exact continuation

Next non-conflicting Phase-1 leaf: **snapshot retention / unreachable-object availability and GC boundary**.

Compare: (a) pinned commit/tree reachable from current role-local `LATEST`; (b) pinned snapshot made unreachable by force rewind/delete-recreate; (c) immutable checkpoint copied/retained in the current reachable role namespace before its historical ancestor can become unreachable; (d) a mutable branch/tag anchor; (e) fail-closed recovery when an expected pinned object cannot be fetched. Adversaries: force rewind, delete/recreate ref, delayed recovery, historical object fetch failure/404, repository rate-limit interruption, application checkpoint GC, same-path reincarnation, and response loss while retaining a snapshot. Measure recoverability, stale resurrection, duplicate retention, mutable-anchor contention and recovery reads. Do not assume an undocumented GitHub unreachable-object retention guarantee, do not require protected branches/rulesets or paid features, and preserve the zero-cost/zero-finite-quota constraint.
