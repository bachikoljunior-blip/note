# Open Source Systems Scan — backlog mutability audit + operator-priority atomicity

Invocation started: 2026-08-27T06:59:30+09:00
Checkpointed: 2026-08-27T07:05:28+09:00

Frozen semantic tuple:
- note main SHA: `0dc9c94734e9f30fbb117bb3998dac74df11a121`
- sanitized control revision: `11`
- open_source config revision: `5`
- open_source config blob: `118f440957ba4654e804af902aa09a9224acca43`

Persistence preflight observed note main `ba6335c6147d6f487c483718d9fc9741e228d035`; own `LATEST.json` was unchanged from the frozen predecessor, so this checkpoint does not overwrite a concurrent open_source continuation. The newer repository head was used only for CAS/persistence safety; no newer control semantics were adopted after the semantic-freeze barrier.

Independence: own clean state + public sources only. No O/O-derived state, other-worker state/config, downstream semantics, legacy/pre-independence research, shared aggregate ledger, or other-role receipts/configs were used.

Public source head verified:
- `lbx154/Argus` public `main`: `33da786bbc6787a2eeb63a5f492498eae87c78c7`.

## 1. Field-by-field audit: a recovery stamp cannot be reconstructed from the live backlog row

Current `Backlog.update(item_id, **fields)` validates status transitions but otherwise applies `setattr` to any dataclass attribute present on the row. Therefore adding `creation_stamp` as an ordinary dataclass field without a special guard would make the stamp itself mutable.

The production callers and specialized backlog methods also show that many fields legitimately change after insertion. For a continuous Manager-created row, the following are runtime-mutable in current source or through a first-class helper:

- scheduling/lifecycle: `status`, `started_ts`, `running_owner`, `finished_ts`, `last_error`, `attempt`, `orphan_retries`;
- operator/review state: `pending_question`, `operator_decision`, `outcome`;
- routing/execution text: `objective` and `manager_decision` can change after creation when an un-routed row is sent back through the Manager; `manager_decision.learned_vertical_status` can also be promoted later;
- presentation: `title` is rewritten after bounded dispatch when the Manager-clean execution title differs;
- convergence/iteration: `iterate`, `iteration_cycles_done`, `iteration_cost_usd`, `consecutive_replans`, `replan_streak_tracked`, `replan_rejections`;
- dependency topology: `deps` is rewritten atomically when an operator answer replaces a blocked node with a continuation;
- supersession metadata: `superseded_by_plan_id` and `superseded_reason` are written by replacement/revision flows;
- `notes` can be populated by operator stop/iteration handling.

A particularly important case is `requeue_for_iteration`: the same stable backlog id is intentionally retained while `objective`, iteration counters, timestamps, and error state change. Recovery equality that hashes the current row would reject a legitimate retry after one such mutation.

Conversely, the audit found no legitimate production `backlog.update(...)` mutation for the core creation contract fields `id`, `ts`, `priority`, `tags`, `original_objective`, `iteration_max_cycles`, `plan_id`, `plan_version`, `node_key`, `context_refs`, `blocker_fingerprint`, `work_kind`, `acceptance_check`, `plan_hypothesis`, `goal_contribution`, `expected_regressions`, `decision_rule`, `non_goals`, `authorization_id`, `authorization_action`, `execution_workdir`, `parallel_safe`, or `owns_paths`. This is an observed-call-site classification, not an API guarantee: current generic `update()` can still mutate any of them if a new caller passes the field.

### Consequence

`creation_stamp` should be an explicitly immutable field (or sidecar identity) written once at insertion. Generic `Backlog.update` should reject any attempt to alter a nonempty stamp. `ensure_item_exact` should compare only that stored immutable stamp, not recompute identity from the current mutable row.

Legacy or ordinary rows without a stamp remain valid backlog rows, but they cannot be treated as an exact recovery match for a stamped handoff. If the same id already exists without the expected stamp, recovery should fail closed rather than guess provenance.

## 2. New TOCTOU: operator-priority allocation is not atomic with insertion

The continuous Manager persistence callback currently does this in two separate operations:

1. `pending = mem.backlog.pending()` and `head_priority = min(...)`;
2. construct the operator row with `priority=min(head_priority - 1, -1)`;
3. call `mem.backlog.add(item)`.

`Backlog.pending()` is a plain load without the backlog lock. `Backlog.add()` acquires the lock only later. A concurrent backlog writer can therefore insert or reprioritize queue state between the priority read and the append. This is a small but real source-level TOCTOU in the exact path whose crash recovery is being hardened.

It also complicates the proposed handoff fence: the target id and semantic task contract are known before side effects, but the exact priority currently depends on live queue state at persist time. Freezing a priority before the fence would either preserve today's race or require another lock dance.

### Narrower design

Move operator-priority derivation into the same backlog-lock transaction as exact insertion:

`ensure_operator_priority_item_exact(item_without_priority, creation_stamp)`

under one `Backlog._locked()` section:

- load current rows once;
- if id exists: require a nonempty equal immutable creation stamp and return that row unchanged, regardless of legitimate later runtime-field mutations;
- if id is absent: derive `priority=min(current_pending_priority - 1, -1)` from the locked rows, persist that chosen value and the immutable creation stamp exactly once, validate the DAG, and save;
- if same id has missing/different stamp: fail closed;
- ordinary `Backlog.add()` independently rejects all duplicate ids.

This makes the priority an insertion-time fact without requiring it to be precomputed before the continuous handoff fence. On recovery, the stored row wins; the current queue is not used to recompute a different priority.

This is preferable to excluding priority from identity and then silently accepting a newly recomputed priority, because priority affects execution order even though it is not semantic task content.

## 3. Regression matrix refined around legitimate post-create mutation

Use the real `Backlog`, not a mock.

1. `add(id=X)` then ordinary `add(id=X)` -> reject; file still has exactly one `X`.
2. exact insert `X/stamp=A` twice -> second call returns the existing row; exactly one `X`.
3. insert `X/stamp=A`, then legitimately mutate lifecycle fields (`running -> paused/resumed`, attempts/timestamps/outcome), exact retry with `A` -> idempotent success and no field rollback.
4. insert `X/stamp=A`, then `requeue_for_iteration` changes objective/counters, exact retry with `A` -> idempotent success and preserves the newer objective/counters.
5. insert `X/stamp=A`, then Manager reroute legitimately changes `objective` / `manager_decision`, exact retry with `A` -> idempotent success and preserves rerouted values.
6. insert `X/stamp=A`, then operator-decision fields mutate, exact retry with `A` -> idempotent success.
7. existing `X` without a stamp + retry `stamp=A` -> fail closed.
8. existing `X/stamp=A` + retry `stamp=B` -> fail closed.
9. generic `Backlog.update(X, creation_stamp=B)` after nonempty `A` -> reject and preserve `A`.
10. two concurrent operator-priority exact inserts with distinct ids -> each priority is allocated under the same lock from the state actually committed before it; no read-before-lock TOCTOU and both IDs remain unique.
11. final continuous-state replace fails after the exact insert; recovery repeats the same target id/stamp twice -> one mission row only, stored priority unchanged, no duplicate event-authority row.

The event emission for `life.planner.task_added` remains downstream observability; exactly-once backlog authority should not depend on whether that fail-soft event was emitted once or more than once.

## 4. Candidate refinement

`clean-os-g1-005` is now:

> Keep existing Manager pipeline locking and deterministic evidence gates. Before continuous replacement side effects, exact-CAS the campaign into a disabled handoff fence carrying the pre-reserved target mission id, immutable creation stamp, semantic protected-route fingerprint, and enough target identity to resume deterministically. Enforce global backlog-id uniqueness. Insert the operator-priority mission with one backlog-lock transaction that both derives priority and performs exact-idempotent insertion; recovery compares only the immutable creation stamp and never rolls back legitimate later row mutations. Then exact-CAS the target objective enabled. Process start/upgrade/replacement must consume current disabled state through the separate exact-state reconcile-or-rearm boundary rather than restore copied objectives.

This remains an unimplemented adaptation proposal, not a measured performance improvement.

## Scope / uncertainty

- No upstream repository mutation, live exploit, or crash injection was performed.
- Findings are source-level transaction/identity analysis at public Argus main `33da786bbc6787a2eeb63a5f492498eae87c78c7`.
- The field classification is based on current production call sites and specialized Backlog methods; future callers could expand legitimate mutability.
- The creation stamp, duplicate guard, atomic operator-priority insert, handoff fence, route fingerprint v4, and unified reconcile/rearm boundary are not implemented or benchmarked.

## Exact continuation

1. Define the minimal immutable `creation_stamp` payload from pre-side-effect values, explicitly separating semantic identity from scheduler-assigned priority now that priority is allocated atomically at insert; verify whether `ts` should be excluded from the stamp and treated as first-insert receipt metadata.
2. Locate the narrowest shared home/API for `ensure_operator_priority_item_exact` without exposing it as a general duplicate-bypass primitive; specify migration for legacy unstamped rows and whether all new `Backlog.add` calls should reject duplicate ids immediately.
3. Place `protected_route_fingerprint_v4` using current vertical/domain/workflow/research/venue semantic normalizers and define v1-v3 restart-identity migration.
4. Finish start/boot/immediate-upgrade/scheduled-upgrade/replacement into one exact-state `reconcile_or_rearm` contract; keep external/admin `PIPELINE_STATE` writer fencing separate.
5. If source remains unchanged, design a minimal upstream regression that injects failure after the operator row is persisted but before final continuous replace, then repeats recovery twice and asserts one row, one immutable stamp, unchanged insertion priority, and no enabled-objective/route split-brain.
