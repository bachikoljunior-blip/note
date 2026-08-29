# Long Horizon clean_g1 checkpoint — cross-invocation recovery closure and rate-limit continuation

## Frozen authority

- transport: `exact_blob_two_pass`
- root control path/revision/blob: `automation_control/DESIRED_STATE.json` / `26` / `481660fb6008a57cea162da38439cf115c8d7ebe`
- own role config path/control/config/blob: `automation_control/roles/long_horizon.json` / `16` / `7` / `41984ccfed213f739f005db5a772baef4a8c711f`
- phase/root/task: `phase_1_chat_parity` / `o-chat-parity-root-v4-zero-work-dependency-zero-quota` / `phase1-clean-long-horizon-overrun-recovery`
- canonical own branch: `clean-long-horizon-phase1-active`
- branch authority path/blob/generation: `research_workers_clean_g1/long_horizon/phase1/BRANCH_AUTHORITY.json` / `dd9eb6a591f643e8653c61e5469a0805be54f3fe` / `1`
- `bootstrap_valid=true`

The root and own role config were read twice before semantic work and the exact blobs/revisions matched. The current root overlay supersedes the older role-local root-problem wording: zero residual richer-mode/Work/protected-primary/manual-user execution, zero optional finite monthly/trial/paid quota dependency, and zero incremental monetary cost remain mandatory.

## Rate-limit state — attempt 2 persisted once

Reconstructed `phase1/LIVE_RATE_LIMIT_STATE.json` at blob `a7b16b13f8db830bd6c0a538dce5e929359dffac`, sequence 1 / retry attempt 1, whose persisted `not_before=2026-08-29T22:50:00+09:00` was already eligible at this invocation.

Applied exactly the predeclared control: one synthetic 429 with missing `Retry-After`, retry attempt 2, deterministic capped-exponential backoff `min(60*2^(attempt-1),300)=120` seconds. Persisted sequence 2 with `observation_time=2026-08-30T03:25:39+09:00`, `not_before=2026-08-30T03:27:39+09:00`, and `selected_backoff_seconds=120`. Readback blob is `9744517a8b49c346a78b67ba62cacfc329c3c4bb`.

No second sample was taken in this invocation. The next scheduled invocation must reconstruct this exact sequence-2 state and prove the 120-second choice and `not_before` survive the invocation boundary unchanged before taking any next retry/switch transition.

## Interruption Case A — existing claim reused, no duplicate authorization

Pre-state:
- pointer `phase1/interruption/CLAIM_ONLY_POINTER.json`: blob `df697842199c52ce3f294599e57cf758de53c99d`, `state_sequence=0`, `PRE_WORK`;
- immutable claim `phase1/interruption/CLAIM_ONLY_CLAIM.json`: blob `3bab77faf9254d8a4f29de30d9b03b67be5763e3`, work identity `claim_only_case_effect_v1`;
- result path was absent by HTTP 404.

Recovery:
- created `phase1/interruption/CLAIM_ONLY_RESULT.json` once from the existing claim; readback blob `34734235f77238b5ec5bea0b44647f1266d99b1b`;
- result explicitly records `new_claim_minted=false`, `external_effect_executed=false`, synthetic effect count 1;
- CAS-advanced the pointer from exact old blob `df697842...` to `state_sequence=1`, status `RESULT_COMMITTED`, new pointer blob `26754ff1e6432aab8883bd200bb2e278156eb608`;
- a duplicate `create_file` against the result path was rejected with HTTP 422 because an existing file requires a current SHA.

Within this repository-transport scope, a crash after durable claim consumption did not require a second claim and did not strand deterministic continuation.

## Interruption Case B — receipt repaired from committed evidence, no effect replay

Pre-state:
- committed pointer `phase1/interruption/POINTER_ADVANCED_STATE.json`: blob `47753ebb7c522e82acded5a0f9864522e9c0503d`, `state_sequence=1`, status `RESULT_COMMITTED_RECEIPT_MISSING`, committed synthetic effect count 1;
- receipt path was absent by HTTP 404.

Recovery:
- created `phase1/interruption/POINTER_ADVANCED_RECEIPT.json` once from the already committed pointer evidence; readback blob `cd6929e9ba80c919957886485c87b95fc431e458`;
- receipt binds the committed pointer blob and records `effect_replayed=false`;
- a duplicate `create_file` against the receipt path was rejected with HTTP 422.

Within this repository-text-state test, receipt repair completed missing evidence without replaying the committed synthetic effect.

## Scope and acceptance guard

These positive results are limited to the tested role-local GitHub Contents transport and synthetic text-state effects. They do not establish safety against external force-push/deletion, arbitrary provider side effects, or any richer execution surface. The route uses no protected-primary merge, richer-mode/Work execution, manual user action, hosted runner, Codespaces, artifact/LFS/package service, cloud/model credit, or other optional finite monthly/trial/paid compute quota. Incremental monetary cost is zero. Repository API transport is state/evidence transport only, not compute.

## Nonempty Phase-1 frontier / exact continuation

1. Fresh two-pass root/config bootstrap; fetch exact canonical branch and validate `BRANCH_AUTHORITY.json` before own-state semantics.
2. Reconstruct `phase1/LIVE_RATE_LIMIT_STATE.json` at sequence 2 and first assert, before any mutation, that `selected_backoff_seconds=120`, `backoff_source=deterministic_exponential_capped`, and `not_before=2026-08-30T03:27:39+09:00` are unchanged across the real invocation boundary. Do not resample.
3. If eligible, run the predeclared next control as a monotonic plan-switch test rather than blind retry: set a remaining-budget condition where `forecast_p90_remaining_seconds + retry_reserve_seconds` exceeds remaining budget, advance `plan_generation` from 1 to 2, switch exactly once to `compact_plan`, and do not consume another external-work attempt.
4. Prove stale pre-switch continuation cannot reactivate generation 1 by using current-blob CAS and a stale-write rejection probe; persist the rejected old generation as evidence only, not authority.
5. Then add the retry-budget-exhaustion boundary as a separate trace: at `max_attempts`, require `SWITCH_PLAN` or durable defer/terminal blocker, never blind retry. Keep forecast-overrun and retry-exhaustion causes separately measurable.
6. Checkpoint exact outcomes, preserve a further non-conflicting Phase-1 frontier, and keep `global_completion=false` until the repository-controlled recurring objective is actually closed under the root acceptance constraints.

`global_completion=false`.
