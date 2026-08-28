# Open Source Systems Scan — Portalocker lower-bound correction + event-tail ordering

- role: `open_source`
- invocation_started_at: `2026-08-28T15:02:43+09:00`
- checkpoint_observed_at: `2026-08-28T15:09:38+09:00`
- frozen note main SHA: `a407c86e0039226a0eef0082fec10c3603befa9f`
- frozen root control revision: `14`
- frozen role config revision: `6`
- post-freeze note main SHA observed for write coordination only: `a27006202dec52ff469f034ff47af7492c63ce29`; not adopted semantically
- public source: `lbx154/Argus@ae2daa1fbc2c918b4e7126151fe55eb68fd0cb98` (rechecked current `main`)
- secondary public source: `wolph/portalocker` tags `v3.0.0`, `v3.1.1`, `v3.2.0`, `v4.0.0`, `v4.3.0`
- independence: own clean state + public sources only; no O/O-derived, other-worker, downstream, legacy, or aggregate-ledger semantics read

## Material update 1 — the declared `portalocker>=3` floor is already incompatible with existing Argus Windows raw-fd call sites

The previous candidate009 plan tried to keep event-log locking compatible with Portalocker 3.0.0 by wrapping Argus's explicitly-0600 `events.lock` descriptor in a real file object. That is locally possible for the event writer, but it would not make the *declared Argus dependency range* true.

Argus currently declares `portalocker>=3` and Python `>=3.11`. Existing production code already passes raw integer descriptors to the module-level `portalocker.lock()` / `unlock()` APIs. Concrete examples include `core/knob_store.py` and `core/cost_control.py`: both create their lock sidecars with `os.open(..., 0o600)` and pass the returned integer fd directly to Portalocker.

Portalocker `v3.0.0` and `v3.1.1` do not actually support that Windows call shape. Their Windows `lock()` casts the supplied object to an IO object, then immediately calls `.tell()`, `.seek()`, and `.fileno()`. Passing Argus's integer fd therefore fails before the OS lock is acquired. Portalocker `v3.2.0` changes the Windows backend shape: `_prepare_windows_file()` explicitly accepts `int`, and the default Windows exclusive path is the `MsvcrtLocker` path. Current 4.x continues to support raw descriptors.

This yields a packaging-level correction: **adding a `portalocker==3.0.0` Windows compatibility cell only for the new event wrapper would be misleading, because that allowed version is already incompatible with other current Argus production lock paths.**

The lower-churn choices are:

1. raise the Argus dependency floor to at least `portalocker>=3.2` and add an explicit Windows `portalocker==3.2.0` lower-bound CI cell; or
2. if supporting 3.0/3.1 is genuinely required, refactor *all* raw-fd Portalocker call sites to real file objects and regression-test that full compatibility surface.

Given the checked public sources, option 1 is substantially smaller. It also lets candidate009 preserve the current event-lock implementation's explicit `0600` creation and raw-fd lifecycle instead of converting it to `os.fdopen()` solely for obsolete lower-bound compatibility. Argus already requires Python 3.11, so a `>=3.2` Portalocker floor does not impose a new Python-version constraint.

I am not claiming every Portalocker 3.x patch was exhaustively tested. The source-exact boundary checked here is: `v3.1.1` still has the incompatible IO-only Windows implementation; `v3.2.0` has explicit raw-int descriptor handling. The appropriate CI contract is therefore the *declared floor actually chosen by Argus*, not an arbitrary oldest major-version tag.

## Material update 2 — Portalocker 3.0/3.1 also make the old event-only compatibility plan structurally fragile under concurrency

There is a second reason not to optimize candidate009 around Portalocker 3.0/3.1. Those Windows implementations use one cached `OVERLAPPED` structure for LockFileEx operations (`v3.0.0` module-global; `v3.1.1` likewise). Current Portalocker's Win32 implementation explicitly creates a fresh `OVERLAPPED` per call and documents that sharing one between concurrent calls is invalid.

Argus does not have one process-global `JsonlEventSink`: production code constructs many sinks, and Manager front-door event emission creates a fresh `JsonlEventSink(...).append(event)` per emission. Per-instance `threading.Lock()` therefore does not serialize all low-level lock calls made by a process.

No Windows crash was reproduced in this run, so this remains a lower-bound concurrency hazard inferred from the two public implementations, not an observed Argus incident. The raw-fd incompatibility above is independently concrete and sufficient to justify correcting the declared dependency floor.

## Material update 3 — candidate011 delimiter repair belongs *before* rotation, not after it

The previous checkpoint placed the unterminated-tail delimiter repair after `_maybe_roll()`. Source review plus a deterministic local model shows the stronger ordering is:

**event authority -> isolate current record boundary -> maybe rotate -> append new JSON row -> project Mission View**.

Why the order matters: current `_maybe_roll()` can move `events.jsonl` to `.1` before the new append. If the old current file contains a complete JSON object but lacks its final newline, moving it first permanently leaves `.1` unterminated. `iter_call_events()` explicitly skips physical rows that do not end in `\n`, so that otherwise-valid old event becomes invisible to exact call reconstruction. If the old tail is partial/malformed, moving it first likewise preserves an ambiguous unterminated generation boundary.

The repair should therefore run under event authority *before* the size/roll decision:

- if current does not exist or is empty: no-op;
- inspect the final byte only, without decoding;
- if it is already `\n`: no-op;
- otherwise append exactly one `\n` delimiter;
- then run the ordinary `_maybe_roll()` and append the new event.

This is idempotent. A crash after the delimiter but before the new event leaves a clean physical boundary; the next append does not add another delimiter. It preserves malformed bytes for forensics instead of truncating them. A complete JSON record missing only its newline becomes recoverable by readers that require newline-terminated rows. Adding one byte can also push a file over the soft roll threshold; rotating it then is the desired result because the rolled generation now ends on a physical record boundary.

A local source-shaped comparison at the roll threshold confirmed the difference: current ordering moved `{"type":"old","x":1}` to `.1` without a newline, while pre-rotation isolation moved the same bytes as `{"type":"old","x":1}\n`; the new event was written to fresh current in both cases. This is not a production crash/power-loss reproduction.

## Updated regression matrix

1. Windows lower-bound install: pin the chosen declared floor (`portalocker==3.2.0` if the floor is raised to `>=3.2`) and exercise existing raw-fd lock paths plus the new event authority.
2. Windows spawned-process event authority: two independent processes targeting one life-dir serialize append/rotation and retain both events exactly once.
3. Permanent acquire error is not retried as contention; `AlreadyLocked` alone is retried.
4. Successful canonical append remains successful if unlock cleanup later fails; do not create duplicate-delivery pressure from post-commit cleanup ambiguity.
5. Complete JSON tail without newline below threshold: delimiter is inserted once and old + new rows are both independently readable.
6. Complete JSON tail without newline at/over threshold: delimiter is inserted before roll; `.1` ends with newline and the new current row is valid.
7. Partial or invalid-byte tail: preserve damaged bytes, terminate the physical line bytewise, and keep the next valid event independently parseable.
8. Already newline-terminated file: byte-for-byte ordinary append semantics, no blank line.
9. `iter_call_events` regression: a valid old call event lacking only the newline must survive the next writer append/rotation rather than becoming permanently skipped.

## Updated implementation frontier

1. Correct dependency metadata first: either raise the Portalocker floor to the source-verified raw-fd-compatible `>=3.2` and test that floor on Windows, or explicitly decide to pay the larger compatibility cost of rewriting all raw-fd callers for 3.0/3.1. Do not add a misleading event-only `3.0.0` compatibility test.
2. Implement the event-specific authority wrapper using the corrected supported Portalocker range, preserving `events.lock` mode `0600`; retry only `AlreadyLocked`, propagate permanent acquire failures, and keep post-commit unlock best-effort.
3. Under that authority, perform candidate011 bytewise boundary isolation **before** `_maybe_roll()`, then add the regressions above.
4. Cross-platformize Mission View authority and enforce `events.lock -> mission-view.lock` for cold bootstrap/reconciliation and writer projection without nested event-lock acquisition. The Windows stale-bootstrap overwrite regression remains open.
5. Finish `PlannerVerdictPersistenceEvidence` (`FOUND/ABSENT/UNKNOWN`) over a stable-generation snapshot. `ABSENT` alone may authorize re-emission; `UNKNOWN` must keep the outbox pending.
6. Move `iter_call_events()` and Mission View reconciliation to the same stable-generation primitive. POSIX can later optimize reader blocking with pinned handles/end offsets; Windows can start correctness-first under exclusive event authority.
7. Continue candidate008 power-loss durability separately; no power-loss guarantee is claimed here.
8. Continue candidate005 Manager-intent `transition_id` provenance separately.

## Scope limits

- Argus public `main` remained `ae2daa1fbc2c918b4e7126151fe55eb68fd0cb98` during this semantic run.
- Portalocker tags were source-inspected; no Windows Portalocker 3.x process was executed in this environment.
- The raw-fd incompatibility claim is source-exact for the checked Argus call sites plus Portalocker `v3.0.0`/`v3.1.1`; the concurrency note about reused `OVERLAPPED` is intentionally weaker and not presented as a reproduced incident.
- Candidate011 remains process-crash/record-boundary containment, not power-loss durability.
- The prior prohibited connector-discovery branch incident was not repeated; this invocation used discovery read-only and mutated only the authorized `open_source` state/receipt destinations.

## Nonempty frontier / exact continuation

First finish the Portalocker floor decision by checking the remaining direct Argus Portalocker call sites for any 3.0/3.1-specific behavior or shared-lock requirement; if none, make `>=3.2` the candidate floor and map one explicit Windows floor CI cell. Then source-map the event authority API around raw fd + 0600 semantics and candidate011's pre-rotation delimiter isolation. Next refactor Mission View cold bootstrap/projection to the single `events.lock -> mission-view.lock` order and write the deterministic stale-bootstrap regression. After that finish PlannerVerdict `FOUND/ABSENT/UNKNOWN` and stable-generation readers. Keep candidate008 durability and candidate005 transition provenance separate.
