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
52. `2026-08-26T1802JST.md`

Read `STATE.md` for the accumulated base, then source-qualified checkpoints above in order as needed. Newest checkpoint supersedes older frontier wording where they conflict.

## Top unresolved frontier

1. Implement/validate the causal SQLite journal before randomized policy/OPE collection: WAL + synchronous=FULL; append-only Decision/BatchConsumption/Outcome plus content-addressed `WorkspaceSnapshotV0`; commit/readback before effect boundaries.
2. Replace mutable provider-batch `metadata.action_id` with immutable physical provider events plus append-only `ProposalBatchConsumptionEventV0`; the minimal overwrite characterization remains one model-like generation batch with two same-batch ghost `REFINE_ARGUMENT` no-ops.
3. Add `RecoveryClassV0`: reducer-only structural actions (`DECOMPOSE`, `PROPOSE_ARGUMENT`, `REFINE_ARGUMENT`, `CHANGE_REPRESENTATION`) are replayable from the exact durable pre-workspace snapshot without re-selection or provider regeneration; checker/candidate actions fail closed when an effect may have occurred and Outcome is absent.
4. Make decisions causally self-contained: every choice row must persist explicit node↔batch↔finalized-proposal identity, baseline rank/admission, structural transition preview/support, exact rational propensity, recovery class, and pre-workspace snapshot reference.
5. Treat current `_finalize_kind()` loss of generator `target_step_ids` as a separate substrate defect/version. Do not silently fix it inside epsilon=0 journal instrumentation.
6. Use reducer-owned pure mechanical transition reports `WOULD_MUTATE / WOULD_NOOP / WOULD_ERROR`, with stable reason codes and action-specific predicted version deltas. Mutation is not the same as mathematical progress.
7. Freeze `ExecutionDecisionEventV0`, `ProposalBatchConsumptionEventV0`, `ExecutionOutcomeEventV0`, `WorkspaceSnapshotV0`, `RecoveryClassV0` and `SemanticRunProjectionV0` before randomized outcomes. Separate runtime node identity, semantic proposal hash and full envelope hash.
8. Execute C229-C261 target-step/overwrite/trace/transition/journal/recovery regressions plus prior F0–F7 crash/replay/idempotence/RNG-isolation tests. Epsilon>0 remains forbidden until all pre-randomization contracts pass.
9. Logging-policy v0 remains D0-ranked supported pool <=5, epsilon=1/4 with exact rational propensities once enabled; record the full baseline frontier even when exploration support is narrower.
10. Deterministic provider pilot remains frozen after journal validation: task-hash order, cap 200 eligible tasks, 10,000 task bootstrap resamples, <=5pp 95% CI half-width, preserving generation/execution/assembly cost separation. Stage A proceeds only if its prespecified lower-CI gate passes; otherwise move upstream to Stage B generation/retrieval/model-routing control.

## Newest synthesis

- **C229–C253:** real controller finalization drops `target_step_ids`; current traces miss causal node→batch identity; physical provider events are mutably re-attributed; structural mutation/no-op/error needs explicit pre-effect preview; Decision/Consumption/Outcome and semantic-proposal identity contracts were frozen.
- **C254:** the initial Stage-A structural set is materially easier to recover safely than checker/tool actions. At pinned CSSC, `DECOMPOSE`, argument edits and representation changes execute only deterministic in-memory reducers after proposal generation has already happened upstream.
- **C255:** current JSONL persistence is terminal-result persistence, not a mid-run journal. A crash before `ControllerResult` construction loses the selected decision/intermediate workspace from the durable trace path.
- **C256:** `ProofWorkspace` is immutable, versioned and already has `to_dict`/`workspace_from_dict`, so content-addressed pre/post workspace snapshots can make the causal journal replayable without inventing a second state model.
- **C257–C258:** freeze recovery by effect class. Pure structural recovery replays the already-selected action under the original decision/propensity; it never reselects or consumes a new RNG draw. Effectful in-doubt actions are censored/fail-closed in v0 unless an actual idempotency/receipt contract is later proven.
- **C259:** SQLite WAL+FULL can durably commit the journal boundary but cannot make a separate external effect exactly-once. Public idempotency contracts illustrate why effectful retries need stable operation identity plus substrate support.
- **C260–C261:** Decision/Outcome schemas gain workspace-snapshot and recovery fields; initial randomized support must be defined by verified executor contracts, not by blindly enumerating all `SearchActionKind` values.

## Exact continuation

1. Executable-validate the one-call two-refine current-code characterization and migrated immutable-batch/two-consumption-edge oracle at the real action-runtime seam.
2. Implement/freeze `WorkspaceSnapshotV0` canonicalization; add `to_dict -> from_dict -> to_dict` byte-canonical round-trip/hash tests and transactionally bind the pre snapshot to Decision/Consumption and post snapshot to Outcome.
3. Implement/shared-test reducer transition preparation/report logic, especially DECOMPOSE +2 and duplicate/self-child deterministic errors.
4. Implement journal tables, payload digests, uniqueness/conflict rules and commit ordering; run F0–F7 plus pure-reducer recovery and effectful-in-doubt fail-closed cases.
5. Add target-step preservation as a separate substrate regression/version, not part of logging equivalence.
6. Implement/freeze `SemanticRunProjectionV0`; verify epsilon=0 hard equivalence with independent logging RNG and no provider regeneration during pure recovery.
7. Only after all pre-randomization tests pass, run the frozen deterministic provider pilot and apply the Stage-A gate; do not run epsilon>0 earlier.
8. Continue only narrow public-source falsification/simplification searches and keep frontier nonempty. `2026-08-26T1802JST.md` is newest and is not global completion.

Do not read legacy `research_workers/reasoning/`, O/O-derived state, comparator/integrator/index/feed/audits, other-worker state/config, shared execution ledger, or other-role receipts.
