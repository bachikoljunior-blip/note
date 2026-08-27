# Open Source Systems Scan — real Backlog fault harness, fence recovery semantics, and durability cost

Invocation started: 2026-08-27T10:30:02+09:00
Checkpointed: 2026-08-27T10:34:46+09:00

Frozen semantic tuple: `note@0ba8457603a8c2c3c79f28f538c40cf11c778aa1 / control 11 / open_source config 5` (`DESIRED_STATE` blob `bf7b8c7f6971c0ec2f3fa7a8d53dca1f88ac50a3`, role-config blob `118f440957ba4654e804af902aa09a9224acca43`). Only own clean state and public sources were used. Public `lbx154/Argus` main was reverified at `33da786bbc6787a2eeb63a5f492498eae87c78c7`.

## 1. The missing fault test can extend an existing real-Backlog seam

Current `tests/manager/test_pipeline_yield.py::test_continuous_handoff_requests_boundary_yield` already gives the needed integration seam without a live Manager backend:
- real `Backlog(life_dir / "backlog.jsonl")`;
- a real pre-existing continuous objective A;
- a fake `Prepared` object whose `commit()` runs under the Manager pipeline lock/yield boundary;
- a `persist(execution_task, division)` callback invoked inside the continuous CAS pre-replace callback.

The current test's `persist` only appends to an in-memory Python list. It therefore does **not** test the current dangerous shape where real backlog state lands before the final continuous write.

Current storage tests already prove both lower-level fault classes independently:
1. `test_replace_failure_after_callback_surfaces_instead_of_false`: the pre-replace callback commits a durable side effect, `continuous.json` replacement fails, and the side effect remains while the old continuous state remains authoritative.
2. `test_post_replace_failure_surfaces_instead_of_false`: replacement lands, then a post-replace durability failure is surfaced; recovery must inspect actual current bytes/generation rather than assume the write did not happen.

Therefore the highest-value regression is not a new mock subsystem. Extend the existing Manager handoff test with real `Backlog` persistence plus the existing `daemon_state.os.replace` / `_fsync_directory` monkeypatch seams.

### Exact harness matrix

**Case A — callback succeeded, final continuous replace failed**
1. seed continuous A enabled at generation N and a pending A backlog row;
2. reserve stable target item ID B;
3. install fake Prepared route B and a persist callback that inserts B into the real Backlog;
4. monkeypatch only replacement of `continuous.json` to raise `EIO` *after* the callback has completed;
5. call continuous handoff;
6. assert the route/backlog side effects expected from the current implementation landed, while `continuous.json` remains the exact old A bytes/generation;
7. under the proposed fix, assert this state is impossible because the first CAS has already converted A into a disabled typed handoff fence before any semantic side effect.

**Case B — final continuous replace landed, directory fsync then failed**
1. same setup;
2. allow `os.replace` but inject error during parent-directory durability step;
3. assert the new continuous generation may already be present despite the raised exception;
4. recovery re-reads current state and branches on exact generation/fence contents; it never blindly repeats route/persist callbacks.

**Case C — recover twice**
After either failure mode, call the recovery boundary twice. Required invariants:
- exactly one target backlog ID exists;
- if the existing row carries the exact immutable creation stamp, the second recovery returns it rather than appending;
- same ID + missing/different stamp fails closed;
- any task-added/queued observable is emitted only when `inserted=True`, so exact retry does not duplicate user/runtime observability;
- final continuous enable occurs only after the target row is durably present and exact.

This suggests `Backlog.ensure_operator_priority_item_exact(...) -> (item, inserted)` rather than returning only an item.

## 2. Important refinement: the fence is a reconciliation checkpoint, not a replay log

`PreparedManagerHandoff.commit()` does more than write a six-field canonical route. It calls `Manager.commit_vertical_decision()`, which can:
- persist an existing vertical/domain contract and reset stage for a new intent;
- materialize learned/project domains;
- create a new custom candidate domain/vertical with adapted stages and supporting files;
- update the goal contract after the route commit.

For new/custom decisions, `_vertical_ops.py` uses `_restore_files_on_error(...)` around multiple affected files. That helps ordinary Python exceptions, but the full semantic mutation is not represented by only `CanonicalRouteV4`.

Therefore `HandoffFenceV1` should **not** be treated as enough information to replay `prepared.commit()` after a process crash. Recovery rules should be:
- current protected route == stored target route **and** target backlog row exact: finish/finalize the fence;
- current protected route == stored target route but row absent: perform only the exact idempotent mission insert, then finalize;
- current protected route == stored source route: re-enter Manager reconciliation on the frozen target objective; do not synthesize the old `PreparedManagerHandoff` from fence fields;
- current route is neither source nor target: fail closed into Manager reconciliation/operator repair.

This reduces fence payload and avoids turning a restart optimization into a second, incomplete route-authority implementation. `target_route_v4` is detection/fencing evidence, not replay authority.

## 3. New semantic-stop and replacement rules while a fence exists

A structured fence must have explicit precedence rules; otherwise a later process start or recovery can resurrect work the operator already changed.

### Semantic stop during fence
A new semantic stop is a monotonic safety action and should win regardless of whether the protected route currently equals fence source or target:
- exact-CAS the current fenced continuous record to `enabled=false`, clear the fence, set an intentional semantic stop reason;
- preserve the fence's target objective as the latest semantic objective for audit/future explicit resume, but do **not** process-rearm it;
- do not try to roll the route back during stop;
- any later explicit resume must pass Manager reconciliation because there is no completed v4 handoff identity for this interrupted transaction.

### Replacement objective C during fence B
Read the protected route and compare to B's two fingerprints:
- route == B.source: B never durably reached its target route; supersede/cancel B and start C from the source route;
- route == B.target: B route mutation landed. If B's exact target backlog row exists, mark it superseded; if absent, **do not create it merely to supersede it**. Then Manager reconciles C from the current B route;
- route matches neither: do not infer which semantic mutation won. Keep execution disabled and fail closed to Manager/operator reconciliation.

Process-only start/restart never clears or plain-rearms a fence.

## 4. Backlog exact-insert contract tightened

Current public source has an asymmetry:
- `Backlog.add()` appends without checking an existing ID;
- `add_many()` rejects duplicate IDs both within the batch and against the file;
- `Backlog.update(item_id, ...)` mutates the first matching row and is generic enough to alter any existing dataclass field.

For continuous recovery:
- add immutable `creation_stamp` to `BacklogItem` and reject generic updates to `id`, `ts`, and `creation_stamp`;
- `ensure_operator_priority_item_exact` holds the existing Backlog cross-process lock for ID lookup, priority calculation, first timestamp creation, stamp creation, and durable rewrite;
- absent ID => insert once and return `(row, True)`;
- one existing ID + identical creation stamp => return existing current row `(row, False)` even if mutable objective/status metadata later changed legitimately;
- existing ID without a stamp, conflicting stamp, or duplicate physical rows => fail closed;
- ordinary `add()` should also reject an already-existing ID so the file has one global identity invariant.

The stamp remains creation identity, not a hash of the mutable current row.

## 5. Local durability-cost probe

A local filesystem microbenchmark reproduced the current whole-file JSONL rewrite shape with representative ~1.29 KiB rows and 30 rewrites per point. Three variants were compared: current-style no explicit fsync, file fsync before replace, and file fsync + parent-directory fsync. These numbers are environment-specific and are **not** an Argus production benchmark.

| rows | file size | no fsync median | file fsync median | file+dir fsync median | file+dir p95 |
|---:|---:|---:|---:|---:|---:|
| 10 | 12.9 KiB | 0.30 ms | 2.32 ms | 3.89 ms | 10.95 ms |
| 100 | 129.3 KiB | 1.33 ms | 4.65 ms | 4.30 ms | 22.52 ms |
| 500 | 647.2 KiB | 5.91 ms | 7.73 ms | 8.56 ms | 17.61 ms |
| 1000 | 1294.7 KiB | 11.68 ms | 14.60 ms | 15.30 ms | 23.71 ms |

Interpretation limited to this environment: adding durable file+directory ordering cost single-digit milliseconds at the median even at 1000 representative rows, and is tiny relative to agent/model latency. However p95 jitter is material and target filesystems differ. Since every later Backlog rewrite replaces the whole file, making only the new exact-insert path durable is insufficient: a subsequent weaker whole-file rewrite can become the latest directory entry before final continuous enable. The structurally coherent candidate is to harden the shared `_atomic_rewrite_jsonl` primitive, then benchmark on the actual supported filesystems before claiming negligible cost.

## 6. Candidate refinement

`clean-os-g1-005` now has a sharper transaction boundary:
1. exact CAS A-enabled -> disabled `HandoffFenceV1` **before all semantic side effects**;
2. use fence target objective as reconciliation input, not as a serialized Prepared replay log;
3. reconcile/commit route under existing Manager pipeline lock;
4. supersede old work if this is a true replacement;
5. `ensure_operator_priority_item_exact` with immutable creation stamp and durable shared Backlog rewrite;
6. final exact CAS from the same fence to B-enabled only after route/row cross-checks;
7. recovery always re-reads actual state after any post-replace error;
8. process restart uses current-state `reconcile_or_rearm`; a fence is never a process-only stop;
9. semantic stop supersedes/cancels a fence; replacement objective uses source/target route comparison and never invents a missing superseded mission;
10. manager-handoff v4 remains derivative optimization, not authority.

No public Argus mutation or live daemon fault injection was performed.

## Exact continuation

1. Define the minimal typed durable recovery receipt/status needed to distinguish `fence -> Manager re-reconcile` from `fence -> route already target -> exact insert/finalize`, without adding a mutable user/model-controlled phase field.
2. Audit whether goal-contract writes and custom-domain materialization can leave crash-visible partial state that the source/target route fingerprint check misses; keep this bounded to recovery correctness rather than broad route refactoring.
3. Convert the harness above into source-exact pytest pseudocode with the current `test_pipeline_yield.py` fake `Prepared` seam and real `Backlog` plus existing daemon fault monkeypatches.
4. Keep external/admin `PIPELINE_STATE` writer fencing as a separate candidate branch.
