# Long Horizon clean_g1 — bounded Phase-1 diagnostic checkpoint

Authority frozen and valid: manifest rev9 blob `7f27ffe597e635505035b45bcece5f8958d3319f`; lifecycle rev1 blob `8fe5d79365dcd943984d69f4767b2ed0c03fc3ac`; root rev26 blob `481660fb6008a57cea162da38439cf115c8d7ebe`; role rev17/config8 blob `d790db45343bec399d00c6e9410432963726d72c`; transport=`exact_blob_two_pass`; enabled_desired=true.

Reconstructed predecessor LATEST blob `156dc1cc59f06b5f3af6d779047781c5ba5fcd6e` on canonical branch `clean-long-horizon-phase1-active`. Selected effect chain was `clean-rate-limit-attempt3-cas-v1`.

This invocation did not execute the semantic rate-limit transition because the mandatory preflight checkpoint write was rejected by the repository write surface before any semantic mutation. No live rate-limit state, scheduler, protected state, or external execution was changed; no wait/poll/backoff/retry or second leaf was started.

Exact continuation: `clean-rate-limit-attempt3-cas-v1`. Next invocation must freshly bootstrap/freeze controls, reconstruct this LATEST, persist and exact-read back the mandatory preflight first, then fetch only canonical `phase1/BRANCH_AUTHORITY.json` and `phase1/LIVE_RATE_LIMIT_STATE.json`. Require authority_generation=1 and live blob `a0a9759e65cf258f60fdb02f12ef101b2667283a`, sequence4/generation2/retry_attempt2/max3/switch_count1/current_plan=`compact_plan`/backoff120. If still matched, apply exactly one current-blob CAS transition for one synthetic 429 without Retry-After to retry_attempt3/backoff240, preserving generation2/switch_count1; on mismatch or CAS conflict, do not retry and persist the exact blocker. Do not also test exhaustion or another leaf.

Scope: global_completion=false; phase1_completion_claimed=false; enabled_desired=true; scheduler_mutation_by_worker=false; residual richer-mode/protected/manual dependency=none; finite monthly/trial/paid quota dependency=none; incremental monetary cost=0; termination=`bounded_slice_complete_recurring_open`; hard_runtime_boundary_reached=false.
