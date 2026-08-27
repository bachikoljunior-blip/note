# open_source clean-g1 run — canonical reader rotation race

Observed invocation start: 2026-08-28T07:01:19+09:00
Checkpoint observation: 2026-08-28T07:12:50.447430+09:00

## Frozen semantic control tuple

This is a continuation inside the same physical invocation as `RUN_20260828_0709_WINDOWS_EVENT_LOCK_AND_SCHEMA7_MIGRATION.md`.

- note main SHA at pre-semantic freeze: `862f4f9087304fdb45ad75f6de47a15eda2cbe2a`
- `DESIRED_STATE` control revision `12`, blob `5c91671e1470d0fa4e2a53f918493004dd3750c3`
- `open_source` config revision `5`, blob `118f440957ba4654e804af902aa09a9224acca43`
- later note-main movement was used only for own-state write/CAS mechanics.
- clean-exploration boundaries remained unchanged.

## Candidate `clean-os-g1-010` — unlocked canonical readers can skip a retained generation during rollover

Candidate 009 showed a Windows **writer/writer** race because `events.lock` is POSIX-only. A separate problem exists even on POSIX: several readers enumerate canonical generation pathnames without taking `events.lock`, while writers rename those pathnames under the lock.

### `iter_call_events()` source path

Current `argus_skill/life/event_log.py`:

1. calls `event_log_paths(log_path)` to obtain a list of generation **pathnames**;
2. later opens those pathnames one-by-one, newest to oldest;
3. does not hold `events.lock` while enumerating or opening them.

A writer can therefore rotate between enumeration and the later `open()` calls.

Deterministic pathname witness:

- initial `.2=A`, `.1=B`, current=`C`;
- reader snapshots `[.2,.1,current]` and reads current C;
- writer, under its valid exclusive lock, moves `.1 B -> .3`, current C -> `.1`, creates new current D;
- reader next opens the **same pathname `.1`**, which now refers to C, so C can be seen twice while B has moved to `.3`, a pathname absent from the reader's frozen list.

For a call whose start row is only in B and later rows are in C, `iter_call_events()` can miss the start generation and return an incomplete call history. This race does not require a broken writer lock; the reader simply never participates in the locking protocol.

### `planner_verdict_was_persisted()` is a correctness-sensitive instance

Current `planner_verdict_was_persisted()` independently scans `sorted(directory.glob("events.jsonl*"))` without `events.lock`.

The Supervisor uses it during durable planner-verdict outbox replay:

- if the delivery ID is found in the canonical event tape, it avoids re-emitting the verdict;
- if the scan returns false, it attempts `_emit(event)` again.

A concurrent rotation can therefore turn a genuinely persisted verdict into a transient **false negative**, causing an unnecessary duplicate verdict append/delivery attempt.

I reproduced this exact pathname race in a local source-shaped simulation:

1. `events.jsonl.1` contained `life.planner.verdict(delivery_id=v1)`;
2. the reader snapshotted `[events.jsonl, events.jsonl.1, events.jsonl.2]` and scanned current first;
3. rollover moved `.1 -> .3` and current -> `.1` before the reader opened its saved `.1` pathname;
4. the reader completed its saved pathname list and returned `found=False` even though the final retained tape still contained the verdict in `.3`.

This is not a full Argus concurrency test and not an observed production incident. It is a deterministic execution of the current pathname-enumeration logic against the current rotation algorithm.

### Same-repository positive control

`daemon/_life_worker_identity.py::_legacy_manager_handoff_identity()` already contains the stronger pattern for a canonical-log reader:

- takes a shared POSIX `events.lock`;
- opens/pins all candidate file handles while the generation names are stable;
- releases the lock;
- reads the pinned handles afterward.

So Argus already recognizes that canonical generation identity must be stabilized across rotation in at least one recovery path.

That helper is POSIX-only (`_fcntl` absent on Windows), so candidate 009's cross-platform lock primitive should become the common foundation.

## Unified adaptation for candidates 006/007/009/010

Rather than create four slightly different locking schemes, expose one dependency-neutral canonical-log snapshot API.

Correctness-first shape:

1. `event_log_locked(life_dir)` — shared blocking cross-platform lock (POSIX flock / Windows msvcrt retry) plus module-level per-path thread serialization.
2. Under that lock, either:
   - scan the required generations completely; or
   - open/pin immutable generation handles plus stable end offsets, then release and parse those handles.
3. Mission View reconciliation must acquire `events.lock -> mission-view.lock`.
4. `iter_call_events()` and `planner_verdict_was_persisted()` must use the same stable-generation snapshot instead of independent pathname globs.
5. On any inability to establish a stable snapshot, fail closed for correctness-sensitive replay decisions rather than report "not found" from an unstable scan.

For `planner_verdict_was_persisted()`, a stable negative answer is important because `False` authorizes an event re-emission attempt.

## Scope

- Candidate 010 applies on POSIX as well as Windows because the affected readers do not acquire the writer's lock at all.
- Candidate 009 remains Windows-specific writer/writer loss; POSIX flock protects writers.
- Candidate 010 is about a reader observing the wrong generation set while the canonical data is still retained; candidate 009 is actual canonical generation loss.
- CLI `event_log_query` catches `OSError`, so one manifestation can be a visible query failure. The planner-verdict persistence check is more correctness-sensitive because a false negative changes replay behavior.

## Additional migration implication

Candidate 007's schema-7 Mission View reconciliation should not merely call `event_log_paths()` and then parse later. The all-generation replay itself must operate over a rotation-stable generation set; otherwise a recovery mechanism can reproduce the same omission it is intended to repair.

## Exact continuation

1. Add literal concurrent-rotation regressions for `iter_call_events()` and `planner_verdict_was_persisted()` using a barrier between generation enumeration and file opening.
2. Compare two implementation shapes: hold the cross-platform event lock for the complete scan versus pin handles/end offsets under the lock and parse after release. Prefer correctness first; measure writer blocking before optimizing.
3. Verify Windows handle/rename semantics before relying on post-lock pinned handles there; if uncertain, keep the lock through scan on Windows.
4. Integrate these tests with candidate 009's two-sink Windows rollover test and use one shared lock/snapshot primitive.
5. Keep schema-7 migration compatibility correction from the preceding checkpoint and require stable-generation replay for every full rebuild.
6. Continue candidate-008 durability ordering separately and re-read public Argus main next invocation.

Frontier remains intentionally non-empty.
