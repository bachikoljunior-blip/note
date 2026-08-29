# Phase-1 multi_agent checkpoint — overlapping same-role `LATEST.json` CAS (Part 53)

## Frozen semantic tuple

- root: control revision `26`, blob `481660fb6008a57cea162da38439cf115c8d7ebe`
- role config: config revision `8`, blob `f6bade5e0f774a0623e615b1fc5f924475732d5c`
- transport: SHA-only exact-SHA, frozen main commit `9fc9d9bc6f31216fcead7ef4d365b02264796f9b`
- predecessor: `PHASE1_LIFECYCLE_WITNESS_IDENTITY_20260830_0539_PART52.md`
- presemantic liveness witness: `automation_control/receipts/multi_agent/20260830T063435+0900_presemantic_liveness_config8.json`, created and exact-read before the first role-local/public semantic read

Executable fixture: `research_workers_clean_g1/multi_agent/phase1_overlapping_latest_cas_20260830_063435_part53.py`  
Result: `research_workers_clean_g1/multi_agent/phase1_overlapping_latest_cas_20260830_063435_part53.json`

## Public transport observation

GitHub's repository Contents API requires the current blob `sha` when replacing an existing file and documents `409 Conflict` as a possible response. This makes the file blob SHA a useful compare-and-swap fence for **that file**. The same documentation warns that conflicting contents operations must be serialized. Source: https://docs.github.com/en/rest/repos/contents

That primitive does not by itself prove that a separate authority/config epoch is still current. This leaf therefore models `LATEST` CAS and semantic authority as distinct domains.

## Finite model

Two old-authority invocations `R1/R2` start from the same `LATEST` blob `L0` and each create an immutable valid checkpoint (`C1/C2`). The lattice varies:

- checkpoint relation: compatible vs conflicting;
- authority change: none / before winner / between winner and loser / after loser;
- whether a new-authority writer also advances `LATEST`;
- winner CAS response loss and crash-before-readback;
- loser retry after conflict;
- compatible-merge response loss.

There are `168` equal-weight scenario shapes and `840` strategy evaluations. Counts are mechanism-lattice counts, not production rates.

Compared strategies:

1. blind last-writer update;
2. current-blob CAS, loser drops its branch;
3. current-blob CAS, loser preserves merge/pending intent;
4. append-only per-checkpoint branch indexing followed by current-authority-fenced, deterministic/idempotent `LATEST` selection;
5. current-authority-fenced fail-closed CAS with pending receipts on detected conflicts.

Metric definitions are exact in the result JSON. In particular, semantic-result loss means a valid `C1/C2` is neither represented by current `LATEST` nor referenced by durable branch/intent/receipt metadata.

## Results

Across all 168 scenarios per strategy:

- `blind_last_writer`: semantic-result loss in `168/168`, stale-current selection in `128/168` (`264` stale write events), duplicate integration `0`.
- `cas_drop`: semantic-result loss in `168/168`, stale-current selection `24/168`, duplicate integration `0`.
- `cas_preserve_intent`: semantic-result loss `24/168`, stale-current selection `24/168`, duplicate integration `3/168`.
- `append_index_fenced`: semantic-result loss `0/168`, stale-current selection `0/168`, duplicate integration `0/168`.
- `fail_closed_authority`: stale-current selection `0/168`, duplicate integration `0/168`, but semantic-result loss `32/168` because an applied winner can crash after response loss and later be overwritten before any independent branch reference is made durable.

The important slices are:

- When authority changes without changing the `LATEST` blob before an old writer's CAS, `cas_drop` and `cas_preserve_intent` each still stale-select in `24/48`; the blob SHA only fences `LATEST`, not the separate authority epoch. `append_index_fenced` and `fail_closed_authority` are `0/48` stale because they explicitly revalidate authority.
- When `R1` successfully becomes current, then a new-authority writer overwrites it before `R2` observes the conflict, `cas_preserve_intent` loses `C1` in `24/24`: the loser can preserve itself and current `N`, but cannot discover the already-overwritten old winner. Pre-indexing both immutable checkpoint identities avoids this loss (`append_index_fenced`: `0/24`).
- In the compatible/no-authority-change slice with ambiguous merge response plus retry, naive `cas_preserve_intent` duplicates `C2` in `3/3`; deterministic applied-merge identity/membership readback keeps `append_index_fenced` at `0/3`.
- In the winner-response-loss + crash + later new-authority overwrite slice, authority-fenced fail-closed CAS still loses discoverability in `8/8`; branch indexing before mutable selection remains necessary for durable result preservation.

## Scope-safe conclusion

A single mutable `LATEST.json` should be treated as a **selection pointer, not the only existence/discoverability record for role results**. For overlapping same-role runs, the strongest tested repository-only pattern is:

1. write the immutable checkpoint;
2. durably register/index that checkpoint with a unique immutable identity before attempting mutable selection;
3. revalidate the current semantic authority domain immediately before selecting;
4. update `LATEST` with current-blob CAS;
5. on ambiguous success, exact-read current state and reconcile by deterministic checkpoint/integration identity instead of blindly replaying;
6. on CAS conflict, never refresh the SHA and overwrite blindly; retain the indexed branch as pending and let a later fenced selector merge compatible branches or choose among conflicts.

This result is finite-model evidence only. It does not claim the repository Contents API provides a cross-file transaction between authority and `LATEST`; the tested safe candidate explicitly treats that as a separate fence.

## Zero-dependency / zero-quota assessment

The candidate uses scheduled Chat plus lightweight repository transport/readback only. Incremental monetary cost is `0`. It adds no hosted runner, external coordinator, cloud/API credit dependency, protected-primary execution, manual user step, or finite monthly/trial/paid quota dependency. Repository API rate limits remain a transport interruption condition: on interruption, preserve immutable checkpoints and fail closed rather than use API volume as compute.

## Exact continuation

Next non-conflicting Phase-1 leaf: **append-only branch discoverability without creating a second mutable global index hotspot**.

Compare (a) one mutable branch-index root, (b) deterministic directory/path enumeration by checkpoint prefix, (c) sharded append-only per-attempt manifests plus a fenced selector, (d) parent-linked immutable checkpoint DAG scanned from `LATEST`, and (e) receipt-referenced pending branches. Adversaries: index-root CAS contention, listing pagination/rate-limit interruption, orphan checkpoint with no index write, branch-index response loss, duplicate manifest creation, authority change during discovery, and old pending branch after config change. Measure branch discoverability, false omission, duplicate selection, mutable-hotspot writes, recovery reads and fail-closed behavior. Preserve the current finding that no failed `LATEST` CAS authorizes overwriting another own-state advance.
