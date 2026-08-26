# Open Source Systems Scan — paused campaign can preserve a live wait while a fresh bounded handoff may revise the same protected route

Role: `open_source` clean exploration.
Same frozen semantic control tuple for this physical invocation: note main `456111f88cd26b8ad796866aaf64a6c44a176908`, control revision 10, role config revision 5, role config blob `118f440957ba4654e804af902aa09a9224acca43`.
Public source remains freshly verified `lbx154/Argus@16bb128992ea9d0c11b5bbca7a4f1d549dea84dd`.

## A concrete surviving stale-live-wait path

The previous checks eliminated two common false positives:

- dynamic-plan rollback can leave stale `stage_projection`, but the same control revision has already cleared `active_wait`, so that projection alone cannot authorize anything;
- a genuine standing-objective replacement changes the continuous objective under the front-door CAS, so the old CampaignControl objective hash no longer matches.

A different source-level sequence survives those fences: **pause -> fresh bounded handoff in the same session/root -> authorization of the preserved old wait.**

### 1. PAUSE explicitly preserves the objective/backlog

The PAUSE control contract says it clocks out the whole session while preserving resumable state: it disables the standing campaign, interrupts the active item, asks the daemon to stop, and leaves the objective/backlog on disk for later resume.

Its implementation calls `disable_continuous_config(..., done_reason="operator pause")`. That helper is documented to disable the latest generation **while preserving its objective** and writes the next continuous generation. The PAUSE handler updates chat state and requests abort/daemon stop, but it does not touch `CampaignControlStore` at all; repository search shows the only `CampaignControlStore` use in `manager_dispatch.py` is the authorization handler.

Therefore an existing CampaignControl `active_wait` can remain durably present after pause.

### 2. Paused means route-contract changes become allowed again

`_allow_manager_route_contract_change(...)` returns `True` whenever continuous state is not enabled or has no objective. Its own contract says that outside an active campaign, a fresh operator handoff may choose a new topology/success bar.

So after PAUSE (`enabled=false`, objective still preserved), a new bounded handoff is treated as outside an active campaign for route-authority purposes.

`manager_bounded_handoff(...)` protects active continuous campaigns with `_bounded_handoff_division(...)`: when continuous is enabled, bounded work is supplemental and must not replace the standing vertical/stage/target/workflow. But `_bounded_handoff_division(...)` returns `None` when continuous is disabled, and the bounded handoff then calls the normal `prepared.commit(...)`, which may persist a newly classified route/vertical under the pipeline lock.

Thus the same life/session can hold:

- a paused old continuous objective and its old CampaignControl live wait, while
- the protected Manager route state is revised by a later bounded task.

### 3. Current authorization identity does not fence PAUSE generation changes

`disable_continuous_config` advances the continuous generation, but the Web/API authorization handler rebuilds current CampaignControl identity by calling `campaign_identity(campaign_epoch=head.campaign_epoch)`.

Supplying the old HEAD epoch deliberately bypasses the current continuous generation for this comparison. The identity still hashes the **current continuous objective**. Because PAUSE preserved that objective, the rebuilt `campaign_id` and `objective_sha256` can still match the old HEAD after pause.

The handler then requires the still-present `active_wait`, exact CampaignControl HEAD revision, wait id, and blocker fingerprint. None of those was changed by PAUSE or by a bounded route commit, because neither path updates CampaignControl.

Therefore the old wait remains eligible for authorization recording even though protected route/vertical state may now describe a different bounded task.

### 4. Authorization recording itself dispatches no task

The current handler replies `Authorization recorded ... No task was dispatched.` This limits the immediate consequence. However it still durably converts a potentially stale blocker into operator authorization state. Later validator-repair claim reconstructs identity from the authorization's stored campaign epoch plus the current continuous objective, so PAUSE/resume generation changes alone do not necessarily invalidate that authorization either.

This is a stronger and more precise current concern than stale `stage_projection`: **the live-wait identity domain can survive a protected route mutation performed while continuous mode is disabled.**

## Why this matters beyond Argus

The general invariant is:

> `paused/resumable` and `free to reuse the same mutable control-state namespace for unrelated work` are incompatible unless the paused campaign is fenced/namespaced.

A system can correctly preserve user intent across pause and still corrupt resume semantics if later work can overwrite shared route/stage state while old blockers/capabilities remain live.

## Candidate correction

Refine `clean-os-g1-005` around a narrower boundary:

1. A PAUSE that promises exact resume should preserve a **campaign-scoped protected route snapshot/revision**, not merely objective/backlog text.
2. While a paused campaign owns a live wait/capability, a fresh bounded task must either:
   - use a distinct protected campaign namespace,
   - be treated as non-mutating supplemental work,
   - or explicitly supersede/invalidate the paused campaign's wait/authorizations before changing shared route state.
3. Authorization issuance must bind to the same protected campaign/route revision that the blocker was produced under whenever the action depends on that route.
4. Do not rely on continuous `generation` unless its semantics are intentionally part of campaign identity; current code explicitly substitutes the HEAD epoch during authorization. If pause/resume is allowed to advance generation without invalidating a campaign, add a separate protected route revision/fence.
5. Keep `stage_projection` derivative and keep the host-ephemeral bearer concern separate.

## Regression targets

Construct the exact sequence in a test fixture:

1. continuous objective A with current CampaignControl `active_wait` W;
2. PAUSE; assert objective A preserved and W remains;
3. submit bounded task B that selects a different route/vertical while continuous remains disabled;
4. request authorization for W;
5. current safe behavior should reject as stale/superseded or require an explicit resume/supersession decision — never silently record W as the blocker of the newly protected route.

Also test the positive cases:

- PAUSE -> RESUME A without intervening route mutation may preserve W if that is deliberate policy;
- active continuous A + bounded supplemental task B must keep route immutable and may preserve W;
- explicit standing replacement A -> C must invalidate W through objective/campaign identity change.

## Scope limits

This is a source-level reachability argument, not a live exploit reproduction. It assumes the operator continues using the same session/life-dir after pause, which the control contract allows as an explicit later-resume context. Authorization recording alone does not execute a repair. The remaining work is to trace resume/backlog consumption and prove whether an authorization recorded in this window can be claimed under a changed route without another stale-state guard.

## Exact continuation

Trace the paused-session authorization through later backlog/resume consumption: determine how an authorization id is attached to a mission, whether resume restores/reclassifies the paused campaign route before claim, and whether `claim_repair_capability` or backlog guards revalidate the protected route/vertical. If claim is fenced later, downgrade this to stale authorization-record observability. If not, it is the first concrete end-to-end stale-live-wait path. Then audit direct/admin writers separately.