# Primary verification — Argus Manager continuous handoff is not exact-once at pinned commit

Verified: 2026-08-27T19:40+09:00

## Scope and pins

This audit is downstream-only and does not modify Argus or any clean exploration worker state/feedback.

- Frozen note semantic tuple for this verifier invocation: `note@c7f8790baf255de02ae8c559dea11b2012dd8ba2`, root control revision 12, downstream control revision 20, `primary_source_verifier` config revision 5.
- Public source pin: `lbx154/Argus@33da786bbc6787a2eeb63a5f492498eae87c78c7`.
- Target: retry/idempotency of the Manager continuous-handoff path when its durable pre-replace callback commits but the final `continuous.json` write fails or becomes durability-ambiguous.
- Evidence type: pinned source inspection plus existing pinned storage-unit tests. No live daemon fault injection and no production failure observation were performed.

## Verified current mechanics

### 1. Mission persistence occurs before the final continuous-state replace

`argus_skill/manager/front_door.py:manager_continuous_handoff()` reads an expected `ContinuousConfigState`, prepares the Manager decision, and calls `compare_and_swap_continuous_config(..., before_write=_commit)` under the pipeline lock. `_commit()` calls `prepared.commit(...)`; the continuous `enqueue_mission()` caller supplies a persistence callback that creates the operator-priority backlog mission before the final `continuous.json` replace.

Therefore a successful callback is a real durable side effect that can precede failure of the final continuous-state transition.

### 2. The persisted mission has an ID, but the current single-item insert is not an exact insert

In `argus_skill/manager/dispatch.py`, the continuous persistence callback constructs `BacklogItem.new(item_id=root_task_id, ...)` and calls `mem.backlog.add(item)`.

At the pinned commit:

- `BacklogItem.new_id()` creates a fresh 12-hex UUID prefix.
- `BacklogItem.new(..., item_id=...)` uses the supplied ID, otherwise creates a new one.
- `Backlog.add(item)` loads the backlog, unconditionally appends the item, validates dependency cycles, and rewrites the file. It does **not** reject an existing identical ID.
- By contrast, `Backlog.add_many(...)` explicitly rejects duplicate IDs both within the batch and against existing backlog IDs.

This contrast is important: Argus already has duplicate-ID conflict logic for batch insertion, but the continuous operator-priority path does not use it.

### 3. Ordinary Web/TUI retries naturally receive a new mission ID

`argus_skill/webapi/manager_dispatch.py` allocates `root_task_id = BacklogItem.new_id()` for a newly classified operator turn before dispatch. An ordinary user/API retry of the same semantic request as a new turn therefore receives a new physical mission identity unless the caller deliberately preserves the old ID.

Even deliberate reuse of the same ID is not currently exact-once: `Backlog.add()` permits another physical row with that same ID.

### 4. The creation event is independently append-only and has no dedupe key

After backlog insertion, the continuous callback best-effort appends a `life.planner.task_added` record through `JsonlEventSink`, carrying the backlog `item_id`. `JsonlEventSink._append()` serializes and appends a new JSON line under a file lock; it does not search for or reject an already-present logical creation event.

The event append is also not transactionally coupled to the backlog insert: its failure is swallowed because the backlog is treated as authoritative. Current state can therefore contain a backlog mission with no matching creation event, and a later retry can append another mission/event pair rather than reconcile an immutable creation receipt.

## Verified ambiguity classes

Pinned `tests/daemon/test_state_portable.py` explicitly covers both storage-level cases:

1. **Precommit committed, final replace failed.** `test_replace_failure_after_callback_surfaces_instead_of_false` makes the callback commit a marker, then fails replacement of `continuous.json`. Argus raises `ContinuousConfigCommitError`; the callback side effect exists while continuous state remains the old expected state.
2. **Final replace landed, durability failed afterward.** `test_post_replace_failure_surfaces_instead_of_false` replaces `continuous.json` and then raises an I/O failure. Argus raises `ContinuousConfigWriteAfterReplaceError`, while readback shows the new objective/generation actually landed.

These tests verify the storage semantics; they do not execute the real Backlog persistence callback.

## Retry/idempotency result

At the pinned commit, current code does **not** guarantee “one physical mission plus one creation event” across either ambiguity class.

For `ContinuousConfigCommitError`, the caller learns that the precommit happened and the final continuous replace did not land, but the exception carries no immutable creation receipt identifying the exact backlog row/event already committed. A fresh Web/TUI retry gets a fresh root task ID and can append a second mission and a second `task_added` event. Reusing the same root task ID still does not make the insert idempotent because single-item `Backlog.add()` does not reject an existing ID.

For `ContinuousConfigWriteAfterReplaceError`, readback can determine that the new continuous state may already be present. However, there is still no creation receipt binding that continuous generation to exactly one backlog row and one creation event. A blind semantic retry can therefore re-enter mission persistence rather than prove that creation already occurred exactly once.

The current `enqueue_mission()` exception path does not compensate by deleting the already-persisted operator-priority backlog item when `manager_continuous_handoff()` raises. Nor should destructive rollback be assumed safe without a creation identity, because the final continuous write may already have landed in the post-replace ambiguity case.

## What is and is not proven

**Verified from pinned source/tests:**

- callback-first ordering creates a durable-precommit/final-write split;
- both failure classes are intentionally surfaced rather than collapsed to a false CAS result;
- single-item backlog insertion lacks existing-ID conflict/idempotency semantics;
- batch insertion has stronger duplicate-ID rejection, showing the missing property is path-specific;
- `task_added` event persistence is append-only and not deduplicated;
- ordinary fresh operator turns allocate fresh root task IDs;
- current error/readback surfaces do not bind one exact mission/event creation to the continuous transition.

**Not claimed:**

- no production duplicate was observed;
- no real Backlog fault-injection test was executed in this verifier run;
- this does not establish that every retry path duplicates work;
- it does not establish that proposed `handoff_fence` / reconciliation-receipt machinery is correct or sufficient before implementation and tests.

## Design implication

The clean-worker proposal for a pre-reserved target mission ID plus immutable creation identity is materially motivated by current source behavior, but it remains a proposal. A minimal exact-once design needs at least:

1. a mission identity reserved before the callback;
2. exact-insert semantics that return “already exists and identical” versus “ID conflict” rather than blindly appending;
3. an immutable creation receipt/event identity tying mission creation to the semantic handoff;
4. recovery that reads current continuous state plus that receipt before deciding whether to insert, finalize, or refuse;
5. explicit handling of “backlog insert succeeded but event append failed” without creating a second backlog row.

## Exact next verification

Stay on the same pinned Argus commit only long enough to map the smallest reusable current primitives for an exact-insert recovery contract:

1. inspect tests/callers for single-item duplicate-ID behavior and determine whether `Backlog.add_many([item])` could safely supply exact-ID conflict semantics or whether a dedicated `add_exact` result type is required;
2. inspect existing immutable/idempotent event or message-ID primitives elsewhere in Argus that could serve as a creation receipt instead of inventing a new persistence subsystem;
3. define a source-exact regression matrix for: precommit-success/final-replace-fail, post-replace durability ambiguity, repeated recovery with the same reserved ID, and event-append failure after backlog insert;
4. keep those tests/design requirements separate from current guarantees until actually implemented and executed.
