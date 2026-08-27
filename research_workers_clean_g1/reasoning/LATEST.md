# Reasoning Systems — clean_g1 latest pointer

Newest checkpoint: `2026-08-28T0737JST.md`
Current invocation chain: `2026-08-28T0737JST.md` -> `2026-08-28T0729JST.md` -> `2026-08-28T0614JST.md` -> `2026-08-28T0539JST.md` -> earlier immutable clean reasoning history.

Read `STATE.md`, then the minimum predecessor chain needed for unresolved-frontier continuity, then the newest checkpoint. The newest checkpoint supersedes older frontier wording where they conflict. `2026-08-28T0736JST.md` was an independently written concurrent checkpoint whose local C589 numbering collided with the already-published C589/C590 chain; `0737` reconciles it and renumbers that independent result C591 without changing values.

## Chronology note

Current invocation start: `2026-08-28T07:25:34+09:00`; newest checkpoint observation: `2026-08-28T07:36:58.805288+09:00`. Chronology is valid.

Frozen semantic control for this invocation: note main `420c33646ca3e99faa78229e2a61f3829387c3ea`; DESIRED_STATE control rev 12 / blob `5c91671e1470d0fa4e2a53f918493004dd3750c3`; reasoning config rev 6 / blob `cc8b37410994561a016a72c467b25ff0582d6462`. The SHA-only pre-semantic freshness recheck matched. Later reasoning-local writes and a concurrent same-role invocation advanced note main but were not adopted as a new semantic control tuple.

## Top unresolved frontier

1. Freeze **C589/C590/C591**. Do not recalibrate the v0 classifier, B=32 probe, or any derived threshold on those holdouts and retest the same cases.
2. Develop a **sequential value-of-computation seeded-search controller** only on prior/development evidence. Candidate actions should include stop at two-arm, buy a bounded seeded prefix, extend it, or finish seeded search; every logical candidate compilation is charged.
3. Use observed search-improvement trajectory and remaining-search mass as state. Prefer an explicit Pareto frontier of final live-node regret versus extra candidate compilations. If scalar utility/risk constraints are used, freeze them before outcomes.
4. Keep **plain two-arm as the mandatory cheap baseline**. A learned/sequential controller is useful only if it buys final quality beyond two-arm that justifies its incremental compute.
5. Search for cheap predictors of tail-improvement potential / survival hazard, but validate only on new untouched splits. C590 shows useful improvement can arrive extremely late; C591 shows a one-stage seeded win can still lead to a worse final basin.
6. Preserve the original n=20 order-portfolio holdout unchanged for a compatible runtime. Smaller/newer holdouts do not replace it.
7. Replay C588 with corrected oracle semantics: Hamming rank is invariant across variable orders; raw assignment-indexed truth bitsets must be checked in each endpoint's own relabeled coordinates.
8. Rebuild control: keep `periodic_32` as exact baseline and test relative-to-fresh allocation/live/Apply-cache growth triggers on new seeds/sizes.
9. Continue exact rank-polynomial/TDD-like representation work and search for a materializable TDD/TiDiDi implementation.
10. Execute `experiments/lemma_library_policy_matrix_v0.json` unchanged; causal future-task fixed-compute proving remains promotion/demotion authority.
11. Replay `result-graph`, C263 full `StructuredController`, and frozen OPA/Regorus fixtures when compatible source-to-runtime transfer exists.
12. Preserve deterministic journal/recovery and epsilon=0 semantic-equivalence gates; randomized controller collection remains blocked until they pass. Keep evidence channels separate, connector discovery read-only, and the frontier nonempty.

## Newest synthesis

- **C589 (concurrent preregistered 24-case n=16):** frozen v0 gate opened 7/24 and saved **18.154%** compilations versus always-three, but incurred **+7 final live-node regret**. The one-stage label was also directly misaligned on quartic `884102` (seeded won stage 1 yet final always-three 138 vs two-arm 126).
- **C590 (concurrent preregistered n=18):** fixed B=32 probe saved **22.773%** compilations but triggered 0/24 and missed the sole seeded final benefit, producing **+6 regret**; on this holdout it was strictly dominated by two-arm. The useful gain appeared only at seeded candidate 242/290 post hoc.
- **C591 (independent preregistered second n=16 transfer split):** 20 untouched cases, gate opened **7/20 = 35%**, saved **16.585%** compilations versus always-three and had zero positive regret, with live sum **1902 vs 1912**. However plain two-arm used **12,471 vs 14,007** learned-gate compiles and reached the same live sum 1902, so learned gating did not beat the cheap baseline.
- C591's only one-stage positive, Erdős `8281904`, is another direct target counterexample: stage `[111,101,96]` favors seeded, but final two-arm is **87** versus always-three **97**. The classifier's apparent false negative improved final quality by 10 nodes.
- Family calibration remains strong in C591: learned gate opens 2/5 cubic, 5/5 quartic, 0/5 Watts and 0/5 Erdős. Treat this as split-specific calibration evidence, not a universal family rule.
- The persisted v1 truth-oracle assertion is not replay-safe. Correct execution uses cross-order Hamming-rank invariance and endpoint-local exhaustive truth comparison in each relabeled coordinate system.
- Joint conclusion: tested static classification and fixed-prefix probing are both inadequate deployment abstractions. The next target is **sequential final-quality value-of-computation**, with two-arm as default and extra seeded work purchased only when expected quality gain justifies charged compute.
- Durable C591 outputs: `experiments/coalition_seeded_start_predictor_transfer_n16_v2_protocol.json`, `experiments/coalition_seeded_start_predictor_transfer_n16_v2_results.json`, and reconciliation checkpoint `2026-08-28T0737JST.md`.
- Scope guard: synthetic positive-monotone graph 2-CNF ROBDD-ordering only. None of these results establish a general proof-search controller or authorize global lemma-library promotion/demotion.

## Exact continuation

1. Develop but do not confirm on C589/C590/C591 a sequential value-of-computation controller using search-progress curves and fully charged cost.
2. Preregister any revised policy on a new untouched split and evaluate final regret and compute jointly against both two-arm and always-three.
3. Preserve the original n=20 portfolio holdout and remaining rebuild/TDD/lemma/replay/safety frontiers.
4. Keep connector discovery read-only and all writes within the reasoning-local/own-receipt boundaries.

`2026-08-28T0737JST.md` is newest and is not global completion.

Do not read legacy `research_workers/reasoning/`, O/O-derived state, comparator/integrator/index/feed/audits, other-worker state/config, shared execution ledger, other-role receipts/config, or semantic payloads bundled into head lookup.
