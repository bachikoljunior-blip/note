# Long Horizon Phase-1 preflight — semantic stale payload guard

- role: `long_horizon`
- phase_id: `phase_1_chat_parity`
- root_problem_id: `o-chat-parity-root-v4-zero-work-dependency-zero-quota`
- task_id: `phase1-clean-long-horizon-overrun-recovery`
- effect_chain_id: `clean-rate-limit-semantic-stale-payload-guard-v1`
- authority transport: manifest-bound exact blobs (`transport_mode=exact_blob_sha`)
- instruction manifest: `automation_control/INSTRUCTION_CONTROL_MANIFEST.json`, control_revision=19, blob=`c3def7875026c6a9ddd3d1b401670aa379cd6c57`
- lifecycle: `automation_control/RUN_LIFECYCLE.json`, control_revision=1, blob=`8fe5d79365dcd943984d69f4767b2ed0c03fc3ac`
- root: `automation_control/DESIRED_STATE.json`, control_revision=26, blob=`481660fb6008a57cea162da38439cf115c8d7ebe`
- role config: `automation_control/roles/long_horizon.json`, control_revision=17, config_revision=8, blob=`d790db45343bec399d00c6e9410432963726d72c`
- bootstrap_valid: true
- enabled_desired: true

## Reconstructed frontier
Canonical role branch: `clean-long-horizon-phase1-active`.
LATEST blob consumed: `6b4ba3515972e9582e492d65b72bc71e56883c5e`.
Current canonical state evidence blob: `f79a86302e6c4fcb095aec7b22cc6491bb3da20a`, state_sequence=6, plan_generation=3, retry_attempt=3/max_attempts=3, current_plan=`defer_no_retry_plan`.
Stale predecessor payload blob: `5217ac80d20baad6afd158bd5e39c4b39e9200ff`, state_sequence=5, plan_generation=2, current_plan=`compact_plan`.

## Planned atomic boundary
Test only the controller pre-write semantic freshness predicate while assuming the caller possesses current repository CAS authority: `incoming.plan_generation < current.plan_generation => REJECT_STALE_GENERATION`. The test must issue no LIVE state write, must create no retry attempt 4, and must not change generation 3. This deliberately withholds credit from repository CAS so semantic-generation defense is isolated.

## Forecast / switch threshold
One local deterministic comparison plus one final role-local checkpoint/LATEST/receipt chain only. No public-source expansion, no wait/poll/backoff, no connector retry, no second leaf. If the semantic guard cannot be evaluated without mutating LIVE state, record a missing-capability child instead of weakening state.

## Fixed acceptance constraints
Residual richer-mode/Work/protected-primary/manual execution dependency: none allowed. Finite monthly/trial/paid quota dependency: none allowed. Incremental monetary cost: 0. Scheduler mutation by worker: forbidden. `global_completion=false`; `phase1_completion_claimed=false`.

Exact continuation on preflight failure: reconstruct the same current and predecessor blobs and retry only `clean-rate-limit-semantic-stale-payload-guard-v1` in the next invocation without issuing a LIVE write.
