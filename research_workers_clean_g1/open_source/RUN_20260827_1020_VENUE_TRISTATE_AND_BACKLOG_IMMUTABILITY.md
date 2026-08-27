# Open Source Systems Scan — Target-venue tri-state contract and Backlog identity immutability

Invocation started: 2026-08-27T10:02:23+09:00
Checkpointed: 2026-08-27T10:20:00+09:00

Frozen semantic tuple remains `note@0690108bdb37bbcf3ca1ea9f7a032ca1706ea9b9 / control 11 / open_source config 5 / config blob 118f440957ba4654e804af902aa09a9224acca43`. Only own clean state and public `lbx154/Argus` source were used.

## 1. Full production-call scan found no legitimate `Backlog.update(... id=...)` or `ts=...`

The current public Argus source search for `backlog.update`/Backlog lifecycle mutations surfaced the production call sites in:
- `apps/_life_actions.py`;
- `life/chat/router.py`;
- `manager/dispatch.py`;
- `life/supervisor/_core.py`;
- `life/supervisor/_mission_execution.py`;
- `_mission_execution_runtime.py`;
- `_mission_execution_settlement.py`;
- `_planning_cycle_verdict.py`;
- `_planning_cycle_enqueue.py`;
- `_planning_cycle.py`;
- `backlog_guard.py`.

Every inspected production `backlog.update(...)` mutates lifecycle/task fields such as `status`, `title`, `objective`, `manager_decision`, `started_ts`, `finished_ts`, `running_owner`, questions, outcomes, replan counters, or iteration state. **No inspected production caller deliberately mutates `BacklogItem.id` or the creation timestamp `ts`.**

Representative uses include:
- CLI/chat cleanup changes `title` or `status`;
- Manager dispatch clears `pending_question`;
- backlog guard replaces a Manager-cleaned `objective` and routing evidence;
- mission runtime/settlement moves status and start/finish timestamps;
- planner reconciliation changes outcome/replan counters.

This supports making `id` and creation `ts` unconditionally immutable in generic `Backlog.update()`. `started_ts` / `finished_ts` remain mutable lifecycle fields and must not be confused with creation `ts`.

Proposed compatibility rule:

```python
_IMMUTABLE_UPDATE_FIELDS = {"id", "ts", "creation_stamp"}
```

`Backlog.update(item_id, **changes)` validates all keys before mutating a row. Any attempt to write one of those fields raises/fails before `_save()`, even when the proposed value equals the current value. This avoids treating generic update as a hidden identity-rewrite API and leaves the exact-insert/recovery primitive as the only authority for `creation_stamp`.

Tests:
1. `update(id=...)` rejects and leaves the JSONL byte-identical;
2. `update(ts=...)` rejects and leaves bytes unchanged;
3. `update(creation_stamp=...)` rejects;
4. mutable `started_ts` / `finished_ts` continue to work;
5. legacy rows with no stamp remain readable.

## 2. Venue needs presence information, not just a string

Current Manager routing already has a useful precedent: `live_view_decided` separately records whether a field was actually answered. `target_venue` needs the same distinction.

Current behavior collapses three states:
- Manager omitted `TARGET_VENUE`;
- Manager explicitly wrote `TARGET_VENUE=none` (which `read_optional` converts to empty string);
- non-research route where venue is inapplicable.

All currently become `decision.target_venue == ""`. `_commit_vertical_decision_locked()` then passes `decision.target_venue or None`, so `persist_vertical()` cannot tell "preserve" from "clear". This is why stale venue can survive route changes.

Minimal typed extension:

```python
@dataclass
class VerticalDecision:
    ...
    target_venue: str = ""
    target_venue_decided: bool = False
```

Parsing:
- `target_venue_decided = "target_venue" in obj`;
- `read_optional` already normalizes `none|null|n/a|-|(none)` to empty string;
- if route is non-research, semantic venue is empty regardless of the raw answer.

Prompt/active contract:
- render current research venue in the active route contract (`target_venue=AAAI 2026` or `target_venue=none`);
- tell Manager: omit `TARGET_VENUE` to keep the current research venue unchanged; write `TARGET_VENUE=none` only to clear an existing research venue; write a value only when operator evidence sets/replaces it; never infer a venue.

## 3. Persistence should distinguish preserve / clear / set explicitly

Avoid silently changing the public meaning of `persist_vertical(... target_venue="")` without a contract. A narrow API is clearer:

```python
def persist_vertical(
    ...,
    target_venue: str | None = None,
    clear_target_venue: bool = False,
) -> None:
```

Semantics:
- `target_venue is None` and `clear_target_venue=False` => preserve current raw field;
- nonempty `target_venue` => normalized display string is written;
- `clear_target_venue=True` => remove `target_venue` from pipeline state;
- passing both clear + nonempty target is invalid/fail-closed.

Manager commit policy:
- next vertical != `research` => always `clear_target_venue=True`;
- research + `target_venue_decided=True` + nonempty => set;
- research + `target_venue_decided=True` + empty => clear;
- research + `target_venue_decided=False` => preserve.

This preserves the useful existing behavior for a supplemental same-research handoff that does not restate the venue, while giving explicit operator/Manager intent a real clearing path and preventing venue leakage when leaving research.

## 4. Regression matrix for venue state

Four minimum route-state regressions:

### A. Preserve on supplemental same-research handoff
1. persist `research`, venue `AAAI 2026`;
2. Manager returns same research route without `TARGET_VENUE`;
3. assert decision `target_venue_decided=False`;
4. commit;
5. persisted venue remains `AAAI 2026`.

### B. Explicit clear
1. persist research + AAAI;
2. Manager states `TARGET_VENUE=none`;
3. assert `target_venue_decided=True`, value empty;
4. commit;
5. raw `target_venue` key removed; semantic fingerprint venue empty.

### C. Leaving research clears venue
1. persist research + AAAI;
2. Manager changes route to software;
3. commit;
4. raw venue key removed, even though the non-research decision never states a venue.

### D. Re-entering research does not resurrect stale venue
1. research + AAAI;
2. change to software (must clear);
3. later change to research without venue;
4. assert no AAAI venue reappears.

Additional parser regression: a named-line footer that omits `TARGET_VENUE` must be distinguishable from one that says `TARGET_VENUE=none`; JSON `{"target_venue": null}` should count as explicitly decided-clear for compatibility.

## 5. Route fingerprint v4 should be produced by a semantic-route reader

Rather than scatter conditionals among identity writers, add one pure `canonical_route_identity(project_root)` reader whose output is the audit object and whose compact sorted JSON is hashed when needed.

Rules from current Manager semantics:
- canonical `vertical` first;
- `workflow_mode` normalized to direct/staged;
- `domain` only meaningful for research; otherwise empty;
- research target only for a target-capable vertical;
- research direction only for research; otherwise empty;
- target venue only for research, normalized with `_normalize_venue_key`; otherwise empty;
- `current_stage` excluded.

Call it after Manager commit, not before, so the identity describes the route actually made durable. `manager-handoff.json` v4 stores both the canonical object and hash for auditability.

This reader also prevents stale legacy raw keys from creating false route drift in non-research routes, while the venue clear regressions ensure new commits stop producing that stale state.

## Candidate refinement

`clean-os-g1-005` now has two newly source-justified hardening details:
- backlog creation identity can safely protect `id`, creation `ts`, and `creation_stamp` from all generic updates; no legitimate production update of `id`/`ts` was found at the verified public head;
- target venue must become an explicit preserve/clear/set route field before it is trusted as part of restart identity. Same-research omission preserves; explicit `none` clears; leaving research clears; v4 identity reads canonical semantic state after commit.

No live mutation or performance benchmark was performed.

## Exact continuation

1. Specify concrete `CreationStampV1` and `HandoffFenceV1` parser/serializer validation limits and fail-closed error types.
2. Build the current process-control `reconcile_or_rearm` matrix for Web start, daemon boot, immediate/scheduled upgrade, replacement, and operator-decision projection, with exact current-state CAS rules.
3. Design the real Backlog final-continuous-replace fault-injection regression and one-time event assertion.
4. Benchmark durable Backlog whole-file rewrite at representative queue sizes before recommending global file+directory fsync as default.
5. Keep external/admin PIPELINE_STATE writer fencing separate.
