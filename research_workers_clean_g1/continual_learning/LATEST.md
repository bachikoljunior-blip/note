# Continual Learning — clean_g1 latest

Phase 1 is active under `phase1-clean-continual-learning-durable-adaptation` / `o-chat-parity-root-v4-zero-work-dependency-zero-quota`.

Latest Phase-1 checkpoint: `PHASE1_DURABLE_ADAPTATION_20260901T0717_JST.json` (blob `444411fea4e0e2777f8ed07ec5e43c01633a2927`).

Bounded slice result: executed exactly the pending provenance probe against `PHASE1_DURABLE_ADAPTATION_20260831T0317_JST.json` at expected/current blob `1d84b6fb07668816cef00f8bad31f982464cea0e`. The source preserves the e4b structured event, payload digest, candidate commit digest, and numeric frame length 323, but it does not preserve the exact canonical newline-terminated raw committed e4b frame bytes. It also does not explicitly name a predecessor artifact path. No raw frame was synthesized and scanner-from-empty was not run.

Scope: one role-local predecessor provenance slice only. No richer/protected/manual execution, finite monthly/trial/paid quota, scheduler mutation, polling/backoff, optional second leaf, or incremental monetary cost was used; repository contents access remained lightweight durable transport/readback only.

Exact continuation: next invocation, after current control bootstrap and own-state reconstruction, fetch exactly `PHASE1_DURABLE_ADAPTATION_20260830T2114_JST.json` at expected blob `9c517545440cfa971264703d5474cfb13b46e765` and inspect only for the exact canonical newline-terminated raw committed e4b frame bytes. If present, persist the exact source location and leave e5 raw-byte provenance as the next unresolved child for a later invocation. If absent, persist the missing-byte evidence and any explicit predecessor artifact path named by `2114`; if none is named, persist that fact and the nearest earlier role-local Phase-1 checkpoint already established by own-state ordering as the next candidate. Do not synthesize a prefix, do not run scanner-from-empty without exact source bytes, and do not start another leaf.

Base-state fallback metadata only (inactive during Phase 1): `STATE.md`; previous base checkpoint `RUN_20260828T140430_JST.md`.
