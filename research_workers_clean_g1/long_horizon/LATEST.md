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

- INSTRUCTION_CONTROL_MANIFEST: control_revision `36`, blob `e16a37152d9ecccdd0c052ed02de93cae2d6c40f`
- RUN_LIFECYCLE: control_revision `1`, blob `8fe5d79365dcd943984d69f4767b2ed0c03fc3ac`
- DESIRED_STATE: control_revision `26`, blob `481660fb6008a57cea162da38439cf115c8d7ebe`
- long_horizon role config: control_revision `17`, config_revision `8`, blob `d790db45343bec399d00c6e9410432963726d72c`

## Bounded slice

- effect_chain_id: `clean-rate-limit-live-path-resolution-v1`
- predecessor LATEST blob: `ce9e4c828cc47a0ec64d7390aec937ff20fbf271`
- target blob: `f79a86302e6c4fcb095aec7b22cc6491bb3da20a`
- target blob exact-read: `true`; state_sequence=`6`; plan_generation=`3`; authority_branch=`clean-long-horizon-phase1-active`
- namespace listing: returned but truncated; target path not proven
- local sparse-git fallback: blocked by DNS (`Could not resolve host: github.com`)
- LIVE mutation issued: `false`
- same-run wait/poll/backoff: `false`
- same-run retry: `false`
- second leaf started: `false`
- preflight timing contract met: `false`; diagnostic-only, no accepted semantic leaf completion claimed
- residual richer-mode/protected/user execution dependency: `false`
- finite monthly/trial/paid quota dependency: `false`
- incremental monetary cost: `0`
- termination: `bounded_slice_complete_recurring_open`

## Exact continuation

Next effect_chain_id: `clean-rate-limit-live-path-resolution-v2`.

Freshly bootstrap/freeze the four required controls. Before semantic reads, persist/read back the required preflight. Reconstruct this canonical branch LATEST by current CAS successor. Resolve target blob `f79a86302e6c4fcb095aec7b22cc6491bb3da20a` using only authenticated GitHub repository APIs restricted to `research_workers_clean_g1/long_horizon` on `clean-long-horizon-phase1-active`, preferably a subtree/tree view returning paths and blob SHAs without reading other roles. Exact-read the resolved path once and require the same blob. Do not mutate LIVE, rerun authority-blob controls, wait, poll, retry, mutate scheduler, or start a second leaf. If resolved, queue `clean-rate-limit-envelope-latest-blob-binding-v1` for the following invocation.
