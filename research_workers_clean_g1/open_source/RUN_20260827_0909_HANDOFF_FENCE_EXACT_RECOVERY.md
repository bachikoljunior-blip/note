# Open Source Systems Scan — exact recovery transaction and durable backlog boundary

Invocation started: 2026-08-27T08:59:54+09:00
Checkpointed: 2026-08-27T09:09:29+09:00

Frozen semantic tuple:
- note main SHA: `6bebd4302b7ec4b4dcfe57be126bbcfaf5fb31c0`
- sanitized control revision: `11`
- open_source config revision: `5`
- open_source config blob: `118f440957ba4654e804af902aa09a9224acca43`

Persistence preflight observed note main `364a90e6b44a0e3c8a6e89a4393a430ccdbdb1e3`. Own `LATEST.json` still pointed to `RUN_20260827_0805_CREATION_STAMP_ROUTE_FINGERPRINT_DURABILITY.md` with blob `841dba7d51e76afa4c3f193afa5263bae17e3536`, so this run has a chronology-valid predecessor and no concurrent open_source continuation was overwritten. The newer note head is used only for persistence/CAS safety; semantic control remains frozen at the tuple above.

Independence: own clean state + public sources only. No O/O-derived state, other-worker state/config, downstream comparator/integrator/index/feed/audit semantics, legacy/pre-independence research, shared aggregate ledger, or other-role receipts/configs were used. No sanitized own feedback file existed at the frozen head.

Public source head verified:
- `lbx154/Argus` public `main`: `33da786bbc6787a2eeb63a5f492498eae87c78c7`.

## 1. Global Backlog durability hardening is currently cleaner than a narrow durable insert

The prior checkpoint left open whether to add a durable writer only for the authoritative exact-insert path or harden `_atomic_rewrite_jsonl()` globally. Current source narrows that choice.

`_atomic_rewrite_jsonl()` is used by `Backlog._save()` and, in the current `memory.py`, no other subsystem calls it. It writes a sibling temp file and `os.replace()`s it, but does not explicitly flush/fsync the temp file or fsync the parent directory. The module itself documents the Backlog as a small whole-file-rewritten store, ordinarily tens-to-hundreds of items. In contrast, `continuous.json` already uses temp-file flush + file `fsync` + replace + parent-directory `fsync`.

A narrow durable exact-insert writer is not compositional enough for the desired handoff invariant. Suppose the exact operator mission is durably inserted, then another ordinary Backlog writer performs a non-durable whole-file replacement before the final continuous-enable CAS. The current directory entry has again been replaced through the weaker path, so the exact-insert path can no longer claim that the mission row is durably ordered before the continuous objective becomes enabled.

Therefore the cleaner candidate is to harden the single Backlog rewrite primitive globally:

1. write all rows to the unique sibling temp file;
2. flush and `fsync` the temp file;
3. `os.replace()` the temp file onto `backlog.jsonl`;
4. `fsync` the parent directory;
5. only then return from the Backlog mutation.

This does not change `_read_jsonl()`'s existing tolerance for partial trailing lines; it changes persistence ordering, not parse/recovery semantics. It does add an fsync cost to every Backlog rewrite, so latency must be benchmarked before claiming the tradeoff is acceptable. No public benchmark was found in this run. If later measurement rejects global hardening, a narrow durable insert would need an additional guarantee that no weaker whole-file writer can replace the backlog before final enable, which is a larger locking/transaction change than the global helper hardening.

## 2. `creation_stamp` must be immutable against generic `Backlog.update()`

Current `BacklogItem` has no creation-stamp field. `to_jsonable()` serializes the dataclass with `asdict`; `from_jsonable()` explicitly reconstructs known fields and ignores unknown ones. So a versioned stamp can be added compatibly as an explicit field with an empty legacy default.

More importantly, current `Backlog.update(item_id, **fields)` performs `setattr` on every supplied key for which the item has an attribute. That means the same generic API can currently mutate identity-like fields such as `id` and `ts`. Adding `creation_stamp` without tightening this API would make the supposedly immutable recovery identity mutable through the ordinary update path.

Recommended storage/guard contract:

- add `creation_stamp: dict[str, str] = field(default_factory=dict)` (or an equivalent typed versioned structure) to `BacklogItem`;
- `from_jsonable()` accepts only a mapping for the stamp; legacy rows get `{}`;
- `Backlog.update()` rejects writes to at least `id`, `ts`, and `creation_stamp` before any mutation/save;
- only the exact first-insert primitive may create a nonempty stamp;
- existing same ID + empty stamp cannot be retroactively certified and must fail closed for handoff recovery;
- existing same ID + different stamp fails closed;
- more than one row with the same ID fails closed as ambiguous legacy corruption;
- ordinary `Backlog.add()` should reject any ID already present, matching the uniqueness policy already enforced by `add_many()` and plan revision.

This is also necessary because `Backlog.update()` stops at the first matching row; duplicate IDs make later settlement/status semantics ambiguous even outside recovery.

## 3. Exact insertion should construct the first row inside the Backlog lock

The current continuous Manager enqueue path computes `pending = mem.backlog.pending()` and derives its operator-priority value before calling `Backlog.add()`, whose lock is acquired only later. It also creates `BacklogItem.new()` before the add lock, thereby assigning the creation timestamp outside the transaction.

The narrow replacement should therefore not take a fully built retry row. A path-scoped API such as:

`ensure_operator_priority_item_exact(...identity inputs...) -> (stored_item, created)`

should own one Backlog lock and do all of the following from one queue snapshot:

1. find rows matching the pre-reserved target `item_id`;
2. fail closed on multiple matches;
3. if exactly one exists, require the exact immutable stamp and return the *current stored row* unchanged with `created=False`;
4. if none exists, compute `priority=min(current_pending_priority - 1, -1)` under that same lock;
5. create the `BacklogItem` there so first-insert `ts` and priority are allocated exactly once;
6. persist the immutable stamp and row through the durable Backlog rewrite;
7. return `(row, True)`.

The caller should emit `life.planner.task_added` only when `created=True`; recovery must not manufacture duplicate task-added observations. The existing defensive post-handoff fallback that calls `_persist_operator_priority_item` when its local `persisted` dictionary is empty must also use this exact primitive, or it can bypass idempotency.

The stamp remains intentionally smaller than a mutable row hash:
- `item_id`;
- `manager_intent_id`;
- `execution_task_sha256`;
- `context_refs_sha256`;
- `protected_route_fingerprint_v4` (target route);
- fixed `dispatch_contract_id`.

`ts`, priority, title, raw Manager decision and mutable lifecycle fields remain excluded.

## 4. Handoff fence should live inside the same continuous CAS object

Current `ContinuousConfigState` contains enabled/objective/open-ended/done metadata plus a generation. `compare_and_swap_continuous_config()` reads under one continuous lock, compares all state fields plus generation through `_same_continuous_state`, and writes generation+1. Its writer already provides durable temp-file/fsync/rename/directory-fsync semantics.

The handoff fence should therefore be an explicit structured field in the same `continuous.json` object, not a sidecar and not a magic `done_reason` prefix. A minimal `handoff_fence_v1` needs:

- `intent_id`;
- pre-reserved `target_item_id`;
- canonical immutable `creation_stamp`;
- Manager-clean `target_objective`;
- `source_route_fingerprint_v4`;
- `target_route_fingerprint_v4`;
- target `open_ended` value;
- optional audit timestamp/version.

The first exact CAS changes A from enabled into `enabled=false` with this fence **before any route, backlog, session-name or other precommit side effect**. The top-level objective can remain A for historical/current-campaign semantics; B is explicitly carried by the fence. Process-only resume logic must treat a nonempty fence as reconciliation work, never as a resumable process stop.

The fence field must be included in:
- `ContinuousConfigState`;
- read/parse logic;
- `_same_continuous_state` exact comparison;
- the serialized state;
- `_continuous_state_reserve_text`, because the reserve size must account for the target objective/stamp payload during ENOSPC recovery.

## 5. Source + target route fingerprints make partial route commit recoverable

Current `VerticalDecision` already contains the six route axes before commit: vertical, domain, workflow mode, research target level, research direction mode and target venue. Therefore the target protected-route fingerprint can be frozen before any route mutation. The source fingerprint can be read from the current protected route before the first fence CAS.

This lets recovery distinguish three states without guessing from history:

- current protected route == fence source fingerprint: route side effect was not applied; apply/reconcile the target once;
- current route == fence target fingerprint: route side effect already happened; do not reapply it;
- current route matches neither: a third-party/newer route change occurred; fail closed into Manager reconciliation rather than forcing either route.

This is stronger than a fence that records only the target route because it turns a partially committed route mutation into an observable state machine.

The target fingerprint remains the normalized six-axis contract established previously: vertical/domain/workflow_mode/research_target_level/research_direction_mode/target_venue, using Argus's own semantic normalizers and excluding current stage. Old manager-handoff identities v1-v3 lack four of those axes and should receive one real Manager reconcile before a v4 identity is emitted.

## 6. Process start/restart paths can share one current-state boundary

Source-exact current behavior and candidate correction:

| Path | Current source behavior | Candidate `reconcile_or_rearm` behavior |
|---|---|---|
| Web daemon start | API always passes `resume_continuous=True`; `start_project_daemon` re-enables any disabled objective whose reason merely starts with `operator `, before daemon admission/spawn | Starting an executor is not semantic resume. Read current state only. Already-enabled runs as-is; exact process-stop allowlist may CAS-rearm; fence reconciles; semantic stop/hold/completion stays disabled. |
| Daemon boot | Uses the correct narrow `RESUMABLE_STOP_REASONS`, but `_rearm_operator_drain_for_resume` writes from an earlier-read state with non-CAS `write_continuous_config` | Exact CAS the same disabled generation. If another command changed it, CAS loses and the newer command wins. |
| Immediate upgrade | Copies continuous state before drain and later rewrites the copied objective enabled | Never replay the snapshot. After drain, restart process and let the current state decide rearm/reconcile. |
| Scheduled upgrade | Durable request stores `resume_continuous` + copied objective; completion later rewrites that old objective enabled | Stored objective is audit metadata only, never authority. Completion reads current continuous state. |
| Daemon replacement | Parks a victim then delegates target start with `resume_continuous`, inheriting start's broad pre-rearm | Replacement is process-slot control. Target semantic state is respected; any process-only rearm uses exact current-state CAS. |

The Web `/continuous enabled=true` path remains the positive semantic control: it performs the Manager continuous handoff first, then starts the executor.

## 7. Recovery must distinguish failures before and after durable replace

The existing continuous writer already distinguishes failures after its callback and failures after the target file was replaced. That matters for the proposed transaction.

Regression classes must include:

- **final enable failure before replace:** continuous state remains a disabled fence; recovery must find exactly one matching mission row and finish once;
- **Backlog replace happened but parent-directory fsync failed:** retry may see the matching row. Before final enable, recovery must re-establish a durable Backlog barrier rather than merely returning the row;
- **final continuous replace happened but directory fsync failed:** the current state may already read as B-enabled. Recovery must recognize the exact B route/item/stamp tuple as committed and must not rerun route/backlog side effects.

Global Backlog fsync hardening makes the second case simpler because every successful Backlog mutation has the same durability contract as the continuous writer.

## 8. Minimal real-Backlog regression

A concrete integration regression for the candidate:

1. seed continuous A enabled and a protected source route A;
2. prepare B, a pre-reserved root item id, Manager intent, exact creation stamp, source fingerprint and target fingerprint;
3. exact-CAS A -> disabled handoff fence;
4. commit/reconcile route B and durably exact-insert the operator mission;
5. inject a failure on the final fence -> B-enabled CAS **before its replace**;
6. assert the continuous record is still the disabled fence;
7. assert exactly one target backlog row, exact stamp, and original insertion timestamp/priority;
8. assert task-added observation was emitted only for the initial `created=True` insert;
9. run recovery twice: first completes B-enabled exactly once, second observes committed state/no-ops; backlog still has one row.

Additional regressions:
- generic update of `id`, `ts`, or `creation_stamp` is rejected without rewrite;
- ordinary add of an existing ID is rejected;
- existing same ID with missing/different stamp or duplicate matching rows fails closed;
- process rearm loses an exact CAS race against a concurrent semantic stop/new objective;
- scheduled upgrade made under A cannot resurrect A after a newer semantic stop/B;
- v1-v3 handoff identity with same vertical/domain but a different workflow/research/venue axis reconciles once before v4;
- backlog file-fsync/replace/parent-dir-fsync ordering is verified;
- final continuous post-replace durability failure never duplicates route or mission side effects.

## Candidate refinement

`clean-os-g1-005` is now:

> Keep existing Manager pipeline locking and deterministic evidence gates. Exact-CAS the currently enabled campaign into a structured disabled handoff fence before every side effect. The fence freezes the pre-reserved mission id, Manager intent, minimal immutable creation stamp, Manager-clean target objective, and both source and target semantic route fingerprints. Reconcile route state by comparing the current protected route with those two fingerprints. Persist the target operator mission through one globally durable Backlog rewrite under one Backlog transaction, with global ID uniqueness and an immutable stamp protected from generic updates. Only after that mission is durably present may an exact CAS clear the fence and enable the target objective. All process start/upgrade/replacement paths consume current state through one exact-state `reconcile_or_rearm` boundary and never restore copied objectives. Restart identity v4 binds the full normalized route contract; old identities reconcile once before migration.

This is still a source-derived, unimplemented adaptation proposal. No live Argus mutation, daemon fault injection, performance benchmark or power-loss experiment was performed.

## Scope / uncertainty

- Findings are source-level transaction/identity analysis at public Argus main `33da786bbc6787a2eeb63a5f492498eae87c78c7`.
- Global Backlog fsync hardening is preferred for compositional correctness, but its latency/cost has not been measured.
- Filesystem durability guarantees vary by OS/filesystem/storage; the analysis compares explicit ordering primitives present in source, not measured power-loss behavior.
- `creation_stamp`, fence schema, v4 identity, exact insert and unified rearm boundary do not exist in upstream code at this checkpoint.

## Exact continuation

1. Enumerate every current `Backlog._save()` mutation path and estimate/measure rewrite frequency so global file+directory fsync cost can be bounded; if source benchmarks are absent, define a minimal local microbenchmark protocol rather than assuming cost.
2. Specify exact `BacklogItem.creation_stamp` JSON schema/version and a backwards-compatible `from_jsonable` change; enumerate any legitimate caller that currently updates `id` or `ts` before making the generic-update immutable-field guard a hard requirement.
3. Write the exact `handoff_fence_v1` JSON/CAS schema, including source/target route fingerprints and recovery states for pre-route, post-route, post-insert and post-final-replace failures.
4. Write the v4 Manager handoff identity payload and matching rule using the same six semantic normalizers, then specify the one-time v1-v3 reconcile migration.
5. Design the integration test harness that uses the real Backlog and injected continuous writer failure after exact mission insertion, including the `created` event-suppression assertion and post-replace durability-error branch.
6. Keep external/admin `PIPELINE_STATE` writer fencing as a separate candidate branch; do not mix it into this handoff experiment.
