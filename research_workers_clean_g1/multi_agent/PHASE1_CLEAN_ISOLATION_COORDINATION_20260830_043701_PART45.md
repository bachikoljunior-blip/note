# Phase-1 multi_agent checkpoint — CLEAN-isolation coordination boundary (Part 45)

## Frozen semantic tuple

- frozen authority commit: `302327074272033f246c5d8f555df61004e3802f`
- root: control revision `26`, blob `481660fb6008a57cea162da38439cf115c8d7ebe`
- role config: config revision `8`, blob `f6bade5e0f774a0623e615b1fc5f924475732d5c`
- transport: `sha_only_exact_sha`
- predecessor: `PHASE1_MEMBERSHIP_PHANTOM_20260830_043701_PART44.md`

Part 44 found a safe generic way to bind changing role membership to a wide ticket, but that mechanism requires a cross-role shared semantic object that the current CLEAN config does not authorize. Part 45 therefore removes that object and asks what coordination remains possible when a worker may use only its own clean state, sanitized root/config, public sources, and role-authorized own writes.

Executable model: `research_workers_clean_g1/multi_agent/phase1_clean_isolation_coordination_20260830_part45.py`  
Result: `research_workers_clean_g1/multi_agent/phase1_clean_isolation_coordination_20260830_part45.json`

The finite lattice has `648` scenarios and `4,536` strategy evaluations. It varies effect relation (`same_effect`, non-commutative `conflicting_effects`, `disjoint_effects`), designated-owner state (alive, crashed, slow-then-late), generation advance, role-membership addition, response-loss retry, finite versus unbounded unrelated branch interference, and repository interruption before or after effect application.

## Result 1 — no-shared-state failover exposes a crash-vs-delay indistinguishability boundary

Two worlds are enough to isolate the problem for a non-commutative conflicting effect.

- **Crash world:** designated owner has stopped; backup sees only its own state plus static sanitized control.
- **Slow world:** designated owner is delayed and later resumes; until the backup's takeover point, the backup has the same allowed observations as in the crash world.

A policy that never fails over can preserve exclusivity, but it loses finite progress if the designated owner really crashed. In the model, `static_owner_no_failover` has **144/144** non-commutative owner-crash cases with no finite progress.

A timeout/tick policy that *does* fail over makes progress in the crash world, but it must make the same decision in the observationally identical slow world. `timeout_takeover_no_fence` is **144/144 unsafe** in the corresponding slow-then-late non-commutative slice: duplicate, conflicting or stale authority can exist when the old owner later resumes.

This is deliberately scope-limited. It is a finite-model indistinguishability argument under the stated observation and effect assumptions, not a universal distributed-computing impossibility theorem.

## Result 2 — deterministic effect IDs solve retry identity, not conflicting authority

A durable sink keyed by a stable effect ID is sufficient for retrying the **same** logical effect: `durable_idempotent_effect_id_sink` has no duplicate effect in **216/216** same-effect scenarios, including response-loss retries.

But idempotency by effect ID does not serialize two different effect IDs that modify the same semantic conflict key. When two workers may act on different conflicting effects, the idempotent-only sink is **144/144 conflict-unsafe** in that slice. It also leaves 108 stale-generation cases across the full lattice because an old-generation effect can have a valid but different ID.

Therefore the necessary identity tuple for general conflicting effects is not just `effect_id`; it includes something like:

`conflict_key + current_generation/epoch + effect_id`

and the authority check must occur at effect application, not only in local worker state.

## Result 3 — authoritative sink-side epoch fencing is a complete generic positive control, but not a current Phase-1 route

`conflict_key_epoch_fenced_sink` atomically validates the conflict-key's current epoch/generation and consumes a durable effect ID at application. In the finite model it is **safe and finite-progress in 648/648** scenarios: zero duplicate, zero conflicting effect and zero stale-epoch application.

Apache Kafka provides a concrete public precedent for this *shape*: the broker protocol carries a producer epoch and checks it against the current broker-side epoch, rejecting mismatches. This demonstrates that stale-writer fencing can live at the authoritative sink rather than in the client alone:
- https://kafka.apache.org/40/design/protocol/

Kafka is **not** an accepted Phase-1 dependency here. A broker cluster would be an external hosted coordination/sink dependency, and the frozen root requires operation with optional hosted quotas at zero. The source is mechanism evidence only.

The current CLEAN role also has no authorized arbitrary cross-role sink that atomically validates such epochs. So this positive control identifies the missing capability; it does not close the task.

## Result 4 — strict role-local partitioning is genuinely CLEAN-compatible, but only for disjoint effects

`partitioned_role_local_only` lets every role publish only inside its own role-authorized namespace. This needs no other-worker read and no shared coordination object.

It is safe and finite-progress in **216/216** disjoint-effect scenarios. For the remaining **432/432** same/conflicting-effect scenarios it deliberately fails closed as an unsupported effect class rather than inventing shared authority.

This is a real current-boundary-safe subset: static namespace partition eliminates conflicts by construction. But it is not full parity for cross-role or wide effects, so `phase1_general_acceptance` remains false.

This result narrows the design goal: current CLEAN isolation can safely support coordination-free work exactly where effect rights are already disjoint; the difficult part is transfer/failover or non-commutative sharing of one authority domain.

## Result 5 — branch-ref conflict is storage serialization, not semantic conflict resolution or fairness

GitHub documents that updating a ref with `force=false` requires a fast-forward and can return `409 Conflict`, preventing a stale branch update from overwriting newer work:
- https://docs.github.com/en/rest/git/refs

That is valuable storage-level conflict detection, but `branch_conflict_only` still has 108 duplicate-effect and 108 conflicting-effect cases in the full finite model when semantic retries are allowed. A later retry from a fresh branch base can still apply a *different semantic effect* unless a conflict-key rule exists above the ref.

It also has **216/216 starvation-unproven** cases under the `unbounded` unrelated-commit schedule. Non-force branch publication detects movement; it does not grant a turn.

Thus branch CAS cannot replace either effect-key fencing or a liveness admission mechanism.

## Result 6 — exact minimal unresolved capability under current CLEAN isolation

For non-commutative cross-role effects that require finite failover, every tested route lands in one of four classes:

1. **Static unique owner, no failover:** safe exclusivity can be retained, but owner crash sacrifices finite progress.
2. **Local timeout/takeover without a shared fence:** finite failover is possible, but slow-old-owner execution is unsafe.
3. **Idempotent/commutative effect algebra:** concurrency can be harmless for a restricted effect class; this is the next leaf.
4. **Shared authority at effect time:** a CLEAN-authorized epoch/fence object or authoritative sink rejects stale/conflicting writers; this solves the generic finite model but is not currently exposed as an authorized general cross-role surface.

The unresolved capability is therefore narrower than “need a coordinator.” It is an **authority point observable at effect application for the same conflict domain**, unless the effect can be redesigned so concurrent/repeated application is algebraically harmless.

The frozen CLEAN rules specifically prevent solving this by reading other-worker role-local state or writing the shared aggregate execution ledger. An unavailable shared manifest, external broker or protected/user installation step remains an unresolved child rather than a handoff.

## Zero-dependency / zero-quota assessment

All local finite experiments and persisted artifacts use role-authorized repository transport only. No GitHub Actions, Codespaces, artifact/LFS/package storage, cloud compute, external model/API credit, richer-mode arbitration, protected-primary operation or manual user action is part of the accepted subset. Incremental monetary cost is zero. Repository rate limits are modeled as bounded interruption/recovery, never as authority revocation.

Kafka and GitHub public docs are architectural evidence only; no external service is added to the accepted execution path.

## Exact continuation

Next leaf: **coordination-free algebraic redesign**.

Test whether the unresolved cross-role fence can be eliminated for larger useful subclasses by converting effects into:

- grow-only set / join-semilattice contributions;
- content-addressed immutable contributions;
- monotonic max/version registers where lower values are harmlessly dominated;
- statically escrowed disjoint rights;
- deterministic single-owner effects with no failover;
- a fenced shared sink as the strong comparison baseline.

Required adversaries: duplicate replay, two distinct payloads under the same semantic key, owner crash, late old owner, role add, generation supersession, response loss and repository interruption.

The key additional gate is **final reduction**: a CRDT/immutable contribution is not a Phase-1 solution if producing the useful outcome still requires a reducer to read other-worker state, an external merge service, protected execution or manual user action. The target is the largest effect class whose useful terminal outcome is executable entirely inside current CLEAN boundaries; any required reducer becomes a new explicit unresolved child.
