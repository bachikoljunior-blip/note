# Open Source Systems Scan — boot handoff initiation and durable task-added idempotency

Invocation started: 2026-08-27T17:58:28+09:00
Checkpointed: 2026-08-27T18:07:51.185551+09:00

Frozen semantic tuple: `note@ad8fa2c445a67e15064b32222ce14a8978b04c29 / control 12 / open_source config 5` (`DESIRED_STATE` blob `5c91671e1470d0fa4e2a53f918493004dd3750c3`, role-config blob `118f440957ba4654e804af902aa09a9224acca43`). The tuple was frozen only after the required SHA-only ref recheck and before the first role-local semantic read. Later note-main movement was observed only for collision-safe role-local writes and is not adopted semantically in this invocation.

Public source frozen for substantive inspection: `lbx154/Argus@7cb5546d364c7d11dcc3bff4151993b7aa72a414`, verified as current public `main` through a SHA-only Git-ref lookup. No O, other-worker, downstream, or legacy semantic state was read.

## 1. Boot is itself a semantic handoff initiator, not only a fence reconciler

The daemon boot path reads the durable continuous state, applies the narrow process-resume helper, constructs the live provider, and then decides whether an existing Manager handoff identity is safe to reuse. When `init_continuous` has a nonempty objective but no acceptable durable handoff identity, `_rf_manager_divide_on_boot()` performs a fresh Manager decision before the supervisor is constructed.

That fresh boot handoff is materially equivalent to the risky front-door ordering already identified: under the Manager pipeline lock it calls `compare_and_swap_continuous_config(..., before_write=_commit_decision)`, and `_commit_decision` first commits Manager route/stage state and may supersede pending backlog work. Only after those independent side effects does `continuous.json` get replaced.

Current boot failure handling is a useful process-local safety layer: after a same-generation failure it clears `init_continuous`, suppresses the still-enabled old objective for this process, and records a handoff failure; after a concurrent generation advance it rereads the provider. But this does not make the partial Manager side effects crash-stable or durably reconcilable. A route/reset/supersede may already have landed while `continuous.json` remains the old generation.

**Design consequence:** `HandoffFenceV1` cannot be a front-door-only object that boot merely consumes. A shared `begin_or_reconcile_handoff` boundary must allow at least two initiators:

- `front_door`: starts a fence before route/session/backlog/persist side effects for an operator continuous handoff;
- `daemon_boot`: starts a fence when boot has a semantic continuous objective but no reusable matching handoff identity, and reconciles an existing compatible fence when one is already durable.

A fresh non-resume daemon with no semantic resume intent should still not create a fence merely because an old enabled campaign exists; current boot suppression remains the positive control for that case.

## 2. Exact first-class fence schema

The fence must live inside `ContinuousConfigState`, because the current reader reconstructs only known fields and ordinary whole-state writes discard unknown JSON keys. It must also participate in reserve sizing and the manual CAS equality check.

Proposed `HandoffFenceV1` authority fields:

```text
version: 1
fence_id: stable random identifier
intent_id: Manager intent identifier
origin: front_door | daemon_boot
source_continuous_generation: exact generation from which fence began
source_route_v4: semantic protected-route fingerprint
requested_objective: durable raw semantic objective needed for a fresh Manager re-decision
requested_objective_sha256: integrity digest of requested_objective
target_open_ended: requested continuous lifetime bit
dispatch_mode: operator_priority_backlog | continuous_provider_seed
target_item_id: pre-reserved Backlog ID when dispatch_mode=operator_priority_backlog, else empty
target_route_v4: absent until Manager has reconciled, then exact semantic route fingerprint
target_execution_task: absent until Manager has reconciled, then Manager-clean task
target_execution_task_sha256: integrity digest
manager_receipt: optional ManagerReconcileReceiptV1, added only after strict postcondition validation
mission_spec: optional immutable reconstruction spec for operator_priority_backlog, added only after Manager reconciliation
created_at: audit only; excluded from authority equality except normal whole-state CAS bytes
```

The raw requested objective is intentionally retained, not only its digest. If recovery finds the protected state still at the source route, it must be able to rerun Manager semantically. A digest alone cannot reconstruct that request, and boot objectives are not guaranteed to have an external transcript/ref that can safely serve as the source.

`source_route_v4` / `target_route_v4` use the previously established semantic fields: normalized `vertical`, `domain`, `workflow_mode`, `research_target_level`, `research_direction_mode`, and semantically normalized `target_venue`. `current_stage` is excluded because ordinary valid progress changes it.

The invariant remains hard: **`handoff_fence != null => enabled == false`**. Generic writers need typed `PRESERVE/CANCEL/FINALIZE/REFUSE` behavior; no caller may preserve a fence while setting `enabled=true`.

## 3. Strict Manager receipt needs an intent-bound reset transition

`ManagerReconcileReceiptV1` should bind:

```text
version: 1
fence_id
intent_id
target_route_v4
pipeline_canonical_sha256
vertical
first_stage
observed_current_stage
replacement_reset_required
reset_transition_digest / transition identifier when reset is required
custom_domain_canonical_sha256 when the vertical is project-local
recorded_at: audit only
```

`pipeline_canonical_sha256` is SHA-256 over the parsed full protected pipeline object rendered with sorted keys and compact separators; raw JSON whitespace/order is not authority.

The strict mint gate direct-reads the protected `PIPELINE_STATE`, strictly loads the persisted vertical/domain with no research fallback, requires `current_stage` to equal the exact first stage, requires that target stage to be `in_progress`, and rejects any downstream status in `{done, ready, in_progress, skipped}`. For replacement resets it also requires fresh reset history.

A new subtle gap is now explicit: current `reset_stage_for_replacement_intent` ultimately records reset history as `{at, from_stage, to_stage, direction, reason, by}`. It has no durable `intent_id`/transition token. Therefore a later receipt can prove that *a* Manager reset happened and bind the resulting full-state digest, but cannot directly prove that the reset was performed for this exact fence intent. The stronger candidate is to pass a stable `transition_id`/`intent_id` through the replacement-reset primitive and record it in the reset history; strict receipt mint then requires `direction=reset`, `by=manager`, the expected first stage, and `transition_id == fence.intent_id`.

This is an unimplemented adaptation, not a claim about current Argus behavior.

## 4. The physical continuous-mission task-added event is now mapped exactly

For the front-door continuous dispatch, `manager/dispatch.py` creates one operator-priority `BacklogItem`, calls `mem.backlog.add(item)`, then best-effort appends:

```json
{
  "type": "life.planner.task_added",
  "item_id": "<same backlog item id>",
  "source": "manager_operator",
  "operator_priority": true,
  "title": "...",
  "objective": "...",
  "deps": [],
  "priority": -1
}
```

The event type is canonical and signal-level, and an existing dispatch regression asserts exactly this `item_id`, `source`, and `operator_priority` shape.

However the current `JsonlEventSink.append()` is an ordinary locked append. It has no stable event ID, no deduplication check, and no exactly-once replay primitive. The dispatch wrapper also swallows event append failure because the backlog row is authoritative.

This corrects the predecessor's proposed regression: **an exactly-once Backlog insert plus `inserted: bool` is not enough to prove exactly one durable `life.planner.task_added` event.** Two crash windows show why:

1. backlog row commits, process dies before event append; retry sees `inserted=False`, so emitting only when `inserted=True` leaves zero events;
2. backlog row and event append both happen, process dies before final handoff enable; blindly re-emitting on retry can produce a duplicate because the event log has no idempotency key.

## 5. Minimal event-idempotency primitive instead of a cross-file transactional outbox

A full database transaction is not required for this narrow observable if the event sink gains one stable idempotent append primitive.

Proposed contract:

```text
creation_stamp: immutable on the Backlog item
task_added_event_id = "planner-task-added:" + item_id + ":" + sha256(creation_stamp)
append_event_once(event_id, payload)
```

`append_event_once` should run under the existing `events.lock`, preserve `event_id` in the canonical event row, inspect retained `events.jsonl*` generations for that exact ID, and append only when absent. The append should flush/fsync the event file before success; if the live events file is newly created or rotation changes directory entries, parent-directory durability must also be handled. Recovery then always calls `append_event_once` after `ensure_operator_priority_item_exact`, regardless of whether the backlog insert was new or an idempotent replay.

This closes both windows:

- row exists / event absent -> recovery appends once;
- row exists / event already appended but caller never observed success -> recovery finds the same stable event ID and does not append again.

For scale, a durable event-id index could optimize lookup later, but a separate index must not be treated as authority unless its own crash consistency is solved. The append-only event row itself is the simplest source of truth for the rare `task_added` recovery path.

If this primitive is not added, the correct contract must be weakened to **exactly-once Backlog authority plus best-effort task-added observability**; claiming exactly-one durable event would exceed the current implementation.

## 6. Real-Backlog recovery regression, corrected

The existing real-Backlog Manager pipeline-yield harness and existing continuous-storage callback/replace failure injection remain sufficient building blocks, but the target test needs the event-idempotency primitive above.

```python
def test_handoff_replace_failure_recovers_backlog_and_task_event_exactly_once(...):
    # A enabled; old backlog exists; target item id is pre-reserved in fence.
    # begin_or_reconcile_handoff exact-CASes A -> disabled fence B BEFORE side effects.
    # Manager route/reset reconciliation succeeds and strict receipt is minted.
    # ensure_operator_priority_item_exact(...) persists one row with immutable creation_stamp.
    # append_event_once(stable_task_event_id, life.planner.task_added payload) persists once.
    # Inject ambiguous/failing final continuous write after those side effects.
    # Recovery rereads current continuous bytes/generation; run recovery twice.
    # Assert:
    #   exactly one backlog row for target id,
    #   exactly one retained task-added event with stable event_id,
    #   exactly one final B-enabled transition,
    #   fence cleared only by FINALIZE.
```

`ensure_operator_priority_item_exact` still needs one Backlog lock covering ID collision check, priority calculation, first timestamp/stamp creation, and insert. Same ID + same immutable creation stamp returns the current row; same ID + different/missing stamp or duplicate physical IDs fails closed. The shared Backlog whole-file rewrite remains only temp+`os.replace` today, so power-loss durability still requires file and parent-directory fsync if the candidate claims durable ordering against the final continuous enable.

## 7. Boot-specific recovery state machine

The boot path should use the same durable fence but does not need to fabricate a front-door operator-priority backlog item. Its natural `dispatch_mode` is `continuous_provider_seed`.

- no fence + semantic boot objective needing Manager -> begin disabled fence, then Manager reconcile;
- matching fence + protected state still matches `source_route_v4` -> rerun Manager from durable `requested_objective`;
- matching fence + protected state appears target-like -> do not trust route fingerprint alone; strict-mint/validate `ManagerReconcileReceiptV1`; if valid, continue; otherwise rerun Manager/fail closed;
- protected state matches neither source nor target -> do not guess; require fresh reconciliation;
- only after strict receipt and all dispatch-mode-specific durable side effects are complete may FINALIZE clear the fence and enable the Manager-clean target objective.

Current boot's process-local suppression on failure remains useful defense-in-depth but should not be mistaken for durable recovery state.

## 8. Candidate refinement

`clean-os-g1-005` is now:

**a shared front-door/boot first-class disabled HandoffFenceV1 installed before semantic side effects; strict ManagerReconcileReceiptV1 with intent-bound replacement-reset evidence and canonical protected-state/custom-domain digests; dispatch-mode-specific finalization; pre-reserved mission identity plus immutable exact Backlog insert for front-door continuous work; stable idempotent `life.planner.task_added` event append keyed by the Backlog creation identity; exact-state process rearm; and v4 semantic protected-route identity for restart reuse.**

This run did not modify Argus, reproduce a live race, or benchmark the proposed change. The result is a source-level architecture/regression candidate at the pinned public commit.

## Exact continuation

1. Inspect `PreparedManagerHandoff.commit()` and `Manager.commit_vertical_decision()` call boundaries to determine the least invasive way to thread a fence `intent_id` into replacement-reset history without changing unrelated stage transitions.
2. Inspect event-log rotation/retained-generation readers to specify a bounded but correct `append_event_once` implementation and crash tests, including create/rotation fsync behavior.
3. Specify the immutable `mission_spec` fields needed in a front-door fence to reconstruct the target row when a crash happens after Manager reconciliation but before Backlog insert, while keeping mutable priority/timestamp assigned exactly once under Backlog lock.
4. Turn boot/front-door fence initiation into one source-shaped helper API and map each existing caller to begin/reconcile/finalize semantics.
5. Keep external/admin whole-object `PIPELINE_STATE` writer fencing and global JSON-state CAS as a separate candidate branch; do not broaden this result into a claim about all Argus state writers.
