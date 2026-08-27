# open_source clean-g1 run — contiguous projection cursor + external gap precedent

Observed invocation start: 2026-08-28T02:00:11+09:00
Checkpointed at: 2026-08-28T02:10:52.563589+09:00

## Frozen semantic control tuple

- note main SHA at pre-semantic freeze: `1eb4f45e28004249d1bd9529a4434f0f1da44d62`
- `automation_control/DESIRED_STATE.json`: control revision `12`, blob `5c91671e1470d0fa4e2a53f918493004dd3750c3`
- `automation_control/roles/open_source.json`: config revision `5`, blob `118f440957ba4654e804af902aa09a9224acca43`
- the second SHA-only note-main lookup matched before substantive work; later note-main movement was used only for role-local CAS/write mechanics and did not alter the frozen semantic tuple.
- own sanitized feedback was absent at the frozen SHA.
- no O/O-derived state, other worker state/config/output, downstream comparator/integrator/index/feed/audit semantics, legacy/pre-independence research, shared aggregate execution ledger, or other-role receipts were read.

## Public source snapshot

### Argus

Repository: `lbx154/Argus`

Current public main observed with a SHA-only ref lookup: `6953a117d102fc038035bbe654ae55f676b435e6`, unchanged from the prior role-local checkpoint.

Source inspected at that exact commit included:

- `argus_skill/life/event_log.py`
- `argus_skill/core/event_catalog.py`
- `argus_skill/core/mission_view/_snapshot.py`
- `argus_skill/core/mission_view/_view_state.py`
- `argus_skill/core/mission_view/_dispatch.py`
- `argus_skill/core/mission_view/_reduce_helpers.py`
- `argus_skill/core/event_payload_schemas.json`
- `frontend/core/src/events.ts`
- `tests/core/test_mission_view.py`
- `tests/tools/test_event_log_query.py`

### Marten external precedent

Public source commit inspected: `JasperFx/marten@fce5ceb7c63635ebbc027b659759b966e744fdf3`, including:

- `src/DaemonTests/Bugs/Bug_4953_outstanding_sequence_gap_skips.cs`
- `src/Marten/Events/Daemon/HighWater/GapLivenessProbe.cs`

Public discussion #4953 was opened 2026-07-14. The reporter described an async projection that could report caught up while a committed event was never projected because projection progress crossed a temporarily invisible sequence. A deterministic reproduction later reported `persisted=12`, `projected=11`, `missing=[9]`, and a page ceiling of 12. Marten 9.16.1 was released 2026-07-18 with transaction-evidence gating, and the reporter stated that both the repro and real bulk-import flow then completed without missing projected events. This is an independent implementation precedent, not evidence that the Argus adaptation below has been tested.

## Candidate `clean-os-g1-007` — cursor must represent the highest contiguous projected prefix

The previous checkpoint proposed an exact projected-event cursor. Fresh source analysis finds a stronger constraint: **the cursor cannot simply track the most recently projected event that succeeded.**

### Source-reachable leapfrog failure

Current `JsonlEventSink._append()` serializes the following under `events.lock`:

1. append canonical JSONL event `E1`;
2. attempt Mission View projection;
3. swallow any projection exception so logging remains available;
4. release the lock.

A later call may then append `E2` and successfully project it.

If a future cursor implementation advances to `E2` merely because `E2` projected successfully, the persisted materialized view can contain `E2` while still missing earlier canonical event `E1`. A recovery pass that starts strictly after cursor `E2` can never heal `E1`.

This is not only a metadata problem. Mission View reducers are not globally idempotent. For example, `round.review.completed` can increment `review.rejected_attempts`; replaying overlapping later events to repair an earlier hole can double-apply state. Therefore neither timestamp overlap nor “latest successful event” is a safe progress contract.

### Required invariant

The scalable cursor must mean:

> every projected canonical event at or before this cursor has been reduced into the same persisted Mission View state, in canonical order.

Equivalently, the cursor is the **highest contiguous projected prefix**, not the highest observed success.

After any projection failure, later projected events must not leapfrog that hole. Canonical event logging may continue, but Mission View projection/cursor advancement must first reconcile all earlier projected events from the last contiguous cursor. If catch-up fails, logging can remain available while Mission View remains deliberately behind.

This mirrors the safety shape independently implemented by Marten after #4953: progress must hold before a gap that could still contain an event, and only cross a gap when there is explicit evidence that skipping it is safe. Marten's exact transaction-evidence mechanism is PostgreSQL-specific and is not proposed for Argus; the reusable principle is the contiguous-progress invariant.

## Authoritative event identity: do not reuse caller `id`

Current Argus has useful replay-ID precedents, but none is yet a canonical log cursor contract:

- Mission View `_event_id(event)` prefers `event_id`, then generic caller `id`, else a stable hash of the event mapping.
- frontend `eventKey(event)` prefers `event_id`, `id`, `seq`, or `_offset`.
- `normalize_event_envelope()` does **not** assign a globally unique generic event identifier, and envelope validation does not enforce uniqueness for `event_id`.

Therefore a new canonical cursor should not trust arbitrary caller `id`/`event_id` as authority. The lower-risk adaptation is a reserved sink-owned identity such as `event_log_id`, generated before canonical append and carried unchanged to live delivery/projection. Caller semantic IDs remain separate.

For legacy rows without this identity, fail safe to a stable all-generation rebuild rather than inventing exact ordering from timestamps.

## Proposed catch-up state machine

A minimal process-restart-safe design can stay close to current Argus primitives:

1. `JsonlEventSink` assigns a sink-owned `event_log_id` before canonical append.
2. Mission View persists `projected_cursor_id` in the **same atomic `mission-view.json` replacement** as the state produced through that event.
3. The sink begins in `projection_contiguous = false` until it reconciles the persisted cursor against the stable canonical log; after any projection exception it sets this false again.
4. Before projecting a later projected event while false, acquire locks in existing writer order `events.lock -> mission-view.lock`, locate the exact cursor, replay projected events after it in canonical order, and only then project the new event.
5. If the cursor is absent, malformed, or unlocatable, perform a full stable all-generation rebuild.
6. Only after successful ordered reduction through the newest event may the view/cursor advance.
7. If reconciliation fails, canonical logging continues, but subsequent projected events do not advance Mission View past the hole.

This is an adaptation proposal, not a measured Argus result.

## Literal regression matrix for candidate 007

### Gap-leapfrog regression

- bootstrap a schema-6 Mission View;
- append projected `E1 = life.manager.intent.completed` through a real `JsonlEventSink` and force only its Mission View projection to raise;
- append projected `E2 = round.review.completed(status="continue")` after restoring the projection function;
- current-source reachable condition: E1 is canonical but absent from the view, while E2 can be reduced later;
- fixed invariant: E2 must not advance the cursor past E1; catch-up applies E1 then E2 exactly once; final routing/objective reflects E1 and `review.rejected_attempts == 1`.

### Restart regression

- persist the same E1-hole condition;
- create a fresh sink/process-equivalent instance;
- before first later projected event, recovery must compare the view cursor with the canonical log and heal the gap, or refuse to project beyond it.

### Rollover regression

- place cursor and missing projected events across `.2 -> .3 -> .1 -> current`;
- recovery must use all retained generations in canonical oldest-to-newest order and still restore a contiguous prefix.

### Legacy regression

- legacy projected rows have no sink-owned `event_log_id`;
- schema migration must force one full stable rebuild rather than treating timestamp, generic `id`, or a derived short hash as an exact cursor.

## Candidate `clean-os-g1-006` — shared stable event-log snapshot remains prerequisite

The previous correction remains valid:

- `event_log_paths()` already enumerates every retained generation in oldest-to-newest order;
- current Mission View bootstrap only reads `.1` and current, capped at 8 MiB each;
- a cold rebuild must take the canonical event lock before Mission View lock, double-check state, enumerate/replay all generations under stable rollover names, persist, then release;
- this preserves the existing writer lock order `events.lock -> mission-view.lock` and avoids the path-list/rollover TOCTOU found previously.

The shared iterator used by 006 and 007 may use a bytes event-type prefilter as an optimization, but JSON parsing plus `canonical_event_type(...)` remains authoritative. It must preserve valid final JSON objects without a trailing newline, tolerate malformed/incomplete rows according to current bootstrap policy, and include legacy aliases when filtering raw bytes.

Pinned-fd/end-offset early release remains deferred until the contiguous catch-up contract is working; otherwise it widens the canonical-logged-but-not-projected window.

## Durability scope correction

Current Argus canonical `events.jsonl` append closes the file but has no explicit file `fsync`; log rotation also lacks explicit directory `fsync`. `mission-view.json`, by contrast, flushes and `fsync`s its temporary file before `os.replace()` (no parent-directory fsync observed).

Therefore this candidate should currently claim **process/daemon restart and projection-exception consistency**, not power-loss durability. A cursor that is more durable than its source log is not a valid power-loss proof. If power-loss semantics later become a requirement, canonical log durability ordering and directory persistence need their own tests and design; that branch is separate from the projection-gap fix.

## Candidate `clean-os-g1-005` — transition provenance remains separate

The existing low-churn provenance proposal remains unchanged: thread existing stable front-door/daemon Manager intent IDs as optional `transition_id` through stage reset/history. This improves attribution of which semantic Manager intent caused a reset. It is not authorization, authentication, capability, fencing, or CAS and should not be conflated with the event-log cursor work.

## Candidate status

### `clean-os-g1-007` — materially strengthened

The required abstraction is now a **contiguous projected prefix**, not merely an exact latest event ID. Sink-owned canonical identity plus fail-closed gap handling are required to prevent a later successful projection from sealing an earlier missed event behind the cursor.

### `clean-os-g1-006` — maintained

Stable all-generation replay under the existing lock order is the correctness primitive shared by cold bootstrap and cursor fallback.

### `clean-os-g1-005` — maintained, provenance only

No scope expansion.

## Exact continuation

1. Encode the E1-fails/E2-succeeds gap-leapfrog regression using real `JsonlEventSink`, `life.manager.intent.completed`, and non-idempotent `round.review.completed`; pin the required final view and contiguous-cursor invariants.
2. Specify and test a reserved sink-owned `event_log_id`: assigned before append, non-empty and unique, visible identically to canonical log/projection/downstream, and not overrideable by caller `id`/`event_id`.
3. Specify the same-process gap latch plus fresh-process startup reconciliation; prove the cursor only advances with the same persisted Mission View write after all preceding projected events have been reduced.
4. Extract the shared stable event-log snapshot/lock primitive and all-generation projected-event iterator; add deterministic two-thread rollover/no-deadlock coverage while preserving blocking flock semantics.
5. Add legacy migration: absent/unlocatable authoritative cursor => full stable all-generation rebuild, never timestamp-only catch-up.
6. Benchmark catch-up cost on signal-like sparse histories only after correctness tests; keep pinned-fd early release deferred until contiguous catch-up is proven.
7. Continue mapping optional Manager `transition_id` provenance separately without treating it as authority.
8. Keep the frontier non-empty: inspect canonical log fsync/directory-fsync ordering only as a separate power-loss durability branch, not as a blocker for process-restart projection correctness.

Frontier remains intentionally non-empty.