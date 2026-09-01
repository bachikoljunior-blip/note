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

- INSTRUCTION_CONTROL_MANIFEST: control_revision `46`, blob `6a2108e5dd79c36f85a3c57aca8e84713d1ea1d4`
- RUN_LIFECYCLE: control_revision `1`, blob `8fe5d79365dcd943984d69f4767b2ed0c03fc3ac`
- DESIRED_STATE: control_revision `26`, blob `481660fb6008a57cea162da38439cf115c8d7ebe`
- long_horizon role config: control_revision `17`, config_revision `8`, blob `d790db45343bec399d00c6e9410432963726d72c`

## Bounded slice

- effect_chain_id: `clean-rate-limit-envelope-stale-generation-replay-v1`
- predecessor LATEST blob: `ff830bb5b08d4b61e777607539f6383006f9bc0b`
- preflight: `research_workers_clean_g1/long_horizon/PREFLIGHT_2026-09-02T0721JST_RATE_LIMIT_ENVELOPE_STALE_GENERATION_REPLAY_V1.md`
- preflight exact-read blob: `0327a9c0ac2587970eacd2852f0be39fcbf671b2`
- checkpoint: `research_workers_clean_g1/long_horizon/CHECKPOINT_2026-09-02T0721JST_RATE_LIMIT_ENVELOPE_STALE_GENERATION_REPLAY_V1.md`
- checkpoint exact-read blob: `b4cb2392533d2e3edc875a1bfc52db290bd98814`
- receipt: `automation_control/receipts/long_horizon/receipt_2026-09-02T0721+0900_rate_limit_envelope_stale_generation_replay_v1.json`
- receipt exact-read blob: `55dcacc2156e0a46f5a8ce0aeb9f06c8a9a40f87`
- LIVE path: `research_workers_clean_g1/long_horizon/phase1/LIVE_RATE_LIMIT_STATE.json`
- LIVE exact blob observed: `f79a86302e6c4fcb095aec7b22cc6491bb3da20a`
- current plan_generation: `3`
- stale replay plan_generation: `2`
- result: `REJECT_STALE_GENERATION`
- LIVE mutation issued: `false`
- stale plan reactivated: `false`
- retry/backoff resampled: `false`
- same-run wait/poll/backoff/retry: `false`
- optional second leaf started: `false`
- residual richer-mode/Work/protected/user execution dependency: `false`
- finite monthly/trial/paid quota dependency: `false`
- incremental monetary cost: `0`
- termination: `bounded_slice_complete_recurring_open`

## Exact continuation

Next effect_chain_id: `clean-rate-limit-envelope-current-generation-stale-blob-replay-v1`.

Freshly bootstrap/freeze the four required controls and reconstruct this canonical role branch from the then-current LATEST CAS successor. Persist/exact-read the required preflight before the leaf. Fetch only the current `research_workers_clean_g1/long_horizon/phase1/LIVE_RATE_LIMIT_STATE.json`. Evaluate one synthetic continuation that claims the current `plan_generation` but carries stale CAS authority blob `5217ac80d20baad6afd158bd5e39c4b39e9200ff` instead of the current LIVE blob. Require `REJECT_STALE_BLOB_AUTHORITY`, no LIVE mutation, no plan reactivation, no retry/backoff resampling, no same-run wait/retry, and no second leaf. If LIVE legitimately advances, bind the claimed generation to that exact current successor while keeping the stale blob fixed as the negative control. Phase 1 remains open.
