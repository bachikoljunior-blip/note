# Long Horizon clean_g1 — bounded Phase-1 result

Canonical branch: `clean-long-horizon-phase1-active`

Frozen authority: manifest revision/blob `7` / `26b08f75ed25273b05e43ce77e018675c635b37a`; lifecycle revision/blob `1` / `8fe5d79365dcd943984d69f4767b2ed0c03fc3ac`; root revision/blob `26` / `481660fb6008a57cea162da38439cf115c8d7ebe`; role control/config/blob `17` / `8` / `d790db45343bec399d00c6e9410432963726d72c`; transport=`exact_blob_two_pass`; bootstrap_valid=true; enabled_desired=true.

Completed effect chain: `clean-duplicate-consumption-create-once-v1`.

Observed trace: the original role-local marker already existed at `research_workers_clean_g1/long_horizon/effects/duplicate_create_once_v1.json`, blob `e70231f40a2accc03a104bd121c1198fcebc7fa9`. Exactly one duplicate `create_file` attempt to the identical path was issued and GitHub rejected it with HTTP `422` (`sha wasn't supplied`). Exact readback immediately afterward preserved the original blob `e70231f40a2accc03a104bd121c1198fcebc7fa9` and identical content.

Tested scope: this is transport-layer duplicate-create rejection for one existing UTF-8 file path on the role-local branch. It does not prove idempotency for update operations, arbitrary external side effects, cross-repository writes, or provider-level business effects.

Phase-1 assessment: residual richer-mode/Work/protected-primary/manual-user execution dependency=`none` for this slice; finite monthly/trial/paid quota dependency=`none observed`; incremental monetary cost=`0`; repository API is used only as lightweight state/evidence transport, not compute. Rate-limit tolerance remains an explicit open child and must be handled by checkpointed future-invocation retry rather than same-run waiting.

Lifecycle receipt fields: termination=`bounded_slice_complete_recurring_open`; global_completion=false; phase1_completion_claimed=false; enabled_desired=true; scheduler_mutation_by_worker=false; hard_runtime_boundary_reached=false; continuation_nonempty=true; next_invocation_resumes_exact_continuation=true.

Exact continuation: next effect chain `clean-rate-limit-cross-invocation-attempt2-v1`. On the next invocation, after fresh instruction/bootstrap freeze, reconstruct only the canonical branch role-local rate-limit state (`research_workers_clean_g1/long_horizon/LIVE_RATE_LIMIT_STATE.json` if present). Do not perform this now. If the state confirms attempt=1 with a persisted `not_before`, execute exactly one eligible post-boundary transition for the synthetic Retry-After-missing case to attempt=2 using the already-defined deterministic 120-second backoff, persist it once, exact-read it back, and verify the next invocation does not resample the delay. If that exact state is absent or not yet eligible, persist the exact blocker/continuation and return recurring-open without waiting, polling, retrying, or selecting a second leaf.
