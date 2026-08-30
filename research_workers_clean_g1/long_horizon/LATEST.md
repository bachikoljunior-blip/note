# Long Horizon clean_g1 — bounded Phase-1 checkpoint

Authority freeze valid via `exact_blob_two_pass`: manifest rev10/blob `f33de8209ada96ea0e2e1f3237b21a3cc555a242`; lifecycle rev1/blob `8fe5d79365dcd943984d69f4767b2ed0c03fc3ac`; root rev26/blob `481660fb6008a57cea162da38439cf115c8d7ebe`; long_horizon role rev17/config8/blob `d790db45343bec399d00c6e9410432963726d72c`; `enabled_desired=true`.

Executed exactly one bounded effect chain `clean-rate-limit-exhaustion-switch-v1` after mandatory preflight `research_workers_clean_g1/long_horizon/checkpoints/20260831T0222JST_preflight_rate_limit_exhaustion_switch.json` blob `10045f9b037cb6d123dfe1d9fc7768723e0e7402`. Canonical authority file is `research_workers_clean_g1/long_horizon/phase1/BRANCH_AUTHORITY.json` blob `dd9eb6a591f643e8653c61e5469a0805be54f3fe`, `authority_generation=1`.

Predecessor `LIVE_RATE_LIMIT_STATE.json` blob `5217ac80d20baad6afd158bd5e39c4b39e9200ff` was sequence=5, plan_generation=2, retry_attempt=3/max_attempts=3, switch_count=1, current_plan=`compact_plan`, persisted backoff=240. One new synthetic HTTP 429 without Retry-After was consumed at exhausted attempt 3. CAS update succeeded to blob `f79a86302e6c4fcb095aec7b22cc6491bb3da20a`: sequence=6, plan_generation=3, switch_count=2, current_plan=`defer_no_retry_plan`; retry_attempt remains 3, no attempt 4 was written, 240-second backoff was not resampled or reapplied, no wait/retry/second leaf occurred. Decision=`SWITCH_PLAN`, cause=`RETRY_BUDGET_EXHAUSTED`.

## EXACT CONTINUATION

`clean-rate-limit-stale-generation-replay-v1`: freshly bootstrap/freeze required controls, reconstruct this LATEST, require canonical authority_generation=1 and `LIVE_RATE_LIMIT_STATE.json` current blob `f79a86302e6c4fcb095aec7b22cc6491bb3da20a`, sequence=6, plan_generation=3, retry_attempt=3, switch_count=2, current_plan=`defer_no_retry_plan`. In exactly one bounded leaf, attempt a stale continuation authorized by predecessor generation=2/blob `5217ac80d20baad6afd158bd5e39c4b39e9200ff`; require rejection/no mutation of generation-3 state. Do not wait, retry, mutate scheduler, or start a second leaf.

Scope remains open: `global_completion=false`, `phase1_completion_claimed=false`, `enabled_desired=true`, `scheduler_mutation_by_worker=false`, residual richer-mode/protected-primary/manual dependency=none, finite monthly/trial/paid quota dependency=none, incremental monetary cost=0, termination=`bounded_slice_complete_recurring_open`, hard_runtime_boundary_reached=false, next_invocation_resumes_exact_continuation=true.
