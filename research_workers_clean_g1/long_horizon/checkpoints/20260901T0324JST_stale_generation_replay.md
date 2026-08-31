# Long Horizon Phase-1 checkpoint — stale generation replay

- role: `long_horizon`
- effect_chain_id: `clean-rate-limit-stale-generation-replay-v1`
- phase_id: `phase_1_chat_parity`
- root_problem_id: `o-chat-parity-root-v4-zero-work-dependency-zero-quota`
- task_id: `phase1-clean-long-horizon-overrun-recovery`
- bootstrap_valid: `true`
- transport_mode: `exact_blob_two_pass`
- enabled_desired: `true`
- global_completion: `false`
- phase1_completion_claimed: `false`
- scheduler_mutation_by_worker: `false`

## Frozen authority

Manifest control27 was readable first; RUN_LIFECYCLE control1/blob `8fe5d79365dcd943984d69f4767b2ed0c03fc3ac`; DESIRED_STATE control26/blob `481660fb6008a57cea162da38439cf115c8d7ebe`; long_horizon control17/config8/blob `d790db45343bec399d00c6e9410432963726d72c`. Root and role were identical across the required two passes.

Predecessor LATEST blob: `a85129d7b8d6fbc687fed1ad8cbf30df1169c8d1` on `clean-long-horizon-phase1-active`.
Preflight: `research_workers_clean_g1/long_horizon/preflight/20260901T0323JST_stale_generation_replay_preflight.json`, exact-read blob `9c209a1bd3c68227b74d06bde8abe405fdeb37f6`.
Canonical LIVE state before and after the bounded control: blob `f79a86302e6c4fcb095aec7b22cc6491bb3da20a`, `state_sequence=6`, `plan_generation=3`.

## Single bounded control

Precommitted authority predicate: reject when the presented continuation has `plan_generation < canonical_plan_generation` **or** its presented state blob differs from the canonical LIVE blob. No repository mutation is part of the predicate.

Negative control presented generation `2` with prior-state blob `5217ac80d20baad6afd158bd5e39c4b39e9200ff` against canonical generation `3` / LIVE blob `f79a86302e6c4fcb095aec7b22cc6491bb3da20a`.

Result: `REJECT_STALE_GENERATION_AND_STATE_BLOB`.

Positive control presented generation `3` with LIVE blob `f79a86302e6c4fcb095aec7b22cc6491bb3da20a`.

Result: `ADMIT_CURRENT_AUTHORITY`.

The exact-read after evaluation returned the same LIVE blob, sequence and generation, so this leaf caused no LIVE-state mutation. It also did not reactivate `compact_plan`, consume retry attempt 4, resample backoff, wait/poll, retry a connector operation, or start a second semantic leaf.

## Scope and acceptance guards

This proves only the precommitted compound stale-generation/state-blob predicate on the canonical role-local repository state. Because the negative control violated both generation and blob predicates, it does **not** yet isolate the blob-fence contribution.

Residual richer-mode/Work/protected-primary/manual execution dependency: none introduced.
Finite monthly/trial/paid quota dependency: none introduced; only lightweight repository text transport was used.
Incremental monetary cost: `0`.
Conflict check: role-local namespace and canonical role branch only; no O, downstream, other-worker semantics or scheduler mutation consumed.

## Exact continuation

Next effect_chain_id: `clean-rate-limit-stale-blob-replay-v1`.

Freshly bootstrap/freeze required controls, reconstruct the LATEST produced by this slice, and exact-read the same canonical LIVE state. In exactly one bounded in-memory control, present `plan_generation=3` but stale prior-state blob `5217ac80d20baad6afd158bd5e39c4b39e9200ff`; require rejection solely by the state-blob/CAS authority fence, compare generation `3` + current LIVE blob as the positive control, verify no LIVE mutation, then persist/read back checkpoint, LATEST and immutable own receipt. Preserve `enabled_desired=true`, `global_completion=false`, `phase1_completion_claimed=false`; do not mutate scheduler or start a second leaf.

Termination for this slice: `bounded_slice_complete_recurring_open`.
