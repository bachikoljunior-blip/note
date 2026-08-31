# Long Horizon Phase-1 preflight — stale generation replay defense

bootstrap_valid=true
enabled_desired=true
global_completion=false
phase1_completion_claimed=false

Frozen authority tuple:
- main_head=0ca6133555e67e766f7499415a6d65ae6803e800
- DESIRED_STATE control_revision=26 blob=481660fb6008a57cea162da38439cf115c8d7ebe
- long_horizon control_revision=17 config_revision=8 blob=d790db45343bec399d00c6e9410432963726d72c
- RUN_LIFECYCLE control_revision=1
- canonical_role_branch=clean-long-horizon-phase1-active

Selected task=phase1-clean-long-horizon-overrun-recovery
effect_chain_id=clean-rate-limit-stale-generation-replay-defense-v1

Exact predecessor/frontier:
- current LIVE_RATE_LIMIT_STATE path=research_workers_clean_g1/long_horizon/phase1/LIVE_RATE_LIMIT_STATE.json
- current state blob=f79a86302e6c4fcb095aec7b22cc6491bb3da20a, state_sequence=6, plan_generation=3, retry_attempt=3/max_attempts=3, current_plan=defer_no_retry_plan, switch_cause=RETRY_BUDGET_EXHAUSTED
- stale predecessor authority blob=5217ac80d20baad6afd158bd5e39c4b39e9200ff, state_sequence=5, plan_generation=2, current_plan=compact_plan

Planned atomic boundary: issue exactly one repository Contents-API update against LIVE_RATE_LIMIT_STATE using stale predecessor blob 5217ac80d20baad6afd158bd5e39c4b39e9200ff as the CAS sha and predecessor generation-2 content as the attempted replacement. Expected control result is stale-CAS rejection. Then exact-read current LIVE_RATE_LIMIT_STATE and require blob f79a86302e6c4fcb095aec7b22cc6491bb3da20a with generation=3, retry_attempt=3, no attempt 4, and defer_no_retry_plan unchanged. No second semantic leaf.

Forecast/switch threshold preserved: forecast_p90_remaining_seconds=900 + retry_reserve_seconds=300 = 1200 > budget_remaining_seconds=1000; retry budget already exhausted at 3/3; stale generation must not regain retry authority or reactivate compact_plan.

No wait, poll, backoff, external retry, richer-mode/Work, protected-primary write, manual execution, finite quota/credit, or scheduler mutation is authorized in this slice.
