# Open Source Systems Scan — handoff fence idempotency + current-head revalidation

Invocation started: 2026-08-27T03:01:56+09:00
Checkpointed: 2026-08-27T03:06:37.065729+09:00

Frozen semantic tuple for this invocation:
- note main SHA: `1ee41254fe0356508bd2c3f19b9631fd192c109b`
- sanitized control revision: `10`
- open_source config revision: `5`
- open_source config blob: `118f440957ba4654e804af902aa09a9224acca43`

Independence: own clean state + public sources only. No O/O-derived state, other-worker state/config, downstream semantics, legacy/pre-independence research, aggregate execution ledger, or other-role receipts/configs were used. The selected control/config tuple was frozen before the first role-local semantic read.

Public source revalidation:
- `lbx154/Argus` current public `main` observed at `67361617e1967830cd62bce990ff90012797645e`.
- Relative to the previous source head `658f8310254ae70f61614c6adb88c6430289597b`, current main is 5 commits ahead.
- The compare does not modify the continuous/restart/handoff files central to this branch (`argus_skill/manager/front_door.py`, `argus_skill/manager/dispatch.py`, `argus_skill/daemon/state.py`, `argus_skill/daemon/_life_worker_identity.py`, or daemon-upgrade lifecycle files). The findings below therefore remain source-current at the observed head.

## 1. Post-route side effects are not equally dangerous; the current code lets us classify them

Current `manager_continuous_handoff()` performs its `before_write` callback in this order:

1. `PreparedManagerHandoff.commit()` → `Manager.commit_vertical_decision(...)` changes protected route/stage state; `_record_goal_contract(...)` is fail-soft and does not propagate recording errors.
2. If this is a true replacement, `Backlog.supersede_pending_for_replacement(...)` retires pending/non-running old work.
3. `_maybe_name_session(..., replacing=True)` updates the display name.
4. Optional `persist(...)` writes the newly routed mission/work item.
5. Only after the callback returns does the continuous writer replace `continuous.json`.

The post-route operations have different failure/idempotency properties:

- **Backlog supersession can propagate a failure** from its lock/load/save path after route mutation. On a successful retry it is naturally idempotent at the semantic level because already-terminal `superseded` rows are skipped.
- **Session rename is fail-soft**: `_maybe_name_session()` catches every exception and returns an empty result, so it cannot abort the handoff after route mutation. Repeating the same rename is cosmetic.
- **The production continuous persist path can propagate**: `manager.dispatch.enqueue_mission()` passes `_persist_operator_priority_item`, which calls `mem.backlog.add(item)` without catching that write. Its event-log append is separately fail-soft.
- **The final continuous replace can still fail after all callback side effects committed**, preserving the already-known cross-object partial-precommit hazard.

This narrows the recovery problem: session naming does not need transaction machinery; supersession is already replay-safe enough; the new mission persist is the important non-idempotent side effect.

## 2. New concrete recovery defect: the production persist primitive is not replay-idempotent

`Backlog.add()` currently takes the backlog lock, loads all items, blindly `append(item)`, validates dependency cycles, and rewrites the file. It does **not** reject or coalesce an existing item with the same id. This contrasts with the batch-add path, which explicitly rejects duplicate ids.

`BacklogItem.new(item_id=root_task_id, ...)` preserves a caller-supplied stable id; if none is supplied it generates a fresh id.

Therefore a recovery implementation that simply replays `_persist_operator_priority_item()` after a route/persist success followed by final continuous-state failure is unsafe:

- with the same stable `root_task_id`, the current `Backlog.add()` can append a second row with the same id;
- with a new id, it can create a second semantic copy of the same operator-priority mission.

This is an adaptation/recovery concern derived from current source. It is not a claim that current Argus automatically retries this exact failed handoff today or that duplicate rows have occurred in production.

## 3. Existing regression coverage proves the success ordering but misses failure/recovery semantics

`tests/manager/test_pipeline_yield.py::test_continuous_handoff_requests_boundary_yield` already asserts an important ordering: inside `persist(...)`, the old backlog rows are already `superseded`, and after success the continuous objective is updated.

What it does not test is the high-value failure boundary:

- route commit succeeds;
- supersession and/or new-item persist succeeds;
- final continuous replacement fails;
- recovery/retry must not duplicate the persisted mission and must never expose `old objective A enabled + new route B`.

This is now the most direct regression target for the candidate.

## 4. Refined two-CAS repair: fence first, then require idempotent durable side effects

The safe handoff needs both **fail-closed execution fencing** and **replay-safe side effects**.

Proposed sequence:

1. Exact CAS `A enabled@g -> handoff fence disabled@g+1` **before every route/backlog/persist side effect**.
2. Under the existing Manager pipeline lock, reconcile/commit route B.
3. Retire old pending backlog work (already semantically idempotent).
4. Persist the new operator-priority mission through an idempotent primitive, not raw `Backlog.add()`.
5. Rename the session best-effort.
6. Exact CAS `fence@g+1 -> B enabled@g+2` only after required durable side effects are established.

A minimal mission-persist contract is `ensure_backlog_item_exact(item_id, payload_digest, item)`:

- no existing id → append exactly once;
- existing id with identical canonical payload digest → return the existing row as success;
- existing id with different payload → fail closed as an identity collision;
- all checks and write occur under the existing backlog lock.

This is narrower than making all backlog writes globally transactional and gives fence recovery an exact durable fact to inspect.

## 5. Fence recovery should reconcile observed durable facts, not blindly replay a callback cursor

A disabled handoff fence is a semantic reconciliation state, not a process-stop reason. On restart/retry:

- If protected route and exact mission id+payload already match B, finalize only after revalidation; do not re-add the mission.
- If route is still A and the mission is absent, a fresh/validated Manager reconciliation may perform the side effects.
- If route is B but the mission is absent, create it through `ensure_backlog_item_exact` before enabling B.
- If route/misson identity is ambiguous or conflicts, remain disabled and rerun Manager reconciliation rather than guessing.
- Never auto-rearm a fence through the drain/SIGTERM process-only allowlist.

This avoids maintaining a fragile multi-file "side-effect cursor" whose own update could race the objects it describes.

## 6. Exact-state process rearm remains the complementary primitive

Current public main still has `_rearm_operator_drain_for_resume()` reading a previously obtained disabled `ContinuousConfigState` and then performing unconditional `write_continuous_config(enabled=True, objective=state.objective)` when the reason is in the exact process-stop allowlist.

The narrow replacement remains:

`rearm_process_stop(expected_disabled)`

- caller supplies the exact disabled state it observed, not a copied objective;
- require `done_reason in RESUMABLE_STOP_REASONS` and a nonempty objective;
- perform exact full-state/generation CAS to enabled with the same objective/open-ended semantics;
- CAS miss means reread/adopt current state and never restore the stale snapshot.

Boot, immediate upgrade, replacement, scheduled upgrade and Web start should all converge on this process-only boundary rather than carrying semantic objective snapshots through lifecycle operations.

## 7. Candidate refinement

`clean-os-g1-005` is now best stated as:

> Preserve Argus's existing outer Manager lock and deterministic evidence gates, but make continuous Manager replacement a two-CAS disabled handoff fence; make every required post-fence side effect exact/idempotent (especially mission creation); make process restart use exact-state rearm only; and bind semantic resume/reconciliation to a canonical protected-route fingerprint rather than old objective+vertical+domain identity alone.

This remains an unimplemented adaptation proposal, not a measured improvement.

## High-value regression additions

1. Route B + supersession + mission persist succeed, final continuous replace fails: durable state must be disabled fence, and exactly one mission row may exist.
2. Recover that fence twice: mission row count/identity stays unchanged; second recovery is a no-op/finalization, not a duplicate enqueue.
3. Existing same mission id but different payload digest: recovery fails closed and does not enable B.
4. Supersession succeeds then later step fails: retry does not change already-superseded rows again except harmless timestamps must not churn if already terminal.
5. Session rename failure never blocks finalization when all authoritative side effects are valid.
6. Boot process-rearm reads drain record g, concurrent semantic command produces g+1, rearm CAS misses and preserves g+1 byte-for-byte.
7. Scheduled/immediate upgrade carries process intent only; no saved objective may overwrite a newer semantic command.

## Scope and uncertainty

- No live exploit was executed and no upstream Argus repository was mutated.
- Current-head source comparison was performed before these conclusions.
- `Backlog.add()` replay risk is a property of the current primitive; whether a particular front-end retry reuses the same `root_task_id` depends on that caller. The recovery design must be safe under either same-id or new-id replay.
- The two-CAS/idempotent-persist design has not been implemented or benchmarked.

## Exact continuation

1. Inspect all direct `Backlog.add()` uses in continuous/Manager replacement paths and decide whether the minimal repair should be a new `ensure_backlog_item_exact` primitive or a narrower handoff-specific idempotency record.
2. Specify a source-level regression using the real `Backlog` plus an injected post-callback continuous replace failure, then a recovery attempt, asserting one exact mission and no executable old-objective/new-route mix.
3. Finish the canonical protected-route fingerprint v4 helper/migration test plan and bind fence finalization/semantic resume to it.
4. Map boot, immediate upgrade, replacement, scheduled upgrade and Web start onto one exact-state `reconcile_or_rearm` API; prove no process helper writes a caller-copied objective.
5. Keep external/admin `PIPELINE_STATE` writer fencing as a separate branch; do not conflate it with continuous/restart authority.
