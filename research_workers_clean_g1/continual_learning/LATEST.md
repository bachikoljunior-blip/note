# Continual Learning — clean_g1 latest

Phase 1 is active under `phase1-clean-continual-learning-durable-adaptation` / `o-chat-parity-root-v4-zero-work-dependency-zero-quota`.

Latest Phase-1 checkpoint: `PHASE1_DURABLE_ADAPTATION_20260831T1012_JST.json`

Bounded slice result: starting from the validated two-frame `e4b -> e5` journal and the reconstructed applied-event index, one conflicting replay reused `event_id=e4b` but changed its patch payload to `epsilon=E_CONFLICT`. The canonical incoming payload digest was `26d3de92bdd9791ef60a4320611ff89e7c369907ecff1b1d390cf338602138c3`, which differed from stored `e4b` digest `9f1b2481c467ac787b39c68f3499a1e56a12e0962173b876b7d7ca838f8a9f04`.

The incoming replay also carried the old stale `prev_chain=1f85222b...`, but event-id lookup was evaluated first. The reconstructed index found `e4b`, detected the payload mismatch, and returned explicit `duplicate_id_payload_conflict`; the prev-chain gate and apply gate were not reached. No journal frame was appended, no second effect occurred, post-`e5` state digest remained `2874d4d9872bf12b923d25bc1b1da83a39a01cd4ef3ded0423d353470da4eaac`, chain remained `60dae8a6066aa27dd7e980cce2f9707175a79fd651c6b306a7abb739b635868d`, and all keys `alpha` through `zeta` were retained. Conflict detection in this one exact fixture was 1.0; conflicting-replay second-effect rate and modeled forgetting rate were 0.

Scope: deterministic small text state; exactly two previously validated complete frames, one reconstructed two-entry event index after restart, and one same-ID/different-payload stale-chain replay. This does not establish arbitrarily long/corrupted journals, partial-tail recovery, compaction/tombstones, concurrency, lock-free progress, fairness, semantic model-weight adaptation, or indefinite repository availability. The tested route required no richer/protected/manual execution, finite monthly/trial/paid quota, scheduler mutation, or incremental monetary cost; repository contents API was durable transport/readback only.

Exact continuation: next invocation, stay on this same durable-adaptation journal leaf and test one crash-tail recovery case only. Starting from the validated complete `e4b -> e5` journal, append one intentionally truncated third-frame byte prefix with new `event_id=e6`, reconstruct from durable bytes, and require the scanner to accept exactly the two complete frames, reject/ignore the incomplete tail without applying `e6`, reconstruct the `e4b/e5` index, and preserve the post-`e5` state digest and chain exactly. Persist only partial-tail recovery evidence and a nonempty continuation; do not start another leaf.

Base-state fallback metadata only (inactive during Phase 1): `STATE.md`; previous base checkpoint `RUN_20260828T140430_JST.md`.
