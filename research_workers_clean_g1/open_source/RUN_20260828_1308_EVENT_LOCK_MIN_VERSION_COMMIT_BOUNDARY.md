# Open Source Systems Scan — event-lock minimum-version + commit-boundary refinement

- role: `open_source`
- invocation_started_at: `2026-08-28T13:00:02+09:00`
- checkpoint_observed_at: `2026-08-28T13:08:30+09:00`
- frozen note main SHA: `0dd97c62678923281362091099cbee26402dd4d0`
- frozen root control revision: `13`
- frozen role config revision: `6`
- post-freeze note main SHA observed for write coordination only: `4fd657520f1db4474d77642efb5286129dcfe42a`; not adopted semantically
- public source: `lbx154/Argus@ae2daa1fbc2c918b4e7126151fe55eb68fd0cb98` (rechecked current `main`)
- secondary public source: `wolph/portalocker@v3.0.0` plus current public head `c86f80c2505de8e44fb9d2493eb94ab96201fef6`
- local connector-discovery/write-boundary guard: present and enforced from open_source config 6; no probe mutation performed
- independence: own clean state + public sources only; no O/O-derived, other-worker, downstream, legacy, or aggregate-ledger semantics read

## Material update 1 — the event authority wrapper must pass a real file object, not Argus's current raw integer fd

Argus currently opens `events.lock` with `os.open(...)` and passes the raw descriptor directly to POSIX `fcntl.flock`. Moving that call mechanically to Portalocker would be unsafe across the repository's declared dependency range `portalocker>=3`.

At Portalocker 3.0.0, the Windows low-level `lock()` path casts its argument to a file object, then calls `.tell()`, `.seek()`, and `.fileno()` before `LockFileEx`. A raw integer descriptor therefore is not a portable argument at the declared minimum version. Current Portalocker accepts a broader `FileArgument`, so a Windows CI job resolving only latest Portalocker could hide this lower-bound regression.

The lowest-churn event lock should therefore open `<life_dir>/events.lock` as a real binary file object (`a+b` or equivalent) and give that object to the low-level `portalocker.lock(...)` / `portalocker.unlock(...)` calls.

## Material update 2 — do not use high-level `portalocker.Lock` for canonical event authority

Portalocker's high-level retry semantics changed materially inside Argus's supported `>=3` range:

- Portalocker 3.0.0 `Lock.acquire()` catches every `LockException` and retries it until timeout; `timeout=None` means the normal finite default, not an unbounded wait.
- Current Portalocker retries only `AlreadyLocked` and immediately propagates a non-contention `LockException`.
- Current Portalocker also changed release behavior: release errors are suppressed/logged by default, while the 3.0.0 `Lock.release()` directly unlocks/closes and may propagate.

Therefore using the high-level context manager would make Argus canonical-event failure semantics depend on whichever Portalocker version pip resolved. The stable contract already common to the checked minimum/current low-level API is narrower:

1. call `portalocker.lock(real_file_handle, LOCK_EX | LOCK_NB)`;
2. on `portalocker.exceptions.AlreadyLocked`, sleep and retry;
3. on plain `LockException` or any other backend error, fail immediately;
4. after the protected append/roll section, perform best-effort unlock and always close the file handle.

For the canonical writer, contention alone should wait indefinitely so an ordinary competing writer does not turn a durable append into failure. Permanent failures must not be converted into an infinite retry.

## Material update 3 — release failure is part of the event append commit boundary

Argus's generic `core.file_lock.exclusive_file_lock()` is not quite suitable even after exception classification. It calls `portalocker.unlock(handle)` in `finally` without suppressing release errors.

That matters for `JsonlEventSink._append()`: if the canonical event line has already been appended but unlock then raises, the outer `_append()` exception path can report `False` even though the durable-log side effect already happened. A caller interpreting `False` as “not persisted” can retry and append the same logical event again.

The current POSIX event-log implementation avoids that particular ambiguity by making unlock best-effort before closing the descriptor. The cross-platform replacement should preserve this **commit-aware release** rule: once the canonical append body has succeeded, an unlock failure must not retroactively convert the append into a negative persistence acknowledgement. Cleanup should still close the real file handle so the OS can release any remaining advisory lock.

This is a different policy from state-boundary locks whose caller may legitimately want release errors surfaced. It is another reason to keep the first change event-specific rather than generalize `exclusive_file_lock()` immediately.

## Material update 4 — broad `exclusive_file_lock()` cleanup has observable callers

The generic helper currently catches all Portalocker `LockException` and converts continued failure into `TimeoutError`. A source-exact caller in `daemon/commands.py`, `_execution_lock(blocking=False)`, explicitly catches only `TimeoutError` and converts it to `acquired=False`.

Changing the helper globally so permanent `LockException` escapes would be semantically cleaner, but it would also change that caller from a boolean “busy/unavailable” result to an exception unless the daemon-command path is audited and updated. That raises the blast radius beyond candidate009's event-log correctness goal.

Recommendation: first add a narrowly scoped event-log authority wrapper; treat a generic `exclusive_file_lock()` exception-classification cleanup as a separate compatibility change with its own caller matrix.

## Material update 5 — literal regression matrix for the event wrapper

A small wrapper can be pinned with source-shaped tests before touching the broader reader stack:

1. **contention then success:** monkeypatch low-level lock to raise `AlreadyLocked` N times then succeed; assert only contention is retried and protected body runs exactly once.
2. **permanent Portalocker failure:** plain `LockException` propagates immediately; assert one lock attempt and no retry sleep.
3. **non-Portalocker backend failure:** an unexpected permanent backend exception also propagates immediately; do not misclassify it as contention. This protects lower-version Windows backend differences.
4. **real-handle contract:** the object given to `portalocker.lock` has `.tell()` and `.fileno()` and is not a raw `int`.
5. **post-commit unlock failure:** protected body completes, unlock is forced to fail, wrapper still reports the body success while closing the handle. This prevents “append landed but acknowledgement false” duplicate retries.
6. **portable spawned-process lock:** copy Argus's existing `tests/core/test_daemon_lock.py` `multiprocessing.get_context()` shape: child holds `events.lock`, parent append cannot finish until release, then exactly one event exists.
7. **lower-bound compatibility coverage:** because current portable CI installs `-e '.[qr]'` and therefore resolves a current Portalocker, either add a narrow Windows job/test with `portalocker==3.0.0` or make the common file-object + low-level-API contract an explicit lower-bound regression. Do not rely on latest-Windows CI alone.

The current `tests/core/test_file_lock.py` only covers contention-to-`TimeoutError`; it does not cover permanent `LockException` classification or post-body unlock failure.

## Material update 6 — candidate010 delivery-id byte scan should stay format-agnostic at the helper boundary

The planner outbox helper normally computes a SHA-256 delivery id, but `write_planner_verdict_outbox()` deliberately preserves a caller-provided `event['delivery_id']` if present. The evidence helper therefore should not globally assume every stored id is a 64-byte lowercase hex digest unless the production planner path separately validates that invariant.

A safe byte-oriented evidence implementation can simply encode the requested `delivery_id` as UTF-8 and use those exact bytes as the prefilter. Then:

- a stable snapshot containing a valid matching `life.planner.verdict` => `FOUND`;
- a candidate row containing the target bytes but not decodable/verifiable => `UNKNOWN` unless another valid match proves `FOUND`;
- only a complete stable snapshot with no matching event and no target-relevant ambiguity => `ABSENT`.

This keeps the `FOUND / ABSENT / UNKNOWN` Supervisor contract intact without overclaiming the id format.

## Updated implementation/test frontier

1. Add an event-specific cross-platform exclusive-lock context in `argus_skill/life/event_log.py` (or a tiny event-log-private helper): real file object; low-level Portalocker call; indefinite retry only on `AlreadyLocked`; immediate permanent-error propagation; commit-aware best-effort unlock/close.
2. Add tests 1–5 above, including a permanent-error test that proves no retry loop and a post-commit unlock-failure test that proves a landed append is not reported missing.
3. Add the spawned-process Windows/macOS event-lock integration test and place it in `PORTABLE_TESTS`.
4. Decide lower-bound CI strategy for `portalocker==3.0.0`; current portable CI alone exercises a current resolver result and is insufficient to catch the raw-int incompatibility.
5. Implement `PlannerVerdictPersistenceEvidence` (`FOUND/ABSENT/UNKNOWN`) over the stable-generation primitive and literal Supervisor branches in the existing outbox regression fixture.
6. Move `iter_call_events()` and Mission View recovery to the same stable-generation snapshot primitive; preserve existing call ordering and `events.lock -> mission-view.lock` ordering.
7. Continue candidate008 power-loss durability separately: canonical event append still lacks an explicit fsync ordering guarantee, while Mission View fsyncs its temp file but not the parent directory.
8. Continue candidate005 Manager-intent `transition_id` stage provenance separately.

## Scope limits

- Argus public `main` was rechecked and remained `ae2daa1fbc2c918b4e7126151fe55eb68fd0cb98` for this source scope.
- Portalocker 3.0.0 was inspected specifically because Argus declares `portalocker>=3`; current Portalocker source was checked separately to identify cross-version behavior drift.
- No full Argus checkout pytest was executed here; the tests above are source-shaped implementation maps.
- No production Windows generation-loss, duplicate planner verdict, release-failure duplicate, or filesystem-lock incident is claimed.
- The post-commit unlock rule is specific to canonical event persistence acknowledgement; it is not evidence that every Argus lock should suppress release failures.
- Candidate008 power-loss durability remains separate and unproven.

## Nonempty frontier / exact continuation

First pin the event-specific wrapper API and its five deterministic unit regressions, then map the spawned-process portable test plus an explicit lower-bound Portalocker coverage strategy. Next finish the planner-verdict `FOUND/ABSENT/UNKNOWN` helper without assuming a global SHA-only delivery-id format, and wire the same stable-generation primitive into `iter_call_events()` and Mission View reconciliation. Continue candidate008 durability and candidate005 transition-lineage provenance as separate branches.
