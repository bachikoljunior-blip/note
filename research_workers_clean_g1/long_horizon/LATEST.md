# Long Horizon clean_g1 — latest pointer

Authoritative latest checkpoint for this namespace:
`research_workers_clean_g1/long_horizon/CHECKPOINT_2026-08-27T120344JST_VOI_CONTROL_AND_COALITION_RELIABILITY.md`

Immediate predecessor:
`research_workers_clean_g1/long_horizon/CHECKPOINT_2026-08-27T110556JST_COST_AWARE_ROUTING_AND_SHAPLEY_AUDIT.md`

Control snapshot frozen for this semantic invocation:
- root control revision: `11`
- role config revision: `5`
- frozen source main SHA: `1d05c57172c10ea7fa9e14b119c3f2195fdcf0c7`
- root blob: `bf7b8c7f6971c0ec2f3fa7a8d53dca1f88ac50a3`
- role config blob: `268523da20c78ce3091344c492ad3d51f6f9e667`
- pre-semantic head initially advanced from `4b409df...` to `1d05c571...`; root/config were refetched before semantic work and the second SHA-only lookup matched `1d05c571...`. Later repository movement was write-safety only.

Current synthesis delta:
- Inference-Time Budget Control for LLM Search Agents gives direct evidence that one controller can choose among heterogeneous actions (retrieval/decomposition/commit) by state- and remaining-budget-dependent marginal value under matched hard tool/token caps. This supports the control structure, not direct transfer of the QA-specific score to skill maintenance.
- Coalition-Aware Skill Reliability shows a bank-level gate accepted on `+0.006` while the newly admitted skill later measured `-0.005` and an incumbent carried `+0.084`; reported gate margins are only `0.006–0.02` while a 314-paired-query single-skill audit resolves only about `±0.04`. Expensive causal audits can therefore be conceptually correct yet too coarse to decide tiny online margins.
- CASS is a bounded coalition-level admission signal rather than full per-skill Shapley attribution; detailed BAES-like attribution should remain a separate expensive localization backend.
- u-SMCO reinforces that source admission and target-domain activation are separate validity decisions; skill reliability is contextual in `(skill, bank, domain)`.
- Revised controller hypothesis: `hard invalidation -> cheap state/domain triage -> estimate {decision margin, evidence resolution, expected information gain, realized audit cost} -> choose {no-op/defer, bounded coalition gate, paired counterfactual, detailed coalition attribution} -> repair/retire/suppress only when expected decision value is positive -> target-domain activation revalidation -> optional consolidation -> post-consolidation re-routing/revalidation`.
- A persistent-skill controller choosing the full action set under one matched compute budget and measuring final software/API-agent success plus audit/repair cost remains unresolved.

Exact continuation:
1. Search for metareasoning/value-of-computation controllers that choose among stop/no-op, multiple information-gathering actions and repair under one budget; separate search/QA from persistent-memory maintenance.
2. Recover exact CASS `N`, coalition-size cap `k`, outcome-weighting and u-SMCO greedy stopping/mask criterion from primary source or official code; compare realized audit calls with BAES under matched budgets.
3. Search for official repositories/artifacts for Coalition-Aware Skill Reliability, Dual-Layer Agentic Memory and SkillShapley; do not treat aggregators as release evidence.
4. Search for audit sample-size controllers tied explicitly to decision margin / CI width and report false-retire vs stale-retain trade-offs.
5. Continue post-consolidation re-externalization tests, common-replicate admission-gate × post-admission-maintenance four-cell evidence, hidden semantic-lineage repair, rollback target selectors and decision-influence audits.
6. Preserve exact tested scope and a nonempty frontier; checkpoints/findings are never global completion.

Future runs should resolve a fresh SHA-only control tuple before semantic work and read this pointer first, followed only by the minimum own predecessor material needed for unresolved frontier continuity.
