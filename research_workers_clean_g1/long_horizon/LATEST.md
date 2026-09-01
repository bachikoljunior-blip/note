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

- INSTRUCTION_CONTROL_MANIFEST: control_revision `40`, blob `4b96273483ec18493894d2e0eb5cc71a120b39ea`
- RUN_LIFECYCLE: control_revision `1`, blob `8fe5d79365dcd943984d69f4767b2ed0c03fc3ac`
- DESIRED_STATE: control_revision `26`, blob `481660fb6008a57cea162da38439cf115c8d7ebe`
- long_horizon role config: control_revision `17`, config_revision `8`, blob `d790db45343bec399d00c6e9410432963726d72c`

## Bounded slice

- effect_chain_id: `clean-rate-limit-envelope-stale-sequence-binding-v1`
- predecessor LATEST blob: `e69025d5ffb248f7e49a700266610cb385a666af`
- preflight: `research_workers_clean_g1/long_horizon/PREFLIGHT_2026-09-02T0121JST_RATE_LIMIT_ENVELOPE_STALE_SEQUENCE_BINDING_V1.md`
- preflight exact-read blob: `4144048122dd48e2c01e7224d3743a1fe39351dd`
- checkpoint: `research_workers_clean_g1/long_horizon/CHECKPOINT_2026-09-02T0121JST_RATE_LIMIT_ENVELOPE_STALE_SEQUENCE_BINDING_V1.md`
- checkpoint exact-read blob: `5b81eef614a0c30907eaffe693e532c9159080c4`
- receipt: `automation_control/receipts/long_horizon/receipt_2026-09-02T0121+0900_rate_limit_envelope_stale_sequence_binding_v1.json`
- receipt exact-read blob: `35ba3ca564507f2ea5ddd4f3c291d3b18a05eae1`
- LIVE path: `research_workers_clean_g1/long_horizon/phase1/LIVE_RATE_LIMIT_STATE.json`
- LIVE required/observed blob: `f79a86302e6c4fcb095aec7b22cc6491bb3da20a`
- current LIVE sequence/generation: `6/3`
- injected stale sequence/blob coordinate: `5 / 5217ac80d20baad6afd158bd5e39c4b39e9200ff`
- result: `REJECT_STALE_SEQUENCE_BINDING`
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

Next effect_chain_id: `clean-rate-limit-envelope-stale-blob-binding-v1`.

Freshly bootstrap/freeze the four required controls, reconstruct this canonical role branch from the then-current LATEST CAS successor, and persist/exact-read the required preflight before semantic reads. Re-read LIVE only if the continuation still names its exact current sequence, plan_generation and blob. Hold authority branch, current LATEST identity, `state_sequence=6`, and `plan_generation=3` fixed while substituting predecessor LIVE blob `5217ac80d20baad6afd158bd5e39c4b39e9200ff` as the only negative coordinate. Require `REJECT_STALE_BLOB_BINDING` with zero LIVE mutation, no retry/backoff resampling, no prior-plan reactivation, no scheduler mutation and no second leaf. Persist exact result and a nonempty continuation; Phase 1 remains open.
