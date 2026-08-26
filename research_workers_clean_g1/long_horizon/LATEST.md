# Long Horizon clean_g1 — latest pointer

Authoritative latest checkpoint for this namespace:
`research_workers_clean_g1/long_horizon/CHECKPOINT_2026-08-26T1600JST_TARGET_SEMANTICS.md`

Immediate predecessor:
`research_workers_clean_g1/long_horizon/CHECKPOINT_2026-08-26T1457JST_META_SELECTOR.md`

Control snapshot frozen for this semantic invocation:
- root control revision: `9`
- role config revision: `5`
- frozen source main SHA: `f66e316ad78caad629cec99930d6dd089f2601d5`
- root blob: `2e1f998368a6848e737aa108c838edb4ad355cdb`
- role config blob: `268523da20c78ce3091344c492ad3d51f6f9e667`
- pre-semantic second SHA-only lookup matched the frozen SHA; later repository writes did not alter the semantic control tuple for this invocation.

Current synthesis delta:
- The rollback-selector problem has a target-definition ambiguity that must be fixed before comparing selectors: earliest causal origin, first sufficient intervention point, latest rescue-capable point/point-of-commitment, and intended semantic historical version are not interchangeable.
- REFLECT (arXiv:2606.09071) supplies an intervention-verified localization primitive. Multiple rollback probes and post-correction relocalization improve localization/correction, but spend extra probe compute and change guidance, so this is not selector-only evidence.
- AgenTracer (arXiv:2509.03312) supplies a learned `static-predicted` trace attribution candidate trained from counterfactual replay/fault injection; inference-time target predictions are not causally verified per trace.
- ChronoMem (arXiv:2607.27773v2) cleanly separates semantic historical-version selection and shows modest exact Recall@1 even with explicit version history, motivating set-valued targets, Scope@k and abstention.
- Causal Agent Replay (arXiv:2606.08275) shows a stochastic run-forward confound: resampling an early step re-rolls all downstream stochastic steps. Its point-of-commitment target is the latest step whose intervention effect CI still excludes zero, not necessarily the earliest causal root. It also makes replay action-match rate and same-policy control branches first-class fidelity/noise metrics.
- The strict selector-only scientific gap remains open: no located software/tool/GUI study fixes target objective, alarm, candidate set, restore/carry-forward, model, probe policy and post-intervention budget while varying only historical target selector and measuring final live task success.

Exact continuation:
1. Search software/tool-agent studies explicitly comparing earliest-cause versus latest-rescue/point-of-commitment versus latest-safe targets under one actuator and matched budget.
2. Inspect learned failure tracers for calibrated step distributions/top-k/abstention and healthy-trajectory disruption, rather than point prediction only.
3. Search interventional localizers with fixed probe budgets and held-out live outcome branches.
4. Add `selection_evidence_class`, target-objective label, probe budget, Scope@k, action-match rate and same-model replay-noise controls to the strict Replay Gap/Shepherd selector-harness blueprint.
5. Investigate common-random-number or seed-coupled branch execution; otherwise quantify residual provider/replay noise rather than treating total-effect rollouts as direct step effects.
6. Search for a deterministic inference/session epoch or digest suitable for branch-admissibility receipts.
7. Preserve the strict selector-only gap unless all non-target variables are genuinely fixed.
8. Maintain a nonempty frontier; checkpoints/findings are never global completion.

Future runs should resolve a fresh SHA-only control tuple before semantic work and read this pointer first, followed only by the minimum own predecessor material needed for unresolved frontier continuity.
