# open_source clean-g1 run — projection cursor/state atomicity + durability boundary

Observed invocation start: 2026-08-28T04:03:13+09:00

## Frozen semantic control tuple

- note main SHA at pre-semantic freeze: `ece8f2890381618cb2035b8e9575cf2562f5721a`
- `automation_control/DESIRED_STATE.json`: control revision `12`, blob `5c91671e1470d0fa4e2a53f918493004dd3750c3`
- `automation_control/roles/open_source.json`: config revision `5`, blob `118f440957ba4654e804af902aa09a9224acca43`
- the repeated SHA-only note-main lookup matched before the first role-local/public-source semantic read; later note-main movement was used only for role-local CAS/write mechanics and did not alter this frozen tuple.
- own sanitized feedback was absent at the frozen SHA.
- no O/O-derived state, other worker state/config/output, downstream comparator/integrator/index/feed/audit semantics, legacy/pre-independence research, shared aggregate execution ledger, or other-role receipts were read.

## Public source snapshot

### Argus

Repository: `lbx154/Argus`

Current public main observed by SHA-only ref lookup: `ae2daa1fbc2c918b4e7126151fe55eb68fd0cb98`.

This is four commits ahead of the prior role-local source checkpoint `93a01f185f3c4800f127feca0739dbe7331c1950`. A direct commit comparison showed no changes in the files carrying candidate-006/007 (`argus_skill/life/event_log.py`, `argus_skill/core/mission_view/_snapshot.py`, `_view_state.py`, `_dispatch.py`, `_reduce_mission.py`, or `argus_skill/manager/front_door.py`), and those files were re-read at the exact current commit.

Observed current-source facts remain:

- `JsonlEventSink._append()` holds a process-local lock plus POSIX `events.lock`, rotates if needed, appends one JSONL line, then attempts Mission View projection. Projection exceptions are intentionally swallowed so canonical logging continues.
- `event_log_paths()` enumerates retained `.2/.3/.../.1/current` generations oldest-to-newest, but Mission View `_bootstrap_view()` still reads only `events.jsonl.1` and live `events.jsonl`, using only each file's tail up to 8 MiB.
- `update_mission_view_event()` reduces one event and persists the whole Mission View under the Mission View lock; the persisted view currently has `last_event_ts` but no authoritative canonical-log cursor/sequence.
- `handle_event()` normalizes/redacts once into `safe_event`, then persisted events pass through `_append()`, which normalizes/redacts again; downstream delivery receives the first mapping while canonical serialization/projection receives the second. Production Manager front-door also constructs a fresh `JsonlEventSink(...).append(event)` for each Manager event, bypassing `handle_event()`.
- `round.review.completed` with `status in {continue, blocked}` increments `review.rejected_attempts`, so arbitrary overlap replay is not globally idempotent.

### Apache Kafka / Kafka Streams 4.3+

Repository: `apache/kafka`

Current public trunk observed by SHA-only ref lookup: `db8a0925513a76d1a4f13df00867c7491a4b3ce7`.

Current `StateStore` contract states that a store managing changelog offsets guarantees those offsets are persisted with the written records and should commit them atomically where possible. Current `RocksDBStore` implements this by:

- declaring an `offsets` column family;
- setting RocksDB `atomicFlush=true`;
- returning `managesOffsets() == true`;
- passing changelog offsets into `commit(...)`;
- writing changelog offsets plus the position into the offsets column family before `commitStagedWrites()`.

The accepted/released KIP-1035 rationale is directly relevant: a separate checkpoint file cannot atomically synchronize the state and the changelog position it represents, so Kafka 4.3 moved per-store offsets into the state store itself and configured RocksDB to atomically flush all column families. Kafka's own 4.3 documentation also preserves an important distinction: co-location/atomic flush aligns state with its offset, but low-traffic RocksDB state need not become durable on every task commit; durability occurs when RocksDB actually flushes. Atomic consistency and disk-durability timing are separate properties.

### Marten

Repository: `JasperFx/marten`

Current public master was rechecked at `fce5ceb7c63635ebbc027b659759b966e744fdf3`. Its async-daemon contract remains a useful independent control: projection progress/high-water advances contiguously and holds below an outstanding sequence gap until the gap is proven dead. Current regression tests explicitly assert that a projection/high-water mark must not advance across an in-flight sequence.

## Candidate `clean-os-g1-007` — strengthened by current state-store offset precedent

The required Argus invariant remains:

> Under shared `events.lock`, a projected append may advance Mission View only across one contiguous canonical prefix ending at the newly appended event, and the resulting Mission View state plus canonical cursor must become visible together. If reconciliation/reduction/view-write fails, the prior view/cursor stays authoritative and a later projected append must repair the gap before advancing.

Kafka 4.3 materially strengthens one design choice: **put the projection cursor inside the same persisted Mission View object rather than in a separate sidecar or process-local latch.** The cursor is metadata describing exactly which canonical records the materialized state represents, analogous to the state-store changelog offset Kafka now co-locates with the state it describes.

A low-churn file-backed Argus shape is therefore:

1. one explicit persisted-event preparation step normalizes/redacts once and overwrites any caller-provided canonical event identity with a sink-owned opaque ID;
2. under `events.lock`, append the exact prepared mapping to the canonical JSONL;
3. for a projected event, acquire Mission View lock in existing order `events.lock -> mission-view.lock`;
4. load the persisted Mission View cursor;
5. locate it across a stable all-generation canonical-log view;
6. reduce every projected canonical event after that cursor through the newly appended event in canonical order;
7. persist both the resulting view and newest cursor in the same Mission View replacement;
8. if cursor lookup/reduction/write fails, do not advance the cursor; absent/unlocatable legacy cursor falls back to stable full rebuild.

This rejects a sink-local/process-local `projection_gap` boolean as correctness authority. Manager front-door creates fresh sink objects per event and the file lock is explicitly cross-process, so safety must be reconstructed from shared durable state on every projected append.

### Required regressions

1. **Fresh sink hole:** sink A canonical-appends projected E1 while its Mission View projection is forced to fail; A is discarded; fresh sink B appends projected E2. Fixed result must reduce E1 then E2 exactly once and advance the cursor only to E2.
2. **Cross-process equivalent:** two sink/process instances sharing one `life_dir` must satisfy the same result under `events.lock`.
3. **View+cursor atomicity:** after successful in-memory reduction, force Mission View replacement failure; both prior view and prior cursor must remain authoritative.
4. **Direct append identity:** Manager-front-door-shaped `.append()` must mint the same sink-owned ID seen by canonical storage and projection.
5. **Handle-event identity:** one persisted `handle_event()` must call the canonical-ID generator exactly once and canonical/projection/downstream must see the identical prepared mapping.
6. **Caller override:** caller-supplied canonical ID cannot become authoritative.
7. **Deep rollover recovery:** cursor and missing projected event may straddle `.2/.3/.../.1/current`; ordering and lock order must remain stable.
8. **Legacy migration:** no/unlocatable cursor => stable all-generation rebuild, not timestamp or generic caller-ID guessing.

## Candidate `clean-os-g1-008` — canonical-log durability must precede derived-view durability

A separate durability boundary is now explicit.

Current Argus calls `events.jsonl` the ground-truth replay surface, but the current append path writes/closes the file without an observed explicit `fsync`, and rollover performs `os.replace()` operations without an observed parent-directory `fsync`. By contrast, Mission View `_write_unlocked()` writes a temp file, flushes it, calls `os.fsync()` on that file, and then replaces `mission-view.json` (also without an observed parent-directory `fsync`).

This source asymmetry does **not** prove an observed data-loss incident, and this run did not emulate real power failure. It does mean the stronger power-loss invariant is not established by the current implementation:

> A derived Mission View/cursor must never be durably ahead of the canonical log bytes it claims to represent.

For an append-only authoritative log plus rebuildable materialized view, the desirable failure asymmetry is the opposite: canonical log may be durable while Mission View lags, because catch-up/rebuild can repair that; Mission View being durable for an event absent from the recovered canonical log is harder to reconcile truthfully.

### Minimum file-backed durability ordering to test

A correctness-first variant is:

1. append canonical event;
2. flush + `fsync` canonical event file before any durable projection checkpoint can advance;
3. if rollover renames generations, durably order the directory metadata as well;
4. reconcile contiguous projected prefix;
5. write Mission View temp, file-`fsync`, replace, parent-directory `fsync`;
6. only then report the new view/cursor durable.

Batch/group commit may amortize the sync cost, but must preserve the same ordering. A larger architectural alternative is a transactional local store (for example SQLite WAL) containing canonical event identity, materialized state and cursor, but that has substantially higher migration/churn and should not be preferred without measurement.

### Local feasibility probe (not production evidence)

A local synthetic filesystem microbenchmark in this run measured one ~1 KiB canonical append with file `fsync`, followed by atomic-replace Mission View with file+parent-directory `fsync`. Median end-to-end times over 120 iterations per size were approximately:

- 4 KiB view: 2.28 ms
- 64 KiB view: 2.67 ms
- 256 KiB view: 2.96 ms
- 1 MiB view: 4.83 ms

These numbers are environment-specific, include neither Argus reduction work nor production filesystem/device behavior, and must not be generalized. They only show that a correctness-first fully-synced prototype is not obviously infeasible on this local environment. Real Argus signal/full-verbosity workloads need measurement before selecting per-event fsync versus grouped commits.

### Durability regressions to add after candidate-007 process consistency

- inject failures at canonical write / canonical fsync / rollover rename / Mission View temp write / Mission View fsync / replace / directory fsync boundaries;
- after each simulated restart, the recovered state may be old or new but must never expose a Mission View cursor beyond recoverable canonical events;
- keep power-loss claims separate from process-crash/projection-exception claims until a filesystem-appropriate durability test exists.

## Scope limits

- This run re-read current public sources and derived source-shaped candidate designs; it did not patch Argus or claim a live production incident.
- Candidate-007 is about projection-exception/process-restart consistency and exact contiguous-prefix provenance.
- Candidate-008 is a durability-ordering hypothesis/invariant prompted by observed source behavior; real power-loss behavior was not reproduced.
- Kafka KIP-1035 is an independent implementation precedent for state+offset co-location/atomic flush, not evidence that the Argus adaptation itself improves outcomes.
- The local fsync benchmark is a feasibility probe only.
- `clean-os-g1-005` optional Manager `transition_id` remains a separate provenance-only branch, not authorization/fencing/CAS.

## Exact continuation

1. Turn the fresh-sink A/E1-projection-fails -> fresh-sink B/E2-succeeds sequence into a literal existing-test-shaped regression around current `JsonlEventSink` + `load_mission_view` semantics.
2. Specify a first-class Mission View cursor field and one shared reconciliation helper under `events.lock`; use view+cursor same-object replacement, not a sidecar.
3. Specify `_prepare_persisted_event` / `_append_prepared` so normalization/redaction and sink-owned canonical identity happen exactly once for both `handle_event()` and direct `.append()`.
4. Add deep-generation stable replay under `events.lock -> mission-view.lock`, including rollover while recovery is attempted and legacy no-cursor fallback.
5. Build the minimal fault-injection harness for candidate-008 that asserts canonical durable-before-view ordering without claiming real power-loss reproduction; compare per-event fsync versus small group-commit batches on realistic Mission View sizes.
6. Re-read current Argus public main next run before carrying source claims forward; the repository is moving quickly.
7. Keep the frontier non-empty: after projection/cursor correctness, inspect whether a file-backed grouped durability protocol is sufficient or whether a transactional local store is warranted; continue optional Manager `transition_id` provenance independently.

Frontier remains intentionally non-empty.
