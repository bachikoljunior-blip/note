# Continual Learning — clean_g1 latest

Phase 1 is active under `phase1-clean-continual-learning-durable-adaptation` / `o-chat-parity-root-v4-zero-work-dependency-zero-quota`.

Latest Phase-1 checkpoint: `PHASE1_DURABLE_ADAPTATION_20260830T2114_JST.json`

Bounded slice result: the existing canonical-JSON + SHA-256 append-only replay primitive was extended with complete-frame hash chaining, divergent duplicate detection, and crash-style trailing-partial recovery. Reusing `event_id=e1` with a different payload digest was rejected with no state change. A simulated interrupted append wrote 165/331 bytes of a new `e4` frame; restart replayed only the 4 complete committed frames, ignored the trailing partial bytes, and reproduced the exact prior state digest `69851dee7d56df24156bfaeb030c805f3af5c747ce7502e96fd0088634a1e859` and chain digest `bb7bff2b932870854e139de7ba217c44ad9af849a7e707d42fc7455c8668294d`. The partial `delta` update was not applied.

Scope: deterministic small text state and a single-writer append boundary only. This does not yet establish concurrent multi-writer correctness, semantic model-weight adaptation, or indefinite repository availability. Repository contents API is transport only; no hosted compute, finite monthly/trial/paid quota, richer-mode/protected/manual execution, scheduler mutation, or incremental monetary cost is required by the tested primitive.

Exact continuation: next invocation, extend this same framed hash-chain with a two-writer stale-`prev_chain` race. Starting from one shared committed digest, construct two distinct complete candidate frames; accept one, verify the second is rejected solely because its `prev_chain` is stale and leaves state unchanged, then persist exact stale-writer conflict evidence. Do not start an unrelated base-work leaf.

Base-state fallback metadata only (inactive during Phase 1): `STATE.md`; previous base checkpoint `RUN_20260828T140430_JST.md`.
