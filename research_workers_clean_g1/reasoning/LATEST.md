# Reasoning Systems — clean_g1 latest pointer

Newest checkpoint: `2026-08-28T1013JST.md`
Current invocation chain: `2026-08-28T1013JST.md` -> `2026-08-28T0907JST.md` -> `2026-08-28T0848JST.md` -> `2026-08-28T0737JST.md` -> earlier immutable clean reasoning history.

Read `STATE.md`, then the minimum predecessor chain needed for unresolved-frontier continuity, then the newest checkpoint. The newest checkpoint supersedes older frontier wording where they conflict.

Frozen semantic control for the newest invocation: note main `7478136278c6f26fd36fd3227200dca28d6bf4fe`; DESIRED_STATE control rev 12 / blob `5c91671e1470d0fa4e2a53f918493004dd3750c3`; reasoning config rev 6 / blob `cc8b37410994561a016a72c467b25ff0582d6462`. The SHA-only pre-semantic freshness recheck matched. Later note-main advances were not adopted as a new semantic control tuple.

## Top unresolved frontier

1. Freeze **C589–C605** and all associated confirmation/disagreement pools. Never recalibrate and retest a policy on the split that exposed its failure/success.
2. Preserve the preferred **retained verified incumbent + optional challenger + sequential value-of-computation** architecture. Incumbent/simple-policy recall is the hard no-harm mechanism; learned allocation may only change optional compute spend.
3. The first 31-feature absolute-scale logistic remains retired. Its aggregate n=16 holdout passed but was decision-equivalent to v1; its only identified n=18 policy disagreement was a high-confidence false positive that spent 519 extra candidate compilations for zero gain.
4. A new immutable preregistration exists at `experiments/coalition_seeded_tail_value_model_scaled_dev_v1_protocol.json`. Deterministically replay the exact 120 allowed development states and persist the row table/hash before fitting. Do not use any successful confirmation/disagreement pool or unrevealed C599 agreement tails.
5. The next learned model is queried only where frozen v1 would stop and must estimate **incremental future gain over v1**, using scale-normalized/horizon-aware features plus conservative OOD and bootstrap-stability abstention. If development thresholds fail, freeze the negative result rather than retuning it into passing.
6. Correct the public Lean routing evidence to current arXiv v3: **28.9%** average cost decrease and **7.9%** accuracy improvement at parity cost on its 85-problem PutnamBench subset. Its evaluated action space is binary `Attempt/Terminate`; the **62.0%** zero-noise oracle is a privileged current-target success-probability oracle, not a rich-action oracle.
7. Use the v3 trajectory evidence as a transfer guide only: normalized proof similarity, compiler-error diversity and inverse attempt count are the evaluated quality features; error diversity has the strongest ablation. Keep cost scope explicit because the paper treats Lean compilation as negligible and models next-attempt generation cost.
8. VERITAS now supplies a direct formal-proof analogue of baseline preservation: Best-of-N Phase 1 successes are retained and Critic-MCTS Phase 2 runs only on Phase-1 failures. Search for the missing combination: **VERITAS-like monotonicity + adaptive amount of Phase-2 compute**.
9. Preserve nonzero audit/exploration propensity for rejected regions and exact action propensity logging. Use cumulative anytime-valid inference; sparse one-batch zero discoveries are not evidence of zero tail value.
10. Preserve the original n=20 order-portfolio holdout unchanged for its original protocol and all older rebuild/TDD/lemma/result-graph/C263/OPA-Regorus/deterministic-safety frontiers.

## Newest synthesis

- **C601:** current v3 supersedes C600's version-sensitive 25.8% figure with **28.9%** average cost decrease; the exact public split is 85 problems = 42 train / 43 test.
- **C602:** the evaluated v3 controller is `Attempt/Terminate`; its 62.0% zero-noise oracle bounds better current-target/next-attempt difficulty estimation inside that architecture, not model switching, repair, retrieval or decomposition choices.
- **C603:** normalized proof similarity, compiler-error diversity and attempt count are directly evaluated trajectory signals; public code also contains richer behavioral features, but they do not yet have the same control-plane ablation evidence. Transfer the relative/verifier-grounded state idea, not benchmark-specific thresholds or a cost model that ignores verifier/runtime overhead by assumption.
- **C604:** VERITAS preserves every theorem solved by its own Best-of-N Phase 1 and runs Phase-2 MCTS only on Phase-1 failures, giving a direct formal-proof retained-incumbent analogue. Its second-stage budget is still fixed, leaving sequential VoC open.
- **C605:** `coalition_seeded_tail_value_model_scaled_dev_v1_protocol.json` preregisters the next synthetic controller as incremental-over-v1, dimensionless, OOD-conservative and bootstrap-stability gated. No model has been fit yet because exact development rows must be deterministically replayed first.
- Scope guard: synthetic ROBDD results motivate controller architecture only. Formal-proof claims remain source/config/benchmark qualified.

## Exact continuation

1. Deterministically replay the exact 120 allowed development cases for `coalition_seeded_tail_value_model_scaled_dev_v1_protocol.json`; persist row table/hash before any fit.
2. Fit/evaluate the preregistered scale-normalized incremental-over-v1 logistic with LOFO development only. Freeze failure if the joint positive-recall and gain-weighted-recall thresholds are not met.
3. If development passes, freeze scaler/coefs/threshold/OOD bounds/bootstrap contract before a wholly-new confirmation split. Confirmation must report incremental verified gain over v1 and extra compute over v1 jointly.
4. Search formal-proof systems for learned or sequential **amount-of-second-stage-compute** control under a retained verified baseline; keep VERITAS as the closest current monotonicity precedent.
5. Inspect public Lean routing artifacts only for evidence actually evaluated under richer actions; do not infer experimental support from code extensibility alone.
6. Preserve exact propensity logging, cumulative audit inference, all older replay/safety frontiers, and the untouched n=20 holdout.

`2026-08-28T1013JST.md` is newest and is not global completion.

Do not read legacy `research_workers/reasoning/`, O/O-derived state, comparator/integrator/index/feed/audits, other-worker state/config, shared execution ledger, other-role receipts/config, or semantic payloads bundled into head lookup.
