# Open Source Systems Scan — Manager handoff precommit split-brain on continuous replace failure

Role `open_source`; frozen note control remains main `31face47d7ee4b9b686ee3ae55fb9dbdeb877284`, control revision 10, role config revision 5, role blob `118f440957ba4654e804af902aa09a9224acca43`. Public source: `lbx154/Argus@8c5a0e356c470ad4cbdc904a7fbe4de14af366cf`.

## New source-level failure mode

The current Manager continuous-handoff transaction has a fail-open cross-file ordering gap under an I/O failure **after the route precommit but before `continuous.json` replacement**.

Current flow in `manager/front_door.py`:

1. read current continuous snapshot `expected` (campaign/objective A);
2. prepare Manager decision B;
3. request daemon pipeline yield;
4. acquire Manager pipeline lock;
5. call `compare_and_swap_continuous_config(... expected=expected, objective=B, before_write=_commit)`;
6. `_commit` calls `prepared.commit()`, which commits the Manager vertical/workflow/venue/stage route state B;
7. the continuous writer then replaces `continuous.json` with B;
8. pipeline yield is cleared in `finally` even on failure.

`daemon/state.py` deliberately executes `before_write` immediately before the atomic target replace. Its regression test `test_replace_failure_after_callback_surfaces_instead_of_false` proves the exact failure semantics: if the callback successfully commits external state and the following `os.replace(continuous.json)` fails, `ContinuousConfigCommitError` is raised, the callback side effect remains committed, and `continuous.json` remains the old expected state.

Manager route commit has its own `_restore_files_on_error` around errors *inside* `commit_vertical_decision`, but that context has completed successfully before the later continuous replace fails. `PreparedManagerHandoff.failed()` only records a failed intent; it does not restore the committed route. Finally, the manager pipeline-yield token is cleared.

Therefore the source admits this sequence without concurrency:

- continuous state remains enabled for objective A;
- Manager protected route/pipeline state has already changed to B;
- handoff returns an error;
- daemon pipeline yield is removed;
- the existing daemon can continue A while resolving the newly committed B route/state.

This is a **cross-file split-brain caused by post-precommit I/O failure**, distinct from the earlier race/resurrection findings. No live fault injection or repository mutation was performed.

## Why existing CAS does not solve this by itself

The continuous CAS is correct about its own file. It cannot roll back arbitrary state committed by `before_write`. The state tests intentionally surface this as `ContinuousConfigCommitError` rather than falsely reporting CAS failure, but the caller currently lacks a compensating or fail-closed protocol.

Reversing the order alone is not safe either: writing continuous B first and then failing route commit would run B under route A.

## Minimal fail-closed transaction candidate

A safer file-based protocol can reuse existing primitives without pretending to make multiple files atomically replaceable:

1. while holding the Manager pipeline lock and pipeline yield, CAS continuous A to a **disabled handoff-fence state** bound to A's exact generation/objective (e.g. reason `manager handoff transition pending`); this first durable step prevents A from running under any later route change;
2. commit route/pipeline state B with the existing internal rollback guard;
3. re-read/validate route B and CAS the exact disabled handoff-fence generation to enabled objective B;
4. only after step 3 succeeds publish the new handoff identity and clear the yield;
5. if route commit fails, either compensate the fence back to A using exact CAS or leave A disabled and surface recovery; never resume unknown mixed state;
6. if final enable CAS loses to a newer semantic command, keep the newer command authoritative and do not force-enable B; route reconciliation can occur through the normal Manager boundary.

This is a fail-closed mini-transaction rather than cross-file atomicity. A crash at each boundary leaves either old A+old route, or a disabled fenced state, or coherent B+B — never intentionally leaves an enabled old objective with a new route.

The handoff-fence reason must **not** be in `RESUMABLE_STOP_REASONS`, so raw process restart cannot release an incomplete semantic transaction.

## Required crash/fault tests

- failure before first fence replace -> A/A remains unchanged;
- crash after fence lands but before route commit -> A is disabled; route remains A; no automatic process resume;
- route commit raises -> route rollback guard restores A; fence remains disabled or is exact-CAS compensated;
- route B commits, final continuous enable replace fails -> route B + disabled handoff fence, never enabled A;
- concurrent operator stop after fence -> final B enable CAS fails; operator stop wins;
- concurrent newer Manager handoff waits on pipeline lock and reconciles after prior handoff exits;
- restart while handoff fence is present -> exact process-resume gate refuses to re-arm it;
- successful handoff -> expected generation increments according to the explicit two/three-step protocol and handoff identity binds the final generation/route revision.

## Scope

This does not eliminate the independent need for:

- existing continuous generation CAS on ordinary lifecycle writers;
- decision-card execution-lineage binding;
- protected Manager route revision/digest;
- external/admin `PIPELINE_STATE` writer fencing.

It closes a distinct cross-file commit ordering failure in the current Manager-authored continuous handoff itself.

## Exact continuation

1. Audit `before_write` uses repository-wide for any other cross-file callback that can leave an enabled execution state paired with a committed side effect after target replace failure.
2. Inspect Manager handoff identity publication and route snapshot/readback to define exactly what step 3 must verify before final enable.
3. Check whether a current disabled transitional state can be represented without violating `continuous_mode_error`/boot assumptions, or whether a small explicit `transition_id` field is cleaner.
4. Trace manager-pipeline-yield recovery on crash to ensure a stale yield token is self-clearing/fenced.
5. Keep the existing separate frontier branches active.
