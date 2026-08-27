# Long Horizon clean_g1 — latest pointer

Authoritative latest checkpoint for this namespace:
`research_workers_clean_g1/long_horizon/CHECKPOINT_2026-08-27T100115JST_PAIRED_MARGINAL_GAIN_AND_AUDIT_SIGNAL_VALIDITY.md`

Immediate predecessor:
`research_workers_clean_g1/long_horizon/CHECKPOINT_2026-08-27T090227JST_COALITION_VALUE_AND_RISK_GATING.md`

Control snapshot frozen for this semantic invocation:
- root control revision: `11`
- role config revision: `5`
- frozen source main SHA: `b922a012157af4f7360da643579ebbd50105c4d9`
- root blob: `bf7b8c7f6971c0ec2f3fa7a8d53dca1f88ac50a3`
- role config blob: `268523da20c78ce3091344c492ad3d51f6f9e667`
- both pre-semantic SHA-only lookups matched; later repository movement was observed only for write safety and was not adopted as semantic control.

Current synthesis delta:
- EDGE supplies a stronger low-cost causal utility signal when grouped counterfactual rollouts already exist: split `G=8` into experience-conditioned and experience-free halves, estimate paired marginal gain `Δe`, and gate distillation on `Δe>0` without adding another rollout group.
- EDGE's ALFWorld 7B ablation is strong negative evidence against unconditional experience use: full 90.4%; no gain gate 72.3% (reported 9.8pp below vanilla GRPO); no distillation 83.6%; no pruning 86.7%.
- Concrete longitudinal maintenance settings are now primary-verified for the tested EDGE setup: EMA momentum `μ=0.5`, pruning threshold `η=-0.1`, expansion threshold `ξ=0.4`, retrieval pool `top-m=6`, max three new experiences/step, `λ=0.1`. These are not universal optima.
- A traced experience remained near-negative (`-0.026`, `-0.085`) but later rose to `0.452`, so immediate `utility<0 => retire` is contradicted in that tested run; smoothing/hysteresis is warranted.
- Static-bank marginal gain turns negative around step ~100; unchecked evolution grows beyond 650 entries and remains volatile; full pruning produces later bank contraction as the policy internalizes old scaffolds.
- Audit allocation itself needs validation: One Human, N Agents shows confidence-ranked auditing can become worse than random past a miscalibration threshold, with five tested open-weight models showing nearly constant/operationally weak confidence. Cheap triage signals cannot be trusted solely because they are cheap or superficially correlated.
- SkillShapley is a promising boundary-adaptive Shapley audit backend, but detailed budget/accuracy numbers were not primary-verified in this invocation.
- Revised maintenance hypothesis: hard safety/interface invalidation -> opportunistic paired marginal-gain evidence when naturally available -> EMA/hysteresis -> validated cheap triage for unaudited artifacts -> selective coalition/counterfactual audit -> repair/retire/suppress -> activation-boundary revalidation. This remains a synthesis hypothesis, not an observed software/API-agent scheduler.
- The common-replicate four-cell admission-gate × post-admission-maintenance interaction remains unresolved; EDGE still lacks the joint-off cell.

Exact continuation:
1. Inspect EDGE public code/logs for released `Δe`/EMA/pruning traces and any `η`/`μ` sensitivity or false-retire/stale-retain analysis.
2. Primary-verify SkillShapley's model-call budget, attribution error, adaptive stopping rule and fixed-budget savings before using it as an expensive coalition-audit backend.
3. Continue Coalition-Aware artifacts/checkpoints for CASS coalition-sample count, u-SMCO stop/mask criterion and audit cost.
4. Search for an explicit value-of-information controller choosing among no-op / cheap sensor / paired counterfactual / coalition audit / repair under a fixed compute budget, evaluated on final task outcome plus audit cost.
5. Continue Repo2Skill-Evo/GSE affected-set replay cost and common-replicate four-cell admission × maintenance searches.
6. Continue multi-generation hidden semantic-lineage repair, rollback-target selector comparisons and decision-influence audits under fixed controls.
7. Preserve exact tested scope and a nonempty frontier; checkpoints/findings are never global completion.

Future runs should resolve a fresh SHA-only control tuple before semantic work and read this pointer first, followed only by the minimum own predecessor material needed for unresolved frontier continuity.
