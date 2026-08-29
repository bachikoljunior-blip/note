# Long Horizon clean_g1 diagnostic checkpoint — bootstrap quarantine

## Frozen control intended for this invocation

- root control path/revision/blob: `automation_control/DESIRED_STATE.json` / `26` / `481660fb6008a57cea162da38439cf115c8d7ebe`
- own role config path/control/config/blob: `automation_control/roles/long_horizon.json` / `16` / `7` / `41984ccfed213f739f005db5a772baef4a8c711f`
- canonical own branch: `clean-long-horizon-phase1-active`
- branch authority blob/generation: `dd9eb6a591f643e8653c61e5469a0805be54f3fe` / `1`
- phase/root/task: `phase_1_chat_parity` / `o-chat-parity-root-v4-zero-work-dependency-zero-quota` / `phase1-clean-long-horizon-overrun-recovery`

## Why this invocation is quarantined

Before the authoritative root/config bootstrap was completed, connector discovery used a repository-wide search while locating the `note` repository and surfaced results from the forbidden `O` repository namespace. No substantive O-derived mechanism, ranking, worker result, or downstream state was intentionally adopted, but the CLEAN contract is stricter than intent: it says `never O`, and the exact-blob two-pass fallback requires the bootstrap passes to precede semantic work without forbidden input.

Therefore this invocation does **not** satisfy the provenance contract. Set:

- `bootstrap_valid=false`
- `quarantine_reason=accidental_forbidden_repository_discovery_before_clean_bootstrap`
- `global_completion=false`

The semantic/mechanism results written earlier in this invocation must not be counted as Phase-1 acceptance evidence until independently reproduced or revalidated in a later invocation that begins cleanly from the known `bachikoljunior-blip/note` control paths.

## Role-local artifacts created or advanced before quarantine detection

The following role-local writes remain durable transport traces but are quarantined as acceptance evidence for this invocation:

- `phase1/LIVE_RATE_LIMIT_STATE.json` advanced to blob `a0a9759e65cf258f60fdb02f12ef101b2667283a`.
- `phase1/EDGE_RATE_LIMIT_RECONSTRUCTION_SEED.json` advanced to blob `9df591c1ba2cf1171245938e638f4a03f6262448`.
- stale predecessor writes against both lineages returned HTTP 409.
- `phase1/CROSS_INVOCATION_PLAN_ABA_STATE.json` A1 seed was created at blob `25782176c6b9f81ac7de8e22fe48e257333ebbdc`.
- `phase1/EMPIRICAL_SCHEDULED_CHAT_OBSERVATIONS.json` sample 1 was created at blob `06e16fa7d671b1bb3026852459a6086d3679ae4b`.
- `CHECKPOINT_2026-08-30T0528JST_PHASE1_CROSS_INVOCATION_RECONSTRUCTION.md` exists at blob `a2b29d25a86f219bd99c9ebfc5176607a0bcf40f` but is superseded by this diagnostic checkpoint and is not acceptance evidence.

No attempt is made to erase or rewrite history. The quarantine boundary is explicit and monotonic.

## Safe exact continuation

1. On the next invocation, use the now-known repository directly: fetch `bachikoljunior-blip/note:automation_control/DESIRED_STATE.json` first, then `automation_control/roles/long_horizon.json`; perform the required second pass before any own-state/public semantic read. Do not run global repository discovery.
2. Require the same root/config tuples or follow the fresh tuples if authority has legitimately advanced. If the two passes mismatch, write only a diagnostic checkpoint and return noncompletion.
3. Validate `phase1/BRANCH_AUTHORITY.json` on `clean-long-horizon-phase1-active`, then read this diagnostic `LATEST.md` and the minimum own-state artifacts.
4. Treat blobs `a0a9759...`, `9df591c...`, `25782176...`, and `06e16fa...` as quarantined transport state, not Phase-1 acceptance evidence. Reproduce the key one-time-switch and malformed-`Retry-After` reconstruction assertions under a clean bootstrap before promoting them.
5. Do not use empirical sample 1 for calibration. Either mark it invalid in the next clean observation file update or start a fresh clean empirical series.
6. Seed a fresh cross-invocation ABA lineage under clean provenance instead of promoting the contaminated A1 seed. Preserve at least two real invocation boundaries across A1 -> B2 -> A3.
7. Preserve zero residual richer-mode/Work/protected-primary/manual execution, zero optional finite monthly/trial/paid quota dependency, zero incremental cost, and a nonempty frontier. `global_completion=false`.

`global_completion=false`.
