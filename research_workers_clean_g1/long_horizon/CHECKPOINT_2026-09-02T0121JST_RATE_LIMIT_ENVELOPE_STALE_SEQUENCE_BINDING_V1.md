# Long Horizon Phase-1 checkpoint — stale sequence binding v1

- phase_id: `phase_1_chat_parity`
- root_problem_id: `o-chat-parity-root-v4-zero-work-dependency-zero-quota`
- task_id: `phase1-clean-long-horizon-overrun-recovery`
- effect_chain_id: `clean-rate-limit-envelope-stale-sequence-binding-v1`
- enabled_desired: `true`
- global_completion: `false`
- phase1_completion_claimed: `false`
- scheduler_mutation_by_worker: `false`
- bootstrap_valid: `true`
- transport_mode: `exact_blob_two_pass`

## Frozen controls

- manifest: control_revision `40`, blob `4b96273483ec18493894d2e0eb5cc71a120b39ea`
- lifecycle: control_revision `1`, blob `8fe5d79365dcd943984d69f4767b2ed0c03fc3ac`
- root: control_revision `26`, blob `481660fb6008a57cea162da38439cf115c8d7ebe`
- role: control_revision `17`, config_revision `8`, blob `d790db45343bec399d00c6e9410432963726d72c`

## Preflight / predecessor

- predecessor LATEST blob: `e69025d5ffb248f7e49a700266610cb385a666af`
- preflight path: `research_workers_clean_g1/long_horizon/PREFLIGHT_2026-09-02T0121JST_RATE_LIMIT_ENVELOPE_STALE_SEQUENCE_BINDING_V1.md`
- preflight exact-read blob: `4144048122dd48e2c01e7224d3743a1fe39351dd`
- LIVE path: `research_workers_clean_g1/long_horizon/phase1/LIVE_RATE_LIMIT_STATE.json`
- required/observed LIVE blob: `f79a86302e6c4fcb095aec7b22cc6491bb3da20a`

## Single bounded negative control

The durable current envelope read back unchanged as `state_sequence=6`, `plan_generation=3`, `current_plan=defer_no_retry_plan`. The injected continuation coordinate was the stale `state_sequence=5` carried by predecessor LIVE blob `5217ac80d20baad6afd158bd5e39c4b39e9200ff`, while the authority branch, current predecessor LATEST identity, current plan generation, and current LIVE blob were held fixed.

Result: `REJECT_STALE_SEQUENCE_BINDING`.

Observed/required invariants:
- stale sequence accepted: `false`
- current LIVE sequence/generation: `6 / 3`
- injected stale sequence: `5`
- LIVE mutation issued: `false`
- retry/backoff resampled: `false`
- prior plan reactivated: `false`
- scheduler mutation: `false`
- same-run wait/poll/backoff/retry: `false`
- optional second leaf started: `false`
- provider/external work invoked: `false`

This closes only the tested stale-state-sequence coordinate for the current repository-carried continuation envelope. It does not prove global long-horizon safety or Phase-1 completion.

## Phase-1 acceptance fields

- residual richer-mode/Work/protected-primary/manual-user execution dependency: `false`
- finite monthly/trial/paid quota dependency: `false`
- incremental monetary cost: `0`
- conflict check: role-local branch/path only; no O, downstream, other-worker, shared-ledger, protected-primary, or scheduler mutation consumed.
- termination: `bounded_slice_complete_recurring_open`
- hard_runtime_boundary_reached: `false`

## Exact continuation

Next effect_chain_id: `clean-rate-limit-envelope-stale-blob-binding-v1`.

Freshly bootstrap/freeze the four required controls, reconstruct the then-current canonical role-branch LATEST, and persist/exact-read a new preflight before semantic reads. Re-read LIVE only if the continuation still names its exact current sequence, generation and blob. Hold authority branch, current LATEST identity, `state_sequence=6`, and `plan_generation=3` fixed while substituting predecessor LIVE blob `5217ac80d20baad6afd158bd5e39c4b39e9200ff` as the only negative coordinate. Require `REJECT_STALE_BLOB_BINDING` with zero LIVE mutation, zero retry/backoff resampling, zero plan reactivation, zero scheduler mutation, and no second leaf. Persist/read back the exact result and another nonempty continuation; Phase 1 remains open.
