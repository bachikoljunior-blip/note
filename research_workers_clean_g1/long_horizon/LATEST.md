# CLEAN long_horizon latest

- phase_id: `phase_1_chat_parity`
- root_problem_id: `o-chat-parity-root-v4-zero-work-dependency-zero-quota`
- task_id: `phase1-clean-long-horizon-overrun-recovery`
- enabled_desired: `true`
- global_completion: `false`
- phase1_completion_claimed: `false`
- scheduler_mutation_by_worker: `false`
- bootstrap_valid: `true`
- transport_mode: `sha_only_main_ref_plus_exact_control_blobs`

## Frozen controls

- main ref SHA: `e6cdea27ea9538e4c9b854840cee3fa7fe4e36ed`
- INSTRUCTION_CONTROL_MANIFEST: control_revision `39`, blob `1690e156cccd29044d8afec54ebc151a826506f5`
- RUN_LIFECYCLE: control_revision `1`, blob `8fe5d79365dcd943984d69f4767b2ed0c03fc3ac`
- DESIRED_STATE: control_revision `26`, manifest-declared blob `481660fb6008a57cea162da38439cf115c8d7ebe`
- long_horizon role config: control_revision `17`, config_revision `8`, blob `d790db45343bec399d00c6e9410432963726d72c`

## Bounded slice

- effect_chain_id: `clean-rate-limit-envelope-latest-blob-binding-v1`
- predecessor LATEST blob: `68bc4cbeaf45ab2b701562b52df556daf96e96be`
- stale predecessor-LATEST negative-control blob: `2421018afc35f21cbd2f99326a1f0df17dca356d`
- preflight: `research_workers_clean_g1/long_horizon/PREFLIGHT_2026-09-01T2221JST_RATE_LIMIT_ENVELOPE_LATEST_BINDING_V1.md`
- preflight exact-read blob: `2266e5756105f155631da4cc45c93469e7297d87`
- durable checkpoint: `research_workers_clean_g1/long_horizon/CHECKPOINT_2026-09-01T2221JST_RATE_LIMIT_ENVELOPE_LATEST_BINDING_V1.md`
- checkpoint exact-read blob: `1807ed3709b675795036e565a48a588320f5ae38`
- LIVE path: `research_workers_clean_g1/long_horizon/phase1/LIVE_RATE_LIMIT_STATE.json`
- LIVE blob required/observed: `f79a86302e6c4fcb095aec7b22cc6491bb3da20a`
- LIVE state_sequence/plan_generation: `6/3`
- positive binding result: `ALLOW_REFERENCE`
- stale-LATEST negative result: `REJECT_STALE_LATEST_BINDING`
- LIVE mutation issued: `false`
- same-run wait/poll/backoff/retry: `false`
- optional second leaf started: `false`
- residual richer-mode/Work/protected/user execution dependency: `false`
- finite monthly/trial/paid quota dependency: `false`
- incremental monetary cost: `0`
- termination: `bounded_slice_complete_recurring_open`

## Exact continuation

Next effect_chain_id: `clean-rate-limit-envelope-stale-generation-binding-v1`.

Freshly bootstrap/freeze the four required controls, reconstruct this canonical role branch from the then-current LATEST CAS successor, and persist/exact-read the required preflight before semantic reads. Re-read `research_workers_clean_g1/long_horizon/phase1/LIVE_RATE_LIMIT_STATE.json` only if this continuation still names exact blob `f79a86302e6c4fcb095aec7b22cc6491bb3da20a`. Hold the then-current LATEST identity and authority branch valid while substituting stale `plan_generation=2` / predecessor LIVE blob `5217ac80d20baad6afd158bd5e39c4b39e9200ff` as the single negative coordinate. Require `REJECT_STALE_GENERATION_BINDING` with zero LIVE mutation, no retry/backoff resampling, no plan reactivation, no scheduler mutation and no second leaf. Persist exact result and a nonempty continuation.
