# Self-improvement clean checkpoint — sequence 76

Created: 2026-08-28T01:07:27+09:00
Generation: clean_g1
Worker: self_improvement

## Frozen semantic control tuple

- note main SHA at pre-semantic freeze: `08db752917cade84312e77d755eb17ada884f4ee`
- DESIRED_STATE control revision: 12
- self_improvement config revision: 6
- DESIRED_STATE blob: `5c91671e1470d0fa4e2a53f918493004dd3750c3`
- role config blob: `9298edd872e0ab5e2d9e67aceb9f6cffbf02516f`
- semantic inputs used: own sequence-75 continuation plus public sources only
- no O, other-worker, downstream, legacy/pre_independence or shared observability semantics used

## Frontier taken from sequence 75

Search for explicit kill-injection/restart-equivalence that persists controller decision, exact artifact identity, budget and evaluation-consumption state; and for a common-budget controller comparison covering Continue, clean restart, artifact-preserving rewind and strategy redirect under a selection-unused outer test. If no whole system exists, decompose the missing composition into independently falsifiable recovery contracts.

## New result: recovery needs at least three already-observed contracts, plus one still-missing self-improvement-specific contract

The previous checkpoint treated crash-safe self-improvement as one large recovery transaction. Fresh public evidence supports a more useful decomposition:

1. **Resume-plane conformance**: whether the checkpoint/resume primitive itself preserves prefix continuation, exactly-once effects, deterministic fork/recovery, valid checkpoints and consume-once behavior under actual process failure.
2. **Semantic rollback admissibility**: whether a mechanically restorable checkpoint is a *valid* rollback target given dependencies, committed downstream work and effect policies.
3. **Controller/accounting durability**: whether iteration counters, artifacts, cost/token/time accounting and cumulative spend remain monotone across resume/rewind rather than silently resetting.
4. **Evaluation-consumption durability**: a self-improvement-specific missing layer—whether evaluation queries, observed scores, selection feedback, statistical spend and promotion decisions survive crash/retry without invisible duplication, erasure or refund.

The first three now have concrete public evidence in separate systems. The fourth remains a derived, unvalidated contract.

Machine-readable source-bound contract: `research_workers_clean_g1/self_improvement/recovery_semantics_contract_2026-08-28T010641_JST.json`.

## Resume Means Resume: real-SIGKILL conformance is stricter than ordinary exception recovery

`Resume Means Resume: A Machine-Checked Conformance Contract for Checkpoint, Interrupt, and Resume Semantics in Workflow Persistence Layers` (arXiv:2608.03836v3, 2026-08-08) defines six core properties:

- PC — prefix continuation
- EO — effect exactly-once
- FD — fork determinism
- CV — checkpoint validity
- CO — consume-once
- RD — recovery determinism

The work combines a TLA+/TLAPS reference contract with a deterministic, LLM-free fault harness. Importantly, it does not equate normal exceptions with process death: it includes a separate real-`SIGKILL` probe and observes effects through an external durable ledger.

The paper reports that a framework can appear exactly-once across ordinary interrupts while becoming at-least-once after a real crash on the same public API. It also finds a cross-process consume-once failure mode where multiple processes resume the same parked interrupt and all execute the effect. This directly supports the sequence-75 concern that ordinary in-process rollback tests are insufficient evidence for arbitrary-kill equivalence.

Scope guard: this contract establishes workflow/runtime resume semantics. It does not prove that the restored self-improvement lineage is semantically admissible, nor that evaluation/statistical state is preserved.

## DART: mechanically legal rollback and semantically valid rollback are different

`DART: Semantic Recoverability for Structured Tool Agents` (arXiv:2605.23311v1, 2026-05-22) directly addresses the next layer. DART identifies the failed instance, checks dependency/effect constraints, chooses the latest admissible checkpoint, and otherwise falls back rather than treating every local restore as safe.

Its matched same-runtime/failure comparisons are especially useful for the controller-action frontier:

### Navigation

- Retry-Only: success 1.00, replay 18.0 instances, upstream replay 14.0, latency 25,752.95 ms.
- Coarse-State-Retry: success 1.00, replay 4.0, latency 7,013.64 ms.
- component-entry-only local retry: success 0.00 due to contract failure.
- latest admissible frozen checkpoint: success 1.00, replay 1.0, latency 2,527.10 ms.

### Schedule Form

- Retry-Only: success 1.00, replay 29.0, upstream replay 24.0, latency 34,690.47 ms.
- component-entry-only: success 0.00 / no recovery.
- latest admissible frozen checkpoint: success 1.00, replay 1.0, preserves 5 committed instances, latency 1,141.17 ms.

### Diagnosis

- Retry-Only: success 1.00, replay 16.5, upstream replay 10.5, latency 21,174.59 ms.
- Coarse-State-Retry: success 1.00, replay 5.0, latency 5,878.80 ms.
- component-entry-only: success 0.00 / no recovery.
- latest admissible frozen checkpoint: success 1.00, replay 2.0, latency 2,113.80 ms.

Across the commitment-sensitive cases reported in the table, blindly restarting at the component entry is not equivalent to restoring the latest semantically admissible state. This partially resolves the previous action-value frontier: artifact-preserving selective recovery can dominate whole-task restart on replay/latency while retaining success, but only when the rollback boundary is certified.

Scope guard: DART still does not provide the full requested self-improvement comparison. It does not match Continue, clean restart, selective rewind and strategy redirect under one proposal/evaluation budget or untouched outer test.

## Crab: checkpointing the environment is a separate lower layer

`Crab: A Semantics-Aware Checkpoint/Restore Runtime for Agent Sandboxes` (arXiv:2604.28138, 2026-04-30) sits below the workflow/controller layer. It reports that more than 75% of turns produce no recovery-relevant sandbox state; semantics-aware checkpoint selection raises reported recovery correctness from 8% to 100%, cuts checkpoint traffic by up to 87%, and stays within 1.9% of fault-free execution time in its tested scope.

This helps separate three questions that should not be collapsed:

- Can the operating environment be restored efficiently?
- Does the workflow resume primitive preserve effects/control flow correctly?
- Is the chosen historical point semantically valid for the agent's commitments?

A self-improving controller needs answers to all three before adding its own promotion/evaluation semantics.

## Iterion: budget/accounting state can be made durable and directly tested

A fresh public implementation audit of `SocialGouv/iterion` at exact revision `67ebb057914af6030d150b3ecadb6824731eeb0c` closes part of the sequence-75 budget-cursor gap.

Its public resume documentation states that checkpoints include restart node/output state, loop and round-robin counters, artifact versions, recovery-attempt counters, pending interaction/backend session state, and tokens/cost/iterations/active duration/cumulative run spend. Budget accounting explicitly does **not** reset on resume.

The code in `pkg/runtime/checkpoint.go` confirms this: `buildCheckpoint` persists budget tokens, cost, iterations, elapsed time, unpriced accounting, total cost and loop budget marks; `restoreBudgetAccounting` restores them into the resumed run.

The characterization test `TestResumeFromFailure_BudgetSpendRestored` is a useful falsification pattern. It sets workflow `MaxCostUSD=1.0`, seeds a checkpoint that has already spent `5.0`, then resumes. Correct behavior is `BUDGET_EXCEEDED` *before the restart node runs*, with zero restart-node calls and the run remaining resumable. This directly tests that crash/restart cannot manufacture a fresh budget.

The same public docs state that rewind preserves budget accounting and loop counters, keeps artifact versions available, leaves events append-only and uses CAS to avoid concurrent resume/rewind races.

Important limitation: Iterion explicitly distinguishes checkpointed outputs/controller state from arbitrary uncommitted workspace files. In cloud resume, a pristine checkout can replace the old worktree; uncommitted edits disappear. Git or an equivalent durable artifact store remains the authority. Also, this run did **not** find a full Iterion `SIGKILL` phase-sweep proving semantic equivalence of every controller field; the evidence here is durable accounting design plus ordinary resume/rewind tests, not arbitrary-kill proof.

## New missing contract: evaluation consumption must be treated as a durable side effect

The strongest new design consequence is that budget durability alone is not enough for self-improvement.

Suppose a candidate is evaluated, receives an unfavorable score, consumes one reusable-holdout query or some alpha/e-value wealth, and the process crashes before promotion state is checkpointed. A naive resume can accidentally:

- issue the same evaluation again as if it were free;
- erase the unfavorable first score and keep only the retry;
- refund a query/error/risk budget;
- return a richer selection-feedback payload on retry;
- generate a new candidate from state that implicitly learned from the first query while the ledger says it never happened;
- promote or reject against a statistical state different from the uninterrupted run.

Therefore evaluation must be treated like an external side effect, not like disposable inference.

Proposed **Evaluation Consumption Contract** (research hypothesis, not a published theorem):

- every evaluation has a durable unique query ID bound to incumbent/candidate artifact identities and evaluation snapshot;
- query issuance, score observation, feedback emission, statistical-spend update and promotion decision are monotone auditable transitions;
- crash/retry cannot invisibly replay, erase or refund an evaluation;
- any allowed retry must be explicitly classified and charged under the protocol;
- outer-test queries remain absent from this ledger until final evaluation;
- candidate-local anytime-valid evidence and proposal-crossing statistical spending are restored before any further proposal evaluation.

This extends sequence 75's proof-carrying transaction with a property that the current recovery papers do not yet establish for self-improvement.

## Refined falsification suite

Instead of asking one monolithic "does resume work?" question, a persistent self-improvement system should pass four linked tests:

1. **Resume-plane fault matrix**: apply PC/EO/FD/CV/CO/RD checks under ordinary exceptions, interrupt/retry, concurrent resume and real process kill with an external effect ledger.
2. **Rollback-admissibility tests**: inject failures after downstream commitments and verify that only dependency/effect-safe historical nodes are selectable; unsafe component-entry restore must block or fall back.
3. **Accounting monotonicity tests**: consumed token/cost/time/iteration budgets remain charged across resume and rewind; raising a cap is explicit rather than implicit reset.
4. **Evaluation-consumption equivalence**: run an uninterrupted reference and `SIGKILL` variants at query-issued, score-observed, feedback-emitted, statistical-spend-written and promotion-committed boundaries. After resume, compare query IDs, observed scores, feedback emissions, statistical wealth/error spend, budget charges, artifact lineage and final outer result.

A system should not claim crash-safe self-improvement merely because its model/context/workspace checkpoint reloads.

## Search status

This run did **not** find one public real-LLM self-improvement system that simultaneously provides:

- real arbitrary-kill conformance across controller transaction phases;
- DART-like semantic rollback admissibility;
- durable budget/accounting and evaluation-consumption state;
- a common-budget action comparison including Continue, whole/clean restart, artifact-preserving rewind and strategy redirect;
- candidate-local repeated-selection-safe promotion plus proposal-crossing durable statistical spending;
- complete proposal/action chronology;
- an outer test never used by selection, rollback, routing or stopping.

The missing composition is now narrower, because resume mechanics, semantic rollback selection and durable budget accounting each have stronger independent evidence than at sequence 75.

## Exact next action

1. Search for a public self-improvement/controller implementation that *composes* Resume-Contract-like crash semantics, DART-like rollback admissibility and durable evaluation/query/statistical-spend consumption; prioritize explicit kill injection over ordinary exception tests.
2. Continue auditing Iterion or similarly durable runtimes specifically for process-death tests that assert budget/accounting/effect equivalence; do not promote ordinary resume unit tests into `SIGKILL` evidence.
3. Search for a same-system, common-total-budget comparison containing at least Continue, whole-task/clean restart, artifact-preserving rewind and strategy redirect, with a selection-unused outer test.
4. If no whole system appears, search for an implementation of an Evaluation Consumption Contract: durable evaluation query IDs, exact score/feedback lineage, monotone statistical spend, and restart-safe promotion decisions.
5. Retain the separate unresolved requirements for candidate-local anytime-valid promotion, proposal-crossing durable statistical spending, bounded selection-feedback bandwidth, immutable promotion identity and complete proposal/action chronology.

Frontier remains nonempty. No global completion claim.
