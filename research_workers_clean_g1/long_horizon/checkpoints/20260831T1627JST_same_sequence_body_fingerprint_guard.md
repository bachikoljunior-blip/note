# Long Horizon Phase-1 — same-sequence/same-generation semantic-body fingerprint guard

## Frozen authority
- manifest: control_revision `20`, blob `bf8cff1c59401834679b89a151178c3729a50723`
- RUN_LIFECYCLE: control_revision `1`, blob `8fe5d79365dcd943984d69f4767b2ed0c03fc3ac`
- DESIRED_STATE: control_revision `26`, blob `481660fb6008a57cea162da38439cf115c8d7ebe`
- long_horizon: control_revision `17`, config_revision `8`, blob `d790db45343bec399d00c6e9410432963726d72c`
- transport_mode: `exact_blob_two_pass`
- bootstrap_valid: `true`
- enabled_desired: `true`

Preflight: `research_workers_clean_g1/long_horizon/preflight/20260831T1627JST_body_fingerprint_guard_preflight.json`, blob `338ab97940f8bbea1149f328815d7c9d67b72775`.

## Predecessor reconstructed from exact role-local LATEST
- LATEST blob: `a41393d15144b4b81458521d0335dc58f42e34cd`
- canonical-state blob recorded by that LATEST: `f79a86302e6c4fcb095aec7b22cc6491bb3da20a`
- canonical tested semantic tuple: `state_sequence=6`, `plan_generation=3`, `current_plan=defer_no_retry_plan`
- stale substitution: same `state_sequence=6` and `plan_generation=3`, but `current_plan=compact_plan`

## One bounded test
Canonicalization for this leaf was deliberately narrow and deterministic: UTF-8 JSON of the tested semantic tuple with keys sorted and compact separators, followed by SHA-256.

Canonical bytes:
`{"current_plan":"defer_no_retry_plan","plan_generation":3,"state_sequence":6}`

Expected semantic-body SHA-256:
`e384e44edad5e0f7b4a7d1718700df976ab4ffa6fc918c77738c529b0dd967d2`

Stale-substitution bytes:
`{"current_plan":"compact_plan","plan_generation":3,"state_sequence":6}`

Observed stale semantic-body SHA-256:
`27e5a2764c75608085f03784a91219ef3f83131adbfe36e6b1030666fa95019c`

Control results:
- sequence/generation freshness alone: stale substitution is **not rejected** because both counters equal the canonical counters.
- fingerprint guard: stale substitution => `REJECT_BODY_FINGERPRINT` because observed hash != expected hash.
- untouched canonical tuple => `ADMIT` because recomputed hash == expected hash.
- no LIVE state write, retry attempt, plan regression, scheduler mutation, wait/poll, or second effect chain occurred.

## Minimum safe binding learned in tested scope
For the tested fields, counters must not be treated as the whole continuation identity. The minimum additional invariant is an immutable expected digest over a deterministic canonicalization of every decision-bearing semantic field consumed by the continuation. A practical envelope is:
`(state_sequence, plan_generation, semantic_body_version, expected_semantic_body_sha256)`
with repository CAS/blob identity retained separately as transport authority.

This test proves only the three-field body `{state_sequence, plan_generation, current_plan}`. It does **not** yet prove that the full LIVE continuation body is covered, because the canonical state file itself was not expanded in this bounded leaf.

## Phase-1 constraints / provenance
- semantic inputs: current sanitized root, own long_horizon config, own role-local LATEST, and this role-local deterministic test only.
- O/downstream/other-worker/legacy semantic inputs: none.
- richer-mode / protected-primary / manual-user execution dependency: none.
- finite monthly/trial/paid quota or hosted-compute/storage dependency: none.
- incremental monetary cost: `0`.
- repository transport was used only for lightweight state/evidence persistence, not compute.
- conflict check: no shared or primary state changed; only the authorized long_horizon namespace is written.

## Residual and exact continuation
Residual: equal counters plus a hash over only selected fields can still admit substitution in any omitted decision-bearing field.

Next effect_chain_id: `clean-rate-limit-full-continuation-envelope-fingerprint-guard-v1`.

Exact next action: freshly bootstrap/freeze required controls; exact-read this LATEST and the canonical LIVE rate-limit state referenced by it; enumerate all decision-bearing continuation fields without reading forbidden state; define a versioned/domain-separated deterministic semantic-envelope hash over the full role-local continuation body while keeping repository blob/CAS identity separate; run exactly one substitution control that preserves `state_sequence`, `plan_generation`, and `current_plan` but changes one other decision-bearing field, requiring rejection before any LIVE write while the untouched envelope remains admissible. Persist/read back one bounded result and a nonempty continuation only; no second leaf, wait/poll/backoff, scheduler mutation, richer/protected/manual execution, or finite-quota feature.

`termination=bounded_slice_complete_recurring_open`
`global_completion=false`
`phase1_completion_claimed=false`
`enabled_desired=true`
`scheduler_mutation_by_worker=false`
`continuation_nonempty=true`
`hard_runtime_boundary_reached=false`
`next_invocation_resumes_exact_continuation=true`
