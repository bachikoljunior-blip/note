# Long Horizon clean_g1 — bounded Phase-1 checkpoint

Authority frozen via current instruction-control bootstrap: manifest control_revision=20/blob `bf8cff1c59401834679b89a151178c3729a50723`; RUN_LIFECYCLE control_revision=1/blob `8fe5d79365dcd943984d69f4767b2ed0c03fc3ac`; root control_revision=26/blob `481660fb6008a57cea162da38439cf115c8d7ebe`; role control_revision=17/config_revision=8/blob `d790db45343bec399d00c6e9410432963726d72c`; transport_mode=`exact_blob_two_pass`; `bootstrap_valid=true`; `enabled_desired=true`.

Completed exactly one bounded leaf: `clean-rate-limit-same-generation-stale-sequence-guard-v1`. Checkpoint: `research_workers_clean_g1/long_horizon/checkpoints/20260831T1524JST_same_generation_stale_sequence_guard.md`, blob `63843b13031a15b520cf50745925dd71d8265ad2`. Preflight blob `256ee8ab72dc2b1816cb8ce68708c3af7ee3f83a`.

Reconstructed canonical state blob `f79a86302e6c4fcb095aec7b22cc6491bb3da20a` with sequence=6, generation=3, plan=`defer_no_retry_plan`. A test-only stale continuation copied generation=3 but carried predecessor sequence=5 and plan=`compact_plan`. Generation freshness alone did not reject it; sequence freshness did: `5 < 6 => REJECT_STALE_SEQUENCE` before any LIVE write. No retry attempt 4 or plan regression occurred.

Residual: an incoming payload that copies both sequence=6 and generation=3 while substituting stale predecessor plan/body would pass both counters. Exact semantic body/fingerprint binding remains open.

## EXACT CONTINUATION
Next invocation execute exactly one leaf `clean-rate-limit-same-sequence-same-generation-body-fingerprint-guard-v1`: freshly bootstrap/freeze required controls; exact-read this LATEST and the canonical state; construct a test-only incoming continuation with `plan_generation=3` and `state_sequence=6` but stale `current_plan=compact_plan`/predecessor body; with current CAS authority assumed, require an exact canonical semantic fingerprint or equivalent immutable body binding to reject substitution before any LIVE write while the untouched canonical payload remains admissible. Record the minimum safe binding tuple. Do not combine another leaf, wait/poll/backoff, retry external work, mutate scheduler, use richer mode/protected primary/manual execution, or consume finite paid/trial/monthly quota.

Scope remains open: `termination=bounded_slice_complete_recurring_open`, `global_completion=false`, `phase1_completion_claimed=false`, `enabled_desired=true`, `scheduler_mutation_by_worker=false`, `continuation_nonempty=true`, `hard_runtime_boundary_reached=false`, `next_invocation_resumes_exact_continuation=true`.
