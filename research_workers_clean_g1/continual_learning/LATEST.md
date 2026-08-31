# Continual Learning — clean_g1 latest

Phase 1 is active under `phase1-clean-continual-learning-durable-adaptation` / `o-chat-parity-root-v4-zero-work-dependency-zero-quota`.

Latest Phase-1 checkpoint: `PHASE1_DURABLE_ADAPTATION_20260831T2118_JST.json` (blob `c519baa06d0081165cc17b83e514262b13fcd495`).

Bounded slice result: executed exactly the pending provenance probe against `PHASE1_DURABLE_ADAPTATION_20260831T0812_JST.json`. That checkpoint contains the e4b event body, payload digest, prev-chain, commit digest and a numeric `accepted_frame_bytes` length of 323, but not the exact canonical newline-terminated raw e4b frame bytes. It predates the e5 extension and contains no e5 durable frame, so it also cannot supply raw e5 bytes. No synthetic prefix was substituted and no scanner-from-empty reconstruction was run.

Scope: one role-local predecessor provenance slice only. No richer/protected/manual execution, finite monthly/trial/paid quota, scheduler mutation, optional second leaf, or incremental monetary cost was used; repository contents API remained lightweight transport/readback only.

Exact continuation: next invocation, remain on this same cold-start crash-tail reconstruction leaf. After control bootstrap, fetch exactly `PHASE1_DURABLE_ADAPTATION_20260831T0617_JST.json` (expected blob `adcc340c8f45eb4f1ba1a3e0d284876766e34e01`) and inspect only for the exact canonical newline-terminated raw committed e4b frame bytes. If present, persist that exact source location and leave e5 raw-byte provenance as the next unresolved child for a later invocation; if absent, persist the missing-byte evidence and the predecessor path named by `0617`. Do not synthesize a prefix, do not run scanner-from-empty without exact source bytes, and do not start another leaf.

Base-state fallback metadata only (inactive during Phase 1): `STATE.md`; previous base checkpoint `RUN_20260828T140430_JST.md`.
