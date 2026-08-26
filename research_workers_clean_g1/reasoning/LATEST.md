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
47. `2026-08-26T1701JST.md`

Read `STATE.md` for the accumulated base, then source-qualified checkpoints above in order as needed. Newest checkpoint supersedes older frontier wording where they conflict.

## Top unresolved frontier

1. Implement/validate the causal SQLite journal before randomized policy/OPE collection: WAL + synchronous=FULL; append-only decision/batch-consumption/outcome; commit/readback before effect boundaries; conservative censoring.
2. Replace mutable provider-batch `metadata.action_id` in authoritative learning evidence with immutable `ProposalBatchConsumptionEvent` joins. The normal-runtime same-batch two-consumer overwrite now has a fully specified `StructuredController` fixture: seed live `s1`, then emit two same-batch frontier-valid no-op refines with ghost replacement IDs.
3. Replace the earlier boolean `effect_precondition` idea with a reducer-owned pure three-way structural preview: `EFFECTFUL / NO_EFFECT / WOULD_ERROR`, stable reason code, and optional predicted workspace-version delta. Do not duplicate reducer logic in the policy layer.
4. Keep `baseline_frontier_eligible`, structural preview status, and `exploration_supported` separate. Epsilon=0 must preserve D0 behavior even when D0 selects a known no-op/error; exploratory alternatives may be restricted to the frozen safe/effectful subset.
5. Freeze `SemanticRunProjectionV0` before randomized outcomes, including effect status/reason and workspace-version transition while excluding journal-only metadata/timing.
6. Execute the C221-C228 integration/preview regressions plus prior C214/F0–F7 faults at real action-runtime/journal/fake-executor seams. Randomized epsilon>0 remains forbidden until these pass.
7. Logging-policy v0 remains D0-ranked supported pool <=5, epsilon=1/4, exact rational propensities; record the full baseline frontier even when exploration support is narrower.
8. Provider deterministic pilot remains frozen after journal validation: deterministic task hash order, cap 200 eligible tasks, 10,000 task bootstrap resamples, <=5pp 95% CI half-width target. Preserve G/E/A separation.
9. Stage-A randomized collection proceeds only with sufficient precision and either lower-CI execution-cost share >=10% in a primary dimension or lower-CI task-level multi-action opportunity >=25%; otherwise shift upstream to Stage B generation/retrieval/model-routing control.
10. Keep public-source search narrow/secondary and frontier nonempty.

## Newest synthesis

- **C216–C220:** same-batch multi-consumer overwrite is reachable through frontier-valid structural no-ops; successful structural mutations usually invalidate sibling cache entries via workspace-version bump, so the repeated-consumer path concentrates on no-effect transitions; frontier membership is broader than effective-action support.
- **C221–C224:** the smallest real integration regression is now specified using the existing `StructuredController` action-runtime test scaffold. First seed live step `s1`; then one provider batch emits two distinct refines with live `target_step_ids=("s1",)` but ghost payload replacement IDs. Both are selected in sequence without an intervening generation. Current final provider-event attribution must end on node2; migrated behavior must preserve immutable physical cost plus two consumption edges.
- **C225–C227:** a boolean precondition is insufficient because structural actions can be effectful, deterministic no-op, or deterministic exception. A reducer-owned pure preview should be the single semantic source for both reducer and exploration-support filtering. Baseline eligibility remains separate to preserve epsilon=0 identity.
- **C228:** `SemanticRunProjectionV0` should add selected structural effect status/reason and workspace-version before/after, but exclude journal event IDs/timestamps/WAL/flush timing.

## Exact continuation

1. Specify the concrete model-like structured generator metadata and exact budget for the C221 fixture so it creates provider ledger events with no external provider/checker dependency and ends deterministically after the two no-op refines.
2. Inspect `CostLedger.to_dict()` and the existing provider-attribution test event filters, then freeze exact current-code and migrated assertion code.
3. Design the reducer-owned `StructuralEffectReport` API and parity tests in `tests/test_reducer.py`, including `WOULD_ERROR` decomposition graph cases and edge cases where empty structural payloads are still effectful under current semantics.
4. Extend the causal journal schema so Decision records baseline eligibility + preview status/reason and Outcome records actual effect/version transition; preserve immutable batch-consumption joins.
5. Run same-batch overwrite/migration, crash/replay, epsilon=0 RNG isolation, and preview/reducer-parity tests before any epsilon>0 collection.
6. Only after those pass, execute the prespecified deterministic provider pilot and frozen Stage-A gate.
7. Continue only narrow public-source falsification/simplification searches and keep frontier nonempty. `2026-08-26T1701JST.md` is newest and is not global completion.

Do not read legacy `research_workers/reasoning/`, O/O-derived state, comparator/integrator/index/feed/audits, other-worker state/config, shared execution ledger, or other-role receipts.
