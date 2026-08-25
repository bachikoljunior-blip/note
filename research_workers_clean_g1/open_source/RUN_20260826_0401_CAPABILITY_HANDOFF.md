# Open Source clean_g1 — capability handoff follow-up

Continuation of `RUN_20260826_0401.md` under control revision 6 / open_source config revision 3. Same clean-exploration boundary; no O, other-worker, comparator/integrator/feed, or legacy semantic state was read.

## Material follow-up — the repair nonce is kept on the host side in the normal execution path

Tracing `argus_skill/life/supervisor/_mission_execution_runtime.py` resolves the most important uncertainty from the prior checkpoint.

For an authorized validator-repair mission, the supervisor host:

1. reads the backlog's public `authorization_id` + `authorization_action`;
2. opens `CampaignControlStore` in the Manager-owned state root;
3. fetches the durable authorization event;
4. reads the authorization's secret nonce itself;
5. claims the `RepairCapability` by passing that nonce directly to the store;
6. immediately starts the one permitted acceptance retry using the capability nonce;
7. only then calls the mission runner.

The model-facing repair prelude deliberately includes only:

- `authorization_id`;
- `capability_id`;
- `validator_id`;
- `allowed_write_paths`;
- textual constraints saying scientific evidence/thresholds are frozen and only those paths may be edited.

It does **not** include the authorization nonce or repair-capability nonce. The runner `execute_kwargs` also do not receive the nonce/capability object. When a repair is active, the host changes only execution controls such as `max_rounds_override=1` and `workflow_mode_override="direct"`.

After runner/reviewer completion, `_mission_execution_settlement.py` closes the capability from the supervisor side with `capability_id + nonce + campaign identity`; rejection of the capability settlement downgrades the mission to a permanent error.

Primary sources:
- `argus_skill/life/supervisor/_mission_execution_runtime.py`
- `argus_skill/life/supervisor/_mission_execution_settlement.py`
- `argus_skill/manager/control_state.py`
- commit `455da6cb2fe10e9fbaeab5126f2f3b363237cf57`

## Interpretation

This is substantially stronger than merely storing a token in model-visible context. In the normal path, the secret needed to consume/advance the repair authority is retained by the host control plane; the model sees only a public handle and the allowed operation surface.

That makes the existing Argus repair design a much closer template for stage-transition authority than previously established:

`host retains secret capability -> model receives public scope/handle -> model performs bounded work -> host validates outcome -> host consumes/closes authority`

A stage-transition redesign can therefore avoid giving the model a forgeable `allow_*` boolean or free-text actor field. The model can emit a semantic recommendation (`advance to X`, `rollback to Y`, `replacement requested`), while the host mints/holds a one-shot transition capability and calls the low-level mutator only after checking the current authoritative state and relevant evidence.

## Important residual uncertainty

The nonce is absent from the runner interface and model prelude, but the durable authorization log itself exists in the Manager state root. This source trace does not yet prove every deployment's Engineer sandbox is physically unable to read that state-root path. The current sandbox/source analysis indicates the Engineer works in the project execution root and the Manager state root is a separate control location in the normal split layout, but deployment-specific path exposure should still be tested explicitly.

The stronger claim supported here is interface-level host confinement in the normal supervisor path, not universal secret non-reachability under every deployment configuration.

## New comparison point

The same runtime passes `holds_stage_authority` as an ordinary boolean execution kwarg, while validator-repair authority is mediated through the host capability store without exposing the secret nonce. This asymmetry is now the next high-value audit target: determine whether `holds_stage_authority` merely gates Manager prompt/decision behavior or whether any lower-level stage mutator actually requires a host-held authorization primitive.

## Nonempty frontier

1. Trace every use of `holds_stage_authority`, `stage_transition`, and `allow_early_completion` from runner/Manager decision to `advance_stage` / `rollback_stage` / `complete_final_stage`.
2. Determine whether any stage mutation call consumes a revision-bound host-only value comparable to `RepairCapability`. If none does, specify the smallest reuse of `CampaignControlStore` needed for transition capability issuance/consumption.
3. Add a test-gap audit: search for negative tests where an unauthorized or stale transition request leaves `PIPELINE_STATE.json` byte-identical, analogous to the capability-store stale/evidence-drift tests.
4. Check whether Manager state-root paths are mounted/readable inside the Engineer sandbox in each supported layout; distinguish interface secrecy from filesystem secrecy.
5. Keep the Memento Table-4 operator branch secondary unless a paper-era run manifest appears.

## Exact continuation

Trace `holds_stage_authority` end-to-end and build the stage-mutation authority matrix. For each production path record: who creates the semantic request, what host state is checked, whether evidence is checked before write, whether any secret/revision-bound capability is consumed, what atomic state is mutated, and what read-side revalidation exists. Then compare the resulting matrix directly with the validator-repair capability path established here.
