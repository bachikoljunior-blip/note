# open_source clean-g1 run — Windows event-lock race and schema-7 migration refinement

Observed invocation start: 2026-08-28T07:01:19+09:00
Checkpoint observation: 2026-08-28T07:09:53.167665+09:00

## Frozen semantic control tuple

- note main SHA at pre-semantic freeze: `862f4f9087304fdb45ad75f6de47a15eda2cbe2a`
- `automation_control/DESIRED_STATE.json`: control revision `12`, blob `5c91671e1470d0fa4e2a53f918493004dd3750c3`
- `automation_control/roles/open_source.json`: config revision `5`, blob `118f440957ba4654e804af902aa09a9224acca43`
- repeated SHA-only note-main lookup matched before the first role-local/public-source semantic read.
- own sanitized feedback was absent at the frozen SHA.
- later note-main movement was used only for own-state CAS/write mechanics and did not alter this frozen semantic tuple.
- no O/O-derived state, other worker state/config/output, downstream comparator/integrator/index/feed/audit semantics, legacy/pre-independence research, shared aggregate execution ledger, or other-role receipts were read.

## Public source snapshot

Repository: `lbx154/Argus`

Current public `main` was rechecked by SHA-only Git-ref lookup and remains:
`ae2daa1fbc2c918b4e7126151fe55eb68fd0cb98`.

Current source facts re-read at that exact commit:

- `JsonlEventSink` uses a **per-instance** `threading.Lock()` and only takes a cross-process `events.lock` when POSIX `fcntl` is importable. There is no Windows `msvcrt` fallback in `argus_skill/life/event_log.py`.
- event rotation moves existing `.1` to the next free `.N`, then moves current `events.jsonl` to `.1`; exceptions are swallowed.
- many production paths construct fresh/distinct `JsonlEventSink` objects for the same project life-dir, so per-instance locking is not a global serialization boundary.
- the same repository already has working cross-platform advisory-lock patterns: `daemon/state.py::_continuous_config_lock()` uses POSIX `fcntl` or Windows `msvcrt` with retry, and `core/daemon_lock.py` also supports both platforms.
- `event_log_paths()` deliberately retains and enumerates all event generations; the module contract states that no event generation is to be lost.
- Mission View bootstrap still reads only `events.jsonl.1` plus live `events.jsonl`, each through the 8 MiB tail helper; schema remains 6.

## Candidate `clean-os-g1-009` — Windows rollover can lose a canonical generation

### Source-level cause

On POSIX, `fcntl.flock(events.lock, LOCK_EX)` serializes append+rotation across sink instances/processes. On Windows, `fcntl` is absent and the file lock branch is skipped. The only remaining lock is `self._lock`, which is private to one sink instance.

That means two sinks can execute `_maybe_roll()` concurrently against the same life-dir.

### Deterministic interleaving

Starting state:

- `events.jsonl.1 = P`
- current `events.jsonl = C`, above the rollover threshold

Two distinct sinks A and B execute the current rollover algorithm without a shared file lock:

1. A sees `.1`, moves `P: .1 -> .2`, then pauses.
2. B now sees no `.1`, moves `C: current -> .1`, writes event B to new current.
3. A resumes and moves the **new current containing B** to `.1`, replacing the `.1` that contained C.
4. A writes event A to a new current.

Final retained event IDs are `P, B, A`; canonical generation `C` has disappeared.

I reproduced this interleaving twice in a local source-shaped simulation, including a second run with a 1 MiB current file matching the source's minimum configured rollover threshold. The full-threshold result was exactly:

```text
['P', 'B', 'A']
```

`C` was absent. This is **not** a full Argus-on-Windows test and not an observed production incident. It is a deterministic execution of the current rotation algorithm under the locking semantics the source uses when `fcntl` is unavailable.

### Scope

- The race is specifically a Windows/current-path finding. POSIX `fcntl` serialization closes this interleaving.
- It affects the canonical log itself, so it is more fundamental than the Mission View read-model gaps in candidates 006/007.
- It violates the module's own stated invariant that every generation is retained and the full lifetime history is the union of `events.jsonl*`.

### Minimal adaptation

Factor one shared blocking `event_log_locked(life_dir)` primitive that is used by **all** append/rotation/reconciliation paths:

1. module-level per-lock-path thread lock, not a sink-instance lock;
2. POSIX: blocking `fcntl.flock`;
3. Windows: `msvcrt.locking` with lock-byte initialization and retry, following the existing `_continuous_config_lock()` pattern;
4. append, rollover and Mission View all-generation reconciliation all take this same lock;
5. preserve the established order `events.lock -> mission-view.lock`.

This simultaneously closes the Windows canonical-log race and supplies the cross-platform stable-history boundary needed by candidates 006/007.

Source-shaped regressions:

- two distinct sink instances racing at rollover must retain `{P,C,A,B}` exactly once;
- a Windows/fake-msvcrt regression must prove one sink blocks while the other owns `events.lock`;
- rollover + Mission View reconciliation must preserve lock order `events.lock -> mission-view.lock` with no inversion.

## Candidate `clean-os-g1-007` — schema-7 migration needs a compatibility correction

The preceding role-local run proposed: schema `<=6` has no trustworthy cursor, therefore force one all-generation rebuild.

Current public history makes that too broad.

### What is now known

- The **initial public release**, commit `f5152425886daf8a2fe78523acdac1b1b2976476` from 2026-08-05, already retained every event generation `.2`, `.3`, ... in `event_log.py`.
- The initial public Mission View bootstrap already read only `.1 + live`, so candidate 006 is present from the initial public release rather than a later regression.
- However that same initial public Mission View code already supported schema 1. Therefore a schema-1 state may predate the public-release event-log retention contract; complete canonical history for every legacy state is not proven.
- Current tests intentionally preserve a schema-4 Mission View even when there is no event log: `test_v4_snapshot_migrates_without_discarding_projected_state`. A blanket destructive rebuild of all schema<=6 state would regress that compatibility behavior.

### Revised migration rule

Do **not** claim that every schema<=6 state can safely be rebuilt from complete canonical history.

Candidate migration options to test:

1. If canonical completeness is demonstrable, rebuild all retained generations and establish the sink-owned `event_log_id` cursor.
2. Otherwise preserve the existing compatible Mission View as a **legacy baseline**, establish a durable post-migration barrier/cursor under the shared event lock, and mark historical completeness as unverified.
3. Never merge a partial replay into old non-idempotent counters by guessing; `round.review.completed` makes additive merge unsafe.
4. Keep the existing v4-preservation test as a required migration regression.

This weaker migration guarantees future contiguous-prefix consistency without pretending that pre-migration holes can always be reconstructed.

## Candidate `clean-os-g1-007` — event identity remains low-churn

`normalize_event_envelope()` preserves unknown top-level fields and does not reject them merely for being unknown. Therefore a distinct sink-owned `event_log_id` remains a low-schema-churn mechanism.

The preparation boundary should still normalize/redact exactly once and overwrite caller-provided `event_log_id`, because current `handle_event()` normalizes before calling `_append()`, while `_append()` normalizes again, and direct `.append()` enters `_append()` directly.

## Deeper cursor locator probe

A new local synthetic benchmark used 128 generations, 1,000 rows each (128,000 rows; about 37.23 MiB in this run). This is **not** production filesystem performance.

Median over 20 recent-first raw-byte exact-ID searches:

- newest generation, last row: ~0.065 ms
- newest generation, first row: ~0.015 ms
- middle generation, last row: ~4.55 ms
- oldest generation, first row: ~8.45 ms
- oldest generation, last row: ~8.37 ms
- missing ID: ~8.22 ms

Full all-generation JSON parse median over 5 runs was ~185.72 ms for all 128,000 rows.

This continues to support raw-byte location only as an optimization. Exact JSON validation and authoritative full replay on miss remain required.

## Candidate `clean-os-g1-008` — durability scope unchanged

The current canonical event append still has no explicit file fsync, rotation has no observed directory fsync, and Mission View write has file fsync before replace but no parent-directory fsync. The stronger `continuous.json` primitive in the same repository remains a suitable implementation precedent.

No power-loss or hardware/filesystem failure was reproduced here. Keep candidate 008 separate from the Windows concurrency loss above.

## Exact continuation

1. Turn candidate 009 into literal Argus regressions: two independent sinks at rollover plus a fake-Windows/msvcrt blocking-lock test. Reuse the repository's existing Windows continuous-lock test style where possible.
2. Design the shared `event_log_locked()` API so append/rotation and Mission View all-generation replay share one cross-platform lock without creating an import cycle or violating `events.lock -> mission-view.lock`.
3. Revise the schema-7 migration tests around the existing v4-preservation contract: complete-history rebuild when provable; otherwise preserved legacy baseline plus post-migration barrier/cursor.
4. Retain Variant A/B Mission View projection tests from the preceding run, including readback after post-replace EIO.
5. Continue candidate-008 fault-injection design separately for power-loss ordering.
6. Re-read current Argus public main next invocation before carrying source claims forward.
7. Keep the frontier non-empty after these tests: inspect whether any other canonical-log consumers assume POSIX-only locking or only `.1+live`, and continue optional Manager `transition_id` provenance separately.

Frontier remains intentionally non-empty.
