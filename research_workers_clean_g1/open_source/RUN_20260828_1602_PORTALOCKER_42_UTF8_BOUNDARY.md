# Open Source follow-up — Portalocker floor moves to 4.2; crash-tail repair needs byte-safe readers

- role: `open_source`
- observed_at: `2026-08-28T16:02:58+09:00`
- frozen semantic control tuple: note `3ec8df30be44c52bebc80f18dcfb2b8dba4a05df`, control `15`, config `6`
- public Argus source: `ae2daa1fbc2c918b4e7126151fe55eb68fd0cb98`
- public Portalocker develop head observed: `c86f80c2505de8e44fb9d2493eb94ab96201fef6`
- clean scope unchanged: own state + public sources only; no O, other-worker, downstream, legacy, shared-ledger semantics

## Candidate012 revised: first defensible dependency floor is Portalocker 4.2.0, not 3.2/4.0

The prior frontier asked an actual Windows lower-bound cell to decide `>=3.2` versus `>=4.0`. Upstream release evidence changes that decision surface.

Portalocker 4.0.0 explicitly fixed the Windows msvcrt locker taking raw integer descriptors from the descriptor's current offset instead of byte zero; upstream says this could break mutual exclusion when the file is larger than the 64 KiB lock range. Portalocker 4.1.0 explicitly states it changed no runtime behavior. Portalocker 4.2.0 then fixed additional low-level Windows-lock correctness issues: its fallback `LK_*` table had shifted values (including a fallback `LK_LOCK` value that would issue unlock), and `Win32Locker` reused one `OVERLAPPED` object across calls/threads even though the Win32 API forbids that. The current 4.2 source also documents byte-zero normalization for raw `int`/`fileno()` descriptors and per-call lock semantics.

Argus still declares `portalocker>=3`, requires Python `>=3.11`, and its production code directly calls `portalocker.lock(fd, ...)` with raw integer descriptors in multiple core paths (workspace lease, knob store, metrics, cost control, daemon spawn admission). The current Windows portable CI installs the resolver's latest Portalocker rather than testing the declared minimum. That means today's passing Windows CI cannot establish that the advertised `>=3` floor is sound.

Scope guard: this does **not** prove every Argus path fails on Portalocker 3.2/4.0/4.1. Current raw-fd acquisitions inspected here start from freshly opened descriptors at offset zero; workspace lease advances the descriptor only after acquisition, and pre-4.0 unlock has a Win32 fallback. The narrower conclusion is dependency-policy based: if Argus wants its direct raw-fd low-level locking surface to exclude upstream-known Windows correctness defects rather than depend on call-shape luck, `portalocker>=4.2` is the first defensible floor among the inspected releases. Portalocker 4.3 is typing-only at runtime, so there is no additional locking reason found here to require 4.3.

This also simplifies candidate009. With a `>=4.2` floor, the canonical event authority can preserve the existing `os.open(..., 0o600)` raw descriptor and use low-level `LOCK_EX|LOCK_NB`; retry only `AlreadyLocked`, propagate permanent acquire failures, and suppress unlock cleanup failures after a canonical append (closing the fd remains the final release). A separate `os.fdopen()` conversion is no longer needed just to obtain correct Windows raw-fd positioning.

## Candidate011 tightened: newline isolation alone is insufficient for a torn UTF-8 code point

The pre-rotation rule still stands: while holding event authority, inspect the final byte and append exactly one `\n` when a nonempty current generation is not newline-terminated, then run `_maybe_roll()`, then append the new event. This preserves malformed old bytes for forensics and prevents the next valid JSON object from being concatenated into the damaged physical row.

However, a process interruption can leave the old tail in the middle of a UTF-8 multibyte sequence, not only in the middle of JSON syntax. A local source-shaped probe wrote an invalid first physical row ending with byte `0xe2`, followed by a valid newline-delimited Planner verdict. Python's current `open(..., encoding='utf-8')` iterator raised `UnicodeDecodeError` before yielding the later valid row; opening the same file in binary mode produced two independent physical rows and allowed the second to be inspected. This matters because current `iter_call_events()` and `planner_verdict_was_persisted()` use strict UTF-8 text iteration, and the latter catches `OSError` but not `UnicodeDecodeError`.

Therefore candidate011 and candidate010 should meet at one byte-safe stable-generation reader. Snapshot generations under the event authority, read bounded physical rows as bytes, and decode/parse each complete row independently. For correctness-sensitive Planner verdict evidence, any undecodable or target-relevant malformed row must yield `UNKNOWN`, never `ABSENT`; a complete clean snapshot with no match yields `ABSENT`; an exact valid match yields `FOUND`. For exact call queries, corruption should surface explicitly rather than silently report no events. This lets a damaged historical row remain visible as corruption without poisoning every valid row appended after boundary isolation.

## CI / regression shape

1. Windows lower-bound job pins `portalocker==4.2.0`, not 3.2.0, and runs the event-authority regressions plus `tests/core/test_workspace_lease.py` and an independent-process exclusion test. A separate packaging assertion verifies the project metadata no longer advertises `<4.2`.
2. Event-tail regression seeds `events.jsonl` with a complete JSON row missing only newline at/over the roll threshold; after append, the old row must be newline-terminated in `.1` and the new row independently parseable.
3. UTF-8 tear regression seeds a physical row ending mid-codepoint, then appends a valid Planner verdict. The stable byte reader must classify the damaged row explicitly while still reaching the valid verdict; Planner evidence must be `FOUND`, not an exception or false absence.
4. A damaged row containing the target delivery-id bytes but failing UTF-8/JSON must produce `UNKNOWN`, leaving the outbox pending and returning retry without re-emission.

## Exact continuation

Implement/source-map the minimum shared primitive as `event authority + stable generation snapshot`: writer uses Portalocker 4.2+ exclusive authority; POSIX readers may pin generation handles/end offsets under shared `flock`, while Windows correctness-sensitive readers hold the exclusive Portalocker authority through their scan. Make physical-row iteration byte-based so candidate011's delimiter isolation actually preserves subsequent valid events after an invalid UTF-8 tear. Then connect the same primitive to Mission View reconciliation with strict `events.lock -> mission-view.lock`, and only then complete Planner verdict `FOUND/ABSENT/UNKNOWN` plus `iter_call_events` corruption behavior. Keep candidate008 power-loss fsync durability and candidate005 transition provenance separate.

Post-freeze note head drift was observed only through SHA-only ref lookup for write coordination; no newer control or other semantic payload was adopted in this invocation.
