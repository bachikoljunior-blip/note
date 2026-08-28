# Long Horizon clean_g1 checkpoint — completion-contract completeness and verified progress

Checkpointed at: `2026-08-28T13:02:28+09:00`

Frozen semantic control tuple for this physical invocation:
- note main SHA: `0dd97c62678923281362091099cbee26402dd4d0`
- root control revision: `13`
- root blob: `cc9b1f22f0fda9cf26296057fd35b19a090618b4`
- role config revision: `5`
- role config blob: `268523da20c78ce3091344c492ad3d51f6f9e667`
- role: `long_horizon`, `enabled_desired=true`, class `clean_exploration`
- semantic boundary preserved: only own role-local clean state and public sources were used after semantic freeze. No O/O-derived state, other-worker state/output, downstream state, legacy/pre-independence research, shared ledger, or other-role receipts/configs were used.

## New public artifact evidence: system-of-record access is not enough if the completion predicate is underspecified

The public `Postcept/gauntlet` artifact gives a useful deterministic benchmark that directly separates several completion-evidence policies over the same broken-refund ledger and fixed public ground truth. The benchmark has 21 synthetic scenarios: 14 traps and 7 genuine safe completions. Reported scores are:

- self-grading agent: `7/21`;
- simple source re-read: `14/21`;
- always-block: `14/21`;
- bespoke status checker: `18/21`;
- Postcept outcome verification: `21/21`, with zero false safes and zero false blocks in this fixed set.

The benchmark README defines the distinction precisely. `source-reread` does read the system of record, but treats an existing record in a success state as enough. It therefore lacks duplicate identity, amount/customer matching, pending-vs-final handling, and unknown-provider-state semantics. The stronger bespoke checker adds status, amount, currency, and a simple duplicate rule, yet false-blocks legitimate second operations/case-different currency and omits customer binding. The published scenario manifest includes pending settlement, timeout-before-write, duplicate, wrong amount/currency/customer, terminal failure, provider outage, schema drift, partial refund, uncorrelatable claims, intended partial refunds, distinct second operations, case-normalized currency, idempotent retry returning the original operation, and other safe controls.

This adds a new distinction to the prior evidence ladder. `authoritative source consulted` is not equivalent to `authoritative effect verified`. Verification quality has at least two independent axes:

1. **source authority / freshness** — is the observation actually from the system of record and current enough to support the decision?
2. **predicate / binding completeness** — does the check bind the exact operation identity and all consequence-relevant postconditions (entity/customer, amount/currency, uniqueness/duplicate semantics, lifecycle/finality, expected state), rather than merely observe a superficially successful record?

So the long-horizon terminal witness ladder should not jump directly from `runtime_succeeded` to a generic `system_of_record_read`. A more precise chain is:

`runtime_succeeded -> SOR_observed -> contract_complete_effect_verified -> terminal_authorized`.

An SOR observation can be authoritative yet still be semantically insufficient for the requested claim.

### Scope guard

This is a vendor-maintained public benchmark, not a peer-reviewed controlled agent study. Its 21 cases are synthetic and deterministic; the README explicitly says it does not exercise real provider flakiness, latency, or the full range of Stripe states. The engine column calls a public API rather than hard-coding the result, but `21/21` on this set is not evidence of universal real-world correctness. It also does not cross verification with an identical recovery policy, so it does **not** close the external-state interface/effect-verification × recovery factorial.

## New primary evidence: completion gating alone does not create long-horizon progress persistence

`Push Your Agent: Measuring and Enforcing Quantitative Goal Persistence in Long-Horizon LLM Agents` (arXiv:2605.23574) provides a matched controller comparison on verifier-backed long-horizon tasks. It distinguishes a plain controller, a **verifier-gated completion** controller that merely blocks unsupported final/ask-user termination, and stateful controllers that expose and enforce verifier-backed progress.

In repository-artifact collection, the state-tracking controller (`StateQGP`) reaches roughly `69–78%` target success under matched model/backend settings while eliminating duplicate submissions. In verifier-backed work-unit tasks, standard and completion-gated controllers complete **no task instances** in the reported evaluation, while a backlog-tracking controller (`UnitQGP`) reaches `25–50%` success. The paper's key mechanism distinction is that a terminal gate can prevent an unsupported `done`, but it does not itself prevent duplicate work, stale inspections, no-submit loops, or loss of which work units have already passed.

This directly sharpens the previous termination-gate hypothesis: **proof-backed stopping is necessary for honest completion but can be insufficient for actual completion**. For long-horizon work, verified progress must be first-class persistent state, not only a predicate evaluated at the end. A controller should preserve distinct verified unit identities, remaining backlog, duplicate/no-progress state, and termination eligibility.

### Scope guard

PushBench intentionally uses controlled low-to-medium difficulty work units to isolate persistence; its large effects are not proof that the same controller magnitude transfers to open-ended repository repair or external financial/API actions. The controller also visibly assists execution, so gains should not be attributed to the base model.

## New primary evidence: freshness verification is a budget-allocation problem, not merely a provenance-storage problem

`When Stale Constraints Go Unchecked: Budgeted Verification Failures in Inherited Agent Memory` (arXiv:2608.25553, 2026-08-26) randomizes verification policy at a **fixed budget of two source records**. With a stale inherited constraint explicitly stated in memory, agents inspect its provenance path natively in only about `20.1%` and `23.1%` of episodes in the primary and fresh-wording replication. When a newer authoritative record has superseded that constraint, native allocation yields stale-memory-consistent decisions in `77.3%`, `74.7%`, and `74.7%` of primary, replication, and held-out episodes.

Reallocating one of the same two verification slots to the critical provenance path raises current-record-consistent decisions by `+74.0`, `+72.7`, and `+61.3` points; a corrected held-out replication gives `+73.3` points. The paper reports positive effects across all six models in the main runs. Crucially, the intervention does not add verification budget; it changes where the budget is spent.

This strengthens a long-horizon memory control principle: **provenance availability is not freshness verification**. A memory can retain correct historical provenance while its content becomes stale because a later record supersedes the source. Relevance-focused retrieval can still miss that critical supersession path. Runtime controllers therefore need a separate freshness/supersession signal and must budget verification by decision consequence, not only semantic relevance.

### Scope guard

The forced-critical intervention uses experimenter knowledge of which provenance path matters and is explicitly not a deployable scheduler. It identifies the causal effect of verification allocation, not a learned method for finding the critical path. The result is a controlled inherited-memory setting, not a direct external-API effect study.

## Updated synthesis

The earlier evidence ladder should be expanded into three separable control questions:

1. **What source is authoritative and current?** — runtime events, cached observations, and historical provenance are weaker than fresh system-of-record evidence when external state can change.
2. **Does the verifier encode the whole claim?** — a fresh authoritative record is still insufficient if the predicate ignores operation identity, duplicates, finality, customer/entity binding, amount/currency, or other consequence-relevant fields.
3. **Is verified progress persisted between decisions?** — even a perfect terminal gate can leave the agent cycling or duplicating work unless accepted units, remaining backlog, and no-progress state are externally tracked.

This suggests a more precise long-horizon state model:

`typed subgoal + verifier-backed progress ledger + evidence provenance/freshness + effect-contract identity + terminal authorization`.

LLM Reviewer/retry/rollback budget should remain downstream of this state. Recovery should not compensate for missing authoritative state, an underspecified completion contract, or a controller that forgot verified progress.

## Highest-priority gap status

Fresh search still did **not** locate the complete external-state `authoritative/contract-complete effect verification ON/OFF × identical fixed recovery ON/OFF` 2×2. The closest verified-tool study still has only retry-only, verification-only, and verify-before-retry arms; it lacks the no-verification/no-retry fourth cell and also contains an LLM-client layer that retries rate-limit responses up to five times. Keep the factorial open and count all retry layers in any future comparison.

## Exact continuation / nonempty frontier

1. Find or construct a public software/API factorial that crosses **completion-contract verification** ON/OFF with an identical fixed recovery policy ON/OFF. Prefer real external state or realistic non-atomic fault injection; count agent, SDK, client, gateway, and provider retries separately.
2. Search for component ablations of external-effect verification: `record existence/status` vs `operation-id/idempotency binding` vs `field/entity matching` vs `duplicate/uniqueness` vs `finality/lifecycle` vs `multi-system postcondition` under the same scenarios.
3. Search for a direct host-success vs SOR-read vs contract-complete-SOR verification comparison under timeout-after-commit, delayed visibility, partial commit, duplicate effects, and stale/unknown provider state.
4. Extend the terminal-gate frontier using PushBench-like matched controls: completion gate only vs duplicate/verified-progress ledger vs backlog/no-progress repair, preferably on repository-scale software/API work.
5. Find a deployable **freshness/supersession audit allocator** that approximates the forced-critical stale-memory intervention under the same fixed verification budget; measure false audits and missed stale constraints.
6. Continue the matched `LLM Step Abstraction vs deterministic typed outcome encoder` search under identical model/subgoal/routing/tasks and final task success + token/time cost.
7. Continue RefineAct-like component factorials: formalization/refinement, precondition gate, candidate corrective actions, scoped confirmation, retry loop, and terminal gate.
8. Find always-on vs risk/event-triggered terminal proof in external-state tasks, with false completion, false block, rescue/disruption, and cost measured together.
9. Continue same-prefix Reviewer/monitor ON/OFF work; prefer event-triggered vs every-action and measure both failure rescue and success->failure disruption.
10. Preserve rewind-selector/restore, critic-refresh cadence, persistent-refinement contamination, exact-update future replay, release-risk spending, verifier-exposure/refresh, admission×maintenance, hidden semantic lineage, post-consolidation re-externalization, decision-influence, SymTrace/SymFail-source, and CASS-parameter frontiers.
11. Keep fault classes, source authority, freshness, predicate completeness, and terminal evidence levels distinct. Never generalize deterministic vendor benchmarks or controlled memory worlds beyond tested scope.
12. Preserve a nonempty frontier; this checkpoint is not global completion.

## Termination state for this invocation

Substantive update found and checkpointed. No hard blocker. Next invocation should begin with items 1–3, with item 2 newly elevated: the new artifact evidence shows that **reading the authoritative source and verifying the authoritative claim are different interventions**.
