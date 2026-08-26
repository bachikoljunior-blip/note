# Open Source Systems Scan — PAUSE → bounded route change → standing STEER creates an end-to-end stale-route capability path

Role: `open_source` clean exploration.
Same frozen semantic control tuple for this physical invocation: note main `456111f88cd26b8ad796866aaf64a6c44a176908`, control revision 10, role config revision 5, role config blob `118f440957ba4654e804af902aa09a9224acca43`.
Public source remains freshly verified `lbx154/Argus@16bb128992ea9d0c11b5bbca7a4f1d549dea84dd`.

## Final lifecycle reachability result

The previous report left one question open: after a PAUSE and a bounded task changes the protected Manager route, can a *supported* lifecycle reach a continuous Planner cycle before a Manager re-handoff restores the old route?

Current source says **yes**. The supported route is a standing STEER promotion on the already-running non-continuous daemon.

This converts the prior latent cross-binding defect into a concrete source-level end-to-end stale-route capability path. It is still a source/reachability result, not a live exploit reproduction.

## Reachable sequence

### A. Establish campaign A + live wait W

A continuous campaign has:

- continuous objective A;
- Manager protected route/vertical A;
- CampaignControl HEAD for A;
- Reviewer terminal evidence diagnosing a validator defect;
- `active_wait = W`.

### B. PAUSE A

PAUSE:

- disables continuous mode;
- preserves objective A and backlog;
- advances continuous generation;
- stops the current daemon;
- does not mutate CampaignControl, so W remains current there.

### C. Submit bounded task B and autostart a normal non-continuous daemon

The Web work-item path `enqueue_task_command(..., autostart_daemon=True)`:

1. runs `manager_bounded_handoff`;
2. when continuous mode is disabled, the bounded handoff is allowed to commit a fresh Manager route/vertical B rather than inherit A;
3. autostarts the project daemon with `resume_continuous=False`.

The daemon executes B under non-continuous mode.

Important lifecycle detail: a non-continuous supervisor does **not** invoke Planner when its backlog becomes empty. It returns `backlog_empty`. But the outer `LifeWorker` daemon does **not** exit on that result: `_rf_main_loop` is a resident drain loop, resets supervisor counters, sleeps the poll interval, and calls the same supervisor again until a real daemon stop/terminal condition occurs.

Therefore after B finishes there is a supported state with:

- daemon still alive;
- protected route B;
- continuous disabled but objective A still stored;
- old CampaignControl wait W still present.

### D. Authorize W after route B is current

The authorization handler can still accept W because it rebuilds identity with the CampaignControl HEAD epoch and the current continuous objective. PAUSE preserved objective A, and route B is not part of CampaignControl identity.

Issuance captures project/evidence hashes and clears W into a current authorization id, but does not bind the authorization to Manager route B/A or protected `PIPELINE_STATE` revision.

### E. Promote to standing with STEER — without a Manager route re-handoff

`_handle_steer_control(...)` has a direct standing-promotion path:

- it reads current continuous state;
- when `lifetime == "standing"`, it chooses `standing_objective = active_objective or current.objective or manager_directive`;
- if B has completed, there is no running item, so the preserved `current.objective` A wins;
- it calls `compare_and_swap_continuous_config(... enabled=True, objective=A, open_ended=True)` directly;
- it updates chat continuous state and queues the steering directive.

Crucially, this path does **not** call `Manager.divide`, `commit_vertical_decision`, `manager_continuous_handoff`, or any route-reset/rehandoff primitive. The protected Manager route remains B.

The direct continuous promotion advances continuous generation but, exactly like the authorization path already analyzed, CampaignControl identity can remain A because the authorization/claim lineage carries the stored CampaignControl epoch and objective A is unchanged.

### F. The resident daemon hot-reloads continuous A under route B

The same daemon is still running from bounded task B. `LifeSupervisor.run()` calls `_reload_continuous_config()` at the top of each loop, and the daemon outer loop repeatedly invokes the supervisor.

Once STEER has enabled A, the supervisor becomes continuous without rebooting. There is no boot-time Manager divide to restore route A because no process restart occurred.

When backlog is empty, continuous mode now invokes Planner. Planner receives:

- `continuous_objective = A`;
- current protected state root whose route/vertical is still B;
- the current authorization list, including the authorization derived from W.

### G. Planner can enqueue the authorization under current route B

Planner TaskSpec directly supports `authorization_id` / `authorization_action`. `_validated_task_authorization` checks only current authorization id + allowed action, not protected route/stage/revision compatibility.

The queued item separately receives the current `manager_decision`/route metadata. Thus a validator-repair task can carry:

- authorization lineage from A/W;
- current Manager route B.

### H. Capability claim has no route cross-binding

The mission claim path then checks:

- authorization nonce;
- CampaignControl campaign/objective/epoch;
- exact CampaignControl HEAD revision;
- current authorization id;
- expiry;
- frozen evidence and project-tree hashes;
- terminal Reviewer diagnosis and validator id.

It still does not compare against protected route/vertical/current stage/pipeline revision or `item.manager_decision.vertical`.

The mission runtime handles the item's current Manager vertical separately after authorization processing.

Therefore, if Planner elects to use the surfaced authorization, the existing checks permit the authorization/capability lineage from A to be consumed while the Manager protected route is B, assuming the separately frozen worktree evidence has not changed in a disallowed way.

## Why the ordinary restart path did not prove this earlier

A fresh daemon with a continuous objective but no valid durable Manager-handoff match performs Manager divide/commit before supervisor startup, which can restore/reconcile the route. That made restart-based reachability ambiguous.

The standing STEER path bypasses that ambiguity because it changes continuous state **inside a resident daemon** and performs no Manager route handoff.

## Exact security/correctness claim

Observed source supports this narrower statement:

> A paused campaign's blocker authorization is not bound to Manager protected route state. A later bounded route change plus direct standing STEER promotion can make the resident continuous Planner operate under the old objective and new route, surface the old authorization as current, enqueue it, and reach the validator-repair claim path without a route/revision mismatch check.

This is not evidence that the model will always choose the repair task, nor evidence that arbitrary code execution follows. It is an end-to-end **model-reachable authority mismatch** in the current control contract.

## Minimal fix candidate for `clean-os-g1-005`

Do not make `stage_projection` authoritative. Instead add one protected route identity/revision that is carried through the privileged lineage:

1. Manager-owned route/stage mutation increments a durable `pipeline_revision` (or immutable `route_generation`) under the existing pipeline lock/CAS boundary.
2. `activate_wait` records the exact protected route identity/revision that produced the blocker.
3. `issue_authorization` requires the same current protected revision and persists it into the authorization.
4. `claim_repair_capability` rechecks the protected revision before consuming the authorization.
5. Any PAUSE-era bounded task that changes the shared protected route must either:
   - explicitly supersede/clear old wait + current authorizations,
   - use a separate campaign-scoped protected namespace,
   - or make the old campaign's later resume restore a matching route revision before authorization can be used.
6. Direct standing STEER promotion must not re-enable a stored objective against a different protected route without a Manager reconciliation step.
7. Keep worktree frozen-evidence/tree checks; they protect artifacts, not Manager route authority.

## Regression test

A high-value regression can be deterministic without depending on Planner stochasticity by injecting a valid Planner verdict/TaskSpec:

1. campaign A + validator defect + W;
2. PAUSE A;
3. bounded B commits route B and resident non-continuous daemon remains alive;
4. authorize W;
5. standing STEER re-enables preserved A without route re-handoff;
6. inject Planner task referencing authorization under current manager decision B;
7. current implementation reaches claim; fixed implementation must reject because wait/authorization route revision from A != current protected route revision B.

Positive controls:

- PAUSE A -> no route mutation -> standing resume A can preserve W if policy intends it;
- active A + bounded supplemental task cannot mutate route, so W remains usable;
- explicit standing replacement A -> C invalidates W through objective/campaign identity;
- same route revision + unchanged frozen evidence allows the intended validator repair once.

## Scope limits

No live exploit, unauthorized write, or repair mutation was performed. The final step depends on Planner choosing the authorization-bearing task; source makes that choice explicitly available and the host validation accepts it, but it is not deterministic model behavior. The finding applies to the verified Argus commit and the specific PAUSE/bounded/STEER resident-daemon path.

## Exact continuation

Audit whether other direct continuous-state promotions (`steer`, operator-decision resolution, daemon control, CLI/API re-arm) similarly bypass Manager route reconciliation, then enumerate every producer/consumer of the proposed protected route revision. Separately audit direct/admin `persist_vertical`, math objective, rollback/reset, and completion writers for the same revision/CAS invariant. Seek a smaller fix that reuses existing Manager pipeline lock plus continuous-config CAS rather than introducing a second competing authority store.