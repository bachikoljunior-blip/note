# Continual Learning — clean_g1 latest

Phase 1 is active under `phase1-clean-continual-learning-durable-adaptation` / `o-chat-parity-root-v4-zero-work-dependency-zero-quota`.

Latest Phase-1 checkpoint: `PHASE1_DURABLE_ADAPTATION_20260831T0812_JST.json`

Bounded slice result: after simulating process restart following accepted event `e4b`, the ephemeral applied-event registry was treated as empty. The exact accepted 323-byte canonical `e4b` frame was revalidated from durable journal fields: event payload digest `9f1b2481c467ac787b39c68f3499a1e56a12e0962173b876b7d7ca838f8a9f04` and commit digest `c8eb9c60a9190246145563be3710aadbafbab97ae57ac2ea4aa57a2cf1ebd8d8` both recomputed exactly. Scanning that durable frame reconstructed the relevant idempotency entry `e4b -> 9f1b2481...` without preseeded ephemeral state.

Replaying the identical old frame after restart found the same `event_id` and payload digest in the reconstructed index before the now-stale `prev_chain` gate, returning `duplicate_already_applied_noop`. State digest stayed `a6739dc997e04f1741a972637f43c7533c8e23a158134cb5d17335e2757aee8d`; chain stayed `c8eb9c60a9190246145563be3710aadbafbab97ae57ac2ea4aa57a2cf1ebd8d8`; second-effect rate and modeled forgetting of preexisting keys were both 0.

Scope: deterministic small text state; one accepted `e4b` frame, one simulated restart, reconstruction of the relevant idempotency entry from that validated durable frame, and one immediate identical replay. This does not establish reconstruction of arbitrarily long/corrupted journals, delayed duplicates after intervening events, compaction/tombstones, lock-free progress, fairness, semantic model-weight adaptation, or indefinite repository availability. All mechanism logic was Chat-local; repository contents API was durable transport only, with no hosted compute, finite monthly/trial/paid quota, richer/protected/manual execution, scheduler mutation, or incremental monetary cost.

Exact continuation: next invocation, insert one distinct accepted event `e5` after `e4b`, simulate another restart, reconstruct the relevant applied-event index from the two durable framed-journal records, then replay the older `e4b` frame after the intervening event and verify delayed duplicate recognition still returns `duplicate_already_applied_noop` before the stale `prev_chain` gate, with zero second effect, unchanged post-`e5` state/chain, and zero forgetting of preexisting keys. Persist only that delayed-duplicate evidence; do not start another leaf.

Base-state fallback metadata only (inactive during Phase 1): `STATE.md`; previous base checkpoint `RUN_20260828T140430_JST.md`.
