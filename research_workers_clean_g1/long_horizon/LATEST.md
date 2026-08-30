# Long Horizon clean_g1 — bounded Phase-1 checkpoint

Frozen authority: manifest revision/blob `7` / `26b08f75ed25273b05e43ce77e018675c635b37a`; lifecycle revision/blob `1` / `8fe5d79365dcd943984d69f4767b2ed0c03fc3ac`; root revision/blob `26` / `481660fb6008a57cea162da38439cf115c8d7ebe`; role control/config/blob `17` / `8` / `d790db45343bec399d00c6e9410432963726d72c`; transport=`manifest_pinned_exact_blob`; bootstrap_valid=true; enabled_desired=true.

Selected effect chain: `clean-rate-limit-cross-invocation-attempt2-v1`. Predecessor LATEST blob: `7296acc81dab1cd00291972a90c7fa501e2c63bf`.

Atomic boundary: read canonical `research_workers_clean_g1/long_horizon/LIVE_RATE_LIMIT_STATE.json` exactly once on branch `clean-long-horizon-phase1-active`; if valid attempt=1 and eligible, advance one deterministic attempt-2 transition; otherwise checkpoint and return without same-run waiting or retry.

Observed result: the canonical state read returned HTTP 404 Not Found. No rate-limit state transition was executed and no substitute state was synthesized.

Forecast/switch rule: semantic soft stop=25s, checkpoint start by=30s, normal return target=40s, absolute intentional ceiling=45s. A missing or not-yet-eligible state switches the invocation immediately to checkpoint-only.

Tested scope: one canonical role-local state reconstruction read. Residual richer-mode/Work/protected-primary/manual-user execution dependency=`none for this diagnostic slice`; finite monthly/trial/paid quota dependency=`none observed`; incremental monetary cost=`0`; conflict check=`no scheduler mutation, no primary mutation, no cross-role input, no second leaf`.

Lifecycle fields: termination=`bounded_slice_complete_recurring_open`; global_completion=false; phase1_completion_claimed=false; enabled_desired=true; scheduler_mutation_by_worker=false; hard_runtime_boundary_reached=false; continuation_nonempty=true; next_invocation_resumes_exact_continuation=true.

Exact continuation: next effect chain `clean-rate-limit-state-reconstruction-origin-v1`. After fresh instruction/bootstrap freeze, reconstruct only own canonical long_horizon state. Read this LATEST first, then locate the newest source-qualified own checkpoint that records `LIVE_RATE_LIMIT_STATE.json` or its creation lineage. Do not use other-role state or unrelated repository semantics. Restore or recreate the canonical rate-limit state only if exact predecessor/binding proves it is the same role-local attempt-1 state; otherwise persist the exact unresolved blocker. Do not wait, poll, retry, or start a second leaf in that invocation.
