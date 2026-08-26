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
50. `2026-08-26T1701JST-followup3.md`
51. `2026-08-26T1701JST-followup4.md`

Read `STATE.md` for the accumulated base, then source-qualified checkpoints above in order as needed. Newest checkpoint supersedes older frontier wording where they conflict.

## Top unresolved frontier

1. Implement/validate the causal SQLite journal before randomized policy/OPE collection: WAL + synchronous=FULL; append-only Decision/BatchConsumption/Outcome; commit/readback before effect boundaries; conservative censoring.
2. Replace mutable provider-batch `metadata.action_id` with immutable physical provider events plus append-only `ProposalBatchConsumptionEventV0`; the minimal overwrite characterization is one model-like generation batch with two same-batch ghost `REFINE_ARGUMENT` no-ops.
3. Make decisions causally self-contained: every choice row must persist explicit node↔batch↔finalized-proposal identity, baseline rank/admission, structural transition preview/support and exact rational propensity.
4. Treat current `_finalize_kind()` loss of generator `target_step_ids` as a separate substrate defect/version. Do not silently fix it inside epsilon=0 journal instrumentation.
5. Use reducer-owned pure mechanical transition reports `WOULD_MUTATE / WOULD_NOOP / WOULD_ERROR`, with stable reason codes and action-specific predicted version deltas. Mutation is not the same as mathematical progress.
6. Freeze `ExecutionDecisionEventV0`, `ProposalBatchConsumptionEventV0`, `ExecutionOutcomeEventV0` and `SemanticRunProjectionV0` before randomized outcomes. Separate runtime node identity, semantic proposal hash and full envelope hash.
7. Execute C229-C253 target-step/overwrite/trace/transition/journal regressions plus prior F0–F7 crash/replay/idempotence/RNG-isolation tests. Epsilon>0 remains forbidden until all pre-randomization contracts pass.
8. Logging-policy v0 remains D0-ranked supported pool <=5, epsilon=1/4 with exact rational propensities once enabled; record the full baseline frontier even when exploration support is narrower.
9. Deterministic provider pilot remains frozen after journal validation: task-hash order, cap 200 eligible tasks, 10,000 task bootstrap resamples, <=5pp 95% CI half-width, preserving generation/execution/assembly cost separation.
10. Stage A proceeds only with sufficient precision and either lower-CI execution-cost share >=10% in a primary dimension or lower-CI multi-action-task rate >=25%; otherwise move upstream to Stage B generation/retrieval/model-routing control. Keep public-source search narrow and frontier nonempty.

## Newest synthesis

- **C229–C233:** real controller finalization drops `target_step_ids`; the overwrite regression reduces to one provider batch/two ghost refines with one model-call budget, while target-step preservation must be independently substrate-versioned.
- **C234–C238:** current result traces cannot reconstruct node→batch causality and structural “executed” records/zero execution cost cannot distinguish mutation from no-op. Decision events therefore need explicit finalized proposal identity and batch/source joins.
- **C239–C240:** successful DECOMPOSE advances the workspace by +2 whereas successful argument/representation transitions are +1. Preview status is renamed mechanically to `WOULD_MUTATE / WOULD_NOOP / WOULD_ERROR` so mutation is never conflated with usefulness.
- **C241–C245:** preserve runtime node ID separately from a semantic proposal hash that excludes transport/cost metadata; the exact one-call two-refine characterization test, provider-event filter and shared reducer-preview architecture are fixed.
- **C246:** ghost REFINE payloads pass proposal validation because argument payload validation checks alignment shape but not live-step existence/coverage; the reducer is where the no-hit becomes a no-op.
- **C247–C253:** transition reason-code taxonomy and complete causal schemas are frozen: Decision committed before effect, BatchConsumption in the same transaction, Outcome after immediate execution truth, censored when Outcome is absent; semantic projection excludes journal-only mechanics and includes substrate/proposal/transition semantics.

## Exact continuation

1. Executable-validate the one-call two-refine current-code characterization and migrated immutable-batch/two-consumption-edge oracle at the real action-runtime seam.
2. Implement/shared-test reducer transition preparation/report logic, especially DECOMPOSE +2 and duplicate/self-child deterministic errors.
3. Implement journal tables, payload digests, uniqueness/conflict rules and C248–C251 commit ordering; run F0–F7 fault injection.
4. Add target-step preservation as a separate substrate regression/version, not part of logging equivalence.
5. Implement/freeze `SemanticRunProjectionV0` with semantic proposal hashes and immediate transition outcomes; verify epsilon=0 hard equivalence with independent logging RNG.
6. Only after all pre-randomization tests pass, run the frozen deterministic provider pilot and apply the Stage-A gate; do not run epsilon>0 earlier.
7. Continue only narrow public-source falsification/simplification searches and keep frontier nonempty. `2026-08-26T1701JST-followup4.md` is newest and is not global completion.

Do not read legacy `research_workers/reasoning/`, O/O-derived state, comparator/integrator/index/feed/audits, other-worker state/config, shared execution ledger, or other-role receipts.
