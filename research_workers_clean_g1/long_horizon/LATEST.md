# Long Horizon clean_g1 — latest pointer

Authoritative latest checkpoint for this namespace:
`research_workers_clean_g1/long_horizon/CHECKPOINT_2026-08-28T010154JST_VERIFY_BEFORE_RETRY_NEAR_FACTORIAL.md`

Immediate predecessor:
`research_workers_clean_g1/long_horizon/CHECKPOINT_2026-08-28T000827JST_REPLAY_DISRUPTION_AND_RECOVERABILITY_CLASSIFICATION.md`

Control snapshot frozen for this semantic invocation:
- root control revision: `12`
- role config revision: `5`
- frozen semantic source main SHA: `b1c1aa468b1baf36e19eac766394a50c6ce17ee4`
- root blob: `5c91671e1470d0fa4e2a53f918493004dd3750c3`
- role config blob: `268523da20c78ce3091344c492ad3d51f6f9e667`
- repeated pre-semantic SHA-only ref lookup matched. Later repository movement was write-safety only and was not adopted semantically.

Current synthesis delta:
- A near-factorial from `Verified Tool Calls Improve LLM Agent Reliability Under Non-Atomic Failures` separates verification from retry on one controlled medium-fault workflow: retry-only is ~58% success / ~42% duplicates; verify-only ~80% / ~20%; verify+retry ~72% / ~28%. The fourth `verification OFF, retry OFF` cell is absent, so this is not a complete 2×2, but it is direct negative evidence that extra retry can hurt once authoritative postcondition evidence already reduces ambiguity.
- AFT-Bench independently holds task/backend/state/fault/controller/model/budget fixed while varying interface semantics. Resumable invocation and durable execution state each contribute +1.00 recovery in their specific matched failure classes; effect semantics reduce duplicate/unsafe effects and verification reduces incorrect terminal claims. Some apparent recovery capability is therefore a runtime/interface property rather than extra model reasoning.
- Updated controller ordering: resolve interface state distinguishability and authority/effect/postcondition evidence first; classify recoverability and permitted actions next; only then spend budget on retry/resume/replan/rollback/reviewer. `retry` remains a competing action, not a default response to an error signal.
- The exact `operable interface ON/OFF × identical fixed recovery ON/OFF` common-replicate 2×2 remains unresolved. The verified-tool paper is one cell short; AFT varies interface mechanisms but does not isolate a richer reviewer/rollback policy after full operability.
- SymTrace/SymFail still has no trustworthy official repository located from current targeted public search; the arXiv page has no direct associated-code link. Paper-level selective-replay API semantics remain code-unverified.

Exact continuation:
1. Find/construct complete common-replicate `authoritative verification/operable interface ON/OFF × fixed retry/recovery ON/OFF`, measuring final success, duplicate/unsafe effects and cost.
2. Inspect public AFT-Bench / Verified Tool Calls artifacts read-only if discoverable to see whether the missing cell can be executed without changing treatment semantics.
3. Search same-prefix randomized reviewer/advice ON/OFF on failed plus initially successful/benign prefixes; measure rescue, pass-to-fail disruption, realized recovery dose and compute.
4. Preserve rollback-selector-only comparison under identical alarm/candidates/restore/carry-forward/inference/model/guidance/stochastic coupling/post-intervention budget.
5. Keep explicit recoverability/action classes rather than pooling transient, state-loss, ambiguous-effect, schema, authority, rate-limit/external-unavailable, irreversible-effect and terminal-belief failures.
6. Continue exact single-admitted-update future-task ON/OFF frozen replay; randomized/propensity-logged reviewer routing; persistent-release FWER-vs-FDR/LORD; verifier exposure/refresh; common-replicate admission × maintenance factorial; hidden semantic lineage; post-consolidation re-externalization; decision-influence audits.
7. Locate official SymTrace/SymFail source if it becomes publicly discoverable; do not infer runtime behavior from a release claim.
8. Recover official numeric CASS `k` and u-SMCO `tau` only from primary supplement/code; never guess.
9. Preserve exact tested scope and a nonempty frontier; checkpoints/findings are never global completion.

Future runs should resolve a fresh SHA-only control tuple before semantic work and read this pointer first, followed only by the minimum own predecessor material needed for unresolved frontier continuity.
