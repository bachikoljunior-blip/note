# Open Source Systems Scan — Backlog hot-path durability and handoff schema refinement

Invocation started: 2026-08-27T10:02:23+09:00
Checkpointed: 2026-08-27T10:07:52+09:00

Frozen semantic tuple:
- note main SHA: `0690108bdb37bbcf3ca1ea9f7a032ca1706ea9b9`
- sanitized control revision: `11`
- open_source config revision: `5`
- open_source config blob: `118f440957ba4654e804af902aa09a9224acca43`

Persistence preflight later observed note main `615938fad789423ebecb60bca2e641c967044fb8`. Own `LATEST.json` still pointed to `RUN_20260827_0909_HANDOFF_FENCE_EXACT_RECOVERY.md` with blob `92692d67a37f19197c820b6dedf496aff2415e18`, so this run has a chronology-valid predecessor and did not overwrite a concurrent open_source continuation. The newer note head was used only for persistence/CAS safety; semantic control remained frozen at the tuple above.

Independence: own clean state + public sources only. No O/O-derived state, other-worker state/config, downstream comparator/integrator/index/feed/audit semantics, legacy/pre-independence research, shared aggregate ledger, or other-role receipts/configs were used. No sanitized own feedback file existed at the frozen head.

Public source head verified:
- `lbx154/Argus` public `main`: `33da786bbc6787a2eeb63a5f492498eae87c78c7`.

## 1. Global Backlog fsync would sit on a real mission hot path, not a rare control path

Current `argus_skill/life/memory.py` has one Backlog persistence primitive: `Backlog._save()` delegates to `_atomic_rewrite_jsonl()`. The latter writes a unique sibling temp file and calls `os.replace()`, but does not explicitly flush/fsync the temp file and does not fsync the parent directory. The module documents Backlog as a small whole-file-rewritten store, normally tens-to-hundreds of items.

A complete source pass over the current `Backlog` class found **19 direct `_save(...)` call sites/branches**:

1. `add`
2. `add_many`
3. `supersede_pending_for_replacement`
4. `apply_plan_revision`
5. `supersede_active_plan`
6. `update`
7. `continue_with_operator_reply`
8. `stop_for_operator_decision`
9. `claim_next` after skipping prompt-example rows
10. `claim_next` when dependency cascade changed but nothing is ready
11. `claim_next` after a successful claim
12. `reap_orphans`
13. `requeue_for_iteration`
14. `stop_iteration`
15. `resume_paused`
16. `resume_all_paused`
17. `resume_paused_statuses`
18. `remove`
19. `next_pending` when dependency reconciliation mutates rows

`mark_running`, `mark_done`, and `mark_failed` are wrappers over `update`, so they do not add separate `_save` source calls, although they do drive that same whole-file rewrite at runtime.

The mission lifecycle establishes a stronger practical bound. `_run_one()` claims an item with `backlog.claim_next()`, which performs a pending→running rewrite. Final settlement then almost always performs another Backlog mutation: success uses `mark_done`; failure uses `mark_failed`; operator parking/replan/research pause/abort use `update`; iteration uses `requeue_for_iteration`. Therefore a normal mission has a **source-derived lower bound of roughly two whole-file Backlog rewrites per mission — claim plus settlement**. Learned-vertical promotion, stage short-circuits, claim rollback, dependency cascades, replan loops, and some recovery paths can add more.

This means global file+directory fsync hardening is structurally clean but is not free background bookkeeping: it would place at least two sync barriers on the ordinary mission lifecycle while the Backlog lock is held. No Backlog/fsync benchmark is checked into the current public repository, and no performance effect is claimed here.

A minimal upstream benchmark before adoption should measure the existing writer versus `flush → file fsync → replace → directory fsync` under the actual Backlog lock for 10/100/500/1000 rows, with both no-op-sized status changes and insertions. Report p50/p95/p99 lock hold time, total rewrite bytes, file-fsync time, directory-fsync time, and end-to-end two-write mission cost. Run on at least the supported local filesystem classes rather than extrapolating one laptop result. Correctness tests remain mandatory even if a narrower durability strategy is chosen for performance.

## 2. Argus has two durability precedents, but only continuous state has the full target contract

`argus_skill/team/_store.py::atomic_write_json()` flushes and file-fsyncs the temporary file before `os.replace()`, but it does not fsync the parent directory. It is therefore a useful partial precedent but not sufficient as-is for the stronger ordering needed by the handoff transaction.

`argus_skill/daemon/state.py` already implements the full primitive needed for the continuous side:
- write bytes;
- flush + `fsync` the file;
- optional pre-replace callback;
- `os.replace`;
- parent-directory `fsync`;
- distinguish failures that happened after the target was replaced;
- exact generation-bearing CAS under a cross-process continuous lock.

So the candidate should copy this durability *contract*, not create a new database layer. The Backlog can keep JSONL and its current `portalocker` serialization.

## 3. `creation_stamp` schema can now be made versioned and migration-safe

Current `BacklogItem.to_jsonable()` serializes the dataclass with `asdict`; `from_jsonable()` reconstructs known fields explicitly and ignores unknown fields. That makes an additive versioned field backward-compatible.

Proposed field:

```json
"creation_stamp": {
  "version": 1,
  "item_id": "<pre-reserved backlog id>",
  "manager_intent_id": "intent-...",
  "execution_task_sha256": "<64 hex>",
  "context_refs_sha256": "<64 hex>",
  "protected_route_fingerprint_v4_sha256": "<64 hex>",
  "dispatch_contract_id": "manager_operator_scope_v1"
}
```

Rules:
- Legacy rows deserialize with an empty stamp.
- Only the exact first-insert primitive may create a non-empty stamp.
- Generic `Backlog.update()` must reject changes to at least `id`, `ts`, and `creation_stamp` before mutating anything.
- Ordinary `Backlog.add()` must reject an existing ID, matching `add_many()` / plan-revision uniqueness behavior.
- Recovery sees same ID + exact stamp => return the current stored row unchanged.
- Same ID + missing stamp, different stamp, or more than one matching ID => fail closed. Do not infer a stamp retroactively from mutable row fields.

This guard is not cosmetic: current `Backlog.update()` performs generic `setattr` for any existing dataclass attribute and stops at the first matching ID. A duplicate ID or mutable stamp would make later settlement/recovery ambiguous.

`dispatch_contract_id` is intentionally a small explicit constant describing the immutable Manager→operator-mission creation contract; it does not exist in upstream today. It should not be derived from mutable tags or the entire Backlog row.

## 4. Exact operator-priority insertion should own the full first-write transaction

Current continuous Manager persistence in `manager/dispatch.py` does this in separate steps:
1. `pending = mem.backlog.pending()` outside the write lock;
2. compute `head_priority`;
3. construct `BacklogItem.new(...)` outside the lock, fixing its timestamp there;
4. call `mem.backlog.add(item)` under the lock;
5. emit `life.planner.task_added` afterward.

The fallback after `manager_continuous_handoff()` may call the same persistence function again if the local `persisted` dictionary is empty. This is exactly the crash/retry shape where duplicate rows/events are possible.

A narrow API such as `Backlog.ensure_operator_priority_item_exact(...) -> (stored_item, created)` should, under one Backlog lock:
- find all rows with the pre-reserved target ID;
- fail on multiple matches;
- return the existing row only when its immutable stamp matches exactly;
- otherwise compute `priority=min(current_pending_priority - 1, -1)` from that locked snapshot;
- create the first timestamp exactly once inside the lock;
- construct the row with the creation stamp;
- validate dependencies;
- durably rewrite the backlog;
- return `(row, True)`.

The caller emits `life.planner.task_added` only for `created=True`. A retry that finds the exact row must not manufacture a second task-added observation.

## 5. `handoff_fence_v1` can stay minimal; recovery state should be derived rather than mutable

Current `ContinuousConfigState` contains `enabled`, `objective`, `open_ended`, done metadata, and `generation`. Its exact comparator includes those fields and generation; reserve sizing serializes the same state. A structured fence should be another field inside this same CAS object.

Proposed minimal JSON shape:

```json
"handoff_fence": {
  "version": 1,
  "intent_id": "intent-...",
  "source_objective_sha256": "<64 hex>",
  "target_objective": "<Manager-clean execution task>",
  "target_objective_sha256": "<64 hex>",
  "target_item_id": "<pre-reserved id>",
  "creation_stamp": {"version": 1, "...": "..."},
  "source_route_fingerprint_v4": {"...": "..."},
  "target_route_fingerprint_v4": {"...": "..."},
  "target_open_ended": true
}
```

Do **not** add a mutable `phase` field unless implementation evidence later requires it. The durable world already reveals the phase:
- fence present + current route == source + target item absent => route/insert not committed;
- fence present + current route == target + target item absent => route committed, mission insert pending;
- fence present + current route == target + exact target item present => ready for final enable CAS;
- fence present + current route == source + target item already present => violates the chosen route-before-insert ordering; fail closed instead of guessing;
- fence present + route matches neither source nor target => a newer/third route intervened; Manager reconciliation required;
- target item exists but stamp conflicts/duplicates => fail closed;
- fence absent + target objective enabled + target route + exact item => committed state; recovery no-ops.

The first CAS must change A from enabled to **disabled + fence before every route/backlog/session/persist side effect**. Recovery never treats a fence as a process-resumable stop. The fence must participate in parse/serialization, `_same_continuous_state`, and reserve sizing so ENOSPC recovery also reserves enough space for the target objective/stamp payload.

## 6. Route fingerprint v4 can use exact upstream normalizers

A canonical v4 route identity can reuse the semantics already encoded in Argus rather than inventing string rules:
- `vertical`: Manager/vertical selector canonical value (`_strip_needed`/known vertical semantics; legacy `direct` means `software` only in the migration adapter);
- `domain`: strip/lower and `-`→`_` as `_normalize_domain`;
- `workflow_mode`: only normalized `direct|staged`, otherwise empty;
- `research_target_level`: `exploratory|publishable|doctoral`, otherwise empty;
- `research_direction_mode`: `broad|locked`, otherwise empty;
- `target_venue`: `_normalize_venue_key` — uppercase, remove separators, strip trailing 2/4-digit year, so `AAAI-26`, `aaai2026`, and `AAAI 2026` are the same route identity.

Canonical object:

```json
{
  "version": 4,
  "vertical": "research",
  "domain": "",
  "workflow_mode": "staged",
  "research_target_level": "publishable",
  "research_direction_mode": "broad",
  "target_venue": "AAAI"
}
```

Hash sorted-key compact UTF-8 JSON when a digest is needed. Keep the canonical object as audit data. `current_stage` stays excluded because legitimate execution progress changes it without changing the route contract.

## 7. Manager handoff v4 migration should add route identity without making process rearm impossible

Current `manager-handoff.json` is version 3 and stores only objective hash, vertical, domain, continuous generation, intent ID, and optional source-objective metadata. Matching accepts identity generation `<=` current generation. That permissiveness lets ordinary process-only generation increments resume, but the identity cannot detect same-vertical workflow/research/venue drift.

A v4 identity should add the canonical route object/digest. Versions 1–3 should **not** be synthetically upgraded from their old fields; one real Manager reconcile should emit v4.

Generation matching needs one caution: strict equality would reject a legitimate process-only CAS rearm that increments continuous generation without changing semantic route/objective. Therefore the safe fast-path condition is not simply `handoff_generation == current_generation`. It should require:
- exact objective hash;
- exact v4 route fingerprint;
- no unresolved handoff fence;
- current continuous state is enabled;
- identity generation is not from the future;
- every intervening generation class permitted by the implementation is process-only, or else reconciliation occurs.

The last bullet is not represented in current schema, so either process-only rearm needs an explicit lineage marker or the first implementation can conservatively reconcile whenever generation advanced for a reason it cannot prove process-only. Do not retain v3's bare `<=` rule with only the new fingerprint and call it complete.

## 8. Real regression target and remaining uncertainty

The highest-value integration regression remains:
1. seed continuous A enabled and source route A;
2. prepare B, intent, pre-reserved item ID, creation stamp, source+target route v4;
3. exact-CAS A → disabled structured fence;
4. reconcile/commit route B;
5. exact-insert B mission into the real Backlog and emit task-added once;
6. inject final fence→B-enabled failure before continuous replace;
7. verify fence remains, exactly one row exists with original timestamp/priority/stamp, and only one task-added event exists;
8. recover once to B-enabled, then recover again and no-op;
9. separately inject post-replace directory-fsync failure and verify committed-state detection prevents duplicate side effects.

Durability regression for Backlog itself should assert temp-file flush/fsync occurs before replace and parent-directory fsync after replace. A measured latency benchmark is still required before recommending global fsync as an upstream default rather than a correctness experiment.

## Candidate refinement

`clean-os-g1-005` is now:

> Keep existing Manager pipeline locking and deterministic evidence gates. Before any continuous replacement side effect, exact-CAS the enabled campaign into a structured disabled handoff fence containing a pre-reserved mission ID, Manager intent, immutable versioned creation stamp, Manager-clean target objective, and canonical source/target route-v4 identities. Reconcile route by source/target fingerprint; insert the operator mission exactly once in a single Backlog transaction with global ID uniqueness, immutable creation identity, locked priority/timestamp allocation, durable rewrite, and created-event suppression. Only after the exact mission is durably present may a final exact CAS clear the fence and enable the target. Process start/restart/upgrade paths consume current state rather than copied objectives. Manager handoff v4 binds the full normalized route contract and migrates v1–v3 through one real Manager reconciliation.

This remains a source-derived, unimplemented adaptation proposal. No live Argus mutation, daemon fault injection, fsync benchmark, or power-loss test was performed.

## Exact continuation

1. Inspect all current process rearm call sites and define the smallest explicit generation-lineage marker (or conservative reconcile rule) that lets manager-handoff v4 distinguish process-only generation increments from semantic commands without reviving v3's broad `<=` ambiguity.
2. Specify a concrete Python `CreationStampV1` / `HandoffFenceV1` typed representation and exact serializer/parser validation, including length/type limits for recovery-facing fields.
3. Confirm whether any legitimate production caller deliberately mutates `BacklogItem.id` or `ts`; if none, make the immutable-field guard unconditional and add compatibility tests.
4. Design a benchmark matrix for global Backlog file+directory fsync with the observed ~2-rewrite normal-mission lower bound, then compare a narrow durability barrier alternative only if measured sync cost is material.
5. Write the real-Backlog fault-injection regression around final continuous pre-replace and post-replace failures, including task-added suppression and exact stamp conflict behavior.
6. Keep external/admin `PIPELINE_STATE` writer fencing as a separate candidate branch; do not mix it into this handoff experiment.
