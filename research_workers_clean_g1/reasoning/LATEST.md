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
54. `2026-08-26T1802JST-followup2.md`
55. `2026-08-26T1802JST-followup3.md`
56. `2026-08-26T1802JST-followup4.md`
57. `2026-08-26T1802JST-followup5.md`

Read `STATE.md` for the accumulated base, then source-qualified checkpoints above in order as needed. Newest checkpoint supersedes older frontier wording where they conflict.

## Top unresolved frontier

1. In the first environment able to materialize pinned CSSC source, executable-validate the statically proven one-batch/two-ghost-`REFINE_ARGUMENT` path at the real action runtime; then rerun the identical fixture after immutable batch-consumption migration.
2. Extend the causal journal across the *whole* Stage-A causal chain, not only action selection: provider-generation Attempt/physical Receipt/finalized ProposalBatch before Decision; then Decision/BatchConsumption/pre-workspace snapshot before selected reducer; Outcome/post-workspace snapshot after it.
3. Replace mutable provider-batch `metadata.action_id` with immutable physical provider events plus append-only `ProposalBatchConsumptionEventV0`; recovery must reconstruct unconsumed proposal envelopes from durable finalized batches without a second provider call.
4. Add `WorkspaceSnapshotV0` and `RecoveryClassV0`: reducer-only structural actions (`DECOMPOSE`, `PROPOSE_ARGUMENT`, `REFINE_ARGUMENT`, `CHANGE_REPRESENTATION`) replay from exact durable pre-state under the original decision/propensity, with no new RNG draw or provider generation.
5. Before checker/tool-bearing actions enter randomized support, add durable EffectAttempt/EffectReceipt and physical checker-attempt accounting. Current Lean server/subprocess paths expose no durable per-check operation receipt; in-doubt effects stay censored/fail-closed.
6. Correct checker cost accounting before any policy compares checker-bearing actions: current Lean server retry/fallback can consume multiple physical attempts while the controller records only the final `CheckResult.elapsed_seconds`.
7. Rebuild crash-recovery budget availability from durable generation/effect attempts and receipts. Current check/model budget counters are process-local; a committed dispatch reservation remains conservatively consumed after an in-doubt crash.
8. Make every Decision causally self-contained through content-addressed finalized proposal-envelope refs, exact choice-set/baseline rank/admission, transition preview/support, exact rational propensity, recovery class, and pre-workspace snapshot.
9. Treat `_finalize_kind()` loss of generated `target_step_ids` as a separate substrate defect/version. Do not silently fix it inside epsilon=0 journal instrumentation; later prove the fix changes ghost-refine eligibility.
10. Freeze Decision/Consumption/Outcome/WorkspaceSnapshot/RecoveryClass, generation Attempt/Receipt/Batch, effect Attempt/Receipt, physical checker attempt, and `SemanticRunProjectionV0` schemas before randomized outcomes. Execute C229-C288 plus F0–F7 crash/replay/idempotence/RNG-isolation. Epsilon>0 remains forbidden until all pre-randomization contracts pass.
11. Logging-policy v0 remains D0-ranked support <=5, epsilon=1/4 exact rational propensities only after gates; first randomized action support stays reducer-only, even though upstream provider generation is itself an external effect that must be durably journaled.
12. Deterministic provider pilot remains frozen after journal validation: hash-ordered cap 200 eligible tasks, 10k task bootstrap, <=5pp 95% CI half-width, preserving generation/execution/assembly and physical checker retry cost separation. Stage A proceeds only if its prespecified lower-CI gate passes; otherwise Stage B moves upstream to generation/retrieval/model-routing.

## Newest synthesis

- **C229–C253:** target-step loss, mutable provider attribution, missing causal trace identity and reducer transition semantics were isolated; pre-effect Decision/Consumption and post-effect Outcome contracts were frozen.
- **C254–C266:** four selected structural actions are deterministic reducer-only transitions and can be replayed from content-addressed workspace state under the original decision; current JSONL is terminal-only. Two same-batch ghost-refine no-ops are statically reachable sequentially and deterministically overwrite physical provider attribution under current code; exact regression/migration oracles are fixed.
- **C267–C270:** deterministic candidate bytes/path do not make checker execution exactly-once or OPE-safe. Effectful actions need Attempt/Receipt semantics; in-doubt randomized effects retain original propensity but have censored cost/outcome. Keeping the first selected-action support reducer-only removes this confound.
- **C271–C276:** current checker cost is a post-return summary with no check operation ID. Lean server retries/fallback can consume multiple physical attempts while only the final elapsed result is recorded. Add physical checker-attempt events and retry/fallback fault injection before checker-bearing actions enter learned support.
- **C277–C282:** Lean LSP proof checks are `didOpen/didClose` notifications keyed only by volatile URI/document-version state; subprocess checks likewise have no durable application receipt. Budget reservations are volatile counters. After crash, distinguish admission reservation, physical cost, and policy outcome; do not reset or zero-fill in-doubt effects.
- **C283–C288:** Decision journaling alone is not crash-safe because provider generation happens before selection and current provider events/cache are also in memory. Add durable generation Attempt/physical Receipt/finalized proposal-batch envelopes before Decision. The proposal cache becomes a derived view; recovery must reuse already-paid finalized proposals and never regenerate merely to reconstruct siblings.

## Exact continuation

1. Run C263 unchanged in an executable-capable environment; characterize current overwrite before migration, then verify two immutable consumption edges after migration.
2. Specify/implement generation Attempt/physical Receipt/`ProposalBatchFinalizedV0`, including crash windows before dispatch, after dispatch, after response, after Receipt, and before first Decision.
3. Implement `WorkspaceSnapshotV0` canonical round-trip/hash tests; bind pre snapshot atomically to Decision/Consumption and post snapshot to Outcome.
4. Implement reducer transition reports and `RecoveryClassV0`; pure reducer replay must use the frozen selected proposal and original decision identity.
5. Implement effect Attempt/Receipt plus physical checker attempt aggregation and durable budget reconstruction; keep checker-bearing action randomization disabled until tested.
6. Add target-step preservation only as a separate substrate version and verify its eligibility effect.
7. Run all F0–F7 and expanded generation/checker crash tests; verify epsilon=0 `SemanticRunProjectionV0` equivalence with no extra provider/checker calls and independent logging RNG.
8. Only after all pre-randomization tests pass, run the frozen deterministic provider pilot and apply the Stage-A gate; do not run epsilon>0 earlier.
9. Continue narrow public-source falsification/simplification searches and keep frontier nonempty. `2026-08-26T1802JST-followup5.md` is newest and is not global completion.

Do not read legacy `research_workers/reasoning/`, O/O-derived state, comparator/integrator/index/feed/audits, other-worker state/config, shared execution ledger, or other-role receipts.
