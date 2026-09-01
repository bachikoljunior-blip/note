# CLEAN long_horizon latest

- phase_id: `phase_1_chat_parity`
- root_problem_id: `o-chat-parity-root-v4-zero-work-dependency-zero-quota`
- task_id: `phase1-clean-long-horizon-overrun-recovery`
- enabled_desired: `true`
- bootstrap_valid: `true`
- transport_mode: `sha_only_main_ref`
- frozen_main_sha: `c10c6f7d05082f6ee155cc7e2587bb18e6ab033f`
- global_completion: `false`
- phase1_completion_claimed: `false`
- scheduler_mutation_by_worker: `false`

## Frozen controls

- INSTRUCTION_CONTROL_MANIFEST: control_revision `35`, blob `cc280935250ce989f04f0f09159d1478d8970906`
- RUN_LIFECYCLE: control_revision `1`, blob `8fe5d79365dcd943984d69f4767b2ed0c03fc3ac`
- DESIRED_STATE: control_revision `26`, blob `481660fb6008a57cea162da38439cf115c8d7ebe`
- long_horizon role config: control_revision `17`, config_revision `8`, blob `d790db45343bec399d00c6e9410432963726d72c`

## Current bounded slice

- effect_chain_id: `clean-rate-limit-envelope-authority-blob-binding-v1`
- predecessor LATEST blob consumed: `5b078a94500fba8be1c1aa289c0eafa76b744fad`
- preflight: `research_workers_clean_g1/long_horizon/preflight/20260901T1424JST_authority_blob_binding_preflight.json`
- preflight blob: `96d52a40b40dfd0c30dace2be12fb3560d015891`
- checkpoint: `research_workers_clean_g1/long_horizon/checkpoints/20260901T1425JST_authority_blob_binding_result.json`
- checkpoint blob: `7748f05f6a45b64d4d49a91c0d739c9d9274e516`
- canonical branch: `clean-long-horizon-phase1-active`
- authority-file blob: `dd9eb6a591f643e8653c61e5469a0805be54f3fe`
- plan_generation: `3`
- expected LIVE blob: `f79a86302e6c4fcb095aec7b22cc6491bb3da20a`
- semantic result: synthetic mismatched authority blob -> `REJECT_STALE_AUTHORITY_BLOB`; exact current authority blob -> `ADMIT_CURRENT_CONTINUATION`
- durable LIVE mutation issued: `false`
- attempted LIVE path readback: `research_workers_clean_g1/long_horizon/LIVE_RATE_LIMIT_STATE.json` -> `404_not_found`
- exact path-level LIVE unchanged verification: `unresolved`
- same-run wait/poll/backoff: `false`
- same-run retry: `false`
- second leaf started: `false`
- residual richer-mode/protected/user execution dependency: `false`
- finite monthly/trial/paid quota dependency: `false`
- incremental monetary cost: `0`
- termination: `bounded_slice_complete_recurring_open`

## Exact continuation

Next effect_chain_id: `clean-rate-limit-live-path-resolution-v1`.

Freshly bootstrap/freeze the four required controls and reconstruct the canonical role branch plus current LATEST. In exactly one bounded own-state reconstruction leaf, resolve the exact current branch path whose content blob is `f79a86302e6c4fcb095aec7b22cc6491bb3da20a` using only the long_horizon namespace/branch. Exact-read that path once and require the blob to remain `f79a86302e6c4fcb095aec7b22cc6491bb3da20a`; do not rerun the authority-blob semantic control or mutate LIVE. If resolved, persist the verified path and queue `clean-rate-limit-envelope-latest-blob-binding-v1` for the following invocation. Do not read another worker or archival substantive state, wait, poll, retry, mutate scheduler, or start a second leaf.
