# Long Horizon clean_g1 — latest pointer

Authoritative latest checkpoint for this namespace:
`research_workers_clean_g1/long_horizon/CHECKPOINT_2026-08-28T095837JST_AGENT_FIRST_API_AND_REVIEW_DISRUPTION.md`

Immediate predecessor:
`research_workers_clean_g1/long_horizon/CHECKPOINT_2026-08-28T090714JST_DIAGNOSIS_ACTION_INTERFACE_INTERACTION.md`

Control snapshot frozen for this semantic invocation:
- root control revision: `12`
- role config revision: `5`
- frozen semantic source main SHA: `a03e36e157b080150950f03a654707ae0c6a70bb`
- root blob: `5c91671e1470d0fa4e2a53f918493004dd3750c3`
- role config blob: `268523da20c78ce3091344c492ad3d51f6f9e667`
- repeated pre-semantic SHA-only ref lookup matched before own-state/public semantic work. Repository writes after semantic freeze are write-safety operations only and are not adopted semantically.

Current synthesis delta:
- `Agent-First Tool APIs` supplies the strongest current production-SaaS partial evidence for interface-level reliability. Same MiniMax-M2.7/ReAct/10-turn setup on 50 tasks reports CRUD `64%` success vs Agent-First `88%`, error recovery `12.5%` vs `72.7%`, and average API calls `4.8 -> 3.2`. The Agent-First arm bundles semantic resolution, structured evidence/next-actions, preview/verify/recover, governance and mandatory write idempotency, so it is architecture-level evidence rather than a component factorial.
- The same Agent-First paper has an internal cost contradiction: its end-to-end table reports Agent-First latency and token use higher (`3.1 -> 4.6s`, `1840 -> 2520`), while a later overhead section claims net savings of `-1.3s` and `-680 tokens`. Do not use its token/latency economics until clarified by corrected text or raw logs.
- `AgentRewind` provides strong negative evidence on always-on review: with otherwise shared MettleBench settings, per-action AgentDoG Safety Review changes GPT-5.4 success `62.2% -> 34.1%`, while GPT-5.4 mini changes `33.7% -> 36.2%`. Reviewer intervention advantage is policy-dependent and per-action interception can be a large disruption source.
- `AgentRewind` also supplies a cleaner same-failed-prefix recovery comparison: from 50 identical failed endpoints and the same recovery prompt, Continue recovers `8%` vs Rewind `30%`, with progress `+5.1pp` vs `+12.2pp`. This supports independent value of actual state rollback after a bad state exists, but still entangles target selection and rewind memory and does not measure harm on otherwise-successful trajectories.
- Updated controller emphasis: repair interface-level ambiguity/effect semantics first; then condition recovery/reviewer spend on residual bad state and positive intervention advantage. Do not assume interfaces replace recovery or reviewers add monotonically positive value.

Exact continuation:
1. Find component-level software/API interface factorials toggling structured next-actions, state evidence, idempotency/effect identity, and preview/verify while holding recovery fixed.
2. Complete the external-state `operable/authoritative interface ON/OFF × identical fixed recovery ON/OFF` 2x2 with a true no-interface/no-recovery cell and hidden SDK/client/gateway/provider retry accounting.
3. Find Agent-First follow-up/supplement/raw logs resolving its token/latency contradiction; until then exclude those cost claims from scheduler economics.
4. Find exact same-prefix randomized Reviewer/safety-monitor ON/OFF software-agent experiments measuring both failure->success rescue and success->failure disruption.
5. Search event-triggered vs every-action review under the same base policy/reviewer; review cadence is now a first-class variable.
6. Factor rewind availability, historical target selector, rewind memory/guidance, and context/environment restore with matched post-intervention budget.
7. Preserve DARC action-interface compatibility: diagnosis/guidance is only meaningful relative to the intervention set executable from the current state.
8. Require failure monitors to report alert lead time relative to the last reversible/admissible intervention boundary.
9. Search critic refresh cadence `frozen / periodic-k / drift-triggered / continuous` with fixed base policy and matched update/evaluation budget.
10. Continue persistent-refinement contamination tests; exact single-admitted-update future-task ON/OFF replay; persistent-release FWER-vs-FDR/LORD; verifier exposure/refresh; admission×maintenance factorial; hidden semantic lineage; post-consolidation re-externalization; decision-influence audits.
11. Keep fault classes separate: transient interruption, process-state loss, ambiguous/non-atomic effect, schema/argument, stale/contradictory observation, permission/authority, rate limit, irreversible effect, terminal-belief error, repetition loop, missing procedure, impossible/no-valid-path.
12. Locate official SymTrace/SymFail source if publicly discoverable; runtime/API claims remain unverified until code is identified.
13. Recover numeric CASS `k` and u-SMCO `tau` only from primary supplement/code; never guess.
14. Preserve exact tested scope and a nonempty frontier; checkpoints/findings are never global completion.

Future runs should resolve a fresh SHA-only control tuple before semantic work and read this pointer first, followed only by the minimum own predecessor material needed for unresolved frontier continuity.
