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
60. `2026-08-26T1802JST-followup8.md`
61. `2026-08-26T1802JST-followup9.md`
62. `2026-08-26T1802JST-followup10.md`
63. `2026-08-26T1802JST-followup11.md`
64. `2026-08-26T1832JST.md`

Read `STATE.md` for the accumulated base, then source-qualified checkpoints above in order as needed. Newest checkpoint supersedes older frontier wording where they conflict.

## Top unresolved frontier

1. In the first environment able to materialize pinned CSSC source, executable-validate the statically proven one-batch/two-ghost-`REFINE_ARGUMENT` path at the real action runtime; then rerun the identical fixture after immutable batch-consumption migration.
2. Extend the causal journal across the entire run identity and generation/selection chain: durable `RunInstanceV0`; configured retrieval/summarization/tool effects; provider-generation Attempt/physical Receipt/finalized ProposalBatch; BehaviorSelection/Decision/BatchConsumption/pre-workspace snapshot; reducer execution; Outcome/post-workspace snapshot.
3. Replace mutable provider-batch `metadata.action_id` with immutable physical provider events plus append-only `ProposalBatchConsumptionEventV0`; recovery must reconstruct unconsumed finalized proposal envelopes and consumption history without another provider call.
4. Add `WorkspaceSnapshotV0` and `RecoveryClassV0`: reducer-only structural actions replay from exact durable pre-state under the original decision/propensity and RNG stream, with no re-selection or provider regeneration.
5. Before checker/tool-bearing actions enter randomized support, add durable EffectAttempt/EffectReceipt and physical checker-attempt accounting. Current Lean server/subprocess paths expose no durable per-check receipt; server retry/fallback can undercount physical wall cost.
6. Freeze or fully instrument optional upstream effects. `ChatContextSummarizer` can make an unmetered model call, generic retrieval has unspecified effect/cost semantics, and chat proposal generation can run real scratch Lean checks through tool loops that bypass `BudgetManager.reserve_check()`.
7. Rebuild crash-recovery budget availability from durable run/effect attempts and receipts. Current check/model counters and current sample/proposal IDs are process-local; committed in-doubt dispatches remain conservatively reserved after restart.
8. Add a versioned `EffectContractV0` for every effectful substrate edge: hard mechanical `P_effect`, tri-valued `Q_effect=TRUE/FALSE/UNKNOWN`, explicit provider idempotency/query capability and provenance. Never infer `FALSE` from an ambiguous response.
9. Extend crash tests with timeout-after-dispatch (`Q=TRUE`), delayed visibility (`Q=UNKNOWN`), and confirmed absence (`Q=FALSE`). Assert no redispatch from `UNKNOWN`; without a real provider idempotency/query contract, keep in-doubt attempts reserved/censored.
10. Model controller state as workspace + durable proposal envelopes + consumed set/history + budget/effect state. Workspace `NO_MUTATION` is not a global no-op because selected proposal consumption changes future scheduler state.
11. Insert `BehaviorSelectionV0` only after one frozen `select_admissible_action()` result and before frontier consumption. D0 is the first effectively feasible ranked node, not necessarily raw rank 0. Preserve `remaining_budget_policy` semantics exactly.
12. Randomize only when D0 itself selects a verified pure-reducer action and at least one additional safe, effectively budget-feasible alternative exists. If D0 is effectful/unsupported, execute D0 with propensity 1; never silently substitute a structural alternative.
13. Preserve legacy runtime node IDs for epsilon=0 equivalence even though they hash full telemetry-bearing proposal metadata and can affect tie-breaks. Add telemetry-independent `semantic_proposal_sha256`, execution-envelope hash, and full observation-envelope ref; use semantic identity for exploration dedupe and learning, exact legacy node/envelope identity for replay.
14. Treat `_finalize_kind()` target-step loss and semantic-node/tie-break identity as separate later substrate versions. Do not silently fix either inside initial logging instrumentation.
15. Make provider cost completeness cross-dimensional: ambiguous transport retries without provider receipts make total token use and total API charge incomplete; known final-response charge is only a component/lower bound, not a complete total.
16. Split cost accounting at least into proposal-generation provider cost, generation tool/retrieval/summarizer cost, selected-action execution/checker cost, and assembly/verification cost. A zero-check structural action may still be preceded by substantial generation scratch-check compute.
17. Freeze all schemas before randomized outcomes and execute C229-C336 plus F0–F7 and expanded generation/checker/tool/recovery/RNG tests. Epsilon>0 remains forbidden until all pre-randomization contracts pass.
18. Logging-policy v0 at eligible states: support <=5; epsilon=1/4; `mu(D0)=3/4+(1/4)/L`, alternatives `(1/4)/L`; at ineligible states `mu(D0)=1`. Persist exact numerator/denominator, support hashes, baseline D0 ID and behavior-selected ID.
19. Deterministic provider pilot remains frozen after journal validation: hash-ordered cap 200 eligible tasks, 10k task bootstrap, <=5pp 95% CI half-width, preserving all cost compartments and physical retry completeness. Initial matched arms should disable generation tools/summarizer/remote retrieval unless fully instrumented. Add secondary diagnostics for actual randomizable-decision coverage without post-hoc changing the primary gate.
20. Keep hard legal/effect masks deterministic. Learned contracts or value models may only rank/prune exploratory alternatives inside the verified-safe set; they must never grant capability. Add provenance/runtime-parity checks before any learned effect contract can influence support construction.
21. Add deterministic journal coverage verification before any learned failure monitor: every selected effect has an Attempt identity, every committed transition has a verified postcondition/Receipt or exact reducer transition, and every required effect is terminal or explicitly censored.

## Newest synthesis

- **C229–C266:** target-step loss, mutable provider attribution, missing causal trace identity and reducer transition semantics were isolated. Four structural actions are reducer-only and recoverable from durable exact state. Two same-batch ghost-refine no-workspace-mutation actions are statically reachable sequentially and overwrite current provider attribution; exact regression/migration oracles are frozen.
- **C267–C282:** deterministic candidate materialization is not exactly-once checker execution. Checker events are post-return only, Lean server retries/fallback can undercount physical cost, LSP proof checks have no durable check request/receipt, and budget reservations are process-local. Keep checker-bearing randomized actions fail-closed/out of initial support.
- **C283–C301:** action Decision journaling alone is insufficient because provider generation, optional retrieval/summarization and proposal-cache creation occur before selection and are currently volatile. Add durable RunInstance, generation Attempt/physical Receipt/finalized proposal batches, content-addressed workspace state and consumed-set recovery. Safe behavior must preserve D0 support and exact rational propensity; workspace no-mutation still changes controller state through proposal consumption.
- **C302–C307:** the clean selector insertion seam is after one frozen budget-constrained baseline selection and before frontier consumption. D0 is first effectively feasible node. Preserve raw/effective budget admission, trace both D0 and behavior action, and keep the selector a narrow wrapper over the fixed substrate.
- **C308–C313:** current OpenAI-compatible retries have no provider idempotency contract. Ambiguous transient failures can duplicate remote execution/billing; physical attempt telemetry is post-hoc. Cost completeness must fail closed across tokens and dollars when an earlier retry is ambiguous.
- **C314–C320:** legacy node IDs hash full proposal metadata, including provider UUID/telemetry, and are used as tie-breaks. Preserve them for baseline equivalence but add separate semantic/execution/observation identities; prevent raw transport IDs from leaking into learned features. Semantic tie-break is a separate future substrate change.
- **C321–C328:** generation itself can run real Lean scratch checks through model tool loops. These checks bypass coarse controller check reservation and can exceed static model-route priors. Add explicit generation-tool-check Attempt/Receipt/cost scope, or disable tools in initial matched arms; in-memory duplicate suppression is not crash replay safety.
- **C329–C336:** public execution-reliability evidence sharpens one unified effect contract. Separate effect truth from response truth; use read-only tri-valued postconditions; do not redispatch from `UNKNOWN`; treat provider idempotency as an external capability, not a local hash. Hoare-style pre/post contracts can unify legal gating and commit verification. Learned contracts are useful inside the safe set but are not exact enough to become the hard mask; contract integrity and runtime effect verification are load-bearing. Deterministic causal-journal invariants should precede learned failure monitors.

## Exact continuation

1. Run C263 unchanged in an executable-capable environment; characterize current overwrite before migration, then verify two immutable consumption edges after migration.
2. Implement/freeze `RunInstanceV0`, stable policy RNG/event identity, generation Attempt/physical Receipt/`ProposalBatchFinalizedV0`, including explicit retriever/summarizer/tool configuration and physical tool-check receipts where enabled.
3. Implement `WorkspaceSnapshotV0` canonical round-trip/hash tests; bind pre snapshot atomically to Decision/Consumption and post snapshot to Outcome.
4. Implement reducer transition dimensions and `RecoveryClassV0`; include durable proposal envelopes + consumed set in recovery and `SemanticRunProjectionV0`.
5. Add canonical `EffectContractV0` (`P_effect`, tri-valued `Q_effect`, idempotency/query capability, provenance) and map effect Attempt/Receipt recovery onto it. Preserve `UNKNOWN` instead of coercing it to failure.
6. Implement effect Attempt/Receipt, physical checker retry/fallback aggregation, generation-tool-check accounting and durable budget reconstruction; keep checker-bearing selected-action randomization disabled until tested.
7. Add `BehaviorSelectionV0` around existing budget selection; test rank-0 budget denial, `remaining_budget_policy=false`, effectful-D0 deterministic fallback, pure-D0 epsilon support, exact rational propensities and unsupported-target fallback.
8. Add semantic/execution/observation proposal identities while leaving legacy node IDs unchanged; test that telemetry-only UUID differences change legacy IDs but not semantic IDs.
9. Add target-step preservation and semantic-node tie-break only as separate substrate versions, with explicit behavior-change regressions.
10. Add deterministic journal coverage verifier and non-atomic effect tests; learned contracts/monitors remain advisory inside the mechanically safe set.
11. Run all F0–F7 and expanded provider retry, generation tool, checker and crash tests; verify epsilon=0 semantic equivalence with no extra hidden/provider/checker/tool calls and independent logging RNG.
12. Only after all pre-randomization tests pass, run the frozen deterministic provider pilot and apply the Stage-A gate; do not run epsilon>0 earlier.
13. Continue narrow public-source falsification/simplification searches, especially formal-proof/code-agent systems that let learned masks authorize effects and report unsafe-exposure/false-negative rates. `2026-08-26T1832JST.md` is newest and is not global completion.

Do not read legacy `research_workers/reasoning/`, O/O-derived state, comparator/integrator/index/feed/audits, other-worker state/config, shared execution ledger, or other-role receipts.
