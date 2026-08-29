# Long Horizon clean_g1 checkpoint — cross-invocation backoff reconstruction, monotonic forecast switch, and retry-exhaustion separation

## Frozen authority

- transport: `exact_blob_two_pass`
- root control path/revision/blob: `automation_control/DESIRED_STATE.json` / `26` / `481660fb6008a57cea162da38439cf115c8d7ebe`
- own role config path/control/config/blob: `automation_control/roles/long_horizon.json` / `16` / `7` / `41984ccfed213f739f005db5a772baef4a8c711f`
- phase/root/task: `phase_1_chat_parity` / `o-chat-parity-root-v4-zero-work-dependency-zero-quota` / `phase1-clean-long-horizon-overrun-recovery`
- canonical own branch: `clean-long-horizon-phase1-active`
- branch authority path/blob/generation: `research_workers_clean_g1/long_horizon/phase1/BRANCH_AUTHORITY.json` / `dd9eb6a591f643e8653c61e5469a0805be54f3fe` / `1`
- `bootstrap_valid=true`

The sanitized root and own role config were fetched twice before semantic work; exact blobs and parsed revisions matched. Root revision 26 supersedes older role-local Phase-1 wording where inconsistent: an accepted route must have zero residual richer-mode/Work/protected-primary/manual-user execution, zero optional finite monthly/trial/paid quota dependency, and zero incremental monetary cost.

## Cross-invocation rate-limit reconstruction — persisted choice survived unchanged

Reconstructed `research_workers_clean_g1/long_horizon/phase1/LIVE_RATE_LIMIT_STATE.json` at pre-mutation blob `9744517a8b49c346a78b67ba62cacfc329c3c4bb`, sequence 2 / plan generation 1 / retry attempt 2. Before any mutation, the persisted fields matched the prior checkpoint exactly:

- `selected_backoff_seconds=120`
- `backoff_source=deterministic_exponential_capped`
- `not_before=2026-08-30T03:27:39+09:00`
- `retry_attempt=2`

No backoff sample was recomputed or replaced. The persisted `not_before` was already eligible in this invocation.

## Forecast-overrun switch — generation 1 -> 2, no retry consumed

Applied the predeclared synthetic forecast-overrun control only after the reconstruction check. The control set:

- remaining budget = 1000 seconds
- forecast p90 remaining = 900 seconds
- retry reserve = 300 seconds
- required forecast+reserve = 1200 seconds

Because `1200 > 1000`, the live state was CAS-updated from exact blob `9744517a...` to sequence 3 / `plan_generation=2`, switched once from `primary_retry_plan` to `compact_plan`, and retained `retry_attempt=2`. `external_work_attempt_consumed_for_switch=false`; the stored 120-second backoff and exact `not_before` were preserved rather than resampled.

Readback live-state blob after the switch: `4395e855dbdde20aecea6d91138465c1885dbdf1`.

This is a deterministic synthetic budget control, not a calibrated estimate of real task duration.

## Stale generation-1 reactivation — rejected by current-blob CAS

Immediately after the successful switch, attempted to update the same live-state path using the now-stale pre-switch blob `9744517a8b49c346a78b67ba62cacfc329c3c4bb` with a generation-1 reactivation payload. GitHub Contents rejected the write with HTTP 409 (`does not match` current content SHA).

A subsequent readback remained sequence 3 / generation 2 / `current_plan=compact_plan` at blob `4395e855dbdde20aecea6d91138465c1885dbdf1`. Thus, within this role-local repository-transport scope, an old generation cannot regain authority merely by replaying a stale continuation after the monotonic switch.

## Retry-budget exhaustion — independent cause control

Created immutable synthetic control:
`research_workers_clean_g1/long_horizon/phase1/RETRY_BUDGET_EXHAUSTION_CONTROL_2026-08-30T0425JST.json`

Readback blob: `a79a1e73060ee11c36366b1dfe6a0dc366eeab41`.

The control deliberately removes forecast overrun while exhausting retry count:

- `retry_attempt=3`, `max_attempts=3` -> exhausted
- remaining budget = 7200 seconds
- forecast p90 + reserve = 900 + 300 = 1200 seconds
- `1200 <= 7200` -> `forecast_overrun=false`

Derived decision is `SWITCH_PLAN`, cause `RETRY_BUDGET_EXHAUSTED`, with `blind_retry_allowed=false` and `external_work_attempt_consumed=false`. A duplicate create against the immutable control path was rejected with HTTP 422. This keeps forecast-overrun and retry-exhaustion causes separately measurable rather than conflating them.

## Scope and acceptance guard

Positive results are limited to the tested role-local GitHub Contents transport and synthetic text-state controls. They do not establish correctness for arbitrary provider side effects, out-of-band branch force-push/deletion, or any richer execution surface. The tested route uses no richer-mode/Work execution, protected-primary merge, manual user execution, hosted runner, Codespaces, artifact/LFS/package storage, cloud/model credit, or other optional finite monthly/trial/paid compute quota. Incremental monetary cost is zero. Repository API use is lightweight state/evidence transport, not compute.

## Nonempty Phase-1 frontier / exact continuation

1. Fresh exact two-pass root/config bootstrap; validate canonical branch authority before own-state semantics.
2. Reconstruct live sequence 3 / generation 2 and prove the switch itself survives the next invocation unchanged: same `switch_count=1`, same `retry_attempt=2`, same plan generation 2, no repeat switch from replayed forecast evidence.
3. Run a cross-invocation stale-generation replay against the persisted generation-2 blob lineage; require CAS rejection and preserve generation 2.
4. Add deterministic collision controls where forecast-overrun and retry-exhaustion are simultaneously true; predeclare and test a stable precedence rule so cause labels cannot oscillate across invocations.
5. Add rate-limit edge controls for malformed/negative `Retry-After`, very large `Retry-After` relative to remaining budget, and repeated reconstruction; persist a single bounded decision rather than sampling per invocation.
6. Test a no-alternative-plan exhaustion trace: require durable `DEFER/BLOCK` rather than blind retry or implicit richer-mode/manual handoff.
7. Preserve exact tested scope and continue selecting non-conflicting Phase-1 leaves until the repository-controlled recurring objective is closed under root revision 26. `global_completion=false`.

`global_completion=false`.
