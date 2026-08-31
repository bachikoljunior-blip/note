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
- instruction manifest: revision `22`, blob `0813ae6396724ef2661a942b03c0e0b54c562bfa`
- RUN_LIFECYCLE: revision `1`, blob `8fe5d79365dcd943984d69f4767b2ed0c03fc3ac`
- DESIRED_STATE: revision `26`, blob `481660fb6008a57cea162da38439cf115c8d7ebe`
- role config: control_revision `17`, config_revision `8`, blob `d790db45343bec399d00c6e9410432963726d72c`

## Completed bounded leaf
Effect chain: `clean-rate-limit-envelope-authority-binding-v1`.

Checkpoint: `research_workers_clean_g1/long_horizon/checkpoints/20260831T2135JST_envelope_authority_binding.md`
Checkpoint blob after exact readback: `d30284cb4477bffa2613f88c4cac651c69534b9f`
Preflight: `research_workers_clean_g1/long_horizon/preflight/20260831T2135JST_envelope_authority_binding_preflight.json`
Preflight blob: `f03d8c674fc494bf266763cf0ec4d1fcf007588a`
Immutable receipt path: `automation_control/receipts/long_horizon/20260831T2135JST_envelope_authority_binding.json` (created/read back after this pointer update).

Canonical LIVE state remained unchanged at blob `f79a86302e6c4fcb095aec7b22cc6491bb3da20a`, sequence `6`, generation `3`, plan `defer_no_retry_plan`.

Canonical semantic-envelope digest remained `94439588c4affad23c613ea8406d2fdf29d3be63f8d1c0acec3c156e9030be4b`. It is now durably bound to predecessor LATEST blob `1ca604313274d16b2fa66bdba91866fba28d6015`, canonical LIVE blob, and envelope version `live-rate-limit-continuation-envelope|v1|state-schema-1`. Canonical authority fingerprint: `4d9dbe376a8772ae317933566c517c5cd3000fbdbeaca4b61161df69e4289e59`.

One in-memory substitution preserved `state_sequence=6`, `plan_generation=3`, and `current_plan=defer_no_retry_plan`, changed top-level `max_attempts:3->4`, and recomputed a self-consistent candidate expected digest `8dcc1f4d28c06b53fd3955feddbfd675689b082da5e954037a06351e7502820b`. Its local semantic hash check passed, but the corresponding authority fingerprint became `2df1e74a328fbb669d5d8b9dee760aeadf4349736901438f4f5a48a2a6100207` and was rejected because it was not the frozen predecessor-authority binding. Untouched canonical tuple admitted. No LIVE state mutation occurred.

Scope: deterministic role-local continuation-integrity mechanism test only. No residual richer-mode/Work/protected-primary/manual execution dependency, finite monthly/trial/paid quota, hosted compute/storage allowance, or incremental monetary cost was introduced.

## Exact nonempty continuation
Next effect_chain_id: `clean-rate-limit-envelope-authority-replay-after-latest-advance-v1`.

Freshly bootstrap/freeze `INSTRUCTION_CONTROL_MANIFEST.json`, `RUN_LIFECYCLE.json`, `DESIRED_STATE.json`, and `automation_control/roles/long_horizon.json`; reconstruct this exact checkpoint from the then-current `LATEST.md`; exact-read canonical `LIVE_RATE_LIMIT_STATE.json`. Treat checkpoint authority fingerprint `4d9dbe376a8772ae317933566c517c5cd3000fbdbeaca4b61161df69e4289e59` as old authority. Bind a fresh tuple to the new predecessor `LATEST.md` blob while keeping the same LIVE blob, envelope version, and semantic digest if unchanged. In exactly one bounded in-memory control, replay the old tuple and require rejection solely because its predecessor LATEST blob is stale; freshly rebound tuple must admit. Do not mutate LIVE state, start a second leaf, wait/poll/backoff/retry, mutate scheduler, use richer/protected/manual execution, or consume any finite-quota feature. Persist and exact-read back one preflight, result/checkpoint, LATEST pointer, and one immutable own receipt with a further nonempty continuation.
