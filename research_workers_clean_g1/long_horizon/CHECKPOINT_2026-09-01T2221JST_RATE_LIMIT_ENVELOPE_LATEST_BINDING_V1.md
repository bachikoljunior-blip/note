# CLEAN long_horizon checkpoint — rate-limit envelope latest-blob binding v1

- phase_id: `phase_1_chat_parity`
- root_problem_id: `o-chat-parity-root-v4-zero-work-dependency-zero-quota`
- task_id: `phase1-clean-long-horizon-overrun-recovery`
- effect_chain_id: `clean-rate-limit-envelope-latest-blob-binding-v1`
- enabled_desired: `true`
- global_completion: `false`
- phase1_completion_claimed: `false`
- scheduler_mutation_by_worker: `false`
- termination: `bounded_slice_complete_recurring_open`
- bootstrap_valid: `true`
- transport_mode: `sha_only_main_ref_plus_exact_control_blobs`

## Frozen authority / predecessor

- main ref SHA: `e6cdea27ea9538e4c9b854840cee3fa7fe4e36ed`
- INSTRUCTION_CONTROL_MANIFEST: control_revision `39`, blob `1690e156cccd29044d8afec54ebc151a826506f5`
- RUN_LIFECYCLE: control_revision `1`, blob `8fe5d79365dcd943984d69f4767b2ed0c03fc3ac`
- DESIRED_STATE: control_revision `26`, manifest-declared blob `481660fb6008a57cea162da38439cf115c8d7ebe`
- long_horizon role config: control_revision `17`, config_revision `8`, blob `d790db45343bec399d00c6e9410432963726d72c`
- predecessor LATEST blob at reconstruction: `68bc4cbeaf45ab2b701562b52df556daf96e96be`
- stale predecessor-LATEST negative-control blob: `2421018afc35f21cbd2f99326a1f0df17dca356d`
- preflight path: `research_workers_clean_g1/long_horizon/PREFLIGHT_2026-09-01T2221JST_RATE_LIMIT_ENVELOPE_LATEST_BINDING_V1.md`
- preflight exact-read blob: `2266e5756105f155631da4cc45c93469e7297d87`

## Exact LIVE reconstruction

- path: `research_workers_clean_g1/long_horizon/phase1/LIVE_RATE_LIMIT_STATE.json`
- required blob: `f79a86302e6c4fcb095aec7b22cc6491bb3da20a`
- observed blob: `f79a86302e6c4fcb095aec7b22cc6491bb3da20a`
- blob_match: `true`
- authority_branch: `clean-long-horizon-phase1-active`
- state_sequence: `6`
- plan_generation: `3`
- retry_attempt/max_attempts: `3/3`
- current_plan: `defer_no_retry_plan`
- switch_count: `2`

## Binding predicate tested

The envelope is admissible only when all frozen authority coordinates agree before any LIVE mutation:

`ALLOW := candidate.authority_branch == LIVE.authority_branch AND candidate.live_blob == observed_live_blob AND candidate.plan_generation == LIVE.plan_generation AND candidate.expected_latest_blob == reconstructed_current_latest_blob`.

Positive control:
- authority_branch = `clean-long-horizon-phase1-active`
- live_blob = `f79a86302e6c4fcb095aec7b22cc6491bb3da20a`
- plan_generation = `3`
- expected_latest_blob = `68bc4cbeaf45ab2b701562b52df556daf96e96be`
- result = `ALLOW_REFERENCE`

Negative stale-LATEST control:
- authority_branch = `clean-long-horizon-phase1-active`
- live_blob = `f79a86302e6c4fcb095aec7b22cc6491bb3da20a`
- plan_generation = `3`
- expected_latest_blob = `2421018afc35f21cbd2f99326a1f0df17dca356d`
- result = `REJECT_STALE_LATEST_BINDING`

The negative control differs only in predecessor-LATEST identity. No write to `LIVE_RATE_LIMIT_STATE.json` was issued, so the stale envelope cannot reactivate, mutate or advance generation-3 state in this slice. The positive control is reference evidence only; this leaf intentionally does not consume another retry, wait, backoff, switch or external effect.

## Scope / dependency assessment

- tested scope: deterministic role-local admission binding for the exact sequence-6/generation-3 LIVE state and one stale predecessor-LATEST substitution
- same-run wait/poll/backoff/retry: `false`
- optional second leaf started: `false`
- LIVE mutation issued: `false`
- residual richer-mode/Work/protected-primary/manual-user execution dependency: `false`
- finite monthly/trial/paid quota dependency: `false`
- incremental monetary cost: `0`
- lightweight repository text transport only; repository API volume is not used as compute

## Exact continuation

Next effect_chain_id: `clean-rate-limit-envelope-stale-generation-binding-v1`.

Freshly bootstrap/freeze the four required controls, reconstruct the canonical role branch from the then-current LATEST CAS successor, and persist/exact-read the required preflight before semantic reads. Re-read `research_workers_clean_g1/long_horizon/phase1/LIVE_RATE_LIMIT_STATE.json` only if the predecessor continuation still names exact blob `f79a86302e6c4fcb095aec7b22cc6491bb3da20a`. Hold the then-current LATEST identity and authority branch valid while substituting stale `plan_generation=2` / predecessor LIVE blob `5217ac80d20baad6afd158bd5e39c4b39e9200ff` as the single negative coordinate. Require `REJECT_STALE_GENERATION_BINDING` with zero LIVE mutation, no retry/backoff resampling, no plan reactivation, no scheduler mutation and no second leaf. Persist exact result and a nonempty continuation.
