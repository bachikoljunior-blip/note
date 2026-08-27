# Open Source Systems Scan — machine-safety fence preservation and replay-identity scope

Invocation started: 2026-08-27T19:58:03+09:00
Checkpointed: 2026-08-27T20:06:06.927144+09:00

Semantic authority is frozen at `note@9f8e7d51e9a8d6226d6dfb14583e72ac1864b306 / control 12 / open_source config 5`. The note repository advanced after semantic freeze; later control semantics were not adopted. Public source is `lbx154/Argus@8a867e7b45f863a9cd4e79e4f6d21ca7a2009e48`, verified as current public `main` during this invocation. Only the clean `open_source` role state and public source were used semantically.

## 1. Current-main continuous disables split cleanly into semantic cancellation versus machine/process preservation

The prior `PRESERVE / CANCEL / FINALIZE / REFUSE` fence policy can now be completed for the current public source.

### Planner-declared project completion — `PRESERVE`

`daemon/_life_worker_run.py` handles `stopped_by == "project_done"` by reading the current continuous state and CAS-disabling only when the state is still enabled and its generation exactly equals the daemon's adopted continuous generation. It preserves the objective and records `done_reason="planner declared project done"`. A bounded daemon then exits. This is an authoritative completion of the currently adopted campaign, but it is not permission to erase or finalize a newer disabled handoff fence. With a first-class fence invariant (`fence != None -> enabled == False`), the existing enabled/exact-generation guard naturally leaves a newer fence alone.

Policy: an active fence survives planner completion; no stale adopted generation may clear it. The current campaign may be terminal, while the newer target remains a separate reconciliation lineage.

### Content-filter disarm — `PRESERVE`

`life/supervisor/_planning_cycle_verdict.py` explicitly treats repeated provider content-filter refusal as a machine safety condition: it CAS-disables an enabled campaign, preserves the objective and records that operator reformulation is required. This is not an operator cancellation of a pending replacement. During an active disabled fence, the current code already skips the write because `current.enabled` is false.

Policy: preserve an active fence and remain disabled; do not convert the safety pause into cancellation of the pending Manager target.

### Backend/continuous structural invalidity — `PRESERVE`

`daemon/_life_worker_boot.py`'s live continuous provider checks `continuous_mode_error`. If the currently visible state is enabled but invalid (for example an unsupported memory backend or missing objective), it writes a disabled state and returns no live objective. This is a structural safety disarm, not semantic cancellation. A disabled active fence is already non-runnable, so it should remain intact rather than be cleared.

The earlier vault/backend-readiness preflight runs before Manager/provider/state mutation, so most boot-readiness failures do not need a fence mutation policy at all.

### SIGTERM/SIGINT/drain process stop — `PRESERVE`

`daemon/state.py` defines exactly two process-resumable stop reasons: `operator drain-stop` and graceful SIGTERM/SIGINT clock-out. `_life_worker_run.py` CAS-disables only the exact adopted generation on graceful operator process stop, while comments explicitly distinguish stopping the daemon process from ending the campaign. `_life_worker_identity.py` later re-arms only those exact reasons on `--resume-continuous`.

Policy: these process-level stops preserve an active handoff fence. They must never be reinterpreted as semantic `CANCEL`, and process restart must still refuse blind enable while a fence exists.

### Idle timeout — no continuous mutation

Idle timeout exits the daemon without rewriting continuous state. No fence-specific state transition is required.

### Explicit `/continuous stop|off|pause` — `CANCEL`

The shared chat router maps all three aliases directly to `disable_continuous_config`. These are explicit semantic operator instructions, unlike SIGTERM/drain. Under the candidate fence API they should cancel the pending handoff and keep the campaign disabled.

This extends the earlier explicit-stop inventory: `pause` is a semantic cancel alias at this command surface even though process-level graceful stopping is preservation.

## 2. Completed current-main active-fence policy

The source-shaped policy is now:

```text
explicit semantic stop/off/pause                  -> CANCEL
resolved operator-decision stop                   -> CANCEL
config/API semantic continuous-off                -> CANCEL

process start / daemon upgrade / stale resume     -> REFUSE blind enable; reconcile_or_rearm
old operator decision "continue"                  -> accept decision; REFUSE blind enable; reconcile
standing STEER shortcut                            -> REFUSE blind enable; reconcile

planner project_done                              -> PRESERVE newer active fence
content-filter disarm                             -> PRESERVE active fence
backend/continuous structural safety disarm       -> PRESERVE active fence
SIGTERM/SIGINT/drain process quiesce              -> PRESERVE active fence
idle timeout                                      -> no continuous-state mutation

strict Manager receipt + required durable effects -> FINALIZE
```

This preserves the distinction Argus already encodes in `RESUMABLE_STOP_REASONS`: process lifecycle authority is not campaign semantic authority.

## 3. Important correction: `event_id` gives duplicate cardinality, not automatically full reducer idempotency

The generic-envelope `event_id` proposal remains useful, but the previous wording "replay-idempotent Mission View" was too broad.

Python Mission View `_event_id()` uses explicit `event_id` first; `_timeline()` suppresses a duplicate timeline row and `_role_work()` upserts the same work ID. TypeScript `eventKey()` likewise gives explicit `event_id` precedence, and `life.planner.task_added` upserts the DAG by `item_id`, timeline by event key and role work by event key.

However both reducers perform state changes before/around those duplicate-aware structures:

- Python dispatcher updates `last_event_ts` before invoking the family reducer and updates `updated_at` afterward.
- TypeScript reducer updates `last_event_ts`; the task-added path also calls `setRole`, which rewrites the Planner role's `updated_at`, while role-work upsert can replace its timestamp/details.

Therefore replaying a second event with the same `event_id` but a changed event timestamp is not a byte-/state-identical no-op. The correct current claim is:

**A stable `event_id` is sufficient for one DAG node, one timeline row and one role-work identity for `life.planner.task_added`; it is not, by itself, a generic whole-reducer exactly-once guarantee.**

There is also a harmless implementation-format asymmetry: Python stores the explicit event ID directly as timeline/role-work identity, while TypeScript's `eventKey()` prefixes the canonical type (`<type>-<event_id>`). Both deduplicate locally, but their stored row IDs are not cross-language identical.

## 4. Literal regression shape for the current candidate

The minimal regression should test the contract actually needed by crash recovery rather than overclaiming full event-store exactly-once semantics.

Python (`tests/core/test_mission_view.py`):

```python
event = {
    "type": "life.planner.task_added",
    "event_id": "planner-task-added:v1:task-1:STAMP",
    "ts": 2,
    "_offset": 1,
    "item_id": "task-1",
    "title": "Fix CLI",
    "objective": "Repair the CLI",
}
replay = {**event, "_offset": 999}

view = emit_event(event)
view = emit_event(replay)

assert sum(node["id"] == "task-1" for node in view["dag"]) == 1
assert sum(row["id"] == event["event_id"] for row in view["timeline"]) == 1
assert sum(row["id"] == event["event_id"] for row in view["role_work"]) == 1
```

TypeScript (`frontend/tui/test/missionView.test.ts`, using shared core reducer):

```ts
const event = {
  type: 'life.planner.task_added',
  event_id: 'planner-task-added:v1:task-1:STAMP',
  ts: 2,
  _offset: 1,
  item_id: 'task-1',
  title: 'Fix CLI',
  objective: 'Repair the CLI',
};
const replay = { ...event, _offset: 999 };

let view = reduceMissionViewEvent(emptyMissionView(), event);
view = reduceMissionViewEvent(view, replay);

assert.equal(view.dag.filter((x) => x.id === 'task-1').length, 1);
const key = `life.planner.task_added-${event.event_id}`;
assert.equal(view.timeline.filter((x) => x.id === key).length, 1);
assert.equal(view.role_work.filter((x) => x.id === key).length, 1);
```

The replay changes transport position but retains the persisted semantic timestamp. If a future contract permits the same event identity to arrive with a different `ts`, then a reducer-entry seen-event guard (or canonical original-event timestamp) is additionally required before claiming full state idempotency.

For the handoff crash path, the stronger protection remains `append_event_once(stable event_id)` at the durable event log itself; Mission View dedup is downstream defense, not the primary exactly-once transaction.

## 5. `transition_id` reset-history regressions are now source-shaped

Current `stage_machine._set_stage()` appends `{at, from_stage, to_stage, direction, reason, by}` and has no transition identity. `vertical_select.reset_stage_for_new_intent()` calls `reset_stage_for_replacement_intent()` for forced replacement and is intentionally fail-open on reset failure. Both front-door and daemon-boot handoff origins already own a stable Manager intent ID before this path.

The previously proposed narrow change remains:

```text
front-door PreparedManagerHandoff.intent_id
or daemon-boot intent-daemon-...
  -> commit_vertical_decision(... transition_id=...)
  -> reset_stage_for_new_intent(... transition_id=...)
  -> reset_stage_for_replacement_intent(... transition_id=...)
  -> _set_stage(... direction="reset", transition_id=...)
  -> stage_history entry carries transition_id
```

Regression set:

1. Front-door replacement emits exactly one relevant `direction="reset"` history row with `transition_id == prepared.intent_id`.
2. Daemon-boot replacement emits a reset row whose transition ID equals the daemon `life.manager.intent.started` intent ID.
3. Strict Manager receipt refuses minting if the newest relevant reset row has no transition ID or a different ID, even if route fields already equal the target.
4. A stale older matching reset followed by a newer different reset cannot satisfy the active fence.

This still does not authenticate all low-level stage callers; it is narrowly provenance for the handoff-reconciliation candidate.

## Candidate update

`clean-os-g1-005` is now narrower and more testable: **semantic user cancellation is the only ordinary path that may cancel an active disabled handoff fence; machine safety, Planner completion and process quiescence preserve it; process/upgrade/stale-resume paths refuse blind enable; and finalization still requires the strict Manager receipt plus durable exact mission/event side effects. Generic `event_id` is retained as replay identity but its claim is narrowed to duplicate cardinality unless a stronger reducer-level guard is added. Existing Manager intent IDs remain the reset-lineage key.**

This remains a proposed adaptation based on public source inspection. No Argus code was changed and no performance or reliability improvement is claimed yet.

## Exact continuation

1. Inspect the persisted event-log replay/stream path to determine whether replay always preserves the original event `ts`; if yes, keep Mission View changes minimal and treat `event_id` as cardinality identity only. If not, add a reducer-entry duplicate guard before state timestamps are mutated.
2. Inspect the current event-envelope validator and event writer to freeze a literal caller-supplied deterministic `event_id` contract and `append_event_once` durable-lock behavior.
3. Locate the narrowest existing front-door and daemon-boot replacement tests and turn the four `transition_id` reset-history cases above into exact pytest modifications.
4. Keep global/external protected `PIPELINE_STATE` writer fencing separate from this handoff-local candidate.
