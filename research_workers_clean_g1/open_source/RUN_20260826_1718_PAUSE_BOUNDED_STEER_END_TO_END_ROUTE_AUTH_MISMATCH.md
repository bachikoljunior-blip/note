# Open Source Systems Scan — PAUSE → bounded route change → standing STEER creates an end-to-end route/authorization mismatch

Role: `open_source` clean exploration.
Frozen semantic control tuple: note main `456111f88cd26b8ad796866aaf64a6c44a176908`, control revision 10, role config revision 5, role config blob `118f440957ba4654e804af902aa09a9224acca43`.
Public source: freshly verified `lbx154/Argus@16bb128992ea9d0c11b5bbca7a4f1d549dea84dd`.

## Result

Current public source contains a supported lifecycle in which a paused campaign's old blocker authorization can become consumable while Manager protected route state belongs to a later bounded task. The mismatch is model-reachable end to end; no live exploit or mutation was performed.

## Reachable sequence

1. Continuous campaign A owns Manager route/vertical A and CampaignControl has a validator-defect diagnosis plus live wait W.
2. PAUSE disables continuous mode while preserving objective A/backlog and does not mutate CampaignControl, so W survives.
3. A fresh bounded task B is submitted while continuous is disabled. The bounded front door may commit a new Manager route B. Web `enqueue_task_command(..., autostart_daemon=True)` starts a daemon with `resume_continuous=False`.
4. The non-continuous supervisor executes B. When backlog empties it does not run Planner, but the outer `LifeWorker` daemon remains resident: `_rf_main_loop` repeatedly invokes the supervisor after its poll sleep instead of exiting on `backlog_empty`.
5. After route B is current, the old W can still be authorized. Authorization identity uses the CampaignControl HEAD epoch plus the current continuous objective. PAUSE preserved objective A, and protected route is not in that identity. Issuance freezes worktree/evidence state and turns W into a current authorization, but still carries no protected route/stage/pipeline revision.
6. `_handle_steer_control` can promote the paused session directly to standing without Manager re-handoff. When B is no longer running it chooses `standing_objective = current.objective` (A) before the steering directive, then calls `compare_and_swap_continuous_config(... enabled=True, objective=A, open_ended=True)` directly. It does not call `Manager.divide`, `commit_vertical_decision`, or `manager_continuous_handoff`, so protected route remains B.
7. The already-resident daemon hot-reloads continuous state at the start of each supervisor loop. It now runs continuous objective A under route B without boot-time Manager reconciliation.
8. On empty backlog, Planner runs. Planner context deliberately exposes `current_authorizations()`, and `TaskSpec` supports `authorization_id` / `authorization_action`.
9. Enqueue validation accepts an authorization by current id and allowed action only. It does not compare the authorization with current Manager route/vertical/stage or a protected pipeline revision. The backlog row separately records the current `manager_decision` for route B.
10. Mission capability claim strongly rechecks CampaignControl HEAD, nonce, expiry, frozen evidence/tree, terminal validator-defect diagnosis and validator id, but still does not bind to protected route/vertical/current stage/`PIPELINE_STATE` revision or `item.manager_decision.vertical`. The mission later processes its current Manager vertical separately.

Therefore, if Planner chooses the surfaced validator-repair authorization, current host validation can consume authorization lineage from A while protected Manager route is B.

## Why restart-based analysis missed it

A fresh daemon starting an enabled continuous campaign can run Manager divide/commit before Supervisor startup when the durable handoff does not match, potentially restoring the route. The standing STEER path avoids this because it re-enables the objective inside an already-running daemon and performs no Manager route reconciliation.

## Minimal design candidate

Do not promote derivative `stage_projection` into authority. Add one Manager-owned protected route identity/revision and carry it through the blocker privilege lineage:

- every Manager route/stage mutation increments a durable `pipeline_revision` or `route_generation` under the existing pipeline lock/CAS boundary;
- `activate_wait` records the exact protected revision that produced the blocker;
- authorization issuance rechecks and persists that same protected revision;
- `claim_repair_capability` rechecks it before consuming the authorization;
- a PAUSE-era bounded task that changes shared protected route must supersede/clear old waits/authorizations, use a distinct campaign namespace, or otherwise fence the paused campaign;
- direct standing STEER promotion must reconcile Manager route before re-enabling a preserved objective when the protected route revision no longer matches;
- keep frozen worktree/evidence hashes as a separate artifact-integrity invariant, not as route authentication.

## Deterministic regression

A regression test need not depend on Planner stochasticity: inject a valid Planner verdict/TaskSpec after establishing A/W -> PAUSE -> bounded B -> authorize W -> standing STEER A. Current code can reach capability claim under manager decision B; fixed code must reject because the authorization's protected route revision from A does not match current route revision B.

Positive controls should preserve intended cases: same-route PAUSE/resume may keep W; active A plus bounded supplemental work cannot mutate route; explicit standing replacement A->C remains fenced by objective/campaign identity; matching route revision plus unchanged scientific evidence permits one intended validator repair.

## Scope limits

This is source-level reachability at the verified Argus commit, not a live exploit reproduction. The final privileged mission still depends on Planner choosing an authorization-bearing task. No unauthorized write, capability use, or external side effect was executed.

## Exact continuation

Audit every other direct continuous-state promotion/re-arm path for the same missing Manager-route reconciliation, especially operator-decision resolution, daemon controls and CLI/API paths. Then inventory every producer/consumer that would need the proposed protected route revision. Separately audit direct/admin `persist_vertical`, math objective, rollback/reset and completion writers for the same revision/CAS invariant, preferring reuse of the existing Manager pipeline lock and continuous-config CAS over a second competing authority store.