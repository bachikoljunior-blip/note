# Long Horizon Phase-1 checkpoint — stale predecessor detected before rate-limit attempt-2 CAS

bootstrap_valid=true
transport_mode=exact_blob_two_pass
phase_id=phase_1_chat_parity
root_problem_id=o-chat-parity-root-v4-zero-work-dependency-zero-quota
task_id=phase1-clean-long-horizon-overrun-recovery
enabled_desired=true
global_completion=false
phase1_completion_claimed=false
scheduler_mutation_by_worker=false
termination=bounded_slice_complete_recurring_open
hard_runtime_boundary_reached=false
next_invocation_resumes_exact_continuation=true

Frozen authority tuple:
- INSTRUCTION_CONTROL_MANIFEST.json control_revision=8 blob=69d051afef01b81aed99eebbd49cf556f8c2a7e5
- RUN_LIFECYCLE.json control_revision=1 blob=8fe5d79365dcd943984d69f4767b2ed0c03fc3ac
- DESIRED_STATE.json control_revision=26 blob=481660fb6008a57cea162da38439cf115c8d7ebe
- roles/long_horizon.json control_revision=17 config_revision=8 blob=d790db45343bec399d00c6e9410432963726d72c

Selected effect_chain_id=clean-rate-limit-live-state-attempt2-cas-v1
Exact predecessor pointer read: research_workers_clean_g1/long_horizon/LATEST.md blob=6353c1f5b82199fa037db55d3f238816b2379a52
Preflight checkpoint initial blob=21a5b83c19113aff17b4aee5dca63ab5a9b4d884

Observed canonical role authority:
- path=research_workers_clean_g1/long_horizon/phase1/BRANCH_AUTHORITY.json
- blob=dd9eb6a591f643e8653c61e5469a0805be54f3fe
- canonical_role_branch=clean-long-horizon-phase1-active
- authority_generation=1

Observed live rate-limit state:
- path=research_workers_clean_g1/long_horizon/phase1/LIVE_RATE_LIMIT_STATE.json
- blob=a0a9759e65cf258f60fdb02f12ef101b2667283a
- state_sequence=4
- plan_generation=2
- retry_attempt=2 of max_attempts=3
- selected_backoff_seconds=120
- not_before=2026-08-30T03:27:39+09:00
- current_plan=compact_plan
- switch_count=1
- current_decision=KEEP_SWITCHED_PLAN

Result: the predecessor continuation required live blob a7b16b13f8db830bd6c0a538dce5e929359dffac, sequence1/attempt1. The authoritative live state is already advanced to blob a0a9759e65cf258f60fdb02f12ef101b2667283a, sequence4/generation2/attempt2. Therefore the planned attempt-2 synthetic 429/CAS transition was correctly NOT executed. No retry, no wait/poll/backoff, no live-state mutation and no second semantic leaf occurred. This is stale-continuation rejection evidence, not completion.

Tested scope: exact canonical branch authority plus one stale predecessor continuation. It shows the role did not replay an already-advanced attempt-2 transition when current durable state disagreed. It does not prove protection against force-push/deletion by an external principal or all stale-state classes.
Residual richer-mode/protected/manual dependency=none
Finite monthly/trial/paid quota dependency=none
Incremental monetary cost=0
conflict_check=stale predecessor detected before mutation; fail-closed path taken
continuation_nonempty=true

Exact continuation: effect_chain_id=clean-rate-limit-attempt3-cas-v1. On the next invocation, re-bootstrap/freeze current controls, reconstruct this checkpoint through LATEST, and preflight first. Fetch exactly the canonical BRANCH_AUTHORITY.json and LIVE_RATE_LIMIT_STATE.json. Require authority_generation=1 and live state blob=a0a9759e65cf258f60fdb02f12ef101b2667283a with state_sequence=4, plan_generation=2, retry_attempt=2, max_attempts=3, switch_count=1, current_plan=compact_plan, selected_backoff_seconds=120. If still matched and the persisted not_before is eligible, record exactly one synthetic 429 with missing Retry-After and CAS-update once to retry_attempt=3 using deterministic backoff_seconds=240 (min(60*2^(3-1),300)), preserving plan_generation=2 and switch_count=1. If mismatch/already advanced/CAS conflict, do not retry; persist exact current lineage/blocker. Do not also test exhaustion or a second leaf in that invocation.
