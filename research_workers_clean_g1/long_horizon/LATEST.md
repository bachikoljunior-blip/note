# Long Horizon clean_g1 — LATEST

- phase_id: `phase_1_chat_parity`
- root_problem_id: `o-chat-parity-root-v4-zero-work-dependency-zero-quota`
- task_id: `phase1-clean-long-horizon-overrun-recovery`
- role: `long_horizon`
- enabled_desired: `true`
- bootstrap_valid: `true`
- transport_mode: `exact_blob_two_pass`
- termination: `bounded_slice_complete_recurring_open`
- global_completion: `false`
- phase1_completion_claimed: `false`
- scheduler_mutation_by_worker: `false`

Frozen controls: manifest control29/blob `0f54cb6b6fb4bc2a52af66851032d3b1e2bc98f7`; RUN_LIFECYCLE control1/blob `8fe5d79365dcd943984d69f4767b2ed0c03fc3ac`; DESIRED_STATE control26/blob `481660fb6008a57cea162da38439cf115c8d7ebe`; long_horizon control17/config8/blob `d790db45343bec399d00c6e9410432963726d72c`.

Predecessor LATEST blob consumed: `3df945236912bca8fb990c24346530d6012b69a5`.
Preflight: `research_workers_clean_g1/long_horizon/preflight/20260901T0521JST_stale_blob_replay_preflight.json`, blob `1a89d75071036c4fa91f357df9c49c5ffb73e1f0`.
Authoritative current checkpoint: `research_workers_clean_g1/long_horizon/checkpoints/20260901T0523JST_stale_blob_replay_compact.json`, blob `17aa91ef3ffedbd71abb7b8e73d852f9cd39f0ea`.

Bounded leaf result: canonical LIVE state exact-read before and after at blob `f79a86302e6c4fcb095aec7b22cc6491bb3da20a`, `state_sequence=6`, `plan_generation=3`. A continuation with current generation `3` but stale prior-state blob `5217ac80d20baad6afd158bd5e39c4b39e9200ff` was rejected as `REJECT_STALE_STATE_BLOB`; generation `3` plus current LIVE blob was admitted. No LIVE mutation, retry attempt 4, backoff resampling, wait/poll, second leaf, scheduler mutation, richer-mode/Work, protected-primary/manual execution, finite quota, or incremental monetary cost was introduced.

## Exact nonempty continuation
Next effect_chain_id: `clean-rate-limit-envelope-authority-binding-v1`.

Freshly bootstrap/freeze required controls; reconstruct this pointer and canonical `research_workers_clean_g1/long_horizon/phase1/BRANCH_AUTHORITY.json`; exact-read canonical `research_workers_clean_g1/long_horizon/phase1/LIVE_RATE_LIMIT_STATE.json`. In exactly one bounded in-memory control, hold `plan_generation=3` and the current LIVE blob fixed, present a non-current `authority_file_blob` in the continuation envelope and require rejection by the envelope/authority binding; compare the exact current authority file blob `dd9eb6a591f643e8653c61e5469a0805be54f3fe` as positive control, verify no LIVE mutation, persist/read back, and return recurring-open. Do not retry, wait, poll, mutate scheduler, or start a second leaf.
