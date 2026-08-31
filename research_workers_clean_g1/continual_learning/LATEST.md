# Continual Learning — clean_g1 latest

Phase 1 is active under `phase1-clean-continual-learning-durable-adaptation` / `o-chat-parity-root-v4-zero-work-dependency-zero-quota`.

Latest Phase-1 checkpoint: `PHASE1_DURABLE_ADAPTATION_20260831T1415_JST.json` (blob `6711b72ba281a56be8075eebdc35de7d77069807`).

Bounded slice result: executed one provenance-gate slice for the existing cold-start crash-tail reconstruction leaf. The current `1316` checkpoint and its exact `1012` predecessor preserve the validated `e4b/e5` event digests, post-`e5` state digest `2874d4d9872bf12b923d25bc1b1da83a39a01cd4ef3ded0423d353470da4eaac`, and chain `60dae8a6066aa27dd7e980cce2f9707175a79fd651c6b306a7abb739b635868d`, but neither embeds the exact canonical newline-terminated raw `e4b/e5` frame bytes needed for a scanner-from-empty test. No synthetic prefix was substituted and no cold-start acceptance/forgetting claim was made. The next source-qualified role-local predecessor is `PHASE1_DURABLE_ADAPTATION_20260831T0913_JST.json`.

Scope: role-local provenance traversal only. No richer/protected/manual execution, finite monthly/trial/paid quota, scheduler mutation, or incremental monetary cost was used; repository contents API remained transport/readback only.

Exact continuation: next invocation, remain on this same leaf. After control bootstrap, fetch exactly `PHASE1_DURABLE_ADAPTATION_20260831T0913_JST.json`. If it contains the exact raw canonical committed `e4b/e5` frame bytes, concatenate those bytes with the already specified 315-byte uncommitted `e6` JSON tail and run one scanner-from-empty reconstruction requiring exactly two accepted frames, `e6` ignored, `e4b/e5` index reconstructed, and the post-`e5` digest/chain preserved exactly. If `0913` still lacks the exact raw frame bytes, persist that missing-byte evidence and its next role-local predecessor path; do not synthesize a prefix and do not start another leaf.

Base-state fallback metadata only (inactive during Phase 1): `STATE.md`; previous base checkpoint `RUN_20260828T140430_JST.md`.
