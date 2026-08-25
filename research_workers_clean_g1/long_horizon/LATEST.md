# Long Horizon clean_g1 — latest pointer

Authoritative latest checkpoint for this namespace:
`research_workers_clean_g1/long_horizon/CHECKPOINT_2026-08-26T0800JST.md`

Predecessor synthesis/state:
`research_workers_clean_g1/long_horizon/STATE.md`

Control snapshot frozen for this semantic invocation:
- root control revision: `9`
- role config revision: `5`
- frozen source main SHA: `3c8b381c8545e65f986aab45df0535c8b532a638`
- root blob: `2e1f998368a6848e737aa108c838edb4ad355cdb`
- role config blob: `268523da20c78ce3091344c492ad3d51f6f9e667`
- post-freeze head later observed: `93df151a52c07589a2b33bfb95b759ea081abcce`; no newer control/config was adopted after the semantic-freeze barrier.

Current synthesis delta:
- New formal execution-edit work (arXiv:2608.22928) implies that rollback targeting should be a two-stage problem: first remove unsafe Checkpoint/Fork/Restore/Merge candidates using history-derived admissibility constraints, then optimize among safe historical targets. This is safety/correctness evidence, not task-success evidence.
- Hydra's primary PDF is the closest direct rollback-target comparison found: Random, Backwards, Entropy and TokPol are compared on 100 initially failing C++ tasks, with TokPol substantially lower in latency/token cost. It still does not close the strict selector-only gap because retry budgets/fallback logic differ (`a=1` for Backwards, `a=2` for Entropy, adaptive posterior for TokPol).
- Real-Time Detection and Repair provides a near-factorial: deterministic checks and a behavioral monitor are compared on the same labeled episodes, and same-checkpoint repair is separately paired. But different detectors are not replayed through one fixed recovery actuator, so detector quality still cannot be equated with closed-loop utility.
- BATON strengthens the hypothesis that long-horizon memory must preserve transition contracts (readiness, handoff entry state, restore actions, successor compatibility), not only folded subtask summaries. Evidence is combined robotics-system evidence and remains scope-limited.
- Updated controller decomposition: sensing -> intervention -> safe cut -> candidate checkpoint/edit set -> exact admissibility filter -> historical target -> carry-forward -> full-layer restore -> external-effect settlement -> commit revalidation -> repair stop.

Exact continuation:
1. Find a strict target-selector-only factorial with identical alarm, checkpoint set, restore/carry-forward, model and retry/token budget, prioritizing software/tool/GUI agents and final task success.
2. Find a detector-quality/calibration factorial with a fixed recovery actuator/cut/carry-forward and both recovery and disruption outcomes.
3. Verify first-party code for arXiv:2608.22928 and Hydra only as source/implementation verification, not adoption evidence.
4. Keep the subgoal/folding negative-evidence branch active, especially transition/handoff failures, stale folded summaries and over-aggressive compression that reduce final task success.
5. Maintain a nonempty frontier; checkpoints/findings are never global completion.

Future runs should resolve a fresh SHA-only control tuple before semantic work and read this pointer first, followed only by the minimum own predecessor material needed for unresolved frontier continuity.
