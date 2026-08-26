# Open Source Systems Scan — pre-spawn semantic re-arm and stale scheduled-upgrade resurrection

Role: `open_source` clean exploration.
Frozen semantic control tuple: note main `1525e6d0512ce012c8b1db6e08216ae6253d7d74`, control revision 10, role config revision 5, role config blob `118f440957ba4654e804af902aa09a9224acca43`.
Public source: `lbx154/Argus@8c5a0e356c470ad4cbdc904a7fbe4de14af366cf` (main verified current before and after semantic inspection).
Invocation started at: `2026-08-26T20:00:24+09:00`.
Checkpointed at: `2026-08-26T20:07:35+09:00`.
Chronology valid: true.

## Result

The prior Web `/daemon/start` re-arm gap persists on current public main, and the remaining call-site audit found two stronger lifecycle defects plus useful positive controls:

1. `start_project_daemon(..., resume_continuous=True)` changes durable campaign semantics **before daemon admission and before spawn succeeds**. A start request can therefore re-enable a stopped/held `continuous.json` and then return `admission_required` or a startup error without having started an executor.
2. Durable scheduled upgrades carry a stale `resume_continuous` boolean + objective and, at completion, unconditionally write `continuous.enabled=true` before restart. An operator-decision `stop` that occurs after the upgrade request was captured does not cancel that request, so the later scheduled restart can resurrect the campaign.

No daemon, capability, external service, or public repository state was mutated. Findings are source-level reachability only.

## Evidence chain — pre-admission semantic mutation

Current `argus_skill/webapi/daemon_lifecycle.py::start_project_daemon` performs this sequence:

1. read daemon status and build config;
2. if `resume_continuous=True`, read `continuous.json`;
3. if disabled + objective + `done_reason.startswith("operator ")`, call `write_continuous_config(... enabled=True ...)`;
4. only after that, compute daemon limit / active count;
5. if over cap, return `admission_required` (or replace a selected idle daemon);
6. only later attempt `spawn_detached_daemon`.

Therefore semantic campaign state is committed before process admission. The command protocol's revision fencing serializes lifecycle commands, but it does not roll back handler side effects when the handler returns nonzero `rc`.

This is independent of the broad-prefix classification defect. Even a legitimately resumable process-stop state should not be durably re-armed merely because an executor start was requested when no slot was available or spawn later failed.

### UI propagation

The Web start endpoint always passes `resume_continuous=True`. Its persisted `daemon.admission.json` retains that flag. The TUI replacement picker carries `admission.resume_continuous` forward and calls `replaceDaemon(..., resumeContinuous)`; `replace_project_daemon` then forwards the same flag into `start_project_daemon`.

The replacement endpoint itself is conservative by default (`ReplaceDaemonIn.resume_continuous=false`; TUI client default false), but an admission generated from Web start intentionally propagates the original resume intent. That makes the pre-admission mutation particularly visible: the target campaign may already be marked enabled before the operator chooses a victim daemon to park.

## Evidence chain — stale scheduled-upgrade resurrection

Current `argus_skill/webapi/daemon_upgrade.py` persists an upgrade request containing:

- `expected_pid`,
- `source_root`,
- `resume_continuous` captured from the then-current `continuous.enabled`,
- `objective`,
- request reason/time.

The request does **not** bind the current continuous generation, done reason, Manager route identity/revision, or a later semantic stop decision.

When `_complete_scheduled_daemon_upgrade` reaches the restart phase and the saved request has `resume_continuous=true`, it does this before starting the executor:

`write_continuous_config(life_dir, enabled=True, objective=objective)`

and then calls `start_project_daemon(..., resume_continuous=True)`.

By contrast, `manager_pending_question._reconcile_campaign_after_decision(stopped=True)` records an explicit operator stop only by disabling continuous with `done_reason="operator chose to stop the campaign"`; that path does not call `request_daemon_stop` and does not remove a pending daemon-upgrade request.

So this sequence is reachable from source contracts:

1. campaign active; scheduled upgrade captures `resume_continuous=true` and objective A;
2. upgrade is still pending/draining;
3. operator resolves a pending decision with `stop`;
4. continuous becomes disabled with `operator chose to stop the campaign`;
5. scheduled upgrade later completes;
6. stale request writes `enabled=true` with objective A and restarts.

The operator's later semantic stop loses to an older process-maintenance request.

## Positive controls / scope limits

- Conversational PAUSE is better behaved for scheduled upgrades: it calls `request_daemon_stop`, and that primitive explicitly unlinks `daemon.upgrade-request.json` before requesting the process stop. `stop_daemon` also cancels the upgrade request unless `preserve_upgrade_request=True` is deliberately used by the upgrade machinery itself. Therefore the stale-upgrade resurrection finding is currently strongest for operator-decision stop and any other semantic disable path that does not cancel or supersede the request; do not generalize it to PAUSE.
- CLI `--resume` / `--continue` are session selectors, not campaign-resume authority. CLI campaign resumption is separately opt-in via `--resume-continuous`, which is passed as launch intent into `LifeWorkerConfig`.
- Daemon boot already has the stronger canonical primitive: `_rearm_operator_drain_for_resume` only re-arms exact `RESUMABLE_STOP_REASONS` (`operator drain-stop` and graceful SIGTERM/SIGINT stop). It does not use an `operator *` prefix.
- TUI `/resume` only switches the selected project/session; it does not itself re-arm continuous mode.
- Web `/continuous enabled=true` remains a positive control because it runs `manager_continuous_handoff()` before starting the daemon.
- No live exploit was executed, and no claim is made that a stale scheduled upgrade has occurred in production.

## Refined design invariant

**Process-control helpers should carry resume intent, not mutate semantic campaign state before process admission. Semantic re-arm belongs in one canonical gate after the process has been admitted and with current state revalidated.**

A minimal consolidation path is:

1. make Web/upgrade/start helpers pass `resume_continuous` as intent without writing `continuous.json` first;
2. use the existing boot-time exact `RESUMABLE_STOP_REASONS` gate (plus protected route reconciliation where required) as the only automatic re-arm point;
3. remove the scheduled-upgrade completion write that force-enables the stale captured objective; let restart consult current durable continuous state instead;
4. if the upgrade request needs to prove it is still current, bind it to continuous generation/request identity and reject/supersede on a later semantic stop rather than replaying a saved boolean;
5. preserve explicit semantic resume (`/continuous enabled=true`) as a separate Manager-mediated operation.

This also fixes the capacity/spawn failure atomicity problem: a failed process start no longer changes campaign semantics.

## Regression matrix

Add tests for:

- Web start at daemon cap + disabled `operator decision stop` state -> `admission_required` and continuous remains disabled;
- Web start spawn failure + resumable drain-stop -> no durable re-arm until canonical admitted boot/reconciliation succeeds;
- successful drain/SIGTERM restart -> still resumes through exact allowlist;
- operator authority hold / operator-decision stop -> daemon start never re-arms automatically;
- scheduled upgrade captured while active, then operator-decision stop before completion -> request must not re-enable/restart campaign semantics;
- scheduled upgrade with no intervening semantic change -> restart still resumes normally;
- PAUSE while upgrade pending -> existing upgrade cancellation remains a positive control;
- TUI/CLI session resume -> selection only, no campaign semantic change.

## Frontier / exact continuation

Frontier remains nonempty. Next:

1. finish the remaining process-resume callers around `upgrade_project_daemon` when the daemon is already absent, Web/TUI explicit start controls, and any recovery/keepalive helper that constructs `LifeWorkerConfig(resume_continuous=True)` directly;
2. determine whether any path still needs to resume a semantically disabled campaign outside the boot exact-reason gate;
3. extend the protected-route revision producer/consumer map so semantic resume after an intentional pause/decision is reconciled against current route identity, while process-only restart remains cheap;
4. keep the raw external/admin `PIPELINE_STATE` writer CAS/fencing matrix separate from this continuous-lifecycle issue.
