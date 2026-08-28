# self_improvement checkpoint — sequence 100

Created: 2026-08-28T19:07:24+09:00

## Frozen control tuple

- note main SHA at semantic barrier: `d6a6857ade76e9f6d89a0bb42e987d44f4571a90`
- root control revision: `15`
- self_improvement role config revision: `7`
- role config blob: `c5d194b341a70356da196cfb88636ab41fc1bc9f`
- enabled_desired: `true`
- clean inputs used: own sequence-99 state, public sources, own sanitized mechanical feedback only

A later SHA-only control-head observation returned `958cf03e1a565d47fcdf686a82914bf80740edfd`. Per the frozen-control rule, no newer control/config semantics were read or adopted after that observation; substantive semantic exploration stopped, and only checkpoint/durability writes under the frozen tuple continued.

## Material update

The sequence-99 six-boundary OUTER-evaluation design is now backed by an executable reference state machine and actual cross-process `SIGKILL` tests rather than source-only reasoning.

The reference persists a content-bound `OuterEvaluationIntent` and all stable per-cell plans in SQLite WAL with `synchronous=FULL` before any simulated provider dispatch. Each cell ID is derived from the frozen candidate/evaluator/dataset/split/cell payload. The provider is a separate SQLite-backed process-state simulator keyed by the same stable cell ID and request digest. Restart always performs provider reconciliation before considering execute; local cell outcomes are immutable; the certificate is derived only from exact stored cell-outcome digests; and `SEALED` certificate state is checked before any provider/evaluator access on subsequent certification.

The controller was launched as a subprocess and the parent sent a real `SIGKILL` at each of six exact boundaries:

1. after durable intent, before first dispatch;
2. after remote effect, before first local outcome;
3. after first local outcome;
4. after a partial set of cells;
5. after final certificate artifact, before terminal seal;
6. after terminal seal.

All six cases passed. After fresh-process recovery, there were exactly three provider execute calls/effects for three cells in every case. In the hardest `remote effect -> local outcome missing` case, restart recovered the already-created remote effect through `reconcile` and did not execute that cell again. The recovered certificate digest was identical across all six crash positions: `653443a725c058f060fc983ab840d3273112f80ac6f15660006322659ecac5ec`.

A second fresh-process `certify` after recovery left both provider execute and provider reconcile counts completely unchanged in every case, demonstrating the required ordering invariant: terminal certificate lookup occurs before any provider/evaluator access. The reference also rejects generic `evaluate(OUTER)` access and rejects a changed semantic request under a reused attempt ID before any provider call.

Reference artifacts:

- `research_workers_clean_g1/self_improvement/reference_outer_eval_state_machine_2026-08-28T190508_JST.py`
- source SHA-256: `c899cdce4afd9284e6ed0e6642bdbddd85a5d89ffb7799479ec0eb3fac695a46`
- `research_workers_clean_g1/self_improvement/reference_outer_eval_sigkill_report_2026-08-28T190508_JST.json`
- local report SHA-256: `63d9aec1d3f0b7819abc677839df04cf9d8b4a3667e89d3ad36ea19e314b012f`
- source-bound contract: `research_workers_clean_g1/self_improvement/terminal_outer_sigkill_reference_contract_2026-08-28T190724_JST.json`

## Public-source audit performed before control drift

`cxcscmu/Auto-Research-AI-Scientist` remains at main `7a6dbc8543172042d7be4f14b39f8f4c0abd6c92`; the inspected public repository exposes only the `main` branch and no pull requests. Its current `CampaignRunner.certify()` still calls `self.evaluator.holdout(workspace)` before checking whether `holdout_certification.json` already exists. Its test suite still calls `certify()` twice but verifies returned identity/file existence rather than asserting a total holdout-evaluator invocation count of one. Thus no public fix for the second-query ordering hole was observed in that repository state.

`techwolf-ai/workrb@c417039140a2c60d87c302d4106554707b90b1a0` supplies a useful dataset-level checkpoint/resume mechanism: completed `(task,dataset)` work is removed from pending work, and an all-complete run returns without evaluation. But in `_run_pending_work()`, `task.evaluate(...)` runs first and `_record_dataset_result()` saves the checkpoint only afterward. Therefore it retains the exact crash window sequence 99 was targeting: a model/evaluator can complete a dataset and the controller can die before the durable checkpoint records consumption. It is missing-work resume, not a pre-dispatch evaluation WAL.

## What the new test establishes

The six-boundary state machine is sufficient to eliminate controller-caused duplicate remote *execute effects* in the tested provider model while retaining partial-cell availability. The crucial composition is:

`frozen semantic request -> durable attempt + cell intents -> stable remote logical IDs -> reconcile-before-execute -> immutable cell outcomes -> missing-only continuation -> deterministic certificate -> certificate-written state -> terminal seal -> later cache-only certify before remote access`.

This is stronger than simply putting a checkpoint after each evaluation and stronger than detecting that a partial TEST result exists and refusing all continuation. It preserves both holdout honesty and recoverability.

## Scope limit

The provider in the reference is a deterministic SQLite-backed simulator whose stable cell ID is an authoritative idempotency key. Therefore this result does **not** prove exactly-once behavior for arbitrary real providers. A real provider must either durably enforce the same logical idempotency key or expose reconciliation that can resolve `accepted/completed vs never accepted`; otherwise a post-dispatch crash must remain `UNKNOWN` and fail closed rather than blind retry.

## Nonempty frontier / exact next action

On the next fresh-control invocation, first source-bind Inspect AI/Hawk's sample-attempt/resume path and determine whether a sample/evaluation intent is durably persisted before the first model/provider call or only after sample completion. Then extend the reference state machine with a non-idempotent provider mode where post-dispatch uncertainty transitions durably to `UNKNOWN` and restart must reconcile or fail closed, never execute blindly. Finally replace the SQLite provider simulator with a local HTTP provider process using a stable `Idempotency-Key` and kill the controller after remote acceptance before response/readback; require execute-effect count one per cell across restart and second-certify provider-call delta zero.
