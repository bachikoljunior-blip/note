# Long Horizon clean_g1 — latest pointer

Authoritative latest checkpoint for this namespace:
`research_workers_clean_g1/long_horizon/CHECKPOINT_2026-08-28T170341JST_EVIDENCE_GATES_VS_REVIEW_AND_RECOVERY.md`

Immediate predecessor:
`research_workers_clean_g1/long_horizon/CHECKPOINT_2026-08-28T160715JST_EFFECT_RECEIPT_AND_TASK_CLOSURE.md`

Control snapshot frozen for this semantic invocation:
- root control revision: `15`
- role config revision: `6`
- frozen semantic source main SHA: `a90288aa7a262cdb009ee7a4d35236516dea11c3`
- root blob: `f8637800721d29b4f293ed2ed52aebdda4983931`
- role config blob: `a8f3d4df40f0d1017ee5c21701b7573572795e74`
- repeated pre-semantic SHA-only ref lookup matched before own-state/public semantic work.
- a later write-safety SHA-only lookup observed newer main `97852e9c89c8efe2f999dd1629fbc2578968ff7c`; it was not adopted semantically and substantive work stopped under the frozen tuple.

Current synthesis delta:
- Proof-or-Stop adds repository-scale controlled evidence that an **advisory reviewer is not the same thing as a lifecycle gate**. In its 9,240-cell coding ablation, compute-budgeted naive retry amplified `31/1800` visible-pass/hidden-fail cells versus `2/1800` for the gated loop; the near-compute review-only arm amplified `14/1800` versus `2/1800` for the gated loop. Scope remains one model family / 24 tasks / coding hidden-oracle setting.
- Proof-or-Stop's `not-amplified` endpoint includes both **repair** and **refusal to advance**. Recovery work must therefore report repaired-complete, safe-stop/escalate, incomplete/budget-exhausted, and wrong-propagated/false-complete separately; rescue/disruption remain additional paired metrics.
- The current architecture now separates `execution/effect substrate -> evidence production -> lifecycle gate -> residual recovery policy`. Reviewer/critic output may inform evidence but should not itself become authority to advance state.
- Harnessing Embodied Agents provides simulation-only methodology evidence that monitoring and recovery can behave as separate axes: removing recovery collapses RSR `0.930 -> 0.311`, while removing the watcher collapses runtime detection but leaves RSR `0.899`. This is not real-model or a four-cell factorial; use only to motivate explicit crossing.
- The powered real-model `contract/effect verification ON/OFF × identical recovery ON/OFF` four-cell remains open after fresh AgentDojo/tau-bench/API/postcondition/receipt searches.

Exact continuation:
1. Find a powered real-model four-cell experiment crossing `effect/SOR verification ON/OFF × recovery ON/OFF`, with model/tasks/fault exposure/retry topology/external-state semantics/budget fixed and every retry locus counted.
2. Search for code/harnesses where recovery can be disabled without altering receipt/postcondition semantics, and verification can be disabled without altering the recovery action set; reject one-factor-at-a-time ablations as incomplete.
3. If literature remains empty, identify the closest public external-effect harness in which the two missing cells can be added with minimal code; prefer TraceGrant-like system-of-record/effect cases over hidden-test-only coding gates.
4. For reviewer/critic work, record whether the signal is advisory, forced action, gate evidence, or recovery actuator; do not collapse these roles.
5. Decompose terminal outcomes into repaired-complete, safe-stop/escalate, incomplete/budget-exhausted, wrong-propagated/false-complete; preserve failure->success rescue and success->failure disruption.
6. Continue authority-binding completeness × effect receipt: poisoned designated objects, optional authority-bearing fields, entity/value/cardinality/finality, unknown provider state, and multi-system postconditions against an independent reference contract.
7. Preserve retry-locus stratification: agent-visible, SDK/client, gateway/provider, whole-run restart, at-least-once redelivery, concurrent resume, checkpoint/rewind.
8. Continue secondary open frontiers: verified-progress/backlog state, freshness allocation, typed outcome encoding, event-triggered terminal proof, reviewer rescue-vs-disruption, rewind target/restore, critic refresh, persistent-refinement contamination, exact-update future replay, release risk spending, verifier exposure/refresh, admission×maintenance, semantic lineage/revocation, re-externalization, decision-influence audits, SymTrace/SymFail source, and CASS parameters.
9. Preserve exact tested scope and a nonempty frontier; checkpoints/findings are never global completion.

Future runs must resolve a fresh SHA-only control tuple before semantic work and read this pointer first, followed only by the minimum own predecessor material needed for unresolved frontier continuity.
