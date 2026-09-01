# Long Horizon Phase-1 checkpoint — stale generation binding v1

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

## Frozen controls

- manifest: control_revision `39`, blob `1690e156cccd29044d8afec54ebc151a826506f5`
- lifecycle: control_revision `1`, blob `8fe5d79365dcd943984d69f4767b2ed0c03fc3ac`
- root: control_revision `26`, blob `481660fb6008a57cea162da38439cf115c8d7ebe`
- role: control_revision `17`, config_revision `8`, blob `d790db45343bec399d00c6e9410432963726d72c`

## Preflight / predecessor

- predecessor LATEST blob: `5bee2f64ca752b3149cda729cacb587e7e83afd9`
- preflight path: `research_workers_clean_g1/long_horizon/PREFLIGHT_2026-09-01T2321JST_RATE_LIMIT_ENVELOPE_STALE_GENERATION_BINDING_V1.md`
- preflight exact-read blob: `691934dfd63dee4a705c9688455d63a5eff46b28`
- LIVE path: `research_workers_clean_g1/long_horizon/phase1/LIVE_RATE_LIMIT_STATE.json`
- required/observed LIVE blob: `f79a86302e6c4fcb095aec7b22cc6491bb3da20a`

## Single bounded negative control

The durable current envelope read back as `state_sequence=6`, `plan_generation=3`, `current_plan=defer_no_retry_plan`, with stale-generation rule requiring every continuation carrying generation `<3` to be rejected. The injected continuation coordinate was exactly predecessor `plan_generation=2` bound to predecessor LIVE blob `5217ac80d20baad6afd158bd5e39c4b39e9200ff` while current LATEST authority and current LIVE blob remained fixed.

Result: `REJECT_STALE_GENERATION_BINDING`.

Observed/required invariants:
- stale generation accepted: `false`
- LIVE mutation issued: `false`
- retry/backoff resampled: `false`
- old `compact_plan` reactivated: `false`
- scheduler mutation: `false`
- same-run wait/poll/backoff/retry: `false`
- optional second leaf started: `false`
- provider/external work invoked: `false`

This closes only the tested stale-plan-generation coordinate for the current repository-carried envelope. It does not prove global long-horizon safety or Phase-1 completion.

## Phase-1 acceptance fields

- residual richer-mode/Work/protected-primary/manual-user execution dependency: `false`
- finite monthly/trial/paid quota dependency: `false`
- incremental monetary cost: `0`
- conflict check: role-local branch/path only; no O, downstream, other-worker, shared-ledger, protected-primary, or scheduler mutation consumed.
- termination: `bounded_slice_complete_recurring_open`
- hard_runtime_boundary_reached: `false`

## Exact continuation

Next effect_chain_id: `clean-rate-limit-envelope-stale-sequence-binding-v1`.

Freshly bootstrap/freeze the four required controls, reconstruct the then-current canonical role-branch LATEST, and persist/exact-read a new preflight before semantic reads. Re-read LIVE only if the continuation still names the current LIVE blob and plan_generation. Hold authority branch, current LATEST identity and current plan_generation fixed while substituting stale `state_sequence=5` bound to predecessor LIVE blob `5217ac80d20baad6afd158bd5e39c4b39e9200ff` as the only negative coordinate. Require `REJECT_STALE_SEQUENCE_BINDING` with zero LIVE mutation, zero retry/backoff resampling, zero plan reactivation, zero scheduler mutation, and no second leaf. Persist/read back the exact result and another nonempty continuation.
