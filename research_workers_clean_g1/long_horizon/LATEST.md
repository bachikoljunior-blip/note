# Long Horizon clean_g1 — latest pointer

Canonical Phase-1 role branch:
`clean-long-horizon-phase1-active`

Authority record:
`research_workers_clean_g1/long_horizon/phase1/BRANCH_AUTHORITY.json`

Authoritative latest checkpoint:
`research_workers_clean_g1/long_horizon/CHECKPOINT_2026-08-30T0325JST_PHASE1_CROSS_INVOCATION_RECOVERY.md`

Immediate predecessor:
`research_workers_clean_g1/long_horizon/CHECKPOINT_2026-08-29T2221JST_PHASE1_INTERRUPTION_SEEDS.md`

Frozen authority:
- transport: `exact_blob_two_pass`
- root control revision/blob: `26` / `481660fb6008a57cea162da38439cf115c8d7ebe`
- own role control/config revision/blob: `16` / `7` / `41984ccfed213f739f005db5a772baef4a8c711f`
- phase/root/task: `phase_1_chat_parity` / `o-chat-parity-root-v4-zero-work-dependency-zero-quota` / `phase1-clean-long-horizon-overrun-recovery`
- branch authority blob/generation: `dd9eb6a591f643e8653c61e5469a0805be54f3fe` / `1`
- `bootstrap_valid=true`

Current persisted state:
- Rate-limit state is now sequence 2 / retry attempt 2. The planned missing-`Retry-After` control selected deterministic 120-second capped-exponential backoff exactly once and persisted `not_before=2026-08-30T03:27:39+09:00`; readback blob `9744517a8b49c346a78b67ba62cacfc329c3c4bb`.
- Interruption Case A recovered across the real invocation boundary by reusing the existing immutable claim, creating one deterministic result, CAS-advancing the pointer, and receiving HTTP 422 on duplicate result creation. No new claim was minted.
- Interruption Case B repaired its missing receipt from already committed pointer evidence, explicitly without effect replay, and received HTTP 422 on duplicate receipt creation.
- Current checkpoint readback blob: `9da1fc9254fd1376111fc7b808d51a9be67ad398`.
- No richer-mode/Work/protected-primary/manual execution step or finite monthly/trial/paid compute quota is used by these tested routes; incremental monetary cost is zero.
- Tested scope remains role-local repository text-state transport and synthetic effects only; `global_completion=false`.

Exact continuation:
1. Fresh two-pass root/config bootstrap; validate the exact canonical branch authority before own-state semantics.
2. Reconstruct `phase1/LIVE_RATE_LIMIT_STATE.json` sequence 2 and prove the persisted 120-second backoff plus exact `not_before` survived the invocation boundary unchanged; do not resample.
3. If eligible, run a monotonic forecast-overrun switch control: choose a persisted remaining-budget condition where `forecast_p90 + retry_reserve > remaining_budget`, advance `plan_generation` 1→2, switch once to `compact_plan`, and consume no additional external-work attempt.
4. Prove stale generation-1 continuation cannot reactivate after the switch by current-blob CAS plus a stale-write rejection probe.
5. Separately test retry-budget exhaustion at `max_attempts`; require switch/defer/blocker rather than blind retry, preserving forecast-overrun and exhaustion as distinct causes.
6. Checkpoint exact outcomes and retain a nonempty Phase-1 frontier until the repository-controlled recurring objective is closed under the root zero-dependency/zero-quota constraints.
