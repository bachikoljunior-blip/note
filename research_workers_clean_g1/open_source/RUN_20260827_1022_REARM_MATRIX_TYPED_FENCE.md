# Open Source Systems Scan — Current-state rearm matrix and typed handoff contract

Invocation started: 2026-08-27T10:02:23+09:00
Checkpointed: 2026-08-27T10:22:00+09:00

Frozen semantic tuple remains the invocation's previously frozen `note@0690108bdb37bbcf3ca1ea9f7a032ca1706ea9b9 / control 11 / open_source config 5`. Only own clean state and public `lbx154/Argus` source were used.

## 1. A single `reconcile_or_rearm` boundary can replace five inconsistent resume semantics

Current public paths are semantically different despite all ultimately wanting "a daemon should be usable again":

| Path | Current state source | Current mutation | Main defect | Proposed boundary |
|---|---|---|---|---|
| Web daemon start | reads current disabled state | if reason merely starts `operator `, non-CAS enable **before admission/spawn** | can rearm intentional stop/hold and can mutate campaign even if daemon admission/spawn fails | start process without changing semantic state; boot calls `reconcile_or_rearm` |
| daemon boot `--resume-continuous` | reads current state | narrow `RESUMABLE_STOP_REASONS`, but non-CAS `write_continuous_config` | semantic command may land between read and rearm | exact CAS the exact disabled process-stop record; otherwise reconcile/no-op |
| immediate upgrade | snapshots continuous state before drain | after stop, copied pre-drain objective can be enabled again | concurrent newer objective/stop can be overwritten | never restore snapshot; after upgrade boot from current state only |
| scheduled upgrade | request stores `resume_continuous` + objective | completion later enables stored objective | stale upgrade can resurrect a stopped/replaced campaign | request stores process-upgrade intent only; completion reads current state |
| daemon replacement | passes `resume_continuous` into Web start helper | inherits Web start mutation | same broad-prefix/pre-admission defects | replacement is process lifecycle only; current-state boot gate decides |
| operator decision continue | reads card + current continuous | if disabled/nonempty, direct non-CAS enable | valid old human decision can rearm a newer route without semantic reconciliation | accept decision record, then separately reconcile/rearm current campaign |

The strong existing positive control is the daemon boot allowlist: only `operator drain-stop` and graceful SIGTERM/SIGINT mean process-only stop. Planner completion, operator authority hold, and semantic operator stop are not process-rearm reasons.

Proposed `reconcile_or_rearm(life_dir, *, resume_intent, manager, ...)` contract:

1. acquire/read the **current** continuous state;
2. if no resume intent: never enable anything;
3. if current state already enabled: validate manager-handoff-v4 fast-path or reconcile if needed; do not rewrite just to start the process;
4. if disabled because of exact process-only stop and objective is nonempty: CAS that exact state to enabled preserving objective/open-ended; on CAS mismatch restart from step 1 rather than applying stale data;
5. if disabled with structured handoff fence: recover/reconcile the fence, never process-rearm it;
6. if disabled for completion/hold/operator stop/content-policy/etc.: leave disabled unless an explicit semantic-resume command has passed Manager reconciliation;
7. semantic resume never copies an objective captured before the gate; it either uses the exact current disabled objective/route or creates a new fenced Manager handoff.

This makes "start executor" and "resume campaign" distinct capabilities.

## 2. `manager-handoff-v4` can retain generation `<=` after these process paths are fixed

Current continuous CAS includes `generation` in `_same_continuous_state`; process-only rearm necessarily increments it. Therefore identity generation equality is too strict for restart optimization.

After the process-control paths above stop restoring stale snapshots, v4 may safely retain the nonfuture relation only when all semantic conditions match:

```text
current.enabled
&& current.handoff_fence is None
&& identity.version == 4
&& identity.objective_sha256 == sha256(current.objective)
&& identity.route_v4 == canonical_route_identity(current protected route)
&& identity.continuous_generation <= current.generation
```

A process-only generation increment keeps objective+route identical. A semantic handoff either changes objective/route or leaves a disabled fence during transition. Thus a second semantic-generation subsystem is not source-justified at present.

Versions 1–3 still require one actual Manager reconciliation because their identity did not bind the full route contract.

## 3. `CreationStampV1` can be strict without inventing broad limits

Current `BacklogItem.new_id()` is exactly 12 lowercase hex characters (`uuid.uuid4().hex[:12]`). The identity-bearing digests are fixed-size SHA-256. No broad arbitrary maximum is required for most stamp fields.

Typed shape:

```python
@dataclass(frozen=True)
class CreationStampV1:
    version: Literal[1]
    item_id: str                 # ^[0-9a-f]{12}$
    manager_intent_id: str       # nonempty, must equal fence/prepared intent
    execution_task_sha256: str   # exactly 64 lowercase hex
    context_refs_sha256: str     # exactly 64 lowercase hex
    route_v4_sha256: str         # exactly 64 lowercase hex
    dispatch_contract_id: Literal["manager_operator_scope_v1"]
```

Validation is relational as well as syntactic:
- `item_id == handoff_fence.target_item_id`;
- stamp `manager_intent_id == handoff_fence.intent_id`;
- execution hash equals canonical Manager-clean target objective bytes;
- route hash equals canonical target route-v4 object;
- context refs are canonicalized first (stable field set/order, then sorted compact JSON) before hashing;
- unknown `version` fails closed;
- missing stamp on an already-existing target ID is not migratable during recovery.

`manager_intent_id` need not be forced into a new regex: it is an already-host-authored opaque identifier and safety comes from exact equality to the frozen fence/prepared handoff, not guessing its format. A reasonable generic string size cap could be added later for defensive parsing, but source evidence does not justify inventing one here.

## 4. `HandoffFenceV1` should be strict authority state inside `ContinuousConfigState`

Proposed typed shape:

```python
@dataclass(frozen=True)
class HandoffFenceV1:
    version: Literal[1]
    intent_id: str
    source_objective_sha256: str
    target_objective: str
    target_objective_sha256: str
    target_item_id: str
    creation_stamp: CreationStampV1
    source_route_v4: CanonicalRouteV4
    target_route_v4: CanonicalRouteV4
    target_open_ended: bool
```

Parser requirements:
- fence is either absent/`None` or one valid object; malformed/unknown version is a **hard state error**, not silently treated as no fence;
- target objective must be nonempty, matching the existing invariant for enabling continuous mode;
- objective hashes are 64 lowercase hex and recompute exactly;
- target item ID is 12 lowercase hex;
- nested stamp cross-checks target item/intent/objective/route;
- source/target route objects pass canonical enum/normalizer validation;
- `target_open_ended` is an actual bool, not Python truthiness from strings;
- no user/model-facing mutable `phase`; recovery phase derives from current route + exact backlog row as specified in the preceding checkpoints.

Because this object is authority-bearing, unknown same-version fields should not influence behavior. The safest simple parser is an exact known-key set for v1 and a version bump for extensions; forward-compatibility is recovered by failing closed to Manager/operator repair rather than interpreting a newer transaction partially.

## 5. Continuous-state plumbing required by the fence is small but easy to miss

Current `ContinuousConfigState` and persistence code explicitly enumerate fields. A correct implementation must update **all** of these places together:

- frozen dataclass adds `handoff_fence: HandoffFenceV1 | None`;
- `_read_continuous_state_unlocked` parses it fail-closed;
- `_write_continuous_config_unlocked` serializes it;
- `write_continuous_config` must not accidentally clear an active fence from a generic process-control write — ideally generic writes reject while a fence is present unless using the dedicated transaction API;
- `compare_and_swap_continuous_config` accepts/preserves/clears fence explicitly;
- `_same_continuous_state` compares the full fence plus generation;
- `_continuous_state_reserve_text` includes the fence and full target objective, otherwise ENOSPC reserve sizing underestimates the very recovery payload that matters most;
- status/UI description should identify `handoff_reconciliation` without exposing unnecessary full objective duplicates;
- disable/semantic-stop during a fence needs an explicit policy: a newer operator semantic stop should supersede/cancel the fence under exact CAS, not leave a latent transaction that later re-enables itself.

The current reserve is capped at 1 MiB; this proposal does not claim that cap is always sufficient for arbitrarily large objectives. It does require reserve sizing to account for whatever fence payload the implementation actually permits.

## 6. Suggested exact-CAS tests for `reconcile_or_rearm`

1. **Web start admission failure**: disabled `operator drain-stop`; request process start when daemon admission rejects. Continuous bytes remain disabled and unchanged.
2. **Web start after semantic operator stop**: reason `operator chose to stop the campaign`; process start does not enable it.
3. **Boot process-only race**: read disabled drain generation N; concurrent semantic command writes generation N+1; rearm CAS of N fails and must not overwrite N+1.
4. **Immediate upgrade race**: upgrade begins with A; concurrent command replaces/stops A during drain; post-upgrade startup never writes copied A.
5. **Scheduled upgrade stale request**: schedule while A enabled; operator stops/replaces before completion; completion restarts process but does not resurrect A.
6. **Replacement**: replacing a daemon uses current-state boot policy, not the broad Web-start prefix.
7. **Old operator decision**: accepting a previously asked "continue?" stores the human answer, but if current semantic route/objective differs, execution enters Manager reconciliation rather than direct enable.
8. **Fence not process-rearmable**: disabled structured handoff fence + `resume_intent=True` triggers fence recovery/reconcile, never plain enable.
9. **v4 process generation drift**: same objective+route, later process-only generation => identity fast-path accepted.
10. **v4 semantic route drift**: same objective, same vertical/domain, workflow or research venue changed => fast-path rejected.

## Candidate refinement

`clean-os-g1-005` is now implementable as a set of narrow reusable primitives rather than one large rewrite:
- `CreationStampV1` + immutable Backlog creation identity;
- `Backlog.ensure_operator_priority_item_exact` with durable exact-once insert;
- `HandoffFenceV1` inside exact-CAS continuous state;
- `canonical_route_identity_v4` from persisted semantic route, after fixing explicit target-venue preserve/clear/set semantics;
- one current-state `reconcile_or_rearm` process/semantic resume boundary;
- manager-handoff v4 as a derivative restart optimization, not authority.

No live mutation, daemon fault injection, or latency benchmark was performed.

## Exact continuation

1. Design the exact real-Backlog + continuous fault-injection test harness, including pre-replace callback success/final replace failure, post-replace directory-fsync error, two recoveries, and one task-added event.
2. Define cancellation/supersession semantics when a new operator semantic stop or replacement objective arrives while `HandoffFenceV1` exists.
3. Benchmark Backlog durable rewrite at 10/100/500/1000 rows and isolate file-fsync vs directory-fsync lock time.
4. Keep external/admin `PIPELINE_STATE` writer fencing separate.
