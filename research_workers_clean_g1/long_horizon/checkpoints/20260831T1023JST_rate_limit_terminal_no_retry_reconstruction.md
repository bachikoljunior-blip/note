# Long Horizon clean_g1 — terminal no-retry reconstruction checkpoint

role=long_horizon
phase_id=phase_1_chat_parity
effect_chain_id=clean-rate-limit-terminal-no-retry-reconstruction-v1
canonical_branch=clean-long-horizon-phase1-active
termination=bounded_slice_complete_recurring_open
enabled_desired=true
global_completion=false
phase1_completion_claimed=false
scheduler_mutation_by_worker=false

## Frozen instruction authority

Bootstrap was completed in required order and frozen via exact-blob two-pass semantics:
- `automation_control/INSTRUCTION_CONTROL_MANIFEST.json`: control_revision=17, blob `ec5ab64e62f4b52b92f415f8466f2bc6cce3d58a`
- `automation_control/RUN_LIFECYCLE.json`: control_revision=1, blob `8fe5d79365dcd943984d69f4767b2ed0c03fc3ac`
- `automation_control/DESIRED_STATE.json`: control_revision=26, blob `481660fb6008a57cea162da38439cf115c8d7ebe`
- `automation_control/roles/long_horizon.json`: control_revision=17, config_revision=8, blob `d790db45343bec399d00c6e9410432963726d72c`

No required instruction file was missing or authority-unverifiable. `DESIRED_STATE.json` was not mutated.

## Bounded slice and evidence

Predecessor `LATEST.md` exact-read blob: `f5aef09234c6024abf8de18a29c5f5720cdba71d`.

Bound durable rate-limit state exact-read by immutable git blob `f79a86302e6c4fcb095aec7b22cc6491bb3da20a` reconstructed:
- state_sequence=6
- plan_generation=3; previous_plan_generation=2
- retry_attempt=3; max_attempts=3
- current_plan=`defer_no_retry_plan`; alternative_plan=null
- switch_count=2; switch_cause=`RETRY_BUDGET_EXHAUSTED`
- retry_attempt_4_written=false
- budget_remaining_seconds=1000
- forecast_p90_remaining_seconds=900
- retry_reserve_seconds=300
- forecast_required_seconds=1200
- forecast_overrun=true
- selected_backoff_seconds=240 with `historical_not_reapplied_after_retry_exhaustion`
- same-run wait=false; same-run retry=false in the bound transition

The immutable current-generation consumption was exact-read at `research_workers_clean_g1/long_horizon/consumptions/rate_limit_seq6_plan3_current_generation.json`, blob `a8db5f1cc2e39c44a4997d4a7dbd983a7c35cfbe`. It is `consumed=true`, `consumption_budget=1`, and binds state blob `f79a86302e6c4fcb095aec7b22cc6491bb3da20a`, sequence=6, plan_generation=3, retry_attempt=3, current_plan=`defer_no_retry_plan`.

The exact role-local `research_workers_clean_g1/long_horizon/consumptions/` directory was read after reconstruction. It contained exactly one entry: the generation-3 current-consumption file above, with the same blob `a8db5f1cc2e39c44a4997d4a7dbd983a7c35cfbe`. Therefore, within this dedicated consumption namespace and branch at read time, there was no second consumption record and no attempt-4 consumption record. This bounded absence result does not claim absence of unrelated artifacts elsewhere in the repository.

No retry-attempt-4 authority was consumed or created by this run. No rate-limit state mutation, wait, poll, sleep, backoff, retry, alternate semantic write, scheduler mutation, protected-primary write, or second leaf was performed. The only writes in this invocation were role-local preflight/checkpoint/pointer evidence required by the lifecycle contract.

The terminal marker is control behavior only, not semantic completion. Phase 1 remains open.

## Exact continuation

On the next invocation, bootstrap and freeze the four required controls again, exact-read canonical `LATEST.md`, then reconstruct the immutable sequence-6/generation-3 terminal state blob `f79a86302e6c4fcb095aec7b22cc6491bb3da20a`. Execute exactly one bounded leaf `clean-rate-limit-stale-generation-replay-defense-v1`: use predecessor generation=2 / blob `5217ac80d20baad6afd158bd5e39c4b39e9200ff` as the stale continuation authority and verify that it cannot reactivate `compact_plan`, regain retry authority, create attempt 4, or mutate the generation-3 state. Use current-content CAS authority and exact readback; do not combine another leaf, wait/poll/backoff, retry external work, mutate scheduler, use richer mode/protected primary/manual execution, or consume finite paid/trial/monthly quota. Persist role-local evidence/checkpoint plus a nonempty continuation. Absence/rejection is expected control behavior and is not Phase-1 completion.
