# Phase-1 multi_agent checkpoint — dynamic conflict-domain remap + PREPARED takeover/GC (Part 39)

## Frozen semantic tuple

- frozen authority commit: `64cda245ee44957f79a51b738e9bdfa549d151c4`
- root: control revision `26`, blob `481660fb6008a57cea162da38439cf115c8d7ebe`
- role config: config revision `8`, blob `f6bade5e0f774a0623e615b1fc5f924475732d5c`
- transport: `sha_only_exact_sha`
- predecessor: `PHASE1_MANIFEST_STAGING_20260830_013535_PART38.md`

Part 38 showed that a PREPARED/APPLIED manifest keyed by a stable conflict domain removes unrelated branch-ref conflicts for manifest-aware readers. This leaf tests the two assumptions left open there: whether a conflict domain can change while transitions are in flight, and how an abandoned PREPARED transition can be taken over and garbage-collected without allowing an old finalizer to reappear.

Executable model: `research_workers_clean_g1/multi_agent/phase1_dynamic_domain_takeover_20260830_part39.py`  
Result: `research_workers_clean_g1/multi_agent/phase1_dynamic_domain_takeover_20260830_part39.json`

Counts are finite mechanism counts, not production failure rates.

## A. Dynamic conflict-domain remapping

The remap model has `128` scenario shapes and `768` strategy evaluations. It varies disjoint/overlapping work, no remap vs merge/split/effect-contract drift, whether the remap lands before PREPARED or between PREPARED and finalization, whether a new PREPARED transition races with remap, whether an old PREPARED exists, and unrelated-domain activity.

### Result A1 — a topology/version read in a different authority object is still a TOCTOU check

A local manifest whose conflict-domain mapping becomes stale produced **20 unsafe stale finalizations** and **40 overlapping duplicate/conflict admissions**. Adding a separate topology-epoch read did not improve those counts: the final local-manifest CAS does not compare the separately stored topology epoch, so a remap after that read remains invisible to the final CAS.

This is the same publication-fence distinction seen in earlier parts: a correct read is not an atomic predicate on a later write when the predicate lives in another object.

### Result A2 — drain-then-remap is not closed against a new PREPARED race without an atomic gate

A strategy that scans/drains current PREPARED transitions before changing the mapping, but has no authority operation that atomically prevents new PREPARED transitions, produced **40 unsafe stale / 40 duplicate-overlap** cases when a new transition entered after the drain scan but before remap.

A separate global `FREEZE` bit has the same structural problem if workers read it and then CAS a local manifest: the bit can change between the read and local CAS. To make that gate authoritative, every transition admission/finalization must either touch the same gate object or use a primitive that atomically compares the gate and the touched local manifests.

GitHub's Contents API exposes a current-blob SHA precondition for one file, not a multi-file compare-and-swap transaction:
https://docs.github.com/en/rest/repos/contents

GitHub's public GraphQL API does document `updateRefs`, which can update multiple **Git refs** atomically with `beforeOid` checks. That is a useful public mechanism precedent, but the GitHub connector available to this scheduled Chat role exposes only single-ref `update_ref`, not the `updateRefs` mutation. An unavailable mutation surface is therefore an unresolved capability child, not an accepted handoff under the current Phase-1 rules:
https://docs.github.com/en/graphql/reference/git#mutations

### Result A3 — the tested zero-dependency fallbacks form a locality/safety trade-off

Two strategies were safe in this finite remap model:

- `stable_superset_domain`: never remap the correctness domain; pre-group every possible conflicting effect conservatively. It had unsafe `0`, but **64 false-exclusion** cases for disjoint work.
- `global_root_publication` / global Git-ref publication: make one global authority object/ref the publication fence. Both had unsafe `0`, but **64 unrelated-activity conflicts** and every one of the `128` scenarios touches the global hotspot.

Thus Part 38's local conflict-domain optimization is safe only while the domain membership is stable for the lifetime relevant to in-flight transitions. Dynamic remap cannot be added merely by reading a separate mapping version.

This result does not claim that a global hotspot is mathematically necessary for every database/storage system. It is scoped to the currently exposed repository primitives and the tested separate-file/CAS constructions. A native multi-key transaction could change the result; no accepted such scheduled-Chat repository mutation primitive is currently exposed here.

## B. PREPARED takeover and stage GC

The takeover/GC model independently contains `128` scenario shapes and `768` strategy evaluations over lease expiry, takeover, late old finalizer, requested GC, domain delete/recreate, incarnation-sensitive identity and lost takeover responses.

### Result B1 — expiry is liveness metadata, not a fencing token

With expiry-only takeover and no monotonic epoch, all **16/16** takeover + late-old-finalizer cases allowed the old finalizer to complete. In the 8 relevant cases where GC had already reclaimed its stage, the model also produced **8/8 broken references**.

The safe ordering needs an authority transition first: CAS the manifest to a higher epoch/new transition (or a terminal abandoned state), then treat the old epoch as permanently non-authoritative, and only afterwards reclaim stages that are reachable solely from the old epoch.

### Result B2 — epoch takeover is safe in the incarnation-sensitive slice

For `epoch_takeover_gc_after_commit`, the `64` scenarios with incarnation-sensitive domain identity had **0 stale old finalization and 0 broken references**. Lost takeover responses were reconciled by reading the current transition/epoch identity. Requested old-stage GC occurs only after the higher-epoch takeover is current.

However, if the manifest/domain can be delete-recreated under the same reusable ID and epoch counters reset, the old identity can ABA-match the new object. In the explicit non-incarnation-sensitive recreate + late-old-finalizer slice, the same strategy was **4/4 unsafe**. A deliberately reusable-ID/reset negative control was **8 unsafe** across the wider lattice.

Therefore the fencing tuple is at least `(domain_incarnation, manifest_epoch, transition_id)`, not a bare integer epoch attached to a reusable path/name.

### Result B3 — GC before the fencing transition is current is unsafe

`gc_before_epoch_bump` produced **8/8 broken references and 8/8 stale old finalizations** in the relevant takeover/late-finalizer/GC slice. Keeping abandoned stages forever avoids the deletion race but retains `32` orphan-stage cases in the model and still needs incarnation-sensitive fencing for domain recreation.

The practical repository-local candidate is therefore:

1. immutable domain incarnation ID;
2. current manifest epoch/transition ID;
3. CAS takeover to a higher epoch after the application-level expiry policy says takeover is allowed;
4. readback/reconcile ambiguous takeover responses;
5. only then mark old stages reclaimable;
6. GC must re-check that no current PREPARED/APPLIED manifest references the stage and that the old `(incarnation,epoch,transition)` can no longer finalize.

## Zero-dependency / zero-quota assessment

The PREPARED takeover/GC mechanism is accepted within the tested **stable conflict-domain, no-complete-rewind** scope using only repository current-blob create/update/read operations. It needs no richer-mode/manual/protected step, hosted coordinator, finite monthly/trial/paid quota or incremental monetary cost. Rate limits are checkpoint/backoff interruptions.

Dynamic remapping remains only partially solved. Under the currently exposed primitives, the accepted zero-dependency choices are either:

- keep a stable conservative conflict domain and accept false exclusion; or
- route remapping/publication through a coarser global root/ref and accept contention.

A local remap that requires atomic comparison/update of several independent domain manifests remains an unresolved capability child. Public GitHub `updateRefs` is evidence that atomic multi-ref mutation exists in GitHub generally, but it is not an exposed scheduled-Chat mutation primitive in this role and cannot be counted as the solution.

Other previously open children remain: complete same-domain rewind, direct fixed-path consumer parity without branch-wide publication, and arbitrary external sink authority participation.

## Exact continuation

Next Phase-1 leaf: **contention-aware stable conflict-domain design without dynamic remap**.

Compare zero-cost repository-local ways to choose a stable domain so overlapping work always collides while unrelated work conflicts as little as possible:

- one global domain;
- fixed hash buckets by canonical effect key;
- rendezvous/min-key bucket for multi-effect sets;
- deterministic interval/range partitions;
- one manifest per stable effect-cell plus fail-closed fallback for multi-cell effects;
- immutable staging + single fenced integrator for wide/multi-cell effects.

Negative controls must include overlapping effect sets whose chosen bucket differs, adversarial hot keys, key delete/recreate, effect-set drift after PREPARED, and response-loss retry. Measure collision completeness, false exclusion/hotspot concentration, number of authority objects touched, and whether wide effects silently depend on an unavailable atomic multi-manifest operation.
