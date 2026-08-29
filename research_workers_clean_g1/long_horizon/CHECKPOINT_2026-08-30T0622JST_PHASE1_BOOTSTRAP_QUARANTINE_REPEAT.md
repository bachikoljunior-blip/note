# Long Horizon Phase-1 diagnostic checkpoint

bootstrap_valid=false.

Frozen sanitized control tuple after two-pass read:
- root `automation_control/DESIRED_STATE.json`: revision 26, blob `481660fb6008a57cea162da38439cf115c8d7ebe`
- role `automation_control/roles/long_horizon.json`: control revision 16, config revision 7, blob `41984ccfed213f739f005db5a772baef4a8c711f`
- phase/root/task: `phase_1_chat_parity` / `o-chat-parity-root-v4-zero-work-dependency-zero-quota` / `phase1-clean-long-horizon-overrun-recovery`
- branch authority: `clean-long-horizon-phase1-active`, generation 1, blob `dd9eb6a591f643e8653c61e5469a0805be54f3fe`

Before the first sanitized-root read, broad repository discovery exposed a forbidden repository namespace. No substantive mechanism from it was adopted, but strict CLEAN provenance is violated. This invocation therefore records diagnostics only and promotes no Phase-1 evidence.

No richer-mode, protected-primary, manual execution, hosted-runner, finite-credit, or paid-quota route was used or accepted. Incremental monetary cost: 0. `global_completion=false`.

Exact continuation: next invocation must fetch the root and own role config directly, twice, before any discovery, own-state, or public semantic read. If the tuples match, validate `research_workers_clean_g1/long_horizon/phase1/BRANCH_AUTHORITY.json` on the canonical branch, then reproduce the previously quarantined one-time-switch and malformed-`Retry-After` persistence tests from fresh clean state. Start a fresh empirical lineage and a fresh cross-invocation `A1 -> B2 -> A3` ABA lineage; do not promote prior quarantined blobs.
