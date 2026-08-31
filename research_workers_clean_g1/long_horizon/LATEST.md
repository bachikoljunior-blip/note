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

Frozen controls: manifest control32/blob `89d3263cb84208da613cf90329291d8c391a43da`; RUN_LIFECYCLE control1/blob `8fe5d79365dcd943984d69f4767b2ed0c03fc3ac`; DESIRED_STATE control26/blob `481660fb6008a57cea162da38439cf115c8d7ebe`; long_horizon control17/config8/blob `d790db45343bec399d00c6e9410432963726d72c`.

Predecessor LATEST blob consumed: `c982c7dbba2dafbd9ab294a93d2d25817848e79c`.
Preflight: `research_workers_clean_g1/long_horizon/preflight/20260901T0820JST_authority_blob_binding_preflight.json`, blob `2fd7aaa6df8ba8ff508be13097471deb50bfa574`.
Authoritative current checkpoint: `research_workers_clean_g1/long_horizon/checkpoints/20260901T0821JST_authority_blob_binding_compact.json`, blob `37ab6925fe5aef9639b3d66eb9375edd03e681aa`.

Bounded leaf result: with `plan_generation=3` and current LIVE blob `f79a86302e6c4fcb095aec7b22cc6491bb3da20a` fixed, a synthetic non-current `authority_file_blob=0000000000000000000000000000000000000000` was rejected as `REJECT_STALE_AUTHORITY_BLOB`; the exact current authority blob `dd9eb6a591f643e8653c61e5469a0805be54f3fe` was admitted. LIVE was exact-read after the control and remained at the same blob. No LIVE mutation, wait/poll/retry, second leaf, scheduler mutation, richer-mode/Work, protected-primary/manual execution, finite quota, or incremental monetary cost was introduced.

## Exact nonempty continuation
Next effect_chain_id: `clean-rate-limit-envelope-canonical-branch-binding-v1`.

Freshly bootstrap/freeze required controls; reconstruct this pointer plus canonical `research_workers_clean_g1/long_horizon/phase1/BRANCH_AUTHORITY.json` and `research_workers_clean_g1/long_horizon/phase1/LIVE_RATE_LIMIT_STATE.json`. Hold `plan_generation=3`, current LIVE blob, and current authority-file blob fixed. In exactly one bounded in-memory control, present a continuation envelope with a non-canonical `authority_branch` and require `REJECT_AUTHORITY_BRANCH_MISMATCH`; compare exact `clean-long-horizon-phase1-active` as positive `ADMIT`; verify LIVE unchanged; persist/read back and return recurring-open. Do not retry, wait, poll, mutate scheduler, or start a second leaf.
