# Continual Learning — clean_g1 latest

Phase 1 is active under `phase1-clean-continual-learning-durable-adaptation` / `o-chat-parity-root-v4-zero-work-dependency-zero-quota`.

Latest Phase-1 checkpoint: `PHASE1_DURABLE_ADAPTATION_20260831T0617_JST.json`

Bounded slice result: the previously rejected writer-B event `e4b` was explicitly rebuilt against writer A's current chain `1f85222b849bbe70399c138e37e02da030515407207b2fa489cf966974c97dfc`. Canonical event digest remained `9f1b2481c467ac787b39c68f3499a1e56a12e0962173b876b7d7ca838f8a9f04`; the rebased complete frame was 323 bytes and committed as `c8eb9c60a9190246145563be3710aadbafbab97ae57ac2ea4aa57a2cf1ebd8d8`. Applying it once added `epsilon=E_B` while retaining writer A's `delta=D_A`, giving state digest `a6739dc997e04f1741a972637f43c7533c8e23a158134cb5d17335e2757aee8d`.

Immediate replay of the identical rebased frame was recognized by the modeled applied-event registry as the same `event_id` plus identical payload digest before the now-stale `prev_chain` gate. Replay status was `duplicate_already_applied_noop`: state digest and chain remained exactly unchanged, writer B's second-effect rate was 0, and modeled forgetting of preexisting keys was 0.

Scope: deterministic small text state; one explicit stale-writer rebase, one serialized acceptance, and one immediate identical-frame replay. This does not establish crash-safe persistence of the idempotency registry across restart, arbitrary delayed duplicates after intervening events, lock-free progress, fairness, semantic model-weight adaptation, or indefinite repository availability. All mechanism logic was Chat-local; repository contents API was durable transport only, with no hosted compute, finite monthly/trial/paid quota, richer/protected/manual execution, scheduler mutation, or incremental monetary cost.

Exact continuation: next invocation, simulate a restart after accepted `e4b`, reconstruct the applied-event idempotency index only from the durable framed journal, then replay the identical `e4b` frame and verify cross-run duplicate recognition preserves state digest `a6739dc997e04f1741a972637f43c7533c8e23a158134cb5d17335e2757aee8d` and chain `c8eb9c60a9190246145563be3710aadbafbab97ae57ac2ea4aa57a2cf1ebd8d8` with zero second effect. Persist only that reconstruction-plus-replay evidence; do not start another leaf.

Base-state fallback metadata only (inactive during Phase 1): `STATE.md`; previous base checkpoint `RUN_20260828T140430_JST.md`.
