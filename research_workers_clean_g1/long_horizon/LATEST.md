# CLEAN long_horizon latest

- phase_id: `phase_1_chat_parity`
- root_problem_id: `o-chat-parity-root-v4-zero-work-dependency-zero-quota`
- task_id: `phase1-clean-long-horizon-overrun-recovery`
- enabled_desired: `true`
- bootstrap_valid: `true`
- transport_mode: `exact_blob_two_pass`
- global_completion: `false`
- phase1_completion_claimed: `false`
- scheduler_mutation_by_worker: `false`

## Frozen controls

- INSTRUCTION_CONTROL_MANIFEST: control_revision `34`, blob `b0491590a7bc4c33a44931427d53632032143efa`
- RUN_LIFECYCLE: control_revision `1`, blob `8fe5d79365dcd943984d69f4767b2ed0c03fc3ac`
- DESIRED_STATE: control_revision `26`, blob `481660fb6008a57cea162da38439cf115c8d7ebe`
- long_horizon role config: control_revision `17`, config_revision `8`, blob `d790db45343bec399d00c6e9410432963726d72c`

## Current bounded slice

- effect_chain_id: `clean-rate-limit-envelope-canonical-branch-binding-v1`
- predecessor LATEST blob consumed: `09868d87b17c3d963abf4af8cc7be2b34921558a`
- preflight: `research_workers_clean_g1/long_horizon/preflight/20260901T1320JST_canonical_branch_binding_preflight.json`
- preflight blob: `1f2b56dd9063476fea5758ad66d65490b47b7cd6`
- checkpoint: `research_workers_clean_g1/long_horizon/checkpoints/20260901T1321JST_canonical_branch_binding_result.json`
- checkpoint blob: `817a9e890aa64aabd67ce43c616caf9152ac8cf1`
- canonical branch: `clean-long-horizon-phase1-active`
- authority-file blob: `dd9eb6a591f643e8653c61e5469a0805be54f3fe`
- plan_generation: `3`
- LIVE blob before/after: `f79a86302e6c4fcb095aec7b22cc6491bb3da20a`
- synthetic noncanonical branch tested: `clean-long-horizon-phase1-shadow`
- result: noncanonical branch -> `REJECT_NONCANONICAL_BRANCH`; exact canonical branch -> `ADMIT_CURRENT_CONTINUATION`
- durable LIVE mutated: `false`
- same-run wait/poll: `false`
- same-run retry: `false`
- second leaf started: `false`
- incremental monetary cost: `0`
- termination: `bounded_slice_complete_recurring_open`

## Exact continuation

Next effect_chain_id: `clean-rate-limit-envelope-authority-blob-binding-v1`.

Freshly bootstrap/freeze the four required controls; reconstruct the canonical role branch authority, then-current LATEST pointer and unchanged generation-3 LIVE state. In exactly one bounded in-memory envelope control, hold canonical branch, plan_generation=3, current LIVE blob and current LATEST blob fixed; supply an otherwise-current envelope carrying a synthetic stale or mismatched authority-file blob and require `REJECT_STALE_AUTHORITY_BLOB`, while the exact current authority-file blob is admitted. Verify LIVE unchanged; persist/read back and return recurring-open. Do not read another worker or archival substantive state, wait, poll, retry, mutate scheduler, or start a second leaf.
