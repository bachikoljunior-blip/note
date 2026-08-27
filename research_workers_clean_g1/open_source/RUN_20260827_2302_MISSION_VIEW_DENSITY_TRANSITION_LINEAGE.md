# open_source clean-g1 run — Mission View density stress + transition lineage

Observed invocation start: 2026-08-27T23:02:35+09:00
Checkpointed at: 2026-08-27T23:14:28.920459+09:00

## Frozen semantic control tuple

- note main SHA at pre-semantic freeze: `016c2e65661637e130e6802f7609fd47d942e3cc`
- `automation_control/DESIRED_STATE.json`: control revision `12`, blob `5c91671e1470d0fa4e2a53f918493004dd3750c3`
- `automation_control/roles/open_source.json`: config revision `5`, blob `118f440957ba4654e804af902aa09a9224acca43`
- the second SHA-only note-main lookup matched the first before substantive semantic work; later note-main movement was not adopted into this invocation's semantic control.
- no role-local feedback file existed at the frozen SHA.
- no O/O-derived state, other worker state/config, downstream comparator/integrator/index/feed/audit semantics, legacy/pre-independence research, shared aggregate execution ledger, or other-role receipts were read.

## Public source snapshot

Repository: `lbx154/Argus`

Current public main observed in this invocation: `6953a117d102fc038035bbe654ae55f676b435e6`, nine commits ahead of the prior open-source checkpoint head `ea50b6a9169f3d5885d15f3f13a28543ae9989a8`.

The core `clean-os-g1-006` gap remains source-current at this head:

- `argus_skill/core/mission_view/_snapshot.py::_bootstrap_view()` still replays exactly `events.jsonl.1` and live `events.jsonl`.
- `argus_skill/core/mission_view/_view_state.py::_tail_jsonl()` still caps each selected file at the final 8 MiB.
- `argus_skill/life/event_log.py` still rolls at 100 MiB, retains every `.2`, `.3`, ... generation, and exposes public `event_log_paths()` in oldest-to-newest canonical order.
- Mission View still projects 38 canonical event types. Raw sparse filtering must also include the five legacy aliases that canonicalize into projected types: `round.started`, `mission.started`, `mission.completed`, `mission.error`, and `life.team.waiting`.

This remains a cold-bootstrap/recovery observability correctness finding only. No claim is made that the normal online Mission View projection loses these events.

## `clean-os-g1-006` — literal source-shaped regression design

The existing `tests/core/test_mission_view.py` already has the exact helper style needed: direct JSONL fixture writes, `snapshot_mission_view(...)`, online legacy-alias projection, and Manager-intent routing assertions. The four retained-generation regressions can therefore be added without a new harness.

### 1. All retained generations and canonical order

`test_snapshot_bootstrap_replays_all_retained_generations_in_order`

- leave `mission-view.json` absent;
- put `life.manager.intent.completed` A in `events.jsonl.2`, e.g. `vertical=software`, `workflow_mode=staged`, `route=team`, `lifetime=bounded`;
- put later Manager intent B in `events.jsonl.3`, changing a visible routing field such as `workflow_mode=direct`;
- put only unrelated projected events in `.1` and current;
- call `snapshot_mission_view(tmp_path, session={}, daemon={}, roles=[], backlog=[], continuous={})`;
- assert the final routing reflects B. This proves both `.2 -> .3 -> .1 -> current` replay and that deep retained generations participate.

### 2. Projected event before the 8 MiB tail

`test_snapshot_bootstrap_keeps_projected_event_before_eight_mib_tail`

- place a Manager intent near the beginning of a retained generation;
- append more than `MISSION_BOOTSTRAP_MAX_BYTES` of valid non-projected JSONL after it;
- rebuild from no snapshot;
- assert the Manager route fields are recovered.

### 3. Legacy alias coverage in the sparse fast path

`test_snapshot_bootstrap_sparse_filter_includes_legacy_aliases`

- place `life.team.waiting` only in a deep retained generation;
- rebuild from no snapshot;
- assert Planner status/label matches the existing online alias regression (`waiting` / `Waiting on external work`).

This test catches a raw `rg` filter that lists only canonical names and therefore drops old spellings before `canonical_event_type()` can normalize them.

### 4. No-ripgrep fallback

`test_snapshot_bootstrap_rg_unavailable_falls_back_without_loss`

- force the optional sparse executable lookup unavailable;
- place a Manager intent only in `.2`;
- assert the sequential streaming fallback reconstructs the same routing state.

Malformed JSON and partial trailing-line tolerance should remain at least as permissive as the existing `_tail_jsonl()` path.

## Implementation boundary

The minimum layering is now clearer:

- reuse public `argus_skill.life.event_log.event_log_paths()` for retained-generation enumeration/order;
- keep projected-event filtering inside Mission View, because `_PROJECTED_EVENT_TYPES` and legacy-alias canonicalization are Mission View semantics, not generic event-log storage semantics;
- process one generation at a time in canonical order and reduce as a stream rather than materializing complete history;
- optional fast path: streaming `rg` over the fixed canonical projected names plus aliases, followed by JSON parse + the existing canonical predicate;
- fallback: sequential line-by-line Python scan with the same predicate.

At this public head, importing the public `event_log_paths()` helper from Mission View does not create an immediate top-level import cycle: the event-log module's Mission View import occurs locally inside append/projection.

## Density and multi-hundred-MiB performance stress

These are local synthetic microbenchmarks, not measurements of an Argus production filesystem. They measure only candidate cold-replay scan shapes and must not be generalized to end-to-end Mission View latency.

### Actual current Argus projected event names, ~128.5 MiB

Using the current 38 projected canonical names:

| Shape | Projected rows | streaming `rg` all-gen | sequential Python all-gen |
|---|---:|---:|---:|
| sparse (~0.2% projected) | 1,464 | 219.97 ms | 1,802.40 ms |
| dense (100% projected) | 712,000 | 2,082.08 ms | 1,893.51 ms |

Both complete methods recovered all projected rows. The sparse filter is substantially faster on the sparse shape; on the pathological all-projected shape, sequential Python is faster.

### Larger synthetic retained history

- sparse ~256 MiB: 2,734 projected rows; current two-tail shape recovered only 169, streaming `rg` recovered all in 304.65 ms, full Python recovered all in 3,868.69 ms.
- fully projected ~258.7 MiB: 1,420,000 projected rows; current two-tail shape recovered 87,838, streaming `rg` recovered all in 4,763.75 ms, full Python recovered all in 3,705.36 ms.

### Approximate density crossover, one ~32 MiB generation

| projected density | streaming `rg` | sequential Python | rg / Python |
|---:|---:|---:|---:|
| 0.1% | 58.6 ms | 478.5 ms | 0.12x |
| 1% | 50.2 ms | 461.6 ms | 0.11x |
| 5% | 54.6 ms | 500.5 ms | 0.11x |
| 10% | 89.5 ms | 454.0 ms | 0.20x |
| 20% | 171.2 ms | 472.6 ms | 0.36x |
| 50% | 308.1 ms | 481.7 ms | 0.64x |
| 100% | 513.7 ms | 470.0 ms | 1.09x |

Narrow conclusion: the sparse `rg` path remains the leading fast-path candidate for realistically sparse event histories, but it is **not universally faster**. The correctness design must keep a sequential fallback; an adaptive density heuristic is optional and currently untested. Since this is cold recovery, correctness should not be weakened to preserve the old fixed-tail latency.

## `clean-os-g1-005` — transition-lineage patch is source-compatible

Fresh current-main tracing confirms that both semantic handoff paths already possess a stable Manager intent ID before any replacement reset:

### Front door

- `prepare_manager_execution_task()` creates `intent-{time_ns}` before Manager classification.
- `PreparedManagerHandoff` retains that `intent_id`.
- `PreparedManagerHandoff.commit()` calls `Manager.commit_vertical_decision(... force_stage_reset=...)` but does not pass the intent identity onward.
- ordinary bounded `_manager_divide_user_task()` also uses this object, so an optional lineage parameter must be backward-compatible rather than replacement-only.

### Daemon boot

- `_rf_manager_divide_on_boot()` creates `intent-daemon-{time_ns}` before the decision.
- replacement backlog supersession already uses this same ID as `replacement_id`.
- after a successful continuous-state CAS, the Manager-completed event and persisted handoff identity also use the same ID.
- the call to `mgr.commit_vertical_decision(... force_stage_reset=replacement_intent, _lock_held=True)` still drops that identity before stage mutation.

### Stage state

Current path:

`Prepared/boot intent id` -> `commit_vertical_decision` -> `reset_stage_for_new_intent` -> `reset_stage_for_replacement_intent` or `rollback_stage` -> `_set_stage` -> `stage_history`

Current `stage_history` entry contains only `at`, `from_stage`, `to_stage`, `direction`, `reason`, `by` (+ optional skipped stages). No transition identity is present.

Minimal backward-compatible provenance patch:

- add optional `transition_id: str = ""` to `Manager.commit_vertical_decision` / locked helper;
- thread it to `reset_stage_for_new_intent`;
- thread it through replacement reset and completed-prior-run rollback into `_set_stage`;
- append `stage_history.transition_id` only when non-empty;
- front door supplies `PreparedManagerHandoff.intent_id` and daemon boot supplies the existing `intent-daemon-*` ID;
- internal Planner/Manager stage reconciliation and older call sites keep the default empty value unless they already have an appropriate durable intent identity.

This is provenance only. It does not authenticate or authorize a stage transition and must not be described as such.

A fresh call-site check found a normal continuous planning-cycle `commit_vertical_decision(...)` path that does not originate from a front-door/daemon handoff. Leaving the new parameter optional keeps that path unchanged and avoids inventing a fake lineage identity.

### Exact regression targets

1. front-door forced replacement records `PreparedManagerHandoff.intent_id` on its `direction=reset` history entry;
2. daemon-boot forced replacement records `intent-daemon-*` on its reset entry;
3. same-vertical/same-first-stage forced replacement still records a new `direction=reset` entry carrying the new transition ID;
4. ordinary/internal commit call sites with no supplied transition ID preserve the old history schema (no empty `transition_id` key);
5. future strict reconciliation must reject a route that appears correct when the qualifying reset belongs to a different transition ID.

## Candidate status

### `clean-os-g1-006` — strengthened, performance claim narrowed

Source-level correctness gap remains current. Literal test shape is now mapped onto existing test helpers, and multi-hundred-MiB stress shows a sparse-filter fast path is attractive but not universally faster. No upstream patch, production failure reproduction, or production filesystem benchmark has been performed.

### `clean-os-g1-005` — lineage seam strengthened

Existing front-door and daemon intent IDs can be threaded to stage history with a low-churn optional parameter. This improves recoverable provenance only; it does not replace the separate authority/CAS/fencing work developed in earlier clean runs.

## Exact continuation

1. Draft the minimum `_snapshot.py` iterator patch shape against current source: all-generation `event_log_paths()`, alias-safe streaming sparse filter, JSON/canonical predicate, sequential fallback, malformed/partial-line tolerance; benchmark one mixed `signal`-verbosity-like corpus rather than only synthetic extremes.
2. Map the transition-lineage regressions onto the exact existing tests in `tests/manager/test_pipeline_yield.py`, `tests/daemon/test_life_worker.py`, `tests/skills/test_verticals.py` / stage-machine tests, and verify all `commit_vertical_decision` callers compile with the optional parameter.
3. Keep `clean-os-g1-006` observability recovery and `clean-os-g1-005` protected-handoff authority/fencing as separate candidate branches; do not collapse either into a global PIPELINE_STATE writer refactor without independent evidence.

Frontier remains intentionally non-empty.