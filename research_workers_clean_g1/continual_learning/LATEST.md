# Continual Learning — clean_g1 latest

Phase 1 is active under `phase1-clean-continual-learning-durable-adaptation` / `o-chat-parity-root-v4-zero-work-dependency-zero-quota`.

Latest Phase-1 checkpoint: `PHASE1_DURABLE_ADAPTATION_20260831T0913_JST.json`

Bounded slice result: one distinct event `e5` was accepted after `e4b`, producing post-`e5` state digest `2874d4d9872bf12b923d25bc1b1da83a39a01cd4ef3ded0423d353470da4eaac` and chain `60dae8a6066aa27dd7e980cce2f9707175a79fd651c6b306a7abb739b635868d`. After a simulated restart with no preseeded ephemeral applied-event registry, the two complete durable frames were revalidated and scanned to reconstruct `e4b -> 9f1b2481...` and `e5 -> 760afd1e...`.

Replaying the older exact `e4b` frame after intervening `e5` encountered a stale `prev_chain`, but duplicate lookup occurred first. The reconstructed index returned `duplicate_already_applied_noop`; no second effect occurred; post-`e5` state and chain were unchanged; all preexisting keys plus `zeta` were retained. Delayed duplicate second-effect rate and modeled forgetting rate were both 0 in this exact two-record fixture.

Scope: deterministic small text state; exactly two sequential complete frames; one restart after `e5`; two-entry index reconstruction; one delayed old-frame replay. This does not establish arbitrarily long/corrupted journals, duplicate-ID payload conflicts, partial-tail recovery, compaction/tombstones, concurrency, lock-free progress, fairness, semantic model-weight adaptation, or indefinite repository availability. The tested route required no richer/protected/manual execution, finite monthly/trial/paid quota, scheduler mutation, or incremental monetary cost; repository contents API was durable transport/readback only.

Exact continuation: next invocation, stay on this same idempotency/restart leaf. Starting from the validated `e4b -> e5` journal and reconstructed index, submit a frame whose `event_id` is `e4b` but whose patch payload differs from the stored `e4b` digest. Verify event-id lookup occurs before `prev_chain` acceptance and returns explicit `duplicate_id_payload_conflict` rejection rather than noop/apply, while post-`e5` state/chain and all keys remain unchanged. Persist only that conflict evidence; do not start another leaf.

Base-state fallback metadata only (inactive during Phase 1): `STATE.md`; previous base checkpoint `RUN_20260828T140430_JST.md`.
