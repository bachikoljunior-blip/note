# Open Source Systems Scan — source-shaped fence regressions and Backlog immutability audit

Invocation started: 2026-08-27T14:59:53+09:00
Checkpointed: 2026-08-27T15:05:42+09:00

Frozen semantic tuple: `note@4caeefd9e74bda9648160063ce3a9e50b81cbb27 / control 11 / open_source config 5` (`DESIRED_STATE` blob `bf7b8c7f6971c0ec2f3fa7a8d53dca1f88ac50a3`, role-config blob `118f440957ba4654e804af902aa09a9224acca43`). The second SHA-only note-main check matched before the first substantive semantic read. Note main later advanced to `02c8fbca796b123ea22969168476cda2b61800c5`; per the semantic-freeze contract, no newer control/config was adopted or used to reinterpret this invocation.

Public source frozen for this run: `lbx154/Argus@33da786bbc6787a2eeb63a5f492498eae87c78c7`, verified current `main` by SHA-only Git-ref lookup. Only own clean state and public source were used. Own feedback path was absent (404); no feedback semantics were used.

## 1. The active-fence regressions can now be placed on exact production shortcuts

The predecessor classified continuous writers as `PRESERVE / CANCEL / FINALIZE / REFUSE`. This run converted the highest-risk cases into source-shaped assertions at the exact public call sites.

### 1.1 Web daemon start — process start must not become semantic resume

Current source: `argus_skill/webapi/daemon_lifecycle.py::start_project_daemon`.

Observed order when `resume_continuous=True`:

1. read current continuous state;
2. if disabled, objective nonempty, and `done_reason.lower().startswith("operator ")`, directly call `write_continuous_config(enabled=True, objective=...)`;
3. only after that, compute daemon limit/admission and potentially return `admission_required`;
4. only later attempt daemon spawn.

Therefore a source-shaped active-fence regression should set a disabled fenced state with a nonempty objective, request daemon start with resume intent, force admission refusal, and assert all of:

- continuous bytes/generation/fence remain unchanged;
- no semantic enable occurs before admission/spawn;
- the returned result identifies reconciliation/resume as pending rather than silently consuming the fence;
- no later process-only retry may clear or enable through the fence.

This is stronger than checking the eventual daemon status: the invariant is that **executor admission failure cannot change campaign authority**.

### 1.2 Immediate upgrade — pre-stop snapshot must not be restored

Current source: `argus_skill/webapi/daemon_upgrade.py::upgrade_project_daemon`.

The function reads `continuous` before draining/stopping the daemon. After stop succeeds, it reuses that old snapshot: if `continuous.enabled` was true, it writes the saved objective back as `enabled=True`, then starts the daemon.

Regression shape:

- old snapshot A is enabled;
- during stop/drain, current durable continuous state becomes a newer fenced/semantically stopped generation C;
- upgrade proceeds after stop;
- assert C is unchanged and A is never restored.

The fix contract should use only the **current disabled process-stop record under exact generation CAS**, never a pre-stop objective copy.

### 1.3 Scheduled upgrade — persisted request snapshot must not resurrect stale authority

Current source: `_write_daemon_upgrade_request` persists `resume_continuous` and `objective`; `_complete_scheduled_daemon_upgrade` later replays those values with a direct `write_continuous_config(enabled=True, objective=objective)` before restart.

Regression shape:

- request is created while A is enabled;
- before completion, operator stop/new handoff fence produces newer state C;
- scheduled completion reloads its old request;
- assert it may restart the process if allowed, but it must not restore A or clear C.

A request-file snapshot is restart intent/history, not current campaign authority.

### 1.4 Operator decision “continue” — accept the human decision without blindly resuming execution

Current source: `argus_skill/webapi/manager_pending_question.py::_reconcile_campaign_after_decision`.

For `stopped=False`, if current state has an objective and is disabled, it directly writes that objective as enabled. Separately, `_resolved_decision_replay` intentionally preserves idempotent acceptance of an already-applied human choice.

Regression shape:

- decision card is valid and should remain accepted/durable;
- after the card was issued, a newer handoff fence/current route state exists;
- resolving/replaying “continue” must return the decision as accepted while execution remains disabled and pending reconciliation;
- no new continuation item or decision duplicate is created on exact replay.

This separates **human-decision validity** from **current-route execution authority**.

### 1.5 Standing STEER — directive may persist, direct standing promotion must not bypass the fence

Current source: `argus_skill/webapi/manager_dispatch.py` standing STEER path.

It persists the active Manager directive and then directly calls `compare_and_swap_continuous_config(expected=current, enabled=True, objective=standing_objective, open_ended=True)`.

Regression shape:

- active fence exists in current expected state;
- new standing STEER is semantically valid and its directive may be recorded;
- direct standing promotion must return a distinct pending/supersession-reconcile outcome, not enable through the old fence;
- only the common Manager reconciliation boundary may replace/finalize that fence.

### 1.6 Explicit semantic stop — newer operator authority cancels the fence

Current source: `_handle_pause_control` calls `disable_continuous_config(done_reason="operator pause")`, then requests active-item abort and daemon stop. Web/config stop surfaces have the same semantic class.

Regression shape:

- begin from an active disabled handoff fence;
- explicit semantic stop performs `CANCEL` on the exact fence;
- resulting continuous state remains disabled with fence cleared and objective/backlog preserved according to stop policy;
- later process start/upgrade must not resurrect the cancelled target.

### 1.7 Machine safety disarm — preserve, do not reinterpret, a fence

Current source example: content-filter handling in `_planning_cycle_verdict.py` CAS-disables an enabled campaign. Backend incompatibility and planner terminal disarms are the same machine-safety class.

Synthetic active-fence regression should assert a defensive disable path never clears or finalizes a fence. With the invariant `fence != None => enabled == False`, this is normally a no-op/preserve case.

### 1.8 Manager finalization — exact receipt + exact mission are both required

Only live/boot Manager handoff recovery may `FINALIZE`. The regression must require all of:

- exact expected continuous generation;
- exact expected fence identity;
- strict no-fallback Manager reconciliation receipt bound to current protected-state canonical digest;
- exact pre-reserved target mission ID with matching immutable creation stamp;
- target mission durably persisted;
- then, and only then, one CAS clears the fence and enables the target.

Changing any one of generation/fence/receipt/mission stamp must leave continuous state unchanged.

## 2. Full observed production `Backlog.update(...)` audit: no caller intentionally mutates `id` or `ts`

At the pinned Argus source, code search identified the production files that call `Backlog.update(...)`. This run inspected every observed non-test caller returned by that search:

- `life/supervisor/_core.py`
- `life/supervisor/_mission_execution_settlement.py`
- `life/supervisor/_planning_cycle_verdict.py`
- `life/supervisor/_mission_execution_runtime.py`
- `life/supervisor/_planning_cycle_enqueue.py`
- `apps/_life_actions.py`
- `life/chat/router.py`
- `manager/dispatch.py`
- `life/supervisor/_mission_execution.py`
- `life/supervisor/backlog_guard.py`
- `life/supervisor/_planning_cycle.py`

Observed updates cover status, started/finished timestamps, running owner, errors, pending question/operator card, Manager decision, outcome, title/objective, replan counters, and related mutable mission state. **None of these observed production call sites intentionally passes `id=` or `ts=`.**

This matters because current `Backlog.update` generically executes `setattr` for any existing dataclass field. It can therefore mutate `id` or `ts` today, and would also mutate a future `creation_stamp` unless explicitly protected, even though no observed production caller needs that capability.

Source-scoped hardening at this exact public SHA is therefore compatible with the observed production calls:

```text
IMMUTABLE_BACKLOG_FIELDS = {"id", "ts", "creation_stamp"}
Backlog.update(...): reject any attempted update containing one of those fields
```

Do not broaden this into a compatibility claim for unobserved third-party callers or later commits without repeating the call-site audit.

## 3. `Backlog.add` is the duplicate-ID hole; the surrounding APIs already show the intended invariant

Current `Backlog.add(item)` locks, loads, blindly appends, validates DAG cycles, and rewrites. It does not check whether `item.id` already exists. By contrast:

- `add_many` rejects duplicate IDs inside the new batch and against existing rows;
- plan revision rejects replacement IDs that already exist;
- `Backlog.update(item_id, ...)` stops after the first matching row.

Therefore allowing duplicate IDs through `add` makes later state updates ambiguous. The narrow baseline hardening should make ordinary `add` reject an existing ID.

Handoff recovery needs a separate idempotent primitive rather than weakening that rule:

```text
ensure_operator_priority_item_exact(pre_reserved_id, creation_stamp, creation_fields)
```

under one `Backlog._locked()` transaction:

1. load rows and detect duplicate occurrences of the target ID; more than one => fail closed;
2. if one row exists: matching immutable creation stamp => return `{item, inserted:false}`; missing/mismatched stamp => fail closed;
3. if absent: compute operator priority from the **same locked current rows**;
4. generate initial timestamp once, persist immutable stamp, validate DAG, durable-rewrite once;
5. return `{item, inserted:true}` so `life.planner.task_added` is emitted only on the first insert.

## 4. New source confirmation: operator-priority calculation is currently TOCTOU

`manager/dispatch.py::enqueue_mission` currently implements `_persist_operator_priority_item` as:

1. `pending = mem.backlog.pending()`;
2. compute `head_priority = min(...)`;
3. create item with `priority=min(head_priority - 1, -1)`;
4. separately call `mem.backlog.add(item)`.

The pending read and add do not share one Backlog transaction, so another writer can change queue priority/order between them. The proposed exact-insert primitive should therefore own **priority calculation as well as duplicate/idempotency checking**; wrapping only `add` with a duplicate check does not close this TOCTOU.

The same continuous path also has a fallback that calls `_persist_operator_priority_item` after Manager handoff if the callback did not populate its local `persisted` holder. Stable target ID + exact idempotent insert is consequently required even before adding crash recovery.

## 5. Source-shaped regression pseudocode

The implementation can remain small if tests exercise authority semantics at production entry points instead of only testing state serialization.

```text
# daemon start
state = disabled_fence(A_to_B)
force_daemon_admission_refusal()
start_project_daemon(resume_continuous=True)
assert continuous == state

# stale scheduled upgrade
request = upgrade_request(snapshot=A_enabled)
current = newer_disabled_fence(C)
complete_scheduled_upgrade(request)
assert continuous == current

# decision continue
record_valid_operator_decision()
current = newer_disabled_fence(C)
result = reconcile_decision(stopped=False)
assert decision_is_accepted(result)
assert continuous == current

# standing steer
current = disabled_fence(A_to_B)
apply_standing_steer(C)
assert directive_persisted(C)
assert continuous remains disabled/pending_reconcile

# exact mission insertion
r1 = ensure_operator_priority_item_exact(id=X, stamp=S, ...)
r2 = ensure_operator_priority_item_exact(id=X, stamp=S, ...)
assert r1.inserted is True
assert r2.inserted is False
assert exactly_one_backlog_row(id=X)
assert exactly_one_task_added_event(id=X)

# conflicting retry
ensure_operator_priority_item_exact(id=X, stamp=S2, ...)
=> fail closed; no write
```

The highest-value integration fault test remains: use the existing real-Backlog Manager handoff harness, let route reconciliation and exact mission insert succeed, inject failure/ambiguity at the final continuous-state replacement, then run recovery twice. Required invariant: one physical target row, one task-added event, fence remains disabled until strict receipt + exact durable mission are revalidated, and final enable happens once.

## 6. Candidate refinement

`clean-os-g1-005` is now:

**first-class disabled handoff fence + explicit `PRESERVE/CANCEL/FINALIZE/REFUSE` at production continuous writers + source-shaped shortcut regressions + strict no-fallback Manager postcondition receipt + pre-reserved target mission ID + immutable `{id, ts, creation_stamp}` protection + ordinary-add global ID uniqueness + atomic operator-priority exact insert (including priority calculation) + durable real-Backlog recovery + current-state-only process rearm.**

No Argus mutation, live daemon fault injection, unauthorized state change, or production benchmark was performed. Findings are source-level behavior at the pinned public commit and an adaptation/test design.

## Exact continuation

1. Convert the strict no-fallback Manager receipt mint gate into three executable source-shaped cases: built-in research replacement, same-first-stage replacement, and project-local/custom-domain replacement. Deliberately corrupt/remove the custom domain and prove authority cannot be minted via research fallback.
2. Trace every `ContinuousConfigState` constructor/reader/writer/reserve/CAS comparison and specify the backward-compatible first-class `handoff_fence` field plus explicit `PRESERVE/CANCEL/FINALIZE/REFUSE` call signatures. Preserve the invariant `fence != None => enabled == False` across legacy callers.
3. Turn the real-Backlog final-continuous-replace ambiguity test into exact test scaffolding using the existing Manager handoff test harness and continuous-storage fault injection; verify `inserted=False` on recovery and no duplicate task-added event.
4. Recheck the `Backlog.update` caller audit whenever public Argus head changes before implementing immutable-field protection; this run's compatibility result is scoped only to `33da786bbc6787a2eeb63a5f492498eae87c78c7`.
5. Keep external/admin `PIPELINE_STATE` whole-object writer fencing and global JSON-state CAS as a separate candidate branch; do not broaden this result into a claim about all Argus state writers.
