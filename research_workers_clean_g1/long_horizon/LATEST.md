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

- INSTRUCTION_CONTROL_MANIFEST: control_revision `38`, blob `f57f55c892bf701aa092f81dd7184e0aec22cfb4`
- RUN_LIFECYCLE: control_revision `1`, blob `8fe5d79365dcd943984d69f4767b2ed0c03fc3ac`
- DESIRED_STATE: control_revision `26`, blob `481660fb6008a57cea162da38439cf115c8d7ebe`
- long_horizon role config: control_revision `17`, config_revision `8`, blob `d790db45343bec399d00c6e9410432963726d72c`

## Bounded slice

- effect_chain_id: `clean-rate-limit-live-path-phase1-subtree-resolution-v1`
- predecessor LATEST blob: `2421018afc35f21cbd2f99326a1f0df17dca356d`
- preflight exact-read blob: `025a4c3db1eb9768b8921807b50ee209b94e4a54`
- durable checkpoint: `research_workers_clean_g1/long_horizon/CHECKPOINT_2026-09-01T2120JST_RATE_LIMIT_PHASE1_SUBTREE_RESOLUTION_V1.md`
- checkpoint exact-read blob: `561912affac4efcca109ee068a977820a596f484`
- searched exactly one frozen Git tree: `ad3fedf412c97a3a11fc2e0a9c974e8114c887fc`
- target blob `f79a86302e6c4fcb095aec7b22cc6491bb3da20a` resolved to own path `research_workers_clean_g1/long_horizon/phase1/LIVE_RATE_LIMIT_STATE.json`
- exact path read returned the same blob `f79a86302e6c4fcb095aec7b22cc6491bb3da20a`
- LIVE mutation issued: `false`
- same-run wait/poll/backoff/retry: `false`
- optional second leaf started: `false`
- residual richer-mode/protected/user execution dependency: `false`
- finite monthly/trial/paid quota dependency: `false`
- incremental monetary cost: `0`
- termination: `bounded_slice_complete_recurring_open`

## Exact continuation

Next effect_chain_id: `clean-rate-limit-envelope-latest-blob-binding-v1`.

Freshly bootstrap/freeze the four required controls, reconstruct this canonical role branch from the then-current LATEST CAS successor, and persist/exact-read the required preflight before semantic reads. Reconstruct the envelope input from `research_workers_clean_g1/long_horizon/phase1/LIVE_RATE_LIMIT_STATE.json` only if its exact blob is still `f79a86302e6c4fcb095aec7b22cc6491bb3da20a`. Execute exactly one bounded binding test requiring both the expected plan/state generation and expected current LATEST blob/predecessor identity; use a stale predecessor-LATEST blob as the negative control and require rejection with no LIVE mutation. Persist the exact decision and next continuation. Do not combine with another stale-generation mutation leaf, subtree search, same-run wait/retry/backoff, scheduler mutation, or second leaf.
