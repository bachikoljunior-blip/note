# Open Source Systems Scan — stale CampaignControl stage projection is not current authorization authority

Role: `open_source` clean exploration.
Frozen semantic control tuple: note main `456111f88cd26b8ad796866aaf64a6c44a176908`, control revision 10, role config revision 5, role config blob `118f440957ba4654e804af902aa09a9224acca43`.
Public source: `lbx154/Argus@16bb128992ea9d0c11b5bbca7a4f1d549dea84dd`, freshly verified as current `main` during this invocation.

## Scope correction

The previous run established a real sequential coherence gap: a normal Manager advance can be projected into `CampaignControlStore`, then the dynamic-plan settlement guard can roll the actual pipeline back without a second control projection. Therefore `CampaignControl.stage_projection` can describe an advance while `.argus/PIPELINE_STATE.json` has already returned to the prior stage.

This run checked whether that stale projection is *currently* used as authorization authority. The answer is narrower than the previous candidate wording implied: **no production authorization path found reads `stage_projection` at all.**

Repository-wide search for `stage_projection` at the verified source head returns only:

1. `manager/control_state.py`, where the field is initialized, carried forward, and written by `clear_wait_for_new_evidence(...)`;
2. `apps/_runtime_stage_transition.py`, which supplies the post-stage-write projection;
3. tests.

Inside `CampaignControlStore`, `stage_projection` has exactly two semantic roles: default/carry-forward storage and optional replacement during `clear_wait_for_new_evidence(...)`. It is not consulted by `issue_authorization`, capability claim, current-wait validation, or validator-repair admission.

## Current authorization freshness inputs

The Web/API authorization path reads the current CampaignControl HEAD/snapshot and refuses issuance unless `active_wait` is a current dict. It then issues against the wait's `blocker_fingerprint`, exact expected control `state_revision`, expected `wait_id`, the allowed action set, scoped writable paths, watched evidence paths/tree, campaign identity/epoch, expiry, and source message identity.

`CampaignControlStore.issue_authorization(...)` rechecks the exact expected HEAD revision under its lock. If a wait is expected, it also rechecks the same `wait_id` and `blocker_fingerprint` before committing the authorization revision.

For validator repair, claim additionally checks the current terminal Reviewer diagnosis (`failure_source == validator_defect`) and exact `validator_id`. No `stage_projection` check appears in that path.

The current allowed action vocabulary is:

- `validator_repair`
- `acceptance_retry`
- `provenance_repair`
- `artifact_refresh`
- `resume_blocked_work`

None was found to derive permission from `stage_projection` itself.

## Why the specific normal rollback sequence fails closed for new authorization

`clear_wait_for_new_evidence(...)` always includes `active_wait: null` in the same control revision that optionally writes the new `stage_projection` and terminal evidence.

Therefore the already-observed normal sequence is:

1. Manager stage mutation succeeds.
2. Runtime clears the active wait and writes an advance projection into CampaignControl.
3. Dynamic-plan settlement rolls the actual pipeline stage back.
4. CampaignControl can now have a stale stage projection — **but it has no active wait to authorize**.
5. The Web/API authorization handler rejects issuance because there is no current Manager-bound blocker awaiting authorization.

So the concrete normal-path divergence is presently an **observability/coherence defect**, not a demonstrated authorization bypass.

## What remains potentially security-relevant

The remaining question is different: can a protected pipeline writer mutate stage/route/objective state *while an existing `active_wait` remains current in CampaignControl* and without changing campaign identity or HEAD in a way that invalidates authorization?

That requires auditing direct/non-projected writers such as rollback/reset/route replacement and their lifecycle context, not the dynamic-plan rollback already proven above.

A serious case would need all of these simultaneously:

- current CampaignControl still carries a live `active_wait`;
- protected pipeline state changes in a way relevant to the blocker/action scope;
- CampaignControl HEAD/wait identity remains accepted;
- authorization issuance/claim does not independently revalidate the changed protected field.

No such production sequence was established in this invocation.

## Candidate refinement

Refine `clean-os-g1-005` again:

1. Keep `stage_projection` explicitly derivative unless a future authorization action actually consumes stage/route semantics.
2. Do **not** migrate protected stage state into CampaignControl merely to repair the currently observed stale projection; that would solve more than the evidence requires and create another authority-migration surface.
3. Preserve the separate single-authoritative `pipeline_revision`/CAS candidate for lost-update, stale-writer, and wrong-path mutation defense.
4. If a privileged action is ever stage/route-sensitive, bind it directly to the authoritative pipeline revision/digest and revalidate that protected state at issuance/claim time; do not treat CampaignControl revision or derivative projection as a substitute.
5. Keep the host-ephemeral bearer redesign separate: current source still persists raw nonce, while observed recovery tests do not require same-bearer continuity.

## Regression targets

- Advance -> CampaignControl clear/projection -> dynamic rollback -> authorization request: must fail because `active_wait` is absent, regardless of stale `stage_projection`.
- Inject a stale `stage_projection` while keeping HEAD otherwise valid: current authorization semantics must remain unchanged.
- For each direct rollback/reset/route writer, construct the state with a live wait and prove either (a) the writer clears/invalidates it, (b) campaign identity changes, or (c) authorization revalidates the changed protected field.
- If any writer preserves a semantically stale live wait, add exact protected pipeline revision/digest binding rather than making derivative projection authoritative.

## Scope limits

No unauthorized authorization was executed. The negative conclusion is limited to the current verified Argus source and the specific `stage_projection` field/current authorization flow. It does not prove all protected pipeline writers are safe with respect to live waits.

## Exact continuation

Audit direct `rollback_stage`, `reset_stage_for_replacement_intent`, vertical/route replacement, final completion, and external/admin pipeline writers specifically under a pre-existing live `active_wait`. For each path determine whether it clears the wait, advances CampaignControl, changes campaign identity/epoch, or can leave a semantically stale blocker authorizable. Only if such a path exists should stage/route binding be promoted from defense-in-depth to current authorization correctness. In parallel, keep the separate writer-CAS and ephemeral-bearer tracks intact.