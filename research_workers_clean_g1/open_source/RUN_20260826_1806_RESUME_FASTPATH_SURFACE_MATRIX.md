# Open Source Systems Scan — resume fast-path surface matrix and missing coverage

Role: `open_source` clean exploration.
Frozen semantic control tuple: note main `b0cc6f3ae62b88d7423e3fc1545d1b598c85381d`, control revision 10, role config revision 5, role config blob `118f440957ba4654e804af902aa09a9224acca43`.
Public source: `lbx154/Argus@16bb128992ea9d0c11b5bbca7a4f1d549dea84dd` (freshly verified at invocation start).
Predecessor in this invocation: `RUN_20260826_1804_EXPLICIT_DAEMON_RESUME_SAME_VERTICAL_STALE_ROUTE_HANDOFF.md`.

## Additional result

The narrow Manager-handoff identity is shared by multiple explicit restart/resume surfaces, not just one Web button. The implementation has good process-identity/admission locks around daemon lifecycle, but the semantic resume fast path is still keyed by an identity that omits same-vertical route changes.

### Surface matrix

- **Web daemon start**: `/api/projects/{sid}/daemon/start` always calls `start_project_daemon(..., resume_continuous=True)`. If continuous is disabled with a preserved objective and an `operator ...` reason, the lifecycle helper re-enables it before spawn. Fresh boot then uses `_resume_matches_manager_handoff()`.
- **Daemon replacement**: `replace_project_daemon(..., resume_continuous=...)` parks the selected victim and starts the target through the same `start_project_daemon()` helper. When the caller requests continuous resume, it inherits the same semantic fast path.
- **Daemon upgrade/restart**: both immediate and scheduled upgrade paths snapshot whether continuous was enabled, may rewrite `continuous.json` enabled before restart, and then call `start_project_daemon(..., resume_continuous=...)`. They therefore converge on the same boot handoff gate.
- **CLI `--resume-continuous`**: the flag is copied into `LifeWorkerConfig`; boot re-arms only process-stop reasons (`operator drain-stop` / graceful signal stop), then evaluates the same `_resume_matches_manager_handoff()` fast path. A route change made while the daemon is stopped can therefore matter even though CLI pause semantics are narrower than Web explicit-resume semantics.

### Why same-vertical changes are real route changes

When continuous mode is disabled, `_allow_manager_route_contract_change()` returns true for a fresh handoff. `commit_vertical_decision()` can persist `workflow_mode`, `research_target_level`, `research_direction_mode`, `target_venue`, adapted stages and operator-objective state while keeping the same selected vertical/domain. These fields affect subsequent execution/validation but are absent from Manager handoff v3 identity.

### Fast-path identity is intentionally permissive across continuous rewrites

`_manager_handoff_identity_matches()` requires objective hash + vertical + domain, but permits `identity.continuous_generation <= current_generation`. This supports stop/rearm without forcing a new Manager call, yet means an old handoff can remain acceptable after a newer continuous-state generation. Without an independent exact protected route revision, generation cannot distinguish a benign process restart from a semantic route mutation performed while the campaign was disabled.

### Legacy event fallback does not repair the omission

If no sidecar match is available, `_resume_matches_manager_handoff()` reconstructs a legacy identity from a prior `life.manager.intent.completed` event using execution task + vertical + domain. That fallback also does not bind workflow mode, research bar, target venue, stage, or an authoritative route revision, so it preserves the same false-positive class.

## Test gap

The dedicated `tests/daemon/test_continuous_resume_gate.py` verifies suppression, same-objective generation re-arm, drain/graceful-stop resume, finished-campaign non-resume, authority-hold preservation, and objective-file freshness. In the inspected test file there is no regression that mutates a same-vertical Manager route field between handoff and resume and then requires the fast path to reject it.

## Refined invariant

One exact protected route/pipeline revision must be part of every semantic resume credential. Lifecycle admission locks, daemon command revisions, continuous generation and process identity remain useful but are different invariants. Specifically:

1. Manager route mutation increments protected revision under the established Manager pipeline lock.
2. continuous handoff identity/event records the exact revision.
3. all explicit resume surfaces eventually require current revision equality before taking the no-Manager fast path.
4. mismatch does **not** necessarily reject resume; it forces Manager reconciliation before Planner/Engineer execution.
5. crash restart with exact unchanged revision remains cheap and deterministic.

## Scope limits

No live daemon was mutated and no exploit was run. This is a source-level cross-call-site audit of one verified public commit. Replacement/upgrade only inherit the issue when they actually resume a campaign; unrelated daemon parking/admission behavior is out of scope.

## Exact continuation

Finish auditing direct re-arm/promotion paths that do not converge through fresh boot, especially operator-question/decision resolution and any live config endpoints. Then enumerate every route mutation producer and semantic credential consumer that must carry the protected revision, including CampaignControl wait/authorization/capability, manager-handoff identity/event fallback, standing STEER, backlog manager_decision, Planner context and low-level stage/route writers. Keep direct/admin persist_vertical, math-objective, rollback/reset/completion writers in a separate CAS/fencing matrix so process serialization is not confused with semantic authorization.