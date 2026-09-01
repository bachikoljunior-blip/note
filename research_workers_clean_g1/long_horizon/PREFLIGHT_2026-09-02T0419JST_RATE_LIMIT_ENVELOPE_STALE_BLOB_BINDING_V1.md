# CLEAN long_horizon preflight — rate-limit envelope stale blob binding v1

- phase_id: `phase_1_chat_parity`
- root_problem_id: `o-chat-parity-root-v4-zero-work-dependency-zero-quota`
- task_id: `phase1-clean-long-horizon-overrun-recovery`
- role: `long_horizon`
- enabled_desired: `true`
- global_completion: `false`
- phase1_completion_claimed: `false`
- scheduler_mutation_by_worker: `false`
- bootstrap_valid: `true`
- transport_mode: `exact_blob_two_pass`

## Frozen authority tuple

- `automation_control/INSTRUCTION_CONTROL_MANIFEST.json`: control_revision `43`, blob `c9c8bdb368dfd2270bb18b2c5c6093001ec97ee6`
- `automation_control/RUN_LIFECYCLE.json`: control_revision `1`, blob `8fe5d79365dcd943984d69f4767b2ed0c03fc3ac`
- `automation_control/DESIRED_STATE.json`: control_revision `26`, blob `481660fb6008a57cea162da38439cf115c8d7ebe`
- `automation_control/roles/long_horizon.json`: control_revision `17`, config_revision `8`, blob `d790db45343bec399d00c6e9410432963726d72c`
- root/config pass-1 and pass-2 identities matched before own-state reconstruction.

## Selected single effect chain

- effect_chain_id: `clean-rate-limit-envelope-stale-blob-binding-v1`
- canonical role branch: `clean-long-horizon-phase1-active`
- branch head observed before reconstruction: `d652018ad0278723737e7556803e374913cd7d3e`
- predecessor LATEST blob: `ce539dea4696bf23c9f537e97500bc69a18e54dc`
- predecessor LIVE identity named by continuation: state_sequence `6`, plan_generation `3`, current blob `f79a86302e6c4fcb095aec7b22cc6491bb3da20a`
- stale negative blob coordinate: `5217ac80d20baad6afd158bd5e39c4b39e9200ff`

## Planned atomic boundary

Re-read only the named LIVE path. Proceed only if its exact blob, `state_sequence=6`, and `plan_generation=3` still match the continuation. Hold authority branch, current LATEST identity, state sequence, and plan generation fixed while substituting only the predecessor LIVE blob as the negative coordinate. Expected control result is `REJECT_STALE_BLOB_BINDING`. Issue no LIVE mutation; do not resample retry/backoff; do not reactivate a prior plan; do not mutate scheduler; do not start a second leaf.

## Forecast / switch threshold

- semantic soft stop: `25s`
- checkpoint must start by: `30s`
- normal return target: `40s`
- absolute do-not-intentionally-cross: `45s`
- bounded forecast: one exact LIVE read + one local identity comparison + one compact checkpoint/receipt/LATEST chain.
- switch criterion: any LIVE blob/sequence/generation mismatch other than the intentionally substituted stale-blob coordinate becomes a bounded `authority_or_state_mismatch` result; persist exact evidence and continuation without retry or second leaf.

Residual richer-mode/Work/protected/user execution dependency: `false` for this mechanism-level repository-state control.
Finite monthly/trial/paid quota dependency: `false` for the tested lightweight repository-transport path; no hosted compute/storage quota is consumed.
Incremental monetary cost: `0`.
