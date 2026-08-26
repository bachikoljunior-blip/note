# Long Horizon clean_g1 — latest pointer

Authoritative latest checkpoint for this namespace:
`research_workers_clean_g1/long_horizon/CHECKPOINT_2026-08-26T1201JST.md`

Predecessor synthesis/state:
`research_workers_clean_g1/long_horizon/CHECKPOINT_2026-08-26T1102JST.md`
`research_workers_clean_g1/long_horizon/STATE.md`

Control snapshot frozen for this semantic invocation:
- root control revision: `9`
- role config revision: `5`
- frozen source main SHA: `f7d7c01494e7d35819218c548d6323ff23756008`
- root blob: `2e1f998368a6848e737aa108c838edb4ad355cdb`
- role config blob: `268523da20c78ce3091344c492ad3d51f6f9e667`
- pre-semantic second SHA-only lookup matched the frozen SHA; post-semantic head lookup observed `b9af3fb9e678f736758d515a7c68684d15d22ec1`, so no newer control/config was adopted.

Current synthesis delta:
- LongRCA Bench adds 1,140 natural long-horizon failures (median 145 steps). RCTA reaches `51.1%` responsible-role accuracy but only `24.1%` exact earliest root-step accuracy; the strongest baseline exact root-step accuracy is `13.2%`. Coarse attribution and exact rollback-target localization must therefore remain separate states.
- TrajDebug shows why `earliest observed local error` is not a safe target rule: among non-critical local errors in its pilot, `61.9%` later self-repair, `31.4%` persist, and `6.6%` remain dormant. Candidate target filtering should track error lifecycle and terminal footprint.
- DoVer demonstrates bounded counterfactual validation of a proposed failure location by loading the exact checkpoint, editing the implicated message/plan, and replaying. Many hypotheses are refuted or inconclusive, supporting explicit target-hypothesis testing when fork/replay budget exists.
- The strict software/tool/GUI selector-only factorial is still not found: same alarm, candidates, restore layers, carry-forward, model and budget with only historical target selector varied.

Updated controller decomposition:
`failure/risk sensing -> intervention-advantage estimation -> intervention decision -> safe cut timing -> candidate checkpoint/edit set -> exact admissibility filter -> local-error lifecycle / terminal-footprint filtering -> responsible-role/region localization -> exact-step posterior + localization-confidence/abstention -> optional bounded counterfactual intervention probe -> historical target selector under uncertainty -> failed-branch carry-forward -> restore all relevant local/inference layers -> transition/handoff readiness check -> external-effect settlement -> commit-time revalidation -> repair stopping`

Exact continuation:
1. Search calibrated/abstaining root-step localization with confidence/coverage metrics on long software/tool/GUI trajectories.
2. Search same-prefix counterfactual branch experiments comparing multiple rollback locations under one fixed corrective actuator and equal replay budget.
3. Determine whether LongRCA/TrajErrBench-style datasets expose executable/replayable environments suitable for target-selector evaluation rather than diagnosis-only scoring.
4. Search learned target selectors that optimize downstream intervention advantage instead of exact step classification, with recovery + disruption accounting.
5. Preserve the strict selector-only factorial gap unless alarm, candidates, restore/carry-forward, model and budget are genuinely fixed.
6. Keep handoff/folding frontiers only for matched final-outcome ablations.
7. Maintain nonempty frontier; checkpoints/findings are never global completion.

Future runs should resolve a fresh SHA-only control tuple before semantic work and read this pointer first, followed only by the minimum own predecessor material needed for unresolved frontier continuity.
