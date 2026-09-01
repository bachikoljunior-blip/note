# Long Horizon Phase-1 preflight — rate-limit envelope authority-file binding v1

- phase_id: `phase_1_chat_parity`
- root_problem_id: `o-chat-parity-root-v4-zero-work-dependency-zero-quota`
- task_id: `phase1-clean-long-horizon-overrun-recovery`
- enabled_desired: `true`
- global_completion: `false`
- phase1_completion_claimed: `false`
- scheduler_mutation_by_worker: `false`
- bootstrap_valid: `true`
- transport_mode: `sha_only_main_ref_plus_exact_blob_crosscheck`
- frozen main SHA: `681c5a5558239c24993d9e44b56ee02adc8ede40`

## Frozen controls

- INSTRUCTION_CONTROL_MANIFEST: control_revision `45`, blob `06557aeef00aeb74dc2148cc48873ca6227170fb`
- RUN_LIFECYCLE: control_revision `1`, blob `8fe5d79365dcd943984d69f4767b2ed0c03fc3ac`
- DESIRED_STATE: control_revision `26`, manifest-bound blob `481660fb6008a57cea162da38439cf115c8d7ebe`
- long_horizon role config: control_revision `17`, config_revision `8`, blob `d790db45343bec399d00c6e9410432963726d72c`

## Selected bounded effect chain

- effect_chain_id: `clean-rate-limit-envelope-authority-file-binding-v1`
- predecessor canonical branch: `clean-long-horizon-phase1-active`
- predecessor LATEST blob: `735c4140fb734edb10f34662f7dff1c334a54ab5`
- exact predecessor continuation: fetch only `research_workers_clean_g1/long_horizon/phase1/LIVE_RATE_LIMIT_STATE.json` and `research_workers_clean_g1/long_horizon/phase1/BRANCH_AUTHORITY.json` from the canonical branch; test whether LIVE's embedded `authority_file_blob` equals the exact current authority-file blob and whether the authority record names the same canonical branch and authority generation expected by LIVE.
- planned atomic boundary: one read-only authority-binding comparison; do not mutate LIVE or BRANCH_AUTHORITY.
- forecast: bounded two-file read plus one comparison, followed by checkpoint/receipt/LATEST persistence.
- switch threshold: any missing/unreadable file, exact blob/binding mismatch, or authority-coordinate mismatch => persist `REJECT_AUTHORITY_BINDING_MISMATCH` (or exact read blocker) with a later rebind child; no in-run repair, retry, wait, polling, backoff, or second leaf.
- residual richer-mode/Work/protected/user execution dependency: `false`
- finite monthly/trial/paid quota dependency: `false`
- incremental monetary cost: `0`

This preflight is checkpoint-first and must be exact-read before the leaf.
