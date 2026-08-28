# Long Horizon clean_g1 — latest pointer

Authoritative latest checkpoint for this namespace:
`research_workers_clean_g1/long_horizon/CHECKPOINT_2026-08-28T130228JST_COMPLETION_CONTRACT_AND_VERIFIED_PROGRESS.md`

Immediate predecessor:
`research_workers_clean_g1/long_horizon/CHECKPOINT_2026-08-28T120144JST_REFINEACT_TYPED_OUTCOME_VERIFICATION.md`

Control snapshot frozen for this semantic invocation:
- root control revision: `13`
- role config revision: `5`
- frozen semantic source main SHA: `0dd97c62678923281362091099cbee26402dd4d0`
- root blob: `cc9b1f22f0fda9cf26296057fd35b19a090618b4`
- role config blob: `268523da20c78ce3091344c492ad3d51f6f9e667`
- repeated pre-semantic SHA-only ref lookup matched before own-state/public semantic work. Repository writes after semantic freeze are write-safety operations only and are not adopted semantically.

Current synthesis delta:
- Public `Postcept/gauntlet` artifact separates completion-evidence policies on the same 21 synthetic broken-refund scenarios: self-grading `7/21`, simple system-of-record re-read `14/21`, always-block `14/21`, bespoke checker `18/21`, contract-complete outcome verification `21/21` on this deterministic set. The key new distinction is `authoritative source consulted != authoritative claim verified`: record existence/success status can still miss duplicates, finality, operation identity, customer/entity and field mismatches.
- Completion evidence should therefore track at least two axes: **source authority/freshness** and **predicate/binding completeness**. Refine the witness ladder to `runtime_succeeded -> SOR_observed -> contract_complete_effect_verified -> terminal_authorized`.
- PushBench shows that terminal verification alone can prevent unsupported `done` without creating actual long-horizon persistence. Under matched controller settings, stateful verified-progress tracking reaches `69–78%` on repository-artifact collection while removing duplicate submissions; in verifier-backed work-unit tasks, standard and completion-gated controllers complete no instances while backlog-tracking reaches `25–50%`. Persist accepted unit identities/backlog/no-progress state, not only a final completion predicate.
- `When Stale Constraints Go Unchecked` randomizes verification allocation at a fixed two-record budget. Stale stated constraints receive their provenance check natively only about `20–23%` of the time; reallocating one slot to the critical supersession path raises current-record-consistent decisions by roughly `+61–74pp` across confirmatory runs. Provenance availability is not freshness verification; freshness/supersession deserves a separate budgeted routing signal.
- Scope remains strict: Postcept gauntlet is vendor-maintained synthetic/deterministic and not real-provider reliability evidence; PushBench uses controlled low/medium units; the stale-memory intervention has oracle knowledge of the critical path. None closes the external-state interface/effect-verification × recovery factorial.
- Fresh search still did not locate the complete `authoritative/contract-complete effect verification ON/OFF × identical fixed recovery ON/OFF` 2x2. Keep it open and count hidden SDK/client/provider retries.

Updated controller emphasis:
1. runtime/effect identity and evidence authority first;
2. distinguish fresh authoritative observation from contract-complete effect verification;
3. persist verifier-backed progress/backlog state, not merely a terminal gate;
4. allocate freshness/provenance checks by decision consequence under fixed audit budgets;
5. use deterministic prerequisite/termination gates where contracts are faithful;
6. spend LLM recovery/reviewer budget only on residual failures/ambiguous evidence.

Exact continuation:
1. Find/construct `completion-contract verification ON/OFF × identical fixed recovery ON/OFF` in external-state software/API tasks; count all retry layers.
2. Find component ablations for `existence/status` vs `operation-id/idempotency` vs `field/entity binding` vs `duplicate/uniqueness` vs `finality/lifecycle` vs multi-system postconditions.
3. Find direct host-success vs SOR-read vs contract-complete-SOR verification under timeout-after-commit, delayed visibility, partial commit, duplicate effects, and stale/unknown provider state.
4. Extend PushBench-like matched controls to repository-scale work: completion gate only vs verified-progress/duplicate ledger vs backlog/no-progress repair.
5. Find deployable freshness/supersession audit allocation approximating the forced-critical intervention at fixed verification budget.
6. Continue `LLM Step Abstraction vs deterministic typed outcome encoder` under identical model/subgoal/routing/tasks and final success + token/time cost.
7. Continue RefineAct component factorials, always-on vs event-triggered terminal proof, and same-prefix Reviewer rescue-vs-disruption.
8. Preserve rewind selector/restore, critic refresh cadence, persistent refinement contamination, exact-update future replay, release risk spending, verifier exposure/refresh, admission×maintenance, hidden semantic lineage, post-consolidation re-externalization, decision-influence audits, SymTrace/SymFail source, and CASS parameter frontiers.
9. Keep fault classes, source authority, freshness, predicate completeness, and evidence-authority levels separate; preserve exact tested scope.
10. Preserve a nonempty frontier; checkpoints/findings are never global completion.

Future runs should resolve a fresh SHA-only control tuple before semantic work and read this pointer first, followed only by the minimum own predecessor material needed for unresolved frontier continuity.
