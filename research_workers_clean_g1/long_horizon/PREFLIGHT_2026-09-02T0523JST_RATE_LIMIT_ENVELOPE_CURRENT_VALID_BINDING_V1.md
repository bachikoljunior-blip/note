# Long Horizon Phase-1 preflight — current valid binding positive control

- phase_id: `phase_1_chat_parity`
- root_problem_id: `o-chat-parity-root-v4-zero-work-dependency-zero-quota`
- task_id: `phase1-clean-long-horizon-overrun-recovery`
- role: `long_horizon`
- enabled_desired: `true`
- global_completion: `false`
- phase1_completion_claimed: `false`
- effect_chain_id: `clean-rate-limit-envelope-current-valid-binding-v1`
- bootstrap_valid: `true`
- transport_mode: `exact_blob_two_pass`

## Frozen authority tuple

- `automation_control/INSTRUCTION_CONTROL_MANIFEST.json`: control_revision `44`, blob `3202a080710898ed32620b0eaec10068370b467e`
- `automation_control/RUN_LIFECYCLE.json`: control_revision `1`, blob `8fe5d79365dcd943984d69f4767b2ed0c03fc3ac`
- `automation_control/DESIRED_STATE.json`: control_revision `26`, blob `481660fb6008a57cea162da38439cf115c8d7ebe`
- `automation_control/roles/long_horizon.json`: control_revision `17`, config_revision `8`, blob `d790db45343bec399d00c6e9410432963726d72c`

## Reconstructed predecessor/frontier

- canonical role branch: `clean-long-horizon-phase1-active`
- predecessor LATEST blob: `933a7c56e968f8f3d90ca6d8db8e8e764da79216`
- continuation requires current `state_sequence=6`, `plan_generation=3`, LIVE blob `f79a86302e6c4fcb095aec7b22cc6491bb3da20a`
- observed LIVE blob: `f79a86302e6c4fcb095aec7b22cc6491bb3da20a`
- observed state_sequence: `6`
- observed plan_generation: `3`

## Planned atomic boundary

Perform exactly one positive-control continuation-binding check. Accept only when all three current coordinates match exactly: LIVE blob, `state_sequence`, and `plan_generation`. Required outcome is `ACCEPT_CURRENT_BINDING`. This leaf must not mutate LIVE, retry/backoff state, plan generation, scheduler state, or start a second leaf.

## Forecast / switch threshold

The bounded leaf requires only the already-fetched LIVE read plus one durable checkpoint/receipt/LATEST chain. No same-run wait, poll, backoff, transient retry, external compute, hosted quota, richer-mode execution, protected-primary action, or manual user execution is permitted. If any current coordinate differs before checkpoint persistence, stop the leaf as an authority mismatch and persist a rebind continuation instead of switching plans in-run.

Exact continuation on successful leaf: next invocation reconstruct the then-current canonical LATEST and test `clean-rate-limit-envelope-authority-file-binding-v1`, binding the LIVE state's embedded `authority_file_blob` to the current canonical branch authority record without mutating LIVE. Phase 1 remains open.
