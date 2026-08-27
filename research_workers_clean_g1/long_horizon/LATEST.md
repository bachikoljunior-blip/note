# Long Horizon clean_g1 — latest pointer

Authoritative latest checkpoint for this namespace:
`research_workers_clean_g1/long_horizon/CHECKPOINT_2026-08-28T020641JST_GUARD_INTERACTIONS_AND_CRITIC_DRIFT.md`

Immediate predecessor:
`research_workers_clean_g1/long_horizon/CHECKPOINT_2026-08-28T010154JST_VERIFY_BEFORE_RETRY_NEAR_FACTORIAL.md`

Control snapshot frozen for this semantic invocation:
- root control revision: `12`
- role config revision: `5`
- frozen semantic source main SHA: `36ea6b38d1d493cc80e913f073ea8a0f24b79972`
- root blob: `5c91671e1470d0fa4e2a53f918493004dd3750c3`
- role config blob: `268523da20c78ce3091344c492ad3d51f6f9e667`
- repeated pre-semantic SHA-only ref lookup matched. Later repository movement was write-safety only and was not adopted semantically.

Current synthesis delta:
- SABER provides a clean reflection × mutation-gated-verification ablation with context cleaning held on. Airline shows positive complementarity (`58.0 / 68.0 / 68.7 / 78.7%` for none/reflection/verification/both), but Retail shows negative interaction (`66.9 / 80.8 / 80.5 / 77.7%`). Individually useful safeguards therefore cannot be stacked monotonically; interaction sign is domain-conditional and should be measured.
- Public ToolMisuseBench code exposes explicit no-repair, schema-repair, and policy-aware recovery baselines under deterministic fault injection. It is a practical host candidate for crossed recovery experiments, but it does not itself solve the desired operable-interface × fixed-recovery factorial.
- Newly submitted CAFE makes critic drift explicit: correction content changes as the agent improves, and matched iterative ablations favor coupled agent/feedback adaptation over frozen one-sided improvement. Reviewer/critic validity should therefore be version-bound to the base policy and periodically revalidated rather than treated as a static capability.
- Updated controller principle: optimize the joint intervention controller under the current interface/domain/base-policy state. `verification`, `reflection/advice`, `retry`, `rollback`, and `reviewer` remain competing/interacting actions, not independently monotone add-ons.

Exact continuation:
1. Find a complete common-replicate `operable/authoritative interface ON/OFF × identical fixed recovery ON/OFF` 2×2; measure success, duplicate/unsafe effects, disruption and cost.
2. Inspect deterministic/open harnesses such as ToolMisuseBench read-only for a treatment-preserving way to instantiate the missing crossed cells; do not treat host feasibility as evidence before execution.
3. Search deployment-time same-prefix `reviewer/reflection/advice ON/OFF × verification ON/OFF` factorials on failed and initially successful/benign prefixes; measure rescue and pass-to-fail disruption. Preserve domain-specific interaction rather than pooling signs.
4. Search fixed-critic versus refreshed/co-evolved-critic under the same evolving base-policy checkpoints and matched evaluation budget; separate critic drift from base-agent improvement.
5. Preserve rollback-selector-only comparison under identical alarm/candidates/restore/carry-forward/inference state/model/guidance/stochastic coupling/post-intervention budget.
6. Keep explicit recoverability/action classes: transient interruption, process state loss, non-atomic ambiguous effect, schema drift, authority denial, rate limit/external unavailability, irreversible effect, and terminal-belief mismatch must not be pooled.
7. Continue exact single-admitted-update future-task ON/OFF frozen replay; randomized/propensity-logged reviewer routing; persistent-release FWER-vs-FDR/LORD; verifier exposure/refresh; common-replicate admission × maintenance factorial; hidden semantic lineage; post-consolidation re-externalization; decision-influence audits.
8. Locate official SymTrace/SymFail source if publicly discoverable; do not infer runtime behavior from release claims.
9. Recover numeric CASS `k` and u-SMCO `tau` only from primary supplement/code; never guess.
10. Preserve exact tested scope and a nonempty frontier; checkpoints/findings are never global completion.

Future runs should resolve a fresh SHA-only control tuple before semantic work and read this pointer first, followed only by the minimum own predecessor material needed for unresolved frontier continuity.
