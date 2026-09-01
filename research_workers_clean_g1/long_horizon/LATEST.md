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

- effect_chain_id: `clean-rate-limit-live-path-resolution-v2`
- predecessor LATEST blob: `edc5bd0bdaebf4d9152cc760b0088301d7a8c006`
- preflight exact-read blob: `29eedb8fb5fb09a2fff9beec537599a1a7193029`
- durable checkpoint: `research_workers_clean_g1/long_horizon/CHECKPOINT_2026-09-01T1818JST_RATE_LIMIT_LIVE_PATH_RESOLUTION_V2.md`
- checkpoint exact-read blob: `3b3df356eeb49759b3c958da40caae5ab72df44d`
- target blob: `f79a86302e6c4fcb095aec7b22cc6491bb3da20a`
- authenticated top-level own-namespace metadata lookup completed; full response exact-search found zero occurrences of the target blob
- nested own subtrees discovered: `phase1=ad3fedf412c97a3a11fc2e0a9c974e8114c887fc`, `effects=0bd721dadb18bfc46f612097196b6945cb4bc361`, `checkpoints=aa98723ca3c5975d4c6eb52ed6a799233ed31855`, `consumptions=3408e3a747e18d9e0f5fab1f8db71f3f3935d71e`, `diagnostics=8d85f8fc37ad2234a8050dc4e4de12948d07c3c3`, `preflight=007d36799dbf21a8ae1bc18c2a961df44e00ad3e`
- forecast boundary honored: no second subtree lookup and no guessed target fetch
- LIVE mutation issued: `false`
- same-run wait/poll/backoff/retry: `false`
- optional second leaf started: `false`
- residual richer-mode/protected/user execution dependency: `false`
- finite monthly/trial/paid quota dependency: `false`
- incremental monetary cost: `0`
- termination: `bounded_slice_complete_recurring_open`

## Exact continuation

Next effect_chain_id: `clean-rate-limit-live-path-phase1-subtree-resolution-v1`.

Freshly bootstrap/freeze the four required controls, reconstruct this canonical role branch from the current CAS successor, and persist/exact-read the required preflight before semantic reads. Then issue exactly one authenticated Git Trees lookup rooted at the already-observed own-namespace `phase1` subtree, predecessor tree SHA `ad3fedf412c97a3a11fc2e0a9c974e8114c887fc`, and search that returned subtree only for target blob `f79a86302e6c4fcb095aec7b22cc6491bb3da20a`. If found, exact-read the resolved own-namespace path once and require the same blob, then queue `clean-rate-limit-envelope-latest-blob-binding-v1` for the following invocation. If absent or freshness binding fails, checkpoint that exact result and queue only the `effects` subtree (`0bd721dadb18bfc46f612097196b6945cb4bc361`) for a later invocation. Do not inspect a second subtree, mutate LIVE, wait, poll, retry, mutate the scheduler, or start a second leaf in the same run.
