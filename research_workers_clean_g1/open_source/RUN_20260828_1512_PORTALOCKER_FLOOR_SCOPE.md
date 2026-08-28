# Open Source follow-up — Portalocker floor scope narrowed

- role: `open_source`
- observed_at: `2026-08-28T15:12:36+09:00`
- frozen control tuple remains note `a407c86e0039226a0eef0082fec10c3603befa9f`, control `14`, config `6`
- public Argus source remains `ae2daa1fbc2c918b4e7126151fe55eb68fd0cb98`
- clean scope unchanged

## Follow-up to the 15:09 checkpoint

Repository-wide code search found no Portalocker shared-lock use (`portalocker.LOCK_SH`); the only `LOCK_SH` hit is the POSIX `fcntl`-based legacy event reader. Current direct Portalocker lock sites use exclusive locking. This removes one reason to preserve Portalocker 3.0/3.1 Win32 `LockFileEx` shared semantics.

However, `>=3.2` should still be treated as a **candidate floor requiring a real Windows lower-bound regression**, not yet a proven semantic floor. `core/workspace_lease.py` is an especially useful canary: it acquires a raw-fd exclusive lock, then writes owner JSON through that same fd (advancing its file position), and later calls `portalocker.unlock(fd)` on the still-open descriptor. Portalocker 3.2 accepts raw integer fds, but its Windows `_prepare_windows_file(int)` does not normalize their position before the msvcrt operation. Portalocker 4.0+ does normalize raw fds to byte 0, and the 4.0 migration notes explicitly call out the pre-4.0 raw-fd current-position behavior as a correctness bug for byte-range locking.

Portalocker 3.2's unlock path has an EACCES fallback through its Win32 locker, so source inspection alone does not prove Argus's workspace lease fails there. The correct decision procedure is therefore:

- `portalocker>=3.2` is the **source-verified API floor** for raw integer fd support checked here;
- pin `portalocker==3.2.0` on an actual Windows runner and exercise `workspace_lease` acquire -> owner write -> release -> reacquire, plus cross-process exclusion and the new event authority;
- if that lower-bound regression is clean, `>=3.2` is defensible;
- if not, use `portalocker>=4.0`, whose raw-fd position normalization is explicit and whose exclusive Windows path no longer needs pywin32.

Argus already requires Python >=3.11, while Portalocker 4.0 requires only Python >=3.10, so choosing a 4.x floor would not create a Python-version compatibility cost.

The existing macOS/Windows portable CI does not include `tests/core/test_workspace_lease.py`; it installs the current resolver and therefore cannot answer this floor question. The lower-bound cell should explicitly include that test module rather than testing the event writer in isolation.

## Candidate011 ordering remains revised

The pre-rotation delimiter conclusion from the 15:09 checkpoint stands. `iter_call_events()` requires newline-terminated physical rows, so a complete JSON tail missing only `\n` must be boundary-isolated before `_maybe_roll()` can move it into `.1`. This also gives the lower-bound Windows event-authority test one precise crash-recovery assertion: old complete no-newline row survives rotation and the new row remains independently parseable.

## Exact continuation

First run/source-map one Windows lower-bound compatibility cell around Portalocker 3.2 semantics, with `workspace_lease` as the raw-fd position canary and event authority as the target path; this decides `>=3.2` versus `>=4.0` rather than guessing from API shape. Then finish event authority + pre-rotation candidate011 regressions. Next cross-platformize Mission View with strict `events.lock -> mission-view.lock`, then finish PlannerVerdict `FOUND/ABSENT/UNKNOWN` and stable-generation readers. Durability and stage-transition provenance remain separate branches.
