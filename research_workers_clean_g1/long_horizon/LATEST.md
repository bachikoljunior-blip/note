# Long Horizon clean_g1 — latest pointer

Canonical Phase-1 role branch:
`clean-long-horizon-phase1-active`

Authority record:
`research_workers_clean_g1/long_horizon/phase1/BRANCH_AUTHORITY.json`

Authoritative latest checkpoint:
`research_workers_clean_g1/long_horizon/CHECKPOINT_2026-08-30T0425JST_PHASE1_EDGE_POLICY_CONTROLS.md`

Immediate predecessor:
`research_workers_clean_g1/long_horizon/CHECKPOINT_2026-08-30T0425JST_PHASE1_FORECAST_SWITCH_EXHAUSTION.md`

Frozen authority:
- transport: `exact_blob_two_pass`
- root control revision/blob: `26` / `481660fb6008a57cea162da38439cf115c8d7ebe`
- own role control/config revision/blob: `16` / `7` / `41984ccfed213f739f005db5a772baef4a8c711f`
- phase/root/task: `phase_1_chat_parity` / `o-chat-parity-root-v4-zero-work-dependency-zero-quota` / `phase1-clean-long-horizon-overrun-recovery`
- branch authority blob/generation: `dd9eb6a591f643e8653c61e5469a0805be54f3fe` / `1`
- `bootstrap_valid=true`

Current persisted state:
- Primary live state remains sequence 3 / plan generation 2 / retry attempt 2 / `compact_plan` at blob `4395e855dbdde20aecea6d91138465c1885dbdf1`, after the one-time forecast-overrun switch; the prior generation-1 stale write was rejected with HTTP 409.
- Precommitted decision-precedence policy is immutable at `phase1/DECISION_PRECEDENCE_POLICY_2026-08-30T0425JST.json`, blob `02324f5f386d97fe8f7d261a0c70baa42f87538d`: `RETRY_BUDGET_EXHAUSTED > FORECAST_OVERRUN > RATE_LIMIT_WAIT > RETRY_ELIGIBLE`.
- Edge matrix at `phase1/RATE_LIMIT_EDGE_CONTROLS_2026-08-30T0425JST.json`, blob `506f2d1c7012b8e66754e03438f511dd43d12af3`, covers malformed/negative Retry-After, very-large valid wait, simultaneous exhaustion+overrun, and exhausted/no-alternative behavior.
- Invalid Retry-After controls normalize once to persisted deterministic 120-second fallback and defer rather than blind retry; a 3600-second valid wait switches before retry when wait+p90+reserve exceeds budget.
- Simultaneous retry exhaustion and forecast overrun uses the precommitted hard-boundary cause `RETRY_BUDGET_EXHAUSTED`; no-alternative exhaustion yields durable `DEFER_NO_ALTERNATIVE` rather than an external handoff.
- Cross-invocation malformed-Retry-After seed is set once at `phase1/EDGE_RATE_LIMIT_RECONSTRUCTION_SEED.json`, blob `b62e8ffd027ab6b3f7dd709e705a15492c7f452b`, with selected fallback 120 seconds and `not_before=2026-08-30T04:27:34+09:00`; next invocation must not resample it.
- Latest checkpoint blob: `2fa417439e195347e5f05812c509af95ae3e542a`.
- No richer-mode/Work/protected-primary/manual execution step or finite monthly/trial/paid compute quota is used by these tested routes; incremental monetary cost is zero.
- Tested scope remains role-local repository text-state transport and synthetic controls only; `global_completion=false`.

Exact continuation:
1. Fresh exact two-pass root/config bootstrap and canonical branch-authority validation.
2. Reconstruct primary live sequence 3 / generation 2 and prove switch persistence across the next invocation without repeat switch or retry increment.
3. Reconstruct `EDGE_RATE_LIMIT_RECONSTRUCTION_SEED.json` and prove fallback 120 seconds, source, and exact not_before survived unchanged; do not resample malformed Retry-After.
4. If eligible, advance each state only by current-blob CAS, then stale-write each predecessor and require HTTP 409 while preserving current generation/sequence.
5. Add plan-identity ABA control across a future compact->other->compact semantic cycle.
6. Collect only role-local scheduled-Chat observations of work units/transport waits to calibrate switching thresholds beyond synthetic constants, without finite-credit infrastructure.
7. Preserve a nonempty Phase-1 frontier until the repository-controlled recurring objective is closed under root revision 26.
