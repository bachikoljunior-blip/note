# Long Horizon Phase-1 preflight — stale generation binding v1

- phase_id: `phase_1_chat_parity`
- root_problem_id: `o-chat-parity-root-v4-zero-work-dependency-zero-quota`
- task_id: `phase1-clean-long-horizon-overrun-recovery`
- effect_chain_id: `clean-rate-limit-envelope-stale-generation-binding-v1`
- enabled_desired: `true`
- global_completion: `false`
- phase1_completion_claimed: `false`
- scheduler_mutation_by_worker: `false`
- bootstrap_valid: `true`
- transport_mode: `exact_blob_two_pass`

## Frozen authority tuple

- `automation_control/INSTRUCTION_CONTROL_MANIFEST.json`: control_revision `39`, blob `1690e156cccd29044d8afec54ebc151a826506f5`
- `automation_control/RUN_LIFECYCLE.json`: control_revision `1`, blob `8fe5d79365dcd943984d69f4767b2ed0c03fc3ac`
- `automation_control/DESIRED_STATE.json`: control_revision `26`, blob `481660fb6008a57cea162da38439cf115c8d7ebe`
- `automation_control/roles/long_horizon.json`: control_revision `17`, config_revision `8`, blob `d790db45343bec399d00c6e9410432963726d72c`

## Exact predecessor / frontier

- canonical role branch: `clean-long-horizon-phase1-active`
- predecessor LATEST blob: `5bee2f64ca752b3149cda729cacb587e7e83afd9`
- required current LIVE blob: `f79a86302e6c4fcb095aec7b22cc6491bb3da20a`
- negative coordinate: stale `plan_generation=2` with predecessor LIVE blob `5217ac80d20baad6afd158bd5e39c4b39e9200ff`
- expected current LIVE generation from predecessor continuation: `plan_generation=3`, `state_sequence=6`

## Planned atomic boundary

After exact-readback of this preflight, re-read only the named LIVE state. Proceed only if its blob is exactly `f79a86302e6c4fcb095aec7b22cc6491bb3da20a`. Compare the stale generation coordinate against the current durable envelope. The only admissible negative-control result is `REJECT_STALE_GENERATION_BINDING`; issue no LIVE update, do not resample retry/backoff, do not reactivate an old plan, do not mutate scheduler state, and do not start a second leaf. Persist/read back one checkpoint, CAS-advance LATEST from predecessor blob `5bee2f64ca752b3149cda729cacb587e7e83afd9`, and persist/read back an immutable own receipt with a nonempty continuation.

## Forecast / switch threshold

- forecast: one LIVE read, pure comparison, then bounded persistence/readback; zero external/public semantic work.
- switch threshold: any LIVE blob mismatch, authority mismatch, CAS conflict, write failure, or missing state converts this chain to a bounded diagnostic continuation; no same-run retry, wait, poll, backoff, or alternate second leaf.
- residual richer-mode/Work/protected/manual-user dependency permitted: `false`
- finite monthly/trial/paid quota dependency permitted: `false`
- incremental monetary cost required: `0`
