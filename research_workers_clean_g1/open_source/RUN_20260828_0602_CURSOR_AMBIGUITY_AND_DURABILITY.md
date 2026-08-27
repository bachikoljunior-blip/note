# open_source clean-g1 run — cursor ambiguity, schema-7 migration, and durability ordering

Observed invocation start: 2026-08-28T05:58:07+09:00
Checkpoint observation: 2026-08-28T06:01:52.950930+09:00

## Frozen semantic control tuple

- note main SHA at pre-semantic freeze: `76324edcba319024c8f771d29eea41a7d81d0e9f`
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

- `JsonlEventSink._append()` normalizes, appends to canonical `events.jsonl` under `events.lock`, then best-effort projects the one event to Mission View. Projection exceptions are swallowed and do not undo the canonical append.
- `handle_event()` normalizes before persistence selection and `_append()` normalizes a persisted event again; direct `.append()` goes straight through `_append()`.
- `normalize_event_envelope()` preserves extra fields and validation does not reject unknown envelope keys, so a distinct sink-owned `event_log_id` can be introduced without changing every per-event payload schema.
- frontend `EventMsg` is an open interface (`[key: string]: unknown`), and current `eventKey()` already prefers explicit identity fields, so preferring `event_log_id` is low-wire-churn.
- Mission View schema remains `6`; `_bootstrap_view()` reads only `events.jsonl.1` and live `events.jsonl` through the 8 MiB tail helper.
- `_write_unlocked()` fsyncs the temporary Mission View file before `os.replace()` but does not fsync the parent directory.
- Argus's separate `continuous.json` writer already implements a stronger internal durability pattern: temp-file fsync, replace, parent-directory fsync, post-replace ambiguity detection, and a regression where replace lands before an `EIO` is surfaced.

## Candidate `clean-os-g1-007` — two exact write-failure variants

The previous fresh-sink E1/E2 witness needs two different persistence failure semantics. They must not be treated as the same retry case.

### Variant A: pre-replace projection loss

1. Append E1 = `round.review.completed(status=continue)` to canonical log.
2. Force Mission View write to fail **before** target replacement.
3. Discard that sink.
4. Append E2 = `round.review.completed(status=blocked)` from a fresh sink.
5. Canonical log contains E1 and E2; persisted Mission View still reflects neither E1 before E2 begins.
6. Correct schema-7 reconciliation must replay E1 then E2 and end with `review.rejected_attempts == 2`.

This is the semantic-hole case from the previous run.

### Variant B: replace landed, then an ambiguous error is raised

1. Append E1 to canonical log.
2. During Mission View `_write_unlocked`, call the real `os.replace(tmp, mission-view.json)` and then raise `OSError(EIO)`.
3. The projection caller sees an exception, but the target bytes already contain E1.
4. Append E2 from a fresh sink.
5. Correct recovery must **read back the persisted view/cursor** before deciding what to replay. If it blindly assumes E1 failed and replays E1 again, the non-idempotent counter becomes `3` instead of `2`.

This distinction is not speculative in the abstract: Argus's own continuous-state tests already encode the exact "replace then fail" ambiguity and assert that the new generation/objective may have landed despite the raised exception. Candidate-007 should reuse the same semantic rule: exceptions after an atomic replacement are not sufficient evidence that the old state is still authoritative.

Source-shaped regression sketch:

```python
def test_projection_post_replace_error_does_not_double_apply(tmp_path, monkeypatch):
    # Arrange schema-7 sink-owned IDs and cursor-enabled reconciliation.
    sink_a = JsonlEventSink(None, life_dir=tmp_path, verbosity="full")

    real_replace = view_state.os.replace
    failed = False

    def replace_then_fail(src, dst):
        nonlocal failed
        real_replace(src, dst)
        if not failed and str(dst).endswith("mission-view.json"):
            failed = True
            raise OSError(errno.EIO, "replace landed; durability result ambiguous")

    monkeypatch.setattr(view_state.os, "replace", replace_then_fail)
    assert sink_a.append({
        "type": "round.review.completed",
        "ts": 1.0,
        "status": "continue",
        "reason": "E1",
    }) is True

    # Restore normal writes, then use a fresh sink like Manager front-door events.
    monkeypatch.setattr(view_state.os, "replace", real_replace)
    sink_b = JsonlEventSink(None, life_dir=tmp_path, verbosity="full")
    assert sink_b.append({
        "type": "round.review.completed",
        "ts": 2.0,
        "status": "blocked",
        "reason": "E2",
    }) is True

    assert load_mission_view(tmp_path)["review"]["rejected_attempts"] == 2
```

The precise monkeypatch target may move after refactoring, but the invariant is fixed: post-replace ambiguity is resolved by readback, not by exception class or blind retry.

## Schema-7 migration contract

A concrete low-churn schema is:

```json
{
  "schema_version": 7,
  "bootstrapped": true,
  "projection": {
    "event_log_id": "opaque-sink-owned-id-or-null"
  }
}
```

Rules:

1. Schema `<=6` has no trustworthy canonical cursor. On read, upgrade the object shape to schema 7 but force `bootstrapped=false`; do not infer a cursor from `last_event_ts`, caller `event_id`, array position, or filename.
2. Cold migration acquires a stable all-generation canonical view and rebuilds from `empty_mission_view()`.
3. During rebuild, track the last **projected** canonical row carrying sink-owned `event_log_id`.
4. If at least one such row exists, persist that ID with the rebuilt state.
5. If retained history is entirely legacy and has no sink-owned ID, persist `event_log_id=null` with `bootstrapped=true`. This means "state rebuilt, no trustworthy incremental anchor yet", not "cursor corrupt".
6. The first later persisted projected event with a sink-owned ID sees the null cursor, performs one all-generation rebuild through its own target ID, and then establishes the anchor. This avoids repeated rebuild loops without inventing a legacy position.
7. A schema-7 file missing/malforming the `projection` object is not trusted as incrementally anchored; fail safe to rebuild.
8. When a non-null cursor cannot be located in retained canonical generations, rebuild from all retained generations rather than guessing.

The cursor remains embedded in the same `mission-view.json` replacement as the state it certifies.

## Sink-owned `event_log_id` preparation boundary

Current `normalize_event_envelope()` copies arbitrary mapping keys and does not reject unknown fields; frontend `EventMsg` is also open. Therefore the ID can be introduced as an envelope-level persistence identity without changing every event payload schema.

Use one preparation boundary:

- `_prepare_persisted_event(event)` normalizes/redacts once and **overwrites** any caller-provided `event_log_id` with a newly generated opaque ID.
- persisted `handle_event()` and direct `.append()` both call that preparation exactly once.
- the exact prepared mapping is used for canonical JSONL storage, Mission View reconciliation, and downstream delivery.
- transient/non-persisted events do not claim canonical-log identity.
- Python/frontend replay identity may prefer `event_log_id`, but correctness still comes from contiguous-prefix reconciliation, not UI dedup.

## Recent-first opaque cursor location benchmark

A local synthetic benchmark tested 32 retained generations, 2,500 JSONL rows each (80,000 rows, 42.61 MiB total). Rows were roughly 0.5 KiB and carried opaque string IDs. This is **not** Argus production filesystem performance.

Median location time using recent-first raw-byte search for the exact `"event_log_id":"..."` needle:

- cursor in newest generation: **0.18 ms**
- cursor near middle generation: **4.66 ms**
- cursor in oldest generation: **9.24 ms**
- missing cursor: **41.32 ms**

For comparison, recent-first full JSON parsing took about 2.73 / 77.82 / 155.49 / 156.86 ms respectively, and authoritative all-generation JSON parsing was about **154.35 ms**.

Implication: use a portable recent-first byte locator as an optimization for a non-null opaque cursor while `events.lock` holds generations stable. Once located, parse/validate the matched row and replay from after that row through the target. If the cursor is absent/unlocatable, authoritative all-generation replay remains the correctness fallback. The locator is never authority by itself.

Because cursor location searches only `event_log_id`, it does not need a fragile projected-event-type regex or legacy-alias list. Projection filtering happens after JSON parse through the existing canonical event machinery.

## Lock-order / import boundary

Current writer order is `events.lock -> mission-view.lock`. Current `snapshot_mission_view()` holds the Mission View lock while calling `_bootstrap_view()`. Therefore a schema-7 bootstrap must not acquire `events.lock` from inside the existing locked region.

Recommended structure:

1. briefly read Mission View under Mission View lock;
2. if schema/current cursor state is trustworthy, use it;
3. otherwise release Mission View lock;
4. acquire a shared/public event-log lock helper;
5. acquire Mission View lock;
6. re-read Mission View (another writer may have repaired it);
7. if still needed, rebuild/reconcile using stable `event_log_paths()`;
8. persist state+cursor and release in reverse order.

`life/event_log.py` only imports Mission View lazily inside `_append()`, so factoring a small public `event_log_locked(life_dir)` helper there (or into a tiny dependency-neutral lock module) appears lower risk than duplicating `fcntl` locking in `_snapshot.py`. This is source-shape analysis, not an executed patch.

## Candidate `clean-os-g1-008` — refined durability ordering using an existing Argus primitive

Current source still does **not** prove power-loss ordering from canonical event to derived view:

- canonical `events.jsonl` append closes/flushed the Python file but does not explicitly fsync the event file;
- rotation uses `os.replace()` without an observed parent-directory fsync;
- Mission View fsyncs its temp file before replace but does not fsync the parent directory afterward.

Argus already has a stronger internal implementation in `daemon/state.py`: `_atomic_write_bytes()` fsyncs the temp file, replaces, fsyncs the parent directory, and detects post-replace ambiguity by readback. This is a strong same-repository precedent, but candidate-008 remains **unmeasured** until a power-loss/fault harness exists.

Candidate ordering:

1. under `events.lock`, perform any rollover;
2. append the canonical event;
3. flush + fsync/fdatasync the canonical event file;
4. if rollover or file creation changed directory entries, fsync the event-log directory before any derived-view advancement;
5. only then reconcile Mission View;
6. Mission View temp file is fsynced, replaced, and its parent directory fsynced;
7. if a post-replace error is observed, read back state/cursor before deciding whether replay is needed.

The desired asymmetry is: "canonical event durable, view may lag" is recoverable; "view/cursor durable while canonical event is not" should not be an allowed committed outcome.

No power-loss incident or hardware/filesystem fault was reproduced in this run.

## Scope limits

- Public Argus source was re-read at exact `main` `ae2daa1fbc2c918b4e7126151fe55eb68fd0cb98`; no public repository was mutated.
- No full Argus checkout/test suite was executed locally.
- The cursor-location benchmark is a local synthetic filesystem microbenchmark, not production performance.
- `event_log_id`, schema 7, contiguous-prefix reconciliation, and durability changes are proposed adaptations.
- Candidate-007 concerns projection exception/process-restart consistency. Candidate-008 remains a separate power-loss durability hypothesis.
- Existing Kafka/Marten precedents from prior role-local state remain background support; no downstream/O information was used.

## Exact continuation

1. Turn Variant A and Variant B into literal tests against the existing `tests/core/test_mission_view.py` and event-log sink test layout; use Argus's existing continuous post-replace test as the internal pattern for Variant B.
2. Specify the exact schema-7 `_read_unlocked()` migration table and malformed-schema behavior, including the one-extra-rebuild legacy-null-cursor path.
3. Map `event_log_locked()` plus stable all-generation iteration into `_snapshot.py` without lock inversion; verify no import cycle with current lazy Mission View import in `life/event_log.py`.
4. Benchmark the recent-first byte cursor locator on deeper generation counts and on a cursor near generation boundaries; keep full JSON replay authoritative on miss.
5. Design candidate-008 fault injection that distinguishes: event-file fsync failure, rollover-directory fsync failure, Mission View replace-before-directory-fsync ambiguity, and recovery readback.
6. Re-read current Argus public main before carrying source claims forward.
7. Keep the frontier non-empty after these tests: continue evaluating whether the same canonical-cursor mechanism can support bounded incremental read models beyond Mission View without introducing cross-view coupling, and continue the optional Manager `transition_id` provenance branch separately.

Frontier remains intentionally non-empty.
