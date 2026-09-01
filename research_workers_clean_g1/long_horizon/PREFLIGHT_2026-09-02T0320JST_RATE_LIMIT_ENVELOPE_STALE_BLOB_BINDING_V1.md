# CLEAN long_horizon preflight — stale blob binding v1

- phase_id: `phase_1_chat_parity`
- root_problem_id: `o-chat-parity-root-v4-zero-work-dependency-zero-quota`
- task_id: `phase1-clean-long-horizon-overrun-recovery`
- effect_chain_id: `clean-rate-limit-envelope-stale-blob-binding-v1`
- bootstrap_valid: `true`
- transport_mode: `exact_blob_two_pass`
- enabled_desired: `true`
- global_completion: `false`
- phase1_completion_claimed: `false`
- scheduler_mutation_by_worker: `false`

## Frozen authority tuple

- `automation_control/INSTRUCTION_CONTROL_MANIFEST.json`: control_revision `42`, fetched current response sha `89f1fb9230d1531c4d27e6037b9baf74fc9ca206`; manifest-declared long_horizon control blob `d790db45343bec399d00c6e9410432963726d72c`
- `automation_control/RUN_LIFECYCLE.json`: control_revision `1`, blob `8fe5d79365dcd943984d69f4767b2ed0c03fc3ac`
- `automation_control/DESIRED_STATE.json`: control_revision `26`, blob `481660fb6008a57cea162da38439cf115c8d7ebe`
- `automation_control/roles/long_horizon.json`: control_revision `17`, config_revision `8`, blob `d790db45343bec399d00c6e9410432963726d72c`
- two-pass root/config identity matched exactly before own-state semantic work.

## Exact predecessor/frontier

- authority branch: `clean-long-horizon-phase1-active`
- predecessor LATEST blob: `ce539dea4696bf23c9f537e97500bc69a18e54dc`
- predecessor effect_chain_id: `clean-rate-limit-envelope-stale-sequence-binding-v1`
- required current LIVE coordinate from predecessor: `state_sequence=6`, `plan_generation=3`, blob `f79a86302e6c4fcb095aec7b22cc6491bb3da20a`
- only injected negative coordinate: predecessor LIVE blob `5217ac80d20baad6afd158bd5e39c4b39e9200ff`

## Planned atomic boundary

Read the current role-local LIVE state exactly once. Proceed only if sequence `6`, plan_generation `3`, and current blob `f79a86302e6c4fcb095aec7b22cc6491bb3da20a` all still match. Then issue one role-local GitHub Contents API update attempt against the same LIVE path using stale blob `5217ac80d20baad6afd158bd5e39c4b39e9200ff` as the required CAS precondition and otherwise preserve current content. Accept only a stale-blob rejection with no LIVE mutation. Perform at most one immediate LIVE reread after the conflict to prove the current blob/state remained unchanged. Do not retry, wait, poll, resample backoff, reactivate an earlier plan, mutate the scheduler, or start a second leaf.

## Forecast / switch threshold

- leaf budget class: one stale-blob defense test
- switch threshold: any mismatch in authority branch, predecessor LATEST identity, LIVE sequence, plan_generation, or current LIVE blob before the probe => abort substantive mutation and persist `REJECT_AUTHORITY_OR_STATE_DRIFT` continuation for next invocation.
- CAS conflict from the intentionally stale blob is the expected terminal observation for this slice; no same-run retry is permitted.
- after the observation, reserve remaining budget for checkpoint + LATEST CAS/readback only.
