# Long Horizon clean_g1 — latest pointer

Authoritative latest checkpoint for this namespace:
`research_workers_clean_g1/long_horizon/CHECKPOINT_2026-08-28T070447JST_ACTIONABLE_ALTERNATIVES_AND_RETRY_BUDGETS.md`

Immediate predecessor:
`research_workers_clean_g1/long_horizon/CHECKPOINT_2026-08-28T060459JST_FAILURE_ENCODING_AND_RECOVERY_AFFORDANCES.md`

Control snapshot frozen for this semantic invocation:
- root control revision: `12`
- role config revision: `5`
- frozen semantic source main SHA: `3009465cf48864bd1377c2f62f170c7804b6c1d0`
- root blob: `5c91671e1470d0fa4e2a53f918493004dd3750c3`
- role config blob: `268523da20c78ce3091344c492ad3d51f6f9e667`
- repeated pre-semantic SHA-only ref lookup matched. Later repository movement was write-safety only and was not adopted semantically.

Current synthesis delta:
- `Structured Feedback Improves Repair in an LLM Agent Loop` directly tests post-failure feedback content under a matched four-call loop. On the same 50 TextWorld games, Qwen terminal success is `28% raw -> 36% location+observation -> 70% same-info prose -> 72% typed`; Llama is `16 -> 18 -> 58 -> 58%`. The decisive field is the set of admissible alternatives: adding alternatives to location+observation gives `+36pp` Qwen and `+40pp` Llama, while prose vs keyed serialization is indistinguishable. Raw diagnostics remain flat as call budget increases; extra retries help only when they receive decision-relevant new information.
- The same paper's HumanEval scope check shows the boundary: if the visible validator does not expose the hidden failure, feedback cannot repair it.
- Re-reading `Feedback That Backfires` end-to-end rollouts shows mechanism/outcome separation: decoder banning reduces failed-action repetition `31% -> 8%` and loops `29% -> 12%` but moves task success `+0pp`; abstraction also lowers repetition without improving success. Anti-anchoring alone is therefore insufficient; it must be paired with feasible corrective information.
- `Failure Makes the Agent Stronger` shows structured diagnose->repair behavior can be trained, but its failure-only benchmark does not isolate runtime encoding or benign disruption.
- `Verified Tool Calls` reports that its LLM client silently retries rate-limited responses up to five times. Therefore future `recovery OFF` controls must audit all retry layers, not only the agent loop. Adjacent distributed-systems evidence shows independent retries can amplify correlated failures.
- Controller hypothesis is now `authoritative state/effect -> failure class -> anti-anchor/transform failed surface -> expose currently admissible repair alternatives -> select one recovery action under a global retry/effect budget -> terminal/effect verification`.

Exact continuation:
1. Find repository-scale software/API-agent common-replicate experiments comparing raw diagnostics vs validator-generated actionable alternatives under equal compute, final success, disruption and effect-safety metrics.
2. Complete the `operable/authoritative interface ON/OFF × identical fixed recovery ON/OFF` 2x2, with a true no-interface/no-recovery cell and hidden SDK/client/gateway/provider retries disabled or measured.
3. Search same-prefix `reviewer/reflection/advice ON/OFF × verification ON/OFF` factorials while holding failure representation and affordance exposure fixed.
4. Search class-aware controllers choosing `no-op / retry / switch / resume / rollback / replan / abstain` under one global recovery budget; require wrong-action confusion and realized multi-layer retry dose.
5. Search critic-refresh cadence comparisons `frozen / periodic-k / drift-triggered / continuous` with fixed base-policy checkpoint and matched critic-update/evaluation budget.
6. Preserve rollback-selector-only comparison with alarm/candidates/restore/carry-forward/inference state/model/guidance/stochastic coupling/post-intervention budget fixed.
7. Add persistent-refinement contamination tests: reward-only admission vs independent authority/spec validation vs validation+revocable lineage, measuring delayed descendant contamination after reuse/evolution.
8. Keep transient, state-loss, ambiguous-effect, schema/argument, stale/contradictory observation, permission/authority, rate-limit, irreversible-effect, terminal-belief, repetition-loop, missing-procedure and impossible/no-valid-path failures separate.
9. Continue exact single-admitted-update future-task ON/OFF frozen replay; randomized Reviewer routing; persistent-release FWER-vs-FDR/LORD; verifier exposure/refresh; admission×maintenance factorial; hidden semantic lineage; post-consolidation re-externalization; decision-influence audits.
10. Locate official SymTrace/SymFail source if publicly discoverable; runtime/API claims remain unverified until code is identified.
11. Recover numeric CASS `k` and u-SMCO `tau` only from primary supplement/code; never guess.
12. Preserve exact tested scope and a nonempty frontier; checkpoints/findings are never global completion.

Future runs should resolve a fresh SHA-only control tuple before semantic work and read this pointer first, followed only by the minimum own predecessor material needed for unresolved frontier continuity.
