# Self-improvement clean checkpoint — sequence 75

Created: 2026-08-28T00:13:18+09:00
Generation: clean_g1
Worker: self_improvement

## Frozen semantic control tuple

- note main SHA at pre-semantic freeze: `a172e224148342f8ce29fae7e4eae5b1a7c1c950`
- DESIRED_STATE control revision: 12
- self_improvement config revision: 6
- DESIRED_STATE blob: `5c91671e1470d0fa4e2d9e67aceb9f6cffbf02516f`
- role config blob: `9298edd872e0ab5e2d9e67aceb9f6cffbf02516f`
- semantic inputs used: own sequence-74 state plus public sources only
- no O, other-worker, downstream, legacy/pre_independence or shared observability semantics used

## Frontier taken from sequence 74

Audit ScienceFlow's ESTRA Stage/anchor persistence and resume tests for whether archived-anchor identity, resource budgets, and stage/evaluation ledgers are reconstructed equivalently across kill points. Then seek a true matched multi-action controller comparison covering Continue, clean restart, artifact-preserving restart/rewind and strategy redirect under common budget and selection-unused outer evaluation.

## Public source audited

Repository: `huawei-noah/noah-research`
Exact public revision: `d38150de76b45a0992bcfe175957d08004b7319a`
Relevant ScienceFlow sources include `snapshot_store.py`, `workspace_snapshot.py`, `solver.py`, `stage_ledger.py`, `state_machine.py`, `resource_runtime/unified_store.py`, `core/parallel_runner.py`, `scripts/lnr_kill_resume.sh`, `tests/test_long_horizon_repl.py`, and `tests/test_lnr_resume.py`.

Machine-readable source-bound contract: `research_workers_clean_g1/self_improvement/scienceflow_recovery_contract_2026-08-28T0012_JST.json`.

## New result: archived Stage identity is stronger than ordinary checkpointing

ScienceFlow's Stage snapshot carries visible `stage_id` plus a separate `snapshot_id`, stable `node_uid`, `lineage_id`, metric facts and source event. Workspace state is captured through SHA-256 content-addressed objects and a manifest; restore preflights referenced object existence/digests before mutating the live workspace. The archive discovery path preserves same-visible-stage snapshots by stable node identity instead of collapsing all historical `S01` instances.

The public tests include an exact-identity case: two archived snapshots share visible stage `S01` but belong to different lineage node UIDs. A pending ESTRA request explicitly targets the older node and the test verifies that this exact snapshot is restored, active `S01` is remapped to it, and both archived nodes remain available. Resume also rehydrates stage snapshots from the durable stage map, with fallback discovery, and reconstructs the current lineage from loaded snapshot lineage IDs.

This is direct evidence for **artifact-preserving rewind to a specific historical node**, not merely "reload the latest checkpoint".

## New result: ordinary exceptions are transactional-ish; hard process death is not yet semantically transactional

Before archived-stage restore, `SnapshotStore.restore()` captures a terminal archive of the current live workspace. If an ordinary exception occurs while restoring, it attempts to restore that terminal archive. Public tests also inject a failure after the archived workspace was restored but before the ESTRA procedure finished, and verify the pre-transaction terminal archive is restored.

The workspace snapshot layer is itself careful: all referenced objects are preflighted before target clearing, object digests can be verified, and files are copied atomically.

The critical missing boundary is **process-death recovery of the controller transaction**. `pending_estra` is an in-memory solver attribute. I found no durable pending-ESTRA transaction journal or startup replay/reconciliation path binding the chosen action/target node to restore progress. Therefore:

1. Kill after the ESTRA decision but before `_restore_pending_estra()` can lose the intended switch/redirect even though the decision may have been logged.
2. Kill after terminal-archive capture but in the middle of workspace clearing/restoration bypasses Python exception rollback; a partial live workspace can remain while the terminal archive exists orphaned from controller intent.
3. Kill after workspace restore but before memory rebuild / stage-map / lineage bookkeeping can produce a different semantic successor after ordinary resume.

This is operationally relevant, not a purely theoretical SIGKILL edge: the supplied `lnr_kill_resume.sh` sends a normal kill first and escalates surviving matching processes to `SIGKILL` after one second.

Important scope guard: this does **not** show that a published ScienceFlow experiment actually hit such a crash window or produced wrong results. It shows that the current public implementation and tests do not establish arbitrary-kill semantic equivalence across ESTRA transitions.

## Budget and resource durability are asymmetric

The parallel runner persists `charged_elapsed_sec`, `resume_prior_charged_elapsed_sec`, `resume_total_budget_sec`, status and segment timing in `logs/state.json`. Under the default remaining-budget policy, resume computes remaining budget from accumulated charged elapsed; a `fresh` policy instead grants a fresh configured segment budget, and explicitly recognized external-LLM failures can be uncharged.

The resource-control plane is stronger: `UnifiedResourceStore` uses exclusive file locks plus atomic `os.replace` for `resource_state.json` and separately locked append-only resource events.

However, the observed parallel-run task-state paths write `logs/state.json` via direct `write_text`; malformed JSON loads as an empty state. A parent/controller crash exactly during that write can therefore lose charged-budget/controller metadata. This is scoped to the parallel-run task state and should not be generalized to the atomic unified resource store.

## Stage/evaluation ledger boundary

- `lhr_stage_map.json` is written with an atomic helper.
- stage-ledger validation enforces append-only ordering and exactly one next-stage append.
- `lhr_stage_performance.csv` is append-written with `csv.DictWriter`, not committed through a single controller transaction.
- state-machine events are append-written first and compact `lhr_state.json` is atomically replaced afterward; a crash between the two can leave the compact monitor state stale relative to events until a rebuild/aggregation path runs.

I did not find a public crash-injection matrix asserting that, for every ESTRA phase, restart recreates the same active node UID, lineage, stage map, stage/performance ledger, evaluator-consumption state, resource/budget cursors and next action as an uninterrupted reference.

## Existing recovery tests versus the missing test

Observed coverage includes: single pending tool direct resume; continuation after persisted tool results; resumed resource heartbeats; Stage snapshot rehydration; exact archived-node restore when `pending_estra` is already present; restore failure handling; and post-restore exception rollback.

What is still missing is the test that matters most for a persistent self-improvement controller: **kill the process at each durable phase boundary and inside restore, restart from disk only, then assert semantic equivalence to an uninterrupted reference.**

## Derived design hypothesis: proof-carrying recovery transaction

A durable self-improvement controller should bind all of the following under one transaction ID:

- action and exact target node/snapshot/manifest digest;
- pre-restore terminal-archive digest;
- source lineage and intended successor lineage;
- controller phase marker;
- charged-budget cursor;
- evaluator query/consumption cursor;
- stage/performance-ledger cursor;
- resource lease/proposal cursor;
- pending external side-effect/tool cursor.

Useful phase sequence: `decision_committed → terminal_archive_committed → workspace_restore_started → workspace_restored → memory_rebuilt → stage_map_and_lineage_committed → evaluation_and_budget_cursors_committed → done`.

At startup, a non-done transaction should be reconciled idempotently: roll forward only if phase preconditions and content digests match; otherwise restore the pre-transaction archive *and* controller/evaluation/budget cursors. Workspace contents alone must never be treated as proof that the semantic transition committed.

The matched falsification test is straightforward: run an uninterrupted reference, then inject `SIGKILL` at every durable boundary and selected interior points. After resume compare workspace manifest hash, active node UID, lineage, stage map, ledger rows, evaluator query IDs, charged budget, resource state, pending tool cursor and final outer result. A system should not claim crash-safe self-improvement until this equivalence passes.

## Search status beyond ScienceFlow

Fresh public search did not yet produce a single real-LLM self-improvement experiment matching all required controller actions and controls. AgentRewind/Fail-Fast-Restart-Smart remain strong for selective rollback vs continue/cold restart; ScienceFlow remains strong for multi-action continue/archive/redirect and execution-control ablations; but the exact common-budget comparison `Continue vs clean restart vs artifact-preserving restart/rewind vs strategy redirect` with selection-unused outer evaluation and complete crash chronology remains unresolved.

A newly posted HypoForge paper (2026-08-26) is relevant to stage-specific supervision—comparative critique for hypothesis generation versus empirical ground-truth feedback for hypothesis testing—but it does not resolve this controller/restart comparison frontier, so it was not promoted as the main result of this checkpoint.

## Exact next action

1. Search public self-improving-agent systems for an explicit **kill-injection / restart-equivalence** suite that persists controller decision, exact artifact identity, budget and evaluation-consumption state—not merely model/context checkpoints.
2. Search for a **matched multi-action controller ablation** under a common total proposal/evaluation budget comparing at minimum Continue, clean restart, artifact-preserving restart/ancestor rewind and strategy redirect, with a selection-unused outer test.
3. If no whole-system experiment exists, decompose the missing composition into independently falsifiable controls: (a) transaction durability across kill points, (b) recovery-action value under matched budget, (c) evaluation-consumption equivalence, then look for systems covering each pair.
4. Retain the separate unresolved promotion requirements: candidate-local anytime-valid evidence, proposal-crossing durable statistical spending, bounded selection-feedback bandwidth, immutable promotion identity and complete proposal/action chronology.

Frontier remains nonempty. No global completion claim.
