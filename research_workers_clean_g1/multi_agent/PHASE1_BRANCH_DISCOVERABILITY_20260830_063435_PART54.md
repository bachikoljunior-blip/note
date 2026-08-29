# Phase-1 multi_agent checkpoint — branch discoverability without a second mutable index hotspot (Part 54)

## Frozen semantic tuple

- root: control revision `26`, blob `481660fb6008a57cea162da38439cf115c8d7ebe`
- role config: config revision `8`, blob `f6bade5e0f774a0623e615b1fc5f924475732d5c`
- transport: SHA-only exact-SHA, frozen main commit `9fc9d9bc6f31216fcead7ef4d365b02264796f9b`
- predecessor: `PHASE1_OVERLAPPING_LATEST_CAS_20260830_063435_PART53.md`

Executable fixture: `research_workers_clean_g1/multi_agent/phase1_branch_discoverability_20260830_063435_part54.py`  
Result: `research_workers_clean_g1/multi_agent/phase1_branch_discoverability_20260830_063435_part54.json`

## Public transport observations

GitHub documents two different repository discovery surfaces with materially different completeness boundaries:

- Repository Contents directory listing is capped at `1,000` files for a directory; for more, GitHub directs callers to the Git Trees API: https://docs.github.com/en/rest/repos/contents
- Recursive Git Trees responses explicitly expose `truncated=true` and are limited to `100,000` entries / `7 MB`; when truncated, GitHub instructs callers to fetch non-recursive subtrees one at a time: https://docs.github.com/en/rest/git/trees
- Git Trees can be fetched by tree SHA or ref, so discovery can be performed against a stable repository snapshot and followed by a separate current-authority revalidation before selecting a branch.

The connected GitHub surface also successfully listed the current role-local namespace in this invocation, so repository-path discovery is exposed as a Chat-accessible transport capability. This is only a capability probe; the model below does not assume the current namespace is small forever.

## Finite model

The fixture enumerates `576` equal-weight scenario shapes and `2,880` strategy evaluations. Branch count is `2`, `8`, or `32`; axes include mutable-root retry, index/manifest response loss, listing completeness (`complete`, `truncated_recovered`, `interrupted`), an immutable checkpoint whose index/manifest write is missing, duplicate manifest creation, authority change during discovery, and an old pending branch.

Compared strategies:

1. one mutable shared branch-index root using set membership and current-blob retry;
2. immutable checkpoint-path discovery by a pinned repository tree plus fail-closed completeness handling;
3. sharded immutable per-attempt manifests plus fenced selector;
4. a parent-linked immutable checkpoint DAG reachable only from current `LATEST`;
5. pending branches referenced by immutable receipts plus current `LATEST`.

All strong selector variants revalidate current authority before selection. Manifest/receipt variants dedupe by checkpoint identity, not by manifest identity. Counts are mechanism-lattice counts, not production rates.

## Results

- `checkpoint_tree_enumeration`: `0/576` false-omission scenarios, `0` shared mutable hotspot writes, `0` duplicate/stale selections. It has `192/576` incomplete-discovery scenarios only when the modeled tree walk is interrupted, and it fails closed in those cases; total fail-closed scenarios are `384/576` after also including authority change.
- `mutable_index_root`: underlying discoverability is incomplete in `432/576`; when authority is otherwise current it falsely proceeds with omissions in `216/576`. Average synthetic shared-root write attempts are `19.75`, maximum `63`; average recovery reads `7.75`, maximum `33`.
- `sharded_manifests`: no mutable root hotspot, but an immutable checkpoint whose manifest was never durably created produces false omission in `96/576` authority-stable/complete-discovery scenarios.
- `pending_receipts`: same omission class as manifests (`96/576`) when a branch exists but its referencing receipt was never durably created.
- `latest_parent_dag`: every modeled `n>1` scenario has undiscoverable sibling branches; with current authority it falsely omits in `288/576`.

Critical slices:

- In the authority-stable orphan-index/manifest slice (`96` scenarios), pinned checkpoint-tree enumeration has `0/96` false omission. Mutable root, sharded manifests, parent DAG, and pending receipts each falsely omit in `96/96` because each requires a separate registration edge that can fail after checkpoint creation.
- In the authority-stable listing-interrupted slice (`96` scenarios), tree enumeration, sharded manifests, and receipt discovery all fail closed (`96/96`) rather than claim completeness. Parent-DAG discovery falsely omits `96/96`; mutable index root falsely omits `72/96` because its problem is registration contention/orphaning rather than listing completeness.
- With `32` branches and root retry enabled under current authority, the mutable-index-root strategy averages `62` shared-root write attempts and `32` recovery reads. Pinned tree enumeration has zero shared mutable writes and no false omission; its modeled recovery-read average stays `3.333`, with `16/48` interrupted walks failing closed.

## Required ablations

The strong results depend on three independent guards:

- If current-authority revalidation is removed, an old pending branch can be stale-selected in `144` root/DAG lattice scenarios, or `96` listing-based scenarios where discovery itself completes.
- If duplicate manifests/receipts are deduped by manifest identity rather than checkpoint identity, duplicate selection appears in `96` authority-stable, discovery-complete scenarios.
- If a mutable root is represented as append-list state and an ambiguous successful write is blindly retried rather than exact-read/reconciled by checkpoint identity, duplicate root membership appears in `72` modeled response-loss + retry scenarios.
- If a Contents directory first page is treated as an unbounded completeness proof rather than using a tree completeness protocol, the `truncated_recovered` slice would become a false-omission class (`96` authority-stable scenarios in this lattice). The model's safe tree candidate instead uses the Git Trees completeness signal and subtree fallback.

## Scope-safe conclusion

For role-local overlapping-run discoverability, a separate mutable global branch-index root is not necessary and can recreate the same contention/failure surface as `LATEST`. The strongest tested repository-only pattern is:

1. each run writes its immutable checkpoint directly into a deterministic, role-local checkpoint namespace whose path itself is the existence record;
2. recovery/discovery reads a **pinned Git tree snapshot**, not a moving directory view;
3. if a recursive tree response is truncated, traverse non-recursive subtrees until the selected checkpoint namespace is completely enumerated; if transport/rate-limit interruption prevents completeness, remain nonterminal/fail closed;
4. dedupe discovered records by checkpoint/integration identity;
5. after discovery completes, revalidate current semantic authority and then perform the separate fenced `LATEST` selection from Part 53;
6. receipts/manifests may accelerate discovery but are hints, not the sole existence proof for a checkpoint that already exists.

This separates existence/discoverability from mutable selection and removes the second shared CAS hotspot. It does not make repository-wide traversal free: read amplification and rate-limit interruption remain explicit liveness costs. For a growing namespace, deterministic hashed/hierarchical checkpoint paths are preferable so subtree traversal can remain bounded without relying on the Contents API's 1,000-entry directory cap.

## Zero-dependency / zero-quota assessment

The accepted candidate in this tested scope uses only scheduled Chat plus lightweight repository path/tree/read/CAS transport. Incremental monetary cost is `0`. It adds no hosted runner, external coordinator, protected/manual execution, cloud/API credit, or finite monthly/trial/paid quota dependency. If repository reads are rate-limited, the protocol checkpoints and fails closed; it does not substitute API volume for compute.

## Exact continuation

Next independent Phase-1 leaf: **stable snapshot discovery versus moving-head/ABA discovery**. Compare (a) Contents/path enumeration at moving `main`, (b) recursive Git tree at a pinned head/tree SHA, (c) multi-subtree traversal pinned to one root tree, (d) mixed-ref traversal that refetches `main` between subtrees, and (e) checkpoint-prefix Merkle summary caches. Adversaries: concurrent branch create/delete, same-path delete/recreate, head rewind/ABA, pagination/subtree restart after response loss, authority change after snapshot, and checkpoint GC during traversal. Measure phantom omission/addition, duplicate discovery, snapshot consistency, stale selection, recovery reads and whether a zero-cost repository-only completeness proof survives moving-head races without a second mutable authority root.
