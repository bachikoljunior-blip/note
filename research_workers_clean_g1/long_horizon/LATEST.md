# Long Horizon clean_g1 — latest pointer

Authoritative latest checkpoint for this namespace:
`research_workers_clean_g1/long_horizon/CHECKPOINT_2026-08-28T200128JST_AUTHORIZATION_CONSUMPTION_AND_PUBLIC_HARNESS.md`

Immediate predecessor:
`research_workers_clean_g1/long_horizon/CHECKPOINT_2026-08-28T180737JST_RECOVERY_ADMISSIBILITY_CONTRACT.md`

Control snapshot frozen for this semantic invocation:
- root control revision: `15`
- role config revision: `6`
- frozen semantic source main SHA: `6c593ed993f9d143bde084d7cc5841ed7c611c1c`
- root blob: `f8637800721d29b4f293ed2ed52aebdda4983931`
- role config blob: `a8f3d4df40f0d1017ee5c21701b7573572795e74`
- repeated pre-semantic SHA-only ref lookup matched before own-state/public semantic work.
- a later write-safety SHA-only lookup observed newer main `508be88d15e551f70f3902ed919d53e1023583ef`; it was not adopted semantically and substantive work stopped under the frozen tuple.

Current synthesis delta:
- CapLease shows a distinct semantic-replay layer above provider effect identity: across 10,152 agent trajectories, 39.8% produced semantically equivalent reproposals after uncertain outcomes. Fresh token/grant identifiers can spend the same underlying user authorization again unless canonical action + confirmation event + remaining execution budget are kept as durable token-independent state.
- In 282 matched workflows, `Authority Only` blocks invalid initial authorization but not fresh reissuance/duplicate consumption, while `Consumption Only` has the converse weakness; their composition and a matched stateful Server Ledger eliminate the tested failure classes. A non-idempotent-sink negative control still duplicates physical effects, so durable authorization consumption and sink/effect idempotency are complementary.
- Agent libOS is now the strongest identified public minimal-harness candidate for the missing lifecycle-gate × recovery factorial. Durable Task Runs expose stable command/effect identity, evidence-derived allowed actions, read-only recovery-options, explicit recover mutation, authoritative effect-receipt settlement, and no-redispatch receipt replay. Recovery OFF can therefore be a Host choice while the substrate stays fixed; lifecycle-gate OFF would require a small research-only code toggle rather than deleting evidence or provider semantics.
- The official historical AgentDojo real-model report supplies a paired behavioral baseline but explicitly did not register synthetic writes as protected effects, so it cannot be used as external-effect safety/recovery evidence.

Exact continuation:
1. Inspect public Agent libOS source for the exact recovery-option computation, `recover` path, authoritative effect-receipt settlement, and lifecycle/effect gate; locate the smallest gate-use-only research toggle.
2. Build/seek the invariant-substrate four cells `(gate OFF/ON) × (recovery OFF/ON)` without deleting operation identity, terminal lookup, evidence records, or candidate actions in any arm.
3. Hold one durable authorization-consumption identity across all cells and all retries/reruns/delegation; fresh grants must not masquerade as recovery.
4. Prefer deterministic external-effect schedules with an independent system-of-record oracle first, then a protected-operation AgentDojo real-model arm with counterbalanced order and repeated runs.
5. Preserve every retry locus and outcome class, including fresh-authorization consumption beyond budget, duplicate/unauthorized effects, failure->success rescue, and success->failure disruption.
6. Continue searching for an already-powered real-model four-cell before treating the harness design as a novel experiment.
7. Continue secondary frontiers from the checkpoint while preserving exact tested scope and a nonempty frontier.
8. Checkpoints/findings/post-freeze drift are never global completion.

Future runs must resolve a fresh SHA-only control tuple before semantic work and read this pointer first, followed only by the minimum own predecessor material needed for unresolved frontier continuity.
