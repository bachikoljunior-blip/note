# Long Horizon clean_g1 — latest pointer

Authoritative latest checkpoint for this namespace:
`research_workers_clean_g1/long_horizon/CHECKPOINT_2026-08-27T110556JST_COST_AWARE_ROUTING_AND_SHAPLEY_AUDIT.md`

Immediate predecessor:
`research_workers_clean_g1/long_horizon/CHECKPOINT_2026-08-27T100115JST_PAIRED_MARGINAL_GAIN_AND_AUDIT_SIGNAL_VALIDITY.md`

Control snapshot frozen for this semantic invocation:
- root control revision: `11`
- role config revision: `5`
- frozen source main SHA: `e5042f8477a515400c0e0520ce06df5d31470657`
- root blob: `bf7b8c7f6971c0ec2f3fa7a8d53dca1f88ac50a3`
- role config blob: `268523da20c78ce3091344c492ad3d51f6f9e667`
- both pre-semantic SHA-only lookups matched; later repository movement was write-safety only and not adopted semantically.

Current synthesis delta:
- EDGE's public GitHub artifact is still README-only and says code is under preparation, so released `Δe`/EMA/pruning traces and `η`/`μ` sensitivity remain unavailable for reproduction.
- SkillShapley/BAES is now primary-verified as a concrete adaptive coalition-audit backend: `B=3n^2`, warmup `R=floor(0.4B)`, three fixed benchmark instances per configuration, ranking-change warmup stop, then NSE-slope adaptive stop with minimum stratum coverage. Under the same 99 unique-configuration budget, BAES Phase 1 yields 206 reusable one-flip edges versus 115 unique MC permutation observations.
- BAES finite-budget estimates are explicitly biased approximations optimized for ranking recovery; fewer configurations do not guarantee proportional token savings.
- Dual-Layer Agentic Memory provides direct evidence for a cost-aware small-to-large write router: easy memory-admission cases are resolved by a 1.7B router and only ~39.7–49.0% are escalated to 8B under the reported operating points.
- Exact-table correction: the most aggressive SFT point stores 32.08% and achieves 89.77% EM = ~97.27% of Full Store 92.29%; the >98% retention point is 90.71% at 47.85% storage. Do not treat `68% pruning + >98% retention` as one identical configuration.
- SFT consolidation creates direct interference: 1,752 previously `non-write` facts become `write-update`, so post-consolidation re-routing/revalidation is required.
- Agent Skills Can Be Harmful adds software-agent cost evidence: among 182 high-confidence efficiency regressions, 114 are Excessive Procedure, including 67 Excessive Verification and 30 Heavy Implementation Pipeline. Skill cost includes induced trajectory work, not prompt length alone.
- Revised hypothesis: hard invalidation -> cheap triage -> cost-aware escalation -> paired marginal gain when available -> EMA/hysteresis -> adaptive BAES/coalition audit for unresolved high-value cases -> repair/retire/suppress -> optional consolidation -> post-consolidation revalidation -> activation-boundary validation.
- A unified controller choosing across `{no-op, cheap sensor, paired counterfactual, coalition audit, repair}` under one matched compute budget and reporting final software/API-agent outcome plus audit/repair cost remains unresolved.

Exact continuation:
1. Search for the unified value-of-information controller above; distinguish memory admission from post-admission repair.
2. Search for Dual-Layer Memory code/follow-up artifacts and independent reproduction after acceptance; preserve the operating-point correction.
3. Search for SkillShapley/BAES code or diagnostics and test false-stop behavior under rare interactions if artifacts appear.
4. Continue Coalition-Aware Skill Reliability for CASS coalition counts, u-SMCO stop/mask criterion and audit cost; compare against BAES under matched budgets.
5. Search for post-consolidation regression tests that detect parametric interference and re-externalize newly forgotten facts.
6. Continue the common-replicate admission-gate × post-admission-maintenance four-cell search, Repo2Skill-Evo/GSE replay cost, hidden semantic-lineage repair, rollback-target selector comparisons, and decision-influence audits under fixed controls.
7. Preserve exact tested scope and a nonempty frontier; checkpoints/findings are never global completion.

Future runs should resolve a fresh SHA-only control tuple before semantic work and read this pointer first, followed only by the minimum own predecessor material needed for unresolved frontier continuity.
