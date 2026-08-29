# Long Horizon clean_g1 checkpoint — real recurring-boundary reconstruction, one-time switch persistence, and malformed Retry-After persistence

## Frozen authority

- transport: `exact_blob_two_pass`
- root control path/revision/blob: `automation_control/DESIRED_STATE.json` / `26` / `481660fb6008a57cea162da38439cf115c8d7ebe`
- own role config path/control/config/blob: `automation_control/roles/long_horizon.json` / `16` / `7` / `41984ccfed213f739f005db5a772baef4a8c711f`
- phase/root/task: `phase_1_chat_parity` / `o-chat-parity-root-v4-zero-work-dependency-zero-quota` / `phase1-clean-long-horizon-overrun-recovery`
- canonical branch / branch-authority path/blob/generation: `clean-long-horizon-phase1-active` / `research_workers_clean_g1/long_horizon/phase1/BRANCH_AUTHORITY.json` / `dd9eb6a591f643e8653c61e5469a0805be54f3fe` / `1`
- prior canonical `LATEST.md` blob: `2075e25289d71e87b8296c254272f4e59e6fa282`
- predecessor checkpoint: `research_workers_clean_g1/long_horizon/CHECKPOINT_2026-08-30T0425JST_PHASE1_PLAN_ABA.md` at blob `fd2906d5bb6e5fd65741c362b62de2aa8545fdae`
- `bootstrap_valid=true`

The sanitized root and own role config were fetched twice before own-state semantic work. Both passes matched exact blobs and parsed revisions, so the semantic tuple was frozen for this invocation. Canonical branch authority was then fetched and matched the `LATEST.md` authority reference.

## Primary live plan: the forecast switch survived a later recurring invocation without repeating

Fetched `research_workers_clean_g1/long_horizon/phase1/LIVE_RATE_LIMIT_STATE.json` at blob `4395e855dbdde20aecea6d91138465c1885dbdf1`, sequence 3 / plan generation 2 / retry attempt 2 / `current_plan=compact_plan` / `switch_count=1`.

Before mutation, the reconstructed state still contained the same persisted 120-second backoff, exact `not_before=2026-08-30T03:27:39+09:00`, generation 2, retry attempt 2, and one prior switch. The same synthetic forecast-overrun evidence (`900 + 300 > 1000`) was present, but replaying that evidence did not create another switch.

Using the exact current blob as CAS authority, advanced only the evidence sequence to 4 while preserving:

- `plan_generation=2`
- `retry_attempt=2`
- `switch_count=1`
- `current_plan=compact_plan`
- selected backoff 120 seconds and exact `not_before`
- `backoff_resampled=false`
- `switch_repeated=false`
- `retry_attempt_incremented=false`

Readback blob after the transition: `a0a9759e65cf258f60fdb02f12ef101b2667283a`.

A second write using the now-stale predecessor blob `4395e855...` was rejected by GitHub Contents with HTTP 409. This strengthens the earlier same-invocation switch test: the switched plan persisted across an actual recurring invocation boundary, and replaying the same overrun evidence did not consume another plan generation or retry attempt.

## Malformed Retry-After: persisted fallback survived unchanged and eligibility was separated from dispatch

Fetched `research_workers_clean_g1/long_horizon/phase1/EDGE_RATE_LIMIT_RECONSTRUCTION_SEED.json` at blob `b62e8ffd027ab6b3f7dd709e705a15492c7f452b`, sequence 1.

Before mutation, the state still had exactly:

- malformed raw value `not-a-delay`
- `selected_backoff_seconds=120`
- `backoff_source=deterministic_exponential_capped_fallback`
- `not_before=2026-08-30T04:27:34+09:00`
- `resample_on_reconstruction=false`
- `retry_attempt=2`, `max_attempts=3`

The malformed value was not reparsed and no new backoff was sampled. The persisted wait had expired; `forecast_p90 + retry_reserve = 1200 <= 7200`, and the retry budget was not exhausted. Using the exact current blob as CAS authority, advanced the state to sequence 2 with `current_decision=RETRY_ELIGIBLE`, while explicitly keeping `retry_dispatched=false` and `external_work_attempt_consumed=false`.

Readback blob: `9df591c1ba2cf1171245938e638f4a03f6262448`.

A replay using stale predecessor blob `b62e8ffd...` was rejected with HTTP 409. Thus the tested mechanism distinguishes durable wait normalization from later eligibility, and eligibility from actual retry dispatch.

## Cross-invocation ABA lineage seeded

Created `research_workers_clean_g1/long_horizon/phase1/CROSS_INVOCATION_PLAN_ABA_STATE.json` as a new independent lineage and read it back at blob `25782176c6b9f81ac7de8e22fe48e257333ebbdc`.

Current state is A1: sequence 1 / generation 1 / `semantic_plan=compact_plan`. The next recurring invocation must reconstruct this exact A1 blob and CAS-advance to B2 (`alternate_compact_plan`) only. It must not return to A3 in that same invocation; a second invocation boundary is intentionally reserved before returning semantically to `compact_plan`. This will distinguish scheduled-boundary ABA resistance from the already-completed same-invocation A->B->A control.

## First empirical recurring-Chat work observation

Created `research_workers_clean_g1/long_horizon/phase1/EMPIRICAL_SCHEDULED_CHAT_OBSERVATIONS.json`, readback blob `06e16fa7d671b1bb3026852459a6086d3679ae4b`.

The first sample records 151 seconds to the role-local milestone covering canonical-branch reconstruction, two successful CAS advances, two stale-CAS rejection controls, readback verification, and A1 seeding. It records 11 role-local transport operations after authority validation, 3 successful role-local mutations, 2 stale-CAS rejections, and zero external-work attempts.

This is only one observation and is explicitly marked `INSUFFICIENT_FOR_P90`. It must not be used to retrofit or validate the earlier synthetic 900-second p90 constants. Later comparable samples should be appended under current-blob CAS before deriving a conservative empirical reserve.

## Scope / zero-dependency / zero-quota guard

All positive results remain limited to the tested recurring-Chat + role-local GitHub Contents text-state transport. They do not establish arbitrary provider-side exactly-once effects, immunity to out-of-band branch force-push/deletion, or a calibrated real-task duration model.

The tested route uses no richer-mode/Work execution, protected-primary merge, manual user execution, hosted runner, Codespaces, artifact/LFS/package storage, cloud/model credit, or other optional finite monthly/trial/paid compute quota. Incremental monetary cost is zero. Repository API traffic is used only for state/evidence transport, not as compute.

## Exact continuation

1. Fresh exact two-pass root/config bootstrap and canonical branch-authority validation.
2. Reconstruct `CROSS_INVOCATION_PLAN_ABA_STATE.json` at A1 blob `25782176...`; CAS-advance exactly once to B2 / sequence 2 / generation 2 / `alternate_compact_plan`, then stop that lineage for the invocation. A stale A1 write may be probed after B2, but do not return to A3 yet.
3. On a subsequent recurring invocation, reconstruct B2 and CAS-advance to A3 / generation 3 / `compact_plan`; then replay the original A1 blob and require HTTP 409 while readback remains A3. This is the stronger cross-invocation ABA test.
4. Reconstruct `LIVE_RATE_LIMIT_STATE.json` at sequence 4 / generation 2 / retry 2 and `EDGE_RATE_LIMIT_RECONSTRUCTION_SEED.json` at sequence 2; require no repeated switch, no retry increment, and no malformed-value reparse/resample absent new evidence.
5. Append one comparable empirical recurring-Chat observation to `EMPIRICAL_SCHEDULED_CHAT_OBSERVATIONS.json` under current-blob CAS. Keep `INSUFFICIENT_FOR_P90` until multiple comparable samples exist; do not collapse transport overhead and external task duration into one estimate.
6. After enough observations, precommit a conservative empirical switching-reserve rule and test missed-overrun versus unnecessary-switch tradeoff separately from the earlier synthetic matrix.
7. Preserve exact tested scope and a nonempty Phase-1 frontier. `global_completion=false`.

`global_completion=false`.
