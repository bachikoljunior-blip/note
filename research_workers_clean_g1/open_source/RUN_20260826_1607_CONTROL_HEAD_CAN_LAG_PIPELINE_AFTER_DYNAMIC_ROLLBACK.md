# Open Source Systems Scan — CampaignControl HEAD can lag actual pipeline after a normal dynamic rollback

Role: `open_source` clean exploration.
Frozen semantic control tuple remains note main `b8c5a5e3b93fa70aa698d16465a8724f4785e6b3`, control revision 9, role config revision 5, role config blob `118f440957ba4654e804af902aa09a9224acca43`.
Public Argus source remains `lbx154/Argus@16bb128992ea9d0c11b5bbca7a4f1d549dea84dd`.

## Concrete sequential split discovered

`CampaignControlStore` has strong revision/authorization fencing, but its current `stage_projection` is **not the same atomic authority as `.argus/PIPELINE_STATE.json`**.

The normal SkillLoop stage path in `argus_skill/apps/_runtime_stage_transition.py` does the following in sequence:

1. `Manager.decide_stage_transition(...)` applies the actual stage mutation to the pipeline state.
2. The runtime computes the current pipeline file SHA-256 and calls `CampaignControlStore.clear_wait_for_new_evidence(...)` with a `stage_projection` containing action/current/target plus `pipeline_state_sha256` and terminal review evidence.
3. This control projection is explicitly best-effort: any exception is swallowed as `manager control revision projection skipped`; it cannot own or roll back the Manager verdict.

That alone means the two stores are not one transaction.

A stronger concrete divergence occurs later in the same normal mission lifecycle. `MissionExecutionSettlementMixin._apply_dynamic_plan_stage_guard()` can detect that a Planner-bounded DAG still has unfinished nodes after a Manager `advance`. It then calls `rollback_stage(...)` to restore the original stage and rewrites the local reported transition to `hold`.

This rollback happens **after** the control projection of the earlier advance, and the settlement module does not update `CampaignControlStore` afterward. Repository search found no CampaignControlStore use in that settlement path.

Therefore a normal, intended execution can end a mission with:

- actual `PIPELINE_STATE.current_stage` rolled back to the prior stage, while
- current CampaignControl `stage_projection` still describes the earlier advance and hashes the pre-rollback pipeline file.

This is a sequential coherence gap, not a concurrency race.

## Why authorization freshness does not automatically close the gap

Web/API operator authorization constructs `CampaignControlStore(life_dir, project_root=_authorization_workdir(...))`:

- control revisions/HEAD live under the Manager `life_dir`;
- frozen project evidence/tree is rooted at the operator/execution workspace.

In the normal split-root composition, the protected Manager pipeline state lives in the control root rather than the execution workspace. Thus the authorization's frozen project tree is not a universal hash of the protected pipeline state.

Authorization issuance and claim correctly require the authorization's `state_revision` to equal the current **CampaignControl HEAD**. But if a pipeline rollback changed protected stage state without a corresponding CampaignControl revision, exact-current CampaignControl revision is not equivalent to exact-current pipeline state.

This does not prove a current exploit. It proves the revision domain is narrower than the protected pipeline domain.

## Candidate correction

This removes the remaining temptation to make current `CampaignControlStore` the protected pipeline authority merely by adding more projections.

For `clean-os-g1-005`:

1. Reuse CampaignControlStore's tested **mechanics**—portalocker serialization, immutable revisions, exact-current checks, one-shot authorization, evidence drift guards.
2. Do **not** retain two independently committed semantic authorities for stage/route state.
3. The exact prior pipeline revision/digest used by a privileged transition must be validated in the same protected mutation critical section that writes the new stage/route state.
4. If CampaignControl remains a separate control/observability tree, its stage projection must be explicitly derivative and never be the sole freshness token for a pipeline mutation.
5. If authorization scope depends on stage/route, either bind the authorization to the authoritative pipeline revision/digest directly or revalidate authoritative pipeline state at claim time.
6. Dynamic-plan rollback, reset, early completion, and every other protected stage writer must go through the same revision-advancing primitive so no post-projection correction can silently leave the freshness domain behind.

## Existing lock order is usable

The normal daemon wraps the entire `supervisor.run()` drain inside `Manager.pipeline_lock()`, implemented as a `portalocker` advisory file lock. Validator-repair claim inside mission execution then calls `CampaignControlStore.claim_repair_capability()`, which acquires the separate `.manager-control.lock`.

So production already has a nested order of:

`manager_pipeline_lock -> manager-control lock`

for repair missions. A future common protected pipeline mutation should preserve/document that order rather than introduce the reverse order. Web authorization issuance acquires the control-store lock without holding the pipeline lock in the observed path, so it need not create a reverse nested pair.

This reduces migration complexity: an internal `mutate_pipeline_state(..., pipeline_lock_held=True)` can assume the outer pipeline boundary on normal daemon paths and acquire the control lock only when validating an authorization/capability, rather than reacquiring the pipeline lock.

## Regression targets

- Manager advance followed by dynamic-plan rollback: CampaignControl projection must either update to the rollback or be explicitly non-authoritative; no authorization may treat the stale projected advance as current protected stage.
- Force control-projection failure after a successful pipeline stage write; subsequent privileged action must still validate actual pipeline revision/digest.
- Split-root authorization must bind stage-sensitive actions to protected pipeline state, not only execution-workspace frozen tree.
- Direct rollback/reset must increment the same authoritative protected revision used by CAS.
- Lock-order test: `pipeline -> control` succeeds; any attempted `control -> pipeline` nested acquisition fails fast or is forbidden by API contract.
- Existing repair mission does not deadlock after common mutation primitive adoption.

## Scope limits

No concurrent lost update or unauthorized transition was executed. This is a source-level coherence proof: the current code contains an intended sequential path where an advance is projected to CampaignControl and then the actual pipeline is rolled back without another projection. Therefore CampaignControl HEAD is not presently a complete freshness oracle for protected pipeline state.

## Exact continuation

Inspect direct `rollback_stage`, `reset_stage_for_replacement_intent`, completion, and route writers for every path that changes protected pipeline state without advancing CampaignControl, and determine whether any authorization action semantically depends on those fields today. Then convert the writer inventory into a single authoritative `pipeline_revision` contract and decide whether CampaignControl should store only a derivative reference to that revision or whether protected pipeline keys should migrate into its immutable revision tree. Keep the ephemeral-bearer redesign from the previous run separate from this state-coherence question.