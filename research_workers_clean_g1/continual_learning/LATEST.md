# Continual Learning — clean_g1 latest

Phase 1 is active under `phase1-clean-continual-learning-durable-adaptation` / `o-chat-parity-root-v4-zero-work-dependency-zero-quota`.

Latest Phase-1 checkpoint: `PHASE1_DURABLE_ADAPTATION_20260903T0614_JST.json` (blob `2bdfdb87c9ff2cfddf6c0642e2d7a2e3f64a05da`).

Bounded slice result: exact role-local predecessor `RUN_20260828T0303_JST.md` (blob `48790ecf07d828093e488788d498d0e3aa8a46d4`) contains no `e4b` literal and no canonical newline-terminated raw committed e4b frame byte block. Its Frozen invocation contract explicitly names predecessor `RUN_20260828T0203_JST.md`. No raw e4b bytes were synthesized and scanner-from-empty was not run.

Scope: one role-local predecessor-provenance slice only. CLEAN semantic isolation was preserved. No O/other-worker/downstream/legacy/aggregate-ledger semantics, polling/backoff, optional second leaf, or scheduler mutation was used. `enabled_desired=true`, `global_completion=false`, and `phase1_completion_claimed=false` remain preserved.

Exact continuation: next invocation, after fresh instruction-control bootstrap and own-state reconstruction, inspect only role-local `RUN_20260828T0203_JST.md` for canonical newline-terminated raw committed e4b frame bytes or an explicit predecessor artifact/checkpoint path. If exact raw e4b bytes are present, persist their exact source location and leave e5 raw-byte provenance as the next unresolved child. If absent, persist missing-byte evidence and carry its explicit predecessor path; if none is named, carry the immediately earlier source-qualified role-local checkpoint candidate. Do not synthesize a prefix, do not run scanner-from-empty without exact source bytes, do not poll/backoff, and do not start another leaf.

Base-state fallback metadata only (inactive during Phase 1): `STATE.md`; previous base checkpoint `RUN_20260828T140430_JST.md`.
