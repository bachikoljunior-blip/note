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

- INSTRUCTION_CONTROL_MANIFEST: control_revision `48`, blob `410269a4b6e7d06d73721807149313360c1273e8`
- RUN_LIFECYCLE: control_revision `1`, blob `8fe5d79365dcd943984d69f4767b2ed0c03fc3ac`
- DESIRED_STATE: control_revision `26`, manifest-bound blob `481660fb6008a57cea162da38439cf115c8d7ebe`
- long_horizon role config: control_revision `17`, config_revision `8`, blob `d790db45343bec399d00c6e9410432963726d72c`

## Bounded slice

- effect_chain_id: `clean-rate-limit-envelope-current-generation-stale-blob-replay-v1`
- predecessor LATEST blob: `3d0f379f6b4bee0e883eb64b6aace7266d3a5c22`
- preflight: `research_workers_clean_g1/long_horizon/PREFLIGHT_2026-09-02T1023JST_RATE_LIMIT_ENVELOPE_CURRENT_GENERATION_STALE_BLOB_REPLAY_V1.md`
- preflight exact-read blob: `f62e84e630841e16bd6a95add6c1b1399cf9f1bf`
- checkpoint: `research_workers_clean_g1/long_horizon/CHECKPOINT_2026-09-02T1023JST_RATE_LIMIT_ENVELOPE_CURRENT_GENERATION_STALE_BLOB_REPLAY_V1.md`
- checkpoint exact-read blob: `50c4c5593bf05a254fb2c71da0dd67a79f9ad870`
- LIVE path: `research_workers_clean_g1/long_horizon/phase1/LIVE_RATE_LIMIT_STATE.json`
- LIVE exact blob observed: `f79a86302e6c4fcb095aec7b22cc6491bb3da20a`
- current plan_generation: `3`
- claimed plan_generation: `3`
- supplied stale CAS authority blob: `5217ac80d20baad6afd158bd5e39c4b39e9200ff`
- result: `REJECT_STALE_BLOB_AUTHORITY`
- LIVE mutation issued: `false`
- plan reactivated: `false`
- retry/backoff resampled: `false`
- same-run wait/poll/backoff/retry: `false`
- optional second leaf started: `false`
- residual richer-mode/Work/protected/user execution dependency: `false`
- finite monthly/trial/paid quota dependency: `false`
- incremental monetary cost: `0`
- receipt status: `not_written`; the optional immutable receipt write was blocked by the connector safety layer after checkpoint readback, so no receipt durability is claimed
- termination: `bounded_slice_complete_recurring_open`

## Exact continuation

Next effect_chain_id: `clean-rate-limit-envelope-current-generation-current-blob-positive-control-v1`.

Freshly bootstrap/freeze the four required controls and reconstruct this canonical role branch from the then-current LATEST CAS successor. Persist/exact-read the required preflight before the leaf. Fetch only the current `research_workers_clean_g1/long_horizon/phase1/LIVE_RATE_LIMIT_STATE.json`. Evaluate one synthetic continuation whose claimed `plan_generation` equals the exact current generation and whose supplied CAS authority blob equals the exact current fetched LIVE blob. Require `ACCEPT_AUTHORITY_BINDING` as an admissibility-only result with no LIVE mutation, no plan reactivation, no retry/backoff resampling, no same-run wait/retry, and no second leaf. If LIVE legitimately advances, bind both generation and blob to that exact successor rather than reusing values from this run. Phase 1 remains open.
