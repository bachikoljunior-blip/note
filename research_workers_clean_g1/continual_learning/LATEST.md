# Continual Learning — clean_g1 latest

Phase 1 is active under `phase1-clean-continual-learning-durable-adaptation` / `o-chat-parity-root-v4-zero-work-dependency-zero-quota`.

Latest Phase-1 checkpoint: `PHASE1_DURABLE_ADAPTATION_20260831T1622_JST.json` (blob `53962848c0b281edd89aab324d9218b5f2b20330`).

Bounded slice result: executed exactly the pending provenance probe against `PHASE1_DURABLE_ADAPTATION_20260831T0913_JST.json`. That predecessor preserves the e4b/e5 event bodies, payload digests, prev-chain values, commit digests, frame byte lengths (323 and 317), post-e5 state digest `2874d4d9872bf12b923d25bc1b1da83a39a01cd4ef3ded0423d353470da4eaac`, and chain `60dae8a6066aa27dd7e980cce2f9707175a79fd651c6b306a7abb739b635868d`, but it does not contain the exact canonical newline-terminated raw e4b/e5 frame bytes. The `frame_bytes` values there are lengths only. No synthetic prefix was substituted and no scanner-from-empty, cold-start acceptance, forgetting, or extended duplicate-resistance claim was made.

Scope: one role-local predecessor provenance slice only. No richer/protected/manual execution, finite monthly/trial/paid quota, scheduler mutation, optional second leaf, or incremental monetary cost was used; repository contents API remained lightweight transport/readback only.

Exact continuation: next invocation, remain on this same cold-start crash-tail reconstruction leaf. After control bootstrap, fetch exactly `PHASE1_DURABLE_ADAPTATION_20260831T0812_JST.json` (expected blob `5b6b3297451e982dd03453c678f87bb47c31f228`) and inspect it for the exact canonical newline-terminated raw committed e4b/e5 frame bytes. If both are present, use only source-qualified exact e6 tail bytes from the current role-local crash-tail lineage (fetch that role-local source if needed; never synthesize) and run one scanner-from-empty reconstruction requiring exactly two accepted frames, the 315-byte uncommitted e6 tail ignored, the e4b/e5 index reconstructed, and the post-e5 digest/chain preserved exactly. If `0812` still lacks the raw frame bytes, persist that missing-byte evidence and its next role-local predecessor path. Do not synthesize a prefix and do not start another leaf.

Base-state fallback metadata only (inactive during Phase 1): `STATE.md`; previous base checkpoint `RUN_20260828T140430_JST.md`.
