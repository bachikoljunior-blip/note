# CLEAN long_horizon checkpoint — stale blob binding v1

- phase_id: `phase_1_chat_parity`
- root_problem_id: `o-chat-parity-root-v4-zero-work-dependency-zero-quota`
- task_id: `phase1-clean-long-horizon-overrun-recovery`
- effect_chain_id: `clean-rate-limit-envelope-stale-blob-binding-v1`
- termination: `bounded_slice_complete_recurring_open`
- enabled_desired: `true`
- global_completion: `false`
- phase1_completion_claimed: `false`
- scheduler_mutation_by_worker: `false`
- bootstrap_valid: `true`
- transport_mode: `exact_blob_two_pass`

## Frozen authority

- INSTRUCTION_CONTROL_MANIFEST: control_revision `42`, fetched response sha `89f1fb9230d1531c4d27e6037b9baf74fc9ca206`
- RUN_LIFECYCLE: control_revision `1`, blob `8fe5d79365dcd943984d69f4767b2ed0c03fc3ac`
- DESIRED_STATE: control_revision `26`, blob `481660fb6008a57cea162da38439cf115c8d7ebe`
- long_horizon role: control_revision `17`, config_revision `8`, blob `d790db45343bec399d00c6e9410432963726d72c`
- authority branch: `clean-long-horizon-phase1-active`
- predecessor LATEST blob: `ce539dea4696bf23c9f537e97500bc69a18e54dc`
- preflight path: `research_workers_clean_g1/long_horizon/PREFLIGHT_2026-09-02T0320JST_RATE_LIMIT_ENVELOPE_STALE_BLOB_BINDING_V1.md`
- preflight exact-read blob: `13f89c2e0982236de6b4cc681a893f4450825d69`

## One bounded probe

Current LIVE was read after preflight and matched the predecessor contract exactly: `state_sequence=6`, `plan_generation=3`, current blob `f79a86302e6c4fcb095aec7b22cc6491bb3da20a`. The only substituted negative coordinate was predecessor LIVE blob `5217ac80d20baad6afd158bd5e39c4b39e9200ff` supplied as the GitHub Contents API CAS precondition while preserving the current LIVE content byte-for-byte.

Observed result: `REJECT_STALE_BLOB_BINDING`. The update call returned HTTP `409` with message that the LIVE path does not match stale blob `5217ac80d20baad6afd158bd5e39c4b39e9200ff`. The single permitted post-conflict reread returned current LIVE blob `f79a86302e6c4fcb095aec7b22cc6491bb3da20a` with `state_sequence=6` and `plan_generation=3` unchanged.

Within this tested role-local branch/path scope:
- LIVE mutation issued successfully: `false`
- physical LIVE state changed: `false`
- retry/backoff resampled: `false`
- prior plan reactivated: `false`
- retry attempt 4 written: `false`
- same-run wait/poll/backoff/retry: `false`
- scheduler mutation: `false`
- optional second leaf: `false`
- residual richer-mode/Work/protected/manual-user execution dependency: `false`
- finite monthly/trial/paid quota dependency: `false`
- incremental monetary cost: `0`

This proves only that the current Chat-exposed repository Contents API path rejects a stale content-blob CAS coordinate for this role-local LIVE file and leaves the verified state unchanged. It does not prove all stale-authority classes or global task completion.

## Exact continuation

Next effect_chain_id: `clean-latest-pointer-stale-cas-binding-v1`.

On the next invocation, freshly bootstrap/freeze required controls, reconstruct canonical role state from the then-current `research_workers_clean_g1/long_horizon/LATEST.md`, and persist/exact-read the required preflight before semantic work. Hold the current authority branch, current LIVE blob/sequence/generation, and current LATEST content fixed. Use predecessor LATEST blob `ce539dea4696bf23c9f537e97500bc69a18e54dc` as the only stale CAS coordinate in one update attempt against the then-current LATEST path while preserving its current content. Require HTTP 409-style stale-CAS rejection plus one readback proving the pointer did not roll back. Do not mutate LIVE, resample retry/backoff, reactivate an earlier plan, wait/poll/retry, mutate the scheduler, or start a second leaf. Persist exact result and another nonempty continuation; Phase 1 remains open.
