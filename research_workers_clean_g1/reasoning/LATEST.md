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
48. `2026-08-26T1701JST-followup.md`
49. `2026-08-26T1701JST-followup2.md`

Read `STATE.md` for the accumulated base, then source-qualified checkpoints above in order as needed. Newest checkpoint supersedes older frontier wording where they conflict.

## Top unresolved frontier

1. Implement/validate the causal SQLite journal before randomized policy/OPE collection: WAL + synchronous=FULL; append-only decision/batch-consumption/outcome; commit/readback before effect boundaries; conservative censoring.
2. Replace mutable provider-batch `metadata.action_id` in authoritative learning evidence with immutable `ProposalBatchConsumptionEvent` joins. The minimal normal-runtime overwrite fixture is one model-like generation call that emits two distinct same-batch `REFINE_ARGUMENT` no-ops on the initial root.
3. Make decision traces causally self-contained: current `cache_fill` knows batch but not node IDs, while `choice_set`/`action_selected` know nodes but omit batch/proposal identity. Decision/consumption events must persist explicit node↔batch↔proposal joins.
4. Treat current `_finalize_kind()` loss of generator-supplied `target_step_ids` as a separate substrate defect/version; do not silently fix it inside epsilon=0 journaling experiments.
5. Use a reducer-owned pure three-way structural preview `EFFECTFUL / NO_EFFECT / WOULD_ERROR`; executor records and zero execution cost are not evidence of semantic progress.
6. Keep `baseline_frontier_eligible`, structural preview status, and `exploration_supported` separate. Epsilon=0 preserves D0 behavior; exploratory alternatives may use only the frozen safe/effectful subset.
7. Freeze `SemanticRunProjectionV0` with substrate version, finalized proposal identity, effect status/reason and workspace-version transition; exclude journal-only IDs/timing.
8. Execute C229-C238 overwrite/trace/target-step/preview regressions plus prior crash/replay F0–F7. Epsilon>0 remains forbidden until all pre-randomization contracts pass.
9. Logging policy and deterministic provider pilot remain frozen: D0 supported pool <=5, epsilon=1/4 when eventually enabled; pilot cap 200 tasks, 10,000 task bootstrap resamples, <=5pp 95% CI half-width, preserve G/E/A.
10. Stage A proceeds only with sufficient precision and lower-CI execution-cost share >=10% in a primary dimension or lower-CI multi-action task rate >=25%; otherwise shift upstream to Stage B. Keep public-source search narrow and frontier nonempty.

## Newest synthesis

- **C229–C233:** real controller finalization drops `target_step_ids`; this simplifies the overwrite regression to one provider batch/two ghost refines with one model-call budget, but target-step preservation must be separately versioned as a substrate fix.
- **C234:** final trace is not currently sufficient to reconstruct node→batch causality: batch aggregate and selected nodes are emitted in different events without a durable join, while mutable ledger attribution loses earlier consumers.
- **C235–C236:** `argument_records` and zero action-execution cost both conflate meaningful structural mutations with deterministic no-ops. Semantic effect must be an explicit Outcome field, not inferred from “executed” records or cheapness.
- **C237:** the one-call fixture has clean event invariants: exactly one model batch, two selected refines, zero checker calls, and current final provider request/usage/charge attribution ending on node2.
- **C238:** DecisionEvent v0 needs finalized proposal identity/body-or-content-address plus batch/source, branch/obligation versions, baseline rank/admission, preview/support and exact propensity; opaque node IDs alone are insufficient for replay/OPE.

## Exact continuation

1. Freeze concrete Python code for the one-call two-refine generator/current+migrated regression, including provider metadata and exact event filters.
2. Specify canonical finalized-proposal fingerprint and explicit node↔batch representation in DecisionEvent/ConsumptionEvent schemas.
3. Design reducer-owned `StructuralEffectReport` plus preview/reducer parity tests, including deterministic decomposition errors and empty-payload current semantics.
4. Add target-step-preservation as a separate substrate regression/version.
5. Extend causal Decision/Outcome journal and `SemanticRunProjectionV0`, then run crash/replay, idempotence/conflict, epsilon=0 RNG isolation and effect-parity tests.
6. Only after these pass, run the frozen deterministic provider pilot and Stage-A gate.
7. Continue narrow public-source falsification/simplification searches and keep frontier nonempty. `2026-08-26T1701JST-followup2.md` is newest and is not global completion.

Do not read legacy `research_workers/reasoning/`, O/O-derived state, comparator/integrator/index/feed/audits, other-worker state/config, shared execution ledger, or other-role receipts.
