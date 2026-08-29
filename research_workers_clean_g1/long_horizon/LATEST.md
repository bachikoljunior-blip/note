# Long Horizon clean_g1 — latest pointer

Canonical Phase-1 role branch:
`clean-long-horizon-phase1-active`

Authority record:
`research_workers_clean_g1/long_horizon/phase1/BRANCH_AUTHORITY.json`

Authoritative latest checkpoint on the canonical role branch:
`research_workers_clean_g1/long_horizon/CHECKPOINT_2026-08-29T2221JST_PHASE1_ACTIVE_BRANCH_RATE_SEED.md`

Immediate predecessor checkpoint:
`research_workers_clean_g1/long_horizon/CHECKPOINT_2026-08-29T2221JST_PHASE1_RECURRING_BOUNDARY_ABA.md`

Frozen authority:
- transport: `exact_blob_two_pass`
- root control revision/blob: `26` / `481660fb6008a57cea162da38439cf115c8d7ebe`
- own role control/config revision/blob: `16` / `7` / `41984ccfed213f739f005db5a772baef4a8c711f`
- phase/root/task: `phase_1_chat_parity` / `o-chat-parity-root-v4-zero-work-dependency-zero-quota` / `phase1-clean-long-horizon-overrun-recovery`
- `bootstrap_valid=true`

Current result:
- Later-invocation checkpoint reconstruction, set-once resume consumption, duplicate rejection, stale-pointer CAS rejection, and A->B->A monotonic authority controls are live and persisted.
- A fixed canonical role branch now resolves the observed two-branch ambiguity without protected main: exact `clean-long-horizon-phase1-active` plus `BRANCH_AUTHORITY.json` generation 1. The authority file exists on the canonical branch and not on the older timestamped role branch.
- A live cross-invocation rate-limit state is seeded at `phase1/LIVE_RATE_LIMIT_STATE.json`, blob `a7b16b13f8db830bd6c0a538dce5e929359dffac`, with persisted `not_before=2026-08-29T22:50:00+09:00`, attempt 1 and server-derived 1800s delay.
- Next eligible invocation must reconstruct that exact state and, only after eligibility, persist the planned missing-Retry-After attempt-2 transition with deterministic 120s backoff chosen once.
- No richer-mode/Work/protected-primary/manual execution step or finite monthly/trial/paid compute credit is used; incremental monetary cost is zero. Lightweight repository state transport remains rate-limit-aware.

Exact continuation:
1. Fresh-bootstrap root/config, then fetch exactly `clean-long-horizon-phase1-active`; validate `BRANCH_AUTHORITY.json` before `LATEST`.
2. Reconstruct `LIVE_RATE_LIMIT_STATE.json`. If at/after persisted `not_before`, CAS-update to sequence 2 / retry attempt 2 with a planned synthetic 429 missing Retry-After and deterministic 120s backoff. If still early, preserve/defer with no state resampling.
3. On a later invocation verify the 120s backoff persists unchanged; then exhaust retry budget into switch/defer with monotonic generation.
4. Test claim-created/pointer-not-advanced and pointer-advanced/receipt-missing interruption recovery.
5. Preserve exact scope and a nonempty frontier; `global_completion=false`.
