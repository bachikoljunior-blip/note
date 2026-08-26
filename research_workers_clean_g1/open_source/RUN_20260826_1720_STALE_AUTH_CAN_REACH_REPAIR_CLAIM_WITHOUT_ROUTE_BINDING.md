# Open Source Systems Scan — a recorded authorization can reach validator-repair claim without any protected route/vertical cross-binding

Role: `open_source` clean exploration.
Same frozen semantic control tuple for this physical invocation: note main `456111f88cd26b8ad796866aaf64a6c44a176908`, control revision 10, role config revision 5, role config blob `118f440957ba4654e804af902aa09a9224acca43`.
Public source remains freshly verified `lbx154/Argus@16bb128992ea9d0c11b5bbca7a4f1d549dea84dd`.

## Follow-through from stale authorization record to mission capability

The prior run established a source-level window in which PAUSE preserves objective + CampaignControl wait, a fresh bounded handoff may revise protected route state because continuous mode is disabled, and the old wait can still be authorized because authorization identity reuses the old CampaignControl epoch while PAUSE preserved the objective hash.

This run traced what happens *after* such an authorization is recorded.

### Planner sees the authorization as current

`CampaignControlStore.current_authorizations()` does not compare a public authorization against protected pipeline route/stage. It reads the current CampaignControl HEAD/snapshot, follows `snapshot.authorization_ids`, and returns matching `event == "issued"` rows.

The Planner context explicitly calls `current_authorizations()`, strips each row to a public form, and tells Planner that it may place `authorization_id` + `authorization_action` on a task whose action/write paths match.

The Planner task schema directly supports `authorization_id` and `authorization_action`.

### Enqueue validation checks the CampaignControl authorization, not route compatibility

`_validated_task_authorization(task)`:

1. requires both id and action;
2. currently accepts only `validator_repair` as an enforced mission capability;
3. rebuilds the set from `store.current_authorizations()`;
4. rejects missing/stale ids;
5. checks only that the requested action is in `allowed_actions`.

It does **not** compare the authorization to the task's current Manager route/vertical, current protected pipeline stage, or a protected pipeline revision/digest.

The resulting backlog item stores both:

- the authorization id/action; and
- a separately generated current `manager_decision` for the task.

No source-level cross-check was found between those two authority records at enqueue.

### Mission claim checks CampaignControl revision + workspace evidence, still not protected route

Before execution, `_mission_execution_runtime` loads the authorization and reconstructs campaign identity from the authorization's stored `campaign_epoch` plus the current continuous objective. It then calls `claim_repair_capability(...)`.

`_validate_issued_unlocked(...)` is strong on its own axes:

- exact issued event + nonce;
- campaign id/objective hash/epoch;
- exact current CampaignControl HEAD revision;
- authorization id still current in the HEAD snapshot;
- allowed action + expiry;
- frozen evidence hashes;
- allowed-write-path baselines;
- whole project-tree digest excluding authorized writable files.

`claim_repair_capability(...)` additionally rechecks the terminal Reviewer diagnosis (`failure_source == validator_defect`) and exact `validator_id`, then atomically consumes the authorization into an active one-shot repair capability.

But no check in this claim path binds the authorization to:

- Manager protected route/vertical;
- protected `current_stage`;
- a `PIPELINE_STATE` revision/digest;
- the backlog item's `manager_decision.vertical`.

In the split-root design, the capability store's `project_root` is the execution/operator worktree while CampaignControl state is rooted in the Manager/life state directory. The project-tree digest therefore cannot be assumed to authenticate Manager protected pipeline state.

### The current route is applied separately after authorization handling

The same mission runtime later reads `item.manager_decision`, extracts its `vertical`, materializes/validates that vertical, and executes under that persisted/current route contract. That route handling is separate from the authorization claim and is not compared to the authorization's blocker provenance.

So the two pieces can both be individually valid while referring to different semantic campaigns/routes:

- authorization: old blocker/Reviewer diagnosis from paused campaign A;
- backlog manager decision: current route B selected by bounded work after PAUSE.

## Reachability status

This closes an important part of the chain: **if Planner emits a validator-repair task referencing the authorization recorded in the PAUSE window, current enqueue + capability-claim code contains no protected-route cross-binding that would reject it solely because the Manager route changed.**

It is still not a deterministic live exploit claim. One lifecycle condition remains to prove: whether a Planner cycle can consume that current authorization while route B remains authoritative, before an explicit resume/re-handoff of A restores/supersedes route state or another CampaignControl revision invalidates the authorization.

The source already makes this path model-reachable rather than schema-impossible: current authorizations are deliberately placed into Planner context and `TaskSpec` has the fields required to reference them.

## Design implication

`clean-os-g1-005` now needs a concrete cross-authority invariant, not merely better observability:

> Any privileged mission capability derived from a blocker must be bound to the same protected route/campaign revision under which that blocker was diagnosed.

For Argus-shaped file state, the minimal candidate is:

- add one authoritative protected `pipeline_revision`/digest covering Manager-owned route/stage keys;
- persist that revision (or immutable campaign-route id) into wait -> authorization -> capability lineage;
- recheck it at authorization issuance **and** claim;
- if PAUSE permits unrelated bounded work to revise the shared route namespace, either namespace paused campaign state or invalidate/supersede its live wait/authorizations before the route mutation;
- keep execution-worktree hash/evidence fencing as a separate scientific-artifact invariant rather than treating it as route authentication.

This does not require making derivative `stage_projection` authoritative.

## Regression target

Add a cross-binding regression fixture with distinct routes A and B:

1. establish campaign A, Reviewer validator-defect diagnosis and live wait W;
2. PAUSE A;
3. commit bounded route B in the same state namespace;
4. authorize W;
5. expose the authorization to Planner and create a `validator_repair` TaskSpec under manager decision B;
6. enqueue and attempt claim.

Safe target behavior: reject before privileged execution because authorization route revision != current protected route revision. Existing project-tree and CampaignControl-head checks should remain unchanged.

Positive controls:

- same-route PAUSE/resume with unchanged protected route revision may preserve W deliberately;
- active A + bounded supplemental work that does not mutate protected route may preserve W;
- explicit A -> C standing replacement remains fenced by objective/campaign identity.

## Scope limits

No live mutation or unauthorized repair was executed. The claim is source-level: current Planner/enqueue/claim code lacks protected-route binding after an authorization has become current. Whether a real paused-session lifecycle actually runs a Planner cycle under B before A re-handoff remains the final reachability question.

## Exact continuation

Resolve that final lifecycle question. Trace how bounded staged tasks are executed after PAUSE, whether their supervisor invokes Planner cycles with route B and `current_authorizations`, and how explicit resume/re-arm behaves when a paused objective A coexists with route B. If Planner can consume the authorization before route restoration, classify this as an end-to-end current stale-capability path. If every supported lifecycle restores/supersedes A first, downgrade it to a latent cross-binding defect with a regression-only counterexample. Then audit direct/admin pipeline writers under the same route-revision invariant.