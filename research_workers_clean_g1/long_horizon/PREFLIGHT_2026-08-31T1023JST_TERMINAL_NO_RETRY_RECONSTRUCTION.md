# Long Horizon Phase-1 preflight — terminal no-retry reconstruction

role=long_horizon
phase_id=phase_1_chat_parity
enabled_desired=true
global_completion=false
phase1_completion_claimed=false
bootstrap_valid=true
transport_mode=exact_blob_two_pass

Frozen authority tuple:
- manifest automation_control/INSTRUCTION_CONTROL_MANIFEST.json control_revision=17 blob=ec5ab64e62f4b52b92f415f8466f2bc6cce3d58a
- lifecycle automation_control/RUN_LIFECYCLE.json control_revision=1 blob=8fe5d79365dcd943984d69f4767b2ed0c03fc3ac
- root automation_control/DESIRED_STATE.json control_revision=26 blob=481660fb6008a57cea162da38439cf115c8d7ebe
- role automation_control/roles/long_horizon.json control_revision=17 config_revision=8 blob=d790db45343bec399d00c6e9410432963726d72c

Selected effect_chain_id=clean-rate-limit-terminal-no-retry-reconstruction-v1
Canonical branch=clean-long-horizon-phase1-active
Predecessor LATEST blob=f5aef09234c6024abf8de18a29c5f5720cdba71d
Bound state blob=f79a86302e6c4fcb095aec7b22cc6491bb3da20a
Bound consumption path=research_workers_clean_g1/long_horizon/consumptions/rate_limit_seq6_plan3_current_generation.json
Bound consumption blob=a8db5f1cc2e39c44a4997d4a7dbd983a7c35cfbe
Reconstructed state: sequence=6, plan_generation=3, retry_attempt=3, max_attempts=3, current_plan=defer_no_retry_plan, alternative_plan=null, switch_cause=RETRY_BUDGET_EXHAUSTED, retry_attempt_4_written=false.

Planned atomic boundary: one read-only cross-invocation reconstruction test. Verify the terminal generation-3 state and immutable current-generation consumption, then make one exact role-local expected-absence check for a retry-attempt-4 continuation/consumption under the established seq6 naming contract. Do not create any retry, wait, poll, backoff, mutate LIVE_RATE_LIMIT_STATE, or start a second leaf.

Forecast/switch criterion carried from bound state: budget_remaining_seconds=1000, forecast_p90_remaining_seconds=900, retry_reserve_seconds=300, forecast_required_seconds=1200, forecast_overrun=true. Retry budget is exhausted at attempt 3/3; any fourth retry is unauthorized. If the bounded read-only check cannot be completed without additional capability or a state mutation, checkpoint that blocker and return recurring-open rather than expanding the slice.
