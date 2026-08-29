# Long Horizon clean_g1 checkpoint — plan-identity ABA defense

## Frozen authority

- transport: `exact_blob_two_pass`
- root control path/revision/blob: `automation_control/DESIRED_STATE.json` / `26` / `481660fb6008a57cea162da38439cf115c8d7ebe`
- own role config path/control/config/blob: `automation_control/roles/long_horizon.json` / `16` / `7` / `41984ccfed213f739f005db5a772baef4a8c711f`
- phase/root/task: `phase_1_chat_parity` / `o-chat-parity-root-v4-zero-work-dependency-zero-quota` / `phase1-clean-long-horizon-overrun-recovery`
- canonical branch / authority blob / generation: `clean-long-horizon-phase1-active` / `dd9eb6a591f643e8653c61e5469a0805be54f3fe` / `1`
- predecessor checkpoint: `research_workers_clean_g1/long_horizon/CHECKPOINT_2026-08-30T0425JST_PHASE1_EDGE_POLICY_CONTROLS.md` at blob `2fa417439e195347e5f05812c509af95ae3e542a`
- `bootstrap_valid=true`

## ABA trace

Created role-local live trace:
`research_workers_clean_g1/long_horizon/phase1/PLAN_ABA_STATE_2026-08-30T0425JST.json`

The state moved through three CAS-guarded generations without external work:

- A1: sequence 1 / generation 1 / `plan=compact_plan`, blob `e35d0a1d438b47c3072afc0bb4f021746acd7e68`
- B2: sequence 2 / generation 2 / `plan=alternate_compact_plan`, blob `870c38950558b47778f8f995001645b70c8efccd`
- A3: sequence 3 / generation 3 / `plan=compact_plan`, blob `dfcc8eac076eb5ed797a3f6b847e7a6426920b06`

Thus the semantic plan identity returned to the same value A (`compact_plan`), while authority generation advanced monotonically 1 -> 2 -> 3.

After A3 was committed, attempted to reactivate the original A1 continuation using the exact old A1 blob `e35d0a1d438b47c3072afc0bb4f021746acd7e68`. GitHub Contents rejected the stale update with HTTP 409. Readback remained A3 / sequence 3 / generation 3 / blob `dfcc8eac076eb5ed797a3f6b847e7a6426920b06`.

Within the tested role-local repository transport, returning to the same semantic plan value does not revive the old authority token: generation and current-blob CAS, not payload equality, determine continuation authority.

No external-work attempt was consumed in any A/B/A transition.

## Current independent persistence seeds retained

The primary rate-limit/planning lineage remains sequence 3 / generation 2 / retry attempt 2 / `compact_plan` at blob `4395e855dbdde20aecea6d91138465c1885dbdf1`.

The malformed-`Retry-After` cross-invocation seed remains set once at `research_workers_clean_g1/long_horizon/phase1/EDGE_RATE_LIMIT_RECONSTRUCTION_SEED.json`, blob `b62e8ffd027ab6b3f7dd709e705a15492c7f452b`, selected fallback 120 seconds, `not_before=2026-08-30T04:27:34+09:00`, and `resample_on_reconstruction=false`.

## Scope / acceptance guard

The ABA result is specific to role-local GitHub Contents text-state transport. It does not defend against out-of-band force-push/deletion by an external principal or establish arbitrary provider-side exactly-once semantics. No richer-mode/Work execution, protected-primary merge, manual user execution, hosted runner, Codespaces, artifact/LFS/package storage, cloud/model credit, or optional finite monthly/trial/paid compute quota was used. Incremental monetary cost is zero.

## Nonempty exact continuation

1. Fresh exact two-pass root/config bootstrap and canonical branch-authority validation.
2. Reconstruct primary live sequence 3 / generation 2 and prove the one-time forecast switch survives a real invocation boundary unchanged: switch count 1, retry attempt 2, generation 2, no repeated switch from the same overrun evidence.
3. Reconstruct the malformed-`Retry-After` seed and prove selected fallback 120 seconds/source/exact `not_before` survive unchanged without reparsing or resampling.
4. If each state is eligible, CAS-advance once and then replay its predecessor blob; require stale rejection while preserving current state.
5. Seed a cross-invocation ABA lineage only if needed to distinguish same-invocation CAS safety from scheduled-boundary reconstruction safety; do not count the current same-invocation ABA as that stronger result.
6. Calibrate switching thresholds from future role-local scheduled-Chat observations without optional finite-credit infrastructure, keeping synthetic controls distinct from empirical estimates.
7. Preserve exact tested scope and a nonempty Phase-1 frontier. `global_completion=false`.

`global_completion=false`.
