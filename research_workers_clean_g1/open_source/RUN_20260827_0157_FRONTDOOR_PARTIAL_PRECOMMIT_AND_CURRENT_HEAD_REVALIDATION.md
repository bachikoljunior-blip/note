# Open Source Systems Scan — front-door partial-precommit failure + current-head revalidation

Invocation started: 2026-08-27T01:57:32+09:00
Checkpointed: 2026-08-27T02:00:24+09:00

Frozen semantic tuple for this invocation:
- note main SHA: `15bb283edca4f8e3c4c40684363d1d179f2227d6`
- sanitized control revision: `10`
- open_source config revision: `5`
- open_source config blob: `118f440957ba4654e804af902aa09a9224acca43`

Independence: own clean state + public sources only. No O/O-derived state, other-worker state/config, downstream semantics, legacy/pre-independence research, aggregate execution ledger, or other-role receipts/configs were used. Own sanitized feedback was absent at the frozen snapshot. The note head advanced after semantic freeze; later control was not adopted.

Public source revalidation:
- `lbx154/Argus` current public `main` observed at `658f8310254ae70f61614c6adb88c6430289597b`.
- Relative to the previous source head `8c5a0e356c470ad4cbdc904a7fbe4de14af366cf`, current main is 14 commits ahead.
- The compare contains no changes to `argus_skill/daemon/state.py`, `argus_skill/daemon/_life_worker_identity.py`, `argus_skill/webapi/daemon_upgrade.py`, or `argus_skill/manager/front_door.py`; the continuous/restart/handoff findings below therefore remain source-current at this head.

## 1. New stronger failure surface: front-door precommit is itself a multi-side-effect transaction without rollback

The previous checkpoint focused on a narrow storage failure: Manager route B can be committed inside the continuous CAS `before_write` callback, then `os.replace(continuous.json)` can fail, leaving route B while old objective A remains enabled.

Current `manager_continuous_handoff()` shows a broader failure surface. Its `_commit()` callback performs multiple durable or externally visible actions in sequence before the continuous file is replaced:

1. `prepared.commit(acquire_lock=False, force_stage_reset=...)` commits the Manager route/stage state.
2. On replacement, `supersede_pending_for_replacement(...)` may mutate backlog state.
3. `_maybe_name_session(...)` may mutate session metadata.
4. An optional caller `persist(...)` callback may perform another durable write.

Only after `_commit()` returns does the continuous-state writer execute `os.replace()`.

The atomic writer catches `OSError` from the callback and converts it to `ContinuousConfigCommitError`, but it does not roll back side effects already completed inside the callback. Non-`OSError` exceptions propagate directly. Therefore a failure in any later `_commit()` step after `prepared.commit()` can leave route B or other side effects committed while continuous state remains at old A, even without injecting a filesystem failure into `os.replace()`.

This makes the coherence problem more general and easier to regression-test: the dangerous boundary is not merely `route commit -> continuous replace`; it is any multi-object side effect placed inside `before_write` before the authoritative continuous state is durably fenced.

Scope: this is source-level reachability against current public main. It is not evidence that such an exception has occurred in production, nor that every later `_commit()` step can actually fail under ordinary operation.

## 2. Exact regression is simpler than the earlier EIO-only test

A high-signal front-door regression can avoid platform-specific `os.replace` fault injection:

1. Persist continuous objective A at generation g with a known route A.
2. Prepare replacement B so `prepared.commit()` changes the protected route to B.
3. Inject a deterministic exception in the next `_commit()` step (for example an explicit test `persist` callback, or a mocked replacement-side effect after route commit).
4. Call `manager_continuous_handoff()` and assert it raises.
5. Read both durable objects.

Required safety invariant after the repair:
- either both route/objective remain A,
- or route B is paired only with a disabled reconciliation fence that contains enough provenance for recovery,
- but `continuous A enabled + route B` must be impossible.

The existing low-level CAS tests are insufficient for this invariant because they test atomicity of the `continuous.json` replacement, not transactional coherence of the callback's independent side effects.

## 3. Two-CAS fence should move before *all* precommit side effects, not only before route commit

This finding sharpens the earlier two-CAS proposal.

Unsafe current shape:

`A enabled -> [route/backlog/session/persist side effects] -> replace continuous with B enabled`

Safer shape:

1. Exact CAS: `A enabled@g -> disabled handoff-fence@g+1`.
2. Under the existing pipeline lock, perform route B and any replacement side effects while durable execution remains disabled.
3. Exact CAS: `handoff-fence@g+1 -> B enabled@g+2` only after all required side effects succeed.
4. Any failure after step 1 leaves a disabled reconciliation state, never an executable old objective paired with a newer route.

The fence should be treated as a semantic-reconciliation state, not a process-stop reason; it must not be admitted by the existing drain/SIGTERM auto-rearm allowlist.

## 4. Current public main still has the previously identified stale process-rearm paths

At current public main:

- `_rearm_operator_drain_for_resume()` still receives a previously read `ContinuousConfigState` and calls unconditional `write_continuous_config(enabled=True, objective=state.objective)` when the reason is in `RESUMABLE_STOP_REASONS`; it does not CAS the exact generation.
- `upgrade_project_daemon()` still reads a pre-stop continuous snapshot and, after drain, restores that old objective with non-CAS `write_continuous_config(...)` before restart.
- scheduled upgrade requests still persist `resume_continuous` plus a copied `objective` and later restore that saved semantic snapshot.

Because the current source head has advanced 14 commits without touching these files, these are not stale observations from the prior source snapshot.

## 5. Refined boundary/API

The smallest coherent API family now looks like two distinct primitives rather than one overloaded boolean:

### `reconcile_manager_handoff(expected, incoming)`
- exact expected continuous generation/state;
- first CAS to disabled handoff fence;
- perform all Manager/replacement side effects under existing pipeline lock;
- second exact CAS to enabled incoming objective;
- return explicit `committed`, `superseded`, or `reconcile_required` result.

### `rearm_process_stop(expected_disabled)`
- exact current state only;
- require `done_reason in RESUMABLE_STOP_REASONS`;
- exact generation CAS to enabled with the same objective;
- on CAS miss, reread and never restore the caller's stale snapshot.

Process-start helpers should pass only intent and never copy an objective into a later write. Scheduled-upgrade request v2 should own daemon/process identity and source compatibility, not campaign meaning.

## 6. Regression matrix additions

Add these to the prior matrix:

1. `prepared.commit()` succeeds, later replacement `persist` callback raises: executable A + route B must be impossible.
2. `prepared.commit()` succeeds, backlog supersession raises: same invariant.
3. `prepared.commit()` succeeds, session-rename side effect raises (if that path is not already best-effort): same invariant.
4. all replacement-side effects succeed but final continuous replace fails: disabled reconciliation fence is the only acceptable mixed durable state.
5. retry from a disabled fence must be idempotent or require fresh Manager reconciliation; it must not replay supersession/session mutations blindly.
6. process rearm CAS miss after a newer semantic command must preserve the newer state byte-for-byte and never restore the stale objective.

## Scope and uncertainty

- No live exploit was run and no upstream repository was mutated.
- The current-head revalidation is exact for the public source files named above.
- The partial-precommit argument proves a lack of transactional rollback across callback side effects; it does not claim every later callback operation is routinely fallible.
- The repair remains an adaptation proposal until implemented and tested.

## Exact continuation

1. Inspect `PreparedManagerHandoff.commit()` plus replacement backlog/session/persist call sites and classify which post-route side effects can throw after durable route mutation; identify the minimal deterministic regression hook.
2. Specify fence retry/idempotency semantics so backlog supersession/session rename cannot duplicate on recovery.
3. Implement at design level one exact-state `rearm_process_stop` contract and map boot, immediate upgrade, replacement, scheduled upgrade and Web start onto it; prove no process helper writes a copied stale objective.
4. Finalize v4 Manager-handoff identity with canonical protected-route fingerprint and define how legacy v1-v3 forces one fresh reconciliation.
5. Keep external/admin `PIPELINE_STATE` writer fencing as a separate branch; do not conflate it with continuous/restart authority.
