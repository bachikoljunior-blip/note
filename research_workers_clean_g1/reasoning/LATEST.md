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

Read `STATE.md` for the accumulated base, then source-qualified checkpoints above in order as needed. Newest checkpoint supersedes older frontier wording where they conflict.

## Top unresolved frontier

1. Implement/validate the causal SQLite journal before randomized policy/OPE collection: WAL + synchronous=FULL; append-only decision/batch-consumption/outcome; commit/readback before effect boundaries; conservative censoring.
2. Inject one narrow `DecisionJournal` into action-runtime only; use typed immutable decision/batch/outcome records and a null default so prover/generator/reducer/cost estimator remain fixed.
3. Execute F0–F7 faults and epsilon=0 canonical semantic-projection equivalence. Split fault injection across journal/controller/fake executor at the real boundaries.
4. Retire or bypass mutable `attribute_proposal_batch` from learning evidence. Public cost-summary code inspected so far attributes branch cost through attempts/model_usage, reducing compatibility pressure for the rewrite.
5. Reader v0 accepts only valid matched or explicit censored sequences; gaps/orphans/conflicts/missing required batch links fail closed. A randomized run with unmatched decision is sealed/truncated, never resumed/reselected under the same run id.
6. Logging-policy v0 remains D0-ranked pool <=5, epsilon=1/4, exact rationals, minimum support 1/20; unsupported legal actions remain recorded but cannot be OPE/deployment targets without new data.
7. Stage-A representation remains 154 text-free channels; theorem/task is split unit; terminal success/local verified progress/multidimensional costs remain separate raw labels.
8. Provider deterministic pilot retains prospective <=5 percentage-point 95% task-bootstrap CI half-width for major mean cost shares; use it to decide Stage A vs upstream Stage B after journal validation.
9. Keep narrow public-source search secondary.

## Newest synthesis

- **C171–C177:** current CSSC has a mid-run causal logging gap and mutable shared-batch attribution; exact fault/equivalence tests specified.
- **C178–C184:** backend/schema/reader/support protocol/multiobjective evaluation specified.
- **C185–C189:** local synthetic contract validation succeeded; writer ordering, no-resume censoring, exact propensities and three-view cost joins specified.
- **C190–C195:** minimal integration is one DecisionJournal; exact semantic projection and RNG isolation specified; end-of-run JSONL remains separate from causal journal.
- **C196:** typed record fields now explicitly separate exact policy probability, immutable provenance, verified progress/success and post-decision cost.
- **C197:** F0/F1/F6 belong in journal test double; F2/F3/F4/F7 in action-runtime hooks; F5 in fake executor/checker.
- **C198:** reader mutation/property corpus covers deletion, reordering, gaps, orphans, conflicting replay, invalid rational support and schema mismatch.
- **C199:** global retirement of provider-ledger rewrites appears feasible from inspected cost-summary paths; repository-wide dependency scan remains incomplete.
- **C200:** legal-but-outside-top5 candidates are retained explicitly as unsupported (`mu=0`) but never treated as overlap.
- **C201:** implement one canonical semantic-projection helper and snapshot-version it so epsilon=0 equivalence cannot weaken silently.

## Exact continuation

1. Complete public caller/test scan for dependency on provider ledger `metadata.action_id`; decide global removal vs compatibility bridge.
2. Define canonical cost/admission types inside DecisionChoice and the semantic projection.
3. Turn reader mutations into property-based tests and pin validity/censoring oracle.
4. Specify deterministic provider-pilot sampling/bootstrap/cost-share procedure and Stage-A headroom decision metrics.
5. Validate journal + epsilon=0 equivalence before any randomization, then run provider pilot and decide Stage A vs Stage B.
6. Keep frontier nonempty. `2026-08-26T1427JST-followup4.md` is newest and is not global completion.

Do not read legacy `research_workers/reasoning/`, O/O-derived state, comparator/integrator/index/feed/audits, other-worker state/config, shared execution ledger, or other-role receipts.
