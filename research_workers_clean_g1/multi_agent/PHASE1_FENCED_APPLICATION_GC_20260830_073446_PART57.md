# Phase-1 multi_agent checkpoint — fenced application GC / retention-root concurrency (Part 57)

## Frozen semantic tuple

- root: control revision `26`, blob `481660fb6008a57cea162da38439cf115c8d7ebe`
- role config: config revision `8`, blob `f6bade5e0f774a0623e615b1fc5f924475732d5c`
- transport: SHA-only exact-SHA, frozen main commit `b7d7a2b031311a014bd7f4347218fe4a7cfb569c`
- predecessor: `PHASE1_SNAPSHOT_RETENTION_GC_BOUNDARY_20260830_073446_PART56.md`

Executable fixture: `research_workers_clean_g1/multi_agent/phase1_fenced_application_gc_20260830_073446_part57.py`  
Result: `research_workers_clean_g1/multi_agent/phase1_fenced_application_gc_20260830_073446_part57.json`

## Public / Chat-exposed primitive audit

GitHub's Git Trees API can create one tree containing multiple path changes relative to a base tree, after which the tree is committed and a branch ref is updated. Source: https://docs.github.com/en/rest/git/trees

GitHub's Git Commits API creates a commit from a tree SHA and explicit parent commit SHA. Source: https://docs.github.com/en/rest/git/commits

GitHub's Git Refs API documents `force=false` update as requiring a fast-forward update and returning conflicts on invalid competing publication. Source: https://docs.github.com/en/rest/git/refs

The current Chat GitHub connector exposes `create_tree`, `create_commit`, and `update_ref(force=false)`. Therefore this candidate primitive is Chat-exposed rather than a residual manual/richer-mode executor. No destructive GC was executed against primary/protected state; the positive claim is a finite mechanism model plus public primitive/capability audit.

## Finite model

The fixture enumerates `384` equal-weight scenario shapes and `1,920` strategy evaluations. Axes are:

- whether the target was marked dead;
- current recovery-root membership at the final snapshot (`dead/live`);
- a post-check root flip that makes the target live;
- target path unchanged vs same-path reincarnation;
- current vs stale sweeper epoch;
- branch head unchanged vs advanced before publication;
- observed success vs applied-response-lost vs not-applied-response-lost;
- repository transport available vs rate-limited.

Positive scope is deliberately narrow: the complete recovery-root set, GC/sweeper epoch, and target incarnation must be represented in the **same repository ref/tree authority domain**. Recovery roots outside that domain and complete repository rollback remain unresolved.

Compared strategies:

1. age-only delete;
2. mark/sweep with no final fence;
3. root/epoch recheck followed by Contents delete with target current-SHA precondition;
4. one tree/commit that removes the exact target and advances the GC/root manifest, published through `update_ref(force=false)` from the pinned parent;
5. never delete / fail closed.

## Aggregate results

- `age_only`: deleted live recovery root `144/384`; deleted wrong reincarnation `24`; dead copy deleted `24`; duplicate delete attempt `64`; fail-closed `192`.
- `mark_sweep_unfenced`: deleted live root `72`; wrong incarnation `12`; dead copy deleted `12`; leaked dead copy `36`; duplicate delete attempt `32`; fail-closed `96`.
- `recheck_then_contents_delete_sha`: deleted live root **`6`**; wrong incarnation `0`; dead copy deleted `6`; leaked dead copy `42`; duplicate delete attempt `4`; fail-closed `372`; false blockage `18`.
- `single_ref_commit_fenced`: deleted live root `0`; wrong incarnation `0`; dead copy deleted `3`; leaked dead copy `45`; duplicate delete attempt `0`; fail-closed `381`; false blockage `21`.
- `no_delete_fail_closed`: deleted live/wrong `0`; deleted dead copy `0`; leaked dead copy `48`; fail-closed/false blockage `384/48`.

These are mechanism-lattice counts, not production failure probabilities.

## Critical slices

### Root changes after the final recheck

There are `6` cases where the sweeper has a valid dead mark, the final check sees the target unrooted/current-epoch/same-incarnation, and then the target becomes a live recovery root before deletion. A per-file Contents delete still has the target's unchanged blob SHA and therefore deletes the now-live root in **6/6** modeled cases. The single-ref commit strategy deletes `0/6`: the root-set change advances the same ref domain, so the old-parent proposal no longer publishes as the accepted current state and must be recomputed/fail closed.

This is the key result: **target-SHA CAS fences the target file incarnation, not the recovery-root predicate.** If root membership can change in another file between check and delete, the per-file delete has a TOCTOU gap.

### Same-path reincarnation

For `6` dead-root/current-epoch cases where the target path is delete/recreated before the effect, age-only and unfenced mark/sweep delete the wrong incarnation `6/6`. The recheck+Contents strategy and single-ref strategy both have `0/6` wrong-incarnation deletions because the target SHA / pinned tree no longer matches.

### Unrelated branch-head churn

For `3` cases where the target remains dead, same-incarnation and current-epoch but an unrelated head update occurs, recheck+Contents delete safely removes the dead copy `3/3`. The single-ref strategy fails closed `3/3`, leaving three temporary leaks/false blockages until it rebuilds from the newer head. This is the safety/liveness trade-off of using the whole ref as the atomic predicate domain.

### Applied response loss

On the single all-guards-pass response-loss case, recheck+Contents performs the correct deletion but the blind retry policy causes one duplicate delete attempt. The single-ref candidate uses a durable `applied_transition_id` in the manifest/tree and ref/tree readback before retry, yielding correct deletion and zero duplicate delete attempts in this slice.

## Scope-safe candidate

For **repository-local retained checkpoints whose complete recovery-root membership lives in the same ref/tree domain**, GC should not be `recheck roots -> delete one file`.

Instead:

1. resolve and pin the current branch commit/tree;
2. derive the complete live-root set and current GC/sweeper epoch from that pinned snapshot;
3. if a retained copy is dead, construct one new tree that both deletes the exact target blob/path and advances the GC/root manifest with an `applied_transition_id`;
4. create a commit whose parent is the pinned commit;
5. publish only with `update_ref(force=false)`;
6. on ref conflict, target reincarnation, rate limit, or any head/root change, do not delete; rebuild from the new head;
7. on ambiguous ref-update response, read current ref/tree and the durable transition ID before retry.

This co-locates the deletion effect and the predicate that authorizes it at one publication boundary. A per-file SHA check remains useful for incarnation safety, but is not enough for root-membership safety when the predicate is stored elsewhere.

## Boundaries / nonclaims

- The positive claim does **not** cover recovery-root predicates stored outside the same ref/tree authority domain.
- It does not solve complete repository rollback/restore that erases every current manifest and transition witness.
- No protected branch/ruleset, hosted runner, external coordinator, manual user step, or paid/quota-bearing service is required by the mechanism.
- The destructive primitive itself was not applied to primary/protected state in this CLEAN run.

## Zero-dependency / zero-quota assessment

Incremental monetary cost is `0`. The candidate uses scheduled Chat plus lightweight GitHub repository tree/commit/ref/readback transport exposed in this Chat connector. It adds no hosted compute, cloud/API credit, artifact/LFS/package storage, finite monthly/trial/paid quota, richer-mode arbitration, protected-primary execution, or manual-user execution step. Repository rate-limit interruption is fail-closed and retried from a checkpoint.

Global Phase-1 closure is **not** claimed.

## Exact continuation

Next non-conflicting leaf: **batched/sharded GC publication vs hotspot pressure**. Compare one global retention-root commit, prefix-sharded manifests with shard-local atomic deletion publication, deterministic batch IDs, and no-delete fallback. Adversaries: two sweepers select overlapping dead sets, concurrent `LATEST`/root promotion across shards, one shard rate-limited, batch response loss, target reincarnation, and unrelated head churn. Measure live-root deletion, duplicate batch/delete effects, dead-copy leakage, false conflict/hotspot pressure, and recovery reads. Positive claims require each target's root-membership predicate and deletion publication to share one atomic authority domain; otherwise retain/fail closed.
