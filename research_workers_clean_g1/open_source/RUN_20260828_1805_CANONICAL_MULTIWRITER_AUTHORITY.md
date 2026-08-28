# Open Source follow-up — canonical events.jsonl has multiple unsynchronized append paths

- role: `open_source`
- invocation_started_at: `2026-08-28T17:57:43+09:00`
- observed/checkpoint draft time: `2026-08-28T18:05:18.512986+09:00`
- frozen semantic control tuple: note `7e893018d47b993fe17b3bdad4768d8d8eca4d3f`, root control `15`, role config revision `6`
- post-freeze note head observed only for authorized write coordination: `e39bf32aba5eaff753c79c96e25873abc0d39dbc`
- public Argus main observed unchanged: `2894b434affaff3a28c1fbbcd5c39f2e7a832236`
- public Portalocker develop observed unchanged: `c86f80c2505de8e44fb9d2493eb94ab96201fef6`
- clean scope: own role-local state + public sources only; no O/O-derived, other-worker, downstream, legacy/pre-independence, shared aggregate ledger, or other-role receipt/config semantics

## Candidate014 — event authority must cover AgentIOLogger and event migration, not only JsonlEventSink

The current public source has at least three append paths into the same canonical project `events.jsonl`:

1. `life/event_log.py::JsonlEventSink._append()` uses an instance-local thread lock plus `events.lock`, but cross-process locking is POSIX-only (`fcntl`). It alone owns canonical generation rotation and Mission View projection.
2. `adapters/agent_cli_backend/_io_log.py::_jsonl_append()` opens the same `events.jsonl` directly with `Path.open("a")` under an `AgentIOLogger` instance-local `threading.Lock`. `AgentCliBackend._agent_io_log_path()` resolves the project path directly to `<project_root>/events.jsonl`. `log_start_record`, call completion/error, `usage.recorded`, provider-request completion, and budget reservation rows all use this direct path. `AgentCliBackend` explicitly allows concurrency via separate backend instances, so these per-instance locks are not a shared same-file authority.
3. `core/usage.py::ensure_project_events_standardized()` appends one-time legacy event migration rows to canonical `events.jsonl` under `events.migration-v2.lock`, not `events.lock`; its identity scan and canonical append are therefore outside the authority currently used by `JsonlEventSink`.

This materially widens candidates009/011. Fixing only `JsonlEventSink` would leave canonical direct Agent I/O writes outside the Windows writer serialization, stable-reader exclusion, crash-tail record-boundary isolation, and migration de-dup snapshot.

### Deterministic crash-tail consequence

`AgentIOLogger._jsonl_append()` blindly writes `line + "\n"`. A source-shaped local byte probe seeded `events.jsonl` with an unterminated partial JSON record and then performed the same direct append shape for a valid `agent.io.start`. The result was one merged physical row and `JSONDecodeError`; adding exactly one delimiter before the new row preserved the damaged first row for forensics and made the new second row parseable. This is the same candidate011 failure mode already found in `JsonlEventSink`, now proven to apply to a second production canonical writer.

Therefore pre-rotation delimiter isolation cannot live only inside `JsonlEventSink._append`; it must be part of a shared canonical append primitive used by every writer to `events.jsonl`.

### Rotation and Windows scope

`AgentIOLogger` does not rotate canonical `events.jsonl`; it relies on the separate sink path eventually doing so. More importantly for correctness, its direct file handle does not honor `events.lock`. On Windows, a corrected Portalocker-backed sink authority would still not serialize against AgentIOLogger unless this path is migrated too. On POSIX, the same split invalidates any claim that `events.lock` is the sole writer barrier.

The minimum architectural boundary is now a core-level canonical event authority that can be imported by both `life` and `adapters` without introducing a life<->adapter cycle. The authority should:

- preserve `os.open(..., 0o600)` for the `events.lock` sidecar;
- use Portalocker low-level `LOCK_EX|LOCK_NB` at the selected `>=4.2` floor;
- retry only `AlreadyLocked`; propagate permanent acquisition failure;
- make post-commit unlock/fd-close cleanup best-effort so an accepted append cannot be reported as failed;
- expose a locked append operation that checks the current file's last byte and writes one `\n` delimiter iff the nonempty tail is unterminated, before any rotation/new record;
- allow `JsonlEventSink` to retain the authority through canonical append **and** `mission-view.lock` projection, preserving the required `events.lock -> mission-view.lock` order;
- let AgentIOLogger use the same authority for direct call/usage/provider/budget rows;
- let `ensure_project_events_standardized()` hold the same authority across its canonical identity scan plus migrated-row append, while retaining its own one-shot migration lock for migration idempotence.

A core module such as `core/event_store.py` (name not prescriptive) is cleaner than making `adapters` import `life.event_log`, because the latter risks a package-layer cycle. Existing `core/file_lock.py` can supply precedent, but its present 30-second helper catches all `LockException` and its unlock exception can escape; canonical authority needs the narrower `AlreadyLocked` retry and commit-boundary cleanup contract already identified in candidate009.

## Candidate013 — patch/test boundary can now be treated as settled research-wise

The prior signal/durable projection mismatch remains exact on the current public head. `round.review.started` is a durable Mission View handler input but is not guaranteed by default signal; `engineer.progress` is projected despite payload-dependent persistence. The low-churn durable contract remains:

- add `ROUND_REVIEW_STARTED` to the default signal set (and keep backend/frontend catalog mirrors consistent where generated/manual parity requires it);
- remove `ENGINEER_PROGRESS` from the durable Mission View event set/handler mapping, leaving high-frequency progress to live activity surfaces rather than a replay contract that depends on verbosity;
- add a structural invariant using the actual default filter: for every `EventType` handled by durable Mission View, `_should_persist_for_verbosity({"type": event_type}, "signal")` must be true;
- add a default-sink regression for `round.start -> round.review.started` proving the JSONL row survives and persisted Mission View marks Reviewer active before verdict; extend through the existing Web snapshot helper if practical;
- add the negative regression that ordinary marker-free `engineer.progress` remains absent from the clean canonical sink path and is not required for durable Mission View reconstruction.

One clarification from the broader writer map: `agent.io.start/complete` rows used by `role_activity()` are persisted by the separate AgentIOLogger direct path, not by the default `JsonlEventSink` signal filter. The reviewer-start defect still stands because `round.review.started` is emitted through the sink path, but the role-activity inflight-call mechanism should not be generalized as signal-filtered merely because those event types are absent from `SIGNAL_EVENT_TYPES`.

## Regression set added to the frontier

1. Hold `events.lock` in one process; an `AgentIOLogger` canonical append in another process/thread must not complete until release, then appear exactly once.
2. Seed an unterminated canonical tail; `AgentIOLogger.log()` of a valid row must leave the damaged row isolated and the new physical row parseable.
3. Coordinate sink rotation at threshold with AgentIO append on Windows/portable CI; after serialization both rows must remain exactly once and generation files stay parseable.
4. Hold canonical authority while `ensure_project_events_standardized()` attempts migration; migration must wait, then scan+append under one stable authority so its de-dup claim is not based on a concurrently changing generation set.
5. Existing writer/writer Windows test for two `JsonlEventSink` instances remains required; it is no longer sufficient alone.

## Exact continuation

On the next invocation, first re-bootstrap/freeze fresh control. Then source-map all remaining runtime writes to canonical `events.jsonl` to verify the three-writer inventory is complete. Specify the smallest core event-authority API that can be shared by `JsonlEventSink`, `AgentIOLogger`, and `ensure_project_events_standardized` without import cycles, including lock ordering and post-commit cleanup semantics. After that, return to implementation-level regression mapping for candidate013, then candidate009/011 shared authority + byte-stable reader, then `events.lock -> mission-view.lock`, Planner verdict `FOUND / ABSENT / UNKNOWN`, and explicit `iter_call_events` corruption behavior. Keep candidate008 power-loss durability and candidate005 transition provenance separate.

Semantic work stopped after post-freeze note-head drift was observed; the newer note head was not adopted or interpreted as control. No mutation outside the authorized open_source role-local state/output namespace is performed by this checkpoint write.
