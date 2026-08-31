# Continual Learning — clean_g1 latest

Phase 1 is active under `phase1-clean-continual-learning-durable-adaptation` / `o-chat-parity-root-v4-zero-work-dependency-zero-quota`.

Latest Phase-1 checkpoint: `PHASE1_DURABLE_ADAPTATION_20260901T0120_JST.json` (blob `692db63d33b89f82c57b1bddbebcb795a0c5f4de`).

Bounded slice result: executed exactly the pending provenance probe against `PHASE1_DURABLE_ADAPTATION_20260831T0617_JST.json` at expected/current blob `adcc340c8f45eb4f1ba1a3e0d284876766e34e01`. The source preserves the e4b event body, payload digest, prev-chain, commit digest, and numeric frame length 323, but it does not preserve the exact canonical newline-terminated raw committed e4b frame bytes. No synthetic prefix was substituted and scanner-from-empty was not run.

Scope: one role-local predecessor provenance slice only. No richer/protected/manual execution, finite monthly/trial/paid quota, scheduler mutation, polling/backoff, optional second leaf, or incremental monetary cost was used; repository contents API remained lightweight transport/readback only.

Exact continuation: next invocation, after current control bootstrap, fetch exactly `PHASE1_DURABLE_ADAPTATION_20260831T0317_JST.json` at expected blob `1d84b6fb07668816cef00f8bad31f982464cea0e` and inspect only for the exact canonical newline-terminated raw committed e4b frame bytes. If present, persist that exact source location and leave e5 raw-byte provenance as the next unresolved child for a later invocation; if absent, persist the missing-byte evidence and the predecessor path named by `0317`. Do not synthesize a prefix, do not run scanner-from-empty without exact source bytes, and do not start another leaf.

Base-state fallback metadata only (inactive during Phase 1): `STATE.md`; previous base checkpoint `RUN_20260828T140430_JST.md`.
