# Long Horizon Phase-1 checkpoint — semantic stale payload guard

## Authority / provenance
- role: `long_horizon`
- phase_id: `phase_1_chat_parity`
- root_problem_id: `o-chat-parity-root-v4-zero-work-dependency-zero-quota`
- task_id: `phase1-clean-long-horizon-overrun-recovery`
- effect_chain_id: `clean-rate-limit-semantic-stale-payload-guard-v1`
- instruction manifest: control_revision=19, blob=`c3def7875026c6a9ddd3d1b401670aa379cd6c57`
- RUN_LIFECYCLE: control_revision=1, blob=`8fe5d79365dcd943984d69f4767b2ed0c03fc3ac`
- sanitized root: control_revision=26, blob=`481660fb6008a57cea162da38439cf115c8d7ebe`
- role config: control_revision=17, config_revision=8, blob=`d790db45343bec399d00c6e9410432963726d72c`
- transport_mode: `exact_blob_sha`
- bootstrap_valid: true
- enabled_desired: true
- preflight checkpoint blob: `3e8fcdfc3c64be51d0a9d2e81bd68d1b93ded0dd`

## Reconstructed inputs
Current canonical evidence blob `f79a86302e6c4fcb095aec7b22cc6491bb3da20a`: state_sequence=6, plan_generation=3, retry_attempt=3/max_attempts=3, current_plan=`defer_no_retry_plan`.
Stale predecessor payload blob `5217ac80d20baad6afd158bd5e39c4b39e9200ff`: state_sequence=5, plan_generation=2, retry_attempt=3/max_attempts=3, current_plan=`compact_plan`.

## Single bounded test
Precommitted controller rule: `incoming.plan_generation < current.plan_generation => REJECT_STALE_GENERATION`.
Test condition deliberately assumed the caller already holds the current repository CAS authority, so repository-CAS freshness receives no credit. Evaluating incoming generation 2 against current generation 3 produced:
- decision: `REJECT_STALE_GENERATION`
- LIVE write issued: `false`
- retry attempt after: `3` (no attempt 4)
- plan generation after: `3`
- state sequence after: `6`
- current plan after: `defer_no_retry_plan`

The atomic mechanism-level result is therefore independent of stale-blob CAS rejection: a semantically stale predecessor is rejected before any repository write even when CAS authority is hypothetically current. No wait, poll, backoff, external retry, scheduler mutation, or second leaf occurred.

## Tested scope / limits
This proves only the explicit monotonic `plan_generation` pre-write predicate for the reconstructed generation-2 versus generation-3 pair. It does not prove protection against a malicious or buggy payload that copies `plan_generation=3` while carrying an older `state_sequence`, stale plan body, or mismatched plan fingerprint. It also does not prove concurrent-writer exclusion beyond the already-separate repository CAS mechanism.

Residual richer-mode/Work/protected-primary/manual execution dependency on the accepted mechanism: none; the guard is a deterministic comparison over reconstructed checkpoint fields before a repository write. Finite monthly/trial/paid quota dependency: none in the tested mechanism; lightweight repository text transport only. Incremental monetary cost: 0. No quota-bearing hosted runner, Codespaces, artifact/LFS/package, cloud/model credit, protected-primary merge, or manual user execution is required.

## EXACT CONTINUATION
Next invocation execute exactly one leaf `clean-rate-limit-same-generation-stale-sequence-guard-v1`: freshly bootstrap/freeze required controls; exact-read current role-local LATEST; reconstruct current sequence=6/generation=3 state from blob `f79a86302e6c4fcb095aec7b22cc6491bb3da20a`; construct a test-only stale payload carrying `plan_generation=3` but predecessor `state_sequence=5` and stale `current_plan=compact_plan`; precommit a controller rule that rejects `incoming.state_sequence < current.state_sequence` before any LIVE write while assuming current CAS authority; require no attempt 4, no plan/body regression, and no LIVE write. Record whether a plan-body/fingerprint binding is additionally needed after the sequence guard. Do not combine another leaf, wait/poll/backoff, retry external work, mutate scheduler, use richer mode/protected primary/manual execution, or consume finite paid/trial/monthly quota.

termination=`bounded_slice_complete_recurring_open`; global_completion=false; phase1_completion_claimed=false; enabled_desired=true; scheduler_mutation_by_worker=false; continuation_nonempty=true; hard_runtime_boundary_reached=false; next_invocation_resumes_exact_continuation=true.
