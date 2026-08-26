# Open Source Systems Scan — continuous-generation CAS gap and offline-upgrade re-arm

Role: `open_source` clean exploration.
Frozen semantic control tuple: note main `31face47d7ee4b9b686ee3ae55fb9dbdeb877284`, control revision 10, role config revision 5, role config blob `118f440957ba4654e804af902aa09a9224acca43`.
Public source: `lbx154/Argus@8c5a0e356c470ad4cbdc904a7fbe4de14af366cf` (main verified unchanged before and after semantic inspection).
Invocation started at: `2026-08-26T21:02:51+09:00`.
Checkpointed at: `2026-08-26T21:06:59+09:00`.
Chronology valid: true.

## Result

The continuous-lifecycle problem can be narrowed substantially because Argus already has the exact durable fencing primitive needed for this layer: `continuous.json` carries a monotonically increasing `generation`, all ordinary writes take the cross-process continuous lock and increment that generation, and `compare_and_swap_continuous_config()` atomically rejects a stale expected state while using fsync + atomic replace + parent-directory fsync. The process-resume paths audited here do not consistently use it.

Two concrete gaps remain on current public main:

1. `upgrade_project_daemon()` treats an *absent* daemon as a start request and calls `start_project_daemon(..., resume_continuous=True)`. Because the start helper still re-arms any disabled objective whose `done_reason` merely starts with `"operator "`, an operator maintenance action named “upgrade” can semantically resurrect an intentionally stopped/held campaign even though there is no daemon to upgrade.
2. The supposedly canonical boot-time exact-reason re-arm (`_rearm_operator_drain_for_resume`) correctly limits automatic resume to `RESUMABLE_STOP_REASONS`, but it still performs a stale read → unconditional `write_continuous_config()` sequence. If a newer semantic stop/hold lands after the boot read and before this write, the re-arm can overwrite that newer decision. Existing resume-gate tests exercise reason classification but not this interleaving.

No daemon, repository, capability, external service, or campaign state was mutated. Findings are source-level reachability only.

## Production start/resume call-site classification

Repository-wide `start_project_daemon(` search on current main yields five production modules:

- `webapi/routes/daemon.py`: raw `/daemon/start` always requests `resume_continuous=True`; `/continuous enabled=true` first performs the Manager-mediated semantic handoff and then starts with resume intent; `/daemon/replace` forwards an explicit body flag; `/daemon/upgrade` delegates to upgrade logic.
- `webapi/daemon_upgrade.py`: immediate/scheduled upgrade paths plus the offline-daemon shortcut discussed above.
- `webapi/daemon_lifecycle.py`: the implementation itself and replacement/reclaim forwarding.
- `webapi/routes/manager.py`: Manager message/task flow passes `resume_continuous=bool(result.get("continuous"))`, so resume intent is tied to the Manager result rather than forced true.
- `webapi/mission_items.py`: bounded task enqueue explicitly starts with `resume_continuous=False`.

A separate `LifeWorkerConfig(` search finds only the CLI construction and the Web lifecycle construction among production code. No additional hidden keepalive/recovery constructor that hard-codes `resume_continuous=True` was found in this pass. That is negative source evidence limited to current indexed public main.

## Existing fencing primitive

`daemon/state.py` already provides a stronger mechanism than the lifecycle helpers use:

- `ContinuousConfigState` includes `generation`.
- `write_continuous_config()` holds `.continuous.lock`, reads the current state, writes generation `current+1`, fsyncs the temp file, atomically replaces the target, and fsyncs the parent directory.
- `compare_and_swap_continuous_config()` holds the same lock, requires full equality with the supplied expected state (including generation/done fields), and only then commits the next generation.
- Tests cover lock exclusion, quota reserve behavior, pre/post-replace failure semantics, and durable atomicity.

This means the continuous lifecycle does not need a new distributed capability system merely to reject stale stop/resume writes.

## Canonical boot gate still has a TOCTOU

`_rf_resolve_continuous_boot_state()` reads the continuous state and passes that snapshot to `_rearm_operator_drain_for_resume()`.

The helper correctly requires:

- this is a resume launch, not a fresh `--continuous` launch;
- state is disabled;
- `done_reason` is exactly one of `RESUMABLE_STOP_REASONS`;
- objective is nonempty.

But the commit is `write_continuous_config(...)`, not CAS against the snapshot. The read lock has already been released. A concurrent semantic decision can therefore advance generation and change reason/objective between read and commit, after which the boot helper writes from the stale snapshot and clears the newer reason.

The current `tests/daemon/test_continuous_resume_gate.py` validates drain/graceful-stop re-arm and preservation of a pre-existing authority hold, but it does not inject a newer generation between snapshot acquisition and commit.

## Refined invariant: two fences, not one

The prior candidate remains useful but should distinguish two different authorities:

### Fence A — continuous lifecycle generation

Use the existing `continuous.generation` / full-state CAS for process-state semantics:

- raw start helpers carry resume *intent* only and do not pre-write continuous state;
- boot re-arm CASes `expected=boot_snapshot` and fails closed if any newer semantic write landed;
- scheduled upgrade request records the captured expected continuous generation/state and completion CASes only if it is still current; a later stop/hold supersedes the old maintenance request automatically;
- immediate upgrade should re-read/CAS after process stop rather than force-enable a stale snapshot;
- operator-decision stop/resume reconciliation should use CAS against its `before` snapshot rather than unconditional read→write.

### Fence B — protected Manager route revision

Continuous generation is **not** enough for prior route/authority problems. Bounded work can change protected route/stage/venue/workflow state while continuous state stays unchanged, and current `manager-handoff.json` does not bind all of those fields. Intentional semantic resume after a route-changing pause still needs a Manager-owned route/pipeline revision (or equivalent digest) and reconciliation.

So the minimal architecture is not “one giant capability everywhere.” It is:

1. reuse existing durable continuous CAS for stop/resume/process-maintenance races;
2. add/finish a separate protected-route revision only where semantic execution authority depends on Manager route identity;
3. require both fences only on paths that bridge process restart into semantic execution.

## Regression matrix

Add current-main tests for:

- boot snapshot is resumable drain-stop, concurrent writer changes it to authority hold before re-arm commit -> CAS fails and hold remains byte/state-authoritative;
- boot snapshot is graceful stop, no intervening write -> re-arm succeeds and generation increments once;
- `/daemon/upgrade` on an absent daemon with `operator chose to stop the campaign` -> maintenance operation does not enable continuous state;
- scheduled upgrade captured at generation N, operator stop advances to N+1 -> completion cannot re-enable N;
- immediate upgrade captures enabled state, concurrent semantic disable lands before restart -> old snapshot cannot overwrite it;
- explicit `/continuous enabled=true` remains allowed to persist semantic enable even if process admission subsequently fails (this is an explicit semantic command, unlike raw daemon start);
- bounded task autostart remains `resume_continuous=False`;
- Manager task/decision flow may carry resume intent only when its current semantic result says continuous should run.

## Frontier / exact continuation

Frontier remains nonempty. Next:

1. enumerate every production `write_continuous_config()` read→write caller and classify it as semantic-authority, process-maintenance, or derived projection; identify which can be changed to existing CAS without new schema;
2. inspect immediate upgrade and operator-decision reconciliation interleavings against daemon-command / Manager locks to separate merely theoretical windows from cross-lock reachable ones;
3. inspect all current `compare_and_swap_continuous_config()` production callers to extract the repository’s own preferred stale-write pattern and reuse it rather than inventing another protocol;
4. keep the protected-route revision audit separate: map exactly which route-changing bounded operations do **not** advance continuous generation, proving where Fence B is independently necessary;
5. keep the external/admin `PIPELINE_STATE` writer CAS/fencing matrix as a separate state-authority branch.
