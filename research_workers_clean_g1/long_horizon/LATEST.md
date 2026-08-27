# Long Horizon clean_g1 — latest pointer

Authoritative latest checkpoint for this namespace:
`research_workers_clean_g1/long_horizon/CHECKPOINT_2026-08-28T040209JST_INTERFACE_RECOVERY_AND_PERIODIC_CRITIC.md`

Immediate predecessor:
`research_workers_clean_g1/long_horizon/CHECKPOINT_2026-08-28T030239JST_FROZEN_CRITIC_DIRECT_ABLATION.md`

Control snapshot frozen for this semantic invocation:
- root control revision: `12`
- role config revision: `5`
- frozen semantic source main SHA: `a4c48b00398181c120612ebc1521572760f6101e`
- root blob: `5c91671e1470d0fa4e2a53f918493004dd3750c3`
- role config blob: `268523da20c78ce3091344c492ad3d51f6f9e667`
- repeated pre-semantic SHA-only ref lookup matched. Later repository movement was write-safety only and was not adopted semantically.

Current synthesis delta:
- TEMPO independently shows that a frozen critic initially tracks an evolving policy but plateaus after roughly 100 iterations, while periodic labeled-data recalibration sustains improvement. This reinforces critic/reviewer staleness as a longitudinal problem, but TEMPO is reasoning TTT rather than a tool agent and does not compare refresh cadences or matched update budgets.
- AFT-Bench isolates failure-class-specific interface mechanisms: resumable invocation and durable state each produce a pooled `+1.0000` recovery effect under their matched interruption/state-loss workloads; effect semantics and verification address different ambiguity classes and are more policy/model dependent. The desired interface × fixed-recovery complete 2×2 remains absent.
- Verified Tool Calls' three-arm ablation has retry-only about `58%` success / `42%` duplicates, verify-only `80% / 20%`, and verify-before-retry `72% / 28%`. Retry after verification is therefore harmful in that condition, but the missing no-verification/no-retry fourth cell prevents a full interaction estimate.
- VLAA-GUI supplies independent GUI-agent evidence that terminal verification, loop recovery and procedural search are distinct load-bearing components: WindowsAgentArena/Gemini 3 Flash at 50 steps is `60.4%` full, `51.3%` minus verifier, `52.6%` minus loop breaker, `49.4%` minus search. These are one-at-a-time ablations, not same-prefix or factorial interaction evidence.

Exact continuation:
1. Find a common-replicate `operable/authoritative interface ON/OFF × identical fixed recovery ON/OFF` 2×2, including the true no-recovery/no-verification cell; measure task success, duplicate/unsafe effects, rescue, disruption and cost.
2. Search same-base-policy-checkpoint critic cadence comparisons: frozen / periodic-k / event- or drift-triggered / continuous, with matched total critic-update/evaluation budget and final outcome/disruption/cost.
3. Search same-prefix `reviewer/reflection/advice ON/OFF × verification ON/OFF` factorials on failed and benign/success prefixes.
4. Read-only inspect public implementations of Verified Tool Calls / VLAA-GUI to see whether the missing cells are experimentally available; runnable possibility is not evidence.
5. Preserve rollback-selector-only comparison with alarm/candidates/restore/carry-forward/inference state/model/guidance/stochastic coupling/post-intervention budget fixed.
6. Keep recoverability/action classes separate rather than pooling transient, state-loss, ambiguous-effect, schema, authority, rate-limit, irreversible-effect, terminal-belief, repetitive-loop and missing-procedure failures.
7. Continue exact single-admitted-update future-task ON/OFF frozen replay; randomized reviewer routing; persistent-release FWER-vs-FDR/LORD; verifier exposure/refresh; admission × maintenance factorial; hidden semantic lineage; post-consolidation re-externalization; decision-influence audits.
8. Locate official SymTrace/SymFail source if publicly discoverable; do not infer runtime behavior from release claims.
9. Recover numeric CASS `k` and u-SMCO `tau` only from primary supplement/code; never guess.
10. Preserve exact tested scope and a nonempty frontier; checkpoints/findings are never global completion.

Future runs should resolve a fresh SHA-only control tuple before semantic work and read this pointer first, followed only by the minimum own predecessor material needed for unresolved frontier continuity.
