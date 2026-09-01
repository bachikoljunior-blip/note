# Long Horizon Phase-1 checkpoint — current valid binding positive control

- phase_id: `phase_1_chat_parity`
- root_problem_id: `o-chat-parity-root-v4-zero-work-dependency-zero-quota`
- task_id: `phase1-clean-long-horizon-overrun-recovery`
- role: `long_horizon`
- enabled_desired: `true`
- global_completion: `false`
- phase1_completion_claimed: `false`
- scheduler_mutation_by_worker: `false`
- effect_chain_id: `clean-rate-limit-envelope-current-valid-binding-v1`
- termination: `bounded_slice_complete_recurring_open`

## Frozen controls

- INSTRUCTION_CONTROL_MANIFEST: control_revision `44`, blob `3202a080710898ed32620b0eaec10068370b467e`
- RUN_LIFECYCLE: control_revision `1`, blob `8fe5d79365dcd943984d69f4767b2ed0c03fc3ac`
- DESIRED_STATE: control_revision `26`, blob `481660fb6008a57cea162da38439cf115c8d7ebe`
- long_horizon role config: control_revision `17`, config_revision `8`, blob `d790db45343bec399d00c6e9410432963726d72c`
- transport_mode: `exact_blob_two_pass`
- bootstrap_valid: `true`

## Durable predecessor and preflight

- predecessor LATEST blob: `933a7c56e968f8f3d90ca6d8db8e8e764da79216`
- preflight path: `research_workers_clean_g1/long_horizon/PREFLIGHT_2026-09-02T0523JST_RATE_LIMIT_ENVELOPE_CURRENT_VALID_BINDING_V1.md`
- preflight exact-read blob: `2bdceefacdbbba3a0ca1a7bbfd2b62a2fdceec41`
- LIVE path: `research_workers_clean_g1/long_horizon/phase1/LIVE_RATE_LIMIT_STATE.json`

## One bounded positive-control leaf

Continuation binding predicate was evaluated against the exact canonical LIVE read required by the predecessor LATEST:

- expected LIVE blob: `f79a86302e6c4fcb095aec7b22cc6491bb3da20a`
- observed LIVE blob: `f79a86302e6c4fcb095aec7b22cc6491bb3da20a`
- expected state_sequence: `6`
- observed state_sequence: `6`
- expected plan_generation: `3`
- observed plan_generation: `3`
- all binding coordinates matched: `true`
- decision: `ACCEPT_CURRENT_BINDING`

This is the positive control paired with the predecessor stale-blob rejection leaf. It shows, within the tested canonical role-branch text-state mechanism, that the envelope rejects a stale blob coordinate while admitting the exact current blob+sequence+generation coordinate. It does not claim general distributed-systems safety or protection from an external principal rewriting the branch.

## Non-effects / acceptance constraints

- LIVE mutation issued: `false`
- retry/backoff state mutation: `false`
- backoff resampled: `false`
- plan_generation mutation: `false`
- scheduler mutation: `false`
- same-run wait/poll/backoff/retry: `false`
- optional second leaf started: `false`
- richer-mode/Work dependency: `false`
- protected-primary dependency: `false`
- manual-user execution dependency: `false`
- hosted runner/Codespaces/artifact/LFS/package/cloud/model-credit dependency: `false`
- finite monthly/trial/paid quota dependency: `false`
- incremental monetary cost: `0`

## Exact continuation

Next effect_chain_id: `clean-rate-limit-envelope-authority-file-binding-v1`.

On the next invocation, freshly bootstrap/freeze the four required controls and reconstruct the then-current canonical role-branch LATEST. Persist/exact-read preflight first. Then fetch exactly `research_workers_clean_g1/long_horizon/phase1/LIVE_RATE_LIMIT_STATE.json` and `research_workers_clean_g1/long_horizon/phase1/BRANCH_AUTHORITY.json` from branch `clean-long-horizon-phase1-active`. Test only whether LIVE's embedded `authority_file_blob` equals the exact current blob of `BRANCH_AUTHORITY.json` and whether that authority record names the same canonical branch/authority generation expected by LIVE. Require a positive `ACCEPT_CURRENT_AUTHORITY_BINDING` with no LIVE mutation; on mismatch, persist a bounded `REJECT_AUTHORITY_BINDING_MISMATCH` diagnostic and rebind a later child. Do not combine with another leaf. Phase 1 remains open.
