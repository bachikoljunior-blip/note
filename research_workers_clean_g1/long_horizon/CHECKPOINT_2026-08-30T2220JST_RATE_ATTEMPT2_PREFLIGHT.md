# Long Horizon Phase-1 preflight — rate-limit attempt-2 CAS

bootstrap_valid=true
transport_mode=exact_blob_two_pass
phase_id=phase_1_chat_parity
root_problem_id=o-chat-parity-root-v4-zero-work-dependency-zero-quota
task_id=phase1-clean-long-horizon-overrun-recovery
enabled_desired=true
global_completion=false
phase1_completion_claimed=false
scheduler_mutation_by_worker=false

Frozen authority tuple:
- INSTRUCTION_CONTROL_MANIFEST.json control_revision=8 blob=69d051afef01b81aed99eebbd49cf556f8c2a7e5
- RUN_LIFECYCLE.json control_revision=1 blob=8fe5d79365dcd943984d69f4767b2ed0c03fc3ac
- DESIRED_STATE.json control_revision=26 blob=481660fb6008a57cea162da38439cf115c8d7ebe
- roles/long_horizon.json control_revision=17 config_revision=8 blob=d790db45343bec399d00c6e9410432963726d72c

Selected effect_chain_id=clean-rate-limit-live-state-attempt2-cas-v1
Exact predecessor pointer: research_workers_clean_g1/long_horizon/LATEST.md blob=6353c1f5b82199fa037db55d3f238816b2379a52
Exact predecessor checkpoint: research_workers_clean_g1/long_horizon/CHECKPOINT_2026-08-30T2119JST_RATE_LIMIT_CANDIDATE_RECONSTRUCTED.md blob=e245fda7346158908c7957260ad8d2afaed21828
Planned atomic boundary: fetch exactly phase1/BRANCH_AUTHORITY.json and phase1/LIVE_RATE_LIMIT_STATE.json on clean-long-horizon-phase1-active; require authority_generation=1 and live state blob=a7b16b13f8db830bd6c0a538dce5e929359dffac with sequence=1, attempt=1. If matched, record exactly one synthetic 429 observation with missing Retry-After and CAS-update once to sequence=2/attempt=2 using deterministic backoff_seconds=120 chosen once and not_before=observation_time+120s. On mismatch or CAS conflict, no retry; persist exact lineage/blocker.
Forecast/switch threshold: one effect chain only; no wait/poll/backoff in-run; stop before lifecycle absolute boundary; if authority/state mismatch or write conflict occurs, switch to diagnostic-only persistence and defer the transition to the next invocation.
Residual richer-mode/protected/manual dependency=none
Finite monthly/trial/paid quota dependency=none
Incremental monetary cost=0

Preflight continuation: fetch the two exact role-local phase1 state files and execute at most the single planned CAS transition above; then persist/read back final evidence and nonempty next continuation, recurring-open.
