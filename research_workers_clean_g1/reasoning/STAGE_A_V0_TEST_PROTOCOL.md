# Stage-A v0 causal instrumentation test protocol

Status: pre-implementation / pre-provider-collection.

Pinned public substrate: `anetigone/cssc@f40a3d3aa3054f4b07bb17e3fe5aa6d55e3d28f8`.

Parent feature manifest: `STAGE_A_V0_FEATURE_MANIFEST.json`, semantic SHA-256 `c1f8cacb3b8eedc8ed665869a378e9e71a7a36653fd3efa717c36cc940a81838`.

Parent randomized protocol: `STAGE_A_V0_RANDOMIZED_PROTOCOL.json`, semantic SHA-256 `858af2e3f138655855dca8204cbdbab74da374f15a4fe1e4ea1badad153f455b`.

This protocol is designed to prove that causal logging/randomization does not silently change CSSC semantics and that failures cannot create unverifiable action histories.

## Global invariants

For every run with instrumentation enabled:

- `run_id` is the existing CSSC sample UUID; decision indexes start at 0 and increase monotonically.
- One `execution_decision` exists per decision index, at most one `execution_outcome`, and zero or more `proposal_batch_consumption` joins.
- No outcome or batch-consumption join exists without a matching decision.
- The decision is durably committed before `frontier.consume` or executor side effects.
- If a selected generated proposal references a shared provider batch, its consumption join is durably committed before action execution.
- The outcome is committed before another randomized decision.
- Exact duplicate event replay is idempotent; conflicting duplicate payload for the same `event_id` fails closed.
- Provider/cost-ledger events are immutable; causal batch-consumption joins never add monetary/resource cost.
- An unmatched committed decision is `censored_no_outcome`, never an inferred proof failure.
- With epsilon=0, semantic/controller behavior and non-journal resource accounting match the uninstrumented baseline exactly; wall-clock/trace I/O are measured rather than required equal.

## T01 — budget enforced

Anchor: existing `test_constrained_selection_skips_rejected_higher_ranked_action`.

Setup: top-ranked candidate rejected by raw API-cost admission; lower-ranked candidate admitted; remaining-budget enforcement on.

Assertions:

1. selected node/action matches existing test;
2. top row retains `raw_budget_admission.allowed=false`;
3. top row `effective_selection_allowed=false`;
4. selected row effective admission true;
5. decision baseline node equals selected lower-ranked node;
6. event persisted before frontier consume;
7. epsilon=0 instrumentation does not change choice or budget counters.

## T02 — budget enforcement disabled

Same fixture, remaining-budget enforcement off.

Assertions:

1. top-ranked raw-rejected candidate remains production-selected exactly as current CSSC semantics require;
2. raw admission remains false in the event;
3. `effective_selection_allowed=true`;
4. selected effective admission contains `remaining_budget_policy_disabled`;
5. instrumentation must not re-impose the raw budget gate.

## T03 — structural zero-check action

Anchor: existing structural/decompose end-to-end tests.

Assertions:

- same workspace transition and selected action sequence with/without journal;
- no checker/model event is introduced by logging;
- outcome records proof outcome `not_checked` unless a verifier check actually occurs;
- no positive pseudo-reward is emitted merely because workspace shape changed;
- any later accepted-fact delta is recorded as verifier-grounded progress only when actually validated.

## T04 — checked implementation path

Anchor: `test_action_frontier_runs_real_controller_and_writes_ledger`.

Assertions with epsilon=0:

- final `accepted` identical;
- selected node/action identical;
- checker event sequence identical (`candidate`, `assembly` in the pinned fixture);
- checker count/model calls/token/API cost/reconciled ledger identical;
- one decision and one outcome appear in causal journal;
- only journal bytes/fsync/wall overhead differ.

## T05 — cached candidate competition

Anchor: `test_cached_actions_compete_before_execution`.

Assertions:

- winner identical to pinned baseline;
- unselected candidate is not executed;
- lossless candidate rows include both candidates;
- `candidate_set_sha256` stable under source list reorder;
- `ranked_choice_sha256` binds exact production ordering.

## T06 — failed provider before any decision

Anchor: `test_action_runtime_records_failed_provider_with_na_usage_and_charge`.

Assertions:

- provider failure events/cost reconciliation unchanged;
- no `execution_decision` is journaled because no candidate action was selected;
- no fabricated propensity/action row is produced to make the trace look complete.

## T07 — shared proposal batch consumed twice

New controlled fixture: one provider request returns two valid cached structured proposals sharing one `proposal_batch_id`; both are consumed in separate later decisions.

Assertions:

1. capture canonical provider ledger events immediately after generation;
2. after first and second consumption, those provider ledger events are byte-identical to the captured snapshot;
3. two distinct `proposal_batch_consumption` joins exist, each bound to its own decision/node;
4. provider token/API totals and run reconciliation are identical before/after adding joins;
5. no latest-consumer overwrite of provider `action_id` occurs.

## T08 — decision commit failure before action

Inject SQLite error/transaction failure on `execution_decision` commit.

Assertions:

- `frontier.consume` is not called;
- executor/checker/provider side effects for the selected action do not occur;
- run exits/stops experimental decision loop with explicit instrumentation failure;
- no outcome exists for an uncommitted decision.

## T09 — batch-consumption commit failure before action

Decision is committed; selected action references a shared batch; inject failure committing the consumption join.

Assertions:

- action is not executed;
- committed decision remains unmatched and reader classifies it censored;
- provider ledger is unchanged;
- no subsequent randomized decision occurs in the same run.

## T10 — outcome commit failure after action

Commit decision (and batch join if applicable), execute action successfully, then inject failure committing outcome.

Assertions:

- do not attempt to roll back the already executed action;
- stop further randomized decisions;
- decision remains unmatched/censored;
- later recovery does not label it proof failure or re-execute automatically without a separate recovery protocol.

## T11 — abrupt process recovery

Use SQLite WAL + `synchronous=FULL`.

Subcases:

- child commits event then exits via immediate process termination: committed row must be present after reopen;
- child inserts inside uncommitted transaction then exits: row must be absent after reopen;
- `PRAGMA integrity_check` must return `ok` in the test environment.

The current local smoke test already observed these outcomes; production CI should repeat them on the target runtime/filesystem.

## T12 — idempotent replay

- append new event -> `appended`;
- append same `event_id` and identical canonical payload -> `identical`, row count unchanged;
- append same id with different payload/hash -> `duplicate_conflict`, no mutation.

Do not use `INSERT OR IGNORE` as the semantic implementation.

## T13 — canonical hashes

- candidate-source reorder -> set hash unchanged;
- scheduler rank swap -> set hash unchanged, ranked hash changes;
- mutate obligation version, proposal batch provenance, cost estimator source/version or budget admission -> relevant hash changes;
- same canonical state serialized in separate process -> same hash.

## T14 — HMAC randomized sampler replay

Pinned randomized protocol only.

- construct pool in frozen rule/order;
- reproduce `u64` and `uniform` from HMAC-SHA256 fixed key and exact message;
- recompute chosen action from logged probability vector;
- chosen node and propensity must match event;
- empirical synthetic frequencies for large independent run ids must fall inside a prespecified statistical tolerance around exact probabilities.

## T15 — fallback/support semantics

Subcases:

- baseline action outside safe action kinds -> propensity 1 baseline, explicit skip reason;
- only one safe eligible candidate -> propensity 1 baseline;
- more than five safe candidates -> baseline + top four safe alternatives only; all outside-pool propensities exactly zero;
- learned v0 target policy queried outside supported pool -> deterministic baseline fallback is part of target policy itself.

## T16 — journal overhead

Run identical deterministic controlled workloads with instrumentation off and on. Report:

- action/check/model/token/API/result equality;
- journal decision/outcome count;
- per-event median/p95 append latency;
- journal bytes, WAL/checkpoint bytes, fsync/commit count where observable;
- wall-clock delta and journal fraction of total/action wall time.

Do not claim cost-efficiency improvements if logger overhead is large and unmatched between comparison arms.

## Dataset-reader invariants

On exported/raw journal:

- every outcome/batch join resolves to exactly one decision;
- every decision resolves to its exact lossless candidate set and behavior probability vector;
- censored decisions remain present;
- theorem/task split is assigned before candidate-row expansion and all runs from one theorem remain in one split;
- terminal verified success is defined only for runs with observed terminal result;
- local verified progress and multidimensional cost remain separate labels;
- behavior support diagnostics are computed before OPE/model selection.

## Gate to provider collection

Provider-enabled deterministic pilot may begin only after T01–T16 required local/CI tests pass or each unsupported test is explicitly marked with its unresolved risk. Randomized provider collection additionally requires the pinned randomized protocol, complete propensity replay, and no unresolved fail-open persistence path.
