# Open Source Systems Scan — intent-bound reset threading, append-once event, and crash-reconstructible mission spec

Invocation started: 2026-08-27T17:58:28+09:00
Second checkpoint: 2026-08-27T18:12:38.901823+09:00

Semantic authority remains frozen at `note@ad8fa2c445a67e15064b32222ce14a8978b04c29 / control 12 / open_source config 5`. Public source remains `lbx154/Argus@7cb5546d364c7d11dcc3bff4151993b7aa72a414`. This file extends `RUN_20260827_1807_BOOT_FENCE_EVENT_IDEMPOTENCY.md`; no changed control or other-role semantic state is adopted.

## 1. Least-invasive intent-bound reset threading is now source-shaped

`PreparedManagerHandoff` already owns the exact `intent_id` needed by the front-door path. Its `commit()` calls `manager.commit_vertical_decision(..., force_stage_reset=...)`, but that API currently has no transition identity parameter. The daemon boot path independently creates `intent-daemon-<time_ns>` and then calls the same `mgr.commit_vertical_decision(...)`, again without passing that ID into stage reset.

`Manager.commit_vertical_decision()` delegates to `_commit_vertical_decision_locked()`. The latter calls `vertical_select.reset_stage_for_new_intent(...)`, and replacement reset then calls `stage_machine.reset_stage_for_replacement_intent(...)`. That stage primitive uses `_set_stage(direction="reset")`, whose durable `stage_history` entry currently contains `at/from_stage/to_stage/direction/reason/by` but no intent/transition identifier.

The smallest coherent adaptation therefore follows the existing call stack instead of introducing a sidecar:

```text
PreparedManagerHandoff.commit()
  -> commit_vertical_decision(..., transition_id=self.intent_id)

daemon _rf_manager_divide_on_boot._commit_decision()
  -> commit_vertical_decision(..., transition_id=intent_id)

commit_vertical_decision(..., transition_id="")
  -> _commit_vertical_decision_locked(..., transition_id=...)
  -> reset_stage_for_new_intent(..., transition_id=...)
  -> reset_stage_for_replacement_intent(..., transition_id=...)
  -> _set_stage(..., direction="reset", transition_id=...)
  -> stage_history[-1]["transition_id"] = transition_id when nonempty
```

Nonreplacement stage transitions keep the empty default and remain byte-compatible except where a Manager handoff intentionally supplies an ID. Strict `ManagerReconcileReceiptV1` can then require `transition_id == fence.intent_id` when `replacement_reset_required=true`.

This is still a proposed adaptation. No Argus source was modified.

## 2. `append_event_once` can reuse the existing event lock and retained generations

The current event subsystem already has the two structural pieces needed for an idempotent append:

- `event_log_paths()` enumerates retained `events.jsonl.2`, `.3`, ..., `.1`, then the live `events.jsonl` in lifetime order;
- `JsonlEventSink._append()` already serializes append/rotation with a process-local mutex plus the POSIX `events.lock`.

A source-shaped primitive can therefore avoid a new authoritative index:

```python
def append_once(self, event: dict[str, Any], *, event_id: str) -> tuple[bool, bool]:
    # returns (accepted, inserted)
    payload = self._normalize({**event, "event_id": event_id})
    with self._lock:
        with events_file_lock_exclusive():
            if event_id_exists_in_retained_generations(event_id):
                return True, False
            rolled = self._maybe_roll_durable()
            # same exclusive lock => no competing append can appear between check and write
            append_canonical_line(payload)
            flush_and_fsync_live_event_file()
            if created_new_live_file or rolled:
                fsync_event_directory()
            update_mission_view_best_effort(payload)
            return True, True
```

The exact-ID lookup must parse candidate JSON rows rather than treat a raw substring match as proof, so a partial trailing row or another field containing the same text cannot suppress a real event. Because rotation and append share the same file lock, one pre-append scan is sufficient for concurrency; recovery after an ambiguous prior call scans all retained generations again.

`_maybe_roll()` currently uses `os.replace` without a directory fsync. Therefore claiming *durable* exactly-once across power loss requires either hardening rotation or having the append-once path fsync the directory whenever it moved generations. Ordinary best-effort events need not inherit this stronger contract unless desired.

No separate event-id index should be authoritative initially. A future index may be a performance hint, but a crash between event append and index update otherwise recreates the same two-file coherence problem.

## 3. The target event ID can be deterministic from immutable mission creation identity

For continuous operator-priority work, the canonical event can use:

```text
event_id = "planner-task-added:v1:" + item_id + ":" + sha256(creation_stamp)
```

The event row should carry this `event_id` as an explicit canonical envelope/payload field. The current event normalizer preserves ordinary mapping fields and there is no existing event-id dedup contract, so the addition must be made explicit in the event schema/tests rather than inferred from `item_id` alone.

Recovery always invokes `append_once` after `ensure_operator_priority_item_exact`, even when the backlog item was already present. That distinction is load-bearing:

- row exists but event append never happened -> append once now;
- event append happened but caller crashed before observing success -> retained-generation lookup returns the existing event;
- final continuous enable failed after both -> a second/third recovery still gets exactly one event.

## 4. Front-door `mission_spec` can now be frozen exactly

The current continuous operator-priority construction supplies only the following creation-time values that must be recoverable after Manager reconciliation but before Backlog insertion:

```text
item_id                  # pre-reserved root_task_id
title                    # exact derived title already chosen by dispatch
objective                # Manager-clean execution task
tags = [manager, operator, operator_priority, scope:bounded,
        review:required, stage_transition:skip]
iterate = false
iteration_max_cycles = 1
context_refs              # exact merged normalized refs
original_objective        # current path sets this to execution task
manager_decision          # decision_evidence(committed division) or {routed: true}
target_route_v4           # added explicitly; manager_decision alone does not bind every route field
intent_id
```

`priority` and `ts` must **not** be precomputed in the fence. The current path reads pending priority, then separately calls `Backlog.add`, which is a TOCTOU. The replacement `ensure_operator_priority_item_exact(mission_spec, creation_stamp)` should hold one Backlog lock while it:

1. rejects duplicate physical IDs / conflicting existing stamp;
2. if exact row already exists, returns it unchanged;
3. otherwise reads the current pending queue and fixes priority;
4. generates the first timestamp;
5. constructs the Backlog row with immutable `creation_stamp`;
6. performs the durable whole-file rewrite.

The `creation_stamp` is SHA-256 over canonical immutable `mission_spec` plus its schema version. It excludes mutable scheduler/runtime fields (`priority`, `ts`, `status`, attempts, outcome, later objective refinements) but the stored row still retains the initially chosen priority/timestamp for exact replay.

This spec is sufficient to reconstruct the current front-door row without rerunning title/context/Manager-decision derivation after a crash. Default Backlog fields not listed above remain schema defaults.

## 5. Backlog and event durability ordering

The recovery/finalization order for `dispatch_mode=operator_priority_backlog` should be:

```text
1. strict Manager receipt is valid inside active disabled fence
2. ensure_operator_priority_item_exact -> Backlog row durably present
3. append_event_once -> task-added event durably present exactly once
4. final exact continuous CAS -> enabled target objective, fence cleared
```

The current shared Backlog `_atomic_rewrite_jsonl` writes a temp file and `os.replace`s it but does not explicitly fsync the temp file or parent directory. Therefore step 2 is not power-loss durable under the present implementation. If final-enable ordering is intended to survive host/power crash, the common Backlog rewrite primitive should be hardened to `flush + file fsync -> replace -> directory fsync`, not only the new exact-insert path: every later ordinary Backlog whole-file rewrite can otherwise weaken an earlier stronger write.

## 6. Shared handoff helper and lock order

A minimal shared implementation does not need to keep `continuous.lock` held across Manager/backlog/event work. Preserve the existing Manager-before-continuous lock direction:

```text
with manager.pipeline_lock():
    CAS source continuous -> disabled HandoffFenceV1       # briefly takes continuous.lock
    commit/reconcile Manager route and reset
    strict direct-read ManagerReconcileReceiptV1
    CAS fence -> fence+receipt+mission_spec                 # briefly takes continuous.lock
    exact Backlog insert                                   # backlog lock only
    append_event_once                                      # events lock only
    CAS fence-finalizable -> enabled target, fence=null    # briefly takes continuous.lock
```

A newer semantic command can still cancel/supersede the fence between those CAS points; each subsequent CAS then fails instead of resurrecting the old request. The outer Manager pipeline lock prevents a second Manager route mutation from interleaving. This avoids introducing the reverse `continuous.lock -> pipeline_lock` order.

Boot uses the same state machine with `dispatch_mode=continuous_provider_seed`, skipping Backlog/event steps. It must still begin the disabled fence before its `commit_vertical_decision` side effect and mint the same strict Manager receipt before final enable.

## 7. Updated regression matrix

Highest-value literal tests now are:

1. front-door replacement: final continuous replace fails after route/reset + exact Backlog + append-once event; two recoveries produce one target row, one event ID, one final enable;
2. crash after Backlog insert but before event append; recovery produces the missing event once;
3. crash/exception after fsynced event append but before caller observes success; retry detects existing event ID across retained generations;
4. same event ID already in `.2`/`.3` after multiple rotations; live append is suppressed;
5. partial trailing event line containing the ID but invalid JSON does not count as existing; valid retry appends;
6. replacement reset receipt rejects a reset history row whose `transition_id` differs from fence `intent_id`;
7. daemon boot fresh semantic objective begins the same fence before route side effects; matching existing fence reconciles rather than creating a second one;
8. newer stop/superseding objective between fence phases makes the stale final CAS fail and never re-enables the old target.

## Candidate update

`clean-os-g1-005` now has a source-shaped minimal path for the three formerly vague pieces: **intent-bound reset evidence can be threaded through the existing Manager→vertical_select→stage_machine call stack; front-door crash reconstruction can freeze the exact mission creation spec while assigning priority/time only once under Backlog lock; and the canonical task-added observable needs a stable event ID plus an `append_once` primitive over the existing locked retained event tape rather than relying on `inserted: bool`.**

## Exact continuation

1. Inspect `event_payload_schemas.json` and Mission View reducers for `life.planner.task_added` to identify every compatibility surface of adding `event_id`, and decide whether envelope-level or event-specific schema placement is least disruptive.
2. Inspect `BacklogItem.from_jsonable` plus generic `Backlog.update` to specify backward-compatible `creation_stamp` migration and immutable-field guards without breaking legacy unstamped rows.
3. Convert the proposed shared helper into exact function signatures/state transitions for `begin_handoff`, `record_manager_receipt`, and `finalize_or_reconcile`, including CAS expected-state tuples.
4. Keep global/external protected pipeline writer fencing separate.
