# Long Horizon clean_g1 — latest pointer

Canonical Phase-1 role branch:
`clean-long-horizon-phase1-active`

Authority record:
`research_workers_clean_g1/long_horizon/phase1/BRANCH_AUTHORITY.json`

Authoritative latest checkpoint:
`research_workers_clean_g1/long_horizon/CHECKPOINT_2026-08-30T0529JST_PHASE1_BOOTSTRAP_QUARANTINE.md`

Immediate predecessor:
`research_workers_clean_g1/long_horizon/CHECKPOINT_2026-08-30T0528JST_PHASE1_CROSS_INVOCATION_RECONSTRUCTION.md`

Control tuple observed in this invocation:
- root control revision/blob: `26` / `481660fb6008a57cea162da38439cf115c8d7ebe`
- own role control/config revision/blob: `16` / `7` / `41984ccfed213f739f005db5a772baef4a8c711f`
- phase/root/task: `phase_1_chat_parity` / `o-chat-parity-root-v4-zero-work-dependency-zero-quota` / `phase1-clean-long-horizon-overrun-recovery`
- branch authority blob/generation: `dd9eb6a591f643e8653c61e5469a0805be54f3fe` / `1`
- `bootstrap_valid=false` for this invocation because forbidden repository discovery surfaced before the clean two-pass bootstrap.

Quarantine status:
- Before the authoritative control bootstrap, connector discovery surfaced results from the forbidden `O` repository namespace while locating the `note` repository. No substantive O-derived mechanism was intentionally adopted, but the strict CLEAN provenance contract is violated by that discovery order.
- Therefore the mechanism results written earlier in this invocation are durable transport traces only and must not count as Phase-1 acceptance evidence until independently reproduced or revalidated in a later clean invocation.
- Quarantined current blobs include primary live state `a0a9759e65cf258f60fdb02f12ef101b2667283a`, malformed-`Retry-After` state `9df591c1ba2cf1171245938e638f4a03f6262448`, cross-invocation ABA seed `25782176c6b9f81ac7de8e22fe48e257333ebbdc`, empirical sample series `06e16fa7d671b1bb3026852459a6086d3679ae4b`, and predecessor checkpoint `a2b29d25a86f219bd99c9ebfc5176607a0bcf40f`.
- Latest diagnostic checkpoint blob: `1d9837f9939a3d8afbf2820a13896b8f04caf017`.
- `global_completion=false`.

Exact continuation:
1. Next invocation must start directly with `bachikoljunior-blip/note:automation_control/DESIRED_STATE.json`, then `automation_control/roles/long_horizon.json`, and complete the second pass before any own-state/public semantic read. Do not run global repository discovery.
2. If root/config pass tuples differ, write only a diagnostic checkpoint and return noncompletion. Otherwise freeze the exact tuple, then validate `phase1/BRANCH_AUTHORITY.json` on `clean-long-horizon-phase1-active`.
3. Read this diagnostic pointer and minimum own state. Treat blobs `a0a9759...`, `9df591c...`, `25782176...`, and `06e16fa...` as quarantined transport state, not acceptance evidence.
4. Reproduce the one-time-switch persistence and malformed-`Retry-After` persistence assertions under clean provenance before promoting them.
5. Do not use empirical sample 1 for calibration. Start or append a clean empirical observation lineage with an explicit validity flag.
6. Seed a fresh cross-invocation ABA lineage under clean provenance and preserve at least two real invocation boundaries across A1 -> B2 -> A3 before testing stale A1 after semantic return to A.
7. Preserve zero residual richer-mode/Work/protected-primary/manual execution, zero optional finite monthly/trial/paid quota dependency, zero incremental cost, and a nonempty Phase-1 frontier.
