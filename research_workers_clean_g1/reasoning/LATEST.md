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

Read `STATE.md` for the accumulated base, then source-qualified checkpoints above in order as needed. Newest checkpoint supersedes older frontier wording where they conflict.

## Top unresolved frontier

1. Implement/validate the causal SQLite journal before randomized policy/OPE collection: WAL + synchronous=FULL; append-only decision/batch-consumption/outcome; commit/readback before effect boundaries; conservative censoring.
2. Replace mutable provider-batch `metadata.action_id` in authoritative learning evidence with immutable `ProposalBatchConsumptionEvent` joins. The minimal normal-runtime overwrite fixture is now one model-like generation call that emits two distinct same-batch `REFINE_ARGUMENT` no-ops on the initial root; no preparatory `s1` mutation is required.
3. Treat current `StructuredController._finalize_kind()` loss of generator-supplied `target_step_ids` as a separate substrate defect/version. Do not silently fix it inside epsilon=0 journaling experiments.
4. Use a reducer-owned pure three-way structural preview: `EFFECTFUL / NO_EFFECT / WOULD_ERROR`, stable reason code, optional predicted workspace-version delta. Do not duplicate reducer semantics in the policy layer.
5. Keep `baseline_frontier_eligible`, structural preview status, and `exploration_supported` separate. Epsilon=0 must preserve D0 behavior even when D0 selects a known no-op/error; exploratory alternatives may be restricted to the frozen safe/effectful subset.
6. Freeze `SemanticRunProjectionV0` before randomized outcomes, including substrate version, effect status/reason and workspace-version transition while excluding journal-only metadata/timing.
7. Execute C229-C233 one-call overwrite/target-step regressions, C225-C228 preview/parity regressions, and prior C214/F0–F7 crash/replay faults. Randomized epsilon>0 remains forbidden until these pass.
8. Logging-policy v0 remains D0-ranked supported pool <=5, epsilon=1/4, exact rational propensities; record the full baseline frontier even when exploration support is narrower.
9. Provider deterministic pilot remains frozen after journal validation: deterministic task hash order, cap 200 eligible tasks, 10,000 task bootstrap resamples, <=5pp 95% CI half-width target. Preserve G/E/A separation.
10. Stage-A randomized collection proceeds only with sufficient precision and either lower-CI execution-cost share >=10% in a primary dimension or lower-CI task-level multi-action opportunity >=25%; otherwise shift upstream to Stage B generation/retrieval/model-routing control. Keep public-source search narrow and frontier nonempty.

## Newest synthesis

- **C221–C228:** a real action-runtime overwrite regression and reducer-owned effect-preview design were specified. Structural selection needs effect/no-effect/error semantics in addition to frontier liveness, while epsilon=0 must preserve baseline behavior.
- **C229:** `_finalize_kind()` reconstructs every generated `SearchAction` without copying `target_step_ids`, so real controller proposals reach validation/cache with an empty target-step tuple. The frontier's `target_step_missing` rule therefore cannot protect ordinary generated structural proposals under the current path.
- **C230–C232:** this simplifies the minimal overwrite regression to one provider batch containing two ghost-ID refines on the initial root, with `BudgetConfig(max_checks=1, max_model_calls=1)`. Both execute as no-ops, the second overwrites final provider-event `action_id`, and the run ends deterministically on model-call budget with no checker calls.
- **C231:** all current assertions are available in public result metadata: selected order and batch via `proposal_cache_events`; final overwritten provider request/usage/charge via `cost_ledger.events`.
- **C233:** preserving target-step pins is an independent substrate bugfix/ablation. Semantic projections and policy comparisons must label substrate version so gains cannot be misattributed to learning.

## Exact continuation

1. Freeze the exact one-call two-refine generator/test code shape, including provider metadata and event filters; confirm provider request/usage/charge all share the batch/request identity and current final attribution lands on the second node.
2. Define the migrated `ProposalBatchConsumptionEvent` schema and assertion: one immutable physical batch, two immutable consumer joins, no authoritative physical-event `action_id` rewrite.
3. Design `StructuralEffectReport` and reducer parity tests, including deterministic `WOULD_ERROR` decomposition cases and current-semantics empty-payload edge cases.
4. Add a separate target-step-preservation regression/substrate version; do not combine it with journal instrumentation.
5. Extend Decision/Outcome journal schemas and `SemanticRunProjectionV0` with substrate/effect/version information, then run crash/replay, idempotence/conflict and epsilon=0 RNG-isolation tests.
6. Only after all pre-randomization contracts pass, run the frozen deterministic provider pilot and Stage-A gate.
7. Continue narrow public-source falsification/simplification searches and keep frontier nonempty. `2026-08-26T1701JST-followup.md` is newest and is not global completion.

Do not read legacy `research_workers/reasoning/`, O/O-derived state, comparator/integrator/index/feed/audits, other-worker state/config, shared execution ledger, or other-role receipts.
