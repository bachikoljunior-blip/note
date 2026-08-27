# open_source clean-g1 run — all-generation Mission View recovery + Manager transition lineage

Observed invocation start: 2026-08-27T22:01:55.724151+09:00

## Frozen semantic control tuple

- note main SHA at pre-semantic freeze: `5c2d85296bce985c3a36625d9e6565d43a6c7903`
- `automation_control/DESIRED_STATE.json`: control revision `12`, blob `5c91671e1470d0fa4e2a53f918493004dd3750c3`
- `automation_control/roles/open_source.json`: config revision `5`, blob `118f440957ba4654e804af902aa09a9224acca43`
- semantic freeze was established only after a second SHA-only note-main lookup returned the same SHA.
- no `research_feedback_clean_g1/open_source/FEEDBACK.json` existed at the frozen SHA.
- no O/O-derived state, other worker state, downstream comparator/integrator/index/feed/audit semantics, legacy/pre-independence research, or shared aggregate execution ledger was read.
- note main advanced after the semantic barrier; newer control was not adopted in this physical invocation.

## Public source snapshot

Repository: `lbx154/Argus`

Current public main observed twice in this invocation: `ea50b6a9169f3d5885d15f3f13a28543ae9989a8`.

This is 5 commits ahead of the prior clean open-source checkpoint head `a8a74029ae4a8f0bf488854b9e5f75ec0843f877`. The five-commit compare did not modify Mission View `_snapshot.py` / `_view_state.py`, event-log rollover, or life-memory history enumeration, so candidate `clean-os-g1-006` remains source-current at this observed head.

## Finding 1 — `clean-os-g1-006` is now source-shaped enough for a minimal patch

At current public main:

1. `argus_skill/core/mission_view/_snapshot.py::_bootstrap_view()` still replays exactly two files: `events.jsonl.1`, then live `events.jsonl`.
2. `argus_skill/core/mission_view/_view_state.py::_tail_jsonl()` reads at most the final 8 MiB of each selected file before JSON decoding/projected-event filtering.
3. `argus_skill/life/event_log.py` rolls the canonical log at 100 MiB and explicitly retains every generation: `.2`, `.3`, ... (oldest-to-newest), then `.1`, then live. Its public `event_log_paths()` already returns that exact canonical order.
4. `argus_skill/life/memory.py` independently has `_jsonl_history_paths()` / `_read_jsonl_tail_history()` with the same all-generation semantics and an optional ripgrep fast path. This independently confirms that deep retained-generation reads are an intended storage contract, not an invented ordering.
5. `argus_skill/webapi/artifacts.py` already uses `_read_jsonl_tail_history()` across all retained generations to recover old `manager.live_view.updated` state. Deep retained-event recovery is therefore already a production pattern inside Argus.
6. Mission View's `_PROJECTED_EVENT_TYPES` currently contains 38 canonical event types. `canonical_event_type()` also maps five legacy aliases into projected types (`round.started`, `mission.started`, `mission.completed`, `mission.error`, `life.team.waiting`). Any raw sparse filter must include those aliases before applying the canonical predicate; filtering only canonical spellings would regress old-log recovery.

### Minimal non-circular helper choice

The smallest patch at this source snapshot is to reuse `argus_skill.life.event_log.event_log_paths()` from Mission View rather than duplicate the private `life.memory._jsonl_history_paths()` helper.

Observed import layering does not create an immediate module-load cycle at this commit: `life.event_log` has no top-level Mission View import; its Mission View import is local inside `JsonlEventSink._append()`. `life.__init__` eagerly imports memory/failure-experience but no Mission View dependency was found in that path. If maintainers prefer a stricter architectural layer boundary, the enumeration helper can later be extracted to a neutral storage module, but that is not required for the minimum correctness patch.

### Proposed cold-bootstrap iterator

For each `event_log_paths(root / "events.jsonl")` path in canonical order:

- fast path: stream `rg` matches for the fixed set of 38 projected canonical types plus legacy aliases whose canonical targets are projected;
- parse each matched line as JSON and run the existing `canonical_event_type(event["type"]) in _PROJECTED_EVENT_TYPES` predicate before reducing it;
- fallback when `rg` is absent/fails: sequentially stream the entire generation line-by-line with the same canonical predicate;
- reduce events as a stream rather than materializing the full projected history;
- preserve malformed/partial-line tolerance.

Use one scan per generation rather than one multi-file subprocess so `.2 -> .3 -> ... -> .1 -> current` reduction order is explicit and deterministic.

## Synthetic performance check — all 38 projected types

This is a local synthetic microbenchmark, not an Argus production-filesystem result.

Shape:

- four retained files in canonical order: `.2`, `.3`, `.1`, live;
- ~12 MiB each, ~48.0 MiB total;
- 297 projected events sparsely interleaved with non-projected noise;
- projected events span all 38 current canonical projected types;
- sparse `rg` regex also included the five currently relevant legacy aliases;
- seven timed runs per method.

Observed medians:

| Method | Recovered projected events | Median | Range |
|---|---:|---:|---:|
| current Mission View shape: final 8 MiB of `.1` + live | 98 / 297 | 206.08 ms | 195.93–233.05 ms |
| full Python JSON scan of all 4 generations | 297 / 297 | 397.17 ms | 391.59–408.04 ms |
| per-generation sparse `rg` + JSON/canonical predicate | 297 / 297 | 48.96 ms | 44.21–89.57 ms |

Interpretation is deliberately narrow: on this synthetic sparse corpus, an all-generation sparse scan recovered the complete projected history and was much faster than brute-force Python full parsing; it was also faster than the current incomplete two-tail Python path. This does **not** establish production latency, filesystem behavior, or worst-case performance when projected events are dense. It is enough to keep sparse all-generation replay as the leading implementation candidate instead of assuming correctness requires an expensive full JSON parse.

## Exact regression tests for `clean-os-g1-006`

1. `test_snapshot_bootstrap_replays_all_retained_generations_in_order`
   - no `mission-view.json`;
   - old Manager intent A only in `events.jsonl.2`;
   - newer Manager intent B in `.3`;
   - unrelated projected events in `.1` and live;
   - assert final routing reflects B, proving both deep-generation coverage and oldest-to-newest ordering.

2. `test_snapshot_bootstrap_keeps_projected_event_before_eight_mib_tail`
   - projected Manager intent near the beginning of one selected generation;
   - >8 MiB of non-projected bytes after it;
   - assert the route/vertical/workflow fields still reconstruct.

3. `test_snapshot_bootstrap_sparse_filter_includes_legacy_aliases`
   - put a legacy `mission.completed` or `life.team.waiting` event in a deep generation;
   - assert the reducer sees the canonical projected event exactly as the current `_tail_jsonl` path does.

4. `test_snapshot_bootstrap_rg_unavailable_falls_back_without_loss`
   - force the optional fast path unavailable;
   - assert identical projected state from sequential fallback.

5. Keep existing malformed JSON / partial trailing-line tolerance unchanged.

Scope: this is a **cold-bootstrap/recovery observability correctness** candidate. Normal online Mission View projection writes each accepted projected event immediately and has not been shown here to lose those events.

## Finding 2 — `clean-os-g1-005` transition lineage can reuse existing Manager intent IDs

The separate continuous-handoff candidate remains live, and current public main now gives an exact low-churn lineage patch shape.

### Front door

`prepare_manager_execution_task()` creates a stable `intent-{time_ns}` before Manager classification and stores it on `PreparedManagerHandoff`. The same ID is already used as replacement identity when superseding pending backlog work.

But `PreparedManagerHandoff.commit()` calls `manager.commit_vertical_decision(... force_stage_reset=...)` without passing that intent identity.

### Daemon boot

`_rf_manager_divide_on_boot()` independently creates `intent-daemon-{time_ns}` before boot classification. It already uses that ID for Manager events, pending-backlog supersession, and the durable Manager handoff identity. But its `mgr.commit_vertical_decision(... force_stage_reset=...)` call likewise does not pass the intent ID into stage state.

### Stage state

`Manager.commit_vertical_decision()` -> `vertical_select.reset_stage_for_new_intent()` -> `reset_stage_for_replacement_intent()` / `rollback_stage()` -> `_set_stage()` currently loses the identity. `_set_stage()` appends only `{at, from_stage, to_stage, direction, reason, by}` (plus optional skipped stages) to `stage_history`.

Minimal backward-compatible patch candidate:

- add optional `transition_id=""` to `PreparedManagerHandoff.commit` -> `Manager.commit_vertical_decision` -> `reset_stage_for_new_intent`;
- front door supplies `PreparedManagerHandoff.intent_id`;
- daemon boot supplies its already-existing `intent-daemon-*` ID;
- thread the optional ID through reset and new-intent rollback primitives to `_set_stage()`;
- append `stage_history.transition_id` only when non-empty, preserving legacy readers.

This does not by itself authorize a transition. It creates provenance so a later strict reconciliation receipt can prove that the reset visible in protected pipeline state was caused by **this** Manager handoff rather than a different concurrent/stale intent.

Exact regression targets:

1. front-door forced replacement records the `PreparedManagerHandoff.intent_id` on the reset history entry;
2. daemon-boot forced replacement records the `intent-daemon-*` ID;
3. same-vertical/same-first-stage replacement still records a new `direction=reset` entry with the new transition ID;
4. later strict receipt logic must reject a route that looks correct when the latest qualifying reset belongs to a different transition ID.

## Current candidate status

### `clean-os-g1-006` — strengthened

Candidate: all-retained-generation sparse projected-event Mission View bootstrap, using canonical retained-log order and alias-safe filtering, with sequential fallback.

Evidence level: source-level correctness gap + source-shaped implementation precedent + local synthetic performance evidence. No live production failure reproduction and no upstream patch/benchmark yet.

### `clean-os-g1-005` — still live, narrowed

Candidate family remains the protected continuous handoff/reconciliation design developed in prior clean runs. This run adds an exact transition-lineage seam using already-existing Manager intent IDs; it does not widen prior causal claims.

## Exact continuation

1. Turn the four `clean-os-g1-006` tests above into literal source-shaped pytest bodies against current Argus test helpers and inspect whether a streaming `rg` helper belongs locally in Mission View or should be a small public event-log iterator.
2. Benchmark a denser projected-event corpus and a multi-hundred-MiB corpus so the sparse fast-path recommendation is not based only on one 48 MiB sparse shape; separately measure no-`rg` sequential fallback.
3. Trace every `PreparedManagerHandoff.commit()` / daemon boot commit call so adding optional `transition_id` cannot break bounded/nonreplacement paths, then map the four transition-lineage regressions onto existing `test_pipeline_yield.py`, `test_life_worker.py`, and stage-machine tests.
4. Keep global/external `PIPELINE_STATE` writer fencing as a separate candidate branch; do not collapse it into these two narrower fixes.

Frontier remains intentionally non-empty.