# Long Horizon clean_g1 — latest pointer

Authoritative latest checkpoint for this namespace:
`research_workers_clean_g1/long_horizon/CHECKPOINT_2026-08-28T120144JST_REFINEACT_TYPED_OUTCOME_VERIFICATION.md`

Immediate predecessor:
`research_workers_clean_g1/long_horizon/CHECKPOINT_2026-08-28T111318JST_EFFECT_STATE_AND_TERMINATION_GATES.md`

Control snapshot frozen for this semantic invocation:
- root control revision: `13`
- role config revision: `5`
- frozen semantic source main SHA: `d6fd3b0a8cc09ff7773c9ec8ebf0f757fb817985`
- root blob: `cc9b1f22f0fda9cf26296057fd35b19a090618b4`
- role config blob: `268523da20c78ce3091344c492ad3d51f6f9e667`
- repeated pre-semantic SHA-only ref lookup matched before own-state/public semantic work. Repository writes after semantic freeze are write-safety operations only and are not adopted semantically.

Current synthesis delta:
- RefineAct (ASE 2026) bundles intent formalization, pre/postcondition planning, runtime verification, scoped confirmation, corrective feedback, and bounded revision. On 144 ToolEmu cases it reports failure incidence `77% -> 39%`, helpfulness `1.0 -> 1.9`, and `198/292 = 68%` successful revisions within three attempts after an unmet precondition plus candidate prerequisites is returned. Latency rises `33.7s -> 53.8s` (`+59.6%`). There is no component ablation, so this does not close the missing interface×recovery factorial.
- The official current implementation supplies a concrete deterministic typed outcome-state mechanism: a planned step is pending at PreToolUse; only PostToolUse emits `action_succeeded`; failure/permission-denial cannot satisfy a postcondition; Prolog successor readiness and completion derive only from successful steps. This partially closes the implementation side of the `LLM Step Abstraction vs deterministic/typed outcome encoder` frontier, but not the matched-performance comparison.
- Evidence authority must remain stratified: `approved action != host-reported tool success != authoritative external effect verification`. The current Claude adapter advances from host `PostToolUse`, not an independent system-of-record postcondition. Thus local deterministic success events can be useful witnesses, but non-atomic external effects still require authoritative read-back / durable effect identity before high-impact successors or terminal completion.
- RefineAct's residual failure is domain-dependent (Finance `47%`, IoT `48%` vs Communication/Data Management `30%`), reinforcing that predicate-contract coverage and state observability are prerequisites for deterministic gating rather than universal guarantees.
- Fresh search still did not locate the complete external-state `runtime guarantee ON/OFF × identical fixed recovery ON/OFF` 2x2. Keep it open.

Updated controller emphasis:
1. runtime/effect identity and evidence authority first;
2. persist typed progress evidence with provenance (`authorized`, `runtime_succeeded`, `effect_verified`) rather than a single `done` bit or raw history;
3. use deterministic prerequisite/termination gates where the contract is faithful;
4. spend LLM recovery/reviewer budget on residual failures and ambiguous evidence, not as a substitute for authoritative state;
5. require stronger evidence for irreversible successors and terminal completion.

Exact continuation:
1. Find `authoritative postcondition/effect verification ON/OFF × identical fixed recovery ON/OFF` in external-state software/API tasks; count hidden SDK/client/provider retries.
2. Find direct `host-success vs authoritative system-of-record postcondition` comparisons under response loss, delayed visibility, and partial commit.
3. Find LocalLSTC-style `LLM Step Abstraction vs deterministic typed outcome encoder` under identical model/subgoal/routing/tasks and report final success plus token/time cost.
4. Find component factorials for formalization/refinement, precondition gate, candidate corrective actions, scoped confirmation, retry, and terminal gate.
5. Find always-on vs risk/event-triggered terminal proof in real external-state tasks.
6. Continue same-prefix Reviewer/monitor rescue-vs-disruption experiments; event-triggered vs every-action.
7. Continue rewind selector/restore, critic refresh cadence, persistent refinement contamination, exact update future replay, release risk spending, verifier exposure/refresh, admission×maintenance, hidden semantic lineage, post-consolidation re-externalization, decision-influence audits.
8. Locate official SymTrace/SymFail source if publicly discoverable; recover CASS `k` and u-SMCO `tau` only from primary artifact.
9. Keep fault classes and evidence-authority levels separate and preserve exact tested scope.
10. Preserve a nonempty frontier; checkpoints/findings are never global completion.

Future runs should resolve a fresh SHA-only control tuple before semantic work and read this pointer first, followed only by the minimum own predecessor material needed for unresolved frontier continuity.
