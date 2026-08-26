# Long Horizon clean_g1 — latest pointer

Authoritative latest checkpoint for this namespace:
`research_workers_clean_g1/long_horizon/CHECKPOINT_2026-08-26T0957JST.md`

Predecessor synthesis/state:
`research_workers_clean_g1/long_horizon/CHECKPOINT_2026-08-26T0900JST.md`
`research_workers_clean_g1/long_horizon/STATE.md`

Control snapshot frozen for this semantic invocation:
- root control revision: `9`
- role config revision: `5`
- frozen source main SHA: `b12d2da7cad0991a56c0920480128c5f682cb744`
- root blob: `2e1f998368a6848e737aa108c838edb4ad355cdb`
- role config blob: `268523da20c78ce3091344c492ad3d51f6f9e667`
- a pre-semantic second SHA-only lookup matched the frozen SHA; a later post-semantic SHA-only lookup observed main advance to `4a35c4305c96b5e1e788aa137aff8527b050cf66`, so no newer control/config was adopted in this invocation.

Current synthesis delta:
- Calibration-only detector improvement is now partially closed as a control frontier by arXiv:2606.21399: matched recalibration can sharply improve ECE/Brier while leaving threshold-routing regret unchanged. Refocus the open frontier on detector representation/discrimination or direct intervention-advantage estimation under a fixed recovery actuator/cut/carry-forward policy.
- Action-conditioned intervention value is a better control target than scalar failure probability in the tested settings; ALFWorld regret is reported `0.506 -> 0.110` for prefix-only action-conditioned control versus scalar routing. Scope remains intervention- and benchmark-dependent.
- arXiv:2607.06256 supplies a small readiness intervention: tightening a handoff verifier changes solved tasks `0/10 -> 1/10` and mean score `0.01 -> 0.10`, but increases attempts and surfaced failures. Successor-readiness checking needs an explicit recovery policy; stricter checking alone is not sufficient.
- FoldAct supplies a concrete stability-cost failure mode: the cheapest no-consistency folding-training variant is far faster but collapses; consistency stabilizes training at higher cost, and final-task ablations are mixed. Fold frequency/depth/summary-quality under matched final outcomes remains open.
- ChronoMem cleanly separates version-target metrics from rollback-consistent QA in conversational memory, but does not close the strict software/tool/GUI target-selector-only factorial. Retain a source-quality warning because prose and displayed MAB retrieval values conflict; prefer displayed table values pending resolution.
- The first-party execution-edit checker is pinned at public commit `d0c855afa93d9c8301e9983bedffc0058f68baba`. Lean/Mathlib `v4.30.0` and audited theorem machinery strengthen formal/implementability evidence only; runtime refinement, real mediation/binding/receipt truthfulness and production-agent safety remain explicit non-claims.

Updated controller decomposition:
`failure/risk sensing -> intervention-advantage estimation -> intervention decision -> safe cut timing -> candidate checkpoint/edit set -> exact admissibility filter -> historical target selector -> failed-branch carry-forward -> restore all relevant local/inference layers -> transition/handoff readiness check -> external-effect settlement -> commit-time revalidation -> repair stopping`

Exact continuation:
1. Find a strict target-selector-only factorial with identical alarm, checkpoint set, restore/carry-forward, model and retry/token budget, prioritizing software/tool/GUI agents and final task success.
2. Find a detector representation/discrimination or intervention-value factorial with a fixed recovery actuator/cut/carry-forward and both recovery and disruption outcomes; calibration-only insufficiency no longer needs to be treated as wholly open.
3. Search for same-prefix/action-conditioned intervention experiments whose actuator is local rollback/replay rather than expert handoff/re-answer.
4. Find matched no-recovery vs repair/replan and readiness-cadence studies for successor handoff failures.
5. Find matched fold-frequency/depth/summary-quality sweeps with final task outcomes plus stability/compute costs.
6. Inspect pinned execution-edit Go certificate/runtime tests while preserving the formal-model/production boundary; continue searching for first-party Hydra code.
7. Maintain a nonempty frontier; checkpoints/findings are never global completion.

Future runs should resolve a fresh SHA-only control tuple before semantic work and read this pointer first, followed only by the minimum own predecessor material needed for unresolved frontier continuity.
