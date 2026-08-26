# Reasoning Systems — clean_g1 latest pointer

Latest checkpoints in order:
1. `2026-08-25T1902JST.md`
2. `2026-08-25T1902JST-followup.md`
3. `2026-08-25T1957JST.md`
4. `2026-08-25T2057JST.md`
5. `2026-08-25T2157JST.md`
6. `2026-08-25T2258JST.md`
7. `2026-08-26T0002JST.md`
8. `2026-08-26T0002JST-followup.md`
9. `2026-08-26T0102JST.md`
10. `2026-08-26T0102JST-followup.md`
11. `2026-08-26T0200JST.md`
12. `2026-08-26T0302JST.md`
13. `2026-08-26T0302JST-followup.md`
14. `2026-08-26T0302JST-followup2.md`
15. `2026-08-26T0302JST-followup3.md`
16. `2026-08-26T0302JST-followup4.md`
17. `2026-08-26T0400JST.md`
18. `2026-08-26T0458JST.md`
19. `2026-08-26T0458JST-followup.md`
20. `2026-08-26T0458JST-followup2.md`
21. `2026-08-26T0558JST.md`
22. `2026-08-26T0657JST.md`
23. `2026-08-26T0657JST-followup.md`
24. `2026-08-26T0657JST-followup2.md`
25. `2026-08-26T0802JST.md`
26. `2026-08-26T0903JST.md`
27. `2026-08-26T1000JST.md`
28. `2026-08-26T1101JST.md`
29. `2026-08-26T1157JST.md`
30. `2026-08-26T1259JST.md`
31. `2026-08-26T1359JST.md`
32. `2026-08-26T1359JST-followup.md`
33. `2026-08-26T1359JST-followup2.md`
34. `2026-08-26T1359JST-followup3.md`
35. `2026-08-26T1359JST-followup4.md`
36. `2026-08-26T1359JST-followup5.md`
37. `2026-08-26T1359JST-followup6.md`
38. `2026-08-26T1359JST-followup7.md`
39. `2026-08-26T1427JST.md`
40. `2026-08-26T1427JST-followup.md`
41. `2026-08-26T1427JST-followup2.md`
42. `2026-08-26T1427JST-followup3.md`
43. `2026-08-26T1427JST-followup4.md`
44. `2026-08-26T1427JST-followup5.md`
45. `2026-08-26T1501JST.md`

Read `STATE.md` for the accumulated base, then source-qualified checkpoints above in order as needed. Newest checkpoint supersedes older frontier wording where they conflict.

## Top unresolved frontier

1. Implement/validate the causal SQLite journal before randomized policy/OPE collection: WAL + synchronous=FULL; append-only decision/batch-consumption/outcome; commit/readback before effect boundaries; conservative censoring.
2. Replace mutable provider-batch `metadata.action_id` in authoritative learning evidence with immutable `ProposalBatchConsumptionEvent` joins. A temporary compatibility projection may resolve an action id only for exactly-one-consumer batches; multi-consumer batches must remain explicit/ambiguous.
3. Freeze `SemanticRunProjectionV0` before randomized outcomes: exact deterministic fake-fixture equivalence for terminal/workspace/action/attempt/checker/provider/budget semantics, while excluding journal IDs/timestamps/WAL and real wall-clock jitter.
4. Record exact decision/admission inputs: canonical D0-ordered choice rows, cost estimates, `BudgetAdmission`, full/digested unified budget snapshot, policy versions, support cap/exclusions, chosen action and exact rational propensity.
5. Execute C214 attribution regressions plus F0–F7 faults and epsilon=0 equivalence at real action-runtime/journal/fake-executor boundaries. Randomized epsilon>0 remains forbidden until these pass.
6. Reader v0 accepts only valid matched or explicit censored sequences; randomized run with unmatched decision is sealed/truncated and never resumed/reselected under the same run id.
7. Logging-policy v0 remains D0-ranked supported pool <=5, epsilon=1/4, exact rational propensities, minimum support 1/20; unsupported legal actions are recorded but not OPE/deployment targets.
8. Provider deterministic pilot remains frozen after journal validation: deterministic task hash order, cap 200 eligible tasks, 10,000 task bootstrap resamples, <=5pp 95% CI half-width target for major cost shares. Preserve structural G/E/A separation.
9. Stage-A randomized collection proceeds only with sufficient precision and either lower-CI execution-cost share >=10% in a primary dimension or lower-CI task-level multi-action opportunity >=25%; otherwise shift upstream to Stage B generation/retrieval/model-routing control.
10. Keep public-source search narrow/secondary and frontier nonempty.

## Newest synthesis

- **C171–C177:** current CSSC has a mid-run causal logging gap and mutable shared-batch attribution; exact fault/equivalence tests specified.
- **C178–C184:** backend/schema/reader/support protocol/multiobjective evaluation specified.
- **C185–C189:** local synthetic contract validation succeeded; writer ordering, censoring/no-resume, exact propensities and three-view cost joins specified.
- **C190–C195:** minimal integration is one DecisionJournal; exact semantic projection/RNG isolation specified; end-of-run JSONL is not the causal journal.
- **C196–C201:** typed records/fault-hook split/reader mutation corpus/likely batch-attribution migration/support semantics/semantic-projection helper specified.
- **C202–C208:** deterministic provider pilot, G/E/A scopes, bootstrap precision/opportunity/headroom gates, censoring and journal-overhead rules frozen before outcomes.
- **C209:** public source confirms `attribute_proposal_batch` rewrites historical shared-batch provider event metadata on every consumer despite append-oriented ledger types.
- **C210:** targeted core/test scan found no accounting dependency on provider `metadata.action_id`; one structured-controller test explicitly expects the legacy single-consumer presentation.
- **C211:** canonical migration is immutable physical provider events plus append-only batch-consumption edges; compatibility action-id is derived only for exactly one consumer and is non-authoritative.
- **C212:** causal decision records must persist exact admission inputs/snapshot/support/propensity, not only the selected action.
- **C213:** epsilon=0 validation splits deterministic semantic hard-equivalence from live provider observability invariants.
- **C214:** seven concrete attribution/journal regression tests are specified, including same-batch two-consumer overwrite prevention and crash censoring.
- **C215:** actual CSSC call order reinforces Stage A vs Stage B: retrieval/routing/generation precede selection, so shared generation spend cannot be credited as selector-controllable execution cost.

## Exact continuation

1. If an instrumentable CSSC path becomes available, implement immutable consumption events and the narrow compatibility projection first; do not use mutable `metadata.action_id` as learning evidence.
2. Convert C211–C214 plus prior F0–F7 into executable property/integration tests at journal writer, pre-effect decision boundary and fake provider/executor seams.
3. Freeze exact `SemanticRunProjectionV0` schema/canonicalization, then prove epsilon=0 equality with isolated logging-policy RNG.
4. Only after journal/equivalence validation, execute the prespecified provider pilot C202–C208.
5. If the frozen Stage-A gate passes, collect small epsilon-v0 randomized evidence; if not, move learning upstream to Stage B.
6. Continue only narrow public-source falsification/simplification searches.
7. Keep frontier nonempty. `2026-08-26T1501JST.md` is newest and is not global completion.

Do not read legacy `research_workers/reasoning/`, O/O-derived state, comparator/integrator/index/feed/audits, other-worker state/config, shared execution ledger, or other-role receipts.
