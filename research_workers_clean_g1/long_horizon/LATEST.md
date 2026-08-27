# Long Horizon clean_g1 — latest pointer

Authoritative latest checkpoint for this namespace:
`research_workers_clean_g1/long_horizon/CHECKPOINT_2026-08-27T090227JST_COALITION_VALUE_AND_RISK_GATING.md`

Immediate predecessor:
`research_workers_clean_g1/long_horizon/CHECKPOINT_2026-08-27T080243JST_VALUE_WEIGHTED_MAINTENANCE_CONTROL.md`

Control snapshot frozen for this semantic invocation:
- root control revision: `11`
- role config revision: `5`
- frozen source main SHA: `72c4b5abe2678e96c79ae2feae09cd0b02d97552`
- root blob: `bf7b8c7f6971c0ec2f3fa7a8d53dca1f88ac50a3`
- role config blob: `268523da20c78ce3091344c492ad3d51f6f9e667`
- both pre-semantic SHA-only lookups matched; later own writes or repository changes were not adopted as semantic control.

Current synthesis delta:
- OpenLoopEvolve's official public repository currently contains only a release-pending README; the paper specifies Trig, paired release gates and CanaryMonitor semantics but does not expose validated numeric trigger/degradation thresholds. Concrete OLE scheduler thresholds remain unresolved.
- Skill value is coalition- and deployment-conditioned. Coalition-Aware Skill Reliability shows that aggregate bank gains can hide negative individual/coalition contributions and that utility can reverse after domain transfer; sampled-coalition CASS and label-free u-SMCO reduce this pollution at nonzero audit cost.
- SkillForge supplies a practical cheap usage/EMA-based maintenance sensor with strong ablations and <10% reported skill-management overhead, but whole-episode reward assigned to each invoked skill is not a clean causal marginal under interacting skills.
- Financial-agent auditing shows useful self-evolution can increase exposure/unauthorized-state risk, and execution-interface mismatch can invalidate otherwise useful artifacts. Consequence and executor compatibility therefore need explicit gates rather than being collapsed into task utility.
- BASM supplies decision-time negative evidence against unconditional skill imitation: applicability/risk/avoidance/recovery boundaries are a distinct layer from admission and longitudinal maintenance.
- Revised maintenance hypothesis: use cheap continuous sensors to triage expensive coalition/counterfactual audits; prioritize audits by invalidation hazard × coalition-conditioned value-at-risk × consequence relative to audit/repair cost, with hard safety/interface constraints and uncertainty-aware abstention. This remains a hypothesis, not an observed end-to-end scheduler.
- No controlled software/API-agent study was found that jointly optimizes drift hazard, coalition-conditioned marginal value, consequence/tail risk, maintenance cost and false-edit risk under one fixed stream.

Exact continuation:
1. Search SkillForge author artifacts/code and appendix details for EMA alpha, usage half-life, review thresholds, and sensitivity/cost ablations.
2. Search Coalition-Aware artifacts/checkpoints for coalition-sample count, threshold/proxy sensitivity, u-SMCO stop criteria and cost details.
3. Search for a two-stage cheap-sensor → expensive coalition/counterfactual-audit scheduler, ideally value-of-information/audit-allocation based and evaluated on final task outcome plus audit cost.
4. Continue Repo2Skill-Evo artifact/data and GSE affected-set replay cost/ablation searches.
5. Continue the common-replicate four-cell admission-gate × post-admission-maintenance interaction search.
6. Continue multi-generation hidden semantic-lineage discovery/repair, rollback-target selector comparisons and decision-influence audits under fixed controls.
7. Preserve exact tested scope and a nonempty frontier; checkpoints/findings are never global completion.

Future runs should resolve a fresh SHA-only control tuple before semantic work and read this pointer first, followed only by the minimum own predecessor material needed for unresolved frontier continuity.
