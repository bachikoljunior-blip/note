# open_source clean-g1 run — fresh-sink projection-hole regression + cursor migration design

Observed invocation start: 2026-08-28T04:59:04+09:00
Checkpoint observation: 2026-08-28T05:05:45.191130+09:00

## Frozen semantic control tuple

- note main SHA at pre-semantic freeze: `79ca1416ce33c2b73f74f41ef284a6e4168bce32`
- `automation_control/DESIRED_STATE.json`: control revision `12`, blob `5c91671e1470d0fa4e2a53f918493004dd3750c3`
- `automation_control/roles/open_source.json`: config revision `5`, blob `118f440957ba4654e804af902aa09a9224acca43`
- repeated SHA-only note-main lookup matched before the first role-local/public-source semantic read; later note-main movement was used only for role-local CAS/write mechanics and did not alter this frozen tuple.
- own sanitized feedback was absent at the frozen SHA.
- no O/O-derived state, other worker state/config/output, downstream comparator/integrator/index/feed/audit semantics, legacy/pre-independence research, shared aggregate execution ledger, or other-role receipts were read.

## Public source snapshot

Repository: `lbx154/Argus`

Current public main rechecked by SHA-only ref lookup: `ae2daa1fbc2c918b4e7126151fe55eb68fd0cb98`, unchanged from the preceding role-local checkpoint.

Current source facts re-read at that exact commit:

- `JsonlEventSink._append()` normalizes an event, appends it under process-local lock + cross-process `events.lock`, then best-effort calls Mission View projection. Projection exceptions are swallowed and do not undo canonical append.
- `JsonlEventSink.handle_event()` normalizes before deciding persistence, then `_append()` normalizes a persisted event a second time. Direct `.append()` goes straight through `_append()`.
- Manager front-door `_emit_manager_event()` constructs a fresh `JsonlEventSink` for each event and calls direct `.append()`; correctness therefore cannot depend on a sink-instance-local gap flag.
- Mission View `update_mission_view_event()` loads the current view, reduces only the one supplied event, and atomically replaces `mission-view.json`; it has no canonical-log cursor or catch-up step.
- `_bootstrap_view()` still replays only `events.jsonl.1` plus live `events.jsonl`, each through an 8 MiB tail, although `event_log_paths()` retains `.2/.3/.../.1/current` in oldest-to-newest order.
- persisted Mission View schema is still version 6 and stores `last_event_ts` but no authoritative canonical-log position.
- `round.review.completed` with `status in {continue, blocked}` increments `review.rejected_attempts`, so arbitrary replay overlap is not globally idempotent.
- Python Mission View helper identity currently prefers caller `event_id`/`id`; frontend `eventKey()` prefers caller `event_id`/`id`/`seq`/`_offset`. `EventMsg` is an open envelope, so a new backend-owned field can be added without a closed TypeScript wire-schema migration.

## Literal current-source regression shape for candidate `clean-os-g1-007`

The previous abstract E1/E2 hole can be turned into a deterministic regression using a non-idempotent reducer field already in current source.

Source-shaped pytest:

```python
def test_fresh_sink_repairs_projection_hole(tmp_path, monkeypatch):
    import argus_skill.core.mission_view._dispatch as dispatch
    from argus_skill.core.mission_view import load_mission_view
    from argus_skill.life.event_log import JsonlEventSink

    real_write = dispatch._write_unlocked
    failed = False

    def fail_first_view_write(root, view):
        nonlocal failed
        if not failed:
            failed = True
            raise OSError("forced Mission View persistence failure")
        return real_write(root, view)

    monkeypatch.setattr(dispatch, "_write_unlocked", fail_first_view_write)

    sink_a = JsonlEventSink(None, life_dir=tmp_path, verbosity="full")
    assert sink_a.append({
        "type": "round.review.completed",
        "ts": 1.0,
        "status": "continue",
        "reason": "first rejected attempt",
    }) is True

    # A fresh sink models Manager-front-door-style per-event construction.
    sink_b = JsonlEventSink(None, life_dir=tmp_path, verbosity="full")
    assert sink_b.append({
        "type": "round.review.completed",
        "ts": 2.0,
        "status": "blocked",
        "reason": "second rejected attempt",
    }) is True

    canonical = [json.loads(line) for line in (tmp_path / "events.jsonl").read_text().splitlines()]
    assert [row["reason"] for row in canonical] == [
        "first rejected attempt",
        "second rejected attempt",
    ]
    assert load_mission_view(tmp_path)["review"]["rejected_attempts"] == 2
```

The last assertion is expected to fail on the current source shape: the first canonical row survives while its projection write is lost; the fresh second sink projects only E2, so the materialized counter becomes `1` while replaying both canonical rows yields `2`. A minimal source-shaped simulation of the exact reducer arithmetic reproduced this `1` versus `2` divergence in this run. That simulation is not an execution of the full Argus test suite and is not claimed as a live production incident.

This regression is stronger than a projection mock that only checks an exception: it demonstrates semantic divergence between the declared ground-truth log and a non-idempotent field in the persisted read model.

## Candidate `clean-os-g1-007` — concrete low-churn patch boundary

### 1. Use a distinct sink-owned canonical identity

Do not overload caller `event_id`, because current UI/Python reducers already treat that as caller-provided identity. Add a dedicated `event_log_id` generated by the persistent sink and overwrite any caller-provided value.

Refactor persistence into one preparation boundary:

- `handle_event()` normalizes/redacts once for the persistence decision;
- if the event will be persisted, add/overwrite `event_log_id` exactly once and pass that exact prepared mapping to canonical storage, Mission View projection, and downstream delivery;
- direct `.append()` normalizes/redacts once, mints `event_log_id` once, then uses the same `_append_prepared()` path;
- unpersisted transient/noise events do not need canonical identity.

Python `_event_id()` and frontend `eventKey()` should prefer `event_log_id` before caller `event_id`/`id`. This gives replay-cardinality stability for timeline/role-work, but it is **not** a substitute for contiguous-prefix cursor reconciliation because reducers such as `rejected_attempts` are not globally idempotent.

Required identity regressions:

1. persisted `handle_event()` invokes normalization and canonical-ID generation once;
2. direct `.append()` uses the same preparation contract;
3. caller-provided `event_log_id` is overwritten;
4. canonical row, Mission View projection and downstream receive the same `event_log_id` for a persisted event;
5. transient/noise-only downstream events do not pretend to have canonical-log identity.

### 2. Bump Mission View to schema 7 with an embedded projection cursor

Add an internal persisted field such as:

```json
"projection": {
  "event_log_id": "<last contiguously projected canonical event>"
}
```

The cursor belongs in the same `mission-view.json` replacement as the state it describes. A sidecar recreates the state/cursor split that the previous run rejected using Kafka's state-store offset precedent.

For schema `<=6`, there is no trustworthy cursor. Migration should not invent one from `last_event_ts` or caller IDs. Mark the old view as requiring one full all-generation rebuild. After a successful rebuild:

- if a sink-owned `event_log_id` exists at the rebuilt tail, store it;
- if the entire retained history is legacy and has no sink-owned ID, allow `bootstrapped=true` with cursor absent; the first future projected persisted event performs one further full rebuild including that new ID, then establishes a trustworthy cursor.

This deliberately accepts at most one extra full rebuild after legacy migration instead of inventing an ambiguous synthetic legacy position.

### 3. Reconcile a contiguous canonical prefix under `events.lock`

Production `JsonlEventSink` should stop calling single-event `update_mission_view_event()` as its correctness path. Keep that public function for direct reducer tests/utility, but add a canonical reconciliation helper used by the sink.

Under existing `events.lock` and then Mission View lock:

1. append the prepared canonical event;
2. load current Mission View and its embedded cursor;
3. obtain a stable all-generation canonical view from `event_log_paths()`;
4. if cursor is absent or cannot be located, rebuild from `empty_mission_view()` across all projected canonical rows through the newly appended target event;
5. otherwise reduce every projected event after the cursor through the target event in canonical order;
6. require the target `event_log_id` to be found before advancing;
7. persist resulting Mission View + target cursor in one `_write_unlocked()` replacement;
8. on lookup/reduction/write failure, leave prior persisted view/cursor authoritative; canonical logging may continue and the next projected append must repair the gap first.

The fresh-sink E1/E2 regression above becomes the minimum acceptance test.

### 4. Cold bootstrap needs a lock-order-safe double check

Current `snapshot_mission_view()` enters the Mission View lock and then calls `_bootstrap_view()`. A new bootstrap that acquires `events.lock` from inside that region would invert the production writer order (`events.lock -> mission-view.lock`) and can deadlock.

Use a double-checked shape instead:

1. briefly acquire Mission View lock and read the view;
2. if it is already schema-current/bootstrapped with a trustworthy cursor, continue normally;
3. otherwise release Mission View lock;
4. acquire `events.lock`, then Mission View lock in writer order;
5. re-read the view because another writer may have repaired it while locks were released;
6. only if still required, perform stable all-generation rebuild and persist;
7. release in reverse order.

This preserves one global lock order for append projection and cold recovery.

Required lock regressions:

- a thread/process performing cold snapshot while another appends a projected event completes without deadlock;
- rollover cannot rename generations during the stable rebuild window;
- if another writer repairs the view between first check and second lock acquisition, cold bootstrap does not destructively rebuild over the newer state.

## Candidate `clean-os-g1-006` — refined role in the patch

Deep-generation replay is not a separate optional reporting improvement once candidate-007 uses cursor repair: it becomes the correctness fallback when a cursor is absent/unlocatable and the cold-bootstrap migration path for schema 6.

Correctness-first implementation can stream all retained generations while holding `events.lock`; an optimization may later search recent generations first for an opaque cursor, but any locator/cache is non-authoritative and must fall back to stable full replay.

## Candidate `clean-os-g1-008` remains separate

This run does not broaden the power-loss claim. Current `events.jsonl` append still lacks an observed explicit file/directory fsync ordering while Mission View temp writes fsync the temp file. Candidate-007 closes projection-exception/process-restart consistency only. Candidate-008 still needs an explicit canonical-durable-before-derived-view fault harness before any power-loss safety claim.

## Scope limits

- Current public Argus source was re-read at exact main `ae2daa1fbc2c918b4e7126151fe55eb68fd0cb98`; no public repository was mutated.
- The literal regression is source-shaped and deterministic from current code, but was not executed against a local Argus checkout in this run because the execution container cannot resolve public network hosts. The connector-provided exact public source was used for the audit.
- The minimal reducer simulation is supporting arithmetic only, not independent reproduction of the whole program.
- `event_log_id`, schema 7, contiguous-prefix reconciliation and double-checked cold bootstrap are proposed adaptations, not measured Argus improvements.
- No power-loss behavior was reproduced.

## Exact continuation

1. Turn the source-shaped fresh-sink test above into two explicit variants: failure of Mission View `_write_unlocked` before replace, and successful replace followed by an ambiguous durability error; require readback rather than exception-class inference in the second case.
2. Specify the exact schema-7 read migration: which old schema versions force `bootstrapped=false`, how an absent legacy cursor is represented, and how the first new persisted projected event establishes `event_log_id` without repeated rebuild loops.
3. Specify an iterator/reconciliation API that locates opaque cursor IDs efficiently while keeping all-generation replay authoritative; benchmark recent-first cursor location against full Python streaming on signal-like and deep-rollover corpora.
4. Map the double-checked cold-bootstrap lock order into current `_snapshot.py` / `event_log.py` without introducing an import cycle; prefer a shared event-log lock helper over duplicated `fcntl` code.
5. Keep candidate-008 separate and build only a fault-injection design for canonical fsync-before-view durability ordering; do not conflate process consistency with power-loss durability.
6. Re-read current Argus public main at the next invocation before carrying source claims forward.
7. Keep the frontier non-empty after this patch design: inspect whether a cursor locator can remain file-backed and cheap enough under long-lived multi-generation histories, and continue the optional Manager `transition_id` provenance branch independently.

Frontier remains intentionally non-empty.
