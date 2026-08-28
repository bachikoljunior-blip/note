# Open-source scan checkpoint — event migration replay + retained-generation order

## Frozen control / clean boundary

- Role: `open_source` / `clean_exploration`.
- This invocation froze semantic control at note commit `6c593ed993f9d143bde084d7cc5841ed7c611c1c`, root control revision 15, role config revision 6.
- Later note-head movement was observed only for write coordination. No newer control semantics were adopted.
- Semantic inputs used: this role's own clean state plus public Argus source only. No O/O-derived state, other-worker state/config/receipts, downstream state, legacy/pre-independence semantics, or shared aggregate ledger was read.
- No Argus/source/control/branch/ref mutation was performed.

## Public source revision checked

Argus `main` was SHA-only verified at `eb078f89a82d52fdc9e4043e83c5753ef3c45843` during this run. The two commits since the previous role-local checkpoint were a release rebuild and a WebAPI persistence-failure fix; the event-log / usage files inspected below remain affected at that head.

## Candidate 015 — `events.migration-v2.json` is a one-shot claim without a consumed-source boundary

### Current source behavior

`AgentCliBackend._agent_io_log_path()` still has three routing classes:

1. usage-context project root -> call `ensure_project_events_standardized(project_root)`, then `<project_root>/events.jsonl`;
2. explicit `ARGUS_SKILL_AGENT_IO_LOG` -> that path;
3. otherwise, when `RunnerOptions.working_dir` is set -> `<working_dir>/.argus/events.jsonl`.

`ensure_project_events_standardized()` currently returns immediately when `<root>/events.migration-v2.json` exists. The marker written after migration contains `version`, `completed_at`, source path strings, and row counters, but no size/file identity/consumed offset or content boundary.

Two independent failure modes follow.

### 015-A: later legacy growth can be stranded

A source-reachable exported-API sequence can use the working-dir fallback, later use a project usage context that creates the migration marker, and later use a bare backend/working-dir fallback again. The later `.argus/events.jsonl` rows are never reconsidered because the next standardization call returns on marker existence before observing source state.

A source-shaped local model of the current function produced: first migration appends 1 row; a later legacy append occurs; the second migration returns 0; canonical history still contains only the first row.

Scope qualification: this establishes a supported/exported backend path and mixed-context risk. It is **not** a claim that the current 7x24 daemon normally takes this route: daemon boot sets `ARGUS_SKILL_AGENT_IO_LOG` to the canonical runtime log, and the normal supervisor construction supplies a project usage context. Standalone Doctor/research fallback constructors remain bare-backend writers when that environment override is absent, but exact same-root post-marker reachability is contextual.

### 015-B: a source open failure can still commit the marker

Inside the migration loop, `source_path.open("r", encoding="utf-8")` catches `OSError` and `continue`s. After the loop the function fsyncs canonical and writes the v2 marker unconditionally. Therefore one temporarily unreadable retained legacy generation can be silently skipped and then permanently hidden by the existence-only marker on every future call. This does not require any later writer.

The analogous canonical identity scan also silently skips generations it cannot open. That can turn unknown canonical history into an incomplete identity set and allow duplicate migration rows. The shared event-authority work should make canonical identity evidence fail closed on unreadable generations rather than interpret them as absent.

### Required marker semantics: replayable v3 snapshot, not post-scan signature

Use a marker as an optimization/progress certificate, not a one-time tombstone.

1. Under the migration-specific lock, enumerate current legacy generations.
2. Open each source in binary mode first and capture its **pre-scan** `fstat` boundary: logical path, file identity (`st_dev`, `st_ino` where available), `st_size`, and optionally `st_mtime_ns`. Keep the opened handle for the bounded scan when practical so rename cannot retarget the read.
3. A v3 marker matches only when its consumed source snapshot equals this fresh pre-scan snapshot. Existing v2 markers have no trustworthy consumed boundary and should force one idempotent rescan before being upgraded.
4. Scan only physical rows wholly contained within the captured byte size and require a terminating newline inside that boundary. If a writer is mid-record at capture time, do not claim the partial row as consumed data; later source growth changes the snapshot and triggers another pass.
5. Under canonical `events.lock` authority, isolate an unterminated canonical tail, obtain canonical identities from a stable/openable snapshot, and append unseen migrated rows. Fsync canonical before advancing the marker.
6. Atomically write the marker with the **pre-scan snapshot actually consumed**. Never replace it with a later post-scan stat: an append that lands after EOF was observed but before a post-scan stat could otherwise be falsely certified as consumed.
7. On any legacy source open/read uncertainty, or canonical identity snapshot uncertainty, do not advance the marker. The current caller contract is fail-soft, so returning 0/no marker advance is acceptable; a later invocation retries.
8. On any snapshot mismatch, the simplest safe implementation may rescan all captured legacy history and rely on canonical identity de-duplication rather than maintain per-file incremental cursors. Migration is rare, correctness is more important than a cursor optimization.

### Candidate 015 regressions

- `test_event_standardization_replays_when_legacy_source_grows_after_marker`: migrate A, append B to legacy, rerun -> B appears exactly once, marker snapshot advances.
- `test_event_standardization_does_not_advance_marker_when_a_source_cannot_open`: one retained generation raises `OSError`; marker is absent/unchanged; restored access lets the next call import it.
- `test_event_standardization_marker_records_prescan_boundary`: inject an append after the captured boundary / after EOF observation but before marker write; first pass may import only the captured rows, second pass must detect the changed snapshot and import the late row.
- `test_event_standardization_v2_marker_is_revalidated_once`: pre-existing v2 marker plus legacy history forces safe idempotent replay and upgrades to v3.
- Integration shape: a bare `AgentCliBackend` working-dir call, a project-context migration, and another bare call demonstrate that the legacy fallback cannot be assumed permanently dead after marker creation.

## Candidate 016 — usage history helper reverses the retained generations that the canonical log defines as chronological

A separate deterministic bug was found in `core/usage.py`.

The canonical event-log contract and its existing regression test define generation chronology as:

`events.jsonl.2` (oldest), `.3`, `.4`, ... , `.1` (most recent completed roll), `events.jsonl` (live).

`life/event_log.py:event_log_paths()` and `life/memory.py:_jsonl_history_paths()` follow that ascending-`N>=2` ordering. `tests/tools/test_event_log_query.py` explicitly asserts `.2 -> .3 -> .1 -> live`.

But `core/usage.py:_event_history_paths()` currently builds older generations with `sorted(older, reverse=True)`, yielding `.3 -> .2 -> .1 -> live` once at least `.2` and `.3` exist. A local source-shaped probe reproduced exactly that mismatch.

This helper is not order-insensitive everywhere:

- `ensure_project_events_standardized()` uses it for the legacy source list, so migrated canonical rows can be emitted out of chronology across retained generations.
- `_legacy_event_records()` is an order-dependent state machine: it carries `current_mission`, records `call_missions` at `agent.io.start`, pairs starts/completes, and clears mission state on completion. If a rollover splits mission lifecycle/call rows across `.2` and `.3`, reverse ordering can attribute call usage to the wrong mission or `None`.
- `_legacy_call_threads()` also iterates the same helper and overwrites a call's thread id as rows are encountered; chronological ordering is the natural last-write-wins contract.

A concrete state-machine example under correct chronology is: `.2` starts mission M1; `.3` contains call C1 and then starts M2; `.1` contains call C2. Correct attribution is C1->M1 and C2->M2. The current `.3,.2,.1` traversal sees C1 before M1 and then resets state to M1 before C2, yielding C1->None and C2->M1.

### Candidate 016 patch boundary

The minimal source correction is `sorted(older)` rather than `sorted(older, reverse=True)` in `core/usage.py:_event_history_paths()`. Do not change the rotation naming convention; the canonical event-log implementation and existing query test already establish it.

### Candidate 016 regressions

- Add a direct `core/usage` generation-order regression asserting `.2,.3,.1,live`.
- Add a legacy usage reconstruction test with mission/call rows crossing `.2/.3/.1`; assert call-to-mission attribution remains chronological.
- Add a migration-order regression with distinct sequence markers in `.2`, `.3`, `.1`, live; canonical migrated order must preserve that sequence.

Because this is deterministic, one-line, and independent of the larger locking redesign, candidate 016 should land before the event-authority refactor so later stable-snapshot helpers inherit the correct ordering.

## Current-head status of prior candidates

- Candidate 014 remains present: canonical `events.jsonl` has three append mechanisms (`JsonlEventSink`, `AgentIOLogger`, migration) without one shared authority. Current `AgentIOLogger._jsonl_append` is still instance-local locking plus plain text append.
- Candidate 012 remains present: current `pyproject.toml` still declares `portalocker>=3`; the prior inspected Windows/raw-fd correctness floor remains `>=4.2`.
- Candidate 013 remains present: `ROUND_REVIEW_STARTED` still exists but is absent from `SIGNAL_EVENT_TYPES` at the current Argus head.
- Candidate 011 remains present: canonical sink append still rotates before a new row without delimiter-isolating a damaged unterminated tail.
- Candidate 009/010 remain present: event-call/planner-verdict readers are still path-enumeration + strict text reads rather than byte-row stable snapshots / tri-state persistence evidence.

## Revised implementation order

1. Candidate 016: fix `core/usage.py` retained-generation order and add crossing-rollover usage/migration tests.
2. Candidate 015: replace existence-only v2 migration semantics with replayable pre-scan-boundary v3 semantics; unreadable source/canonical generations must not advance the certificate.
3. Candidate 014/012/011: introduce shared `core/event_store.py` authority (`EventLogAuthorityError(OSError)`, `event_log_authority`, pre-record delimiter isolation), move sink + AgentIO + migration canonical commit under it, and raise Portalocker floor to the validated cross-platform level.
4. Candidate 013: align default signal durability with Mission View projected event types (`ROUND_REVIEW_STARTED` durable; ordinary `ENGINEER_PROGRESS` live-only unless explicitly chosen otherwise).
5. Candidate 009/010/007: byte-based stable generation snapshots, strict `events.lock -> mission-view.lock`, PlannerVerdict `FOUND/ABSENT/UNKNOWN`, and explicit `iter_call_events` corruption behavior.
6. Keep candidate 008 power-loss durability and candidate 005 provenance separate.

## Exact continuation

Fresh-bootstrap on the next run. Re-read root manifest and open_source config, then start from this checkpoint. First verify whether Argus head has moved and whether candidate 016 has already been fixed upstream; if not, map the minimal `tests/core/test_usage.py` cases for `.2/.3/.1/live` ordering and cross-rollover mission attribution. Then specify the v3 migration snapshot data structure and exact failure return contract, including the source-open-`OSError` no-marker-advance regression. After that return to the shared event-store authority and byte-stable reader frontier above. Frontier remains intentionally non-empty.
