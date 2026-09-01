# CLEAN long_horizon latest

- phase_id: `phase_1_chat_parity`
- root_problem_id: `o-chat-parity-root-v4-zero-work-dependency-zero-quota`
- task_id: `phase1-clean-long-horizon-overrun-recovery`
- enabled_desired: `true`
- global_completion: `false`
- phase1_completion_claimed: `false`
- scheduler_mutation_by_worker: `false`
- bootstrap_valid: `true`
- transport_mode: `sha_only_main_ref_plus_exact_blob_crosscheck`

## Frozen controls

- INSTRUCTION_CONTROL_MANIFEST: control_revision `45`, blob `06557aeef00aeb74dc2148cc48873ca6227170fb`
- RUN_LIFECYCLE: control_revision `1`, blob `8fe5d79365dcd943984d69f4767b2ed0c03fc3ac`
- DESIRED_STATE: control_revision `26`, blob `481660fb6008a57cea162da38439cf115c8d7ebe`
- long_horizon role config: control_revision `17`, config_revision `8`, blob `d790db45343bec399d00c6e9410432963726d72c`
- frozen main SHA: `681c5a5558239c24993d9e44b56ee02adc8ede40`

## Bounded slice

- effect_chain_id: `clean-rate-limit-envelope-authority-file-binding-v1`
- predecessor LATEST blob: `735c4140fb734edb10f34662f7dff1c334a54ab5`
- preflight: `research_workers_clean_g1/long_horizon/PREFLIGHT_2026-09-02T0621JST_RATE_LIMIT_ENVELOPE_AUTHORITY_FILE_BINDING_V1.md`
- preflight exact-read blob: `b4a33b6505f5d29a53522f3603a4a4bbad563559`
- checkpoint: `research_workers_clean_g1/long_horizon/CHECKPOINT_2026-09-02T0621JST_RATE_LIMIT_ENVELOPE_AUTHORITY_FILE_BINDING_V1.md`
- checkpoint exact-read blob: `aeb6053643831a6b94db5e09667bfb726d2a6cb4`
- receipt: `automation_control/receipts/long_horizon/receipt_2026-09-02T0621+0900_rate_limit_envelope_authority_file_binding_v1.json`
- receipt exact-read blob: `a4dd9a58f05362687fbc264a7fb51fa9708df3ed`
- LIVE path: `research_workers_clean_g1/long_horizon/phase1/LIVE_RATE_LIMIT_STATE.json`
- LIVE exact blob: `f79a86302e6c4fcb095aec7b22cc6491bb3da20a`
- authority path: `research_workers_clean_g1/long_horizon/phase1/BRANCH_AUTHORITY.json`
- authority exact blob: `dd9eb6a591f643e8653c61e5469a0805be54f3fe`
- result: `ACCEPT_CURRENT_AUTHORITY_BINDING`
- LIVE authority_file_blob matched exact authority blob: `true`
- LIVE authority_branch matched canonical role branch: `true`
- LIVE authority_generation matched authority record generation: `true`
- LIVE mutation issued: `false`
- retry/backoff resampled: `false`
- plan generation mutated: `false`
- same-run wait/poll/backoff/retry: `false`
- optional second leaf started: `false`
- residual richer-mode/Work/protected/user execution dependency: `false`
- finite monthly/trial/paid quota dependency: `false`
- incremental monetary cost: `0`
- termination: `bounded_slice_complete_recurring_open`

## Exact continuation

Next effect_chain_id: `clean-rate-limit-envelope-stale-generation-replay-v1`.

Freshly bootstrap/freeze the four required controls and reconstruct this canonical role branch from the then-current LATEST CAS successor. Persist/exact-read the required preflight before the leaf. Fetch only the current `research_workers_clean_g1/long_horizon/phase1/LIVE_RATE_LIMIT_STATE.json`. Evaluate one synthetic stale continuation carrying predecessor `plan_generation=2` and predecessor blob `5217ac80d20baad6afd158bd5e39c4b39e9200ff` against the current state. Require `REJECT_STALE_GENERATION` because the current generation is newer, and require no LIVE mutation, no reactivation of `compact_plan`, no retry/backoff resampling, no same-run wait/retry, and no second leaf. If LIVE has legitimately advanced, bind the stale replay to that exact current successor while preserving the monotonic-generation rejection property. Phase 1 remains open.
