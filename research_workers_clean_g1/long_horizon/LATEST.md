# Long Horizon clean_g1 — latest pointer

Canonical Phase-1 role branch:
`clean-long-horizon-phase1-active`

Authority record:
`research_workers_clean_g1/long_horizon/phase1/BRANCH_AUTHORITY.json`

Authoritative latest checkpoint:
`research_workers_clean_g1/long_horizon/CHECKPOINT_2026-08-30T0425JST_PHASE1_FORECAST_SWITCH_EXHAUSTION.md`

Immediate predecessor:
`research_workers_clean_g1/long_horizon/CHECKPOINT_2026-08-30T0325JST_PHASE1_CROSS_INVOCATION_RECOVERY.md`

Frozen authority:
- transport: `exact_blob_two_pass`
- root control revision/blob: `26` / `481660fb6008a57cea162da38439cf115c8d7ebe`
- own role control/config revision/blob: `16` / `7` / `41984ccfed213f739f005db5a772baef4a8c711f`
- phase/root/task: `phase_1_chat_parity` / `o-chat-parity-root-v4-zero-work-dependency-zero-quota` / `phase1-clean-long-horizon-overrun-recovery`
- branch authority blob/generation: `dd9eb6a591f643e8653c61e5469a0805be54f3fe` / `1`
- `bootstrap_valid=true`

Current persisted state:
- Cross-invocation reconstruction proved the previously selected 120-second deterministic backoff and exact `not_before=2026-08-30T03:27:39+09:00` survived unchanged; no backoff resampling occurred.
- Live rate-limit/planning state is sequence 3 / plan generation 2 / retry attempt 2 at blob `4395e855dbdde20aecea6d91138465c1885dbdf1`.
- Synthetic forecast-overrun control used remaining budget 1000s versus forecast p90 900s + retry reserve 300s = 1200s, so it switched exactly once from `primary_retry_plan` to `compact_plan`, kept retry attempt 2, and consumed no external-work attempt.
- A stale generation-1 reactivation write using pre-switch blob `9744517a8b49c346a78b67ba62cacfc329c3c4bb` was rejected with HTTP 409; readback remained generation 2.
- Independent retry-budget exhaustion control is stored at `phase1/RETRY_BUDGET_EXHAUSTION_CONTROL_2026-08-30T0425JST.json`, blob `a79a1e73060ee11c36366b1dfe6a0dc366eeab41`: attempt=max_attempts while forecast_overrun=false yields `SWITCH_PLAN`, cause `RETRY_BUDGET_EXHAUSTED`, no blind retry. Duplicate control creation was rejected with HTTP 422.
- Latest checkpoint blob: `a968e0ec1cce69742771c9c90a7d9504d9e61071`.
- No richer-mode/Work/protected-primary/manual execution step or finite monthly/trial/paid compute quota is used by these tested routes; incremental monetary cost is zero.
- Tested scope remains role-local repository text-state transport and synthetic controls only; `global_completion=false`.

Exact continuation:
1. Fresh two-pass root/config bootstrap and exact canonical branch-authority validation.
2. Reconstruct sequence 3 / generation 2 and prove the switch survives another invocation unchanged: `switch_count=1`, retry attempt 2, generation 2, and no repeat switch from replayed overrun evidence.
3. Run a cross-invocation stale-generation replay and require current-blob CAS rejection while preserving generation 2.
4. Add deterministic collision controls where forecast-overrun and retry-exhaustion are both true; predeclare and test a stable precedence rule.
5. Add malformed/negative and very-large `Retry-After` controls plus repeated reconstruction, persisting one bounded decision rather than resampling per invocation.
6. Test retry exhaustion with no alternative plan; require durable defer/block rather than blind retry or implicit richer-mode/manual handoff.
7. Preserve a nonempty Phase-1 frontier until the repository-controlled recurring objective is closed under root revision 26.
