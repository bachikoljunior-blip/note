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

- INSTRUCTION_CONTROL_MANIFEST: control_revision `44`, blob `3202a080710898ed32620b0eaec10068370b467e`
- RUN_LIFECYCLE: control_revision `1`, blob `8fe5d79365dcd943984d69f4767b2ed0c03fc3ac`
- DESIRED_STATE: control_revision `26`, blob `481660fb6008a57cea162da38439cf115c8d7ebe`
- long_horizon role config: control_revision `17`, config_revision `8`, blob `d790db45343bec399d00c6e9410432963726d72c`

## Bounded slice

- effect_chain_id: `clean-rate-limit-envelope-current-valid-binding-v1`
- predecessor LATEST blob: `933a7c56e968f8f3d90ca6d8db8e8e764da79216`
- preflight: `research_workers_clean_g1/long_horizon/PREFLIGHT_2026-09-02T0523JST_RATE_LIMIT_ENVELOPE_CURRENT_VALID_BINDING_V1.md`
- preflight exact-read blob: `2bdceefacdbbba3a0ca1a7bbfd2b62a2fdceec41`
- checkpoint: `research_workers_clean_g1/long_horizon/CHECKPOINT_2026-09-02T0523JST_RATE_LIMIT_ENVELOPE_CURRENT_VALID_BINDING_V1.md`
- checkpoint exact-read blob: `551fd3e8c52a466bca66c596d59bb702a7b7d003`
- receipt: `automation_control/receipts/long_horizon/receipt_2026-09-02T0523+0900_rate_limit_envelope_current_valid_binding_v1.json`
- receipt exact-read blob: `f23e4414759a2b40be49f7986b16328a00e45a68`
- LIVE path: `research_workers_clean_g1/long_horizon/phase1/LIVE_RATE_LIMIT_STATE.json`
- LIVE required/observed blob: `f79a86302e6c4fcb095aec7b22cc6491bb3da20a`
- current LIVE sequence/generation: `6/3`
- result: `ACCEPT_CURRENT_BINDING`
- all current binding coordinates matched: `true`
- LIVE mutation issued: `false`
- retry/backoff resampled: `false`
- plan generation mutated: `false`
- same-run wait/poll/backoff/retry: `false`
- optional second leaf started: `false`
- residual richer-mode/Work/protected/user execution dependency: `false`
- finite monthly/trial/paid quota dependency: `false`
- incremental monetary cost: `0`
- termination: `bounded_slice_complete_recurring_open`

## Exact continuation

Next effect_chain_id: `clean-rate-limit-envelope-authority-file-binding-v1`.

Freshly bootstrap/freeze the four required controls, reconstruct this canonical role branch from the then-current LATEST CAS successor, and persist/exact-read the required preflight before the leaf. Then fetch exactly `research_workers_clean_g1/long_horizon/phase1/LIVE_RATE_LIMIT_STATE.json` and `research_workers_clean_g1/long_horizon/phase1/BRANCH_AUTHORITY.json` from branch `clean-long-horizon-phase1-active`. Test only whether LIVE's embedded `authority_file_blob` equals the exact current `BRANCH_AUTHORITY.json` blob and whether that authority record names the same canonical branch and authority generation expected by LIVE. Require `ACCEPT_CURRENT_AUTHORITY_BINDING` without mutating LIVE. If any binding coordinate mismatches, persist `REJECT_AUTHORITY_BINDING_MISMATCH` and a later rebind child instead of repairing in-run. Do not start a second leaf. Phase 1 remains open.
