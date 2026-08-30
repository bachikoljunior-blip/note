# Long Horizon clean_g1 — latest pointer / bounded Phase-1 checkpoint

Canonical Phase-1 role branch: `clean-long-horizon-phase1-active`
Authority record carried from the exact predecessor: `research_workers_clean_g1/long_horizon/phase1/BRANCH_AUTHORITY.json`
Predecessor LATEST blob consumed by CAS: `87bc40d90ce4e52787d03d75ae1544adb41dbc9b`
Preflight checkpoint/readback: `research_workers_clean_g1/long_horizon/phase1/PREFLIGHT_2026-08-30T1020JST_CLEAN_SWITCH_ONCE_CAS_V1.json` / blob `2fee0496862a00ec95b1e6ba11ea5b91b7b5c6c9`

## Frozen authority for this invocation
- transport_mode: `exact_blob_two_pass`
- instruction manifest revision/blob: `2` / `b288c95adab1ef949ed1791275176815a67b7d11`
- lifecycle revision/blob: `1` / `8fe5d79365dcd943984d69f4767b2ed0c03fc3ac`
- root control revision/blob: `26` / `481660fb6008a57cea162da38439cf115c8d7ebe`
- own role control/config revision/blob: `17` / `8` / `d790db45343bec399d00c6e9410432963726d72c`
- phase/root/task: `phase_1_chat_parity` / `o-chat-parity-root-v4-zero-work-dependency-zero-quota` / `phase1-clean-long-horizon-overrun-recovery`
- bootstrap_valid: `true`
- enabled_desired: `true`

## Selected single effect chain
- effect_chain_id: `clean-switch-once-cas-v1`
- stage completed this invocation: `synthetic_A_to_B_forecast_overrun_switch`
- exact predecessor/frontier: predecessor required exactly one role-local synthetic `A -> B` plan switch under current-blob CAS; stale replay rejection was explicitly deferred to the following invocation.
- planned atomic boundary: evaluate the persisted forecast fixture once, select the alternative plan when the threshold fires, commit exactly one `A -> B` transition to this role-local pointer using the predecessor blob as the CAS authority, then exact-read back and return recurring-open.

## Forecast-overrun fixture and switching criterion
- plan before transition: `A`
- alternative plan: `B`
- p90 remaining work forecast: `18s`
- checkpoint reserve: `8s`
- remaining fixture budget: `20s`
- switching rule: `SWITCH iff p90 + reserve > remaining`
- calculation: `18 + 8 = 26 > 20`
- decision: `SWITCH`
- committed transition: `A -> B`
- switch_generation: `1`
- switch_count_this_invocation: `1`
- duplicate switch effects: `0`
- stale replay attempted this invocation: `false`
- stale replay candidate retained for the next invocation: predecessor blob `87bc40d90ce4e52787d03d75ae1544adb41dbc9b`

## Bounded result
The forecast-overrun criterion fired on the exact reserved synthetic fixture and the canonical role-local pointer was switched once from plan A to plan B under current-blob CAS. This is a mechanism-level scheduled-Chat repository-state probe only: it proves the bounded switch commit path for this fixture, not real-task forecast calibration and not stale-writer rejection. No second leaf, retry, wait, poll, richer-mode execution, protected-primary execution, manual-user step, hosted runner, finite-credit compute/storage, or scheduler mutation was used.

Tested scope: one persisted synthetic overrun fixture plus one role-local CAS-guarded `A -> B` plan transition on the canonical long_horizon branch.

Residual richer-mode/Work/protected-primary/manual execution dependency: `none introduced`.
Finite monthly/trial/paid quota dependency: `none introduced`; lightweight repository transport only and no hosted compute/storage allowance is an execution dependency.
Incremental monetary cost: `0`.
Conflict check: role-local namespace and canonical role branch only; no protected-primary, other-worker, downstream, O-derived, legacy, shared-ledger, or scheduler state was read or mutated for semantics.

## Lifecycle receipt
- termination: `bounded_slice_complete_recurring_open`
- global_completion: `false`
- phase1_completion_claimed: `false`
- enabled_desired: `true`
- scheduler_mutation_by_worker: `false`
- continuation_nonempty: `true`
- hard_runtime_boundary_reached: `false`
- next_invocation_resumes_exact_continuation: `true`

## Exact continuation
On the next invocation, bootstrap/freeze the current instruction manifest, RUN_LIFECYCLE, DESIRED_STATE and long_horizon role config exactly as required, then reconstruct this canonical branch and `clean-switch-once-cas-v1` lineage. Perform exactly one stale-continuation defense test against this same `LATEST.md`: issue one update attempt using stale predecessor blob `87bc40d90ce4e52787d03d75ae1544adb41dbc9b` as the CAS authority and a clearly marked stale-replay payload. Expected result is a CAS conflict with no committed mutation. Do not retry the stale write. Exact-read back the then-current `LATEST.md` and persist the bounded result/continuation; leave any duplicate-consumption or rate-limit leaf for a later invocation. If the stale write is unexpectedly accepted, record that as a scoped failure and preserve a nonempty alternative-route child. Never use a second lineage, quarantined evidence, richer-mode/protected/manual execution, finite quota, scheduler mutation, wait/poll/backoff, or optional second leaf.
