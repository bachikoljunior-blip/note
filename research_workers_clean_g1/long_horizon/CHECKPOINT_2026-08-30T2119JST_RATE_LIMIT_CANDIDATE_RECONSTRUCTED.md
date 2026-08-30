# Long Horizon clean_g1 checkpoint — rate-limit predecessor reconstructed

Authority frozen and valid for this bounded slice: manifest rev8 blob `69d051afef01b81aed99eebbd49cf556f8c2a7e5`; lifecycle rev1 blob `8fe5d79365dcd943984d69f4767b2ed0c03fc3ac`; root rev26 blob `481660fb6008a57cea162da38439cf115c8d7ebe`; role rev17/config8 blob `d790db45343bec399d00c6e9410432963726d72c`; transport=`exact_blob_two_pass`; enabled_desired=true. Preflight was persisted/read back at `research_workers_clean_g1/long_horizon/PREFLIGHT_2026-08-30T2119JST_RATE_LIMIT_CANDIDATE_RECONSTRUCTION.md` blob `4f206b35fc9a6c8f69f9c092fc3fea6a57462b20`.

Effect chain `clean-rate-limit-candidate-content-reconstruction-v1` performed exactly the authorized bounded action: fetched `research_workers_clean_g1/long_horizon/CHECKPOINT_2026-08-29T2221JST_PHASE1_ACTIVE_BRANCH_RATE_SEED.md` on `clean-long-horizon-phase1-active`, and the returned blob exactly matched the required `7f2494356092d909cd442bdf881b342a59a67b73`. No directory enumeration, no live retry-state fetch, no retry observation, no wait/poll/backoff, and no second semantic leaf occurred.

## Reconstructed rate-limit predecessor

From that exact source-qualified predecessor only:

- canonical role-local branch: `clean-long-horizon-phase1-active`;
- durable state path: `research_workers_clean_g1/long_horizon/phase1/LIVE_RATE_LIMIT_STATE.json`;
- predecessor readback blob recorded by the source: `a7b16b13f8db830bd6c0a538dce5e929359dffac`;
- predecessor state: `state_sequence=1`, `plan_generation=1`, `retry_attempt=1`, `max_attempts=3`;
- predecessor observation: synthetic `429` with `Retry-After=1800s`;
- persisted `not_before=2026-08-29T22:50:00+09:00`, `selected_backoff_seconds=1800`, source=`retry_after`;
- declared remaining budget `7200s`, p90 `900s`, reserve `300s`, alternative=`compact_plan`;
- predecessor decision=`DEFER_RATE_LIMIT` because wait+p90+reserve fit the declared budget.

At this invocation's stated local date/time (`2026-08-30 21:19 +09:00`), that predecessor `not_before` is in the past. This does not itself prove the live state is still sequence 1; the next invocation must fetch the exact live state and use current-blob CAS before any transition.

## Exact next transition

Next effect chain: `clean-rate-limit-live-state-attempt2-cas-v1`.

After fresh instruction bootstrap/freeze and preflight persistence/readback, fetch exactly `research_workers_clean_g1/long_horizon/phase1/BRANCH_AUTHORITY.json` and `research_workers_clean_g1/long_horizon/phase1/LIVE_RATE_LIMIT_STATE.json` on `clean-long-horizon-phase1-active`. Require canonical branch authority generation 1 and require the live rate-limit state to be consistent with the reconstructed lineage. If the live state is still blob `a7b16b13f8db830bd6c0a538dce5e929359dffac`, sequence 1 / attempt 1 and its `not_before` has passed, perform exactly one planned synthetic retry observation: `429` with missing `Retry-After`; CAS-update once to sequence 2 / attempt 2; choose deterministic backoff `min(60*2^(2-1),300)=120s` exactly once and persist a new `not_before = observation_time + 120s`. If authority/state is missing, mismatched, already advanced, or CAS conflicts, do not retry or overwrite; persist the exact observed blocker/current lineage and return recurring-open. Do not in that invocation also prove the 120s persistence or exhaust the retry budget; those remain later leaves.

## Scope / acceptance

- tested scope: exact candidate-content reconstruction and next-transition derivation only;
- residual richer-mode/Work/protected-primary/manual-user dependency: `none`;
- finite monthly/trial/paid quota dependency: `none`;
- incremental monetary cost: `0`;
- repository transport is state/evidence transport only, not compute;
- global_completion=`false`;
- phase1_completion_claimed=`false`;
- enabled_desired=`true`;
- scheduler_mutation_by_worker=`false`;
- hard_runtime_boundary_reached=`false`;
- termination=`bounded_slice_complete_recurring_open`;
- continuation_nonempty=`true`.
