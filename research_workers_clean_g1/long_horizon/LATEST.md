# Long Horizon clean_g1 — latest pointer / bounded Phase-1 checkpoint

Canonical Phase-1 role branch: `clean-long-horizon-phase1-active`
Authority record: `research_workers_clean_g1/long_horizon/phase1/BRANCH_AUTHORITY.json`
Preflight checkpoint/readback: `research_workers_clean_g1/long_horizon/phase1/PREFLIGHT_2026-08-30T1120JST_STALE_CAS_REPLAY_V1.json` / blob `492f324b493148673463807a8094510203b5d956`
Predecessor LATEST blob: `bf614651a84c7731fa1612161c97a3176d78ed59`

## Frozen authority
- transport_mode: `exact_blob_two_pass`
- instruction manifest revision/blob: `2` / `b288c95adab1ef949ed1791275176815a67b7d11`
- lifecycle revision/blob: `1` / `8fe5d79365dcd943984d69f4767b2ed0c03fc3ac`
- root control revision/blob: `26` / `481660fb6008a57cea162da38439cf115c8d7ebe`
- own role control/config revision/blob: `17` / `8` / `d790db45343bec399d00c6e9410432963726d72c`
- phase/root/task: `phase_1_chat_parity` / `o-chat-parity-root-v4-zero-work-dependency-zero-quota` / `phase1-clean-long-horizon-overrun-recovery`
- bootstrap_valid: `true`
- enabled_desired: `true`

## Selected single effect chain
- effect_chain_id: `clean-stale-cas-replay-v1`
- atomic action: exactly one attempted replacement of this `LATEST.md` using stale CAS authority blob `87bc40d90ce4e52787d03d75ae1544adb41dbc9b`; no retry.
- observed result: GitHub Contents API returned HTTP `409` with `LATEST.md does not match 87bc40d90ce4e52787d03d75ae1544adb41dbc9b`.
- exact post-attempt readback blob: `bf614651a84c7731fa1612161c97a3176d78ed59`, identical to the pre-attempt current blob.
- committed stale-replay effects: `0`.

## Bounded result
For this exact canonical role-local lineage, a stale continuation carrying the predecessor CAS blob was rejected and did not overwrite the current checkpoint pointer. This is mechanism-level evidence for one stale-writer defense on GitHub Contents API only; it does not establish general distributed-store safety or duplicate-consumption safety.

Residual richer-mode/Work/protected-primary/manual execution dependency: `none introduced`.
Finite monthly/trial/paid quota dependency: `none introduced`; lightweight repository transport only, with no hosted compute/storage allowance used as execution.
Incremental monetary cost: `0`.
Conflict check: role-local namespace and canonical role branch only; no O/downstream/other-worker/legacy/shared-ledger/protected-primary semantic input or scheduler mutation.

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
Next invocation, after the required manifest/lifecycle/root/role bootstrap and a new preflight checkpoint, execute exactly one duplicate-resume-consumption defense leaf `clean-duplicate-consumption-create-once-v1`. Bind a new role-local immutable claim path to this completed stale-defense lineage and to the then-current `LATEST.md` blob; create it once, issue exactly one duplicate create for the identical path, do not retry on conflict, exact-read the surviving claim, and persist the result plus the following continuation. Keep rate-limit recovery as a later separate leaf. If duplicate create is unexpectedly accepted, record a scoped failure and set the following continuation to a generation-bound/CAS alternative; do not start that alternative in the same invocation. Preserve zero richer-mode/protected/manual dependency, zero finite monthly/trial/paid quota dependency, zero incremental cost, clean isolation, enabled_desired=true, global_completion=false, and phase1_completion_claimed=false.
