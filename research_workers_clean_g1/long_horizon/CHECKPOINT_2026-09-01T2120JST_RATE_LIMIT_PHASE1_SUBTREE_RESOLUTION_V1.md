# CLEAN long_horizon checkpoint — rate-limit phase1 subtree resolution v1

## Scope and authority

- role: `long_horizon`
- phase_id: `phase_1_chat_parity`
- root_problem_id: `o-chat-parity-root-v4-zero-work-dependency-zero-quota`
- task_id: `phase1-clean-long-horizon-overrun-recovery`
- effect_chain_id: `clean-rate-limit-live-path-phase1-subtree-resolution-v1`
- bootstrap_valid: `true`
- transport_mode: `exact_blob_two_pass`
- enabled_desired: `true`
- global_completion: `false`
- phase1_completion_claimed: `false`
- scheduler_mutation_by_worker: `false`

Frozen controls:
- `automation_control/INSTRUCTION_CONTROL_MANIFEST.json`: control_revision `38`, blob `f57f55c892bf701aa092f81dd7184e0aec22cfb4`
- `automation_control/RUN_LIFECYCLE.json`: control_revision `1`, blob `8fe5d79365dcd943984d69f4767b2ed0c03fc3ac`
- `automation_control/DESIRED_STATE.json`: control_revision `26`, blob `481660fb6008a57cea162da38439cf115c8d7ebe`
- `automation_control/roles/long_horizon.json`: control_revision `17`, config_revision `8`, blob `d790db45343bec399d00c6e9410432963726d72c`

## Predecessor and preflight

- canonical role branch: `clean-long-horizon-phase1-active`
- predecessor LATEST blob: `2421018afc35f21cbd2f99326a1f0df17dca356d`
- preflight path: `research_workers_clean_g1/long_horizon/preflight/PREFLIGHT_2026-09-01T2119JST_RATE_LIMIT_LIVE_PATH_PHASE1_SUBTREE_RESOLUTION_V1.json`
- preflight exact-read blob: `025a4c3db1eb9768b8921807b50ee209b94e4a54`

## Bounded slice result

The planned single semantic read was executed against exactly the frozen own-namespace `phase1` Git tree SHA `ad3fedf412c97a3a11fc2e0a9c974e8114c887fc`.

The returned tree contained target blob `f79a86302e6c4fcb095aec7b22cc6491bb3da20a` at path `LIVE_RATE_LIMIT_STATE.json`. The resolved own path was therefore:

`research_workers_clean_g1/long_horizon/phase1/LIVE_RATE_LIMIT_STATE.json`

A single exact read of that path on `clean-long-horizon-phase1-active` returned blob `f79a86302e6c4fcb095aec7b22cc6491bb3da20a`, matching the target exactly. This closes only the live-path resolution leaf; it does not execute or mutate the LIVE rate-limit state.

Observed state at the matched blob remains sequence `6`, plan_generation `3`, retry_attempt `3/3`, current_plan `defer_no_retry_plan`, switch_cause `RETRY_BUDGET_EXHAUSTED`, with `selected_backoff_seconds=240` persisted and not resampled in that prior transition. No new 429, wait, retry, LIVE mutation, scheduler mutation, or second semantic leaf occurred in this invocation.

## Acceptance-boundary assessment

- residual richer-mode/Work/protected-primary/manual-user execution dependency: `false`
- finite monthly/trial/paid quota dependency: `false`
- incremental monetary cost: `0`
- repository transport used as lightweight state/evidence transport only: `true`
- same-run wait/poll/backoff/retry: `false`
- optional second leaf started: `false`
- tested scope: own canonical role branch path resolution and exact blob binding only; no claim about broader repository search completeness or global Phase-1 completion.

## Exact continuation

Next effect_chain_id: `clean-rate-limit-envelope-latest-blob-binding-v1`.

Freshly bootstrap/freeze the four required controls, reconstruct the canonical role branch from the then-current LATEST CAS successor, and persist/exact-read the required preflight before semantic reads. Reconstruct the rate-limit envelope input from `research_workers_clean_g1/long_horizon/phase1/LIVE_RATE_LIMIT_STATE.json` only if its exact blob is still `f79a86302e6c4fcb095aec7b22cc6491bb3da20a`. Then execute exactly one bounded binding test that makes the envelope authorize continuation only when both (a) the expected plan/state generation and (b) the expected current LATEST blob/predecessor identity agree. Use a stale predecessor-LATEST blob as the negative control and require rejection with no LIVE mutation. Persist the exact decision and next continuation. Do not combine this with stale-generation mutation testing, another subtree search, any same-run wait/retry/backoff, scheduler mutation, or a second leaf.

Termination: `bounded_slice_complete_recurring_open`.
