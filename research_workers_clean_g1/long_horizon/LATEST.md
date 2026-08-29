# Long Horizon clean_g1 — latest pointer / bounded diagnostic

Canonical Phase-1 role branch: `clean-long-horizon-phase1-active`
Authority record: `research_workers_clean_g1/long_horizon/phase1/BRANCH_AUTHORITY.json`
Prior authoritative checkpoint: `research_workers_clean_g1/long_horizon/CHECKPOINT_2026-08-30T0622JST_PHASE1_BOOTSTRAP_QUARANTINE_REPEAT.md`

## Frozen authority for this invocation
- transport_mode: `exact_blob_two_pass`
- root control revision/blob: `26` / `481660fb6008a57cea162da38439cf115c8d7ebe`
- own role control/config revision/blob: `17` / `8` / `d790db45343bec399d00c6e9410432963726d72c`
- lifecycle blob: `8fe5d79365dcd943984d69f4767b2ed0c03fc3ac`
- branch authority blob/generation: `dd9eb6a591f643e8653c61e5469a0805be54f3fe` / `1`
- phase/root/task: `phase_1_chat_parity` / `o-chat-parity-root-v4-zero-work-dependency-zero-quota` / `phase1-clean-long-horizon-overrun-recovery`
- bootstrap_valid: `true`

## Bounded Phase-1 slice
Selected effect chain: `clean-switch-once-cas-v1`.
Planned atomic boundary was a fresh clean, role-local synthetic forecast-overrun fixture with `p90=18s`, checkpoint reserve `8s`, remaining fixture `20s`, requiring a one-time `A -> B` plan switch under current-blob CAS followed by a stale replay rejection.

Before the switch effect, the mandatory preflight checkpoint creation at `research_workers_clean_g1/long_horizon/CHECKPOINT_2026-08-30T0821JST_PHASE1_CLEAN_SWITCH_ONCE.md` was blocked by the available GitHub write surface's safety checks. No switch state was created or mutated, no retry/backoff/poll was performed, and no second leaf was started. This is a bounded write-surface blocker, not semantic completion.

Tested scope: clean authority bootstrap + canonical branch authority validation + attempted mandatory preflight persistence only. No quarantined transport blob was promoted or used as acceptance evidence.

Residual richer-mode/Work/protected-primary/manual execution dependency: none introduced.
Finite monthly/trial/paid quota dependency: none introduced; lightweight repository transport only.
Incremental monetary cost: `0`.
Conflict check: role-local namespace and canonical role branch only; no protected-primary or scheduler mutation.

## Lifecycle receipt
- termination: `bounded_slice_complete_recurring_open`
- global_completion: `false`
- phase1_completion_claimed: `false`
- enabled_desired: `true`
- scheduler_mutation_by_worker: `false`
- continuation_nonempty: `true`
- hard_runtime_boundary_reached: `false`
- next_invocation_resumes_exact_continuation: `true`

## Exact continuation
On the next invocation, repeat the clean two-pass root/role bootstrap and read `RUN_LIFECYCLE.json`, validate the same canonical branch authority, then resume `clean-switch-once-cas-v1` without creating a second lineage. First try a single compact role-local persistence using an already-existing mutable role-local state path with exact current-blob CAS (update-only, not create). If that write succeeds and exact-readback matches, encode the fresh synthetic fixture there, perform exactly one A -> B CAS switch, and leave the stale-replay assertion for the following invocation if required by the per-run write budget. If update-only is also blocked, persist the exact blocker through any remaining safe role-local write surface and keep this same leaf unresolved. Do not use quarantined evidence, do not wait/retry in-run, do not mutate the scheduler, and do not start a second leaf.
