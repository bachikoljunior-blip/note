# Open Source Systems Scan — first-class fence schema, strict reset minting, and immutable backlog retry identity

Invocation started: 2026-08-27T12:58:47+09:00
Checkpointed: 2026-08-27T13:10:33+09:00

Frozen semantic tuple: `note@af32fdd18a9012f144c60ff5ec4935ebc1eac2f8 / control 11 / open_source config 5` (`DESIRED_STATE` blob `bf7b8c7f6971c0ec2f3fa7a8d53dca1f88ac50a3`, role-config blob `118f440957ba4654e804af902aa09a9224acca43`). The note head advanced after the semantic-freeze barrier; no newer control/config was adopted. Only own clean state and public sources were used. Public `lbx154/Argus` main was reverified at `33da786bbc6787a2eeb63a5f492498eae87c78c7`.

## 1. `handoff_fence` has a small source-compatibility surface, but every whole-state writer must understand it

`argus_skill/daemon/state.py` currently defines `ContinuousConfigState` with only `enabled`, `objective`, `open_ended`, `done_reason`, `done_at`, and `generation`. The exact source shows five reconstruction points that would otherwise erase any new fence:

1. `_read_continuous_state_unlocked()` constructs a fixed dataclass from those fields only;
2. `_continuous_state_reserve_text()` serializes a fixed subset for quota-reserve sizing;
3. `_write_continuous_config_unlocked()` rebuilds the complete JSON object from fixed parameters;
4. `write_continuous_config()`, `compare_and_swap_continuous_config()`, and `disable_continuous_config()` call that whole-object writer without any extension payload;
5. `_same_continuous_state()` manually compares every current field, including `generation` even though the dataclass marks generation `compare=False`.

Code search found direct `ContinuousConfigState(...)` construction only in `daemon/state.py` and daemon tests; production identity/lifecycle code consumes it by attribute/type rather than positional unpacking. Therefore adding an optional defaulted field is source-compatible at the observed constructor boundary, but persistence/CAS compatibility is **not automatic**.

Minimal first-class schema shape:

```text
ContinuousConfigState.handoff_fence: HandoffFenceV1 | None = None
```

with old JSON missing the key reading as `None`, and serialization omitting the key when `None` so legacy no-fence shape remains simple. A correct implementation must thread the field through the reader, reserve serializer, whole-state writer, public write/CAS/disable wrappers, and `_same_continuous_state()`.

### Safety invariant stronger than “preserve unknown field”

Blindly preserving a fence through every old writer is unsafe: a legacy caller can request `enabled=True`, and carrying the old fence into that state would create `enabled + handoff_in_progress`, defeating the disabled-fence invariant. The schema needs an explicit state invariant:

```text
handoff_fence != None  =>  enabled == False
```

and preferably `done_reason == ""` while the fence is an in-progress reconciliation checkpoint. Old/generic writers that encounter an active fence must not silently erase it and must not silently enable through it.

A narrow API migration is a tri-state fence argument (`UNSPECIFIED` = preserve current, `None` = explicitly clear, `HandoffFenceV1` = set/replace) plus validation before write. If `UNSPECIFIED` preserves an active fence and the caller asks to enable, the write fails closed. Semantic stop/supersession and successful handoff finalization explicitly clear; process-only stop may preserve according to the existing exact stop-reason policy. This makes accidental legacy behavior fail closed instead of converting a reconciliation checkpoint into an executable campaign.

`_continuous_state_reserve_text()` must include the fence too. The current 64 KiB minimum reserve is likely larger than a v1 fence, but reserve sizing is a durability contract and must follow the complete state rather than rely on today's minimum size.

### Concrete compatibility tests

- legacy JSON without `handoff_fence` -> `state.handoff_fence is None`;
- ordinary no-fence roundtrip remains equivalent;
- a fence roundtrips through read + a preserve-style read-modify-write without disappearing;
- CAS fails if all ordinary fields/generation match but the fence differs;
- generic enable while an active fence is merely preserved is rejected;
- explicit finalization can clear the exact expected fence and enable the target;
- a large fence participates in reserve sizing/quota-retry serialization;
- corrupted/unknown fence schema fails closed rather than being treated as no fence.

## 2. Authority receipt minting must not reuse prompt-facing stage helpers that deliberately fail open

The current `stage_machine._active_vertical_checklist_defs()` is intentionally a prompt/checklist convenience helper. On **any exception** it falls back to the research checklist. `current_stage()` also depends on that helper and falls back to the first stage when persisted state is missing/invalid for the active order. Those behaviors are useful for prompt liveness but are unsafe for minting `ManagerReconcileReceiptV1`: a broken/missing project-local data domain could otherwise be reinterpreted as research and accidentally produce a receipt for the wrong stage order.

The public tests reinforce the distinction: `resolve_vertical()` still has a legacy research fallback for an undecided/missing low-level state, while corrupt state raises. Therefore even `resolve_vertical()` alone is not strict enough for an authority mint gate when a persisted target is required.

The receipt mint gate should instead:

1. read the protected `PIPELINE_STATE` object directly;
2. require a non-empty persisted `vertical` field;
3. validate that exact value with `require_vertical(payload["vertical"], project_root)` so built-ins and existing project-local data domains are accepted but missing/invalid identities fail;
4. load exactly that vertical with `load_vertical(validated, project_root=project_root)`;
5. obtain its `vertical_checklist_stage_order()` and require a non-empty order;
6. inspect `payload["current_stage"]` directly rather than a fallback-returning `current_stage()` helper.

This is a new important refinement: **prompt robustness helpers and authority-validation helpers should not share fallback semantics.**

### Source-exact replacement-reset assertions

`reset_stage_for_replacement_intent()` delegates to `_set_stage(direction="reset", downgrade_downstream=True, legacy_rollback_history=True)`. `_set_stage` currently guarantees:

- target/current stage becomes the reset target;
- reset target status becomes `in_progress`, including same-stage reset;
- every downstream known stage with `done|ready|in_progress|skipped` becomes `pending`;
- one `stage_history` row with `direction="reset"` is appended;
- one legacy `rollback_history` row is appended using the same transition timestamp.

A conservative receipt-mint assertion can therefore require:

```text
persisted current_stage == strict_stage_order[0]
stages[first].status == "in_progress"
for every downstream known stage record:
    status in {"", "pending"}
stage_history[-1].direction == "reset"
stage_history[-1].to_stage == first
rollback_history[-1].to_stage == first
stage_history[-1].at == rollback_history[-1].at
stage_history[-1].from_stage == rollback_history[-1].from_stage
stage_history[-1].by == rollback_history[-1].rolled_back_by == expected Manager actor
```

The existing forced-replacement regression proves built-in `research` resets `review -> research`, reopens the first stage and downgrades downstream `plan`/`review`. Existing custom-domain tests prove project-local stage orders are a supported production shape. New receipt tests should cover both, plus same-stage reset and a deliberately missing/corrupt custom-domain definition that must **fail** rather than fall back to research.

After these checks pass, mint the canonical whole-object `PIPELINE_STATE` digest described in the predecessor run. If any strict-resolution or reset assertion fails, do not mint; re-enter Manager reconciliation.

## 3. `Backlog.creation_stamp` should be a narrow immutable retry identity, not a snapshot hash

Current `BacklogItem` has no immutable creation identity field. `from_jsonable()` supplies backward-compatible defaults for every field, so adding `creation_stamp: str = ""` is mechanically compatible for legacy rows.

The important current behaviors are:

- `Backlog.add()` appends without checking whether the ID already exists;
- `add_many()` explicitly rejects duplicate IDs in the batch and against existing rows;
- `Backlog.update()` performs generic `setattr()` for **any existing attribute**, meaning it can currently mutate `id`, `ts`, and any future `creation_stamp` unless guarded;
- `_load()` does not reject a file that already contains duplicate IDs;
- whole-backlog writes still use `_atomic_rewrite_jsonl()` = temp file + `os.replace()` without file or parent-directory fsync.

Therefore exact handoff recovery needs both identity uniqueness and immutability:

```text
BacklogItem.creation_stamp: str = ""  # legacy rows remain unstamped
immutable generic-update fields >= {id, ts, creation_stamp}
```

Do **not** reconstruct a stamp from the current row on retry. Legitimate execution mutates objective/Manager decision/status/attempt/outcome/etc. and may reuse the stable item ID through iteration. The stamp is created once from the frozen handoff creation descriptor and remains unchanged.

### Narrow exact-insert transaction

A dedicated `ensure_operator_priority_item_exact(...) -> (BacklogItem, inserted: bool)` should run under the existing cross-process backlog lock:

1. collect all existing rows with the pre-reserved target ID;
2. more than one -> fail closed (legacy duplicate corruption is ambiguous);
3. exactly one -> require a non-empty expected stamp and exact equality with stored `creation_stamp`; mismatch or unstamped legacy row fails closed; match returns the **current mutated row** with `inserted=False`;
4. none -> compute operator-priority and first `ts` inside the same lock, assign the non-empty creation stamp, append once, validate dependency cycles/ID uniqueness, durably save, return `inserted=True`.

The caller emits queued/task-added observability only when `inserted=True`, so crash recovery does not duplicate semantic events.

Because `_atomic_rewrite_jsonl()` rewrites the entire backlog, making only this one insert fsync-durable is not enough: a subsequent ordinary backlog rewrite before final continuous enable could weaken the persistence ordering again. The candidate therefore still prefers hardening the shared backlog rewrite primitive to `flush+file fsync -> os.replace -> parent-directory fsync`, with performance cost measured separately.

## 4. Candidate refinement

`clean-os-g1-005` is now:

**disabled first-class handoff fence with fail-closed enable invariant + CAS-visible fence state + strict no-fallback Manager reset mint gate + canonical whole protected-state receipt + pre-reserved mission ID + immutable creation stamp + exact idempotent operator-priority Backlog insertion + durable whole-backlog rewrite + current-state reconcile/rearm + derivative route-v4 classification.**

This remains a source-derived adaptation candidate. No Argus mutation, live daemon fault injection, unauthorized state change, or production benchmark was performed.

## Exact continuation

1. Enumerate every production `write_continuous_config` / `compare_and_swap_continuous_config` / `disable_continuous_config` call site and classify its required active-fence behavior as `preserve`, `explicit cancel`, `finalize`, or `refuse`; use that to define the exact tri-state API without accidental semantic resurrection.
2. Turn the strict reset mint gate into executable regression pseudocode/tests for built-in research, same-first-stage reset, and a project-local data domain; explicitly test that `_active_vertical_checklist_defs`/legacy fallback cannot mint authority when strict domain resolution fails.
3. Search all production `Backlog.update` call sites for intentional `id` or `ts` mutation before hardening `{id, ts, creation_stamp}`; then specify the exact `ensure_operator_priority_item_exact` method signature and its event-emission integration.
4. Add the real-Backlog second-replace-failure regression from the predecessor run, now asserting fence survival, strict receipt validation, one physical target ID, stable creation stamp, `inserted=False` on retry, and final enable only after durable mission persistence.
5. Keep external/admin `PIPELINE_STATE` writer fencing and global JSON-state CAS as a separate candidate branch; do not broaden this handoff-recovery result into a claim about all Argus writers.
