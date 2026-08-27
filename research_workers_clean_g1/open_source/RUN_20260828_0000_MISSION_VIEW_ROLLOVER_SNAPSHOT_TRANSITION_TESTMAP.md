# open_source clean-g1 run — Mission View rollover snapshot + transition test map

Observed invocation start: 2026-08-28T00:00:22+09:00
Checkpointed at: 2026-08-28T00:13:42.184893+09:00

## Frozen semantic control tuple

- note main SHA at pre-semantic freeze: `5d9d2438d39ec180e65215767f524463fa0f1cc1`
- `automation_control/DESIRED_STATE.json`: control revision `12`, blob `5c91671e1470d0fa4e2a53f918493004dd3750c3`
- `automation_control/roles/open_source.json`: config revision `5`, blob `118f440957ba4654e804af902aa09a9224acca43`
- the second SHA-only note-main lookup matched the first before substantive semantic work; later note-main movement was used only for safe write/CAS mechanics and did not change this invocation's semantic control.
- no role-local feedback file existed at the frozen SHA.
- no O/O-derived state, other worker state/config, downstream comparator/integrator/index/feed/audit semantics, legacy/pre-independence research, shared aggregate execution ledger, or other-role receipts were read.

## Public source snapshot

Repository: `lbx154/Argus`

Current public main observed twice in this invocation: `6953a117d102fc038035bbe654ae55f676b435e6`, unchanged from the prior open-source checkpoint.

The two retained candidates remain distinct:

- `clean-os-g1-006`: Mission View cold-bootstrap/recovery correctness over a multi-generation canonical event log.
- `clean-os-g1-005`: protected handoff/stage-transition provenance and, separately, the previously developed authority/CAS/fencing work. This run only advances the low-churn provenance seam; it does not collapse provenance into authorization.

## `clean-os-g1-006` — new concurrency finding: path enumeration alone is not a stable replay snapshot

Fresh source confirms the existing mismatch:

- `argus_skill/core/mission_view/_snapshot.py::_bootstrap_view()` still replays only `events.jsonl.1` and live `events.jsonl`.
- `_view_state.py::_tail_jsonl()` still reads at most the final 8 MiB from each selected file.
- `argus_skill/life/event_log.py` rolls at 100 MiB, retains all `.2`, `.3`, ... generations, and exposes `event_log_paths()` in canonical oldest-to-newest order.

The prior candidate therefore correctly proposed all-generation replay. This run found an additional requirement: **an all-generation iterator must take a stable rollover snapshot, not merely enumerate path names and then open them later.**

### Why path-name replay can miss a retained generation

The event writer serializes append/rotation with `events.lock`. On rollover, it may rename:

1. old `events.jsonl.1` -> next free `events.jsonl.N`, then
2. live `events.jsonl` -> `events.jsonl.1`.

A deterministic local name-rebinding demonstration used:

- initial `.2 = A-oldest`
- initial `.1 = B-middle`
- initial live = `C-newest`
- reader stores the path list `[.2, .1, live]`
- a rollover occurs before those names are all opened, moving `B` to `.3`, `C` to `.1`, and creating new live `D`

Reading the previously stored *names* then returns `A, C, D`; `B` still exists durably as `.3` but is absent from that replay. This is a source-shaped TOCTOU over path identity, not evidence of an observed production incident.

A second local demonstration pinned/opened the files before the renames and captured their end offsets. The same rollover then occurred, but reads through the already-open file descriptors still returned the intended `A, B, C` snapshot. This demonstrates a viable snapshot primitive, not a completed Argus patch.

### Lock-order constraint

Fresh source also makes lock order important:

- `JsonlEventSink._append()` takes `events.lock` and, while still holding it, calls `update_mission_view_event(...)` for projected events.
- `update_mission_view_event(...)` takes the Mission View lock.
- current `snapshot_mission_view(...)` takes the Mission View lock but does not take `events.lock`.

Therefore a naive patch that acquires `events.lock` *inside* the existing Mission View critical section would invert the writer's order (`mission lock -> events lock` versus `events lock -> mission lock`) and can deadlock. The cold-bootstrap path must preserve a common order of **events lock -> Mission View lock**.

### Correctness-first patch shape

The minimal safe shape is now:

1. Fast path: under only the Mission View lock, return the already-bootstrapped view as today.
2. Cold path: if bootstrap is needed, release that lock, acquire the canonical event-log lock, then acquire the Mission View lock and double-check `bootstrapped`.
3. Under that order, obtain a stable event-log snapshot. A simple first implementation may hold the event lock through replay; a lower-blocking implementation may open/pin every retained generation and capture end offsets while locked, then release only the event lock and replay the captured byte ranges while retaining the Mission View lock.
4. Reduce retained generations in canonical oldest-to-newest order, persist the bootstrapped view, then release the Mission View lock.
5. Events appended after the snapshot boundary may then project normally; because their writer was blocked on the Mission View lock, they are applied after the persisted bootstrap rather than being overwritten by it.

A shared event-log lock helper is preferable to duplicating flock logic. `event_log.py` currently embeds the lock acquisition inside `JsonlEventSink._append`; extracting the same path/process lock discipline for read snapshots would make the order explicit and testable.

Scope remains cold bootstrap/recovery under concurrent rollover only. No claim is made that normal online projection is losing events.

## `clean-os-g1-006` — scan implementation recommendation changed after mixed-density stress

The prior run favored a streaming `rg` fast path for sparse history while keeping Python fallback. This run tested a more signal-like mixed corpus and many-generation shape. These are local synthetic microbenchmarks, not Argus production filesystem measurements.

### Mixed corpus, ~128 MiB, 4 generations, ~32% projected rows

Approx. 226k rows, mixed compact/spaced JSON and variable payload sizes:

- full sequential Python JSON parse: median `596.53 ms`
- Python bytes-regex type prefilter, then JSON parse + canonical projected predicate: `378.17 ms`
- per-generation streaming `rg`, then JSON parse + canonical predicate: `336.97 ms`

### Same ~128 MiB split across 64 generations

- Python bytes-regex prefilter: `381.28 ms`
- spawning `rg` once per generation: `1027.35 ms`
- one `rg` process over all file arguments, single-threaded: `356.96 ms`

The single-process multi-file form was fast in this environment, but this run did not establish a sufficiently strict cross-platform/output-order contract to make its ordering an authority primitive.

### Uniform current SIGNAL vocabulary, ~128 MiB

The current event catalog has 81 signal-vocabulary event types; 34 also belong to the 38 Mission View projected types. A synthetic corpus uniform over those signal names therefore had a projected-row fraction of about `41.97%` (this is a vocabulary-derived test distribution, not measured production frequency):

- full JSON parse: `600.64 ms`
- Python bytes-regex prefilter: `513.75 ms`
- per-generation `rg`: `541.54 ms`

### Revised implementation preference

The portable leading candidate is now a **streaming Python bytes prefilter** for the JSON `type` field, followed by normal JSON parsing and the existing `canonical_event_type(...) in _PROJECTED_EVENT_TYPES` authority check.

Important correctness guard: a prefilter miss must not automatically discard an otherwise valid but unusually formatted JSON object. Either the prefilter must cover the accepted JSON string formatting rigorously, or unmatched valid lines must fall back to normal JSON parse. The prefilter is only an optimization; the JSON + canonical predicate remains authoritative.

`rg` remains an optional optimization worth testing for very sparse large generations, but per-generation process spawning should not be the default. Correct replay order and the stable rollover snapshot are more important than the fast-path choice.

The current `_tail_jsonl()` also tolerates a valid final JSON row without a trailing newline. A replacement streaming iterator should retain at least that permissiveness: malformed or incomplete partial JSON may be skipped, but a complete final JSON object should not be dropped only because the file lacks the final newline.

## `clean-os-g1-006` — regression matrix expanded

Retain the four prior cold-bootstrap regressions:

1. `.2 -> .3 -> .1 -> live` all-generation canonical order.
2. Projected event before the old 8 MiB tail boundary.
3. Legacy alias coverage (`round.started`, `mission.started`, `mission.completed`, `mission.error`, `life.team.waiting`).
4. Optional sparse fast path unavailable -> sequential lossless fallback.

Add concurrency regressions:

5. **rollover during cold bootstrap does not omit a retained generation**: coordinate a writer rollover with a cold reader using barriers; final routing/timeline must include exactly the events in the selected bootstrap boundary and later projected events must appear after it.
6. **lock-order regression**: cold bootstrap must never hold the Mission View lock while waiting to acquire the event-log lock; exercise writer `events lock -> Mission lock` concurrently with bootstrap and require both complete.
7. **snapshot boundary regression**: when files are pinned/captured under the event lock and a writer appends after the boundary, bootstrap reads only captured bytes and the later event is projected exactly once after bootstrap.

The existing `tests/core/test_mission_view.py` fixture style and current event-log helper are sufficient; a new end-to-end harness is not required.

## `clean-os-g1-005` — exact low-churn transition-lineage patch map

Fresh current source still has stable Manager intent identity before replacement reset on both semantic handoff paths:

- front door: `PreparedManagerHandoff.intent_id` (`intent-*`)
- daemon boot: `intent-daemon-*`

Both identities are already used elsewhere, but both are dropped before stage mutation.

Current path:

`existing intent ID -> commit_vertical_decision -> reset_stage_for_new_intent -> reset_stage_for_replacement_intent / rollback_stage -> _set_stage -> stage_history`

Current `stage_history` contains `at`, `from_stage`, `to_stage`, `direction`, `reason`, `by`, plus optional skipped stages. No transition identity is recorded.

Minimum backward-compatible patch:

- add optional `transition_id: str = ""` to `Manager.commit_vertical_decision(...)` and `_commit_vertical_decision_locked(...)`;
- thread it into both new-domain and existing-vertical calls to `reset_stage_for_new_intent(...)`;
- add the same optional argument to `reset_stage_for_new_intent`, `rollback_stage`, `reset_stage_for_replacement_intent`, and `_set_stage`;
- write `stage_history[...]["transition_id"]` only when the normalized value is non-empty;
- `PreparedManagerHandoff.commit()` passes `self.intent_id`;
- daemon boot passes its already-created `intent-daemon-*` ID;
- ordinary `Manager.divide()` and internal planning/reconciliation call sites keep the default empty argument unless they already have an appropriate durable intent identity.

This patch is **provenance only**. The low-level stage primitive explicitly documents that caller identity is not authenticated; a `transition_id` must not be described as a capability, signature, or authorization.

### Source-shaped tests

1. Add a small real-`PreparedManagerHandoff` unit near front-door/pipeline-yield tests with a fake Manager that records kwargs; assert `.commit(force_stage_reset=True)` passes its own `intent_id` as `transition_id`.
2. Extend daemon-boot Manager fake coverage so the forced-replacement call observes its generated `intent-daemon-*` transition ID; assert the same ID remains the backlog replacement identity / completed intent identity.
3. In stage-machine/vertical tests, forced replacement at a later stage records `direction=reset` plus supplied transition ID.
4. Same-first-stage forced replacement still emits a new reset history entry carrying the new transition ID.
5. Non-forced completed-prior-run rollback carries the supplied transition ID when one exists.
6. Existing internal/ordinary callers that pass no transition ID retain the old history schema; do not write an empty key.
7. A future strict handoff-reconciliation test may require that the qualifying reset belongs to the current handoff transition ID, but that belongs to the separate authority/fencing candidate and is not evidence that this provenance patch alone makes recovery safe.

No source call site observed in this run requires a mandatory new parameter; default-empty preserves backward compatibility.

## Candidate status

### `clean-os-g1-006` — strengthened

The correctness gap is no longer just “read all retained generations.” A correct recovery must also define a stable event-log snapshot under concurrent rotation and preserve writer lock order. Performance evidence now favors a portable Python type-prefilter as the default candidate on mixed/signal-like histories; `rg` remains optional rather than foundational.

No production incident, upstream patch, or production filesystem benchmark was observed or executed.

### `clean-os-g1-005` — provenance seam now source-shaped

Existing Manager intent IDs can be threaded into stage history with a small optional-parameter change and directly mapped regression tests. This improves durable lineage only. It does not replace the separate one-shot authority, state revision/CAS, handoff fence, or recovery work developed in earlier clean runs.

## Exact continuation

1. Trace/refactor the event-log lock into a reusable read/write snapshot boundary and compare two implementations: correctness-first lock-held replay versus pinned-fd/end-offset replay that releases the event lock early. Define a two-thread rollover regression that proves no deadlock and no omitted generation.
2. Draft the minimum Mission View iterator using `event_log_paths()` + portable bytes type-prefilter + JSON/canonical authority + sequential fallback, preserving valid no-final-newline rows and malformed-row tolerance.
3. Map `transition_id` regressions to exact existing front-door, daemon-boot, vertical-select, and stage-machine tests; verify every current `commit_vertical_decision` caller remains valid with the optional argument.
4. Keep `clean-os-g1-006` observability recovery separate from `clean-os-g1-005` protected-handoff authority/fencing and from any global PIPELINE_STATE writer refactor.

Frontier remains intentionally non-empty.