# CLEAN long_horizon latest

- phase_id: `phase_1_chat_parity`
- root_problem_id: `o-chat-parity-root-v4-zero-work-dependency-zero-quota`
- task_id: `phase1-clean-long-horizon-overrun-recovery`
- enabled_desired: `true`
- global_completion: `false`
- phase1_completion_claimed: `false`
- scheduler_mutation_by_worker: `false`
- bootstrap_valid: `true`
- transport_mode: `exact_blob_two_pass`

## Frozen controls

- INSTRUCTION_CONTROL_MANIFEST: control_revision `43`, blob `c9c8bdb368dfd2270bb18b2c5c6093001ec97ee6`
- RUN_LIFECYCLE: control_revision `1`, blob `8fe5d79365dcd943984d69f4767b2ed0c03fc3ac`
- DESIRED_STATE: control_revision `26`, blob `481660fb6008a57cea162da38439cf115c8d7ebe`
- long_horizon role config: control_revision `17`, config_revision `8`, blob `d790db45343bec399d00c6e9410432963726d72c`

## Bounded slice

- effect_chain_id: `clean-rate-limit-envelope-stale-blob-binding-v1`
- predecessor LATEST blob: `ce539dea4696bf23c9f537e97500bc69a18e54dc`
- preflight: `research_workers_clean_g1/long_horizon/PREFLIGHT_2026-09-02T0419JST_RATE_LIMIT_ENVELOPE_STALE_BLOB_BINDING_V1.md`
- preflight exact-read blob: `f7f8586862f0ea02a770a700d0b7f2ceddd636f0`
- checkpoint: `research_workers_clean_g1/long_horizon/CHECKPOINT_2026-09-02T0419JST_RATE_LIMIT_ENVELOPE_STALE_BLOB_BINDING_V1.md`
- checkpoint exact-read blob: `02537177803954c74a0fcec2f1fc43bc032386d9`
- receipt: `automation_control/receipts/long_horizon/receipt_2026-09-02T0419+0900_rate_limit_envelope_stale_blob_binding_v1.json`
- receipt exact-read blob: `56ada4d57c36ef0503f25bbd9fbe8c72deee1f74`
- LIVE path: `research_workers_clean_g1/long_horizon/phase1/LIVE_RATE_LIMIT_STATE.json`
- LIVE required/observed blob: `f79a86302e6c4fcb095aec7b22cc6491bb3da20a`
- current LIVE sequence/generation: `6/3`
- injected stale blob coordinate: `5217ac80d20baad6afd158bd5e39c4b39e9200ff`
- result: `REJECT_STALE_BLOB_BINDING`
- LIVE mutation issued: `false`
- retry/backoff resampled: `false`
- prior plan reactivated: `false`
- same-run wait/poll/backoff/retry: `false`
- optional second leaf started: `false`
- residual richer-mode/Work/protected/user execution dependency: `false`
- finite monthly/trial/paid quota dependency: `false`
- incremental monetary cost: `0`
- termination: `bounded_slice_complete_recurring_open`

## Exact continuation

Next effect_chain_id: `clean-rate-limit-envelope-current-valid-binding-v1`.

Freshly bootstrap/freeze the four required controls, reconstruct this canonical role branch from the then-current LATEST CAS successor, and persist/exact-read the required preflight before the leaf. Re-read LIVE only if the continuation still names exact current `state_sequence=6`, `plan_generation=3`, and LIVE blob `f79a86302e6c4fcb095aec7b22cc6491bb3da20a`. Use those exact current coordinates as the positive control and require `ACCEPT_CURRENT_BINDING` without mutating LIVE, retry/backoff state, plan generation, scheduler, or starting a second leaf. If any coordinate has advanced, persist the exact mismatch and rebind the positive-control child on the next invocation. Phase 1 remains open.
