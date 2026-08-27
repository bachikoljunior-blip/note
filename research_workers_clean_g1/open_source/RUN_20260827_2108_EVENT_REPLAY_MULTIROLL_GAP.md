# Open Source Systems Scan — persisted event replay contract and multi-roll Mission View bootstrap gap

Invocation started: 2026-08-27T21:00:37+09:00
Checkpointed: 2026-08-27T21:08:09.765951440+09:00

Semantic authority is frozen at `note@57adc1553d25dae0476166416e45de74035f1b0c / control 12 / open_source config 5`. The note repository advanced after semantic freeze; later control semantics were not adopted. Only this role's clean state plus public source were used semantically. Public Argus source was refreshed during the invocation: current `lbx154/Argus` main was observed at `a8a74029ae4a8f0bf488854b9e5f75ec0843f877`, ten commits ahead of the prior role checkpoint `8a867e7b45f863a9cd4e79e4f6d21ca7a2009e48`.

## 1. Normal persisted-event replay preserves the original event timestamp

The prior frontier asked whether replay changes `ts`, because a stable `event_id` only gives stronger Mission View idempotency if a replayed persisted event does not receive a fresh timestamp.

Current public source gives a clean answer for the inspected normal replay paths:

- `JsonlEventSink._normalize()` calls `normalize_event_envelope(event, timestamp=time.time())`, but `normalize_event_envelope` uses `out.setdefault("ts", ...)`. A caller-supplied timestamp is preserved, and a missing timestamp is injected once before the row is persisted.
- `JsonlEventSink._append()` serializes that normalized payload directly to `events.jsonl`.
- Mission View cold replay `_tail_jsonl()` does `json.loads()` and passes the persisted dict directly to `reduce_mission_view_event()`; it does not re-normalize the envelope.
- CLI/watch JSONL tail paths likewise decode the persisted JSON row without replacing `ts`.
- WebSocket follow decodes the event JSON and forwards it without timestamp replacement.

Therefore the normal durable replay path preserves the original persisted `ts`. The earlier concern that ordinary replay might mutate reducer timestamps is reduced. A generic stable `event_id` remains useful for duplicate cardinality and durable append dedupe; a reducer-entry seen-event guard is not currently required merely to compensate for timestamp reinjection during normal replay.

Scope guard: this does not prove generic whole-reducer exactly-once semantics for every transport or future producer. It establishes the current persisted-log replay behavior inspected here.

## 2. Generic `event_id` belongs in the envelope, but current Python validation does not validate it

Frontend `eventKey()` already treats `event.event_id` as the highest-priority replay identity, ahead of `id`, `seq`, and `_offset`, and explicitly documents that array position is excluded because REST and WebSocket replay can observe the same event at different positions.

Python `validate_event_envelope()` currently validates type, known payload requirements, numeric `ts`, and positive `event_schema_version`, but has no generic rule for `event_id`. `normalize_event_envelope()` preserves arbitrary extra fields, so caller-supplied `event_id` already survives serialization.

Narrow candidate contract:

```text
event_id absent                           -> valid legacy/current event
event_id present and non-empty string     -> valid stable event identity
event_id present but blank/non-string     -> envelope validation failure
```

No event-specific payload schema is needed for this identity field. For handoff recovery, `life.planner.task_added` can deterministically use an ID derived from the stable backlog item identity plus immutable creation identity; ordinary planner tasks need not be retrofitted until a caller requires replay-exact append semantics.

## 3. New independent candidate: Mission View cold bootstrap ignores retained event generations `.2+`

A separate public-source correctness gap emerged while following replay storage.

`argus_skill/life/event_log.py` explicitly retains every rollover generation. Older immutable logs accumulate as `events.jsonl.2`, `.3`, ...; `.1` is the newest completed generation, and the live file is `events.jsonl`.

Argus already has a correct full-history enumerator in `argus_skill/life/memory.py::_jsonl_history_paths()`, ordered oldest-to-newest as `.2`, `.3`, ..., `.1`, live. Its comments document a real analogous failure class: reading only `.1` previously made daily spend disappear after more than one rollover.

But `argus_skill/core/mission_view/_snapshot.py::_bootstrap_view()` still hard-codes only:

```python
for path in (root / "events.jsonl.1", root / "events.jsonl"):
    for event in _tail_jsonl(path):
        reduce_mission_view_event(view, event)
```

So a cold Mission View rebuild after two or more rotations ignores every projected event in `.2+`. `_tail_jsonl()` additionally reads only the last 8 MiB of each selected file.

This matters because not all Mission View state is reconstructed from live overlays. In particular, `life.manager.intent.completed` is the event that projects `routing.route`, `routing.vertical`, `routing.workflow_mode`, `routing.lifetime`, and continuous/open-ended routing flags. `build_snapshot()` later overlays backlog/session/daemon/continuous/current-stage, but does not supply the full protected route tuple to `merge_mission_view_snapshot()`. Thus a missing/corrupt/rebootstrap-required `mission-view.json` can rebuild with current stage/objective repaired while older event-sourced routing/history fields are absent if the authoritative Manager intent has rolled into `.2+`.

This is a **cold-bootstrap/recovery observability correctness gap**, not evidence that ordinary live Mission View projection loses events. Online projection writes `mission-view.json` as events arrive.

### Minimal source-shaped regression

1. Do not create `mission-view.json`.
2. Put an old `life.manager.intent.completed` event with `vertical="software"`, `workflow_mode="staged"`, `route="team"` in `events.jsonl.2`.
3. Put later projected events that do not restate route identity in `.1` and the live file.
4. Call `snapshot_mission_view(...)`.
5. Require routing to retain the Manager route fields from `.2`.
6. Add an ordering case `.2 -> .3 -> .1 -> current` so later events correctly win.

No existing test found in the public tree exercises Mission View bootstrap from `events.jsonl.2` or deeper generations.

## 4. Correctness/performance shape for fixing multi-roll bootstrap

A naive full replay of every byte in a multi-gigabyte retained log is undesirable. The current code already provides useful implementation precedent:

- `_jsonl_history_paths()` gives correct retained-generation ordering.
- `_read_jsonl_tail_history()` can search across every generation using a predicate, raw markers, and optional ripgrep fast path for sparse event types.
- Mission View has an explicit `_PROJECTED_EVENT_TYPES` set.

The smallest robust design should preserve module layering while reusing the same retained-generation ordering and scan only projected event rows. Options to falsify/benchmark next:

1. extract retained JSONL generation enumeration to a small core storage helper shared by `life.memory` and Mission View;
2. add a Mission-View-local equivalent but keep one conformance test against event-log rotation ordering;
3. use a sparse projected-event scan across all generations rather than last-8-MiB tails;
4. longer-term, persist a compact replay checkpoint plus source-log cursor so cold boot never needs lifetime replay.

The first correctness requirement is that no retained generation containing projected events is silently omitted. Performance optimization comes after that invariant.

## 5. Existing handoff candidate remains live on current public main

The public head advanced by ten commits, including changes in `memory.py`, planner enqueue, stage operations, stage machine, and vertical selection. Reinspection still found:

- `Backlog.add()` can append a duplicate ID, while `add_many()` rejects IDs already in live/archive state;
- generic `Backlog.update()` can mutate any existing dataclass field, so a future immutable `creation_stamp` still needs explicit protection;
- `_atomic_rewrite_jsonl()` writes a sibling temp and `os.replace()` but does not call file `fsync` or parent-directory `fsync`; `_append_jsonl()` does file `fsync` only;
- current `commit_vertical_decision -> reset_stage_for_new_intent` still has no `transition_id` parameter, and repo search found no `stage_history.transition_id` field.

So `clean-os-g1-005` remains a separate handoff-local candidate. The new Mission View multi-roll issue should remain a separate candidate rather than being folded into that authority transaction.

## Candidate update

New candidate `clean-os-g1-006`: **cold Mission View rebuild must enumerate every retained canonical event-log generation in authoritative order and replay all projected events needed to reconstruct the read model; a bounded-tail optimization may not silently omit older retained generations. Prefer a sparse projected-event scan or durable checkpoint/cursor over whole-log brute-force replay.**

Evidence strength: public-source reachability/implementation inspection. No live failure reproduction or benchmark was performed in this run.

## Exact continuation

1. Inspect Mission View projected-event sparsity and existing core/life module dependencies to select the smallest non-circular retained-generation helper.
2. Turn the `.2 -> .3 -> .1 -> current` bootstrap case into exact pytest modifications and include a >8 MiB projected-event survival case or an equivalent sparse-scan invariant.
3. Benchmark sparse all-generation projected-event reconstruction against current two-file tail bootstrap on synthetic multi-roll logs; keep correctness fixed before optimizing.
4. In parallel, map the existing front-door and daemon-boot replacement tests onto the four `transition_id` reset-lineage regressions from `clean-os-g1-005`.
5. Keep global/external protected `PIPELINE_STATE` writer fencing separate from both candidates.
