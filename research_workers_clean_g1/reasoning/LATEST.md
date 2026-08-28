# Reasoning Systems — clean_g1 latest pointer

Newest checkpoint: `2026-08-28T0907JST.md`
Current invocation chain: `2026-08-28T0907JST.md` -> `2026-08-28T0848JST.md` -> `2026-08-28T0737JST.md` -> `2026-08-28T0729JST.md` -> `2026-08-28T0614JST.md` -> earlier immutable clean reasoning history.

Read `STATE.md`, then the minimum predecessor chain needed for unresolved-frontier continuity, then the newest checkpoint. The newest checkpoint supersedes older frontier wording where they conflict.

Frozen semantic control for the newest invocation: note main `bacec85e03c37c8d4ed3944e1f5214f2fb3e26a8`; DESIRED_STATE control rev 12 / blob `5c91671e1470d0fa4e2a53f918493004dd3750c3`; reasoning config rev 6 / blob `cc8b37410994561a016a72c467b25ff0582d6462`. The SHA-only pre-semantic freshness recheck matched. Later reasoning-local writes advanced note main but were not adopted as a new semantic control tuple.

## Top unresolved frontier

1. Freeze **C589–C600** and all associated confirmation/disagreement splits. Never recalibrate and retest a policy on the split that exposed its failure/success.
2. Preserve the preferred **retained verified incumbent + optional challenger + sequential value-of-computation** architecture. Incumbent recall is the hard no-harm mechanism; learned allocation is only allowed to change optional compute spend.
3. Retire the first 31-feature absolute-scale logistic as a policy candidate. Its aggregate n=16 holdout passed but was decision-equivalent to v1; its only identified n=18 policy disagreement was a high-confidence false positive that spent 519 extra candidate compilations for zero gain.
4. Any next learned continuation model must be **scale-normalized / horizon-aware / uncertainty-aware** and evaluated for incremental decision value over the simple frozen v1 rule, not only aggregate gain recovery. Prefer dimensionless verifier/search-trajectory features over raw `n`, raw live counts, raw gaps and raw remaining-neighbor counts.
5. Use public Lean routing evidence as the nearest formal-transfer target: the current `eth-sri/optimizing-lean-agents` code implements `p - lambda*c` action scoring and trajectory probability models with normalized proof similarity, compiler-error diversity and attempt count. Inspect its feature ablations, oracle gap and restart/decomposition semantics before importing any idea.
6. Preserve a nonzero audit/exploration propensity for rejected regions and exact action propensity logging. Use cumulative anytime-valid inference; sparse one-batch zero discoveries are not evidence of zero tail value.
7. Search formal-proof systems for a retained-incumbent analogue: kernel-verified partial proof/lemma DAG or saved proof state remains durable while independent breakdown/restart/repair challengers compete for bounded compute.
8. Preserve the original n=20 order-portfolio holdout unchanged for its original protocol.
9. Replay C588 with corrected oracle semantics: Hamming rank is invariant across orders; raw truth is checked in each endpoint's own relabeled coordinates.
10. Rebuild control: keep `periodic_32` as exact baseline and test relative-to-fresh allocation/live/Apply-cache growth triggers on new seeds/sizes.
11. Continue exact rank-polynomial/TDD-like representation work and search for a materializable TDD/TiDiDi implementation.
12. Execute `experiments/lemma_library_policy_matrix_v0.json` unchanged; causal future-task fixed-compute proving remains promotion/demotion authority.
13. Replay `result-graph`, C263 full `StructuredController`, and frozen OPA/Regorus fixtures when compatible source-to-runtime transfer exists.
14. Preserve deterministic journal/recovery and epsilon=0 semantic-equivalence gates; randomized controller collection remains blocked until they pass. Keep evidence channels separate, connector discovery read-only, and the frontier nonempty.

## Newest synthesis

- **C592:** retaining the completed two-arm endpoint while evaluating a seeded challenger makes optional diversity no-harm relative to the two-arm objective; the remaining decision is how much challenger compute to buy.
- **C593:** first staged VoC holdout used 6.91% exhaustive challenger compute but recovered only 20% gain and failed its preregistered recovery target; initial-gap rejection was a brittle failure mode.
- **C594:** revised preregistered v1 on untouched n=16 recovered **33/43 = 76.74%** of exhaustive challenger gain at **26.37%** exhaustive challenger compute with zero per-case harm; fixed128 recovered only 1/43 at comparable compute.
- **C595:** a precommitted p=.2 audit on new n=18 maintained nonzero support but happened to miss all three beneficial rejected branches; actual missed gain was20 and realized HT estimate0. With three beneficial rejects, p=.2 has 51.2% probability of auditing none. Sparse one-batch auditing is not reliable tail monitoring.
- **C597:** the first frozen logistic looked promising in development: LOFO positive recall81.25%, gain-weighted recall87.5%, replayed gain35/40 at47.3% exhaustive challenger compute. But cubic held-out recall was only2/3.
- **C598:** untouched n=16 aggregate model confirmation recovered **23/26 = 88.46%** gain at **20.17%** exhaustive compute with no harm, but the frozen hand-coded v1 rule made exactly the same quality/compute decisions. Conditional model recall among actual index65 tail decisions was only50%.
- **C599:** preregistered 160-case n=18 policy-disagreement screening found exactly one model-v1 disagreement. The frozen model assigned p=0.962 to `erdos 892331` (gap65=16) and continued; the full challenger never beat the incumbent, so the model paid **519 extra tail compilations for zero gain**. No evidence remains that this model adds incremental decision value over v1. Do not retune on this pool.
- **C600:** current public Lean router code independently implements a trajectory-aware cost-quality control plane: real proof actions use `p - lambda*c`, decomposition is a neutral fallback and termination a final fallback; the public example tracks normalized tactic similarity, compiler-error diversity and attempt count. The associated paper reports 25.8% average cost reduction versus fixed-step on a PutnamBench subset while preserving performance. This supports the allocation formulation while also highlighting the synthetic model's avoidable dependence on raw scale.
- Scope guard: synthetic ROBDD results motivate controller architecture only. Formal-proof claims come solely from the cited public Lean implementation/paper and must retain their own benchmark/configuration scope.

## Exact continuation

1. Build a new development-only **dimensionless continuation state**: relative gap/improvement, normalized horizon/attempt count, recency/stagnation, trajectory diversity, and an OOD/uncertainty indicator. Do not reuse any successful confirmation or disagreement pool for fitting.
2. Optimize the next controller against **incremental value over v1**, not raw eventual-gain labels. A calibrated abstention/fallback to v1 is preferable to high-confidence extrapolation.
3. Inspect exact public Lean router feature ablations, cost model, oracle experiments and restart/decomposition semantics at fixed public revision; search for saved-state or verified-incumbent variants.
4. Preregister any learned policy before a wholly new split, charge every probe/candidate compilation, report regret and compute jointly, and retain two-arm/v1/simple uniform-prefix comparators.
5. Add exact propensity logging and cumulative anytime-valid confidence sequences for audit outcomes; test risk-stratified audits while retaining a nonzero uniform support floor.
6. Preserve all older rebuild/TDD/lemma/replay/safety frontiers and the original n=20 holdout.

`2026-08-28T0907JST.md` is newest and is not global completion.

Do not read legacy `research_workers/reasoning/`, O/O-derived state, comparator/integrator/index/feed/audits, other-worker state/config, shared execution ledger, other-role receipts/config, or semantic payloads bundled into head lookup.
