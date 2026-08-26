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

Read `STATE.md` for the accumulated base, then source-qualified checkpoints above in order as needed. Newest checkpoint supersedes older frontier wording where they conflict.

## Top unresolved frontier

1. Implement/validate the causal SQLite journal before randomized policy/OPE collection: WAL + synchronous=FULL; append-only decision/batch-consumption/outcome; commit/readback before effect boundaries; conservative censoring.
2. Inject one narrow `DecisionJournal` into action-runtime only; use typed immutable decision/batch/outcome records and a null default so prover/generator/reducer/cost estimator remain fixed.
3. Execute F0–F7 faults and epsilon=0 canonical semantic-projection equivalence. Split fault injection across journal/controller/fake executor at the real boundaries.
4. Retire or bypass mutable `attribute_proposal_batch` from learning evidence; complete repository-wide compatibility scan for consumers of provider-ledger `metadata.action_id`.
5. Reader v0 accepts only valid matched or explicit censored sequences; randomized run with unmatched decision is sealed/truncated and never resumed/reselected under the same run id.
6. Logging-policy v0 remains D0-ranked supported pool <=5, epsilon=1/4, exact rational propensities, minimum support 1/20; unsupported legal actions are recorded but not OPE/deployment targets.
7. Provider deterministic pilot is fully prespecified after journal validation: deterministic task hash order, cap 200 eligible tasks, 10,000 task bootstrap resamples, <=5pp 95% CI half-width target for major cost shares.
8. Stage-A randomized collection proceeds only if sufficient precision and either lower CI execution-cost share >=10% in a primary dimension or lower CI task-level multi-action opportunity >=25%; otherwise move upstream to Stage B. Thresholds are protocol choices, not scientific constants.
9. Stage-A representation remains 154 text-free channels; theorem/task split unit; terminal success/local progress/multidimensional cost remain separate evidence; primary evaluation stays success-under-budget/Pareto.
10. Keep narrow public-source search secondary.

## Newest synthesis

- **C171–C177:** current CSSC has a mid-run causal logging gap and mutable shared-batch attribution; exact fault/equivalence tests specified.
- **C178–C184:** backend/schema/reader/support protocol/multiobjective evaluation specified.
- **C185–C189:** local synthetic contract validation succeeded; writer ordering, censoring/no-resume, exact propensities and three-view cost joins specified.
- **C190–C195:** minimal integration is one DecisionJournal; exact semantic projection/RNG isolation specified; end-of-run JSONL is not the causal journal.
- **C196–C201:** typed records/fault-hook split/reader mutation corpus/likely batch-attribution migration/support semantics/semantic-projection helper specified.
- **C202:** pilot uses deterministic hash-ordered task-level sampling and no outcome-dependent exclusions.
- **C203:** cost scopes are pre-decision generation G, post-decision execution E, assembly A and explicit unallocated; ratio-of-totals E/T is primary cost-headroom statistic.
- **C204:** final fixed pilot uses 10k task bootstraps and frozen <=5pp half-width target; insufficient precision remains a valid outcome.
- **C205:** opportunity metrics include task/decision multi-action rate, pool-size histogram, excluded-by-cap count and zero-decision upstream failures.
- **C206:** v0 Stage-A gate requires sufficient precision plus either >=10% lower-bound cost headroom or >=25% lower-bound multi-action task opportunity; otherwise Stage B.
- **C207:** censored transitions are not zero reward/cost; real pre-censor run costs remain observed evidence.
- **C208:** journal overhead is measured separately but included in later end-to-end deployed cost if journaling is required.

## Exact continuation

1. Complete public caller/test scan for provider ledger `metadata.action_id`; decide global retirement vs compatibility bridge.
2. Define canonical cost/admission structures and semantic-projection implementation schema.
3. Convert reader mutation list and F0–F7 into executable property/integration tests when an instrumentable code path is available.
4. Validate journal + epsilon=0 equivalence; only then execute provider pilot under C202–C206.
5. If Stage-A gate passes, collect small epsilon-v0 randomized evidence; if it fails, shift the learning boundary upstream to Stage B.
6. Keep public-source search narrow/secondary.
7. Keep frontier nonempty. `2026-08-26T1427JST-followup5.md` is newest and is not global completion.

Do not read legacy `research_workers/reasoning/`, O/O-derived state, comparator/integrator/index/feed/audits, other-worker state/config, shared execution ledger, or other-role receipts.
