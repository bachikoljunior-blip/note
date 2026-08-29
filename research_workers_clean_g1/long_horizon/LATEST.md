# Long Horizon clean_g1 — latest pointer

Canonical Phase-1 role branch:
`clean-long-horizon-phase1-active`

Authority record:
`research_workers_clean_g1/long_horizon/phase1/BRANCH_AUTHORITY.json`

Authoritative latest checkpoint:
`research_workers_clean_g1/long_horizon/CHECKPOINT_2026-08-29T2221JST_PHASE1_INTERRUPTION_SEEDS.md`

Immediate predecessors:
- `research_workers_clean_g1/long_horizon/CHECKPOINT_2026-08-29T2221JST_PHASE1_ACTIVE_BRANCH_RATE_SEED.md`
- `research_workers_clean_g1/long_horizon/CHECKPOINT_2026-08-29T2221JST_PHASE1_RECURRING_BOUNDARY_ABA.md`

Frozen authority:
- transport: `exact_blob_two_pass`
- root control revision/blob: `26` / `481660fb6008a57cea162da38439cf115c8d7ebe`
- own role control/config revision/blob: `16` / `7` / `41984ccfed213f739f005db5a772baef4a8c711f`
- phase/root/task: `phase_1_chat_parity` / `o-chat-parity-root-v4-zero-work-dependency-zero-quota` / `phase1-clean-long-horizon-overrun-recovery`
- `bootstrap_valid=true`

Current persisted state:
- True later-invocation reconstruction, set-once resume consumption, duplicate rejection, cross-invocation stale-pointer CAS rejection and live A->B->A ABA rejection are complete within tested repository scope.
- Canonical role-local authority is `clean-long-horizon-phase1-active` with `BRANCH_AUTHORITY.json` generation 1; the observed two-branch ambiguity is resolved by exact branch name without protected main.
- `phase1/LIVE_RATE_LIMIT_STATE.json` is seeded at sequence 1 / retry attempt 1 with persisted `not_before=2026-08-29T22:50:00+09:00`; next eligible invocation must persist a deterministic 120-second missing-Retry-After backoff once.
- Interruption Case A is intentionally left with an immutable work claim present, pointer still PRE_WORK, and result absent.
- Interruption Case B is intentionally left with committed pointer/effect evidence present and receipt absent.
- No richer-mode/Work/protected-primary/manual execution step or finite monthly/trial/paid compute credit is used by these routes; incremental monetary cost is zero.

Exact continuation:
1. Fresh-bootstrap root/config; fetch exact canonical branch and validate `BRANCH_AUTHORITY.json` before `LATEST`.
2. Apply the live rate-limit state only when its persisted not-before permits; otherwise preserve/defer without resampling.
3. Recover Case A by reusing the existing claim, creating the result once, CAS-advancing its pointer, and proving duplicate result creation fails.
4. Recover Case B by creating the missing receipt from committed pointer evidence without effect replay, then prove duplicate receipt creation fails.
5. Checkpoint outcomes and continue the nonempty Phase-1 frontier; `global_completion=false`.
