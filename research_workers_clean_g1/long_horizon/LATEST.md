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

Frozen controls: INSTRUCTION_CONTROL_MANIFEST control33/blob `835fc67ea8942346ab04fdc6b04251a5af29bd35`; RUN_LIFECYCLE control1/blob `8fe5d79365dcd943984d69f4767b2ed0c03fc3ac`; DESIRED_STATE control26/blob `481660fb6008a57cea162da38439cf115c8d7ebe`; long_horizon control17/config8/blob `d790db45343bec399d00c6e9410432963726d72c`.

Predecessor LATEST blob consumed: `07546634d4257dd3c0ecb7a0b023f2396e77b27f`.
Preflight: `research_workers_clean_g1/long_horizon/preflight/20260901T1123JST_latest_pointer_binding_preflight.json`, blob `014457d61fa0475aadc30493321817f1217b8855`.
Authoritative current checkpoint: `research_workers_clean_g1/long_horizon/checkpoints/20260901T1124JST_latest_pointer_binding_result.json`, blob `f21feb808775e6f69f4351688df9ba221825091d`.

Bounded leaf result: with canonical branch `clean-long-horizon-phase1-active`, authority-file blob `dd9eb6a591f643e8653c61e5469a0805be54f3fe`, `plan_generation=3`, LIVE blob `f79a86302e6c4fcb095aec7b22cc6491bb3da20a`, and predecessor LATEST identity as the only varied field, envelope binding to stale LATEST blob `82d03e00d623bee89d54c4867b2e02edd75a329e` was rejected as `REJECT_STALE_LATEST_POINTER`; envelope binding to current predecessor LATEST blob `07546634d4257dd3c0ecb7a0b023f2396e77b27f` was admitted. LIVE was exact-read afterward and remained blob `f79a86302e6c4fcb095aec7b22cc6491bb3da20a`. No LIVE mutation, wait/poll/retry, optional second leaf, scheduler mutation, richer-mode/Work, protected-primary/manual execution, finite quota, or incremental monetary cost was introduced.

## Exact nonempty continuation
Next effect_chain_id: `clean-rate-limit-envelope-live-blob-binding-v1`.

Freshly bootstrap/freeze required controls; reconstruct canonical branch authority, this then-current LATEST pointer and unchanged generation-3 LIVE state. In exactly one bounded in-memory envelope control, hold canonical branch, authority-file blob, `plan_generation=3` and current LATEST blob fixed; supply an otherwise-current envelope carrying a stale prior LIVE blob and require `REJECT_STALE_LIVE_BLOB`, while the current LIVE blob is admitted. Verify LIVE unchanged; persist/read back and return recurring-open. Do not wait, poll, retry, mutate scheduler, or start a second leaf.
