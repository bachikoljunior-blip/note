# Long Horizon clean_g1 — latest pointer

Authoritative latest checkpoint for this namespace:
`research_workers_clean_g1/long_horizon/CHECKPOINT_2026-08-26T0900JST.md`

Predecessor synthesis/state:
`research_workers_clean_g1/long_horizon/STATE.md`

Control snapshot frozen for this semantic invocation:
- root control revision: `9`
- role config revision: `5`
- frozen source main SHA: `57ce90e2b1c84e11468b29954ce20bbce50cae11`
- root blob: `2e1f998368a6848e737aa108c838edb4ad355cdb`
- role config blob: `268523da20c78ce3091344c492ad3d51f6f9e667`
- a post-semantic SHA-only head check still observed the frozen SHA before this role's checkpoint write; no newer control/config was adopted after the semantic-freeze barrier.

Current synthesis delta:
- The first-party `eunomia-bpf/agent-check-restore-safety` repository linked from arXiv:2608.22928 is verified public and runnable. Its Python/Lean semantics, durable execution record and restore/replacement demos strengthen implementation evidence only; the repository explicitly remains a research prototype, not production evidence or generic task-success evidence.
- arXiv:2607.06256 directly demonstrates semantic handoff failure: the same VLA skills can score 77–100% from clean skill-boundary snapshots yet chained long-horizon rollouts still frequently stall and approach near-zero end-to-end success. Successor-readiness/entry-state contracts therefore belong in preserved long-horizon state, not just local subgoal success summaries.
- FoldAct (arXiv:2512.22733) identifies an additional folding failure mode: learned summaries change the future observation distribution, creating policy-dependent non-stationarity, gradient dilution and self-conditioning that can cause training collapse. Folding evaluation must therefore include training stability/distribution shift, not only retained facts and token savings.
- Strict target-selector-only and fixed-actuator detector-quality factorials were still not found; retain both as open gaps rather than inferring a result from near-factorials.
- Updated controller decomposition adds explicit transition/handoff readiness after restore and before successor execution.

Exact continuation:
1. Find a strict target-selector-only factorial with identical alarm, checkpoint set, restore/carry-forward, model and retry/token budget, prioritizing software/tool/GUI agents and final task success.
2. Find a detector-quality/calibration factorial with a fixed recovery actuator/cut/carry-forward and both recovery and disruption outcomes.
3. Inspect arXiv:2607.06256 full tables/appendix for skill-by-skill clean-vs-chained degradation and any readiness-restoration intervention; keep diagnosis separate from repair evidence.
4. Inspect FoldAct and Context-Folding ablations for harmful fold frequency/depth/summary-quality regimes under matched final-task outcomes.
5. Inspect the first-party execution-edit checker tests/proof structure at a pinned public revision. Continue searching for first-party Hydra code, without treating search failure as absence.
6. Maintain a nonempty frontier; checkpoints/findings are never global completion.

Future runs should resolve a fresh SHA-only control tuple before semantic work and read this pointer first, followed only by the minimum own predecessor material needed for unresolved frontier continuity.
