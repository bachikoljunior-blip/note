# CLEAN long_horizon checkpoint — current-generation stale-blob replay

- phase_id: `phase_1_chat_parity`
- root_problem_id: `o-chat-parity-root-v4-zero-work-dependency-zero-quota`
- task_id: `phase1-clean-long-horizon-overrun-recovery`
- effect_chain_id: `clean-rate-limit-envelope-current-generation-stale-blob-replay-v1`
- enabled_desired: `true`
- global_completion: `false`
- phase1_completion_claimed: `false`
- scheduler_mutation_by_worker: `false`
- bootstrap_valid: `true`
- transport_mode: `exact_blob_two_pass`
- termination: `bounded_slice_complete_recurring_open`

## Frozen controls

- INSTRUCTION_CONTROL_MANIFEST: control_revision `48`, blob `410269a4b6e7d06d73721807149313360c1273e8`
- RUN_LIFECYCLE: control_revision `1`, blob `8fe5d79365dcd943984d69f4767b2ed0c03fc3ac`
- DESIRED_STATE: control_revision `26`, manifest-bound blob `481660fb6008a57cea162da38439cf115c8d7ebe`
- long_horizon role config: control_revision `17`, config_revision `8`, blob `d790db45343bec399d00c6e9410432963726d72c`

## Preflight / predecessor

- predecessor LATEST blob: `3d0f379f6b4bee0e883eb64b6aace7266d3a5c22`
- preflight path: `research_workers_clean_g1/long_horizon/PREFLIGHT_2026-09-02T1023JST_RATE_LIMIT_ENVELOPE_CURRENT_GENERATION_STALE_BLOB_REPLAY_V1.md`
- preflight exact-read blob: `f62e84e630841e16bd6a95add6c1b1399cf9f1bf`

## Single bounded probe

Current LIVE state was fetched exactly once after preflight readback:
- path: `research_workers_clean_g1/long_horizon/phase1/LIVE_RATE_LIMIT_STATE.json`
- exact current transport/content blob: `f79a86302e6c4fcb095aec7b22cc6491bb3da20a`
- current `state_sequence`: `6`
- current `plan_generation`: `3`
- current plan: `defer_no_retry_plan`
- current decision: `SWITCH_PLAN`

Synthetic continuation claim:
- claimed `plan_generation`: `3` (matches current generation)
- supplied CAS authority blob: `5217ac80d20baad6afd158bd5e39c4b39e9200ff`
- exact current LIVE blob required for authority: `f79a86302e6c4fcb095aec7b22cc6491bb3da20a`
- blob equality: `false`

Decision: `REJECT_STALE_BLOB_AUTHORITY`.

The rejection is intentionally ordered after generation equality but before any state mutation, plan activation, retry scheduling or backoff choice. This isolates stale CAS authority from the previously tested stale-generation condition. The embedded `authority_file_blob` field inside the JSON was not treated as a transport CAS token; the fetched GitHub content blob is the current repository authority used by this probe.

## Effects / controls

- LIVE mutation issued: `false`
- plan reactivated: `false`
- retry/backoff resampled: `false`
- retry attempt consumed: `false`
- same-run wait/poll/backoff/retry: `false`
- optional second leaf started: `false`
- richer-mode/Work/protected-primary/manual-user execution dependency: `false`
- finite monthly/trial/paid quota dependency: `false`
- incremental monetary cost: `0`

## Tested scope

This is a synthetic repository-state authority-binding control on the canonical role-local branch. It shows that a continuation can be rejected when its semantic generation is current but its CAS authority blob is stale, without mutating the LIVE rate-limit state. It does not by itself establish full scheduler persistence, full task success, or global Phase-1 completion.

## Exact continuation

Next effect_chain_id: `clean-rate-limit-envelope-current-generation-current-blob-positive-control-v1`.

Freshly bootstrap/freeze the four required controls and reconstruct the then-current canonical role LATEST. Persist/exact-read preflight. Fetch only the current LIVE rate-limit state. Evaluate one synthetic continuation whose claimed `plan_generation` equals the exact current generation and whose supplied CAS authority blob equals the exact current fetched LIVE blob. Require `ACCEPT_AUTHORITY_BINDING` as an admissibility-only result with no LIVE mutation, no plan reactivation, no retry/backoff resampling, no wait/retry, and no second leaf. If LIVE legitimately advances, bind both generation and blob to that exact successor rather than reusing the values recorded here. Phase 1 remains open.
