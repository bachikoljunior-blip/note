# Open Source Systems Scan — explicit daemon resume can trust a stale same-vertical Manager handoff

Role: `open_source` clean exploration.
Frozen semantic control tuple: note main `b0cc6f3ae62b88d7423e3fc1545d1b598c85381d`, control revision 10, role config revision 5, role config blob `118f440957ba4654e804af902aa09a9224acca43`.
Public source: freshly verified `lbx154/Argus@16bb128992ea9d0c11b5bbca7a4f1d549dea84dd`.

## Result

The previously identified PAUSE -> bounded route change -> standing STEER route/authorization mismatch is not the only resume surface. A fresh explicit daemon resume can also skip Manager route reconciliation when the paused campaign's old handoff and the bounded replacement share the same `vertical` and `domain` but differ in other protected route fields. This is a deterministic host-side resume path; it does not require Planner to select an authorization-bearing task. No live mutation/exploit was performed.

## Reachable source-level sequence

1. Continuous campaign A has a durable `manager-handoff.json`. Version 3 binds only `objective_sha256`, `vertical`, `domain`, `continuous_generation`, and `intent_id` (plus optional source-objective metadata). It does not bind `workflow_mode`, research target/direction, target venue, current stage, or an authoritative pipeline/route revision.
2. PAUSE disables continuous mode with `done_reason="operator pause"` while preserving the objective and backlog for explicit later resume.
3. While continuous is disabled, `_allow_manager_route_contract_change()` returns `True`, so a fresh bounded operator handoff B may revise persisted route-contract fields. `commit_vertical_decision()` persists `research_target_level`, `research_direction_mode`, `workflow_mode`, `target_venue`, and related state even when the chosen `vertical`/`domain` are unchanged.
4. The Web `/daemon/start` endpoint always calls `start_project_daemon(..., resume_continuous=True)`. That start path sees a disabled objective with an `operator ...` done reason and re-enables `continuous.json` before spawning the fresh daemon.
5. Boot then calls `_resume_matches_manager_handoff()`. It reads the *current* persisted vertical/domain but compares them against the old sidecar using only objective hash + vertical + domain + `identity.continuous_generation <= state.generation`.
6. If B changed workflow mode / research bar / target venue / stage-relevant route state while preserving A's vertical/domain, the old A handoff can still match. `resume_has_manager_handoff=True` then suppresses `_rf_manager_divide_on_boot()`; the daemon treats A's handoff as already reconciled and starts A under B's newer same-vertical route contract.

The existing fresh-daemon safety path therefore catches route changes that alter vertical/domain, but it can false-positive on same-vertical/domain route changes because the resume identity is narrower than the persisted Manager route.

## Why this materially refines the candidate

Earlier analysis treated a fresh daemon restart as a likely reconciliation boundary because `_rf_manager_divide_on_boot()` reruns Manager when no valid durable handoff matches. The current source shows that this boundary is only as strong as `_resume_matches_manager_handoff()`, whose identity omits several Manager-owned route fields. A single protected `route_generation` / `pipeline_revision` should therefore bind not only wait -> authorization -> capability and live STEER promotion, but also `manager-handoff.json` crash/resume identity.

## Minimal invariant

- Every Manager-owned route mutation that can change execution semantics increments one authoritative protected revision under the existing pipeline lock.
- `manager-handoff.json` records the exact protected revision/digest committed with the objective.
- `_resume_matches_manager_handoff()` requires exact current protected revision equality, not just objective/vertical/domain plus `generation <=`.
- Explicit daemon start/upgrade may re-arm a paused objective, but boot must re-run Manager reconciliation whenever that protected revision has advanced since the handoff.
- Artifact/evidence hashes and continuous generation remain separate invariants; neither substitutes for route identity.

## Deterministic regression

Create standing A and its handoff; PAUSE; submit bounded B while disabled that preserves vertical/domain but changes one persisted route field such as `workflow_mode` or `target_venue`; explicitly start the daemon with resume. Current code can make `_resume_matches_manager_handoff()` return true and skip boot Manager divide. Fixed code must reject the stale handoff revision and reconcile A before dispatch.

Positive controls: unchanged same-route pause/resume remains fast; a bounded supplemental task while A is still active cannot revise route contract; vertical/domain changes already force a handoff mismatch; crash restart with exact unchanged protected revision remains resumable.

## Scope limits

This is source-level reachability at the verified Argus commit. It does not assert a reproduced production incident, does not claim every same-vertical bounded task changes route fields, and does not broaden the finding to unrelated daemon/session implementations.

## Exact continuation

Audit daemon upgrade/replacement and CLI `--resume-continuous` paths for the same narrow handoff-identity false positive and inspect tests for missing same-vertical route-change coverage. Then finish the inventory of direct continuous promotion/re-arm paths (including operator-decision resolution if present) and map every producer/consumer that must carry the proposed protected route revision. Separately continue the direct/admin `persist_vertical`, math-objective, rollback/reset/completion writer audit for the same exact-revision/CAS invariant.