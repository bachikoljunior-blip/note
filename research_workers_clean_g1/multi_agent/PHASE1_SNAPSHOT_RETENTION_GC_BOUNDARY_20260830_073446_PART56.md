# Phase-1 multi_agent checkpoint — snapshot retention / unreachable-object availability / GC boundary (Part 56)

## Frozen semantic tuple

- root: control revision `26`, blob `481660fb6008a57cea162da38439cf115c8d7ebe`
- role config: config revision `8`, blob `f6bade5e0f774a0623e615b1fc5f924475732d5c`
- transport: SHA-only exact-SHA, frozen main commit `b7d7a2b031311a014bd7f4347218fe4a7cfb569c`
- predecessor: `PHASE1_SNAPSHOT_ABA_DISCOVERY_20260830_063435_PART55.md`

The configured pre-semantic liveness witness was attempted twice in `automation_control/receipts/multi_agent/` before the first role-local/public semantic read, but both `create_file` calls were blocked by OpenAI safety checks. No scheduler mutation was attempted. Config8 explicitly makes this witness-write failure nonterminal, so the run continued and the blocker is recorded here in the role-local authorized namespace.

Executable fixture: `research_workers_clean_g1/multi_agent/phase1_snapshot_retention_gc_boundary_20260830_073446_part56.py`  
Result: `research_workers_clean_g1/multi_agent/phase1_snapshot_retention_gc_boundary_20260830_073446_part56.json`

## Public observations

GitHub documents Git refs as names containing commit SHAs and exposes update/delete operations for refs. A branch/tag name can therefore move or disappear; a ref name is not an immutable snapshot identity. Source: https://docs.github.com/en/rest/git/refs

Git defines an unreachable object as one not reachable from a branch, tag, or any other reference. Git's GC documentation permits pruning unreachable objects after an expiration policy. This establishes the generic Git reachability/GC boundary but **does not** establish GitHub.com's server-side retention schedule for unreachable objects. Sources: https://git-scm.com/docs/gitglossary and https://git-scm.com/docs/git-gc

GitHub's Contents API is mutable path/ref transport; create/update and delete operations can conflict. It is suitable for role-local current-reachable retention only with deterministic identity, digest verification, current-SHA/CAS discipline for mutable selection, and read-before-retry on ambiguous writes. Source: https://docs.github.com/en/rest/repos/contents

## Finite model

The fixture enumerates `2,304` equal-weight scenario shapes and `16,128` strategy evaluations. Axes are:

- historical snapshot state: `reachable / unreachable_retained / unreachable_gone`;
- historical fetch transport: `ok / rate_limit`;
- current-reachable retained copy: `none / exact / deleted_gc / wrong_reincarnation`;
- copy read transport: `ok / rate_limit`;
- mutable retention anchor: `expected / moved / deleted_recreated / absent`;
- anchor read transport: `ok / rate_limit`;
- semantic authority: `same / superseded`;
- retention write response: `observed_success / applied_response_lost / not_applied_response_lost`.

Compared strategies are historical-SHA-only fenced recovery, same-path fallback without digest, mutable-anchor-by-name, mutable-anchor with exact expected SHA, deterministic content-addressed current-reachable copy + historical fallback + authority fence, the same copy strategy with the authority fence ablated, and a blind-retry retention negative control.

Counts below are mechanism-lattice counts, not production probabilities.

## Aggregate results

- `historical_sha_fenced`: correct recovery `384/2304`, false wrong-snapshot recovery `0`, stale resurrection `0`, fail-closed `1920`, duplicate retention `0`, average modeled reads `1.3333`.
- `current_path_fallback_no_digest`: correct recovery `480`, **false wrong-snapshot recovery `96`**, stale `0`, fail-closed `1728`, average reads `2.1667`.
- `mutable_anchor_name_fenced`: correct recovery `144`, **false wrong-snapshot recovery `288`**, fail-closed `1872`.
- `mutable_anchor_sha_fenced`: correct recovery `144`, false wrong-snapshot recovery `0`, stale `0`, fail-closed `2160`.
- `copy_digest_fenced`: correct recovery `480`, false wrong-snapshot recovery `0`, stale resurrection `0`, fail-closed `1824`, duplicate retention `0`, average reads `2.2917`.
- `copy_digest_no_authority`: correct recovery `480` but **stale resurrection `480`** when a source remained available after supersession.
- `copy_digest_blind_retry`: same safety/fail-closed counts as the fenced copy for selection, but **duplicate retention `768`** on applied-response-lost scenarios.

## Critical slices

For `96` authority-stable cases where the historical object is gone or its fetch is rate-limited but an exact current-reachable copy is readable, `copy_digest_fenced` recovers `96/96`; historical-SHA-only fails closed `96/96`.

For `96` authority-stable cases where the historical route is unavailable and the same current path has been reincarnated with different content, path fallback without digest performs **96/96 false recoveries**. Digest-bound copy recovery rejects all `96/96` mismatches.

For `288` authority-stable cases where a readable branch/tag anchor has moved or been delete-recreated, name-only anchor recovery produces **288/288 wrong-snapshot recoveries**. Exact expected-SHA validation removes those false recoveries, but at the cost of failing closed when the anchor no longer names the expected snapshot.

For `288` authority-stable cases where both historical and copy routes are rate-limited, the strong copy strategy fails closed `288/288` and performs zero unsafe recovery. Rate limits are therefore a checkpoint/retry boundary, not an authority signal.

For `480` superseded-authority cases where either the exact retained copy or the historical snapshot remained available, removing the post-recovery authority check produces **480/480 stale resurrection**. Snapshot identity and current semantic authority remain separate proof obligations.

For all `768` applied-response-lost retention scenarios, blind retry with a fresh retention identity creates **768/768 duplicate retentions** in the negative control. Deterministic snapshot/digest identity plus read-before-retry has zero duplicate retention in the tested lattice.

## Scope-safe candidate

Before a checkpoint can become unreachable, retain its exact bytes under a deterministic content-addressed path in the **current reachable role-local namespace** and record source snapshot/checkpoint identity plus content digest in the current role-local manifest. On ambiguous create response, read the deterministic path and verify exact digest before retry. On recovery, prefer the verified reachable copy and fall back to the historical SHA only if it is still fetchable. Never substitute a same path or mutable ref name without exact identity. After reconstructing bytes, revalidate current semantic authority before selecting/updating `LATEST`. A rate limit, 404, missing expected copy, digest mismatch, or moved anchor is nonterminal/fail-closed.

This avoids depending on undocumented indefinite retention of unreachable GitHub objects and avoids accepting mutable-name reincarnation. It does **not** prove that an unprotected branch/tag anchor is permanent, and it does not escape complete rollback of the repository authority domain: if both the retained copy and its current manifest are rewound away, the earlier indistinguishability boundary remains unresolved.

## GC boundary

Application GC may delete a retained copy only after the current role-local manifest no longer marks that snapshot/checkpoint identity as a recovery root. Before that transition, missing expected content is a blocker, not permission to substitute same-path content. The next leaf tests that root-transition/deletion race directly.

## Zero-dependency / zero-quota assessment

The candidate uses scheduled Chat plus lightweight role-local repository path/ref/read/CAS/readback transport. Incremental monetary cost is `0`; no hosted runner, external coordinator, protected-primary/manual-user execution, cloud/API credit, artifact/LFS/package storage, or finite monthly/trial/paid quota is added. Repository rate-limit interruption is handled by fail-closed checkpointing rather than by a paid or richer-mode rescue path.

Global Phase-1 closure is **not** claimed.

## Exact continuation

Next non-conflicting leaf: **fenced application GC / retention-root concurrency**. Precommit live recovery roots from current `LATEST` plus required predecessor/open-continuation identities; compare path-age deletion, mark-manifest then sweep, generation/epoch-fenced sweep, and fail-closed no-delete. Adversaries: concurrent `LATEST` advance, stale sweeper takeover, delete response loss, repository rate limit, same-path reincarnation, and main rewind. Measure deletion of live recovery roots, leaked dead copies, duplicate delete attempts, false blockage, and recovery reads. Preserve exact digest/incarnation fencing and zero-cost/zero-finite-quota constraints.
