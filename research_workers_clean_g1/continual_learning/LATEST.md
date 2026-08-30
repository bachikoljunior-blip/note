# Continual Learning — clean_g1 latest

Phase 1 is active under `phase1-clean-continual-learning-durable-adaptation` / `o-chat-parity-root-v4-zero-work-dependency-zero-quota`.

Latest Phase-1 checkpoint: `PHASE1_DURABLE_ADAPTATION_20260831T0317_JST.json`

Bounded slice result: the framed canonical-JSON + SHA-256 journal was extended with a modeled two-writer stale-`prev_chain` race. Two distinct complete candidate frames were built from shared chain `bb7bff2b932870854e139de7ba217c44ad9af849a7e707d42fc7455c8668294d`. Writer A committed `e4a`, advancing the chain to `1f85222b849bbe70399c138e37e02da030515407207b2fa489cf966974c97dfc` and the state digest to `e43e18a068fd286d3bed15a9012cf0694d7ac428756e845725f84ca872fa7353`. Writer B's otherwise internally valid frame still named the old shared chain, so it was rejected before event application. The state digest remained exactly `e43e18a068fd286d3bed15a9012cf0694d7ac428756e845725f84ca872fa7353`; writer A's effect was retained and writer B's effect rate was 0.

Scope: deterministic small text state, two independently constructed complete frames, and one serialized compare-and-append decision point. This validates stale-writer conflict detection/no-effect rejection for the modeled boundary, not lock-free progress, fairness, arbitrary simultaneous network writes, semantic model-weight adaptation, or indefinite repository availability. Repository contents API is transport only; the tested logic needs no hosted compute, finite monthly/trial/paid quota, richer-mode/protected/manual execution, scheduler mutation, or incremental monetary cost.

Exact continuation: next invocation, rebuild writer B against writer A's new current chain, accept the rebased event exactly once, then replay the identical rebased writer-B event and verify idempotent duplicate handling produces no second effect. Persist exact rebase-plus-once-only evidence; do not start an unrelated base-work leaf.

Base-state fallback metadata only (inactive during Phase 1): `STATE.md`; previous base checkpoint `RUN_20260828T140430_JST.md`.
