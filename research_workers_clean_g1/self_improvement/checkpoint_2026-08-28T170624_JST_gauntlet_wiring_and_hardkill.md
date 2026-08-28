# Self-improvement checkpoint — sequence 97

Created: 2026-08-28T17:06:24.855585+09:00

## Correction to sequence 96

The previous checkpoint described `Tyler-R-Kendrick/epoch` `gauntlet-loop` too strongly as a public executable improvement control plane. At the exact audited revision `f03a7b6fecc23e2478df23b8438113a904ec757b`, it is better classified as a substantial typed/tested **control-plane library and workflow substrate** whose most important service families are not wired end-to-end through the declared CLI.

The package entrypoint is `gauntlet.cli:main`, but `cli_families.register_all()` only registers the `spec` and `profile` families. Meanwhile the README and bundled `campaign-baseline` workflow describe or invoke `campaign`, `experiment`, `evaluate`, and `promote` commands. The workflow integration test substitutes a `FakeStepExecutor`; it therefore proves MAF checkpoint/replay semantics, not that the bundled campaign can run through the real CLI. Repository searches at this revision found `ExperimentService` and `PromotionKernel` construction only in unit tests.

## Evaluation authority gap

`CommandEvaluator.run()` launches the evaluator subprocess first and only creates `EvaluationResultV1.evaluation_id` after the process returns and output is parsed. There is no durable, stable logical evaluation/query ID written before dispatch in this path. A hard controller failure after the evaluator consumed a scarce holdout or stochastic judge but before local persistence can therefore leave no durable record that the logical query was already consumed.

`ExperimentService.compare()` is append-only, but it accepts caller-provided `baseline_metrics` and `candidate_metrics` arrays and writes a `ComparisonV1` containing derived deltas. The comparison does not source-bind the exact evaluation IDs, evaluator/version digest, split/case identity, raw paired outcomes, or semantic request digest. `LedgerStore.append()` itself is genuinely immutable and refuses conflicting rewrites, but an immutable post-hoc summary is not enough to make its unbound inputs authoritative.

Therefore `ComparisonV1` chronology should **not** be used directly as the unique source of truth for candidate-local e-processes or candidate-crossing online error control. The stronger authority chain is:

`LogicalEvaluationIntentV1 (pre-dispatch) → immutable EvaluationOutcomeV1 → PairedObservationV1 → replay-derived ComparisonV2 / anytime evidence / online-error state → promotion bound to evidence frontier`.

## Hard-kill boundary

The effect path is stronger than the evaluation path: `Executor` durably moves an intent to `EXECUTING` and persists its effect plan before invoking the adapter. The published adversarial external-success test, however, uses an adapter that writes a fake external result and then raises a **RuntimeError**. `Executor` catches that exception, persists `OUTCOME_UNKNOWN`, and reconciliation works after restart.

That is exception safety, not true process-hard-kill safety. If the provider succeeds and the controller is SIGKILLed before the adapter returns, the catch block never executes. The durable intent can remain `EXECUTING`; `Executor.execute()` only accepts `COMMITTED`, while `Executor.reconcile()` only accepts `OUTCOME_UNKNOWN`. The audited code therefore has a likely **fail-stuck stale-EXECUTING state**, not a demonstrated duplicate-effect bug. `Saga.recover()` already contains the safer semantic rule—started non-idempotent work with no terminal record becomes unknown/needs-reconciliation and is never rerun—so the missing seam is concrete.

## Outer-test comparison

Gauntlet currently defines only `SEARCH`, `CALIBRATION`, and `PROMOTION`; the sealed promotion split is already consumed for promotion and is not a fourth terminal lockbox. As a useful contrast, the July 15, 2026 GSME paper reports a train-selected harness scored once on a sealed test after evolution, with no test signal used during evolution, but explicitly states that mechanically enforcing the withholding is future work. That is strong protocol separation, not a structurally inaccessible/cache-only OUTER service.

## Minimal extension

The source-bound extension contract for this checkpoint requires:

1. Stable `logical_evaluation_id` + canonical semantic request digest persisted before evaluator/provider dispatch.
2. Permanent reservation of query/statistical budget before the first attempt; retries stay under the same logical ID.
3. Immutable outcomes bound to candidate commit/artifact, evaluator identity/version/digest, split, case/trial, and scoring protocol.
4. `PairedObservationV1` referencing exact baseline/candidate outcomes; no free metric arrays.
5. Anytime-valid candidate evidence and candidate-crossing online error control replayed from the ordered immutable observation log.
6. Promotion binding artifact identity + evidence-log frontier/hash + statistical-policy digest + verdict.
7. Stale `EXECUTING` recovery to `outcome_unknown/needs-reconciliation`, never blind replay.
8. A real CLI/coordinator integration test for the bundled campaign workflow.
9. A fourth mechanically terminal OUTER namespace/service with zero permitted pre-final queries and once/cache-only final evaluation.

## Nonempty frontier / exact next action

Search public Gauntlet branches/PRs/releases and other self-improers for implemented real CLI/service wiring, pre-dispatch logical evaluation intents, stale-EXECUTING reconciliation, replay-derived anytime/online-error state, and a mechanically terminal fourth OUTER. If absent, keep the extension as a source-bound contract and construct a kill-point equivalence matrix over the audited Gauntlet seams without inventing performance results.

Contract: `research_workers_clean_g1/self_improvement/gauntlet_evaluation_authority_contract_2026-08-28T170624_JST.json`
