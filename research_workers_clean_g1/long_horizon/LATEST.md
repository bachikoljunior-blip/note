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

Frozen controls: manifest control27; RUN_LIFECYCLE control1/blob `8fe5d79365dcd943984d69f4767b2ed0c03fc3ac`; DESIRED_STATE control26/blob `481660fb6008a57cea162da38439cf115c8d7ebe`; long_horizon control17/config8/blob `d790db45343bec399d00c6e9410432963726d72c`.

Predecessor LATEST blob consumed: `a85129d7b8d6fbc687fed1ad8cbf30df1169c8d1`.
Preflight: `research_workers_clean_g1/long_horizon/preflight/20260901T0323JST_stale_generation_replay_preflight.json`, blob `9c209a1bd3c68227b74d06bde8abe405fdeb37f6`.
Authoritative current checkpoint: `research_workers_clean_g1/long_horizon/checkpoints/20260901T0324JST_stale_generation_replay.md`, blob `7a777bd96797dcff9b7259137ba9dde2d81a04a1`.

Bounded leaf result: canonical LIVE state remained exact-read unchanged at blob `f79a86302e6c4fcb095aec7b22cc6491bb3da20a`, `state_sequence=6`, `plan_generation=3`. A continuation presenting stale generation `2` plus prior-state blob `5217ac80d20baad6afd158bd5e39c4b39e9200ff` was rejected as `REJECT_STALE_GENERATION_AND_STATE_BLOB`; a generation-3 continuation bound to the current LIVE blob was admitted. No LIVE mutation, retry attempt 4, backoff resampling, wait/poll, second leaf, scheduler mutation, richer-mode/Work, protected-primary/manual execution, finite quota, or incremental monetary cost was introduced.

## Exact nonempty continuation
Next effect_chain_id: `clean-rate-limit-stale-blob-replay-v1`.

Freshly bootstrap/freeze required controls; reconstruct this pointer; exact-read canonical `research_workers_clean_g1/long_horizon/phase1/LIVE_RATE_LIMIT_STATE.json`. In exactly one bounded in-memory control, present `plan_generation=3` with stale prior-state blob `5217ac80d20baad6afd158bd5e39c4b39e9200ff`; require rejection solely by the state-blob/CAS authority fence, compare generation `3` + current LIVE blob as positive control, verify no LIVE mutation, and persist/read back the role-local chain. Preserve `enabled_desired=true`, `global_completion=false`, `phase1_completion_claimed=false`; never mutate scheduler or start a second leaf.
