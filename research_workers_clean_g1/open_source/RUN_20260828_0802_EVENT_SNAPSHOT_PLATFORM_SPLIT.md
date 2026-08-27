# open_source clean-g1 run — stable event snapshot platform split

Observed invocation start: 2026-08-28T07:58:15+09:00
Checkpoint observation: 2026-08-28T08:02:04.353224+09:00

## Frozen semantic control tuple

- note main SHA at pre-semantic freeze: `3dff64912d405392d25f0ca51ed3bcb9275c51d1`
- `DESIRED_STATE` control revision `12`, blob `5c91671e1470d0fa4e2a53f918493004dd3750c3`
- `open_source` config revision `5`, blob `118f440957ba4654e804af902aa09a9224acca43`
- first semantic read was own role-local `LATEST.json`; later note-main movement was used only for own-state CAS/write mechanics.
- clean-exploration boundaries remained unchanged.

## Public source freshness

`lbx154/Argus` public `main` is still `ae2daa1fbc2c918b4e7126151fe55eb68fd0cb98`, unchanged from the preceding role-local checkpoint.

Relevant source at that commit:

- `argus_skill/life/event_log.py`
- `argus_skill/life/planner_verdict_outbox.py`
- `argus_skill/daemon/_life_worker_identity.py`
- `argus_skill/core/daemon_lock.py`
- `tests/daemon/test_state_portable.py`

External platform semantics used only for the platform-specific implementation choice:

- CPython issue #88221 / tracker issue 15244: builtin `open()` on Windows does not share delete access; a normal open handle therefore cannot be assumed rename-friendly.
- Microsoft `CreateFileW`: `FILE_SHARE_DELETE` is the sharing mode that permits later delete/rename access.
- Microsoft CRT `_locking`: `_LK_RLCK` is documented as the same operation as `_LK_LOCK`, so the CRT byte-range primitive does not provide a true concurrent shared-reader mode.

## Candidate `clean-os-g1-010` refinement — stable generation snapshots need a platform split

The previous checkpoint established that `iter_call_events()` and `planner_verdict_was_persisted()` snapshot **pathnames** and later open those names without participating in `events.lock`. A legal concurrent rollover can therefore move a retained generation outside the saved pathname set.

This run tested the two proposed repair shapes.

### POSIX: pinned handles + stable end offsets are materially better than lock-through-scan

A source-shaped local POSIX witness used `.2=A`, `.1=B`, current=`C`.

Unsafe saved-path reopen after rollover:

1. reader snapshots `.2,.1,current` and reads current C;
2. writer moves `.1 B -> .3`, current C -> `.1`, creates current D;
3. saved `.1` now reopens C and saved current reopens D;
4. B is omitted even though it is retained in `.3`.

Pinned-handle variant:

1. under a shared `flock`, open `.2`, `.1`, and current;
2. record each handle's `fstat().st_size`;
3. release the shared lock;
4. writer performs the same renames;
5. the pinned handles still read A, B, C from their original inodes.

The **end offset is required**, not optional. If the writer merely appends to current without rolling, an unbounded pinned handle sees the newly appended rows. Reading only up to the offset captured under the lock gives a true point-in-time generation snapshot.

### Local POSIX blocking measurement

Synthetic 64 MiB JSONL scan, 3 repetitions, local cached filesystem only:

- shared lock held through JSON scan: scan median about `0.409 s`; waiting writer's exclusive-lock delay median about `0.395 s`.
- pin handle/end offset under shared lock and release before scan: scan median about `0.397 s`; writer lock delay median about `7.6 us`.

This is not Argus production performance, but it demonstrates that the POSIX pin-and-release optimization removes essentially the whole parse duration from the writer critical section under this workload.

### Windows: do **not** copy the POSIX pin-and-release implementation with builtin `open()`

Python's normal Windows file opens do not share delete access. `os.replace()`/rename needs compatible delete sharing from existing handles. Therefore a reader that pins ordinary Python file handles and then releases `events.lock` can make the writer's rollover rename fail while those handles remain open.

That interacts badly with current Argus behavior: `_maybe_roll()` catches all rollover exceptions and returns, after which `_append()` proceeds to append to the existing current file. A long pinned reader can therefore silently defer/suppress rollover and let the current file exceed the nominal cap for the duration of the scan.

The obvious `msvcrt.LK_RLCK` escape hatch is not a shared-reader solution: Microsoft documents `_LK_RLCK` as the same operation as `_LK_LOCK`. Argus's existing Windows lock patterns consequently provide a sound **exclusive** cross-process mutex, not a POSIX-style reader/writer lock.

### Recommended platform-specific primitive

Use one public conceptual API, but different initial implementations:

1. **POSIX stable snapshot**
   - module-level per-lock-path thread serialization;
   - shared `flock(events.lock)`;
   - enumerate canonical generations while locked;
   - open every selected generation and capture its end offset while locked;
   - release the shared lock;
   - parse only bytes `[0,end_offset)` from the pinned handles;
   - close handles after scan.

2. **Windows stable snapshot (correctness-first)**
   - module-level per-lock-path thread serialization;
   - blocking `msvcrt.locking` on a dedicated byte of `events.lock` using the retry pattern already exercised by Argus `daemon.state` tests;
   - keep that exclusive lock across enumeration **and the complete correctness-sensitive scan**;
   - release only after the scan; do not rely on normal Python handles surviving post-lock rollover.

3. A future Windows optimization may use a Win32 `CreateFileW` opener with `FILE_SHARE_DELETE` plus a real shared/exclusive cross-process locking primitive, but that is materially more complex and is not required for the first correctness patch.

## API-level fail-closed behavior

### `planner_verdict_was_persisted()`

Its current boolean `False` is an authorization to retry `_emit(event)` from the durable outbox. A failure to establish a stable generation snapshot must therefore **not** be collapsed to `False`.

Minimum safe contract:

- `True`: stable snapshot positively found the delivery ID;
- `False`: stable snapshot completed successfully and proved the ID absent;
- `unknown/error`: leave the outbox pending and retry later; do not re-emit solely from an unstable/failed scan.

This can be represented as a tri-state return or an explicit snapshot exception caught by the Supervisor. The current caller should not acknowledge the outbox on the unknown path.

### `iter_call_events()`

If a stable generation snapshot cannot be acquired, fail the query rather than return a partial call history. Its CLI caller already has an error surface; incomplete data is worse than an explicit retryable failure.

## Literal regression matrix

1. `iter_call_events` concurrent rotation barrier:
   - arrange `.2=A`, `.1=B(start row)`, current=C(later row);
   - block after generation enumeration;
   - roll `.1->.3`, current->.1, create D;
   - patched result must include B then C exactly once.

2. `planner_verdict_was_persisted` concurrent rotation barrier:
   - verdict exists only in `.1`;
   - rotate after pathname discovery;
   - stable scan must still return `True`.

3. POSIX pinned-current append boundary:
   - capture current end offset under shared lock;
   - release, append a later row without rollover;
   - snapshot parser must stop at captured offset.

4. POSIX pinned-handle rollover:
   - pin `.1/current`, release lock, rotate;
   - old handles must yield old generation bytes and writer must not block for parse duration.

5. Windows correctness-first reader/writer serialization:
   - use the existing fake-`msvcrt` portable-test pattern to assert reader lock excludes writer through the scan and retry polling is honored.

6. Windows real-CI rollover test:
   - correctness-first reader holds event lock while scanning;
   - writer waits;
   - after reader releases, rollover succeeds and no generation is lost.
   - explicitly avoid a test that assumes builtin-open pinned handles are rename-compatible.

7. planner-verdict unknown path:
   - force snapshot-lock/open failure;
   - outbox remains pending;
   - `_emit(event)` is not called;
   - a later successful stable scan can decide found/absent.

## Candidate relationships

- `clean-os-g1-009`: Windows writer/writer rollover loss because current `event_log.py` has only per-instance thread locks and POSIX `fcntl`; fix with the same shared cross-platform event-lock foundation.
- `clean-os-g1-010`: reader/rotation omission on all platforms; use the stable snapshot API above.
- `clean-os-g1-006/007`: Mission View full rebuild/reconciliation must consume the same stable generation snapshot; otherwise recovery can inherit candidate 010's omission race.
- `clean-os-g1-008`: power-loss durability ordering remains separate and unproven; this run did not generalize the locking result into a power-loss claim.

## Scope and uncertainty

- POSIX handle/rename behavior and the blocking measurements were reproduced locally, source-shaped, not in an Argus checkout.
- Windows handle semantics are grounded in CPython/Microsoft documentation and current Argus source, not a full Argus-on-Windows execution in this environment.
- The recommendation intentionally chooses a more blocking Windows first patch because correctness can be tested with Argus's existing `msvcrt` lock pattern; performance optimization is a later concern.
- No production incident is claimed.

## Exact continuation

1. Map candidate 009's two-independent-sink writer regression and candidate 010's two reader regressions onto the smallest existing Argus test files; identify the exact module-level lock helper signature that can serve both.
2. Inspect `planner_verdict_was_persisted()` caller control flow and pin the minimal tri-state/exception behavior so snapshot uncertainty leaves the outbox pending without duplicate emit.
3. Add a source-shaped Windows test design for normal-open handle + rollover to demonstrate why pin-and-release is not portable; if public Windows CI already exercises rename/share semantics, reuse it rather than inventing a custom Win32 opener.
4. Feed the same stable snapshot API into Mission View schema-7 full rebuild while retaining the legacy-baseline migration rule when complete canonical history cannot be proven.
5. Continue candidate-008 durability ordering separately.
6. Re-read public Argus main next invocation.

Frontier remains intentionally non-empty.
