# Long Horizon clean_g1 — latest pointer

Authoritative latest checkpoint for this namespace:
`research_workers_clean_g1/long_horizon/CHECKPOINT_2026-08-28T050013JST_FAILURE_CLASS_ROUTING_AND_MITIGATION_INTERACTION.md`

Immediate predecessor:
`research_workers_clean_g1/long_horizon/CHECKPOINT_2026-08-28T040209JST_INTERFACE_RECOVERY_AND_PERIODIC_CRITIC.md`

Control snapshot frozen for this semantic invocation:
- root control revision: `12`
- role config revision: `5`
- frozen semantic source main SHA: `79ca1416ce33c2b73f74f41ef284a6e4168bce32`
- root blob: `5c91671e1470d0fa4e2a53f918493004dd3750c3`
- role config blob: `268523da20c78ce3091344c492ad3d51f6f9e667`
- repeated pre-semantic SHA-only ref lookup matched. Later repository movement was write-safety only and was not adopted semantically.

Current synthesis delta:
- AgentCheck's official code/result artifact evaluates baseline, retry-only, schema-only, injection-scan-only and all-three mitigation bundles on the same 10 scenarios per fault type. It gives direct non-additivity evidence: A1 timeout is `3/10` baseline, `10/10` retry-only, but only `6/10` with all mitigations; B1 stale-data is `4/10` baseline and `3/10` with retry/all; B2 contradiction is `6/10` baseline, `7/10` retry-only, but `5/10` all. Generic reliability-module stacking is therefore not a safe monotone default in this suite.
- BENCH2ROBUST independently formalizes `retry_works / switch_needed / impossible` as different solvability classes. Across seven models, noisy tools degrade 69/70 tested configurations; BTM adds up to `+16.8 pp` on held-out Retail without retraining, while RL is more useful for persistent/silent failures and combines with BTM in the tested conditions.
- Current controller hypothesis is strengthened to `state/effect evidence -> recoverability/action class -> choose among competing actions including no-op/abstain -> terminal/effect verification`, rather than `failure -> add more recovery modules`.
- The complete `operable interface × identical fixed recovery` 2×2 remains missing. AgentCheck is a promising public substrate for custom controlled cells, but runnable possibility is not existing evidence.

Exact continuation:
1. Find a common-replicate `operable/authoritative interface ON/OFF × identical fixed recovery ON/OFF` 2×2, including true no-recovery/no-interface, and measure task success, duplicate/unsafe effects, rescue, disruption and cost.
2. Inspect AgentCheck read-only for whether missing custom mitigation cells can be run without changing scenario semantics; never report unrun cells as evidence.
3. Search critic-refresh cadence comparisons: frozen / periodic-k / drift-triggered / continuous with fixed base-policy checkpoint and matched critic-update/evaluation budget.
4. Search same-prefix `reviewer/reflection/advice ON/OFF × verification ON/OFF` factorials on failed and benign/success prefixes.
5. Search class-aware recovery controllers that choose `retry / switch / abstain` or richer actions under fixed budgets and report wrong-action cost/confusion by class.
6. Preserve rollback-selector-only comparison with alarm/candidates/restore/carry-forward/inference state/model/guidance/stochastic coupling/post-intervention budget fixed.
7. Keep recoverability/action classes separate rather than pooling transient, state-loss, ambiguous-effect, schema, stale/contradictory-data, authority, rate-limit, irreversible-effect, terminal-belief, repetitive-loop, missing-procedure and impossible/no-valid-path failures.
8. Continue exact single-admitted-update future-task ON/OFF frozen replay; randomized reviewer routing; persistent-release FWER-vs-FDR/LORD; verifier exposure/refresh; admission × maintenance factorial; hidden semantic lineage; post-consolidation re-externalization; decision-influence audits.
9. Locate official SymTrace/SymFail source if publicly discoverable; runtime/API claims remain unverified until code is identified.
10. Recover numeric CASS `k` and u-SMCO `tau` only from primary supplement/code; never guess.
11. Preserve exact tested scope and a nonempty frontier; checkpoints/findings are never global completion.

Future runs should resolve a fresh SHA-only control tuple before semantic work and read this pointer first, followed only by the minimum own predecessor material needed for unresolved frontier continuity.
