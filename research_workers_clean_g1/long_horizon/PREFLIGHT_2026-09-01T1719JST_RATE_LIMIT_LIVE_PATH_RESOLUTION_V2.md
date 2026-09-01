# CLEAN long_horizon preflight — rate-limit live path resolution v2

- phase_id: `phase_1_chat_parity`
- root_problem_id: `o-chat-parity-root-v4-zero-work-dependency-zero-quota`
- task_id: `phase1-clean-long-horizon-overrun-recovery`
- enabled_desired: `true`
- global_completion: `false`
- phase1_completion_claimed: `false`
- scheduler_mutation_by_worker: `false`
- bootstrap_valid: `true`
- transport_mode: `exact_blob_two_pass`

## Frozen authority tuple
- INSTRUCTION_CONTROL_MANIFEST: control_revision `37`, blob `c294ff499b893f58da2ca70e269217ac21e71c7b`
- RUN_LIFECYCLE: control_revision `1`, blob `8fe5d79365dcd943984d69f4767b2ed0c03fc3ac`
- DESIRED_STATE: control_revision `26`, blob `481660fb6008a57cea162da38439cf115c8d7ebe`
- long_horizon role config: control_revision `17`, config_revision `8`, blob `d790db45343bec399d00c6e9410432963726d72c`

## Selected bounded effect chain
- effect_chain_id: `clean-rate-limit-live-path-resolution-v2`
- authority_branch: `clean-long-horizon-phase1-active`
- reconstructed predecessor LATEST blob: `edc5bd0bdaebf4d9152cc760b0088301d7a8c006`
- unresolved target blob: `f79a86302e6c4fcb095aec7b22cc6491bb3da20a`
- predecessor frontier: resolve that blob to one path using authenticated GitHub repository APIs restricted to `research_workers_clean_g1/long_horizon` on the authority branch; exact-read the resolved path once and require identical blob; do not mutate LIVE.
- planned atomic boundary: one namespace directory/tree lookup, local response search for the target blob, and at most one exact file read if uniquely resolved.
- forecast: expected to fit one bounded repository-read chain; no waits, polls, retries, or second leaf.
- switch threshold: if the target blob is absent, non-unique, authority-mismatched, or an authenticated repository read fails, stop this chain after durable diagnostic persistence and carry the exact unresolved path/error forward.

Residual richer-mode/protected/user execution dependency: `false`.
Finite monthly/trial/paid quota dependency: `false`.
Incremental monetary cost: `0`.
