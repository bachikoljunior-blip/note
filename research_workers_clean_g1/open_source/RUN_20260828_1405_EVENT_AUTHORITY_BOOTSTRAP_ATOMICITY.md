# Open Source Systems Scan — event authority + Mission View bootstrap atomicity refinement

- role: `open_source`
- invocation_started_at: `2026-08-28T13:59:22+09:00`
- checkpoint_observed_at: `2026-08-28T14:04:45+09:00`
- frozen note main SHA: `ced3c20fcf614bae9e36535a40560a55d496222b`
- frozen root control revision: `13`
- frozen role config revision: `6`
- post-freeze note main SHA observed for write coordination only: `afc22197727fa16561a61bed4655f77933fdc7f7`; not adopted semantically
- public source: `lbx154/Argus@ae2daa1fbc2c918b4e7126151fe55eb68fd0cb98` (rechecked current `main`)
- secondary public source: `wolph/portalocker@v3.0.0`, current public head `c86f80c2505de8e44fb9d2493eb94ab96201fef6`, current release `v4.3.0`
- local connector-discovery/write-boundary guard: present and enforced from open_source config 6; no probe mutation performed
- independence: own clean state + public sources only; no O/O-derived, other-worker, downstream, legacy, or aggregate-ledger semantics read

## Material update 1 — preserve the existing 0600 sidecar mode while switching to a real lock object

The previous candidate009 refinement correctly requires a real file object for the event authority lock because Portalocker 3.0.0's Windows path calls `tell()`, `seek()`, and `fileno()` on the supplied object. A small implementation detail is load-bearing: replacing Argus's current `os.open(..., 0o600)` with a plain `Path.open("a+b")` would create a new `events.lock` using normal open/umask permissions rather than the existing explicit `0600` creation mode.

The lower-churn compatible shape is therefore:

1. `os.open(events.lock, O_CREAT | O_RDWR | O_BINARY-if-present, 0o600)`;
2. wrap that descriptor with `os.fdopen(..., "r+b")` so Portalocker 3.0.0 receives a real seekable file object;
3. use low-level `portalocker.lock(handle, LOCK_EX | LOCK_NB)`;
4. retry indefinitely only on `AlreadyLocked`;
5. propagate permanent acquire errors;
6. after the canonical append body commits, make unlock best-effort and always close the handle.

This preserves the current sidecar confidentiality while satisfying the oldest declared Portalocker API shape.

## Material update 2 — the declared `portalocker>=3` range crosses two materially different Windows implementations

The compatibility problem is broader than raw-fd typing. Portalocker 3.0.0's Windows implementation is `LockFileEx`/pywin32-based and the package declares `pywin32>=226` on Windows. Portalocker 4.0.0 changed the default to the dependency-free `msvcrt` locker, and current Portalocker documents that exclusive locks use `msvcrt` while true shared locks require the optional `win32` extra. Argus still declares the open range `portalocker>=3`.

Therefore one current `windows-latest` CI cell is not a lower-bound compatibility proof. Candidate009 needs at least one explicit `portalocker==3.0.0` Windows lock regression in addition to the ordinary current-resolver portable job. The portable workflow currently installs `-e '.[qr]'`, so it exercises whichever current Portalocker pip resolves.

The proposed event writer contract deliberately uses only the low-level exclusive, non-blocking API common to both checked ends of the supported range and implements its own `AlreadyLocked` retry loop. It does not depend on Windows blocking-lock duration or on shared-lock availability.

## Material update 3 — fixing the writer lock alone leaves a Windows Mission View lost-projection race

The current Mission View lock is structurally the same portability gap as the event writer: `_locked()` uses a process-local `threading.Lock` plus `fcntl.flock` when `fcntl` exists. On Windows, the file-lock half disappears, so two processes can replace `mission-view.json` concurrently.

This becomes directly relevant once `events.lock` is made cross-platform. A source-reachable interleaving is:

1. process A starts `snapshot_mission_view()`, sees an absent/unbootstrapped view, and builds a bootstrap snapshot from the canonical log before projected event E1;
2. process B holds the new cross-platform `events.lock`, appends E1 to the canonical log, then projects E1 into Mission View;
3. because Mission View's Windows lock is only process-local, B can publish its E1-inclusive view while A is still alive;
4. A then publishes its older bootstrap view with `bootstrapped=true`, overwriting B's projection;
5. E1 remains in canonical `events.jsonl`, but future ordinary snapshots trust `bootstrapped=true` and do not automatically recover it.

I reproduced the semantic shape with a deterministic local model using the non-idempotent `round.review.completed` counter: A bootstraps from E0, B appends/projects E1, then A overwrites. The final materialized counter is one lower than canonical replay. This is a source-shaped model, not a production Windows incident.

The correction should therefore treat event-log authority and Mission View bootstrap/reconciliation as one ordering contract: **`events.lock -> mission-view.lock`**. Cold bootstrap must take event authority before publishing a view derived from that event snapshot.

## Material update 4 — do not blindly reacquire `events.lock` inside `update_mission_view_event`

`JsonlEventSink._append()` already holds event authority while calling `update_mission_view_event()`. If the projection helper were mechanically changed to take `events.lock` again through a new separately opened handle, it could self-deadlock. Portalocker's POSIX documentation explicitly notes that two separate `open()` calls in one process conflict under the default `flock` semantics.

The safe API split is:

- writer path: acquire event authority once, append/roll, call an internal Mission View projection routine that assumes event authority is already held and only takes Mission View authority;
- cold bootstrap/reconciliation path: acquire event authority first, then Mission View authority, read a stable canonical snapshot, and publish;
- any public standalone projection helper retained for tests/tooling should either be documented as non-authoritative or acquire the full lock order itself, but it must not be invoked recursively from inside the writer authority.

Production code search at the pinned Argus commit finds `event_log.py` as the production caller of `update_mission_view_event`; other references are tests. This makes internalizing the authority-aware projection path relatively low churn.

## Material update 5 — candidate011: isolate a crash-truncated JSONL record before the next append

A separate record-boundary gap emerged in the canonical event writer. `_append()` writes `line + "\n"` but does not verify that the existing current file ends at a newline boundary. If a prior process/disk interruption leaves a partial JSON object without `\n`, the next successful append concatenates a complete JSON object directly to the partial bytes. The combined physical line is invalid JSON, so the new otherwise-valid event becomes collateral damage along with the old partial record.

The event payload path makes this worth guarding: normalization intentionally preserves full diagnostic repr rather than clipping it, so large individual rows are permitted. No current Argus repair for an unterminated `events.jsonl` tail was found in source search.

A deterministic local reproduction used an unterminated partial Manager-intent JSON prefix followed by a complete Planner-verdict JSON row. After the ordinary append, the file contained one concatenated physical line and `json.loads` rejected it.

The minimally destructive repair is **delimiter isolation, not truncation**:

- while holding event authority and after any rotation decision, inspect the current file if it exists and is non-empty;
- if the final byte is not `\n`, append exactly one newline before the new event row;
- preserve the old partial bytes for forensics; the old row remains malformed, but the next valid event is independently parseable.

A stronger "truncate back to the last newline" repair would throw away partial forensic bytes and is not necessary to protect the next record.

This is candidate `clean-os-g1-011`. It is a process-crash/partial-record isolation hypothesis, separate from candidate008's unproven power-loss durability ordering.

## Candidate011 regression matrix

1. **clean empty file**: no prefix newline is emitted; one valid event remains one line.
2. **clean newline-terminated file**: ordinary append remains byte-for-byte append semantics; no blank line is introduced.
3. **unterminated partial JSON tail below roll threshold**: one delimiter is inserted, the damaged prior row remains present, and the new event parses independently.
4. **unterminated arbitrary UTF-8/invalid-byte tail**: repair works bytewise and does not require decoding the damaged tail.
5. **tail at/over roll threshold**: normal rotation can move the damaged old current generation away; the fresh current file starts directly with the new valid row, without a synthetic leading blank line.
6. **two writers**: tail isolation and append both occur under the same cross-platform event authority so two processes cannot both infer/repair the same tail independently.
7. **planner-verdict interaction**: a target-relevant malformed old row remains `UNKNOWN` evidence, while a later separately delimited valid matching verdict can establish `FOUND`.

## Updated implementation frontier

1. Implement the event-specific authority wrapper with explicit `0600` creation via `os.open` + real file-object wrapping; retry only `AlreadyLocked`; commit-aware best-effort release.
2. Add deterministic wrapper tests plus a spawned-process portable test; add explicit Windows `portalocker==3.0.0` coverage because ordinary portable CI resolves current dependencies.
3. Add candidate011 bytewise unterminated-tail isolation under the same authority and the seven regressions above.
4. Cross-platformize Mission View authority and refactor projection/bootstrap around the single lock order `events.lock -> mission-view.lock`; do not nest a fresh event lock inside writer projection.
5. Finish `PlannerVerdictPersistenceEvidence` (`FOUND/ABSENT/UNKNOWN`) on a stable-generation snapshot. Preserve exact caller-provided delivery-id semantics rather than assuming global SHA-256 formatting.
6. Move `iter_call_events()` and Mission View reconciliation to the same stable-generation primitive. POSIX may later pin handles+end offsets for shorter writer blocking; Windows can begin correctness-first with exclusive event authority.
7. Continue candidate008 power-loss durability separately; no fsync ordering guarantee or production incident is claimed here.
8. Continue candidate005 Manager-intent `transition_id` stage provenance separately.

## Scope limits

- Argus public `main` remained `ae2daa1fbc2c918b4e7126151fe55eb68fd0cb98` at the semantic freeze for this run.
- The Windows Mission View overwrite and candidate011 JSONL concatenation were modeled deterministically from the public source contracts; no production incident or full Windows Argus execution is claimed.
- Portalocker 3.0.0 and current 4.x were checked because Argus explicitly supports the unbounded `portalocker>=3` dependency range.
- Candidate011 contains a containment/recovery proposal, not proof of power-loss durability.
- The prior prohibited connector-discovery branch incident was not repeated; this invocation mutated only authorized open_source state/receipt destinations.

## Nonempty frontier / exact continuation

First convert candidate009 into one explicit authority API contract preserving 0600 mode and add the `portalocker==3.0.0` Windows compatibility cell plus spawned-process contention test. In the same authority primitive, add candidate011's bytewise partial-tail delimiter repair. Then refactor Mission View cold bootstrap/projection to enforce `events.lock -> mission-view.lock` without nested event-lock acquisition and write the deterministic Windows stale-bootstrap overwrite regression. After that, finish PlannerVerdictPersistenceEvidence FOUND/ABSENT/UNKNOWN and move `iter_call_events()` / Mission View reconciliation onto the stable-generation snapshot primitive. Keep candidate008 durability and candidate005 transition provenance separate.
