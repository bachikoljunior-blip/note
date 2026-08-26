# Open Source Systems Scan — continuous CAS caller matrix and independent route fence

Role: `open_source` clean exploration.
Frozen semantic control tuple: note main `31face47d7ee4b9b686ee3ae55fb9dbdeb877284`, control revision 10, role config revision 5, role config blob `118f440957ba4654e804af902aa09a9224acca43`.
Public source: `lbx154/Argus@8c5a0e356c470ad4cbdc904a7fbe4de14af366cf`, current public main verified unchanged during this pass.
Invocation started at: `2026-08-26T21:02:51+09:00`.
Checkpointed at: `2026-08-26T21:12:30+09:00`.
Chronology valid: true.

## New result

The repository already uses `compare_and_swap_continuous_config()` in the places where authors explicitly cared about stale semantic authority. The non-CAS writes implicated by the resume/upgrade findings are therefore architectural outliers rather than a missing system-wide primitive.

Observed production CAS users on current main include:

- daemon boot Manager handoff: snapshot `expected_state`, Manager route commit under pipeline lock in `before_write`, then continuous CAS; a concurrent generation change causes supersession instead of stale adoption;
- Manager front-door continuous handoff: reads expected continuous state and CASes the Manager-authored execution objective while holding the Manager pipeline lock;
- standing promotion in Web Manager dispatch: CASes from the observed current continuous state;
- Planner project-done / permanent content-filter stop: CASes the current generation to disabled;
- daemon run-loop project-done path: additionally requires the daemon's adopted generation to still equal current generation before CASing disabled.

This is strong internal precedent for changing process lifecycle re-arm paths to the existing CAS API rather than adding a new continuous-state protocol.

## Direct non-CAS write caller classification

Repository-wide current-main `write_continuous_config()` production callers reduce to these categories:

### Process-maintenance / lifecycle — should not overwrite newer semantics

- `webapi/daemon_lifecycle.py`: raw start helper pre-rearms a disabled objective based on broad `done_reason.startswith("operator ")`; this is before admission/spawn.
- `webapi/daemon_upgrade.py`: immediate and scheduled upgrade re-enable from captured state/request; offline upgrade calls start with `resume_continuous=True`.
- `daemon/_life_worker_identity.py`: exact-reason boot re-arm is semantically correct in classification but commits a stale snapshot with unconditional write.

These are the clearest candidates for CAS or intent-only refactoring.

### Semantic-authority projection — should CAS its observed `before`

- `webapi/manager_pending_question.py::_reconcile_campaign_after_decision`: operator stop/resume decision reads current continuous state, then unconditionally writes disable/enable. This is under the Web Manager's per-session `threading.RLock`, but daemon commands use a separate cross-process `daemon.command-exec.lock`; the Manager lock does not serialize process maintenance writers. Therefore generation CAS remains necessary even if each subsystem is internally serialized.

### Defensive/derived state

- `daemon/_life_worker_boot.py` has a boot provider guard that can disable an enabled configuration when `continuous_mode_error(...)` says it is invalid. It is safety-oriented rather than authority-creating, but it is still a read-derived write and should be evaluated for stale generation before replacement.
- `apps/_life_actions.py` refuses manual `/config continuous=true` and directs the operator to the Manager-authored `/continuous start <objective>` path; its ordinary control path therefore acts as a positive control for separating semantic enable from generic configuration.

`daemon/state.py` itself is the primitive definition and is not a caller-policy case.

## Command serialization does not solve semantic concurrency

`daemon/commands.py` has a strong durable idempotent command log and a cross-process `daemon.command-exec.lock`. Web `/daemon/start|stop|replace|upgrade` handlers execute under that lock, so two daemon lifecycle commands are serialized.

However, Manager decision resolution is protected by a separate per-session in-process `threading.RLock` in `webapi/manager_state.py`. It does not acquire the daemon command execution lock. Therefore a daemon maintenance command and an operator-decision semantic projection can interleave at `continuous.json`. The file's own generation CAS is the appropriate shared boundary.

## Fence B is independently necessary — direct source proof

The protected route fence is not redundant with continuous generation.

Current Manager route commit code (`manager/_vertical_ops.py`) persists `vertical`, `domain`, `research_target_level`, `research_direction_mode`, `workflow_mode`, and `target_venue`, and can reset stage for a new intent. Current bounded handoff runs the Manager commit under the Manager pipeline lock and persists the bounded task, but it does not update `continuous.json` merely because those route fields changed.

Meanwhile current `manager-handoff.json` resume identity contains objective hash, vertical, domain, continuous generation, and intent id; it does not bind workflow mode, target venue, current stage, research target/direction, or a protected pipeline digest/revision. Its match accepts a handoff generation less than or equal to current continuous generation.

Therefore a bounded handoff can legitimately change protected route fields while `continuous.generation` remains unchanged. A later resume can still satisfy the continuous-state fence yet be semantically stale relative to route authority. This is direct public-source proof that the proposed model requires two orthogonal generations:

- **continuous generation** for enable/disable/objective/process lifecycle semantics;
- **protected route/pipeline revision or digest** for Manager execution topology/authority semantics.

## Minimal candidate patch shape

1. Replace stale lifecycle read→write with existing continuous CAS, or better move process resume to intent-only and let boot perform exact-reason CAS.
2. Scheduled upgrade captures expected continuous state/generation and cannot resurrect if any newer semantic state appears.
3. Operator-decision reconcile CASes the `before` snapshot; a failed CAS means decision remains durably resolved but semantic projection is retried/reconciled against newer state rather than overwriting it.
4. Preserve existing command execution lock for lifecycle command idempotence; do not use it as a substitute for continuous CAS.
5. Add a protected Manager route revision/digest separately; increment it on route/stage-authority changes including bounded handoffs, and bind resume/handoff identities and downstream repair authorization to it where execution authority crosses a pause/restart.

## Exact continuation

Frontier remains nonempty. Next:

1. inspect the remaining CAS callers (`manager/front_door.py`, `webapi/manager_dispatch.py`, Planner verdict) in exact transaction order to extract a common helper pattern for decision+continuous-state commit;
2. design the smallest retry semantics for operator-decision resolution when its semantic projection CAS loses to a newer generation, preserving idempotent decision receipt without stale re-arm;
3. inspect upgrade and raw start tests for current expected behavior so a candidate patch can preserve process restart UX while closing resurrection;
4. map every route-authority mutation that should advance the new protected route revision, including vertical/workflow/venue/stage/reset/rollback, while avoiding descriptor-only/evidence changes;
5. continue the separate external/admin `PIPELINE_STATE` writer fencing branch.
