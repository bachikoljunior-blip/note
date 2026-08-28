# Open Source Systems Scan — planner persistence tri-state + event-lock exception classification

- role: `open_source`
- invocation_started_at: `2026-08-28T11:59:32+09:00`
- checkpoint_observed_at: `2026-08-28T12:06:25+09:00`
- frozen note main SHA: `2e9208bdb49867e32367d7c87d6737792bbda22c`
- frozen root control revision: `13`
- frozen role config revision: `6`
- post-freeze note main SHA observed for write coordination only: `49ba40d54e8f44d860a015b3d64ce2d7cebfa42c`; not adopted semantically
- public source: `lbx154/Argus@ae2daa1fbc2c918b4e7126151fe55eb68fd0cb98` (rechecked current `main`)
- secondary public sources: `wolph/portalocker@v3.0.0` and `wolph/portalocker@c86f80c2505de8e44fb9d2493eb94ab96201fef6`
- local connector-discovery/write-boundary guard: present and enforced from role config 6; no probe mutation performed
- independence: own clean state + public sources only; no O/O-derived, other-worker, downstream, legacy, or aggregate-ledger semantics read

## Material update 1 — the Supervisor tri-state branch can be specified exactly

The current `LifeSupervisor._retry_pending_planner_verdict()` has a narrow critical sequence after stale/delivered-record handling:

1. read `delivery_id` from the pending outbox;
2. call boolean `planner_verdict_was_persisted(...)`;
3. if false, re-emit the planner verdict through `_emit(event)`;
4. if emission succeeds (or the verdict was already found), mark the outbox delivered;
5. clear the outbox for non-terminal replay and return the stored outcome.

Because `_pc_intake_gate()` immediately returns the retry outcome whenever `_retry_pending_planner_verdict()` says it handled a record, the least-churn typed contract is now precise:

- `FOUND`: do **not** call `_emit(event)`; acknowledge the outbox and return its stored outcome;
- `ABSENT`: legal only after a complete stable event-log snapshot was scanned; call `_emit(event)` exactly once, then acknowledge and return the stored outcome;
- `UNKNOWN`: do **not** call `_emit(event)` and do **not** acknowledge/clear the outbox; return `(True, PLAN_RETRY)` so Planner is not invoked and the durable outbox remains pending for a later proof.

Literal Supervisor regressions can therefore monkeypatch only the evidence helper, while separate event-log tests exercise evidence construction:

- `FOUND`: pending outbox + evidence `FOUND` => zero planner-verdict re-emits, outbox retired/acknowledged through the existing path, stored outcome returned;
- `ABSENT`: pending outbox + evidence `ABSENT` => exactly one planner-verdict emit, then acknowledgement, stored outcome returned;
- `UNKNOWN`: pending outbox + evidence `UNKNOWN` => zero planner-verdict emits, pending outbox remains `delivered=false`, return `PLAN_RETRY`;
- an `_emit(event)` failure remains the existing `PLAN_RETRY` path and must not acknowledge the outbox.

This belongs in the existing `tests/life/test_planner_verdict_outbox_regression.py`; no broad Supervisor refactor is required.

## Material update 2 — absence proof should be byte-oriented and ambiguity-preserving

`planner_verdict_was_persisted()` currently opens every `events.jsonl*` as UTF-8 text, silently skips `OSError`, skips malformed JSON after a substring match, and finally maps all unresolved cases to `False`.

A typed evidence helper should instead consume the stable-generation snapshot as bytes:

- the planner `delivery_id` is a SHA-256 hex string and Argus canonical JSON is emitted with `ensure_ascii=False`, so source-produced canonical rows containing that id contain its literal ASCII bytes;
- rows that provably do not contain the target id bytes can be skipped without UTF-8 decoding;
- a candidate row containing the target id bytes but failing decode/JSON/event-shape verification makes the result `UNKNOWN`, unless a valid matching verdict is found elsewhere;
- a valid matching `life.planner.verdict` proves `FOUND` immediately;
- `ABSENT` is legal only if every selected byte range was read successfully and no target-relevant ambiguity occurred.

This preserves the prior corruption scope without poisoning a target-specific absence proof because of unrelated malformed rows.

## Material update 3 — do not add an indefinite mode to `exclusive_file_lock()` naively

The current Argus helper catches **all** `portalocker.exceptions.LockException` and retries until its 30-second deadline. Portalocker's own contract is sharper: contention is `AlreadyLocked`, while a plain `LockException` is a permanent lock failure and should abort immediately. This distinction already exists at Argus's declared minimum Portalocker 3.0.0: POSIX `EACCES/EAGAIN` becomes `AlreadyLocked`, while other `OSError`/`EOFError` becomes `LockException`. Current Portalocker 4.x documents the same contract and its bundled Windows/POSIX lockers preserve it.

Therefore simply changing Argus's helper to `timeout_seconds=None` while retaining `except LockException: retry` would create an **infinite loop on permanent errors** such as a stale descriptor, non-contention filesystem failure, or NFS `EOFError`.

Two safe implementation choices remain:

1. **lowest blast radius:** add an event-log-specific exclusive-lock wrapper that retries only `AlreadyLocked` indefinitely for canonical writers and propagates other `LockException` immediately;
2. **broader cleanup:** fix `core.file_lock.exclusive_file_lock()` itself to retry only `AlreadyLocked`, preserve the existing default `30.0s`, and add `timeout_seconds: float | None` where `None` means unbounded contention wait. Existing bounded callers keep their current timeout contract; permanent failures become immediate rather than being masked for up to 30 seconds.

Because `exclusive_file_lock()` has many production call sites, option 1 is the lower-risk candidate until the broader exception-classification change gets its own compatibility tests.

## Material update 4 — reader and writer wait policies should differ

The canonical writer should preserve today's POSIX authority behavior: contention alone must not turn a durable event append into failure, so its event lock should wait indefinitely **only for `AlreadyLocked`**.

Correctness-sensitive readers do not need the same liveness policy:

- planner persistence evidence can use a bounded Windows exclusive lock; lock timeout maps to `UNKNOWN`, never `ABSENT`, so it safely defers re-emission instead of blocking the supervisor forever;
- `event_log_query` can surface a stable-snapshot acquisition failure as its existing query-error path (exit 2), rather than the false "no event rows" exit 1;
- POSIX readers can keep the fast shared-`flock` design: enumerate/open generations and capture each end offset under the shared lock, then scan those pinned byte ranges after releasing it.

This separation avoids weakening canonical writes while giving planner retry a fail-closed escape from long Windows scans.

## Material update 5 — the portable regression should copy Argus's existing spawned-process pattern

`tests/core/test_daemon_lock.py`, already included in `PORTABLE_TESTS`, uses `multiprocessing.get_context()` and a top-level subprocess helper specifically so Windows CI exercises the real `msvcrt` lock from a spawned process. That is a stronger precedent than a same-process thread test for candidate 009.

A minimal `tests/life/test_event_log_portable.py` can mirror that pattern:

1. child process acquires the new event-log exclusive lock and reports `held` through a queue/event;
2. parent starts a `JsonlEventSink.append(...)` on the same life-dir and asserts it cannot complete while the child holds the lock;
3. child releases; parent append completes successfully;
4. verify the emitted event is present exactly once;
5. add the module to the existing macOS/Windows `PORTABLE_TESTS` list, where installation is only `pip install -e '.[qr]'` — this catches accidental dependence on undeclared Windows shared-lock extras.

Keep the deterministic rollover-loss interleaving as a separate Linux-capable unit regression; do not rely on a scheduling race in CI to prove the old Windows behavior fails.

## Material update 6 — `iter_call_events()` can reuse the same error semantics cleanly

`event_log_query.main()` already distinguishes query failure (exit 2) from a completed scan with no matching rows (exit 1). Once `iter_call_events()` uses the stable-generation snapshot, acquisition/read errors can continue to raise `OSError`/`ValueError` and naturally map to exit 2. No new CLI status code is needed.

Its generation traversal semantics should remain unchanged: search newest-to-oldest until the generation containing `agent.io.start`, then yield retained matches oldest-to-newest. The stable snapshot changes only the pathname/rotation consistency, not call-trace semantics.

## Exact implementation/test frontier

1. Add a shared event-log locking/snapshot API in `argus_skill/life/event_log.py`.
   - writer: cross-platform exclusive lock; indefinite retry only on `AlreadyLocked`;
   - POSIX stable reader: shared `flock`, open generations + capture end offsets under lock, scan pinned ranges outside lock;
   - Windows stable reader: correctness-first exclusive lock while scanning, with caller-selectable bounded timeout where `UNKNOWN` is available.
2. Add `PlannerVerdictPersistenceEvidence` (`FOUND/ABSENT/UNKNOWN`) and a byte-oriented evidence helper in `planner_verdict_outbox.py`; keep the old boolean only as non-authoritative compatibility if needed.
3. Change `_retry_pending_planner_verdict()` so only `ABSENT` authorizes a planner-verdict re-emit; `UNKNOWN` keeps the outbox pending and returns `PLAN_RETRY`.
4. Add literal branch tests for `FOUND`, `ABSENT`, `UNKNOWN`, and emit failure in `tests/life/test_planner_verdict_outbox_regression.py`.
5. Add helper-level corruption regressions: target malformed => `UNKNOWN`; unrelated malformed + complete stable scan => `ABSENT`; valid target anywhere => `FOUND`.
6. Add a spawned-process event-lock integration test modeled on `test_daemon_lock.py` and include it in `PORTABLE_TESTS`.
7. Add lock-helper regression that permanent `LockException` is not retried forever/bounded-to-timeout before deciding whether to generalize `exclusive_file_lock()` or keep an event-specific wrapper.
8. Move `iter_call_events()` and Mission View candidates 006/007 to the same stable-generation primitive; preserve existing call-trace order and `events.lock -> mission-view.lock` ordering.
9. Keep candidate 008 power-loss durability and candidate 005 stage `transition_id` provenance separate.

## Scope limits

- Argus public `main` was rechecked and remains `ae2daa1fbc2c918b4e7126151fe55eb68fd0cb98` for this source scope.
- Portalocker 3.0.0 source was checked specifically because Argus declares `portalocker>=3`; the `AlreadyLocked` vs permanent `LockException` distinction is present at that minimum source version.
- No full Argus checkout pytest was run in this environment; the regressions above are source-shaped patch/test maps.
- No production duplicate planner verdict, Windows generation loss, or call-query omission incident is claimed.
- Bounded-reader timeout is proposed only where the caller can represent `UNKNOWN`/query failure; canonical writer authority must not silently downgrade contention to append failure.
- Power-loss durability remains separate and unproven.

## Nonempty frontier / exact continuation

Start with the event-lock wrapper decision under the newly discovered Portalocker exception contract: map a minimal `AlreadyLocked`-only retry implementation and a permanent-`LockException` regression, then write the literal Supervisor `FOUND/ABSENT/UNKNOWN` branch tests against the current outbox fixture. Next, map the spawned-process event-lock test into `PORTABLE_TESTS`, then wire the stable snapshot into `iter_call_events` and Mission View. Continue candidate 008 durability and candidate 005 transition-lineage provenance separately.
