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
46. `2026-08-26T1600JST.md`

Read `STATE.md` for the accumulated base, then source-qualified checkpoints above in order as needed. Newest checkpoint supersedes older frontier wording where they conflict.

## Top unresolved frontier

1. Implement/validate the causal SQLite journal before randomized policy/OPE collection: WAL + synchronous=FULL; append-only decision/batch-consumption/outcome; commit/readback before effect boundaries; conservative censoring.
2. Replace mutable provider-batch `metadata.action_id` in authoritative learning evidence with immutable `ProposalBatchConsumptionEvent` joins. The same-batch two-consumer overwrite now has a concrete reachable runtime fixture through a valid `REFINE_ARGUMENT` no-op path.
3. Distinguish `baseline_frontier_eligible` from a pure live-state `effect_precondition_status`; current frontier+budget membership includes deterministic structural no-ops.
4. Freeze `SemanticRunProjectionV0` before randomized outcomes, including semantic effect class and workspace-version transition while excluding journal-only metadata/timing.
5. Preserve epsilon=0 current D0 behavior even if D0 selects a known no-op. Treat no-op pruning as a separate substrate change rather than hiding it inside logging.
6. Execute C216/C220 reachable attribution/effect-mask regressions plus prior C214/F0–F7 faults at real action-runtime/journal/fake-executor seams. Randomized epsilon>0 remains forbidden until these pass.
7. Logging-policy v0 remains D0-ranked supported pool <=5, epsilon=1/4, exact rational propensities; exploratory alternatives should be drawn only from the frozen safe/effectful subset while the full baseline frontier is recorded.
8. Provider deterministic pilot remains frozen after journal validation: deterministic task hash order, cap 200 eligible tasks, 10,000 task bootstrap resamples, <=5pp 95% CI half-width target. Preserve G/E/A separation.
9. Stage-A randomized collection proceeds only with sufficient precision and either lower-CI execution-cost share >=10% in a primary dimension or lower-CI task-level multi-action opportunity >=25%; otherwise shift upstream to Stage B generation/retrieval/model-routing control.
10. Keep public-source search narrow/secondary and frontier nonempty.

## Newest synthesis

- **C209–C215:** provider generation events are physically shared but historical `metadata.action_id` is rewritten per consumer; canonical migration is immutable provider events + append-only consumption edges; exact admission/propensity and epsilon=0 contracts were specified; Stage A cannot claim upstream generation spend.
- **C216:** same-batch multi-consumer overwrite is concretely reachable through two frontier-valid `REFINE_ARGUMENT` proposals whose payload replacement ids miss the live graph, causing the first execution to leave workspace version unchanged and the second same-batch node to remain valid.
- **C217:** successful structural mutations bump the global workspace version, so ordinary remaining cached nodes become stale. The repeated-consumer bug is therefore concentrated in no-effect paths rather than all multi-proposal batches.
- **C218:** current frontier membership is broader than an effective-action mask; multiple structural payloads can validate yet reducer-no-op.
- **C219:** Decision/Outcome journaling should record precondition/effect classification plus workspace version before/after, without changing baseline execution initially.
- **C220:** pre-randomization tests should first reproduce the reachable no-op overwrite, then add pure effect-precondition tests, then freeze semantic projection/epsilon=0 before any exploratory no-op filtering.

## Exact continuation

1. Inspect public CSSC tests/fixtures enough to specify the smallest real `StructuredController` integration fixture for the C216 same-batch two-refine path; avoid helper-only tests.
2. Define a pure `effect_precondition(node, workspace)` contract mirroring structural reducer preconditions and identify false-positive/false-negative cases.
3. Update `SemanticRunProjectionV0` to include semantic effect class and workspace-version transition.
4. Preserve epsilon=0 behavioral identity; if no-op pruning is later adopted, benchmark it as a distinct substrate change.
5. After journal + attribution + effect-mask tests pass, execute the prespecified deterministic provider pilot and frozen Stage-A gate.
6. Continue only narrow public-source falsification/simplification searches.
7. Keep frontier nonempty. `2026-08-26T1600JST.md` is newest and is not global completion.

Do not read legacy `research_workers/reasoning/`, O/O-derived state, comparator/integrator/index/feed/audits, other-worker state/config, shared execution ledger, or other-role receipts.
