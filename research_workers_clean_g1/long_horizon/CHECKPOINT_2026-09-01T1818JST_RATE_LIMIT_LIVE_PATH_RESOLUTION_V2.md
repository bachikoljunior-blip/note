# CLEAN long_horizon — bounded Phase-1 slice

- phase_id: `phase_1_chat_parity`
- root_problem_id: `o-chat-parity-root-v4-zero-work-dependency-zero-quota`
- task_id: `phase1-clean-long-horizon-overrun-recovery`
- effect_chain_id: `clean-rate-limit-live-path-resolution-v2`
- enabled_desired: `true`
- global_completion: `false`
- phase1_completion_claimed: `false`
- scheduler_mutation_by_worker: `false`
- bootstrap_valid: `true`
- transport_mode: `exact_blob_two_pass`

## Frozen authority

- INSTRUCTION_CONTROL_MANIFEST: control_revision `38`, blob `f57f55c892bf701aa092f81dd7184e0aec22cfb4`
- RUN_LIFECYCLE: control_revision `1`, blob `8fe5d79365dcd943984d69f4767b2ed0c03fc3ac`
- DESIRED_STATE: control_revision `26`, blob `481660fb6008a57cea162da38439cf115c8d7ebe`
- long_horizon role: control_revision `17`, config_revision `8`, blob `d790db45343bec399d00c6e9410432963726d72c`

## Reconstruction and preflight

- canonical branch: `clean-long-horizon-phase1-active`
- predecessor LATEST blob: `edc5bd0bdaebf4d9152cc760b0088301d7a8c006`
- target blob to resolve: `f79a86302e6c4fcb095aec7b22cc6491bb3da20a`
- persisted preflight: `research_workers_clean_g1/long_horizon/PREFLIGHT_2026-09-01T1818+0900_clean-rate-limit-live-path-resolution-v2.json`
- preflight exact-read blob: `29eedb8fb5fb09a2fff9beec537599a1a7193029`

## Single bounded semantic unit

One authenticated GitHub Contents metadata lookup was issued against only `research_workers_clean_g1/long_horizon` on the canonical role branch. The full connector response remained searchable even though its initial rendering was truncated. Exact search of that response for target blob `f79a86302e6c4fcb095aec7b22cc6491bb3da20a` returned zero matches, so the target is not proven among the top-level entries returned by this lookup.

The same own-namespace lookup exposed six nested subtree identities that can be inspected without reading another role:

- `phase1` tree `ad3fedf412c97a3a11fc2e0a9c974e8114c887fc`
- `effects` tree `0bd721dadb18bfc46f612097196b6945cb4bc361`
- `checkpoints` tree `aa98723ca3c5975d4c6eb52ed6a799233ed31855`
- `consumptions` tree `3408e3a747e18d9e0f5fab1f8db71f3f3935d71e`
- `diagnostics` tree `8d85f8fc37ad2234a8050dc4e4de12948d07c3c3`
- `preflight` tree `007d36799dbf21a8ae1bc18c2a961df44e00ad3e`

The precommitted forecast allowed one metadata lookup plus one exact target read. Because that one lookup did not resolve a path, the slice stopped at its forecast boundary. No second subtree lookup was issued, no guessed path was fetched, and no exact target read was attempted.

## Safety / cost evidence

- LIVE rate-limit state mutation issued: `false`
- same-run wait/poll/backoff: `false`
- same-run retry: `false`
- optional second leaf started: `false`
- cross-role/O/downstream/legacy semantic input consumed: `false`
- residual richer-mode/Work/protected-primary/manual-user execution dependency: `false`
- finite monthly/trial/paid quota dependency: `false`
- incremental monetary cost: `0`
- semantic completion claimed: `false`
- termination: `bounded_slice_complete_recurring_open`

## Exact continuation

Next effect_chain_id: `clean-rate-limit-live-path-phase1-subtree-resolution-v1`.

On the next invocation, freshly bootstrap and freeze the four required controls, reconstruct the canonical role branch from the current CAS successor, and persist/exact-read the required preflight before semantic reads. Then issue exactly one authenticated Git Trees lookup rooted at the already-observed own-namespace `phase1` subtree, predecessor tree SHA `ad3fedf412c97a3a11fc2e0a9c974e8114c887fc`, on `clean-long-horizon-phase1-active`; search only that returned subtree for target blob `f79a86302e6c4fcb095aec7b22cc6491bb3da20a`. If found, exact-read the resolved own-namespace path once and require the same blob, then queue `clean-rate-limit-envelope-latest-blob-binding-v1` for the following invocation. If absent or the subtree identity cannot be freshness-bound to the reconstructed predecessor, checkpoint that exact result and queue the next single-subtree candidate (`effects`, predecessor tree SHA `0bd721dadb18bfc46f612097196b6945cb4bc361`) for a later invocation. Do not inspect a second subtree, mutate LIVE state, wait, poll, retry, mutate the scheduler, or start a second leaf in the same run.
