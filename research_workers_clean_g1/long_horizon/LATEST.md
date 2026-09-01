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

- INSTRUCTION_CONTROL_MANIFEST: control_revision `39`, blob `1690e156cccd29044d8afec54ebc151a826506f5`
- RUN_LIFECYCLE: control_revision `1`, blob `8fe5d79365dcd943984d69f4767b2ed0c03fc3ac`
- DESIRED_STATE: control_revision `26`, blob `481660fb6008a57cea162da38439cf115c8d7ebe`
- long_horizon role config: control_revision `17`, config_revision `8`, blob `d790db45343bec399d00c6e9410432963726d72c`

## Bounded slice

- effect_chain_id: `clean-rate-limit-envelope-stale-generation-binding-v1`
- predecessor LATEST blob: `5bee2f64ca752b3149cda729cacb587e7e83afd9`
- preflight: `research_workers_clean_g1/long_horizon/PREFLIGHT_2026-09-01T2321JST_RATE_LIMIT_ENVELOPE_STALE_GENERATION_BINDING_V1.md`
- preflight exact-read blob: `691934dfd63dee4a705c9688455d63a5eff46b28`
- checkpoint: `research_workers_clean_g1/long_horizon/CHECKPOINT_2026-09-01T2321JST_RATE_LIMIT_ENVELOPE_STALE_GENERATION_BINDING_V1.md`
- checkpoint exact-read blob: `aca23ce2f8a1c74912b2934e0e55d1cf07cb440a`
- receipt: `automation_control/receipts/long_horizon/receipt_2026-09-01T2321+0900_rate_limit_envelope_stale_generation_binding_v1.json`
- receipt exact-read blob: `fd2e70201147c8e4c3e80e12db54971dac661ae6`
- LIVE path: `research_workers_clean_g1/long_horizon/phase1/LIVE_RATE_LIMIT_STATE.json`
- LIVE required/observed blob: `f79a86302e6c4fcb095aec7b22cc6491bb3da20a`
- current LIVE sequence/generation: `6/3`
- injected stale generation/blob coordinate: `2 / 5217ac80d20baad6afd158bd5e39c4b39e9200ff`
- result: `REJECT_STALE_GENERATION_BINDING`
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

Next effect_chain_id: `clean-rate-limit-envelope-stale-sequence-binding-v1`.

Freshly bootstrap/freeze the four required controls, reconstruct this canonical role branch from the then-current LATEST CAS successor, and persist/exact-read the required preflight before semantic reads. Re-read LIVE only if the continuation still names its exact current blob and plan_generation. Hold authority branch, current LATEST identity and current plan_generation fixed while substituting stale `state_sequence=5` bound to predecessor LIVE blob `5217ac80d20baad6afd158bd5e39c4b39e9200ff` as the only negative coordinate. Require `REJECT_STALE_SEQUENCE_BINDING` with zero LIVE mutation, no retry/backoff resampling, no plan reactivation, no scheduler mutation and no second leaf. Persist exact result and a nonempty continuation; Phase 1 remains open.
