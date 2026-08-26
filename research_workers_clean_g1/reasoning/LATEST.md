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
58. `2026-08-26T1802JST-followup6.md`
59. `2026-08-26T1802JST-followup7.md`

Read `STATE.md` for the accumulated base, then source-qualified checkpoints above in order as needed. Newest checkpoint supersedes older frontier wording where they conflict.

## Top unresolved frontier

1. In the first environment able to materialize pinned CSSC source, executable-validate the statically proven one-batch/two-ghost-`REFINE_ARGUMENT` path at the real action runtime; then rerun the identical fixture after immutable batch-consumption migration.
2. Extend the causal journal across the whole run identity + Stage-A causal chain: durable `RunInstanceV0`; retrieval/summarization/generation effects as configured; provider-generation Attempt/physical Receipt/finalized ProposalBatch; Decision/BatchConsumption/pre-workspace snapshot; reducer execution; Outcome/post-workspace snapshot.
3. Replace mutable provider-batch `metadata.action_id` with immutable physical provider events plus append-only `ProposalBatchConsumptionEventV0`; recovery must reconstruct unconsumed proposal envelopes/consumption history without another provider call.
4. Add `WorkspaceSnapshotV0` and `RecoveryClassV0`: reducer-only structural actions replay from exact durable pre-state under the original decision/propensity and original policy RNG stream, with no new provider generation.
5. Before checker/tool-bearing actions enter randomized support, add durable EffectAttempt/EffectReceipt and physical checker-attempt accounting. Current Lean server/subprocess paths expose no durable per-check receipt; current server retry/fallback can also undercount physical wall cost.
6. Freeze optional upstream substrate: `ChatContextSummarizer` can make an uncounted model call inside proposal-generation metadata, and generic retrieval has unspecified effect/cost semantics. Disable these in matched initial arms or instrument their physical effects before claiming complete cost vectors.
7. Rebuild crash-recovery budget availability from durable run/effect attempts and receipts. Current check/model counters and current sample/proposal IDs are process-local; committed in-doubt dispatches stay conservatively reserved after restart.
8. Model controller state as workspace + durable proposal envelopes + consumed set/history + budget/effect state. `workspace NO_MUTATION` is not a global no-op because selected proposal consumption changes future scheduler state.
9. Initial behavior randomization occurs only when D0 itself selects a verified pure-reducer action and at least one additional safe alternative exists. If D0 is effectful/unsupported, execute D0 with propensity 1; never silently replace it with a structural action.
10. Make every Decision causally self-contained through content-addressed finalized proposal-envelope refs, exact choice set/baseline rank/admission, transition dimensions, exact rational propensity, recovery class, and pre-workspace snapshot.
11. Treat `_finalize_kind()` loss of generated `target_step_ids` as a separate substrate defect/version. Do not silently fix it inside epsilon=0 journal instrumentation; later prove the fix changes ghost-refine eligibility.
12. Freeze all schemas before randomized outcomes and execute C229-C301 plus F0–F7 and expanded generation/checker/recovery/RNG tests. Epsilon>0 remains forbidden until all pre-randomization contracts pass.
13. Logging-policy v0 at eligible states: support <=5; epsilon=1/4; `mu(D0)=3/4+(1/4)/L`, alternatives `(1/4)/L`; at ineligible states `mu(D0)=1`. Persist exact numerator/denominator and support hashes.
14. Deterministic provider pilot remains frozen after journal validation: hash-ordered cap 200 eligible tasks, 10k task bootstrap, <=5pp 95% CI half-width, preserving generation/execution/assembly and physical checker retry costs. Add secondary diagnostics for actual randomizable-decision coverage without post-hoc changing the primary gate.

## Newest synthesis

- **C229–C266:** target-step loss, mutable provider attribution, missing causal trace identity and reducer transition semantics were isolated. Four structural actions are reducer-only and recoverable from durable exact state. Two same-batch ghost-refine no-workspace-mutation actions are statically reachable sequentially and overwrite current provider attribution; exact regression/migration oracles are frozen.
- **C267–C282:** deterministic candidate materialization is not exactly-once checker execution. Checker events are post-return only, Lean server retries/fallback can undercount physical cost, LSP proof checks have no durable check request/receipt, and budget reservations are process-local. Keep checker-bearing randomized actions fail-closed/out of initial support.
- **C283–C288:** action Decision journaling alone is insufficient: provider generation and proposal cache creation occur before selection and are currently volatile. Add generation Attempt/physical Receipt/finalized content-addressed proposal batches; cache/frontier become derived views over durable envelopes + consumed edges + recovered workspace.
- **C289–C295:** current run/sample/proposal IDs are process-local UUID/index derivatives. Add durable `RunInstanceV0` with frozen policy/RNG/substrate identity. Optional ChatContextSummarizer can make an unaccounted model call and generic retrieval can be effectful; freeze or instrument both before compute-normalized claims.
- **C296–C301:** safe Stage-A behavior must preserve D0 support. Randomize only when D0 itself is in verified pure-reducer support; otherwise D0 is deterministic. Split workspace transition, proposal consumption and external effect semantics because `NO_MUTATION` still consumes a proposal and changes future controller state. Persist exact rational mixed propensities and decision-level coverage diagnostics.

## Exact continuation

1. Run C263 unchanged in an executable-capable environment; characterize current overwrite before migration, then verify two immutable consumption edges after migration.
2. Implement/freeze `RunInstanceV0`, stable policy RNG/event identity, generation Attempt/physical Receipt/`ProposalBatchFinalizedV0`, including retrieval/summarizer effect declarations.
3. Implement `WorkspaceSnapshotV0` canonical round-trip/hash tests; bind pre snapshot atomically to Decision/Consumption and post snapshot to Outcome.
4. Implement reducer transition dimensions and `RecoveryClassV0`; include consumed-set/proposal-envelope state in recovery and `SemanticRunProjectionV0`.
5. Implement effect Attempt/Receipt, physical checker attempt aggregation and durable budget reconstruction; keep checker-bearing randomization disabled until tested.
6. Add mixed-support behavior tests: effectful D0 => propensity 1; pure D0 + safe alternatives => exact epsilon distribution; unsupported learned target => D0 fallback.
7. Add target-step preservation only as a separate substrate version and verify its eligibility effect.
8. Run all F0–F7 and expanded upstream/effect crash tests; verify epsilon=0 semantic equivalence with no extra hidden/provider/checker calls and independent logging RNG.
9. Only after all pre-randomization tests pass, run the frozen deterministic provider pilot and apply the Stage-A gate; do not run epsilon>0 earlier.
10. Continue narrow public-source falsification/simplification searches and keep frontier nonempty. `2026-08-26T1802JST-followup7.md` is newest and is not global completion.

Do not read legacy `research_workers/reasoning/`, O/O-derived state, comparator/integrator/index/feed/audits, other-worker state/config, shared execution ledger, or other-role receipts.
