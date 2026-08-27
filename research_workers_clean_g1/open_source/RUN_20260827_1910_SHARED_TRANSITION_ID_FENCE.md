# Open Source Systems Scan — shared intent-bound transition threading across front door and daemon boot

Invocation started: 2026-08-27T18:59:03+09:00
Checkpointed: 2026-08-27T19:10:50.302458+09:00

Semantic authority remains frozen at `note@4b19551018936e5b713eea90f7b3b87e3ff2f8c4 / control 12 / open_source config 5 / config blob 118f440957ba4654e804af902aa09a9224acca43`. Public source remains `lbx154/Argus@8a867e7b45f863a9cd4e79e4f6d21ca7a2009e48`. This file extends `RUN_20260827_1905_EVENT_ENVELOPE_CREATION_STAMP_HANDOFF_API.md`; no newer note control semantics were adopted.

## 1. Both semantic handoff origins already have the exact durable intent identity needed for reset provenance

The current front-door `PreparedManagerHandoff` owns a stable `intent_id` created before Manager division. Its `commit()` calls `manager.commit_vertical_decision(..., force_stage_reset=...)`, but that call currently has no transition identity argument.

Daemon boot independently creates `intent_id = intent-daemon-<time_ns>` before its Manager decision. Its `_commit_decision()` calls the same `mgr.commit_vertical_decision(..., force_stage_reset=..., _lock_held=True)` and likewise drops the intent identity before the stage-reset layer.

Therefore a shared fence does not need a new reset ID generator. `HandoffFenceV1.intent_id` can be exactly the already-emitted Manager intent identity in both origins:

```text
front door:
  PreparedManagerHandoff.intent_id

daemon boot:
  local intent-daemon-... identity
```

## 2. The current Manager-to-stage call chain has one clean place to thread `transition_id`

Current `commit_vertical_decision` accepts only `ask_on_new_domain`, `force_stage_reset`, and `_lock_held` beyond task/decision. Its internal commit path calls `vertical_select.reset_stage_for_new_intent(...)` in the relevant existing/new/adapted vertical branches. The current reset helper accepts `old_vertical`, `new_vertical`, `force_replacement`, and `evidence_root`; it has no transition identity parameter.

For forced replacement, `reset_stage_for_new_intent()` calls `stage_machine.reset_stage_for_replacement_intent(...)`. That primitive accepts `target_stage`, `reason`, `reset_by`, and `evidence_root`; it then delegates to `_set_stage(direction="reset", downgrade_downstream=True, legacy_rollback_history=True, ...)`.

Finally `_set_stage()` appends the authoritative `stage_history` entry with:

```text
at / from_stage / to_stage / direction / reason / by
```

and currently no intent/transition identity.

The least-invasive source-shaped threading remains:

```text
PreparedManagerHandoff.commit()
  -> commit_vertical_decision(..., transition_id=self.intent_id)

daemon boot _commit_decision()
  -> commit_vertical_decision(..., transition_id=intent_id)

commit_vertical_decision(..., transition_id="")
  -> _commit_vertical_decision_locked(..., transition_id=...)
  -> reset_stage_for_new_intent(..., transition_id=...)
  -> reset_stage_for_replacement_intent(..., transition_id=...)
  -> _set_stage(..., direction="reset", transition_id=...)
  -> stage_history[-1]["transition_id"] = transition_id when nonempty
```

The default remains empty for unrelated advance/rollback callers, avoiding a repository-wide requirement to mint transition IDs for every historical stage mutation.

## 3. Receipt minting can now prove the reset belonged to the exact active fence

A route fingerprint plus `direction="reset"` was insufficient: an older/newer replacement could have reset to the same first stage. With the existing Manager intent identity threaded through the normal call chain, `ManagerReconcileReceiptV1` can require all of:

```text
fence.intent_id == receipt.intent_id
persisted route fingerprint == fence.target_route_fingerprint
current protected pipeline digest == receipt.pipeline_digest
replacement_reset_required => newest relevant reset history transition_id == fence.intent_id
```

The reset postcondition still must be checked independently: first stage is actionable and no downstream stage remains `done`, `ready`, `in_progress`, or `skipped`. Identity proves *which handoff* performed the reset; postcondition proves the reset actually left a clean executable pipeline.

This does not authenticate every low-level stage caller globally. It is narrowly a handoff-reconciliation witness for `clean-os-g1-005`; broader primitive-bound stage authority remains a separate candidate surface.

## 4. The disabled fence must begin before the current precommit callbacks in both origins

Front door currently performs route/reset, replacement backlog supersession, optional session rename and optional mission persistence inside the continuous CAS `before_write` callback. Daemon boot similarly performs route/reset and replacement backlog supersession inside its continuous CAS `before_write` callback.

Because the same partial-precommit shape exists in both origins, `begin_handoff()` must execute before either callback/Manager commit. Recovery then sees a durable disabled fence even if route/reset succeeds and a later side effect/final continuous replacement fails.

Source-shaped ordering:

```text
with Manager pipeline lock:
  source ContinuousConfigState
  -> begin_handoff exact CAS to disabled fence
  -> Manager commit(... transition_id=fence.intent_id)
  -> strict direct readback + record_manager_receipt exact CAS
  -> origin-specific durable side effects
     front door: exact Backlog mission + append-once task-added event
     daemon boot: no operator-priority Backlog insertion
  -> final exact CAS to enabled target + fence cleared
```

A newer stop/objective change between phases invalidates the next exact CAS. Recovery never blindly replays the old Manager commit merely because target route fields happen to be visible.

## 5. Current public-main writer inventory still requires active-fence policy

A fresh search at `8a867e7b...` still finds production continuous writers in daemon state, daemon boot/identity, Web daemon lifecycle/upgrade, app life actions, and operator-decision handling. The prior `PRESERVE / CANCEL / FINALIZE / REFUSE` classification therefore remains necessary after first-class fence introduction; there is no upstream fence-aware writer policy yet.

The next pass should re-open those exact current call sites rather than inherit the earlier matrix text, because the public main advanced materially since the first audit.

## Candidate update

`clean-os-g1-005` no longer has an unresolved reset-provenance identity problem: **both front-door and daemon-boot handoffs already mint stable Manager intent IDs before any route mutation, and the current shared Manager→vertical-select→stage-machine path can carry that identity into the existing reset `stage_history` without inventing another durable authority object.** The active disabled fence should use that same ID, so the strict receipt can bind semantic intent, route reconciliation, reset provenance, mission creation and final continuous CAS to one lineage.

This remains a proposed adaptation; no Argus code was modified or benchmarked.

## Exact continuation

1. Re-open every current production continuous writer at `8a867e7b...` and classify active-fence behavior as `PRESERVE`, `CANCEL`, `FINALIZE`, or `REFUSE`, with exact source call sites.
2. Convert generic envelope `event_id` into literal Python and TypeScript replay-idempotency tests for `life.planner.task_added`.
3. Freeze `transition_id` regression tests: front-door replacement and daemon-boot replacement each emit exactly one matching reset-history identity; mismatched/stale identity blocks receipt mint.
4. Keep global/external `PIPELINE_STATE` writer fencing separate.
