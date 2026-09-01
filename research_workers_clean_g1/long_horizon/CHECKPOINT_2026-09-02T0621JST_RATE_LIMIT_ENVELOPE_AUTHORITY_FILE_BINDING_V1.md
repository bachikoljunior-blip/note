# Long Horizon Phase-1 checkpoint — rate-limit envelope authority-file binding v1

## Authority and scope

- phase_id: `phase_1_chat_parity`
- root_problem_id: `o-chat-parity-root-v4-zero-work-dependency-zero-quota`
- task_id: `phase1-clean-long-horizon-overrun-recovery`
- effect_chain_id: `clean-rate-limit-envelope-authority-file-binding-v1`
- enabled_desired: `true`
- global_completion: `false`
- phase1_completion_claimed: `false`
- scheduler_mutation_by_worker: `false`
- bootstrap_valid: `true`
- transport_mode: `sha_only_main_ref_plus_exact_blob_crosscheck`
- frozen main SHA: `681c5a5558239c24993d9e44b56ee02adc8ede40`
- INSTRUCTION_CONTROL_MANIFEST: control_revision `45`, blob `06557aeef00aeb74dc2148cc48873ca6227170fb`
- RUN_LIFECYCLE: control_revision `1`, blob `8fe5d79365dcd943984d69f4767b2ed0c03fc3ac`
- DESIRED_STATE: control_revision `26`, manifest-bound blob `481660fb6008a57cea162da38439cf115c8d7ebe`
- long_horizon role config: control_revision `17`, config_revision `8`, blob `d790db45343bec399d00c6e9410432963726d72c`
- predecessor LATEST blob: `735c4140fb734edb10f34662f7dff1c334a54ab5`
- preflight path: `research_workers_clean_g1/long_horizon/PREFLIGHT_2026-09-02T0621JST_RATE_LIMIT_ENVELOPE_AUTHORITY_FILE_BINDING_V1.md`
- preflight exact-read blob: `b4a33b6505f5d29a53522f3603a4a4bbad563559`

## Single bounded leaf

Read exactly the canonical role branch's current rate-limit state and branch-authority record, then tested the current authority-file binding without mutating either file.

Observed state:
- LIVE path: `research_workers_clean_g1/long_horizon/phase1/LIVE_RATE_LIMIT_STATE.json`
- LIVE exact blob: `f79a86302e6c4fcb095aec7b22cc6491bb3da20a`
- LIVE state_sequence / plan_generation: `6 / 3`
- LIVE authority_branch: `clean-long-horizon-phase1-active`
- LIVE authority_file_blob: `dd9eb6a591f643e8653c61e5469a0805be54f3fe`
- LIVE authority_generation coordinate: `1`
- authority path: `research_workers_clean_g1/long_horizon/phase1/BRANCH_AUTHORITY.json`
- authority exact blob: `dd9eb6a591f643e8653c61e5469a0805be54f3fe`
- authority canonical_role_branch: `clean-long-horizon-phase1-active`
- authority_generation: `1`

Binding checks:
- `LIVE.authority_file_blob == exact current BRANCH_AUTHORITY blob`: `true`
- `LIVE.authority_branch == BRANCH_AUTHORITY.canonical_role_branch`: `true`
- `LIVE authority_generation coordinate == BRANCH_AUTHORITY.authority_generation`: `true`
- result: `ACCEPT_CURRENT_AUTHORITY_BINDING`

No LIVE mutation was issued. No retry/backoff was sampled or consumed. No plan generation changed. No same-run wait, poll, backoff, retry, or optional second leaf was performed.

## Acceptance-surface assessment

- residual richer-mode/Work/protected-primary/manual-user execution dependency: `false`
- finite monthly/trial/paid quota dependency: `false`
- incremental monetary cost: `0`
- repository transport role: lightweight state/evidence only, not compute
- tested scope: current canonical-branch authority-file binding only; this does not prove resistance to out-of-band force-push/deletion or all stale-continuation classes.

## Exact continuation

Next effect_chain_id: `clean-rate-limit-envelope-stale-generation-replay-v1`.

Freshly bootstrap/freeze the four required controls and reconstruct the canonical role branch from the then-current LATEST successor. Persist/exact-read the required preflight before the leaf. Fetch only the current `LIVE_RATE_LIMIT_STATE.json`. Evaluate one synthetic stale continuation carrying predecessor `plan_generation=2` and predecessor blob `5217ac80d20baad6afd158bd5e39c4b39e9200ff` against the current state. Require `REJECT_STALE_GENERATION` because current generation is `3`, and require no LIVE mutation, no reactivation of `compact_plan`, no retry/backoff resampling, and no second leaf. If the current LIVE coordinates have legitimately advanced before that invocation, bind the stale replay test to the exact current successor and preserve the same monotonic-generation rejection property. Phase 1 remains open.

## Termination

- termination: `bounded_slice_complete_recurring_open`
- hard_runtime_boundary_reached: `false`
- continuation_nonempty: `true`
- next_invocation_resumes_exact_continuation: `true`
