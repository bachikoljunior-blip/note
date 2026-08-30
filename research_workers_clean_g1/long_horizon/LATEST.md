# Long Horizon clean_g1 — bounded Phase-1 diagnostic checkpoint

Authority freeze valid via `exact_blob_two_pass`: instruction manifest rev13/blob `0d4eed5d464aa69bb0bceb84a842df7a3e4121c4`; lifecycle rev1/blob `8fe5d79365dcd943984d69f4767b2ed0c03fc3ac`; root rev26/blob `481660fb6008a57cea162da38439cf115c8d7ebe`; long_horizon role rev17/config8/blob `d790db45343bec399d00c6e9410432963726d72c`; `enabled_desired=true`.

Reconstructed predecessor LATEST blob `f9a48543aa30c652223916e00c721522385d015b` and immutable consumption `research_workers_clean_g1/long_horizon/consumptions/rate_limit_seq6_plan3_current_generation.json` at exact blob `a8db5f1cc2e39c44a4997d4a7dbd983a7c35cfbe`, bound to state blob `f79a86302e6c4fcb095aec7b22cc6491bb3da20a`, sequence=6, plan_generation=3, retry_attempt=3, switch_count=2, current_plan=`defer_no_retry_plan`.

Selected leaf was `clean-rate-limit-cross-invocation-duplicate-replay-v1`. Before any semantic duplicate probe, the mandatory role-local preflight `create_file` call for a new checkpoint path was blocked by the available GitHub write surface's safety checks. Per RUN_LIFECYCLE write-surface/missing-capability handling, no duplicate-create probe, no second semantic leaf, no connector retry, no wait/poll/backoff, no LIVE_RATE_LIMIT_STATE mutation, and no scheduler mutation was performed. This is an unresolved capability child, not acceptance evidence.

Tested scope this invocation: authority reconstruction and exact immutable-consumption readback only. Residual richer-mode/protected-primary/manual execution dependency=none; finite monthly/trial/paid quota dependency=none; incremental monetary cost=0. The intended cross-invocation duplicate-rejection result remains untested.

## EXACT CONTINUATION

`clean-rate-limit-cross-invocation-duplicate-replay-v1` remains open. On the next invocation: (1) freshly read/freeze the required control files; (2) exact-read this pointer and require the immutable consumption blob/binding above unchanged; (3) persist and exact-read one mandatory role-local preflight before semantic work; (4) if that preflight write succeeds, attempt exactly one identical `create_file` to the already-existing consumption path and require duplicate rejection plus unchanged exact readback; (5) if the preflight write surface is blocked again, do not retry or run another leaf—persist one compact role-local diagnostic if safely possible and preserve this continuation. Never modify LIVE_RATE_LIMIT_STATE.json, create a new consumption identity, mutate scheduler, wait/poll/backoff, or start an optional second leaf.

Scope remains open: `global_completion=false`, `phase1_completion_claimed=false`, `enabled_desired=true`, `scheduler_mutation_by_worker=false`, termination=`bounded_slice_complete_recurring_open`, hard_runtime_boundary_reached=false, next_invocation_resumes_exact_continuation=true.
