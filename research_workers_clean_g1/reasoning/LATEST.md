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

Read `STATE.md` for the accumulated base, then source-qualified checkpoints above in order as needed. Newest checkpoint supersedes older frontier wording where they conflict.

## Top unresolved frontier

1. Implement/validate the causal SQLite journal before randomized policy/OPE collection: WAL + synchronous=FULL; append-only decision/batch-consumption/outcome; commit/readback before effect boundaries; conservative censoring.
2. Inject the journal only into the action-cost-aware runtime through a narrow `DecisionJournal` interface with a null default; keep prover/generator/reducer/cost estimator untouched for the first causal comparison.
3. Execute F0–F7 failures and epsilon=0 `semantic_projection(ControllerResult)` equivalence. Disable/non-bind elapsed-time budget for the semantic equality arm and measure journal timing overhead separately.
4. Remove or bypass mutable shared-provider-batch attribution from learning evidence. Provider cost events stay immutable; batch consumption is an append-only join.
5. Logging-policy v0 is frozen before outcomes: D0-ranked supported pool <=5, epsilon=1/4, exact rational propensities, min support 1/20, D0 fallback outside support.
6. Recovery v0 never resumes/reselects within a run that ends with an unmatched decision; seal truncated/censored and start any later attempt under a new run id.
7. Stage-A representation remains frozen at 154 text-free candidate channels; theorem/task is the split unit; terminal success/local progress/multidimensional costs remain separate labels.
8. Provider deterministic pilot retains prospective 95% task-bootstrap CI half-width <=5 percentage points for major mean cost shares, then decides Stage A vs upstream Stage B.
9. Keep narrow public-source search secondary.

## Newest synthesis

- **C171–C177:** current CSSC has a mid-run causal logging gap and mutable shared-batch attribution; exact failure/equivalence tests are now specified.
- **C178–C184:** journal backend/schema/reader and safe-epsilon support protocol are prespecified; raw evaluation remains multiobjective/Pareto.
- **C185:** simplified local SQLite prototype validated rollback, censoring, batch+decision transaction, outcome rollback, append-only trigger, exact duplicate idempotency/conflict and rational propensity properties.
- **C186:** v0 does not resume a randomized run across an unmatched decision.
- **C187:** reader finite-state machine is READY -> PENDING[/BOUND] -> READY; illegal sequences fail closed.
- **C188:** exact epsilon=1/4 propensity formula/property tests are frozen for L=1..5.
- **C189:** distinguish full run cost, post-decision execution cost and many-to-many proposal provenance; never duplicate a shared batch charge across sibling actions.
- **C190:** minimal integration surface is one injected `DecisionJournal` plus null implementation inside action runtime.
- **C191:** immutable provider events are the learning authority; current `attribute_proposal_batch` rewrite must not be part of OPE evidence.
- **C192:** exact semantic-equivalence projection is field-scoped; unique ids/temp paths/timing/journal artifacts are normalized or measured separately.
- **C193:** epsilon=0 must not consume logging-policy RNG; randomized policy later uses a dedicated recorded RNG.
- **C194:** unit correctness can use deterministic fake generators/providers; a live model is unnecessary for journal validity.
- **C195:** existing atomic end-of-run JSONL trace remains useful but cannot replace a pre-effect causal journal.

## Exact continuation

1. Specify typed record fields/canonical source types for decision/batch/outcome/ack and a deterministic `FaultingDecisionJournal` test double.
2. Specify reader property/fuzz cases and exact semantic-projection normalization helpers.
3. Decide migration path for current provider-batch attribution while keeping learning evidence immutable.
4. Validate journal + epsilon=0 equivalence before randomization.
5. Run deterministic provider cost-share pilot and decide Stage A vs Stage B.
6. Keep frontier nonempty. `2026-08-26T1427JST-followup3.md` is newest and is not global completion.

Do not read legacy `research_workers/reasoning/`, O/O-derived state, comparator/integrator/index/feed/audits, other-worker state/config, shared execution ledger, or other-role receipts.
