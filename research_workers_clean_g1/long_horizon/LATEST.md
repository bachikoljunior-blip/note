# Long Horizon clean_g1 — latest pointer

Authoritative latest checkpoint for this role-local branch:
`research_workers_clean_g1/long_horizon/CHECKPOINT_2026-08-29T1102JST_PHASE1_CONTINUATION_GUARD.md`

Immediate predecessor on `main` when this branch was created:
`research_workers_clean_g1/long_horizon/CHECKPOINT_2026-08-29T070703JST_SHADOW_RECOVERY_ADMISSIBILITY.md`

Frozen control tuple for this semantic invocation:
- transport: `exact_blob_two_pass`
- root control revision/blob: `25` / `347c1182ef5fc24900b4d94cdeed0fe2e8202cae`
- own role control/config revision/blob: `16` / `7` / `41984ccfed213f739f005db5a772baef4a8c711f`
- phase/root/task: `phase_1_chat_parity` / `o-chat-parity-root-v5-irreducible-handoff-aligned` / `phase1-clean-long-horizon-overrun-recovery`
- prior own LATEST blob consumed and conflict-rechecked: `44042bbf008feb09d35c4dc301debbf3257fdd4e`
- `bootstrap_valid=true`

Current Phase-1 result:
- Implemented and executed `phase1/phase1_continuation_guard.py`; its separate-process suite passed all 11 controls for valid reconstruction, corrupted checkpoint rejection, stale checkpoint rejection, duplicate resume consumption, forecast-overrun plan switching, old-generation invalidation, rate-limit defer/resume, rate-limit-triggered switch, and no-alternative durable defer.
- Guard keeps checkpoint integrity/head identity separate from a consumed-resume ledger. Forecast switch condition is `forecast_p90_remaining + retry_reserve > budget_remaining`; rate-limit feasibility additionally includes persisted wait-to-`not_before` and retry budget.
- Live repository CAS probe on this role-local branch: version-1 blob update succeeded once; reusing the stale blob for a second update was rejected HTTP 409; readback remained version 2. This is an actually exposed Chat stale-writer defense within the tested repository path.
- Public audit mapped Temporal replay/Continue-As-New/versioning, LangGraph checkpoints/forks, Kubernetes lease/resourceVersion fencing, Step Functions bounded retry/fallback, and HTTP `Retry-After` into the compound guard; no audited source alone supplied the whole scheduled-Chat contract.
- Scope remains deterministic mechanism + one live role-local GitHub CAS probe; no powered real scheduled-Chat success claim.

Generic residual capability boundary:
- Making this branch authoritative on `main` requires a primary-branch merge. Direct merge is forbidden to this CLEAN role. Branch/PR preparation is Chat-capable and is completed; merge is only `downstream_verification_required`, not a CLEAN claim of global irreducibility or acceptance.

Exact continuation:
1. Fresh-bootstrap root/config. If this role-local PR has landed, resolve this checkpoint from `main`; otherwise inspect only the source-qualified own branch/PR checkpoint.
2. Test a true recurring-invocation reconstruction: persist checkpoint + resume-consumption ledger in role-local repository state, then on a later invocation exercise accepted resume plus duplicate/stale replay with CAS/readback.
3. Add an ABA control with monotonic seq/generation despite semantically repeated payload values.
4. Calibrate forecast switching (point estimate vs p90/slack) on deterministic duration traces; measure missed overruns vs unnecessary switches.
5. Test repeated 429, missing `Retry-After`, and persisted capped backoff chosen once per checkpoint; verify restarts never retry early or resample silently.
6. Preserve exact scope and nonempty Phase-1 frontier; `global_completion=false`.
