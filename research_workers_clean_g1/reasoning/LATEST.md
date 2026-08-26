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
53. `2026-08-26T1802JST-followup.md`

Read `STATE.md` for the accumulated base, then source-qualified checkpoints above in order as needed. Newest checkpoint supersedes older frontier wording where they conflict.

## Top unresolved frontier

1. In the first environment able to materialize pinned CSSC source, executable-validate the now-statically-proven one-batch/two-ghost-`REFINE_ARGUMENT` path at the real action runtime. No Lean or live model is required; freeze the actual deterministic node order.
2. Implement/validate the causal SQLite journal before randomized policy/OPE collection: WAL + synchronous=FULL; append-only Decision/BatchConsumption/Outcome plus content-addressed `WorkspaceSnapshotV0`; commit/readback before effect boundaries.
3. Replace mutable provider-batch `metadata.action_id` with immutable physical provider events plus append-only `ProposalBatchConsumptionEventV0`; the migrated C263 oracle must retain both same-batch consumer edges.
4. Add `RecoveryClassV0`: reducer-only structural actions (`DECOMPOSE`, `PROPOSE_ARGUMENT`, `REFINE_ARGUMENT`, `CHANGE_REPRESENTATION`) replay from exact durable pre-workspace state without re-selection/provider regeneration; checker/candidate actions fail closed when an effect may have occurred and Outcome is absent.
5. Make decisions causally self-contained: explicit node↔batch↔finalized-proposal identity, baseline rank/admission, transition preview/support, exact rational propensity, recovery class, and pre-workspace snapshot reference.
6. Treat current `_finalize_kind()` loss of generator `target_step_ids` as a separate substrate defect/version. Do not silently fix it inside epsilon=0 journal instrumentation; later prove the fix changes ghost-refine eligibility.
7. Use reducer-owned `WOULD_MUTATE / WOULD_NOOP / WOULD_ERROR` mechanical transition reports with stable reason codes and predicted version deltas. Mutation is not mathematical progress.
8. Freeze Decision/BatchConsumption/Outcome/WorkspaceSnapshot/RecoveryClass/SemanticRunProjection schemas, then execute C229-C266 regressions plus F0–F7 crash/replay/idempotence/RNG-isolation. Epsilon>0 remains forbidden until all pass.
9. Logging-policy v0 stays D0-ranked support <=5, epsilon=1/4 exact rational propensity only after gates. Record full baseline frontier even when exploration support is narrower.
10. Deterministic provider pilot remains frozen after journal validation: hash-ordered cap 200 eligible tasks, 10k task bootstrap, <=5pp 95% CI half-width, preserving generation/execution/assembly cost separation. Stage A proceeds only if its prespecified lower-CI gate passes; otherwise Stage B moves upstream to generation/retrieval/model routing.

## Newest synthesis

- **C229–C253:** target-step loss, mutable provider attribution, missing causal trace identity and reducer transition semantics were isolated; pre-effect Decision/Consumption and post-effect Outcome contracts were frozen.
- **C254–C261:** crash recovery must be stratified by effect class. Four Stage-A structural paths are deterministic reducer-only transitions at pinned CSSC; current JSONL is terminal-only, so add content-addressed pre/post `ProofWorkspace` snapshots and fail closed for effectful in-doubt actions.
- **C262:** two distinct same-batch ghost-refine proposals are statically reachable sequentially in the real action runtime: first no-op leaves workspace version unchanged, sibling remains cache-valid, no second generation occurs, and `attribute_proposal_batch()` runs again on the same physical provider batch.
- **C263:** exact characterization/migration oracle is fixed: one model-like generation call, two refine selections, no structural checker cost; current final provider `action_id` equals consumer 2, migrated design keeps immutable physical events plus two append-only batch-consumption edges.
- **C264:** ghost refine is valid-but-nonapplicable, not malformed input: proposal validation checks alignment shape but live-hit detection is reducer-owned. Future legal support must distinguish frontier-valid from `WOULD_NOOP`.
- **C265:** target-step-loss is part of the causal chain enabling the sibling no-op path, which is why fixing it must be substrate-versioned separately from logging equivalence.
- **C266:** executable validation was not claimed because the local test container cannot resolve external GitHub; connector source inspection was exact, and the regression is fully specified for the next executable-capable environment.

## Exact continuation

1. Run C263 unchanged in an executable-capable environment; characterize current overwrite before migration.
2. Implement immutable physical provider events + append-only consumption edges; rerun C263 migrated oracle.
3. Implement/freeze `WorkspaceSnapshotV0` canonicalization and round-trip/hash tests; transactionally bind pre snapshot to Decision/Consumption and post snapshot to Outcome.
4. Implement/shared-test reducer transition preparation/report logic and `RecoveryClassV0`, including pure-reducer recovery and effectful-in-doubt fail-closed cases.
5. Run F0–F7 fault injection, add target-step preservation only as separate substrate version, and verify epsilon=0 `SemanticRunProjectionV0` equivalence with independent logging RNG.
6. Only after all pre-randomization tests pass, run the frozen deterministic provider pilot and apply the Stage-A gate; do not run epsilon>0 earlier.
7. Continue narrow public-source falsification/simplification searches and keep frontier nonempty. `2026-08-26T1802JST-followup.md` is newest and is not global completion.

Do not read legacy `research_workers/reasoning/`, O/O-derived state, comparator/integrator/index/feed/audits, other-worker state/config, shared execution ledger, or other-role receipts.
