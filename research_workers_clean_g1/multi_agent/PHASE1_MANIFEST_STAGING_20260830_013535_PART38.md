# Phase-1 multi_agent checkpoint — PREPARED manifest + immutable staging (Part 38)

## Frozen semantic tuple

- frozen authority commit: `64cda245ee44957f79a51b738e9bdfa549d151c4`
- root: control revision `26`, blob `481660fb6008a57cea162da38439cf115c8d7ebe`
- role config: config revision `8`, blob `f6bade5e0f774a0623e615b1fc5f924475732d5c`
- transport: `sha_only_exact_sha`
- predecessor: `PHASE1_REWIND_EFFECT_RECON_20260830_013535_PART37.md`

Part 37 showed that global Git-ref publication is safe in the tested no-complete-rewind scope but conflicts on unrelated branch advances. This leaf tests whether a per-conflict-domain manifest can preserve single-object fencing while moving multi-path payloads into immutable staging.

Executable model: `research_workers_clean_g1/multi_agent/phase1_manifest_staging_20260830_part38.py`  
Result: `research_workers_clean_g1/multi_agent/phase1_manifest_staging_20260830_part38.json`

The model has `192` scenario shapes and `1,152` strategy evaluations over disjoint/overlapping tasks, cancel/supersede, unrelated branch advance, success-response loss, a staging GC race, crash before finalization and manifest-aware vs direct fixed-path readers.

## Protocol candidate

The strong candidate is a two-CAS state machine in one conflict-domain manifest:

1. current-blob CAS `IDLE/current -> PREPARED(transition_id, authority_epoch, expected_stage_paths+digests)`;
2. write payloads only to immutable transition-scoped stage paths;
3. verify the expected immutable stage set/digests;
4. current-blob CAS `PREPARED(t,e) -> APPLIED(t,e,stage_set,applied_transition_id)`;
5. consumers dereference only the current `APPLIED` manifest;
6. GC treats any current `PREPARED` or `APPLIED` stage set as live and deletes only unreferenced retired stages under a later safe reclamation rule.

Cancel/takeover changes the same manifest blob/epoch, so a stale finalizer cannot complete the old `PREPARED` transition. A lost success response is reconciled from the manifest transition identity rather than retried blindly.

GitHub's Contents API requires the current blob `sha` for updates and returns `409 Conflict`; this is the repository primitive used for the abstract manifest CAS:
https://docs.github.com/en/rest/repos/contents

## Finite results

### Strong conflict-domain manifest

`prepared_conflict_domain_manifest` produced:

- stale publication: `0/192`;
- partial authoritative visibility: `0/192`;
- broken stage reference: `0/192`;
- overlapping-effect duplicate conflict: `0/192`;
- unrelated-branch extra conflict: `0/192`;
- successful terminal shapes: `32`;
- response-loss reconciliations: `16`;
- expected pending/cancel/crash shapes: `160`.

The manifest strategy therefore removes the branch-wide false-conflict mechanism from Part 37 **within a static conflict-domain mapping** because unrelated commits that do not change the manifest blob do not invalidate its file-SHA CAS.

### Result 1 — staging needs a durable PREPARED root before GC can run safely

`staging_no_prepared_gc_guard` wrote immutable stages before any durable live reference. It produced **16 broken-reference scenarios**: GC can delete a stage that is not yet referenced, after which the final manifest can point at missing data.

The fix is not merely longer retry logic. The transition needs a durable `PREPARED` root (or an equivalent GC exclusion proof) before stage creation. This is the same authority/evidence distinction seen earlier: immutable data can still be safely garbage-collected unless some current authority marks it live.

### Result 2 — task identity is not a conflict-domain identity

`per_task_prepared_manifest` protects staging and response-loss recovery, but two tasks with different task manifests can still overlap one authoritative effect. The finite overlap slice produced **16 duplicate/conflicting authoritative publications**.

Therefore the manifest key must be derived from a stable conflict domain that all overlapping effect sets share. A display name or task ID is insufficient.

### Result 3 — writing fixed canonical paths before the manifest is not an atomic-visibility substitute

`fixed_paths_then_manifest` generated **128 stale-authority scenarios** when cancel/supersede lands after the earlier read and **144 partial-visibility scenarios** when a crash or direct fixed-path read can interleave with the sequential physical writes.

The manifest only provides atomic visibility if readers actually treat the manifest as the authority and ignore unreferenced/staged paths.

### Result 4 — direct fixed-path readers are a separate parity child

The strong manifest strategy has `16` terminal scenarios marked `reader_contract_miss`: the manifest is safely `APPLIED`, but a consumer that insists on reading legacy fixed paths does not automatically see the staged payload.

This is not accepted as solved by inventing a background materializer. Under the Phase-1 rules, any extra richer-mode/manual executor would remain unresolved. Scheduled Chat can materialize later using repository writes, but then direct readers can observe a sequential materialization window unless their read contract is changed or the physical paths are published under a single atomic Git-ref boundary.

So there are currently two accepted repository-local shapes, with different consumer contracts:

- **manifest-aware consumers:** PREPARED + immutable stage + APPLIED manifest CAS avoids unrelated branch-ref conflicts;
- **legacy direct-path consumers:** tree/commit + `update_ref(force=false)` remains the stronger tested atomic-visibility primitive, but has branch-wide unrelated-advance conflicts.

GitHub documents tree creation plus commit/ref publication and non-force ref-update semantics here:
- https://docs.github.com/en/rest/git/trees
- https://docs.github.com/en/rest/git/refs

## Zero-dependency / zero-quota assessment

Within the tested static-conflict-domain, no-complete-rewind scope, the strong manifest mechanism uses only lightweight repository file create/update/read operations. It needs no hosted runner, Codespaces, artifact/LFS/package service, external coordinator, manual/protected execution step, optional monthly/trial/paid quota, or incremental monetary cost. Repository API rate limits remain checkpoint/backoff interruptions rather than compute.

Global Phase-1 closure is not claimed. Remaining relevant children now include:

1. complete same-domain rewind with no surviving admissible monotonic witness;
2. direct fixed-path consumer parity without branch-wide Git-ref serialization;
3. dynamic conflict-domain remapping / effect-set drift while PREPARED transitions exist;
4. PREPARED lease expiry/takeover and safe orphan-stage GC;
5. arbitrary external sink effects without atomic authority validation/idempotent status.

## Exact continuation

Next leaf: **dynamic conflict-domain remapping plus PREPARED takeover/GC**.

Model:

- static vs changing overlap graph/effect-set digest;
- remap/merge/split of conflict-domain manifests while a transition is `PREPARED`;
- takeover to a higher manifest epoch after lease expiry;
- late old finalizer after takeover;
- GC of stages from abandoned PREPARED transitions;
- direct manifest-key reuse vs incarnation-sensitive domain IDs;
- conservative global-domain fallback vs local domain epochs;
- unavailable atomic multi-ref/multi-manifest update as an explicit capability child rather than an accepted handoff.

Measure stale finalization, duplicate overlapping effects, orphan-stage retention, false exclusion and conflict locality. The target is to determine whether local conflict domains can remain safe under remapping without reintroducing a single global topology epoch/hotspot.
