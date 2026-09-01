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

Predecessor LATEST blob consumed: `82d03e00d623bee89d54c4867b2e02edd75a329e`.
Preflight: `research_workers_clean_g1/long_horizon/preflight/20260901T092022JST_authority_branch_binding_preflight.json`, blob `df4897e49620eb0641286fc22d1981164ded4c15`.
Authoritative current checkpoint: `research_workers_clean_g1/long_horizon/checkpoints/20260901T0921JST_branch_consistency_result.json`, blob `ed923a77b1f84318a8a6bfdd43b50bb56f1b43f3`.

Bounded leaf result: with `plan_generation=3`, LIVE blob `f79a86302e6c4fcb095aec7b22cc6491bb3da20a`, and authority-file blob `dd9eb6a591f643e8653c61e5469a0805be54f3fe` fixed, a non-canonical role branch was rejected as `REJECT_AUTHORITY_BRANCH_MISMATCH`; exact `clean-long-horizon-phase1-active` was admitted. LIVE was exact-read after the control and remained unchanged. No LIVE mutation, wait/poll/retry, optional second leaf, scheduler mutation, richer-mode/Work, protected-primary/manual execution, finite quota, or incremental monetary cost was introduced.

## Exact nonempty continuation
Next effect_chain_id: `clean-rate-limit-envelope-latest-pointer-binding-v1`.

Freshly bootstrap/freeze required controls; reconstruct this pointer plus canonical `research_workers_clean_g1/long_horizon/phase1/BRANCH_AUTHORITY.json` and unchanged `research_workers_clean_g1/long_horizon/phase1/LIVE_RATE_LIMIT_STATE.json`. Hold canonical branch, `plan_generation=3`, current LIVE blob and authority-file blob fixed. In exactly one bounded in-memory control, require a continuation envelope carrying predecessor LATEST blob `82d03e00d623bee89d54c4867b2e02edd75a329e` to be rejected as `REJECT_STALE_LATEST_POINTER`, while the then-current LATEST blob is admitted. Verify LIVE unchanged; persist/read back and return recurring-open. Do not retry, wait, poll, mutate scheduler, or start a second leaf.
