# CLEAN long_horizon preflight — rate-limit envelope latest-blob binding v1

- phase_id: `phase_1_chat_parity`
- root_problem_id: `o-chat-parity-root-v4-zero-work-dependency-zero-quota`
- task_id: `phase1-clean-long-horizon-overrun-recovery`
- effect_chain_id: `clean-rate-limit-envelope-latest-blob-binding-v1`
- enabled_desired: `true`
- global_completion: `false`
- phase1_completion_claimed: `false`
- scheduler_mutation_by_worker: `false`
- bootstrap_valid: `true`
- transport_mode: `sha_only_main_ref_plus_exact_control_blobs`

## Frozen authority tuple

- main ref SHA: `e6cdea27ea9538e4c9b854840cee3fa7fe4e36ed`
- INSTRUCTION_CONTROL_MANIFEST: control_revision `39`, blob `1690e156cccd29044d8afec54ebc151a826506f5`
- RUN_LIFECYCLE: control_revision `1`, blob `8fe5d79365dcd943984d69f4767b2ed0c03fc3ac`
- DESIRED_STATE: control_revision `26`, manifest-declared blob `481660fb6008a57cea162da38439cf115c8d7ebe`
- long_horizon role config: control_revision `17`, config_revision `8`, blob `d790db45343bec399d00c6e9410432963726d72c`

## Reconstructed own frontier

- canonical role branch: `clean-long-horizon-phase1-active`
- current LATEST blob: `68bc4cbeaf45ab2b701562b52df556daf96e96be`
- predecessor LATEST blob named by prior slice: `2421018afc35f21cbd2f99326a1f0df17dca356d`
- required LIVE input path: `research_workers_clean_g1/long_horizon/phase1/LIVE_RATE_LIMIT_STATE.json`
- required LIVE input blob: `f79a86302e6c4fcb095aec7b22cc6491bb3da20a`

## Planned atomic boundary

Read the LIVE input exactly once and only proceed if its blob is still the required value. Evaluate a pure envelope-authority predicate that requires both the current LIVE generation identity and the current LATEST blob identity. Positive control binds to current LATEST blob `68bc4cbeaf45ab2b701562b52df556daf96e96be`; negative control substitutes stale predecessor LATEST blob `2421018afc35f21cbd2f99326a1f0df17dca356d`. Require the stale control to reject with zero LIVE mutation. Persist the decision, exact continuation, updated LATEST pointer, and immutable own receipt; start no second leaf.

## Forecast / switch threshold

- forecast class: `small deterministic own-state binding test`
- remaining semantic reads planned: `1`
- repository writes planned after this preflight: `3`
- same-run wait/poll/backoff/retry: `0`
- switch criterion: if LIVE blob, authority identity, or write CAS does not match exactly, do not repair or retry in-run; persist the smallest safe diagnostic if possible and return recurring-open.
