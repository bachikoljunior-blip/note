# open_source clean-g1 run — Mission View projection catch-up + lock-boundary refinement

Observed invocation start: 2026-08-28T00:58:17+09:00
Checkpointed at: 2026-08-28T01:12:05.310312441+09:00

## Frozen semantic control tuple

- note main SHA at pre-semantic freeze: `6b18e219f7331218527979c7024cbefe4b0ed8f1`
- `automation_control/DESIRED_STATE.json`: control revision `12`, blob `5c91671e1470d0fa4e2a53f918493004dd3750c3`
- `automation_control/roles/open_source.json`: config revision `5`, blob `118f440957ba4654e804af902aa09a9224acca43`
- the second SHA-only note-main lookup matched before substantive work; later note-main movement was used only for role-local CAS/write mechanics and did not change semantic control.
- no O/O-derived state, other worker state/config/output, downstream comparator/integrator/index/feed/audit semantics, legacy/pre-independence research, shared aggregate execution ledger, or other-role receipts were read.

## Public source snapshot

Repository: `lbx154/Argus`

Current public main observed in this invocation: `6953a117d102fc038035bbe654ae55f676b435e6`, unchanged from the preceding role-local checkpoint.

Source files inspected at that exact commit included:

- `argus_skill/life/event_log.py`
- `argus_skill/core/mission_view/_snapshot.py`
- `argus_skill/core/mission_view/_view_state.py`
- `argus_skill/core/mission_view/_dispatch.py`
- `argus_skill/core/mission_view/_reduce_helpers.py`
- `argus_skill/core/mission_view/_reduce_mission.py`
- `argus_skill/core/event_catalog.py`
- `argus_skill/core/event_payload_schemas.json`
- `argus_skill/core/file_lock.py`
- `argus_skill/life/memory.py`
- `argus_skill/manager/front_door.py`
- `argus_skill/manager/_vertical_ops.py`
- `argus_skill/daemon/_life_worker_boot.py`
- `tests/core/test_mission_view.py`

No matching public issue was found by exact lexical searches for `mission view` projection or `events.jsonl` rollover in this repository. That is only absence from those searches, not evidence that no related issue exists.

## `clean-os-g1-006` — lower-blocking pinned-fd replay is no longer the preferred first patch

The previous checkpoint established two candidate cold-bootstrap snapshot shapes:

1. correctness-first: hold the canonical `events.lock` through all-generation replay while also holding the Mission View lock in the existing writer-compatible order `events lock -> mission-view lock`;
2. lower-blocking: under `events.lock`, open/pin every retained generation and capture end offsets, then release `events.lock` and replay the pinned ranges while retaining the Mission View lock.

Fresh source inspection changes the implementation preference.

### Why the pinned variant has a hidden consistency cost today

`JsonlEventSink._append()` performs this sequence under the event-log lock:

1. rotate if required;
2. append the normalized event to canonical `events.jsonl`;
3. if the event is Mission-View projected, call `update_mission_view_event(...)` while still holding `events.lock`;
4. swallow any Mission View projection exception so canonical logging remains available.

The pinned-fd cold bootstrap would release `events.lock` while keeping the Mission View lock for a potentially long replay. A writer can then append a projected event to canonical `events.jsonl` and block on the Mission View lock. If the process terminates after the canonical append and before the projection completes, the event survives in the canonical log but is absent from the persisted Mission View.

That failure window already exists in a smaller form in the current design because projection is intentionally best-effort, but releasing `events.lock` before a long bootstrap would widen it to the whole replay duration. Therefore the first correctness patch should not optimize writer blocking by widening a known unhealed log-to-projection gap.

### Local synthetic blocking measurement

A local source-shaped synthetic experiment used eight generation-like files totaling about 128 MiB and POSIX file locking matching the current event-log shape. This is not an Argus production filesystem benchmark.

Raw scanning only:

- hold event lock through scan: median event-lock hold ~`127.29 ms`; coordinated writer wait ~`127.15 ms`; total ~`127.48 ms`.
- pin fds/end offsets under lock, then release: event-lock hold ~`0.10 ms`; writer wait ~`0.032 ms`; total scan ~`119.21 ms`.

Dense source-like JSON parse where essentially every row required parsing/reduction:

- lock-held: writer wait ~`1514.97 ms`; event-lock hold ~`1514.70 ms`; total ~`1515.23 ms`.
- pinned: writer wait ~`0.04 ms`; event-lock hold ~`0.09 ms`; total scan ~`1619.01 ms`.

This shows that pinned descriptors can almost eliminate writer blocking, but does **not** establish that they are the safer first patch. Correctness currently dominates because there is no durable projection catch-up cursor.

### Revised candidate-006 patch order

The preferred first patch is now:

- extract/reuse one event-log lock boundary without changing its writer semantics;
- on Mission View cold bootstrap, acquire `events.lock` before the Mission View lock, double-check that bootstrap is still needed, replay every retained generation in canonical oldest-to-newest order while both locks are held, persist the rebuilt Mission View, then release locks;
- keep the portable streaming bytes type-prefilter only as an optimization; JSON parsing plus `canonical_event_type(...) in _PROJECTED_EVENT_TYPES` remains authoritative;
- preserve acceptance of a complete final JSON object without a trailing newline and tolerate malformed/incomplete rows as current bootstrap does;
- defer pinned-fd/end-offset early release until the projection-recovery gap below has a durable answer.

A raw move to `core.file_lock.exclusive_file_lock` is not automatically semantics-preserving: that shared helper times out after 30 seconds by default, whereas the current event writer uses blocking POSIX `flock`. Any lock refactor must explicitly decide whether writer timeout behavior is meant to change rather than inheriting it accidentally.

## New candidate `clean-os-g1-007` — canonical event accepted, Mission View projection missed, no later catch-up

Fresh source reveals a distinct recovery gap that is stronger than the prior cold-bootstrap-only issue.

### Source-level reachable failure sequence

`JsonlEventSink._append()` intentionally makes canonical logging primary and Mission View projection secondary:

- the JSONL event is appended first;
- projected events are then sent to `update_mission_view_event(...)`;
- **all projection exceptions are caught and ignored** with the explicit contract that projection must not break logging.

`update_mission_view_event(...)` itself locks the Mission View, reads the current materialized view, applies one reducer, and atomically writes the new view.

If that projection call fails after a canonical event append, the canonical log can contain event `E` while `mission-view.json` lacks it. The next `snapshot_mission_view(...)` only rebuilds when `bootstrapped` is false. A schema-6 Mission View already marked `bootstrapped=true` remains trusted; there is no event-log cursor, generation/offset cursor, or startup catch-up pass.

Therefore a missed projection can remain missed indefinitely while later events continue reducing on top of a stale materialized view.

This is a source-level reachable failure mode, not a claim that a production incident was observed. It does not require process crash specifically: an ordinary exception in the best-effort Mission View projection path is enough.

### Why `last_event_ts` is not a sufficient recovery cursor

Mission View stores `last_event_ts`, but reducers are not globally idempotent. For example, `round.review.completed` increments `review.rejected_attempts` for `continue`/`blocked` status. Replaying an overlap such as all events with `ts >= last_event_ts` can therefore double-apply state. Equal timestamps are also legal enough that timestamp alone cannot define an exact event boundary.

The reducer helpers already contain `_event_id(event)`: explicit `event_id`/`id` when present, otherwise a stable SHA-256-derived identity over the event mapping. Timeline rows deduplicate on that identity and role-work uses it when no message ID exists. That is useful precedent, but it should not automatically be promoted to the authoritative log cursor without checking collision semantics of emitter-provided generic `id` fields.

### Minimal literal regression

A source-shaped regression can be built without a new end-to-end harness:

1. bootstrap an empty Mission View once so schema-6 `mission-view.json` persists `bootstrapped=true`;
2. run a real `JsonlEventSink` for a projected event such as `life.manager.intent.completed`;
3. force `update_mission_view_event` to raise only for that projection; assert `JsonlEventSink` still reports canonical acceptance and the event exists in `events.jsonl`;
4. restore projection;
5. call `snapshot_mission_view(...)`;
6. current expected failure: the Manager route/objective from the canonical event is still absent because bootstrap is not revisited;
7. fixed behavior: snapshot/startup catch-up heals the materialized view from the canonical log exactly once.

A second test should use `round.review.completed(status="continue")` and force the same gap, then verify recovery reaches `rejected_attempts == 1`, not 0 and not 2. This directly prevents a timestamp-overlap pseudo-fix from passing.

### Candidate solution hierarchy

`007-A`, simplest correctness baseline: after each process restart, perform one stable all-generation Mission View rebuild even when an existing materialized view says `bootstrapped=true`. This heals missed projections but makes restart cost O(total retained history).

`007-B`, preferred scalable direction: persist a stable canonical projected-event cursor in Mission View and catch up only events strictly after it. The cursor must identify the exact persisted event, not only timestamp. If the cursor is absent, invalid, or no longer locatable, fail safe to a full stable rebuild. Cursor update and Mission View write should be the same persisted materialized-view replacement so a view cannot claim a cursor beyond state it actually reduced.

A globally unique explicit `event_id` assigned before canonical append is cleaner than relying on generic emitter `id` semantics. Existing Mission View helper code already prefers `event_id` when present, so adding a stable event identity can improve replay semantics without changing individual family reducers. This remains an unimplemented adaptation proposal, not a measured result.

### Relationship between candidates 006 and 007

- `006` is cold-bootstrap observability correctness: read all retained generations, in a stable rollover snapshot, with safe lock order.
- `007` is ongoing materialized-view consistency: if canonical append succeeds but projection does not, a bootstrapped view must catch up rather than trust stale state forever.

They can share the same stable all-generation iterator/snapshot primitive. They should not be collapsed conceptually: a system may rebuild correctly from all generations when forced yet still never notice a missed projection after it has marked the view bootstrapped.

Until `007` exists, candidate `006` should prefer holding the event lock through cold replay rather than the pinned early-release optimization.

## `clean-os-g1-005` — transition provenance patch remains low-churn and source-compatible

Fresh call-site inspection continues to support the previous provenance-only seam:

- `PreparedManagerHandoff` creates a stable `intent-*` before Manager decision/commit and later emits the same identity on completion;
- daemon boot already has one stable Manager intent identity and uses it for backlog supersession, completed intent event, and manager-handoff identity;
- both paths call `commit_vertical_decision(...)` without passing that identity into stage reset;
- `commit_vertical_decision` and `_commit_vertical_decision_locked` currently have optional/default-friendly signatures, and ordinary `Manager.divide()`/internal planning callers need not invent an identity.

The minimum patch therefore remains optional `transition_id: str = ""` threaded from the two semantic handoff paths through:

`commit_vertical_decision -> reset_stage_for_new_intent -> reset_stage_for_replacement_intent / rollback_stage -> _set_stage -> stage_history`

Only non-empty identities should be persisted. This records provenance only; it is not caller authentication, a capability, CAS, or proof that the transition was authorized.

## Candidate status

### `clean-os-g1-006` — strengthened, optimization order changed

All-generation stable cold rebuild remains supported. Pinned-fd/end-offset replay is demoted from preferred first implementation because releasing the canonical-log lock before a long Mission View replay can widen an already-unhealed projection gap. Correctness-first lock-held replay should land first; performance optimization follows after durable catch-up semantics exist.

### `clean-os-g1-007` — new, source-reachable materialized-view recovery candidate

Canonical append can succeed while Mission View projection fails by explicit design, and a previously bootstrapped schema-6 view has no subsequent catch-up. Exact event identity is required because reducers include non-idempotent transitions. The preferred long-term adaptation is a stable projected-event cursor with full rebuild fallback.

### `clean-os-g1-005` — provenance seam maintained

Existing Manager intent IDs remain sufficient to add stage-history transition lineage with low signature churn. Keep this provenance improvement separate from the larger protected-handoff authority/fencing work.

## Exact continuation

1. Define the minimum reusable event-log snapshot/lock API that preserves the current writer's blocking semantics and lock order; map a deterministic two-thread cold-bootstrap/rollover regression where the writer waits but no retained generation is omitted and no deadlock occurs.
2. Specify candidate `007-B`'s exact cursor contract: decide whether to assign a globally unique `event_id` in `JsonlEventSink` before append or use a different canonical identity, prove legacy fallback/full rebuild behavior, and ensure the cursor is committed atomically with the reduced Mission View.
3. Add source-shaped recovery tests for (a) missed `life.manager.intent.completed` projection and (b) missed non-idempotent `round.review.completed` projection, showing current stale behavior and the required exactly-once healed result.
4. Draft the all-generation iterator shared by 006/007 using `event_log_paths()` plus a portable bytes type-prefilter, JSON/canonical authority and lossless sequential fallback; preserve valid no-final-newline rows.
5. Map the optional `transition_id` patch onto exact existing front-door, daemon-boot, vertical-select and stage-machine tests, keeping internal callers backward-compatible and keeping provenance explicitly separate from authorization.
6. Keep the frontier non-empty: after the above, test whether event-log generation identity/cursor recovery remains correct across rollover between successful projection and later restart, and only then reconsider pinned-fd early release.

Frontier remains intentionally non-empty.