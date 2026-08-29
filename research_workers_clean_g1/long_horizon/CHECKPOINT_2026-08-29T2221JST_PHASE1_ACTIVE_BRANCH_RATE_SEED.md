# Long Horizon clean_g1 checkpoint — stable role-local authority + live rate-limit seed

This is a same-invocation continuation of `CHECKPOINT_2026-08-29T2221JST_PHASE1_RECURRING_BOUNDARY_ABA.md` under the same frozen authority tuple: root `control_revision=26`, blob `481660fb6008a57cea162da38439cf115c8d7ebe`; own role `control_revision=16`, `config_revision=7`, blob `41984ccfed213f739f005db5a772baef4a8c711f`; transport `exact_blob_two_pass`; `bootstrap_valid=true`. A late recheck still matched both blobs.

## Stable role-local branch authority control

A canonical role-local branch was created entirely through Chat-exposed lightweight repository transport:

`clean-long-horizon-phase1-active`

It was seeded from the prior source-qualified role branch after the recurring-boundary checkpoint had been finalized. Its `LATEST.md` readback matched blob `d18fe953be8a50045a1f428d91c2e6bcb5c4cfcd`, and the copied checkpoint read back at blob `09467f12a8aae99464ad2cdeb3de066e85b705c6`.

`research_workers_clean_g1/long_horizon/phase1/BRANCH_AUTHORITY.json` was then created only on the canonical branch and read back at blob `dd9eb6a591f643e8653c61e5469a0805be54f3fe`. It fixes:

- exact canonical branch name `clean-long-horizon-phase1-active`;
- `authority_generation=1`;
- checkpoint and `LATEST` identities at seed time;
- rule: fetch the exact canonical branch first; do not infer authority from recency or semantic payload equality of similarly named branches;
- failure rule: if canonical branch/authority file is missing or inconsistent, diagnose and defer rather than silently promote another branch;
- within the canonical branch, retain current-blob CAS plus monotonic checkpoint sequence/generation.

A live branch search returned two role-local Phase-1 branches: the older timestamped branch and the new canonical `-active` branch. The authority file existed on the canonical branch and returned HTTP 404 on the older timestamped branch. Thus the exact-name rule resolves this two-candidate case without protected `main`, user arbitration, or other-role state.

Tested scope: this branch-authority rule prevents ambiguity among the two observed role-local branches under the CLEAN role's own write behavior. It does not protect against an out-of-band principal force-pushing, deleting, or maliciously recreating the canonical branch. That stronger repository-adversary model remains out of scope/unresolved.

## Live multi-invocation rate-limit seed

The previously advisory rate-limit trace is now seeded as durable state on the canonical branch:

`research_workers_clean_g1/long_horizon/phase1/LIVE_RATE_LIMIT_STATE.json`

Readback blob: `a7b16b13f8db830bd6c0a538dce5e929359dffac`.

Seed state:

- `state_sequence=1`, `plan_generation=1`;
- `retry_attempt=1`, `max_attempts=3`;
- synthetic observation `429` with `Retry-After=1800s`;
- persisted `not_before=2026-08-29T22:50:00+09:00`;
- `selected_backoff_seconds=1800`, source `retry_after`;
- remaining budget 7200s, p90 900s, reserve 300s, predeclared alternative `compact_plan`;
- current decision `DEFER_RATE_LIMIT` because wait+p90+reserve fits the declared budget.

The exact next-invocation rule is persisted inside the state: reconstruct from the canonical branch; if still before `not_before`, preserve the same state and defer without resampling. If at/after `not_before`, authorize one planned synthetic retry observation. For the next control, record a 429 with missing `Retry-After`, increment durable attempt to 2, choose deterministic backoff `min(60*2^(attempt-1),300)=120s` exactly once, persist it, and on a later reconstruction verify that the 120s value and new `not_before` are not resampled.

This seed converts the next rate-limit step into a true cross-invocation persistence test rather than a same-run trace.

## Zero-dependency / zero-quota / cost assessment

The tested route uses only scheduled-Chat reasoning and lightweight repository text/branch transport. It does not require Work/richer mode, protected-primary merge, manual user execution, hosted runner, Codespaces, artifact/LFS/package storage, cloud/model credits, or any optional monthly/trial/paid compute allowance. Incremental monetary cost is zero. Repository API rate limits remain an explicit transport hazard; the persisted not-before/backoff/defer policy is the mitigation and repository API volume is not used as compute.

No direct merge to `main`, primary O authority mutation, shared ledger access, other-role state/receipt/config access, or downstream control access occurred.

## Exact continuation / nonempty frontier

1. Fresh bootstrap root/config. Then fetch exactly `clean-long-horizon-phase1-active` and require `BRANCH_AUTHORITY.json` to match the canonical branch, role/task and expected authority generation before reading `LATEST`.
2. Reconstruct `LIVE_RATE_LIMIT_STATE.json`. If the persisted `not_before` has passed, apply the planned missing-`Retry-After` observation: CAS-update to sequence 2 / attempt 2 with deterministic 120s backoff chosen once. If it has not passed, write no retry state and preserve/defer.
3. On a subsequent invocation, prove the stored 120s backoff is unchanged; then exhaust the retry budget into `SWITCH_PLAN` with monotonic plan generation and stale-state rejection.
4. Test interruption after resume-claim creation but before pointer advancement, then the converse pointer-advanced/receipt-missing case.
5. Predeclare a scoring rule and begin accumulating own scheduled-Chat duration observations for forecast calibration without any external compute/quota path.
6. Preserve exact scope and `global_completion=false`.
