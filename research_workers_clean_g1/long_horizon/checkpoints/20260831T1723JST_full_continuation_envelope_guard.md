# Long Horizon Phase-1 — full continuation semantic-envelope fingerprint guard

## Frozen authority / bounded leaf
- role: `long_horizon`
- phase: `phase_1_chat_parity`
- root problem: `o-chat-parity-root-v4-zero-work-dependency-zero-quota`
- task: `phase1-clean-long-horizon-overrun-recovery`
- effect_chain_id: `clean-rate-limit-full-continuation-envelope-fingerprint-guard-v1`
- manifest: control_revision `21`, blob `5a769b5d12aa818b4f0aa5bbd689032cc54adb03`
- RUN_LIFECYCLE: control_revision `1`, blob `8fe5d79365dcd943984d69f4767b2ed0c03fc3ac`
- DESIRED_STATE: control_revision `26`, blob `481660fb6008a57cea162da38439cf115c8d7ebe`
- long_horizon config: control_revision `17`, config_revision `8`, blob `d790db45343bec399d00c6e9410432963726d72c`
- transport_mode: `exact_blob_two_pass`
- bootstrap_valid: `true`
- enabled_desired: `true`
- preflight: `research_workers_clean_g1/long_horizon/preflight/20260831T1723JST_full_continuation_envelope_guard_preflight.json`, blob `f474232c700a93c0829be378b8c8b45fa5879d92`

Exactly one semantic leaf was executed. No wait/poll/backoff, retry, scheduler mutation, optional second leaf, protected-primary action, richer-mode execution, manual execution, hosted compute, or quota-bearing feature was used.

## Reconstructed canonical continuation
The predecessor `LATEST.md` blob `2dda0a55a27f7dd9adc93f83092ed686255f4158` named canonical state blob `f79a86302e6c4fcb095aec7b22cc6491bb3da20a`. Own-state directory reconstruction resolved it exactly to:

`research_workers_clean_g1/long_horizon/phase1/LIVE_RATE_LIMIT_STATE.json`

Readback matched blob `f79a86302e6c4fcb095aec7b22cc6491bb3da20a`, with `state_sequence=6`, `plan_generation=3`, `current_plan=defer_no_retry_plan`, `retry_attempt=3`, `max_attempts=3`, and `enabled_desired=true`.

## Versioned/domain-separated semantic envelope
Repository blob/CAS identity remains a separate transport-authority layer. The semantic-envelope digest uses SHA-256 over UTF-8 bytes:

`DOMAIN_SEPARATOR || canonical_json(decision_body)`

Domain separator, including the trailing newline:

`long_horizon|phase_1_chat_parity|phase1-clean-long-horizon-overrun-recovery|live-rate-limit-continuation-envelope|v1|state-schema-1\n`

Canonical JSON uses sorted keys, compact separators, JSON `null/true/false`, UTF-8, and no whitespace padding.

Decision-bearing top-level fields included:

`state_sequence`, `plan_generation`, `previous_plan_generation`, `retry_attempt`, `max_attempts`, `observation`, `observation_time`, `retry_after_seconds`, `not_before`, `selected_backoff_seconds`, `backoff_source`, `backoff_status`, `backoff_formula`, `cross_invocation_transition`, `budget_remaining_seconds`, `forecast_p90_remaining_seconds`, `retry_reserve_seconds`, `forecast_required_seconds`, `forecast_overrun`, `previous_plan`, `current_plan`, `alternative_plan`, `switch_count`, `switch_cause`, `external_work_attempt_consumed_for_switch`, `current_decision`, `stale_generation_rule`, `next_invocation_rule`, `incremental_monetary_cost`, `enabled_desired`, `global_completion`, `phase1_completion_claimed`.

Within `cross_invocation_transition`, every structured decision/effect-consumption field is included except repository/provenance blobs `pre_mutation_blob` and `preflight_blob`. Static `schema_version`, `role`, `phase_id`, and `task_id` are bound by the domain separator instead of duplicated inside the decision body. Repository transport fields `authority_branch` and `authority_file_blob` remain separate from the semantic digest. Descriptive evidence-only strings `decision_reason` and `quota_zero_assessment` are intentionally non-authoritative and excluded; continuation policy must not derive authorization from those prose fields.

Canonical decision body (exact):

```json
{"alternative_plan":null,"backoff_formula":"min(60*2^(attempt-1),300)","backoff_source":"persisted_from_generation_2_not_resampled","backoff_status":"historical_not_reapplied_after_retry_exhaustion","budget_remaining_seconds":1000,"cross_invocation_transition":{"authority_generation":1,"backoff_resampled":false,"current_plan_after":"defer_no_retry_plan","current_plan_before":"compact_plan","max_attempts":3,"new_synthetic_429_consumed":true,"plan_generation_after":3,"plan_generation_before":2,"prior_state_sequence":5,"retry_attempt_4_written":false,"retry_attempt_after":3,"retry_attempt_before":3,"same_run_retry_performed":false,"same_run_wait_performed":false,"second_leaf_started":false,"selected_backoff_seconds_after":240,"selected_backoff_seconds_before":240,"state_sequence_after":6,"switch_count_after":2,"switch_count_before":1},"current_decision":"SWITCH_PLAN","current_plan":"defer_no_retry_plan","enabled_desired":true,"external_work_attempt_consumed_for_switch":false,"forecast_overrun":true,"forecast_p90_remaining_seconds":900,"forecast_required_seconds":1200,"global_completion":false,"incremental_monetary_cost":0,"max_attempts":3,"next_invocation_rule":"Reconstruct this exact sequence-6 generation-3 state from the canonical role branch. In exactly one bounded leaf, test stale-generation replay defense by attempting a continuation authorized by predecessor generation=2/blob=5217ac80d20baad6afd158bd5e39c4b39e9200ff and require rejection/no state mutation; do not combine with another leaf.","not_before":null,"observation":"synthetic_429_missing_retry_after_at_exhausted_budget","observation_time":"2026-08-31T02:22:21+09:00","phase1_completion_claimed":false,"plan_generation":3,"previous_plan":"compact_plan","previous_plan_generation":2,"retry_after_seconds":null,"retry_attempt":3,"retry_reserve_seconds":300,"selected_backoff_seconds":240,"stale_generation_rule":"Any continuation carrying plan_generation < 3 is stale and must not reactivate compact_plan or any prior plan; repository writes must use the current content blob as CAS authority.","state_sequence":6,"switch_cause":"RETRY_BUDGET_EXHAUSTED","switch_count":2}
```

Expected semantic-envelope SHA-256:
`94439588c4affad23c613ea8406d2fdf29d3be63f8d1c0acec3c156e9030be4b`

## One substitution control + untouched control
The stale/substituted candidate preserved all three previously tested identity fields exactly:
- `state_sequence=6`
- `plan_generation=3`
- `current_plan=defer_no_retry_plan`

It changed exactly one other decision-bearing field: top-level `max_attempts: 3 -> 4`. That substitution is safety-relevant because `retry_attempt=3`; changing `max_attempts` changes whether retry budget is exhausted without changing sequence, generation, or plan.

Observed substituted semantic-envelope SHA-256:
`8dcc1f4d28c06b53fd3955feddbfd675689b082da5e954037a06351e7502820b`

Results:
- sequence/generation/current-plan equality alone => substituted candidate would remain superficially current.
- full semantic-envelope guard => `REJECT_SEMANTIC_ENVELOPE_FINGERPRINT` because `8dcc... != 9443...`.
- untouched canonical body recomputation => `ADMIT` because digest exactly equals `94439588...`.
- rejection occurs before any LIVE-state write. `LIVE_RATE_LIMIT_STATE.json` was not mutated by this leaf.

This closes the predecessor's omitted-field counterexample for the enumerated decision body: equal sequence/generation/current-plan no longer suffices when another structured decision-bearing field changes.

## Exact scope / remaining gap
This is a deterministic integrity mechanism test over the current role-local LIVE continuation schema; it is not a powered task-success evaluation. The expected digest was trusted as a precommitted value in this leaf. Therefore a candidate that substitutes both the semantic body **and** a self-consistent recomputed expected digest is not yet rejected by the semantic hash alone. Repository blob/CAS authority is separate, but the durable binding between `(predecessor authority, semantic-envelope version, expected digest)` remains the next stale-authority child problem.

No residual richer-mode/Work/protected-primary/manual-user execution dependency was introduced. No finite monthly/trial/paid quota or hosted compute/storage dependency was used. Incremental monetary cost is `0`. Repository access was lightweight state/evidence transport only.

## Nonempty exact continuation
Next effect_chain_id: `clean-rate-limit-envelope-authority-binding-v1`.

Exact next action: freshly bootstrap/freeze required controls; reconstruct this checkpoint through role-local `LATEST.md`; exact-read canonical `LIVE_RATE_LIMIT_STATE.json` and the immutable expected semantic-envelope digest recorded here; define a durable authority tuple binding `predecessor LATEST blob + canonical LIVE blob + semantic-envelope version + expected digest`. Run exactly one in-memory counterexample where `state_sequence`, `plan_generation`, and `current_plan` remain unchanged but `max_attempts` and its expected digest are both substituted self-consistently. Require rejection because the substituted digest is not bound to the frozen predecessor-authority tuple; untouched tuple must admit. Do not mutate LIVE state, start another leaf, wait/poll/backoff/retry, mutate scheduler, use richer/protected/manual execution, or consume any finite-quota feature. Persist/read back one bounded result, `LATEST.md`, and one immutable own receipt with a further nonempty continuation.

`termination=bounded_slice_complete_recurring_open`
`global_completion=false`
`phase1_completion_claimed=false`
`enabled_desired=true`
`scheduler_mutation_by_worker=false`
`continuation_nonempty=true`
`hard_runtime_boundary_reached=false`
`next_invocation_resumes_exact_continuation=true`
