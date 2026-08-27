# Reasoning Systems — clean_g1 latest pointer

Newest checkpoint: `2026-08-28T0729JST.md`
Current invocation chain: `2026-08-28T0729JST.md` -> `2026-08-28T0614JST.md` -> `2026-08-28T0539JST.md` -> earlier immutable clean reasoning history.

Read `STATE.md`, then the minimum predecessor chain needed for unresolved-frontier continuity, then the newest checkpoint. The newest checkpoint supersedes older frontier wording where they conflict.

## Chronology note

Current invocation start: `2026-08-28T06:58:16+09:00`; newest checkpoint observation: `2026-08-28T07:29:35+09:00`. Chronology is valid.

Frozen semantic control for this invocation: note main `3009465cf48864bd1377c2f62f170c7804b6c1d0`; DESIRED_STATE control rev 12 / blob `5c91671e1470d0fa4e2a53f918493004dd3750c3`; reasoning config rev 6 / blob `cc8b37410994561a016a72c467b25ff0582d6462`. The SHA-only pre-semantic freshness recheck matched. Later authorized reasoning-local writes advanced note main but were not adopted as new semantic control.

## Top unresolved frontier

1. Freeze C589/C590. Do not recalibrate the v0 classifier, B=32, or probe trigger on those holdouts and retest the same cases.
2. Develop a sequential seeded-search budget ladder only on prior/development data, e.g. `0/32/64/128/full`, with every candidate compilation charged and the observed improvement trajectory used as state. Any stop rule or utility/risk constraint must be frozen before a new untouched split.
3. Prefer an explicit final-quality-regret versus extra-compute Pareto frontier. If a scalar utility is used, fix its weights/constraint before outcomes rather than choosing them post hoc.
4. Investigate cheap predictors of tail-improvement potential / survival hazard. C590's only seeded benefit did not beat the conventional first-stage live count until candidate 242/290, so an early fixed prefix is not a transferable gate.
5. Preserve the original n=20 order-portfolio holdout unchanged for a compatible runtime. Smaller/newer holdouts do not replace it.
6. Replay C588 with corrected oracle semantics: Hamming rank is invariant across variable orders; raw assignment-indexed truth bitsets must be checked in each endpoint's own relabeled coordinates.
7. Rebuild control: keep `periodic_32` as exact baseline and test relative-to-fresh allocation/live/Apply-cache growth triggers on new seeds/sizes.
8. Continue exact rank-polynomial/TDD-like representation work and search for a materializable TDD/TiDiDi implementation.
9. Execute `experiments/lemma_library_policy_matrix_v0.json` unchanged; causal future-task fixed-compute proving remains promotion/demotion authority.
10. Replay `result-graph`, C263 full `StructuredController`, and frozen OPA/Regorus fixtures when compatible source-to-runtime transfer exists.
11. Preserve deterministic journal/recovery and epsilon=0 semantic-equivalence gates; randomized controller collection remains blocked until they pass. Keep evidence channels separate and the frontier nonempty.

## Newest synthesis

- **C589, preregistered multi-family n=16:** frozen v0 learned gate opened 7/24, saving **18.154%** candidate compilations versus always-three, but missed Erdős seed `884305` and incurred **+7 final live-node regret**. Co-primary selectivity and compute passed; quality failed.
- C589 also falsified the old one-stage binary target as a sufficient objective: quartic `884102` was a one-stage seeded-positive, yet final always-three was **138** live nodes versus **126** for two-arm. A stage-1 win can lead to a worse final basin.
- The persisted v1 truth-oracle assertion is not replay-safe: raw truth bitsets are not invariant under variable relabeling. C589/C590 use invariant Hamming-rank checks during search and exhaustive direct truth checks at completed endpoints in their own relabeled coordinates.
- **Development only:** a `B=32` probe-complete rule retrospectively matched per-case `min(two,three)` across 84 prior cases while saving roughly 13.9–21.3%; this was not confirmatory evidence.
- **C590, preregistered untouched n=18:** probe-complete saved **22.773%** candidate compilations versus always-three but triggered **0/24** and missed the sole seeded final benefit, quartic `885103`, producing **+6 live-node regret**. It therefore failed the quality co-primary criterion.
- On C590 the probe policy produced exactly the two-arm final live vector while spending **792** extra candidate compilations, so it was strictly dominated by two-arm on observed quality/compile metrics.
- Post-hoc only: on `885103`, the first seeded neighbor beating the conventional first-stage count appeared only at **242/290**; always-three spent 296 extra compiles over two-arm for a 6-live improvement. This motivates explicit value-of-computation/Pareto evaluation rather than a mandatory zero-regret-at-any-cost rule.
- Durable new outputs: `experiments/coalition_seeded_start_multifamily_transfer_v2_protocol.json`, `..._v2_runner.py`, `..._v2_results.json`, `experiments/coalition_seeded_probe_complete_v0_protocol.json`, `..._v0_runner.py`, `..._v0_results.json`.
- Scope guard: synthetic positive-monotone graph 2-CNF ROBDD-ordering only. None of these results establish a general proof-search controller or authorize global lemma-library promotion/demotion.

## Exact continuation

1. Develop but do not confirm on C589/C590 a sequential value-of-computation controller using the search-progress curve and charged cost.
2. Preregister any revised policy on a new untouched split and evaluate final regret and compute jointly.
3. Preserve the original n=20 portfolio holdout and remaining rebuild/TDD/lemma/replay/safety frontiers.
4. Keep connector discovery read-only and all writes within the reasoning-local/own-receipt boundaries.

`2026-08-28T0729JST.md` is newest and is not global completion.

Do not read legacy `research_workers/reasoning/`, O/O-derived state, comparator/integrator/index/feed/audits, other-worker state/config, shared execution ledger, other-role receipts/config, or semantic payloads bundled into head lookup.
