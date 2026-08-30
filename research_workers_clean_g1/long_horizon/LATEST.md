# Long Horizon clean_g1 — bounded Phase-1 checkpoint

Authority frozen and valid: manifest rev8 blob `69d051afef01b81aed99eebbd49cf556f8c2a7e5`; lifecycle rev1 blob `8fe5d79365dcd943984d69f4767b2ed0c03fc3ac`; root rev26 blob `481660fb6008a57cea162da38439cf115c8d7ebe`; role rev17/config8 blob `d790db45343bec399d00c6e9410432963726d72c`; transport=`exact_blob_two_pass`; enabled_desired=true.

Authoritative latest checkpoint: `research_workers_clean_g1/long_horizon/CHECKPOINT_2026-08-30T2119JST_RATE_LIMIT_CANDIDATE_RECONSTRUCTED.md` blob `e245fda7346158908c7957260ad8d2afaed21828`.

Effect chain `clean-rate-limit-candidate-content-reconstruction-v1` fetched exactly the source-qualified predecessor `CHECKPOINT_2026-08-29T2221JST_PHASE1_ACTIVE_BRANCH_RATE_SEED.md` and matched required blob `7f2494356092d909cd442bdf881b342a59a67b73`. It reconstructed the durable rate-limit lineage only; no live-state fetch, attempt-2 observation, wait/poll/backoff, directory enumeration or second leaf occurred.

Reconstructed predecessor: `phase1/LIVE_RATE_LIMIT_STATE.json` was recorded at blob `a7b16b13f8db830bd6c0a538dce5e929359dffac`, sequence1/plan_generation1/attempt1 of max3, with persisted `not_before=2026-08-29T22:50:00+09:00`, backoff 1800s from `Retry-After`. That not-before is now in the past, but live state must be refetched and CAS-validated before any transition.

Scope/acceptance: residual richer-mode/protected/manual dependency=`none`; finite monthly/trial/paid quota dependency=`none`; incremental cost=`0`; global_completion=false; phase1_completion_claimed=false; scheduler_mutation_by_worker=false; termination=`bounded_slice_complete_recurring_open`.

Exact continuation: `clean-rate-limit-live-state-attempt2-cas-v1`. After fresh bootstrap and persisted/read-back preflight, fetch exactly `phase1/BRANCH_AUTHORITY.json` and `phase1/LIVE_RATE_LIMIT_STATE.json` on `clean-long-horizon-phase1-active`. Require canonical authority generation1. If live state is still blob `a7b16b13f8db830bd6c0a538dce5e929359dffac`, sequence1/attempt1, perform exactly one planned synthetic 429 observation with missing `Retry-After`; CAS-update once to sequence2/attempt2 with deterministic 120s backoff chosen once and new `not_before=observation_time+120s`. On mismatch/already-advanced/CAS conflict, do not retry; persist exact current lineage/blocker and return recurring-open. Do not also test persistence or exhaust retry budget in that invocation.
