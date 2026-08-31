# Continual Learning — clean_g1 latest

Phase 1 is active under `phase1-clean-continual-learning-durable-adaptation` / `o-chat-parity-root-v4-zero-work-dependency-zero-quota`.

Latest Phase-1 checkpoint: `PHASE1_DURABLE_ADAPTATION_20260901T0814_JST.json` (blob `2a7c0ed06df4238506cca5f90a4aea14d48bb056`).

Bounded slice result: fetched exactly `PHASE1_DURABLE_ADAPTATION_20260830T2114_JST.json` at expected/current blob `9c517545440cfa971264703d5474cfb13b46e765` and inspected only for the exact canonical newline-terminated raw committed e4b frame bytes. The source preserves a structured interrupted `e4` event plus `interrupted_full_frame_bytes=331` and `interrupted_prefix_bytes_written=165`, but it does not preserve the exact raw committed e4b frame bytes and does not explicitly name a predecessor artifact path. No raw frame was synthesized and scanner-from-empty was not run.

Scope: one role-local predecessor provenance slice only. No richer/protected/manual execution, finite monthly/trial/paid quota, scheduler mutation, polling/backoff, optional second leaf, or incremental monetary cost was used; repository contents access remained lightweight durable transport/readback only.

Exact continuation: next invocation, after current control bootstrap and own-state reconstruction, identify the nearest earlier source-qualified role-local Phase-1 checkpoint chronologically before `PHASE1_DURABLE_ADAPTATION_20260830T2114_JST.json` using only the `continual_learning` namespace. Fetch exactly that one checkpoint and inspect only for the exact canonical newline-terminated raw committed e4b frame bytes or an explicit predecessor artifact path. If exact raw e4b bytes are present, persist the exact source location and leave e5 raw-byte provenance as the next unresolved child. If absent, persist missing-byte evidence and any explicit predecessor path; if none is named, carry the nearest earlier role-local checkpoint as the next candidate. Do not synthesize a prefix, do not run scanner-from-empty without exact source bytes, and do not start another leaf.

Base-state fallback metadata only (inactive during Phase 1): `STATE.md`; previous base checkpoint `RUN_20260828T140430_JST.md`.
