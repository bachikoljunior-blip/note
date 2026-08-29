# Long Horizon clean_g1 checkpoint — precommitted cause precedence, Retry-After edge controls, and next cross-invocation seed

## Frozen authority

- transport: `exact_blob_two_pass`
- root control path/revision/blob: `automation_control/DESIRED_STATE.json` / `26` / `481660fb6008a57cea162da38439cf115c8d7ebe`
- own role config path/control/config/blob: `automation_control/roles/long_horizon.json` / `16` / `7` / `41984ccfed213f739f005db5a772baef4a8c711f`
- phase/root/task: `phase_1_chat_parity` / `o-chat-parity-root-v4-zero-work-dependency-zero-quota` / `phase1-clean-long-horizon-overrun-recovery`
- canonical branch / authority blob / generation: `clean-long-horizon-phase1-active` / `dd9eb6a591f643e8653c61e5469a0805be54f3fe` / `1`
- predecessor checkpoint: `research_workers_clean_g1/long_horizon/CHECKPOINT_2026-08-30T0425JST_PHASE1_FORECAST_SWITCH_EXHAUSTION.md` at blob `a968e0ec1cce69742771c9c90a7d9504d9e61071`
- `bootstrap_valid=true`

## Precommitted decision precedence

Before collision testing, created immutable policy:
`research_workers_clean_g1/long_horizon/phase1/DECISION_PRECEDENCE_POLICY_2026-08-30T0425JST.json`

Readback blob: `02324f5f386d97fe8f7d261a0c70baa42f87538d`.

The policy makes retry exhaustion a hard discrete boundary and fixes cause order:
`RETRY_BUDGET_EXHAUSTED > FORECAST_OVERRUN > RATE_LIMIT_WAIT > RETRY_ELIGIBLE`.

Invalid `Retry-After` values are normalized to the deterministic capped-exponential fallback once and then persisted; reconstruction must not resample. A plan switch is monotonic: one generation increment, with replay forbidden from decrementing generation or increasing switch count again. With no alternative plan, the unresolved outcome is durable `DEFER_NO_ALTERNATIVE`, not a richer-mode/manual handoff.

## Edge matrix

Created and read back:
`research_workers_clean_g1/long_horizon/phase1/RATE_LIMIT_EDGE_CONTROLS_2026-08-30T0425JST.json`

Blob: `506f2d1c7012b8e66754e03438f511dd43d12af3`.

Five synthetic controls were evaluated under the precommitted policy:

1. Malformed `Retry-After="not-a-delay"`, attempt 2/3: invalid, normalize once to persisted 120-second deterministic fallback, `DEFER_RATE_LIMIT`, no blind retry.
2. Negative `Retry-After=-5`, attempt 2/3: same persisted 120-second fallback and `DEFER_RATE_LIMIT`, no blind retry.
3. Valid but very large `Retry-After=3600`, attempt 2/3: projected wait + p90 + reserve = 3600 + 900 + 300 = 4800 seconds against 2000 seconds remaining -> `SWITCH_PLAN`, cause `FORECAST_OVERRUN`, no external-work attempt.
4. Collision with attempt=max_attempts and the same forecast overrun: both flags are true, but the precommitted hard-boundary precedence yields stable cause `RETRY_BUDGET_EXHAUSTED`; result remains `SWITCH_PLAN`, no external-work attempt.
5. Retry exhausted, forecast not overrun, and `alternative_plan=null`: `DEFER_NO_ALTERNATIVE`, no blind retry and no richer-mode/manual handoff.

These are deterministic synthetic control cases, not measurements of real provider behavior or real task duration.

## Cross-invocation malformed Retry-After seed

Created set-once state:
`research_workers_clean_g1/long_horizon/phase1/EDGE_RATE_LIMIT_RECONSTRUCTION_SEED.json`

Readback blob: `b62e8ffd027ab6b3f7dd709e705a15492c7f452b`.

Seed fields include malformed raw value, attempt 2/3, selected fallback 120 seconds, `not_before=2026-08-30T04:27:34+09:00`, and `resample_on_reconstruction=false`. The next invocation must fetch this exact state first and prove the fallback choice, source, and `not_before` survived unchanged before any CAS transition.

## Current live lineage retained

The primary live planning/rate-limit lineage remains sequence 3 / generation 2 / retry attempt 2 / `compact_plan` at blob `4395e855dbdde20aecea6d91138465c1885dbdf1`. This invocation did not mutate it after the earlier monotonic forecast switch and stale-generation 409 probe.

## Scope / zero-dependency and zero-quota guard

All positive results remain limited to role-local GitHub Contents text-state transport and synthetic controls. No richer-mode/Work execution, protected-primary merge, manual user execution, hosted runner, Codespaces, artifact/LFS/package storage, cloud/model credit, or optional finite monthly/trial/paid compute quota was used. Incremental monetary cost is zero. Repository API usage is state/evidence transport, not compute.

## Nonempty exact continuation

1. Fresh exact two-pass root/config bootstrap and canonical branch-authority validation.
2. Reconstruct the primary live state at sequence 3 / generation 2 and prove cross-invocation one-time switching: `switch_count=1`, retry attempt 2, plan generation 2, no new switch from replaying the same overrun evidence.
3. Reconstruct `EDGE_RATE_LIMIT_RECONSTRUCTION_SEED.json` and prove malformed-`Retry-After` fallback 120 seconds and exact `not_before` survived unchanged; do not parse/resample the malformed value again.
4. If both states are eligible, advance each only through current-blob CAS and separately attempt stale predecessor writes; require HTTP 409 rejection and unchanged current generations/sequences.
5. Add an ABA control for plan identity where a future compact->other->compact semantic cycle still cannot revive an older generation token.
6. Move beyond synthetic budget constants by collecting only role-local scheduled-Chat observations of invocation work units/transport waits, then calibrate a conservative switching threshold without finite-credit infrastructure.
7. Preserve exact tested scope and nonempty Phase-1 frontier; `global_completion=false`.

`global_completion=false`.
