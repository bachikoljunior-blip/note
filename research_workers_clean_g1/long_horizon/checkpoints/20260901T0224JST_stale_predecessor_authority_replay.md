# Long Horizon Phase-1 — stale predecessor authority replay

## Frozen authority / one bounded leaf
- role: `long_horizon`
- phase_id: `phase_1_chat_parity`
- root_problem_id: `o-chat-parity-root-v4-zero-work-dependency-zero-quota`
- task_id: `phase1-clean-long-horizon-overrun-recovery`
- effect_chain_id: `clean-rate-limit-stale-predecessor-authority-replay-v1`
- transport_mode: `sha_pinned_main`
- frozen main SHA: `09038e6e7a8c2132e728f1b402d3d80396a9afa0`
- manifest: control_revision `27`
- RUN_LIFECYCLE: control_revision `1`, blob `8fe5d79365dcd943984d69f4767b2ed0c03fc3ac`
- DESIRED_STATE: control_revision `26`, blob `481660fb6008a57cea162da38439cf115c8d7ebe`
- long_horizon: control_revision `17`, config_revision `8`, blob `d790db45343bec399d00c6e9410432963726d72c`
- predecessor LATEST blob: `dddaacf5148c79e083ff65c300ed4dfa0f0177a8`
- preflight: `research_workers_clean_g1/long_horizon/preflight/20260901T0223JST_stale_predecessor_authority_replay_preflight.json`, blob `21fd9352e59b46d086f7128e4466abd7fd1f84a9`
- bootstrap_valid: `true`
- enabled_desired: `true`

Exactly one semantic leaf was executed. No wait/poll/backoff, same-run retry, scheduler mutation, optional second leaf, richer-mode/Work, protected-primary/manual execution, hosted compute, or finite-quota feature was used.

## Canonical state readback
Exact read of `research_workers_clean_g1/long_horizon/phase1/LIVE_RATE_LIMIT_STATE.json` returned blob `f79a86302e6c4fcb095aec7b22cc6491bb3da20a`, matching the predecessor checkpoint's expected canonical LIVE blob. Observed state remained `state_sequence=6`, `plan_generation=3`, `current_plan=defer_no_retry_plan`, `retry_attempt=3`, `max_attempts=3`, `enabled_desired=true`.

No LIVE-state write was performed.

## Stale-predecessor replay control
Reused the prior authority-fingerprint rule unchanged:

`SHA256("long_horizon|phase_1_chat_parity|phase1-clean-long-horizon-overrun-recovery|envelope-authority-binding|v1\n" || canonical_json(authority_tuple))`

Common fields in both tuples:
- `canonical_live_blob=f79a86302e6c4fcb095aec7b22cc6491bb3da20a`
- `expected_digest=94439588c4affad23c613ea8406d2fdf29d3be63f8d1c0acec3c156e9030be4b`
- `semantic_envelope_version=live-rate-limit-continuation-envelope|v1|state-schema-1`

Old authority tuple used predecessor LATEST blob `1ca604313274d16b2fa66bdba91866fba28d6015` and recomputed to fingerprint `4d9dbe376a8772ae317933566c517c5cd3000fbdbeaca4b61161df69e4289e59`.

Freshly rebound tuple used the actual current predecessor LATEST blob `dddaacf5148c79e083ff65c300ed4dfa0f0177a8` and recomputed to fingerprint `a08dc3a2f23ed450c22feacd5bd91068f847fb3d12cf9a751acf613d4b10cfb5`.

Observed deterministic decision:
- old tuple replay => `REJECT_STALE_PREDECESSOR`: its predecessor LATEST identity is not the current predecessor blob; canonical LIVE blob, semantic digest and envelope version were otherwise unchanged.
- fresh rebound tuple => `ADMIT`: predecessor identity matches current LATEST while the canonical LIVE blob and semantic digest remain unchanged.
- LIVE state before/after => identical blob `f79a86302e6c4fcb095aec7b22cc6491bb3da20a`.

This closes only the tested pointer-advance replay case: an otherwise unchanged authority tuple does not regain authority after LATEST advances unless it is rebound to the new predecessor identity. It is not a powered task-success result and does not prove resistance to arbitrary branch replacement or external principal compromise.

## Zero-dependency / quota / cost scope
Residual richer-mode/Work dependency: none introduced. Protected-primary/manual execution dependency: none introduced. Finite monthly/trial/paid quota dependency: none introduced. Incremental monetary cost: `0`. Repository text transport only; no hosted compute/storage allowance used.

## Exact nonempty continuation
Next effect_chain_id: `clean-rate-limit-stale-generation-replay-v1`.

Freshly bootstrap/freeze the four required controls; reconstruct the then-current role-local `LATEST.md`; exact-read canonical `research_workers_clean_g1/long_horizon/phase1/LIVE_RATE_LIMIT_STATE.json`. In exactly one bounded in-memory control, replay a continuation authorized by stale predecessor generation `2` / prior state blob `5217ac80d20baad6afd158bd5e39c4b39e9200ff` against canonical generation `3` / current LIVE blob. Require rejection with no LIVE mutation, and compare one freshly bound generation-3 continuation as the untouched positive control. Do not wait/poll/backoff/retry, start a second leaf, mutate scheduler, use richer/protected/manual execution, or consume any finite-quota feature. Persist/read back preflight, result/checkpoint, LATEST and one immutable own receipt.

`termination=bounded_slice_complete_recurring_open`
`global_completion=false`
`phase1_completion_claimed=false`
`enabled_desired=true`
`scheduler_mutation_by_worker=false`
`continuation_nonempty=true`
`hard_runtime_boundary_reached=false`
`next_invocation_resumes_exact_continuation=true`
