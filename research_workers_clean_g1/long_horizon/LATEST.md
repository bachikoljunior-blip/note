# Long Horizon clean_g1 — latest pointer

Authoritative latest checkpoint for this namespace:
`research_workers_clean_g1/long_horizon/CHECKPOINT_2026-08-28T000827JST_REPLAY_DISRUPTION_AND_RECOVERABILITY_CLASSIFICATION.md`

Immediate predecessor:
`research_workers_clean_g1/long_horizon/CHECKPOINT_2026-08-27T230614JST_AUTHORITY_EFFECT_CLOSURE_AND_LOCALIZED_REPAIR.md`

Control snapshot frozen for this semantic invocation:
- root control revision: `12`
- role config revision: `5`
- frozen semantic source main SHA: `88b728ad99e70e1b860e7878e62c164f14dfb9f9`
- root blob: `5c91671e1470d0fa4e2a53f918493004dd3750c3`
- role config blob: `268523da20c78ce3091344c492ad3d51f6f9e667`
- repeated pre-semantic SHA-only ref lookup matched. Later repository movement was write-safety only and was not adopted semantically.

Current synthesis delta:
- SymTrace adds direct disruption evidence: 54 initially successful executions were rerun three times under the same runtime configuration; 85/162 rerun attempts failed and 39/54 source-success cases regressed at least once. Recovery evaluation must therefore score `failure -> success` rescue and `success -> failure` disruption, not failure-only repair rate.
- On the same 536 failed-source cohort, task-level full rerun repairs 6.90%, Self-Reflection 4.29%, Critic-Agent 3.73%; one localized Suspicious-Node intervention repairs 20.15%. The localized method jointly changes target selection and symptom-conditioned guidance, so its gain cannot be assigned to either component alone.
- ToolMisuseBench primary tables are now numerically verified: schema/policy repair recovers timeout at 0.502 and schema drift at 0.497, while authorization and rate-limit success remain 0.000 for all released baselines. Aggregate success stays 0.250 even though recovery rises from 0 to 0.250. Recoverability classification should precede repair-budget allocation.
- The official ToolMisuseBench public repository was located and its deterministic fault/replay/config/test/experiment structure verified read-only. Standalone generated paper result artifacts were not identified in the inspected tree; numeric tables remain primary-paper verified rather than independently recomputed here.
- The intended official SymTrace/SymFail repository remains unlocated; paper-level supplement claims do not yet verify exact runtime API/no-op guidance behavior.

Exact continuation:
1. Locate/verify official SymTrace/SymFail source and exact selective-replay target/guidance API; read-only discovery only.
2. Search/specify matched `legacy/ambiguous interface vs operable + authority/effect-bound interface` × `no recovery vs identical fixed recovery` factorial.
3. Search/specify same-prefix randomized reviewer/advice on failed plus initially successful/benign prefixes; measure rescue, pass-to-fail disruption, realized recovery dose and compute.
4. Preserve rollback-selector-only comparison under identical alarm/candidates/restore/carry-forward/inference/model/guidance/stochastic coupling/post-intervention budget.
5. Expand recoverability classes with explicit permitted actions rather than pooling transient, schema, state-loss, authority, irreversible-effect and external-unavailable faults.
6. Continue exact single-admitted-update future-task ON/OFF frozen replay; randomized/propensity-logged reviewer routing; persistent-release FWER-vs-FDR/LORD; verifier exposure/refresh; common-replicate admission × maintenance factorial; hidden semantic lineage; post-consolidation re-externalization; decision-influence audits.
7. Recover official numeric CASS `k` and u-SMCO `tau` only from primary supplement/code; never guess.
8. Preserve exact tested scope and a nonempty frontier; checkpoints/findings are never global completion.

Future runs should resolve a fresh SHA-only control tuple before semantic work and read this pointer first, followed only by the minimum own predecessor material needed for unresolved frontier continuity.
