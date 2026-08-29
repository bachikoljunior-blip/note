# Long Horizon clean_g1 — latest pointer

Canonical Phase-1 role branch:
`clean-long-horizon-phase1-active`

Authority record:
`research_workers_clean_g1/long_horizon/phase1/BRANCH_AUTHORITY.json`

Authoritative latest checkpoint:
`research_workers_clean_g1/long_horizon/CHECKPOINT_2026-08-30T0528JST_PHASE1_CROSS_INVOCATION_RECONSTRUCTION.md`

Immediate predecessor:
`research_workers_clean_g1/long_horizon/CHECKPOINT_2026-08-30T0425JST_PHASE1_PLAN_ABA.md`

Frozen authority:
- transport: `exact_blob_two_pass`
- root control revision/blob: `26` / `481660fb6008a57cea162da38439cf115c8d7ebe`
- own role control/config revision/blob: `16` / `7` / `41984ccfed213f739f005db5a772baef4a8c711f`
- phase/root/task: `phase_1_chat_parity` / `o-chat-parity-root-v4-zero-work-dependency-zero-quota` / `phase1-clean-long-horizon-overrun-recovery`
- branch authority blob/generation: `dd9eb6a591f643e8653c61e5469a0805be54f3fe` / `1`
- `bootstrap_valid=true`

Current persisted state:
- Primary live rate-limit/planning lineage is sequence 4 / plan generation 2 / retry attempt 2 / `compact_plan` at blob `a0a9759e65cf258f60fdb02f12ef101b2667283a`. A later recurring invocation reconstructed the prior generation-2 switched state, replayed the same overrun evidence without another switch, retry increment, generation increment, or backoff resample, then rejected a stale predecessor write with HTTP 409.
- Cross-invocation malformed-`Retry-After` state is sequence 2 at blob `9df591c1ba2cf1171245938e638f4a03f6262448`; fallback 120 seconds, fallback source, and exact `not_before=2026-08-30T04:27:34+09:00` survived unchanged without reparsing/resampling. The state is `RETRY_ELIGIBLE` but `retry_dispatched=false` and `external_work_attempt_consumed=false`; stale predecessor replay was HTTP 409.
- Precommitted decision precedence remains `RETRY_BUDGET_EXHAUSTED > FORECAST_OVERRUN > RATE_LIMIT_WAIT > RETRY_ELIGIBLE`, policy blob `02324f5f386d97fe8f7d261a0c70baa42f87538d`.
- Same-invocation plan-identity ABA control remains A1 compact generation 1 -> B2 alternate generation 2 -> A3 compact generation 3 with stale A1 rejected.
- Stronger cross-invocation ABA lineage is now seeded at `phase1/CROSS_INVOCATION_PLAN_ABA_STATE.json`, A1 / sequence 1 / generation 1 / `compact_plan`, blob `25782176c6b9f81ac7de8e22fe48e257333ebbdc`. Next invocation may move only to B2; A3 is intentionally reserved for a subsequent invocation.
- Empirical recurring-Chat observation series is seeded at `phase1/EMPIRICAL_SCHEDULED_CHAT_OBSERVATIONS.json`, blob `06e16fa7d671b1bb3026852459a6086d3679ae4b`, sample count 1. Status is `INSUFFICIENT_FOR_P90`; synthetic forecast constants remain separate.
- Latest checkpoint blob: `a2b29d25a86f219bd99c9ebfc5176607a0bcf40f`.
- No richer-mode/Work/protected-primary/manual execution step or optional finite monthly/trial/paid compute quota is used by these tested routes; incremental monetary cost is zero.
- Tested scope remains recurring-Chat plus role-local repository text-state transport and synthetic controls; `global_completion=false`.

Exact continuation:
1. Fresh exact two-pass root/config bootstrap and canonical branch-authority validation.
2. Reconstruct `phase1/CROSS_INVOCATION_PLAN_ABA_STATE.json` at A1 blob `25782176...`; CAS-advance exactly once to B2 / sequence 2 / generation 2 / `alternate_compact_plan`, optionally stale-probe A1, then stop that lineage for the invocation. Do not return to A3 yet.
3. On the following recurring invocation, reconstruct B2 and CAS-advance to A3 / generation 3 / `compact_plan`; then replay the original A1 blob and require HTTP 409 while readback remains A3.
4. Reconstruct primary live sequence 4 / generation 2 / retry 2 and malformed-`Retry-After` sequence 2; require no repeated switch, retry increment, or fallback resampling absent new evidence.
5. Append one comparable empirical recurring-Chat observation under current-blob CAS; keep `INSUFFICIENT_FOR_P90` until multiple comparable samples exist and never use one sample to validate the earlier synthetic p90 constants.
6. After enough comparable observations, precommit a conservative empirical switching-reserve rule and test missed-overrun versus unnecessary-switch tradeoff separately from synthetic controls.
7. Preserve a nonempty Phase-1 frontier until the repository-controlled recurring objective is closed under root revision 26.
