# Open Source Systems Scan — continuous fence call-site matrix and explicit fence-action contract

Invocation started: 2026-08-27T13:57:50+09:00
Checkpointed: 2026-08-27T14:01:41+09:00

Frozen semantic tuple: `note@6ed08bcaa401a21814129ce1229614be72211e51 / control 11 / open_source config 5` (`DESIRED_STATE` blob `bf7b8c7f6971c0ec2f3fa7a8d53dca1f88ac50a3`, role-config blob `118f440957ba4654e804af902aa09a9224acca43`). The first role-local semantic read occurred only after the second SHA-only note-main check confirmed the same head. Only own clean state and public sources were used.

Public source frozen for this run: `lbx154/Argus@33da786bbc6787a2eeb63a5f492498eae87c78c7` (verified current `main` by SHA-only Git-ref lookup).

## 1. Production continuous-state writer inventory at the public Argus head

Code search at the frozen Argus commit found the following non-test callers.

### Direct `write_continuous_config(...)`

- `argus_skill/webapi/daemon_lifecycle.py::start_project_daemon`
- `argus_skill/webapi/daemon_upgrade.py::upgrade_project_daemon`
- `argus_skill/webapi/daemon_upgrade.py::_complete_scheduled_daemon_upgrade`
- `argus_skill/apps/_life_actions.py::render_config_cmd`
- `argus_skill/daemon/_life_worker_boot.py` continuous backend compatibility disarm path
- `argus_skill/webapi/manager_pending_question.py::_reconcile_campaign_after_decision`
- `argus_skill/daemon/_life_worker_identity.py::_rearm_operator_drain_for_resume`

`argus_skill/daemon/state.py` is the storage implementation and is not counted as an external semantic caller.

### `compare_and_swap_continuous_config(...)`

- `argus_skill/manager/front_door.py::manager_continuous_handoff`
- `argus_skill/daemon/_life_worker_boot.py` boot-time Manager divide/handoff
- `argus_skill/webapi/manager_dispatch.py` standing-STEER promotion
- `argus_skill/daemon/_life_worker_run.py` planner-declared project completion disarm
- `argus_skill/life/supervisor/_planning_cycle_verdict.py` content-filter permanent-error disarm

### `disable_continuous_config(...)`

- `argus_skill/webapi/manager_dispatch.py::disable_manager_continuous`
- `argus_skill/apps/_life_actions.py::render_config_cmd` for `continuous=false`
- `argus_skill/life/chat/router.py::_cmd_continuous` for `stop|off|pause`

The existing `ContinuousConfigState` still has only `enabled/objective/open_ended/done_reason/done_at/generation`; therefore no current caller can preserve or explicitly resolve a future handoff fence without a first-class schema/API change.

## 2. Active-fence behavior is not one generic “preserve or clear” rule

The call sites separate into four semantic classes. This is the key refinement from the predecessor run.

### A. `CANCEL` — explicit operator semantic stop

These calls should clear an active handoff fence and leave the campaign disabled:

- Web `disable_manager_continuous`;
- chat `/continuous stop|off|pause`;
- `/config continuous=false`;
- operator-decision resolution with `stopped=True` (`"operator chose to stop the campaign"`).

A user stop is newer semantic authority. Preserving a pending fence would let old work reappear later; silently enabling is obviously wrong.

### B. `REFUSE` — process/lifecycle rearm or semantic shortcut that lacks handoff authority

These calls must not collapse, clear, or enable through an active fence:

- `start_project_daemon(..., resume_continuous=True)`;
- immediate daemon upgrade rearm;
- scheduled daemon upgrade rearm from the persisted request snapshot;
- `_rearm_operator_drain_for_resume`;
- operator-decision `stopped=False` blind resume;
- standing-STEER promotion that directly CASes the current continuous state to `enabled=True`.

The first four are process control, not semantic campaign authority. The latter two represent valid new operator information but do not prove that the protected route/Manager reconciliation associated with the pending fence is still current. They should either trigger explicit supersession/reconciliation or return a pending-reconcile outcome; they must not treat “disabled + objective present” as sufficient authority to enable.

This classification also makes the existing daemon-start bug structurally obvious: `start_project_daemon` currently re-enables any disabled state whose `done_reason` merely starts with `"operator "`, and does so before daemon admission/spawn. A first-class fence must therefore be an explicit hard refusal at this call site, not another string in `done_reason`.

### C. `FINALIZE` — exact handoff completion only

Only the Manager handoff boundaries should be allowed to clear a fence and enable its target:

- live `manager_continuous_handoff` after strict Manager reconciliation and durable target-mission persistence;
- boot-time Manager divide/handoff after the same exact reconciliation conditions on recovery.

Finalization must require the exact expected fence identity/state in the CAS and the strict postcondition receipt from the predecessor design. Merely observing a target-looking route is insufficient because Manager commit includes more than the six-field route fingerprint and replacement reset is currently fail-open.

### D. `PRESERVE / NO-OP` — machine safety or terminal disarm paths

These paths should never cancel a pending fence merely because they are defensive disarms:

- boot-time backend/continuous-mode incompatibility disarm;
- planner-declared `project_done` disarm;
- content-filter permanent-error disarm.

Under the invariant `handoff_fence != None => enabled == False`, these paths normally cannot reach their write branch while a fence is active. If they do observe a fenced state because of a future refactor/race, they should preserve the fence and remain disabled, not reinterpret the safety event as operator supersession.

## 3. Raw tri-state field plumbing is too easy to misuse; use an explicit fence action

The predecessor proposed an `UNSPECIFIED=preserve / None=clear / HandoffFence=set` tri-state field argument. The call-site inventory shows that persistence intent and semantic authority are different enough that the public writer API should make the action explicit.

A narrower contract is:

```text
FenceAction = PRESERVE | CANCEL | FINALIZE | REFUSE
```

with fence creation handled by a dedicated `begin_handoff_fence(...)` primitive rather than a generic whole-state writer.

Required behavior when the current state has an active fence:

- `PRESERVE`: keep the exact fence. Any request with `enabled=True` fails closed. `enabled=False` safety/process writes may update only fields explicitly allowed by the fence schema, preferably no semantic fields at all.
- `CANCEL`: clear the fence and remain disabled. This is reserved for explicit newer semantic stop/supersession operations. It must never be the default.
- `FINALIZE`: require exact expected generation **and exact expected fence identity**, validate the strict Manager receipt/target mission durability, clear the fence, and enable the target in the same continuous-state CAS.
- `REFUSE`: if a fence exists, make no continuous-state mutation and return/raise a distinct pending-reconciliation result. This is the correct behavior for lifecycle/process helpers and shortcut resumes.

Generic legacy callers should default to `PRESERVE`, and the invariant `PRESERVE + active fence + enabled=True => fail closed` prevents accidental resurrection. Process helpers that currently attempt enable should use `REFUSE` so the caller can route to the common `reconcile_or_rearm` boundary instead of receiving a generic storage error.

`_same_continuous_state()` and CAS equality must include the full fence. Otherwise a caller could satisfy generation/ordinary-field equality while racing a different reconciliation checkpoint.

## 4. Why `disable_continuous_config` should not itself mean “cancel fence”

`disable_continuous_config` currently means “atomically disable the latest generation while preserving its objective.” It is used by explicit operator stop surfaces, but the codebase also contains machine-generated disabled states and future defensive callers may reuse it. Therefore adding `clear fence whenever disabling` at the storage layer would collapse semantic stop and safety/process suspension.

The caller must carry the semantic action. Operator-stop surfaces pass `CANCEL`; machine/process disarms keep the default `PRESERVE`. This preserves the existing narrow `RESUMABLE_STOP_REASONS` distinction instead of replacing it with another reason-string convention.

## 5. Regression matrix implied by the call-site inventory

At minimum, add one active-fence regression for each semantic class:

1. Web daemon start with `resume_continuous=True` -> no mutation, no spawn-side semantic rearm from the fence (`REFUSE`).
2. Immediate upgrade after a fence appears -> stale pre-upgrade objective cannot re-enable (`REFUSE`).
3. Scheduled upgrade request created before a later fence -> request cannot resurrect its stored objective (`REFUSE`).
4. `_rearm_operator_drain_for_resume` -> only an unfenced exact process-stop state may rearm; fenced state is untouched (`REFUSE`).
5. Operator decision “continue” against a newer fence -> decision remains accepted/durable but execution is pending reconciliation (`REFUSE` at enable boundary).
6. Standing STEER against a fence -> no direct standing CAS; enter supersession/reconcile path (`REFUSE` at shortcut).
7. Web/chat/config semantic stop against a fence -> fence cleared, disabled remains true (`CANCEL`).
8. Backend incompatibility disarm against a synthetic fenced disabled state -> fence preserved (`PRESERVE`).
9. Planner project_done/content-filter disarm against a synthetic fenced disabled state -> no fence erasure (`PRESERVE`).
10. Live Manager handoff recovery with exact strict receipt + exact mission stamp -> clear exact fence and enable once (`FINALIZE`).
11. Same finalization with changed fence/generation/receipt/mission stamp -> no mutation (`FINALIZE` fail-closed).

This matrix is stronger than testing only `ContinuousConfigState` serialization because it exercises the authority semantics at the actual production call sites.

## 6. Candidate refinement

`clean-os-g1-005` is now:

**first-class disabled handoff fence + explicit `PRESERVE/CANCEL/FINALIZE/REFUSE` authority action at every continuous writer + dedicated fence-begin primitive + strict no-fallback Manager reconcile receipt + canonical protected-state digest + pre-reserved mission ID + immutable creation stamp + exact idempotent durable Backlog insert + exact current-state process rearm + route-v4 classification only as a mismatch detector, not a commit receipt.**

No Argus mutation, live daemon fault injection, unauthorized state change, or production benchmark was performed. Findings are source-level behavior and an adaptation design at the exact public commit above.

## Exact continuation

1. Convert the 11 active-fence cases above into source-shaped regression pseudocode/tests, starting with `start_project_daemon`, immediate/scheduled upgrade, operator decision resume, and standing STEER because they currently contain direct enable shortcuts.
2. Turn the strict no-fallback replacement-reset receipt mint gate from the predecessor into executable built-in research, same-first-stage, and project-local-domain regressions; deliberately corrupt/miss the custom domain and prove no research fallback can mint authority.
3. Search all production `Backlog.update(...)` sites for intentional mutation of `id` or `ts`; only then protect `{id, ts, creation_stamp}` and specify `ensure_operator_priority_item_exact(...)`.
4. Add the real-Backlog final-continuous-replace failure recovery test: one physical target ID, stable immutable creation stamp, `inserted=False` on retry, fence survives ambiguous storage failure, and final enable occurs only after durable mission persistence plus strict Manager receipt.
5. Keep external/admin `PIPELINE_STATE` writer fencing/global JSON-state CAS as a separate candidate branch; do not broaden this result into a claim about all Argus state writers.
