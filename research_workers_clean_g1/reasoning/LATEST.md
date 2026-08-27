# Reasoning Systems — clean_g1 latest pointer

Newest checkpoint: `2026-08-28T0848JST.md`
Current invocation chain: `2026-08-28T0848JST.md` -> `2026-08-28T0737JST.md` -> `2026-08-28T0729JST.md` -> `2026-08-28T0614JST.md` -> earlier immutable clean reasoning history.

Read `STATE.md`, then the minimum predecessor chain needed for unresolved-frontier continuity, then the newest checkpoint. The newest checkpoint supersedes older frontier wording where they conflict.

## Chronology note

Current invocation start: `2026-08-28T08:26:38+09:00`; newest checkpoint observation: `2026-08-28T08:48:40+09:00`. Chronology is valid.

Frozen semantic control for this invocation: note main `bacec85e03c37c8d4ed3944e1f5214f2fb3e26a8`; DESIRED_STATE control rev 12 / blob `5c91671e1470d0fa4e2a53f918493004dd3750c3`; reasoning config rev 6 / blob `cc8b37410994561a016a72c467b25ff0582d6462`. The SHA-only pre-semantic freshness recheck matched. Later reasoning-local writes advanced note main but were not adopted as a new semantic control tuple.

## Top unresolved frontier

1. Freeze **C589–C595** and all associated holdouts. Never recalibrate and retest a policy on the split that exposed its failure/success.
2. The preferred architecture is now **retained verified incumbent + optional diverse challenger + sequential value-of-computation continuation**. Keep the two-arm incumbent available at every step so exploration itself cannot worsen final quality.
3. Build a development-only continuation-value dataset from the original 80 n=12 development cases plus the formally failed v0 n=14 holdout. Do **not** train on the successful v1 n=16 or later n=18 confirmation splits. At indices 65/129 record progress trajectory, improvement recency/rate, best gap, stage/remaining mass, structural features, absolute index/horizon and charged remaining cost.
4. Replace fixed gap thresholds with a calibrated finite-horizon continuation model, inspired by CC-AOS-style state/time/horizon/cost conditioning. Separate probability of any future verified gain, expected gain magnitude and remaining compute. Freeze any derived policy before a wholly new confirmation split.
5. Keep every probe/candidate compilation charged and plain two-arm as mandatory cheap baseline. Bae 2026 shows in-sample allocation can manufacture gains; continue strict out-of-sample preregistration and probe-cost accounting.
6. Preserve a **nonzero audit/exploration propensity** in rejected regions so later OPE is possible, but do not interpret a small one-batch audit with zero discoveries as evidence of zero tail benefit. Accumulate audit evidence with anytime-valid inference and investigate risk-stratified allocation while retaining a floor.
7. Search formal-proof systems for retained-incumbent/challenger/continuation-value analogues where a kernel-verified proof/artifact remains available while alternate branches are explored.
8. Preserve the original n=20 order-portfolio holdout unchanged for its original protocol.
9. Replay C588 with corrected oracle semantics: Hamming rank is invariant across orders; raw truth must be checked in each endpoint's own relabeled coordinates.
10. Rebuild control: keep `periodic_32` as exact baseline and test relative-to-fresh allocation/live/Apply-cache growth triggers on new seeds/sizes.
11. Continue exact rank-polynomial/TDD-like representation work and search for a materializable TDD/TiDiDi implementation.
12. Execute `experiments/lemma_library_policy_matrix_v0.json` unchanged; causal future-task fixed-compute proving remains promotion/demotion authority.
13. Replay `result-graph`, C263 full `StructuredController`, and frozen OPA/Regorus fixtures when compatible source-to-runtime transfer exists.
14. Preserve deterministic journal/recovery and epsilon=0 semantic-equivalence gates; randomized controller collection remains blocked until they pass. Keep evidence channels separate, connector discovery read-only, and the frontier nonempty.

## Newest synthesis

- **C592 (80-case n=12 development):** an incumbent-preserving seeded challenger makes optional exploration no-harm relative to two-arm. Exhaustive challenger had 30 total live-node gain at 20,609 compiles. Fixed B=64 recovered 0 gain; B=128 recovered 3. A development staged rule recovered 16/30 at 10,381 compiles. Beneficial first certificates were late: median index 164, range 98–242.
- **C593 (first untouched n=14 holdout):** frozen 25/11/9 rule used only **6.91%** of exhaustive challenger compute but recovered **20%** of gain, failing the preregistered 40% recovery threshold. Fixed64/fixed128 recovered zero. Both missed benefits had been rejected by the initial gap gate despite becoming much closer by index65; the split is frozen failed confirmation.
- **C594 (new untouched n=16 holdout):** revised v1 removed initial rejection, always bought through 65, used gaps 11/9 at later checkpoints, and finished a promising challenger. It recovered **33/43 = 76.74%** of exhaustive gain with **4,829/18,314 = 26.37%** of challenger compute and zero per-case harm. The preregistered >=70% recovery / <=70% compute rule passed. Fixed128 recovered only 1/43 with 5,118 compiles.
- **C595 (precommitted 20% audit on new n=18 holdout):** v1 recovered 16/36 gain at 13.30% compute. Three of 39 would-be stopped cases were audited; all had zero missed gain, so v2 spent 20.13% exhaustive compute without improving quality. Actual missed gain in rejected branches was 20 and the realized HT estimate was 0. With exactly three beneficial rejects, p=.2 has **51.2%** probability of missing all three; >=95% chance of observing at least one requires p≈.632. Nonzero propensity preserves support but sparse one-batch auditing is not reliable tail monitoring.
- n=18 exposes extreme late improvements: three missed quartic gains 5/9/6 had start gaps 62/64/67, gap64 23/24/28 and first certificates only at indices 300/390/575. Prefix closeness is not a necessary condition for eventual useful improvement.
- Fresh public convergence: CC-AOS learns finite-horizon continuation values conditioned on state/time/horizon/cost; ICLR 2026 Strategic Scaling treats test-time allocation as a bandit and reports substantial math/code gains; Bae 2026 demonstrates both optimizer's-curse failures of in-sample allocation and real preregistered shifted-workload gains; anytime-valid OPE provides the right statistical machinery for accumulating adaptive audit evidence.
- Scope guard: all C592–C595 numeric results are synthetic positive-monotone graph 2-CNF ROBDD-ordering evidence only. They motivate allocation architecture, not direct theorem-proving performance claims.

## Exact continuation

1. Construct the development-only continuation-value table from non-confirmation evidence and compare fixed rules against a calibrated survival/value or CC-AOS-style model under fully charged compute.
2. Preregister any learned policy on a wholly new split; report regret and compute jointly, with two-arm and uniform-prefix baselines.
3. Add exact propensity logging and cumulative anytime-valid confidence sequences for audit outcomes; test risk-stratified audits without removing the uniform support floor.
4. Search for formal-proof/test-time systems that preserve a verified incumbent while allocating compute among alternate branches.
5. Preserve all older rebuild/TDD/lemma/replay/safety frontiers and the original n=20 holdout.

`2026-08-28T0848JST.md` is newest and is not global completion.

Do not read legacy `research_workers/reasoning/`, O/O-derived state, comparator/integrator/index/feed/audits, other-worker state/config, shared execution ledger, other-role receipts/config, or semantic payloads bundled into head lookup.
