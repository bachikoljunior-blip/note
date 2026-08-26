# Open Source Systems Scan — Web daemon start can re-arm operator stop/hold states

Role: `open_source` clean exploration.
Frozen semantic control tuple: note main `e1cfdf0b319c2ca85d83995f8f1774a8f9bd2e48`, control revision 10, role config revision 5, role config blob `118f440957ba4654e804af902aa09a9224acca43`.
Public source: `lbx154/Argus@16bb128992ea9d0c11b5bbca7a4f1d549dea84dd` (main verified current before semantic work).
Invocation started at: `2026-08-26T18:58:29+09:00`.

## Result

A new, narrower live re-arm gap exists independently of the previously identified incomplete Manager-route identity: the Web daemon start path treats **every** disabled continuous state whose `done_reason` starts with `"operator "` as resumable process state, even though the daemon's canonical resume helper and regression tests deliberately distinguish process-stop reasons from operator authority/terminal-work reasons.

No live daemon, external service, capability, or production state was modified. This is source-level reachability against the verified public commit.

## Evidence chain

1. `daemon/state.py` defines exactly two process-level resumable reasons in `RESUMABLE_STOP_REASONS`: `operator drain-stop` and the graceful SIGTERM/SIGINT stop. Its module comment explicitly says work-level reasons such as planner completion or an operator hold must stay authoritative and must not be resumed merely because the daemon restarts.
2. `_rearm_operator_drain_for_resume()` follows that contract exactly: it re-enables only when `state.done_reason in RESUMABLE_STOP_REASONS`. The public regression suite includes `test_resume_continuous_preserves_operator_authority_hold`, which writes `done_reason="operator authority hold: new scope is not authorized"` and asserts it remains disabled.
3. The Web start endpoint `/api/projects/{sid}/daemon/start` always calls `start_project_daemon(..., resume_continuous=True)`.
4. `start_project_daemon()` uses a broader predicate. If continuous is disabled, has a preserved objective, and `done_reason.strip().lower().startswith("operator ")`, it directly calls `write_continuous_config(..., enabled=True, objective=...)` before spawning the daemon.
5. Therefore a work-level operator reason is enough to pass the Web start re-arm predicate even when the canonical daemon resume helper would reject it.

## Concrete reachable states

### Operator decision stop

`manager_pending_question._reconcile_campaign_after_decision(stopped=True)` disables continuous with:

`done_reason="operator chose to stop the campaign"`.

That reason matches the Web start prefix test. Starting the executor later through the ordinary Web daemon-start endpoint can therefore turn that stopped campaign back on before boot. This is stronger than a generic route mismatch: the operator explicitly chose the `stop` outcome, yet a later process-start action can reverse the continuous-state decision.

### Operator authority hold

The public resume regression treats `operator authority hold: new scope is not authorized` as intentionally non-resumable. It also matches the Web start prefix predicate. If such a state reaches `continuous.json`, Web daemon start can re-arm it even though `_rearm_operator_drain_for_resume()` deliberately preserves it.

### Operator PAUSE

PAUSE writes `done_reason="operator pause"` and tells the operator that the objective/backlog are preserved until they explicitly resume. Web daemon start also matches this reason. This may be intended if the product defines "start daemon" as the explicit campaign resume action, but that intent is not sufficient to justify the same prefix rule for terminal/authority operator reasons.

## Positive controls

- `/api/projects/{sid}/continuous` with `enabled=true` is different: `set_continuous()` calls `manager_continuous_handoff()` before enabling the campaign, so it already goes through the semantic Manager handoff boundary.
- `_rearm_operator_drain_for_resume()` already has the correct process-stop allowlist and a regression proving an operator authority hold stays disabled.
- Continuous state writes themselves are lock-protected, generation-incremented, file+directory-fsynced atomic replacements. The defect is semantic classification of **which disabled states are resumable**, not torn-write durability.

## Refined invariant

Do not derive campaign resumability from a string prefix such as `done_reason.startswith("operator ")`.

Separate three operations:

1. **restart executor only** — must not change campaign enabled/disabled semantics;
2. **resume after process-level drain/SIGTERM** — may automatically re-arm only exact `RESUMABLE_STOP_REASONS` and then pass the existing boot Manager-handoff/reconciliation gate;
3. **resume a paused/stopped/held campaign** — must be an explicit semantic resume operation that validates the preserved objective against the current protected route revision and goes through `reconcile_or_rearm_continuous(...)` / Manager reconciliation when route state changed.

An operator-decision `stop` or authority hold must never be converted back to enabled merely because the daemon process is started.

## Regression matrix

Add end-to-end tests around `start_project_daemon(resume_continuous=True)`:

- drain-stop -> re-arms (positive control);
- graceful process stop -> re-arms (positive control);
- planner-declared completion -> remains disabled;
- operator authority hold -> remains disabled;
- operator-decision stop (`operator chose to stop the campaign`) -> remains disabled;
- operator PAUSE -> behavior must be explicit in the API contract: either remain disabled on executor start, or route through an explicit semantic resume function rather than the generic process-start helper;
- unchanged-route semantic resume -> cheap re-arm allowed;
- changed-route semantic resume -> accepted operator intent preserved, but execution remains disabled until Manager route reconciliation completes.

## Inventory progress

Direct/indirect false->true promotion classes now classified:

- Web `/continuous enabled=true`: Manager-authored handoff first — semantic-safe entry path.
- Standing STEER promotion: resident-daemon direct CAS; no fresh Manager route reconciliation — previous finding.
- Operator-decision resolution/replay: resident-daemon direct re-arm; no fresh Manager route reconciliation — previous finding.
- Web `/daemon/start`: process-start helper can directly re-arm any `operator *` done reason — new finding; then boot uses the existing Manager-handoff fast path.
- Boot `_rearm_operator_drain_for_resume`: exact process-stop allowlist — positive control.
- Upgrade/scheduled-upgrade: explicitly restores enabled state and then starts with `resume_continuous`; still converges on the same boot handoff gate and must inherit the same exact-reason semantics.
- `/config continuous=true`: current parser path directs the user to `/continuous start <objective>` instead of enabling directly; not a live bypass in the inspected path.

## Exact continuation

Finish the remaining process-control call-site audit: `replace_project_daemon`, CLI/TUI resume, scheduled upgrade/recovery, process-stop restart and any admission/replacement helper that calls `start_project_daemon(resume_continuous=True)`. Determine which paths should mean executor-only start versus semantic campaign resume. Then define one reusable `reconcile_or_rearm_continuous(expected_route_revision, objective, resume_reason)` boundary with an exact process-stop reason allowlist, and combine it with the protected route-revision producer/consumer map already in the frontier. Keep raw external/admin `PIPELINE_STATE` writers in the separate CAS/fencing matrix.

Frontier remains nonempty.