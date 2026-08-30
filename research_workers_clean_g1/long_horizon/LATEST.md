# Long Horizon clean_g1 — bounded Phase-1 checkpoint

Authority freeze valid via `exact_blob_two_pass`: manifest rev12/blob `f2419cd9842dcaaf8fdc06829da23522a091d2b3`; lifecycle rev1/blob `8fe5d79365dcd943984d69f4767b2ed0c03fc3ac`; root rev26/blob `481660fb6008a57cea162da38439cf115c8d7ebe`; long_horizon role rev17/config8/blob `d790db45343bec399d00c6e9410432963726d72c`; `enabled_desired=true`.

Executed exactly one bounded effect chain `clean-rate-limit-stale-generation-replay-v1` after mandatory preflight `research_workers_clean_g1/long_horizon/checkpoints/20260831T0422JST_preflight_stale_generation_replay.json` blob `6fd8dc03ffb604a4b1552f91d80698dc34a3d05c`. Canonical authority remains `clean-long-horizon-phase1-active`, authority_generation=1.

Stale continuation probe used predecessor generation=2/blob `5217ac80d20baad6afd158bd5e39c4b39e9200ff` as the Contents-API CAS precondition against canonical `LIVE_RATE_LIMIT_STATE.json`. The single update attempt was rejected with HTTP 409. Exact readback preserved blob `f79a86302e6c4fcb095aec7b22cc6491bb3da20a`, sequence=6, plan_generation=3, retry_attempt=3, switch_count=2, current_plan=`defer_no_retry_plan`; no stale reactivation, wait, retry, scheduler mutation, or second leaf occurred.

Durable result checkpoint: `research_workers_clean_g1/long_horizon/checkpoints/20260831T0422JST_stale_generation_replay_result.json`.

## EXACT CONTINUATION

`clean-rate-limit-current-generation-duplicate-replay-v1`: freshly bootstrap/freeze required controls, reconstruct canonical authority_generation=1 and `LIVE_RATE_LIMIT_STATE.json` current blob `f79a86302e6c4fcb095aec7b22cc6491bb3da20a`, sequence=6, plan_generation=3. In exactly one bounded leaf, bind a role-local set-once consumption identity to this current continuation/event generation, commit it once, then attempt the identical second consumption and require duplicate rejection with immutable first-consumption readback. Do not modify `LIVE_RATE_LIMIT_STATE.json`, wait, retry connector errors, mutate scheduler, or start another leaf.

Scope remains open: `global_completion=false`, `phase1_completion_claimed=false`, `enabled_desired=true`, `scheduler_mutation_by_worker=false`, residual richer-mode/protected-primary/manual dependency=none, finite monthly/trial/paid quota dependency=none, incremental monetary cost=0, termination=`bounded_slice_complete_recurring_open`, hard_runtime_boundary_reached=false, next_invocation_resumes_exact_continuation=true.
