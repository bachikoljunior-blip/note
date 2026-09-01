# Long Horizon Phase-1 preflight — rate-limit envelope stale-generation replay v1

- phase_id: `phase_1_chat_parity`
- root_problem_id: `o-chat-parity-root-v4-zero-work-dependency-zero-quota`
- task_id: `phase1-clean-long-horizon-overrun-recovery`
- enabled_desired: `true`
- global_completion: `false`
- phase1_completion_claimed: `false`
- scheduler_mutation_by_worker: `false`
- bootstrap_valid: `true`
- transport_mode: `exact_blob_two_pass`

## Frozen authority tuple

- INSTRUCTION_CONTROL_MANIFEST path: `automation_control/INSTRUCTION_CONTROL_MANIFEST.json`
- manifest control_revision: `46`
- manifest blob: `6a2108e5dd79c36f85a3c57aca8e84713d1ea1d4`
- RUN_LIFECYCLE path: `automation_control/RUN_LIFECYCLE.json`
- RUN_LIFECYCLE control_revision: `1`
- RUN_LIFECYCLE blob: `8fe5d79365dcd943984d69f4767b2ed0c03fc3ac`
- DESIRED_STATE path: `automation_control/DESIRED_STATE.json`
- DESIRED_STATE control_revision: `26`
- DESIRED_STATE blob pass1/pass2: `481660fb6008a57cea162da38439cf115c8d7ebe` / `481660fb6008a57cea162da38439cf115c8d7ebe`
- role config path: `automation_control/roles/long_horizon.json`
- role control_revision/config_revision: `17` / `8`
- role config blob pass1/pass2: `d790db45343bec399d00c6e9410432963726d72c` / `d790db45343bec399d00c6e9410432963726d72c`

## Reconstructed predecessor/frontier

- canonical role branch: `clean-long-horizon-phase1-active`
- predecessor LATEST path: `research_workers_clean_g1/long_horizon/LATEST.md`
- predecessor LATEST blob: `ff830bb5b08d4b61e777607539f6383006f9bc0b`
- selected effect_chain_id: `clean-rate-limit-envelope-stale-generation-replay-v1`
- predecessor continuation: evaluate one synthetic stale continuation carrying predecessor `plan_generation=2` and predecessor blob `5217ac80d20baad6afd158bd5e39c4b39e9200ff` against current LIVE state; require monotonic-generation rejection without mutation or retry resampling.

## Planned atomic boundary

1. Fetch only current `research_workers_clean_g1/long_horizon/phase1/LIVE_RATE_LIMIT_STATE.json` on the canonical role branch.
2. Compare synthetic stale generation `2` to the current durable generation and classify exactly once.
3. Pass only if current generation is newer and result is `REJECT_STALE_GENERATION`; issue no LIVE mutation, plan reactivation, retry/backoff resampling, wait, retry, or optional second leaf.
4. Persist checkpoint, immutable own receipt, and CAS-guarded LATEST successor; exact-read back durable outputs.

## Forecast / switch threshold

- semantic leaf budget: one repository state read and one deterministic comparison.
- persistence reserve: checkpoint + receipt + LATEST successor within the remaining write cap.
- switch/abort threshold: any control/blob mismatch, missing LIVE state, non-monotonic current generation (`<=2`), CAS conflict, or inability to preserve the persistence reserve converts this invocation to a compact recurring-open diagnostic; do not start an alternative semantic leaf in-run.
- same-run waiting/poll/backoff/retry allowed: `false`

Exact continuation if the leaf cannot run: freshly bootstrap/freeze the same four required controls next invocation, reconstruct this exact predecessor/CAS successor, and retry `clean-rate-limit-envelope-stale-generation-replay-v1` from the current LIVE state without mutating the scheduler.
