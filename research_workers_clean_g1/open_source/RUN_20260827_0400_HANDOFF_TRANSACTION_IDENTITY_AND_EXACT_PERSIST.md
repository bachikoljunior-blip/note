# Open Source Systems Scan — handoff transaction identity + exact mission persistence

Invocation started: 2026-08-27T04:00:31+09:00
Checkpointed: 2026-08-27T04:07:45.099068+09:00

Frozen semantic tuple for this invocation:
- note main SHA: `fd651b61fc3a651ee1fe8925a9c50c23eb352b30`
- sanitized control revision: `10`
- open_source config revision: `5`
- open_source config blob: `118f440957ba4654e804af902aa09a9224acca43`

Independence: own clean state + public sources only. No O/O-derived state, other-worker state/config, downstream semantics, legacy/pre-independence research, aggregate execution ledger, or other-role receipts/configs were used. No own sanitized feedback file was present. The selected control/config tuple was frozen before the first role-local semantic read.

Public source head used for this run:
- `lbx154/Argus` public `main`: `0904e8de645a6e4988e49815c9d9e2c3b511c467`.

## 1. The continuous replacement write is localized enough for a narrow repair

The production continuous TEAM path in `argus_skill/manager/dispatch.py::enqueue_mission()` defines `_persist_operator_priority_item()` and supplies it to `front_door.manager_continuous_handoff()`.

That callback creates a `BacklogItem` with `item_id=root_task_id` and calls `mem.backlog.add(item)`. The only other production `mem.backlog.add` use found by code search is the generic/manual life action helper. Therefore the transaction-hardening change does not need to redefine every backlog write: the Manager continuous replacement path can use a new narrow exact-insert primitive while ordinary `/add` semantics remain unchanged.

## 2. New identity result: `root_task_id` is stable inside one operator turn, but not across recovery turns

`webapi/manager_dispatch.py::_classify_operator_turn()` creates exactly one `root_task_id = BacklogItem.new_id()` before the merged front-door classify and carries it through `_ClassifyResult` into `_dispatch_team_mission()`, Manager preparation, and `enqueue_mission()`.

This gives the original handoff a natural stable target-item identity.

But a later recovery initiated as a new operator turn would generate a new root task id. Therefore recovery cannot safely reconstruct mission identity from a fresh turn. The original target item id must be durably captured before any route/backlog side effect if exactly-once recovery is required.

## 3. A handoff receipt and an idempotent backlog write are complementary, not alternatives

The prior frontier treated “exact-idempotent mission persistence” versus “handoff-specific receipt” as a choice. Current source makes that false.

A separate `mission_persisted=true` receipt cannot by itself solve a crash boundary:

1. backlog append succeeds;
2. receipt/final continuous write fails;
3. recovery cannot know whether to append again unless the backlog insertion itself can be safely retried by exact identity.

Conversely, an idempotent backlog primitive without a pre-side-effect durable transaction descriptor cannot preserve the original `root_task_id` and desired handoff identity after a process loss.

The minimal safe design therefore needs both:

- a disabled handoff fence/descriptor written before route mutation; and
- an atomic, idempotent target write under the existing backlog lock.

## 4. `Backlog.add()` is not an acceptable recovery primitive; Argus already has the right in-lock pattern elsewhere

Current `Backlog.add()` does:

`lock -> load -> append -> validate -> save`

with no duplicate-id check. `add_many()` rejects duplicate ids, but a retry that encounters an already-persisted target becomes an error rather than an idempotent success.

Duplicate ids are especially undesirable because `Backlog.update()` walks the rows and updates the first matching id, leaving later duplicate rows semantically ambiguous.

A useful positive internal precedent is `Backlog.continue_with_operator_reply()`: under one backlog lock it validates the pending decision/card condition, marks the old item terminal, appends exactly one continuation, updates dependent edges, validates, and saves. Replaying a resolved decision does not append another continuation. The desired Manager-handoff primitive can use the same “condition + mutation under one existing lock” pattern without a new database or transaction subsystem.

Recommended primitive shape:

`ensure_item_exact(target_item_id, creation_identity, item)`

- target id absent -> append once;
- target id present and immutable creation identity matches -> return existing row as success, even if normal runtime fields have since progressed;
- target id present with conflicting creation identity -> fail closed;
- all checks and save under the existing backlog lock.

## 5. Do not hash the whole `BacklogItem`: some creation fields are volatile or context-dependent

A later recovery cannot safely reconstruct byte-identical `BacklogItem.new(...)` output:

- `BacklogItem.new()` assigns `ts=time.time()`;
- continuous priority is derived from the then-current pending queue head;
- runtime fields such as status, attempts, timestamps and outcome can legitimately change after the item was first persisted.

Therefore “full row equality” would turn legitimate recovery into false conflicts.

`PreparedManagerHandoff` already exists before route commit and already carries the information needed to freeze a creation descriptor:

- `intent_id`;
- original `root_task_id`;
- Manager-clean `execution_task` from the pre-commit decision;
- the Manager decision itself;
- lifetime/open-ended intent.

The first disabled fence should additionally freeze any creation values that would otherwise be recomputed later, such as chosen priority and context-ref digest. The exact-insert primitive should compare canonical immutable creation identity, not mutable runtime state.

A practical descriptor is:

- `target_item_id`;
- `manager_intent_id`;
- canonical execution-task digest;
- canonical fixed tags/review contract;
- frozen priority;
- context-ref digest;
- expected protected-route fingerprint;
- optionally a descriptor schema version.

## 6. The existing `continuous.json` CAS is a strong place to host the fence, but its schema must explicitly carry it

Argus already has cross-process continuous locking, exact generation/full-state CAS, atomic replace, file durability handling, and directory durability handling.

However `ContinuousConfigState` currently contains only:

- enabled;
- objective;
- open_ended;
- done_reason/done_at;
- generation.

So a durable handoff descriptor is not representable there today. If the repair extends continuous state with a handoff/fence field, that field must participate in read/write/reserve serialization and `_same_continuous_state`; otherwise an exact CAS could silently ignore a concurrent fence change.

A separate receipt file is possible but creates another cross-file authority/recovery problem. Reusing the existing continuous CAS remains the lighter candidate if the schema extension is explicit and exact.

## 7. Concrete real-Backlog regression for the cross-object failure boundary

Argus already has two halves of the proof:

- `tests/daemon/test_state_portable.py::test_replace_failure_after_callback_surfaces_instead_of_false` proves a `before_write` side effect can commit while the final `continuous.json` replace fails, leaving old continuous state intact;
- `tests/manager/test_pipeline_yield.py::test_continuous_handoff_requests_boundary_yield` proves the current success ordering: route/backlog side effects happen before final continuous success.

The missing integrated regression should use the real `Backlog` and Manager handoff shape:

1. Persist continuous objective A and old pending backlog work.
2. Prepare replacement B with fixed target item id, for example `target-B`.
3. First exact CAS writes `disabled + handoff fence B` before any route/backlog side effect.
4. Route B commit, old-work supersession, and `ensure_item_exact(target-B, ...)` succeed.
5. Inject `EIO` on the final replace that would enable B.
6. Assert durable continuous state is still the disabled B fence; `A enabled + route B` is impossible.
7. Assert exactly one `target-B` backlog row exists.
8. Recover the same fence: `ensure_item_exact` returns the existing row instead of appending another, then final exact CAS enables B.
9. Run recovery a second time and assert the target row count remains one.
10. Pre-seed `target-B` with a conflicting immutable creation identity and assert recovery remains disabled/fail-closed.

This directly tests the safety invariant rather than a particular implementation detail.

## 8. Restart identity and process rearm remain independently incomplete on current main

`daemon/_life_worker_identity.py` still writes Manager handoff identity version 3 containing objective hash, vertical, domain, continuous generation and intent id. Matching allows identity generation `<=` the current generation and does not bind same-vertical route fields such as workflow mode, research target/direction or target venue.

The process-only rearm helper also still takes a previously read disabled state and calls non-CAS `write_continuous_config(enabled=True, objective=state.objective)` when the stop reason is in the exact process-stop allowlist.

The existing allowlist itself is a positive control: only drain-stop and graceful SIGTERM/SIGINT are process-resumable. The remaining repair is to make rearm exact-state CAS and make semantic crash-resume identity bind the canonical protected route.

V4 identity candidate remains:

`fingerprint(normalized vertical, domain, workflow_mode, research_target_level, research_direction_mode, target_venue)`

with `current_stage` excluded because legitimate progress changes it. V1-v3 should require one fresh Manager reconciliation before emitting v4 rather than being silently accepted as equivalent.

## Candidate refinement

`clean-os-g1-005` is now best stated as:

> Keep Argus's existing Manager pipeline lock and deterministic evidence gates, but make continuous replacement start with an exact-CAS disabled handoff descriptor that freezes the original target mission identity; persist that mission through an atomic idempotent exact-insert under the existing backlog lock; enable the new objective only after route/backlog facts reconcile; use exact-state CAS for process-only rearm; and bind semantic resume to a canonical protected-route fingerprint.

This is an unimplemented adaptation proposal, not a measured improvement.

## Scope and uncertainty

- No live exploit/crash was executed and no upstream Argus repository was mutated.
- Findings are source-level transaction/recovery analysis at public main `0904e8de645a6e4988e49815c9d9e2c3b511c467`.
- The source proves the partial-commit capability and non-idempotent primitive; it does not prove this failure has occurred in production.
- The proposed fence schema, exact-insert primitive, v4 identity and recovery path have not been implemented or benchmarked.

## Exact continuation

1. Specify the exact immutable `creation_identity` field set for `ensure_item_exact`, including how context refs, Manager decision evidence and frozen priority are canonicalized while mutable runtime fields are excluded.
2. Trace Argus's existing normalizers for workflow mode, domain, research target/direction and target venue and turn the v4 route fingerprint into a source-exact helper/migration test plan.
3. Map boot, immediate upgrade, replacement, scheduled upgrade and Web start onto one exact-state `reconcile_or_rearm` boundary; identify every remaining path that restores a caller-copied objective instead of CASing the currently observed disabled record.
4. Keep external/admin `PIPELINE_STATE` writer fencing as a separate branch; do not conflate it with continuous/restart authority.
