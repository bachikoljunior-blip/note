# Long Horizon Phase-1 checkpoint — rate-limit envelope stale-generation replay v1

- phase_id: `phase_1_chat_parity`
- root_problem_id: `o-chat-parity-root-v4-zero-work-dependency-zero-quota`
- task_id: `phase1-clean-long-horizon-overrun-recovery`
- effect_chain_id: `clean-rate-limit-envelope-stale-generation-replay-v1`
- enabled_desired: `true`
- global_completion: `false`
- phase1_completion_claimed: `false`
- scheduler_mutation_by_worker: `false`
- termination: `bounded_slice_complete_recurring_open`
- bootstrap_valid: `true`
- transport_mode: `exact_blob_two_pass`

## Frozen controls

- INSTRUCTION_CONTROL_MANIFEST: control_revision `46`, blob `6a2108e5dd79c36f85a3c57aca8e84713d1ea1d4`
- RUN_LIFECYCLE: control_revision `1`, blob `8fe5d79365dcd943984d69f4767b2ed0c03fc3ac`
- DESIRED_STATE: control_revision `26`, blob `481660fb6008a57cea162da38439cf115c8d7ebe`
- long_horizon role config: control_revision `17`, config_revision `8`, blob `d790db45343bec399d00c6e9410432963726d72c`
- predecessor LATEST blob: `ff830bb5b08d4b61e777607539f6383006f9bc0b`
- preflight path: `research_workers_clean_g1/long_horizon/PREFLIGHT_2026-09-02T0721JST_RATE_LIMIT_ENVELOPE_STALE_GENERATION_REPLAY_V1.md`
- preflight blob: `0327a9c0ac2587970eacd2852f0be39fcbf671b2`

## Single bounded leaf

Current durable state was read exactly once from `research_workers_clean_g1/long_horizon/phase1/LIVE_RATE_LIMIT_STATE.json` on canonical branch `clean-long-horizon-phase1-active`.

- current LIVE blob: `f79a86302e6c4fcb095aec7b22cc6491bb3da20a`
- current state_sequence: `6`
- current plan_generation: `3`
- current plan: `defer_no_retry_plan`
- current retry_attempt/max_attempts: `3/3`
- current switch_count: `2`
- synthetic stale continuation plan_generation: `2`
- synthetic stale predecessor blob: `5217ac80d20baad6afd158bd5e39c4b39e9200ff`
- comparison: `2 < 3`
- result: `REJECT_STALE_GENERATION`

The stale continuation is not eligible to reactivate `compact_plan` or any predecessor plan. The LIVE state was not updated. The persisted backoff (`240s`) was not resampled or reapplied, no fourth retry was created, and no external work attempt was consumed.

## Required invariants

- LIVE mutation issued: `false`
- current plan reactivated from stale continuation: `false`
- retry/backoff resampled: `false`
- same-run wait/poll/backoff/retry: `false`
- optional second leaf started: `false`
- stale continuation accepted: `false`
- monotonic-generation rejection property satisfied: `true`
- residual richer-mode/Work/protected-primary/manual-user execution dependency: `false`
- finite monthly/trial/paid quota dependency: `false`
- incremental monetary cost: `0`

## Tested scope

This proves only the deterministic role-local decision property for the observed durable state: a continuation carrying `plan_generation=2` is rejected when the current durable state is `plan_generation=3`, without mutating the LIVE state or retry envelope. It does not prove resistance to forged current-generation continuations, stale-blob/current-generation mismatches, external force-push, or global Phase-1 completion.

## Exact continuation

Next effect_chain_id: `clean-rate-limit-envelope-current-generation-stale-blob-replay-v1`.

Freshly bootstrap/freeze the four required controls and reconstruct the then-current canonical role-branch LATEST successor. Persist and exact-read the required preflight. Fetch only the current `research_workers_clean_g1/long_horizon/phase1/LIVE_RATE_LIMIT_STATE.json`. Evaluate one synthetic continuation that claims the current `plan_generation` but carries stale CAS authority blob `5217ac80d20baad6afd158bd5e39c4b39e9200ff` instead of the current LIVE blob. Require `REJECT_STALE_BLOB_AUTHORITY`, no LIVE mutation, no plan reactivation, no retry/backoff resampling, no wait/retry, and no second leaf. If LIVE legitimately advances, bind the claimed generation to that exact successor while keeping the stale blob fixed as the negative control. Phase 1 remains open.
