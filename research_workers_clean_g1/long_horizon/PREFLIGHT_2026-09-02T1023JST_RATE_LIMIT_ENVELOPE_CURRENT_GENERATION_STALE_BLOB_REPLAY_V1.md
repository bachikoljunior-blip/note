# CLEAN long_horizon preflight — current-generation stale-blob replay

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

## Frozen authority tuple

- INSTRUCTION_CONTROL_MANIFEST: control_revision `48`, blob `410269a4b6e7d06d73721807149313360c1273e8`
- RUN_LIFECYCLE: control_revision `1`, blob `8fe5d79365dcd943984d69f4767b2ed0c03fc3ac`
- DESIRED_STATE: control_revision `26`, manifest-bound blob `481660fb6008a57cea162da38439cf115c8d7ebe`
- long_horizon role config: control_revision `17`, config_revision `8`, blob `d790db45343bec399d00c6e9410432963726d72c`

## Reconstructed predecessor/frontier

- canonical branch: `clean-long-horizon-phase1-active`
- predecessor LATEST blob: `3d0f379f6b4bee0e883eb64b6aace7266d3a5c22`
- predecessor effect_chain_id: `clean-rate-limit-envelope-stale-generation-replay-v1`
- exact continuation: evaluate one synthetic continuation that claims the current LIVE `plan_generation` while presenting stale CAS authority blob `5217ac80d20baad6afd158bd5e39c4b39e9200ff`; expected decision `REJECT_STALE_BLOB_AUTHORITY` with no LIVE mutation, plan reactivation, retry/backoff resampling, wait/retry, or second leaf.

## Planned atomic boundary

1. Fetch only the current role-local `phase1/LIVE_RATE_LIMIT_STATE.json` after this preflight readback.
2. Bind the synthetic claim to that exact current `plan_generation`.
3. Compare supplied stale authority blob `5217ac80d20baad6afd158bd5e39c4b39e9200ff` with the exact current LIVE blob.
4. If the blobs differ, reject before any mutation or retry scheduling as `REJECT_STALE_BLOB_AUTHORITY`; if they unexpectedly match, persist a bounded diagnostic instead of mutating LIVE.
5. Persist/read back one checkpoint, update LATEST by CAS, and create/read back one own receipt if the write budget remains safe.

## Forecast / switch threshold

- one semantic leaf only; no optional second chain
- no same-run wait, poll, backoff, or transient retry
- if LIVE authority cannot be read or is unverifiable, stop the leaf as bounded diagnostic and preserve the same exact continuation
- if remaining write budget cannot safely complete checkpoint + LATEST CAS, prioritize checkpoint and nonempty continuation over optional receipt
