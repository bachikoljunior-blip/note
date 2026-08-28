# open_source checkpoint — event authority API and writer inventory

Observed semantic window: 2026-08-28T19:01:20+09:00 through pre-write freeze. Semantic control was frozen on note main `d6a6857ade76e9f6d89a0bb42e987d44f4571a90`, root control revision 15, `open_source` config revision 6. Public Argus source was inspected at current main `2894b434affaff3a28c1fbbcd5c39f2e7a832236`. Later note heads were observed only for authorized write coordination; no later control semantics were adopted.

## Update

The source-visible production writer inventory for `events.jsonl` is now classified rather than merely counted. I found no fourth production append mechanism in targeted source searches after separating read-only occurrences and writes to other JSONL files:

1. `life/event_log.py::JsonlEventSink._append()` writes the canonical sink stream, rotates generations, and projects Mission View. It currently serializes cross-process only through POSIX `fcntl`.
2. `adapters/agent_cli_backend/_io_log.py::AgentIOLogger.log()` reaches `_jsonl_append()` and directly appends one normalized row under an instance-local `threading.Lock`. `AgentCliBackend._agent_io_log_path()` routes a configured project to `<project_root>/events.jsonl`; without that project context it may route to `ARGUS_SKILL_AGENT_IO_LOG` or `<working_dir>/.argus/events.jsonl`.
3. `core/usage.py::ensure_project_events_standardized()` reads legacy `<project_root>/.argus/events.jsonl*`, scans canonical identities, and directly appends to `<project_root>/events.jsonl` under `events.migration-v2.lock`, not `events.lock`.

False positives were checked: `core/transcript.py` appends `transcript.jsonl`, `apps/_inbox.py` writes `inbox*.jsonl` and delegates its event to `JsonlEventSink`, and `life/memory.py` reads `events.jsonl` while its generic append helper is for backlog/history files. The raw provider transcript in `_io_log.py` is `agent_io.jsonl`, explicitly documented as a bounded debug artifact; it should stay outside the canonical event-authority primitive.

## Smallest core API boundary

The least-coupled placement remains a new `core/event_store.py` (name provisional), importable from `life`, `adapters`, and `core/usage` without a life↔adapter cycle. The primitive should stay below event normalization and Mission View semantics. A compact contract is:

- `EventLogAuthorityError(OSError)`: domain error for permanent lock-acquire failures. Making it an `OSError` preserves `AgentIOLogger`'s fail-soft logging boundary instead of leaking a Portalocker exception into provider execution.
- `event_log_authority(log_path)`: create/open the adjacent lock sidecar with `os.open(..., O_CREAT|O_RDWR, 0o600)`, wrap it as a real file object, acquire low-level Portalocker `LOCK_EX|LOCK_NB`, retry only `AlreadyLocked`, surface other acquire failures as `EventLogAuthorityError`, and make unlock/close cleanup best-effort after the caller may already have committed a record.
- `isolate_unterminated_tail_unlocked(log_path)`: while authority is already held, inspect only the final byte in binary mode and append exactly one `\n` when the nonempty live file is unterminated. Never truncate damaged bytes.

Rotation, normalization, and Mission View projection should not be put in this low-level helper. `JsonlEventSink` keeps its configured `roll_bytes`, but executes `tail isolation -> _maybe_roll() -> append -> Mission View projection` while shared event authority is held. `AgentIOLogger.log()` executes `tail isolation -> append` under the same authority and keeps raw `agent_io.jsonl` batching/rotation unchanged. Migration keeps `events.migration-v2.lock` and additionally holds canonical event authority across its canonical identity scan plus append; marker persistence remains outside the canonical commit boundary but inside the migration lock.

The error type matters. Current `_jsonl_append()` catches `OSError` only. If the new authority propagated `portalocker.exceptions.LockException` directly, a permanent lock failure could newly escape the logging path and break a provider call, violating the module's fail-soft contract. Normalizing permanent event-authority failures to an `OSError` subclass avoids that regression while still allowing `JsonlEventSink` to return `False` and migration callers to retry later.

## Candidate 011 interaction

Delimiter isolation belongs below all three canonical writers, not inside `JsonlEventSink._append()`. For the sink the order remains `authority -> delimiter isolation -> rotation -> new record`. For AgentIO there is no event-log rotation today, but it still needs `authority -> delimiter isolation -> new record`; otherwise a crash-torn tail absorbs a valid `agent.io.*` row. Migration likewise must isolate the canonical tail before imported rows.

The later stable-reader work should remain byte-row based. `iter_call_events()` still opens generations in strict UTF-8 text mode and skips unterminated rows; the usage migration's `_event_identities()` and legacy row loop are also text-mode readers. Do not mix reader recovery into the first authority patch unless tests require it; keep a second primitive for stable byte-based generation snapshots so corruption behavior is explicit rather than silently broadened.

## Candidate 013 regression placement

- `argus_skill/core/event_catalog.py`: add `EventType.ROUND_REVIEW_STARTED` to `SIGNAL_EVENT_TYPES`.
- `argus_skill/core/mission_view/_dispatch.py` and `_view_state.py`: remove `ENGINEER_PROGRESS` from the durable Mission View dispatch/projected set while retaining `ROUND_REVIEW_STARTED`.
- `tests/test_event_verbosity.py`: add a default/signal persistence assertion for `round.review.started` and retain a negative assertion for ordinary `engineer.progress`.
- `tests/core/test_mission_view.py`: add/adjust the invariant that every durable Mission View event type is persistable under default signal with a minimal payload, plus reviewer-active state coverage.

This is preferable to projecting filtered events directly, because durable Mission View remains replayable from canonical event history.

## Test frontier

1. Cross-process canonical authority: one process holds `events.lock`; an AgentIO canonical append cannot complete until release, then appears exactly once.
2. Mixed sink/AgentIO rotation near threshold: all generations parse and each record appears once on Windows/POSIX.
3. Tail isolation through AgentIO and migration: seed an unterminated/damaged row, append a valid event, preserve damaged bytes and parse the new row.
4. Permanent lock-acquire failure: `AgentIOLogger.log()` remains fail-soft because authority failure is an `OSError` subclass; `JsonlEventSink.append()` reports failure rather than raising.
5. Post-commit unlock failure: cleanup failure cannot convert a committed record into apparent failed append/retry.
6. Migration contention: canonical identity scan and append share ordinary event authority; marker is written only after canonical rows flush/fsync.
7. Candidate013 default-signal/Mission-View invariants.
8. Then candidate009/011 byte-stable snapshot, strict `events.lock -> mission-view.lock`, PlannerVerdict `FOUND/ABSENT/UNKNOWN`, and explicit `iter_call_events` corruption behavior.

## Frontier / exact continuation

Fresh-bootstrap first. Re-read root manifest and role config before using this checkpoint. Then inspect the migration-marker/source-change contract before changing migration locking: determine whether any current production path can continue writing `<project_root>/.argus/events.jsonl` after `events.migration-v2.json` exists. If yes, a marker keyed only by existence can permanently miss later legacy rows and authority alone does not solve it; specify a source-signature/replay rule or prove the writer unreachable. After that, finalize the `core/event_store.py` API/test matrix above, then proceed to candidate013 tests and candidate009/011 stable-reader + Mission View/Planner tri-state work. Keep candidate008 power-loss durability and candidate005 provenance separate.

No O/O-derived, other-worker, downstream, legacy/pre-independence, shared aggregate ledger, commit-message/diff semantics, or repository mutation probes were used. No source/control/branch/ref mutation was performed; this checkpoint is the authorized role-local state write.