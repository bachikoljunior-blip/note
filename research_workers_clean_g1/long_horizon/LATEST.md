# Long Horizon clean_g1 — LATEST

- phase_id: `phase_1_chat_parity`
- root_problem_id: `o-chat-parity-root-v4-zero-work-dependency-zero-quota`
- task_id: `phase1-clean-long-horizon-overrun-recovery`
- role: `long_horizon`
- enabled_desired: `true`
- bootstrap_valid: `true`
- transport_mode: `exact_blob_two_pass`
- termination: `bounded_slice_complete_recurring_open`
- global_completion: `false`
- phase1_completion_claimed: `false`
- scheduler_mutation_by_worker: `false`

## Frozen control
- instruction manifest: revision `21`, blob `5a769b5d12aa818b4f0aa5bbd689032cc54adb03`
- RUN_LIFECYCLE: revision `1`, blob `8fe5d79365dcd943984d69f4767b2ed0c03fc3ac`
- DESIRED_STATE: revision `26`, blob `481660fb6008a57cea162da38439cf115c8d7ebe`
- role config: control_revision `17`, config_revision `8`, blob `d790db45343bec399d00c6e9410432963726d72c`

## Completed bounded leaf
Effect chain: `clean-rate-limit-full-continuation-envelope-fingerprint-guard-v1`.

Checkpoint: `research_workers_clean_g1/long_horizon/checkpoints/20260831T1723JST_full_continuation_envelope_guard.md`
Checkpoint blob after exact readback: `ba1e7d3664463e7e273f8352f74eb5a41ef75b6c`
Preflight: `research_workers_clean_g1/long_horizon/preflight/20260831T1723JST_full_continuation_envelope_guard_preflight.json`
Preflight blob: `f474232c700a93c0829be378b8c8b45fa5879d92`

Canonical state resolved to `research_workers_clean_g1/long_horizon/phase1/LIVE_RATE_LIMIT_STATE.json`, blob `f79a86302e6c4fcb095aec7b22cc6491bb3da20a`, sequence `6`, generation `3`, plan `defer_no_retry_plan`.

A versioned/domain-separated SHA-256 semantic envelope was defined over the structured decision-bearing continuation body while repository blob/CAS identity stayed separate. Canonical digest: `94439588c4affad23c613ea8406d2fdf29d3be63f8d1c0acec3c156e9030be4b`.

One substitution preserved `state_sequence=6`, `plan_generation=3`, and `current_plan=defer_no_retry_plan` but changed decision-bearing `max_attempts:3->4`. Its digest became `8dcc1f4d28c06b53fd3955feddbfd675689b082da5e954037a06351e7502820b`; full-envelope guard rejected it before any LIVE write. Untouched canonical body recomputed to the expected digest and admitted. No LIVE state mutation occurred.

Scope: deterministic role-local continuation-integrity mechanism test only. The expected digest itself was trusted in this leaf, so body+expected-digest joint substitution remains open. No residual richer-mode/Work/protected-primary/manual execution dependency, finite monthly/trial/paid quota, hosted compute/storage allowance, or incremental monetary cost was introduced.

## Exact nonempty continuation
Next effect_chain_id: `clean-rate-limit-envelope-authority-binding-v1`.

Freshly bootstrap/freeze `INSTRUCTION_CONTROL_MANIFEST.json`, `RUN_LIFECYCLE.json`, `DESIRED_STATE.json`, and `automation_control/roles/long_horizon.json`; reconstruct this exact checkpoint from this `LATEST.md`; exact-read canonical `LIVE_RATE_LIMIT_STATE.json` plus expected semantic-envelope digest `94439588c4affad23c613ea8406d2fdf29d3be63f8d1c0acec3c156e9030be4b`. Define one durable authority tuple binding `predecessor LATEST blob + canonical LIVE blob + semantic-envelope version + expected digest`. In exactly one bounded in-memory control, preserve `state_sequence`, `plan_generation`, and `current_plan`, change `max_attempts`, and recompute a self-consistent substituted expected digest; require rejection because that substituted digest is not bound to the frozen predecessor-authority tuple. Untouched tuple must admit. Do not mutate LIVE state, start a second leaf, wait/poll/backoff/retry, mutate scheduler, use richer/protected/manual execution, or consume any finite-quota feature. Persist and exact-read back one preflight, result/checkpoint, this LATEST pointer, and one immutable own receipt, carrying a further nonempty continuation.
