# Open Source Systems Scan — portable event-lock reuse + tri-state persistence evidence

- role: `open_source`
- invocation_started_at: `2026-08-28T10:59:45+09:00`
- frozen note main SHA: `89237fa724851070b8be1fdcf35ce7adc7e20059`
- frozen root control revision: `13`
- frozen role config revision: `6`
- local connector-discovery/write-boundary guard: present and enforced from role config 6; no probe mutation performed in this invocation
- public source: `lbx154/Argus@ae2daa1fbc2c918b4e7126151fe55eb68fd0cb98`
- secondary public source: `wolph/portalocker@c86f80c2505de8e44fb9d2493eb94ab96201fef6`
- independence: own clean state + public sources only; no O/O-derived, other-worker, downstream, legacy, or aggregate-ledger semantics read

## Material update 1 — candidate 010 now has an exact low-churn API boundary

The current public Argus `planner_verdict_was_persisted()` has exactly one production caller outside its own module: `LifeSupervisor._retry_pending_planner_verdict()` in `argus_skill/life/supervisor/_core.py`. The caller treats `False` as permission to call `_emit(event)` again before acknowledging the durable outbox.

That makes the least-churn repair concrete:

1. add a typed helper such as `planner_verdict_persistence_evidence(...) -> FOUND | ABSENT | UNKNOWN`;
2. switch the Supervisor critical path to the typed helper;
3. optionally keep `planner_verdict_was_persisted()` as a compatibility wrapper returning true only for `FOUND`, but do not use the boolean wrapper in retry/re-emission authority.

Supervisor behavior should be:

- `FOUND` -> do not re-emit; proceed to outbox acknowledgement;
- `ABSENT` -> only after a complete stable snapshot may `_emit(event)` run;
- `UNKNOWN` -> keep outbox pending and return retry/awaiting behavior without another canonical planner-verdict append.

The existing regression module `tests/life/test_planner_verdict_outbox_regression.py` is the direct home for this behavior. No other checked production caller was found on the fixed public commit, so the typed critical path does not require a broad call-site migration.

## Material update 2 — corruption must map to UNKNOWN, not only OSError

The present function opens retained event generations as UTF-8 text and catches only `OSError`. A source-shaped local reproduction of the exact loop shows an invalid UTF-8 row raises `UnicodeDecodeError` out of the persistence query rather than returning a result.

A second reproduction shows that a malformed JSON row containing the exact target `delivery_id` is skipped and the function returns `False`. Under the new semantics that row cannot prove absence: it may be the target durable event with damaged syntax.

Therefore `UNKNOWN` should include at least:

- stable-generation snapshot acquisition/open/read failure;
- UTF-8 decode failure in a byte range that cannot be safely excluded;
- a row containing the exact target delivery-id bytes but failing JSON decoding or event-shape verification.

For efficiency and precision the query can scan bytes, prefilter by the ASCII/hex delivery-id bytes, and only decode/parse candidate rows. Malformed unrelated rows that provably do not contain the target id need not make the target-specific query unknown.

Add regressions:

- invalid UTF-8 generation does not crash Supervisor; persistence evidence is `UNKNOWN` when target absence cannot be proven;
- malformed row containing the target delivery id yields `UNKNOWN`, never `ABSENT`;
- malformed unrelated row plus a complete stable scan with no target can still yield `ABSENT` if target bytes are provably absent.

## Material update 3 — Argus already has the cross-platform exclusive lock primitive

The prior continuation proposed adding a Windows-specific `msvcrt` event lock. Current Argus already depends on `portalocker>=3` and has `argus_skill/core/file_lock.py::exclusive_file_lock()`, which performs bounded cross-platform exclusive advisory locking with retry. `tests/core/test_file_lock.py` already exercises contention.

Current portalocker documentation/source clarifies the relevant compatibility:

- POSIX default locking is `fcntl.flock`, so it interoperates with Argus's existing POSIX `flock` event-reader pattern as long as every participant uses the same lock file;
- Windows exclusive locks work through the built-in `msvcrt` path without the optional `pywin32` dependency;
- Windows shared locks in current portalocker require the optional `win32`/`pywin32` extra, which Argus does not declare.

This sharpens candidate 009/010 into a hybrid behind one event-log API rather than a new locking subsystem:

- writer on every platform: reuse a single cross-platform exclusive `events.lock` primitive;
- POSIX correctness-sensitive reader: shared `flock`, enumerate/open generations and capture end offsets under lock, then scan pinned handles outside the lock where allowed;
- Windows correctness-sensitive reader: exclusive event lock for the correctness-first path; do not introduce a shared-lock dependency that silently requires `pywin32`.

One caveat: the existing `exclusive_file_lock()` defaults to a 30-second timeout, while today's POSIX event writer effectively blocks indefinitely on `flock`. Reusing it unchanged could turn prolonged Mission-View/event reconciliation contention into a canonical event write failure. Either add an explicit indefinite-wait mode for event-log authority or keep a dedicated event wrapper with the same portalocker primitive but no finite timeout. Preserve current durability semantics separately; this run does not promote candidate 008.

## Material update 4 — Windows CI can verify candidate 009 directly

Argus's `.github/workflows/tests.yml` already runs `tests/core/test_file_lock.py` and `tests/daemon/test_state_portable.py` on `windows-latest`, but no event-log portable module is in `PORTABLE_TESTS`. The workflow comment itself notes that cross-process locking remains a portability boundary.

A minimal portable regression module can therefore be added to the existing Windows/macOS matrix instead of relying only on Linux monkeypatches:

- two independent event-log participants contend on the same `events.lock` and the second cannot enter append/rotation until the first releases;
- after release, both events are retained exactly once;
- on Windows the test must work with the normal `pip install -e '.[qr]'` dependency set, proving no undeclared `pywin32` requirement.

A separate deterministic unit test can still force the rollover interleaving with independent sink instances so the old Windows no-cross-process-lock implementation fails for the intended reason.

## Material update 5 — stable snapshot also fixes exact call-log queries

`argus_skill/life/event_log.py::iter_call_events()` uses `event_log_paths()` and opens generation pathnames later. `argus_skill/tools/event_log_query.py` maps an empty result to CLI exit code 1 (`no event rows found`). The same pathname-generation TOCTOU can therefore produce a false missing/partial call trace during rollover, independent of the planner-verdict outbox consequence.

The shared stable-generation snapshot primitive should be consumed by both planner persistence evidence and `iter_call_events`; do not leave a second correctness-sensitive generation scanner with the old enumerate-now/open-later behavior.

## Exact implementation/test frontier

1. In `event_log.py`, define one event-lock boundary used by writers and stable readers. Reuse Argus's portalocker-based exclusive primitive on Windows/exclusive paths; preserve POSIX shared `flock` for reader pinning.
2. Add a stable-generation snapshot representation carrying open handle + captured end offset + generation identity. `ABSENT` is legal only after every selected byte range was scanned successfully.
3. In `planner_verdict_outbox.py`, add typed `FOUND/ABSENT/UNKNOWN` evidence; keep any legacy boolean only as a non-authoritative compatibility wrapper.
4. In `_core.py::_retry_pending_planner_verdict`, `UNKNOWN` must short-circuit with the outbox still pending and must not call `_emit(event)` for the planner verdict.
5. Add the UTF-8/malformed-target regressions above to `tests/life/test_planner_verdict_outbox_regression.py`.
6. Add `tests/life/test_event_log_portable.py` (or equivalent) to `PORTABLE_TESTS` so the exclusive writer lock is exercised on real Windows CI without `pywin32`.
7. Move `iter_call_events()` to the same stable snapshot and add rollover-during-query regression.
8. Feed the same stable snapshot/lock ordering into Mission View candidates 006/007; keep candidate 008 power-loss durability separate and candidate 005 `transition_id` provenance-only.

## Scope limits

- Argus public main was rechecked and remains `ae2daa1fbc2c918b4e7126151fe55eb68fd0cb98` for this source scope.
- The Unicode and malformed-target behaviors were reproduced with the exact public function logic in a local minimal simulation, not a full Argus checkout pytest run.
- No production incident is claimed for the planner duplicate path, call-query omission, or Windows rollover race.
- Portalocker shared-lock behavior is not proposed for Windows because current portalocker requires the optional win32 dependency for true shared locks; Argus's declared dependency does not include that extra.
- Power-loss durability remains a separate unproven candidate.

## Nonempty frontier / exact continuation

Start with the typed planner evidence and event-lock abstraction as one coupled patch design: map the exact `_retry_pending_planner_verdict` branches and produce literal regression assertions for `FOUND`, `ABSENT`, and `UNKNOWN`; then map a real-Windows portable event-lock test into the existing `PORTABLE_TESTS` matrix. After that, audit whether `exclusive_file_lock(timeout=30s)` can be safely generalized to an indefinite event-log authority mode without harming its current bounded callers, or whether an event-specific portalocker wrapper is lower risk. Continue stable-snapshot adoption in `iter_call_events` and Mission View, while keeping durability and transition-lineage candidates separate.
