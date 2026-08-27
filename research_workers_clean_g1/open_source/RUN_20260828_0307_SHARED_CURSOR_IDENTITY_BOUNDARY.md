# open_source clean-g1 run — shared projection cursor + canonical identity boundary

Observed invocation start: 2026-08-28T03:02:09+09:00
Checkpointed at: 2026-08-28T03:07:11.140753+09:00

## Frozen semantic control tuple

- note main SHA at pre-semantic freeze: `bf99a9f8e4ad6dd44065949c980cbb19a2d7db0e`
- `automation_control/DESIRED_STATE.json`: control revision `12`, blob `5c91671e1470d0fa4e2a53f918493004dd3750c3`
- `automation_control/roles/open_source.json`: config revision `5`, blob `118f440957ba4654e804af902aa09a9224acca43`
- the second SHA-only note-main lookup matched before substantive role-local/public-source work; later note-main movement was used only for role-local CAS/write mechanics and did not alter the frozen semantic tuple.
- own sanitized feedback was absent at the frozen SHA.
- no O/O-derived state, other worker state/config/output, downstream comparator/integrator/index/feed/audit semantics, legacy/pre-independence research, shared aggregate execution ledger, or other-role receipts were read.

## Public source snapshot

Repository: `lbx154/Argus`

Current public main observed with SHA-only ref lookup: `93a01f185f3c4800f127feca0739dbe7331c1950`.

This is 15 public commits ahead of the prior role-local Argus checkpoint `6953a117d102fc038035bbe654ae55f676b435e6`. The exact current source was re-read at `93a01f1`, including:

- `argus_skill/life/event_log.py`
- `argus_skill/core/event_catalog.py`
- `argus_skill/core/mission_view/_snapshot.py`
- `argus_skill/core/mission_view/_view_state.py`
- `argus_skill/core/mission_view/_dispatch.py`
- `argus_skill/core/mission_view/_reduce_mission.py`
- `argus_skill/manager/front_door.py`
- `argus_skill/apps/_inbox.py`
- `tests/core/test_mission_view.py`

The candidate-006/007 source conditions remain present at this current public main: canonical append happens under `events.lock`; Mission View projection is attempted after append and projection exceptions are swallowed; current cold bootstrap still reads only `events.jsonl.1` and live `events.jsonl` tails; Mission View writes are separate atomic replacements; `round.review.completed(status in {continue, blocked})` increments `review.rejected_attempts` and is therefore not globally replay-idempotent.

## Candidate `clean-os-g1-007` — correction: a sink-local gap latch is insufficient

The prior checkpoint proposed a same-process `projection_contiguous` latch on `JsonlEventSink`. Fresh source analysis shows that is not a sufficient correctness primitive.

### Why the latch can be bypassed even without a process restart

`JsonlEventSink` documents and implements a POSIX file lock specifically to serialize append, rotation and Mission View projection across processes/components. More importantly, current production code frequently constructs short-lived sink objects. For example, Manager front-door `_emit_manager_event()` creates a new `JsonlEventSink(None, life_dir=...).append(event)` for each event, and this path emits projected Manager lifecycle events including `life.manager.intent.started/completed/failed`.

Therefore:

1. sink instance A appends projected E1;
2. E1's Mission View projection raises and is swallowed;
3. any process-local/sink-local boolean on A becomes false;
4. E1's sink may immediately cease to exist;
5. sink instance B is newly constructed for projected E2 with a fresh default latch;
6. B can project E2 unless correctness is re-established from shared durable state while holding `events.lock`.

The same problem exists across concurrently alive processes even if each process retains one long-lived sink. A local boolean in process A cannot fence process B.

### Required correction

The correctness gate must be **shared under the canonical event lock**, not merely remembered by one sink object.

A correctness-first path is:

1. acquire existing `events.lock`;
2. append the current canonical event;
3. for a projected event, acquire Mission View lock in the already-established order `events.lock -> mission-view.lock`;
4. read the persisted projected cursor from Mission View;
5. locate that cursor in a stable all-generation canonical-log view;
6. reduce every projected canonical event after the cursor through the newly appended event in canonical order into one in-memory view;
7. persist the resulting view and newest contiguous cursor in the same atomic Mission View replacement;
8. if locate/reduce/write fails, do not advance the view/cursor; canonical logging may still remain available.

This makes E2 automatically repair an earlier E1 hole regardless of which sink/process wrote E1. A process-local latch may remain as a performance hint only if it cannot bypass this shared check.

A lower-churn alternative is a durable shared `projection_gap` marker, but it still needs exact cursor/log reconciliation on recovery; a per-object boolean alone is rejected.

## Candidate `clean-os-g1-007` — identity mint point must change because current sink normalizes twice

The prior checkpoint proposed a reserved sink-owned `event_log_id`. Current source exposes an implementation trap.

`JsonlEventSink.handle_event()` first calls `_normalize(event)` and stores `safe_event`. For persisted events it then calls `_append(safe_event)`. `_append()` calls `_normalize(event)` **again**, and Mission View projection receives this second normalized `payload`. After `_append()` returns, downstream delivery receives the first `safe_event`.

At the same time, production Manager front-door uses the public `.append(event)` method directly, bypassing `handle_event()` entirely.

Consequences for a naive `event_log_id` patch:

- mint only in `handle_event()` => direct `.append()` projected events have no authoritative ID;
- mint only in `_append()` => canonical log/projection see the ID but downstream `handle_event()` delivery does not;
- mint unconditionally inside `_normalize()` => the two normalization passes can mint two different IDs;
- preserve a caller-provided `event_log_id` to avoid double minting => caller controls what is supposed to be sink authority.

### Required identity boundary

Refactor to one explicit persisted-event preparation step. The safe shape is:

- normalize/redact the source event;
- **unconditionally replace any caller `event_log_id`** with one sink-generated opaque ID exactly once;
- pass that same prepared mapping unchanged to canonical JSONL serialization and Mission View projection;
- for `handle_event()`, deliver that same prepared mapping downstream after canonical acceptance;
- for direct `.append()`, use the same preparation path even though there is no downstream;
- transient/verbosity-dropped events that are never canonical need not claim a canonical `event_log_id`.

One concrete refactor is `_prepare_persisted_event(...) -> dict` plus `_append_prepared(payload) -> bool`; `handle_event()` and public `append()` both call preparation exactly once. `_append_prepared` must not normalize again.

This is stricter than the previous proposal and is required if `event_log_id` is to mean the same event in canonical log, projection and live downstream delivery.

## Source-shaped regression matrix

### 1. Fresh-sink gap regression

Use one `life_dir` and two distinct `JsonlEventSink` objects.

- sink A appends projected E1 (`life.manager.intent.completed`) while Mission View projection is monkeypatched to raise only for E1;
- discard A;
- construct sink B;
- B appends projected E2 (`round.review.completed`, status=`continue`);
- required fixed result: E1 and E2 are both reduced in canonical order, cursor ends at E2, routing/objective reflects E1 and `review.rejected_attempts == 1`.

This directly rejects sink-local gap state as the safety boundary.

### 2. Cross-process equivalent

Use two processes/sinks sharing one `life_dir`, with deterministic barriers around the existing `events.lock`. Force process A's E1 projection to fail; then let process B append E2. The same contiguous-prefix invariant must hold. This validates that the file lock, not object lifetime, is the authority boundary.

### 3. Caller ID override regression

Call `handle_event` with `event_log_id="caller-controlled"` and a projected event. Required fixed result:

- canonical row contains a different sink-generated non-empty ID;
- Mission View projection receives exactly that generated ID;
- downstream receives exactly the same generated ID;
- the caller value is not authoritative.

### 4. Direct append identity regression

Call the production-shaped `.append()` path used by Manager front-door. Required fixed result: canonical row and Mission View projection share one generated `event_log_id` even though no downstream exists.

### 5. Exactly-once preparation regression

Instrument the ID generator and call `handle_event()` for one persisted event. It must be called exactly once; current double-normalization must not result in two IDs.

### 6. Legacy cursor fallback

Rows without sink-owned `event_log_id` remain legacy. An absent/unlocatable authoritative cursor triggers full stable all-generation rebuild rather than timestamp/generic-id guesswork.

## Candidate `clean-os-g1-006` — maintained as shared fallback primitive

The previous all-generation bootstrap gap remains present at current public main: `_bootstrap_view()` still iterates only `events.jsonl.1` and live `events.jsonl`, while `event_log_paths()` can enumerate retained `.2/.3/.../.1/current` generations oldest-to-newest.

The stable all-generation reader remains the shared primitive for:

- cold bootstrap after snapshot loss;
- candidate-007 legacy migration;
- cursor-not-found fail-safe recovery;
- projected-prefix reconciliation after a swallowed projection failure.

The prior lock-order correction also remains: stable recovery must take canonical `events.lock` before Mission View lock, matching writer order, rather than acquiring them in reverse.

## Scope limits

- This run establishes source-level reachability and a corrected design/test contract; it did not patch or execute Argus production code.
- The public Argus head changed since the prior checkpoint, so all source claims above are tied to exact commit `93a01f185f3c4800f127feca0739dbe7331c1950`.
- Canonical `events.jsonl` append/rotation still has no explicit observed file/directory fsync ordering. Claims remain limited to process/daemon restart and projection-exception consistency, not power-loss durability.
- `clean-os-g1-005` optional Manager `transition_id` remains a separate provenance-only branch and is not authority/fencing/CAS.

## Exact continuation

1. Turn the fresh-sink A/E1-fails -> fresh-sink B/E2-succeeds sequence into a literal existing-test-shaped regression around real `JsonlEventSink` and `load_mission_view`.
2. Design the shared reconciliation helper so every projected append under `events.lock` either advances one contiguous prefix or leaves the persisted cursor unchanged; avoid relying on process-local gap state for safety.
3. Specify `_prepare_persisted_event` / `_append_prepared` contracts and test Manager-front-door-shaped direct `.append()` plus normal `handle_event()` so one sink-owned ID is identical in canonical/projection/downstream paths and caller override is impossible.
4. Decide the least-cost cursor locator representation: opaque `event_log_id` plus all-generation scan first; only add generation/offset acceleration after correctness is proven.
5. Add deterministic rollover coverage where the cursor and missing event straddle `.2/.3/.1/current`, preserving `events.lock -> mission-view.lock` and no deadlock.
6. Keep legacy absent/unlocatable cursor => full stable rebuild.
7. Re-check current public Argus main next run because the repository is moving quickly; do not carry this exact commit's source claim forward without readback.
8. Keep the frontier non-empty: separately inspect whether canonical-log power-loss ordering should be hardened after process-restart consistency is closed, and continue optional Manager `transition_id` provenance independently.

Frontier remains intentionally non-empty.