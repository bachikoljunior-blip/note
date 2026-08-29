# Long Horizon clean_g1 — latest pointer

Canonical Phase-1 role branch:
`clean-long-horizon-phase1-active`

Authority record:
`research_workers_clean_g1/long_horizon/phase1/BRANCH_AUTHORITY.json`

Authoritative latest checkpoint:
`research_workers_clean_g1/long_horizon/CHECKPOINT_2026-08-30T0425JST_PHASE1_PLAN_ABA.md`

Immediate predecessor:
`research_workers_clean_g1/long_horizon/CHECKPOINT_2026-08-30T0425JST_PHASE1_EDGE_POLICY_CONTROLS.md`

Frozen authority:
- transport: `exact_blob_two_pass`
- root control revision/blob: `26` / `481660fb6008a57cea162da38439cf115c8d7ebe`
- own role control/config revision/blob: `16` / `7` / `41984ccfed213f739f005db5a772baef4a8c711f`
- phase/root/task: `phase_1_chat_parity` / `o-chat-parity-root-v4-zero-work-dependency-zero-quota` / `phase1-clean-long-horizon-overrun-recovery`
- branch authority blob/generation: `dd9eb6a591f643e8653c61e5469a0805be54f3fe` / `1`
- `bootstrap_valid=true`

Current persisted state:
- Primary live rate-limit/planning state remains sequence 3 / plan generation 2 / retry attempt 2 / `compact_plan` at blob `4395e855dbdde20aecea6d91138465c1885dbdf1`; one-time forecast-overrun switch and stale generation-1 HTTP 409 are preserved.
- Precommitted decision precedence remains `RETRY_BUDGET_EXHAUSTED > FORECAST_OVERRUN > RATE_LIMIT_WAIT > RETRY_ELIGIBLE`, policy blob `02324f5f386d97fe8f7d261a0c70baa42f87538d`.
- Retry-After edge matrix blob `506f2d1c7012b8e66754e03438f511dd43d12af3` covers malformed/negative fallback, large-wait forecast switch, simultaneous exhaustion+overrun, and exhausted/no-alternative defer.
- Cross-invocation malformed-Retry-After seed remains blob `b62e8ffd027ab6b3f7dd709e705a15492c7f452b`, selected fallback 120 seconds, `not_before=2026-08-30T04:27:34+09:00`, no resampling allowed.
- Plan-identity ABA trace at `phase1/PLAN_ABA_STATE_2026-08-30T0425JST.json` moved A1 compact generation 1 -> B2 alternate generation 2 -> A3 compact generation 3. The old A1 blob was then rejected with HTTP 409; readback remains A3 at blob `dfcc8eac076eb5ed797a3f6b847e7a6426920b06`. Same semantic plan value does not restore old authority.
- Latest checkpoint blob: `fd2906d5bb6e5fd65741c362b62de2aa8545fdae`.
- No richer-mode/Work/protected-primary/manual execution step or finite monthly/trial/paid compute quota is used by these tested routes; incremental monetary cost is zero.
- Tested scope remains role-local repository text-state transport and synthetic controls only; `global_completion=false`.

Exact continuation:
1. Fresh exact two-pass root/config bootstrap and canonical branch-authority validation.
2. Reconstruct primary live sequence 3 / generation 2 and prove the one-time forecast switch survives the next real invocation unchanged, with no repeat switch or retry increment.
3. Reconstruct malformed-Retry-After seed and prove fallback 120 seconds/source/exact not_before survive unchanged without reparsing/resampling.
4. If eligible, CAS-advance each lineage once and stale-write each predecessor; require HTTP 409 while preserving current state.
5. Seed cross-invocation ABA only if needed to distinguish scheduled-boundary reconstruction safety from the completed same-invocation A->B->A CAS control.
6. Calibrate switching thresholds from future role-local scheduled-Chat observations without optional finite-credit infrastructure, keeping synthetic controls distinct from empirical estimates.
7. Preserve a nonempty Phase-1 frontier until the repository-controlled recurring objective is closed under root revision 26.
