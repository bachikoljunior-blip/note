# Long Horizon clean_g1 — Phase-1 stale-generation replay defense

## Frozen authority
bootstrap_valid=true; main_head=`0ca6133555e67e766f7499415a6d65ae6803e800`; DESIRED_STATE control_revision=26/blob=`481660fb6008a57cea162da38439cf115c8d7ebe`; long_horizon control_revision=17/config_revision=8/blob=`d790db45343bec399d00c6e9410432963726d72c`; RUN_LIFECYCLE control_revision=1. Canonical role branch=`clean-long-horizon-phase1-active`.

## Exactly one bounded leaf
`effect_chain_id=clean-rate-limit-stale-generation-replay-defense-v1`.

Preflight was durably created/read back at `research_workers_clean_g1/long_horizon/PREFLIGHT_2026-08-31T1123JST_STALE_GENERATION_REPLAY_DEFENSE.md`, blob=`d0a107c19cd56e7cdbaaff0021398ddabff8b31b`.

Reconstructed current terminal no-retry state exactly from `research_workers_clean_g1/long_horizon/phase1/LIVE_RATE_LIMIT_STATE.json`, blob=`f79a86302e6c4fcb095aec7b22cc6491bb3da20a`: state_sequence=6, plan_generation=3, retry_attempt=3/max_attempts=3, current_plan=`defer_no_retry_plan`, switch_cause=`RETRY_BUDGET_EXHAUSTED`, no attempt 4. Reconstructed predecessor blob=`5217ac80d20baad6afd158bd5e39c4b39e9200ff`: state_sequence=5, plan_generation=2, current_plan=`compact_plan`.

Executed one stale continuation replay at the repository Contents API boundary: attempted to replace the canonical LIVE_RATE_LIMIT_STATE with generation-2 predecessor content while presenting predecessor blob `5217ac80d20baad6afd158bd5e39c4b39e9200ff` as CAS authority. GitHub rejected the write with HTTP 409: current path did not match the stale blob. No retry was issued.

Exact post-rejection readback returned the same current blob=`f79a86302e6c4fcb095aec7b22cc6491bb3da20a`, state_sequence=6, plan_generation=3, retry_attempt=3/max_attempts=3, current_plan=`defer_no_retry_plan`, switch_count=2, `retry_attempt_4_written=false`. Thus this tested stale-authority replay could not reactivate `compact_plan`, regain retry authority, create attempt 4, or mutate generation-3 state.

Scope: this proves stale-CAS authority rejection on the canonical role-local Contents-API path. It does **not** prove rejection of a semantically stale generation-2 payload if a buggy caller first rereads the current generation-3 blob and then presents that current blob as CAS authority. CAS freshness and semantic-generation freshness are distinct defenses.

Forecast/retry contract remains unchanged: 900s p90 + 300s reserve = 1200s > 1000s remaining; retry budget remains exhausted at 3/3. No wait/poll/backoff, external retry, scheduler mutation, richer-mode/Work, protected-primary write, manual execution, finite quota/credit, or second semantic leaf occurred. Incremental monetary cost=0.

## EXACT CONTINUATION
Next invocation select exactly one new non-conflicting Phase-1 leaf: `clean-rate-limit-semantic-stale-payload-guard-v1`. Freshly bootstrap/freeze required controls; exact-read LATEST and canonical LIVE_RATE_LIMIT_STATE blob `f79a86302e6c4fcb095aec7b22cc6491bb3da20a`; reconstruct predecessor generation=2 blob `5217ac80d20baad6afd158bd5e39c4b39e9200ff`; then test the controller-level pre-write rule `incoming.plan_generation < current.plan_generation => REJECT_STALE_GENERATION` while deliberately assuming the caller possesses the **current** CAS blob, so repository CAS cannot be credited for the rejection. Persist evidence that no LIVE write is issued, no attempt 4 is created, and generation 3 remains unchanged. Do not combine another leaf, wait/poll/backoff, retry external work, mutate scheduler, use richer mode/protected primary/manual execution, or consume finite paid/trial/monthly quota. If there is no already-authorized role-local semantic guard surface, persist that missing-capability child instead of weakening LIVE state.

termination=bounded_slice_complete_recurring_open
global_completion=false
phase1_completion_claimed=false
enabled_desired=true
scheduler_mutation_by_worker=false
continuation_nonempty=true
hard_runtime_boundary_reached=false
next_invocation_resumes_exact_continuation=true
