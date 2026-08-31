# Long Horizon Phase-1 — semantic-envelope authority binding

## Frozen authority / bounded leaf
- role: `long_horizon`
- phase: `phase_1_chat_parity`
- root problem: `o-chat-parity-root-v4-zero-work-dependency-zero-quota`
- task: `phase1-clean-long-horizon-overrun-recovery`
- effect_chain_id: `clean-rate-limit-envelope-authority-binding-v1`
- manifest: control_revision `22`, blob `0813ae6396724ef2661a942b03c0e0b54c562bfa`
- RUN_LIFECYCLE: control_revision `1`, blob `8fe5d79365dcd943984d69f4767b2ed0c03fc3ac`
- DESIRED_STATE: control_revision `26`, blob `481660fb6008a57cea162da38439cf115c8d7ebe`
- long_horizon config: control_revision `17`, config_revision `8`, blob `d790db45343bec399d00c6e9410432963726d72c`
- transport_mode: `exact_blob_two_pass`
- bootstrap_valid: `true`
- enabled_desired: `true`
- predecessor LATEST blob: `1ca604313274d16b2fa66bdba91866fba28d6015`
- preflight: `research_workers_clean_g1/long_horizon/preflight/20260831T2135JST_envelope_authority_binding_preflight.json`, blob `f03d8c674fc494bf266763cf0ec4d1fcf007588a`

Exactly one semantic leaf was executed. No wait/poll/backoff, same-run retry, scheduler mutation, optional second leaf, protected-primary action, richer-mode execution, manual execution, hosted compute, or quota-bearing feature was used.

## Canonical reconstruction
Exact readback of `research_workers_clean_g1/long_horizon/phase1/LIVE_RATE_LIMIT_STATE.json` matched the predecessor-declared blob `f79a86302e6c4fcb095aec7b22cc6491bb3da20a`, with `state_sequence=6`, `plan_generation=3`, `current_plan=defer_no_retry_plan`, `retry_attempt=3`, `max_attempts=3`, and `enabled_desired=true`.

The versioned/domain-separated continuation-envelope rule from the predecessor checkpoint was reused unchanged:

`SHA256("long_horizon|phase_1_chat_parity|phase1-clean-long-horizon-overrun-recovery|live-rate-limit-continuation-envelope|v1|state-schema-1\n" || canonical_json(decision_body))`

The untouched canonical body recomputed to:

`94439588c4affad23c613ea8406d2fdf29d3be63f8d1c0acec3c156e9030be4b`

matching the predecessor's immutable expected digest.

## Durable authority tuple
This leaf makes the expected digest non-self-authorizing by durably binding it to frozen predecessor/transport authority. The canonical authority tuple is:

```json
{"canonical_live_blob":"f79a86302e6c4fcb095aec7b22cc6491bb3da20a","expected_digest":"94439588c4affad23c613ea8406d2fdf29d3be63f8d1c0acec3c156e9030be4b","predecessor_latest_blob":"1ca604313274d16b2fa66bdba91866fba28d6015","semantic_envelope_version":"live-rate-limit-continuation-envelope|v1|state-schema-1"}
```

Authority fingerprint rule:

`SHA256("long_horizon|phase_1_chat_parity|phase1-clean-long-horizon-overrun-recovery|envelope-authority-binding|v1\n" || canonical_json(authority_tuple))`

Canonical authority fingerprint:

`4d9dbe376a8772ae317933566c517c5cd3000fbdbeaca4b61161df69e4289e59`

The checkpoint itself is the durable role-local record of this tuple/fingerprint; repository blob/CAS identity remains a separate transport layer.

## One self-consistent substitution control + untouched control
The substituted candidate preserved:
- `state_sequence=6`
- `plan_generation=3`
- `current_plan=defer_no_retry_plan`

It changed top-level `max_attempts: 3 -> 4`. Using the unchanged semantic-envelope rule, the candidate body recomputed to:

`8dcc1f4d28c06b53fd3955feddbfd675689b082da5e954037a06351e7502820b`

The candidate also substituted its supplied expected digest to that same `8dcc...` value. Therefore its local semantic body-vs-expected-digest check is self-consistent and passes; a hash-only guard that trusts the candidate-supplied expected digest would admit it.

Keeping predecessor LATEST blob, canonical LIVE blob, and envelope version unchanged but replacing the authority tuple's expected digest with `8dcc...` yields authority fingerprint:

`2df1e74a328fbb669d5d8b9dee760aeadf4349736901438f4f5a48a2a6100207`

Observed result:
- substituted candidate semantic self-check => `PASS_SELF_CONSISTENT_DIGEST`
- substituted candidate authority binding => `REJECT_AUTHORITY_BINDING` because `2df1... != 4d9d...`
- untouched canonical body semantic check => `PASS`
- untouched canonical authority tuple => `ADMIT` because its fingerprint remains exactly `4d9d...`
- rejection/admission was computed entirely in memory before any LIVE-state write.

This closes the predecessor's body+expected-digest joint-substitution counterexample for the frozen predecessor tuple: a candidate cannot make a changed decision body authoritative merely by recomputing and supplying its own matching expected digest.

## Scope / no-mutation evidence
This is a deterministic role-local continuation-integrity mechanism test, not a powered task-success evaluation. `LIVE_RATE_LIMIT_STATE.json` was read but not mutated. Incremental monetary cost is `0`; no finite monthly/trial/paid quota, hosted compute/storage allowance, richer-mode/Work, protected-primary merge, or manual execution dependency was introduced.

## Exact nonempty continuation
Next effect_chain_id: `clean-rate-limit-envelope-authority-replay-after-latest-advance-v1`.

Freshly bootstrap/freeze the four required controls; reconstruct this exact checkpoint through the then-current role-local `LATEST.md`; exact-read canonical `LIVE_RATE_LIMIT_STATE.json`. Treat this checkpoint's authority tuple/fingerprint as the old authority and bind a fresh tuple to the new predecessor `LATEST.md` blob while keeping the same canonical LIVE blob, envelope version, and semantic digest if they remain unchanged. In exactly one bounded in-memory control, replay the old authority tuple after the LATEST pointer advance and require rejection solely because its predecessor LATEST blob is stale; the freshly rebound tuple must admit. Do not mutate LIVE state, start another leaf, wait/poll/backoff/retry, mutate scheduler, use richer/protected/manual execution, or consume any finite-quota feature. Persist and exact-read back one preflight, result/checkpoint, LATEST pointer, and one immutable own receipt with a further nonempty continuation.

`termination=bounded_slice_complete_recurring_open`
`global_completion=false`
`phase1_completion_claimed=false`
`enabled_desired=true`
`scheduler_mutation_by_worker=false`
`continuation_nonempty=true`
`hard_runtime_boundary_reached=false`
`next_invocation_resumes_exact_continuation=true`
