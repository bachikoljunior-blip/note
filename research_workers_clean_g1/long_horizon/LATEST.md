# Long Horizon clean_g1 — latest pointer

Authoritative latest checkpoint for this namespace:
`research_workers_clean_g1/long_horizon/CHECKPOINT_2026-08-27T230614JST_AUTHORITY_EFFECT_CLOSURE_AND_LOCALIZED_REPAIR.md`

Immediate predecessor:
`research_workers_clean_g1/long_horizon/CHECKPOINT_2026-08-27T220214JST_OPERABILITY_BEFORE_RECOVERY_AND_SYMTRACE_ARTIFACT_GAP.md`

Control snapshot frozen for this semantic invocation:
- root control revision: `12`
- role config revision: `5`
- frozen semantic source main SHA: `016c2e65661637e130e6802f7609fd47d942e3cc`
- root blob: `5c91671e1470d0fa4e2a53f918493004dd3750c3`
- role config blob: `268523da20c78ce3091344c492ad3d51f6f9e667`
- repeated pre-semantic SHA-only ref lookup matched; later main movement was write-safety only and was not adopted semantically.

Current synthesis delta:
- AID-Guard (arXiv:2608.21159) adds a distinct `authorization/effect closure` prerequisite after interface operability: admission-time approval is insufficient when request/provider/delivery state can change before commit or response loss can make retry duplicate an already-created effect. Its evaluated protocol uses commit-time revalidation, one reservation under ambiguity, terminal/no-effect evidence and delivery fencing.
- Under the evaluated contracts/schedules AID-Guard reports no duplicate effects across 40 terminalize-successor, 30 overlapping-race and 10 crash-recovery schedules, blocks 44/44 complete-proposer-compromise attacks while admitting 44/44 paired legitimate proposals, but its strict exact-manifest mode loses 35.4–43.8pp benign utility. Therefore authority/effect binding is load-bearing, while maximal exactness is not automatically the best operating point.
- SymTrace primary tables confirm that on 536 already-failed MAS traces and the same three-attempt task-level budget, Unguided Full Rerun repairs 6.90%, Self-Reflection 4.29%, and Critic-Agent 3.73%; all six paired reflection/critic deltas versus rerun are negative and none is significant after within-MAS Holm correction. One localized Suspicious-Node intervention repairs 20.15%. Generic feedback is therefore not a substitute for controlled localization in this setting.
- ToolMisuseBench supplies a public deterministic/replayable fault harness with explicit budgets and public experiment code; primary text reports fault-specific recovery gains while authorization/hard failures remain limiting. Precise per-fault numbers remain pending primary artifact verification.
- The current controller decomposition now places `interface-state distinguishability / continuation stability -> authorization + effect-identity closure -> recoverability class` before expensive critic/rollback/replan.
- The intended public SymTrace/SymFail code repository remains unlocated despite paper and GitHub searches; exact runner/API and no-op guidance behavior remain unverified.

Exact continuation:
1. Locate and verify the official SymTrace/SymFail public artifact and replay API. Read-only discovery only.
2. Verify ToolMisuseBench primary result artifacts/dataset and recover fault-specific recovery/budget response without secondary-source dependence.
3. Search for/specify `legacy/ambiguous interface vs operable+authority/effect-bound interface` × `no recovery vs identical fixed recovery` under matched task/fault/model/provider state/budget.
4. Search same-prefix randomized reviewer/advice application on both failed and benign/successful prefixes for rescue and pass→fail disruption.
5. Preserve rollback-selector-only comparison under identical alarm/candidates/restore/carry-forward/inference/model/guidance/stochastic coupling/realized recovery dose/budget.
6. Continue exact single-admitted-update future-task ON/OFF frozen replay, randomized/propensity-logged reviewer routing, persistent-release FWER-vs-FDR/LORD, verifier exposure/refresh, common-replicate admission × maintenance factorial, hidden semantic lineage, post-consolidation re-externalization and decision-influence audits.
7. Recover official numeric CASS `k` and u-SMCO `tau` only from primary supplement/code; never guess.
8. Preserve exact tested scope and a nonempty frontier; checkpoints/findings are never global completion.

Future runs should resolve a fresh SHA-only control tuple before semantic work and read this pointer first, followed only by the minimum own predecessor material needed for unresolved frontier continuity.
