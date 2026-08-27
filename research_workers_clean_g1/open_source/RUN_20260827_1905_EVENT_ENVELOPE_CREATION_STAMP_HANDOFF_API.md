# Open Source Systems Scan — generic event identity, immutable backlog creation stamp, and exact handoff API

Invocation started: 2026-08-27T18:59:03+09:00
Checkpointed: 2026-08-27T19:05:00.477671+09:00

Semantic authority is frozen at `note@4b19551018936e5b713eea90f7b3b87e3ff2f8c4 / control 12 / open_source config 5 / config blob 118f440957ba4654e804af902aa09a9224acca43`. This run continues `RUN_20260827_1812_INTENT_EVENT_ONCE_MISSIONSPEC.md`. The note repository advanced after semantic freeze; no later control/config semantics were adopted. Public source was refreshed independently: `lbx154/Argus` current `main` is `8a867e7b45f863a9cd4e79e4f6d21ca7a2009e48`, 27 commits ahead of the prior pinned source. The relevant event, backlog, daemon-state and front-door surfaces below were re-read at that exact public commit.

## 1. `event_id` belongs in the generic event envelope, not only `life.planner.task_added`

The current event compatibility surface is more favorable than the previous run assumed.

Frontend `eventKey(event)` already treats `event.event_id` as the highest-priority replay identity, before `id`, `seq` or `_offset`. The shared `EventMsg` wire type has an index signature, so an extra `event_id` already survives TypeScript structurally. Backend Mission View `_event_id()` likewise prefers `event_id`, then `id`, then hashes the complete event. Both frontend and backend timeline/role-work reducers therefore already become replay-idempotent when an explicit stable `event_id` is present.

For `life.planner.task_added`, both reducers independently upsert DAG state by `item_id`, so adding a stable event identity does not alter DAG semantics; it only makes timeline/role-work identity exact across retry/replay. No Mission View reducer change is required for deduplication.

The event payload validator is also permissive: it validates declared properties and required fields but does not reject unknown fields. `normalize_event_envelope()` preserves arbitrary mapping fields. Therefore adding `event_id` only to the `life.planner.task_added` payload schema would work, but would encode the wrong abstraction: replay identity is already generic across event types.

Least-disruptive schema direction:

```text
Generic envelope:
  event_id?: non-empty string

Frontend EventMsg:
  event_id?: string

Backend validate_event_envelope:
  if event_id is present, require non-empty string

Event-specific payload schemas:
  unchanged unless a specific event imposes stronger identity semantics
```

This avoids a payload-schema version bump for `life.planner.task_added`, keeps existing generated event interfaces valid via `EventMsg`, and documents the identity contract at the layer where both frontend and backend already consume it. The current explicit event-ID candidate remains:

```text
planner-task-added:v1:<item_id>:<sha256(creation_stamp)>
```

A regression should feed the same `life.planner.task_added` twice with the same `event_id` but different replay offsets/timestamps and assert one DAG node, one timeline row and one role-work row in both Python and TypeScript Mission View implementations.

## 2. Current `BacklogItem` migration shape supports a backward-compatible immutable `creation_stamp`

At current Argus main, `BacklogItem.from_jsonable()` reconstructs every field explicitly and uses defaults for fields absent from older rows. `Backlog.update()` still performs generic `setattr()` for any existing dataclass attribute. `Backlog.add()` still blindly appends one item, while `add_many()` rejects duplicate IDs against both the batch and existing backlog. `_atomic_rewrite_jsonl()` still writes a sibling temp file and `os.replace()`s it without explicit file fsync or parent-directory fsync.

A backward-compatible `creation_stamp` can therefore be introduced as an appended dataclass field with default `""` and loaded as:

```python
creation_stamp=str(row.get("creation_stamp", ""))
```

Appending the field rather than inserting it among required positional fields avoids changing positional construction compatibility. Legacy rows remain readable and behave exactly as before for ordinary scheduling/update paths.

The guard must be stronger than deserialization compatibility:

```text
immutable generic-update fields = {id, ts, creation_stamp}
```

`Backlog.update()` should reject attempts to mutate any of those fields. No current observed production caller requires changing `id` or initial `ts`; `creation_stamp` is definitionally immutable. Existing mutable fields such as objective, manager_decision, status, attempt/outcome and iteration state remain unaffected.

Exact recovery must not opportunistically stamp a legacy row. For a pre-reserved target ID:

```text
ID absent
  -> insert one new stamped row

exactly one row with same ID and same non-empty creation_stamp
  -> return current row unchanged, inserted=False

same ID with empty legacy stamp
  -> fail closed; provenance cannot be inferred safely

same ID with different stamp
  -> fail closed

duplicate physical rows with same ID
  -> fail closed; existing state is ambiguous
```

Ordinary `Backlog.add()` should independently gain global ID uniqueness, matching the stricter behavior already present in `add_many()` and plan-revision insertion. The idempotent exception belongs only in a dedicated recovery primitive.

The source-shaped signature is now:

```python
@dataclass(frozen=True)
class ExactBacklogInsertResult:
    item: BacklogItem
    inserted: bool

class Backlog:
    def ensure_operator_priority_item_exact(
        self,
        *,
        mission_spec: OperatorPriorityMissionSpecV1,
        creation_stamp: str,
    ) -> ExactBacklogInsertResult:
        ...
```

Inside one existing backlog lock it must perform ID collision validation, compute first priority from the current pending queue, generate first `ts`, construct the row with the immutable stamp, validate dependencies, and durably rewrite. Retry returns the persisted row without recomputing priority/time and without emitting another task-added observable.

Because every later Backlog mutation rewrites the whole file, hardening only this insert is insufficient for a power-loss ordering claim. If final continuous enable is conditioned on durable mission presence, the shared `_atomic_rewrite_jsonl()` must be strengthened to `flush -> file fsync -> os.replace -> parent-directory fsync`, or the guarantee must explicitly remain process-crash-only rather than power-loss durable.

## 3. Exact first-class handoff state and CAS APIs

Current `ContinuousConfigState` contains only `enabled/objective/open_ended/done_reason/done_at/generation`; `_same_continuous_state()` compares exactly those fields and reserve sizing serializes the same state. Therefore `handoff_fence` must be a first-class field everywhere: dataclass, reader, writer, reserve serialization and CAS equality. An ad-hoc JSON key would be dropped by the next ordinary write.

A minimal state shape is:

```python
@dataclass(frozen=True)
class HandoffFenceV1:
    schema_version: int
    intent_id: str
    origin: Literal["front_door", "daemon_boot"]
    dispatch_mode: Literal["operator_priority_backlog", "continuous_provider_seed"]
    source_generation: int
    source_objective: str
    target_objective: str
    source_route_fingerprint: str
    target_route_fingerprint: str
    replacement_reset_required: bool
    root_task_id: str
    creation_stamp: str
    mission_spec: dict[str, Any] | None
    manager_receipt: dict[str, Any] | None

@dataclass(frozen=True)
class ContinuousConfigState:
    ...
    handoff_fence: HandoffFenceV1 | None = None
```

Hard invariant: `handoff_fence is not None -> enabled is False`. Any generic writer asked to enable while preserving an active fence must refuse rather than create `enabled + handoff_in_progress`.

### `begin_handoff`

```python
def begin_handoff(
    life_dir: Path,
    *,
    expected: ContinuousConfigState,
    fence: HandoffFenceV1,
) -> ContinuousConfigState | None:
    ...
```

CAS tuple:

```text
expected = exact current ContinuousConfigState, including generation and fence=None
new      = enabled=False
           objective=expected.objective
           open_ended=expected.open_ended
           done_reason=""
           generation=expected.generation+1
           handoff_fence=fence(source_generation=expected.generation, ...)
```

The source objective remains the top-level disabled objective; the target lives inside the fence until Manager reconciliation is proven. This prevents an uncommitted target from masquerading as the current campaign while preserving all crash-recovery inputs.

### `record_manager_receipt`

```python
def record_manager_receipt(
    life_dir: Path,
    *,
    expected: ContinuousConfigState,
    receipt: ManagerReconcileReceiptV1,
) -> ContinuousConfigState | None:
    ...
```

Preconditions before CAS are strict direct reads, not fallback helpers:

- active fence exists and `receipt.intent_id == fence.intent_id`;
- persisted route semantically equals target route fingerprint;
- exact vertical/domain loads successfully without research fallback;
- if replacement reset is required, current first stage is actionable, no downstream stage remains done/ready/in_progress/skipped, and the newest matching reset-history row carries `transition_id == fence.intent_id`;
- canonical SHA-256 of the complete parsed protected pipeline object is captured after those checks;
- project-local/adapted domain definition digest is captured where applicable.

CAS tuple:

```text
expected = exact disabled fence state
new      = same disabled state
           generation += 1
           handoff_fence.manager_receipt = receipt
```

If a newer semantic command changed the continuous state, this CAS fails. Do not compensate by blindly replaying the old Manager commit.

### `finalize_or_reconcile`

```python
class HandoffResolution(StrEnum):
    FINALIZED = "finalized"
    RECONCILE_REQUIRED = "reconcile_required"
    SUPERSEDED = "superseded"
    REFUSED = "refused"


def finalize_or_reconcile(
    mem: Any,
    *,
    expected: ContinuousConfigState,
    current_route_fingerprint: str,
    current_pipeline_digest: str,
) -> HandoffResolution:
    ...
```

Decision table:

```text
no active fence
  -> REFUSED / nothing to finalize

continuous state no longer equals expected fence state
  -> SUPERSEDED; re-read current authority

receipt missing
  -> RECONCILE_REQUIRED

current protected pipeline digest != receipt.pipeline_digest
  -> RECONCILE_REQUIRED

current route == source route and target receipt is not valid
  -> RECONCILE_REQUIRED; rerun Manager on fence.target_objective

current route neither source nor target
  -> RECONCILE_REQUIRED / fail closed; do not guess

receipt valid and dispatch_mode == operator_priority_backlog
  -> ensure_operator_priority_item_exact
  -> append task-added with append_event_once(stable event_id)
  -> exact final CAS

receipt valid and dispatch_mode == continuous_provider_seed
  -> exact final CAS
```

Final CAS tuple:

```text
expected = exact latest disabled fence state after all required durable side effects
new      = enabled=True
           objective=fence.target_objective
           open_ended=resolved target policy
           done_reason=""
           generation=expected.generation+1
           handoff_fence=None
```

Every exception or ambiguous storage result must be followed by readback of the current continuous generation/fence rather than inference from the exception class. This matches Argus's existing distinction between pre-replace and post-replace continuous-write failures.

## 4. Current public main moved, but the candidate remains applicable

Argus public main advanced from the prior pinned `7cb5546d...` to `8a867e7b...` by 27 commits. The changed set includes event schemas, `life/memory.py`, Manager stage handling and front-door code. Re-reading the exact current files found that the target surfaces still have the relevant contracts:

- `life.planner.task_added` remains a known persisted signal event;
- no generic envelope `event_id` contract exists, while Mission View already consumes it generically;
- `BacklogItem` still has no creation stamp;
- `Backlog.add()` remains duplicate-permissive and `Backlog.update()` remains generic-setattr;
- `_atomic_rewrite_jsonl()` still lacks explicit fsyncs;
- `ContinuousConfigState` still has no fence and CAS equality still covers only the legacy fields;
- `manager_continuous_handoff()` still performs Manager route/replacement/backlog/persist side effects inside `compare_and_swap_continuous_config(... before_write=_commit)` before the final continuous replacement.

Therefore the candidate was not invalidated by the public-source advance. The exact code surface changed materially elsewhere, so implementation must rebase on `8a867e7b...` rather than the prior source commit.

## Candidate update

`clean-os-g1-005` is now source-shaped at all three formerly open compatibility boundaries: **event identity should be generic envelope metadata because both Mission View implementations already consume it generically; `creation_stamp` can migrate as an appended optional dataclass field while exact recovery fails closed on unstamped/conflicting IDs and generic updates protect immutable creation identity; and the shared handoff can be expressed as three exact continuous-state CAS primitives with a first-class disabled fence, strict readback receipt and finalization only after durable mission/event side effects.**

This remains an unimplemented adaptation proposal, not a measured Argus improvement.

## Exact continuation

1. Inspect current `PreparedManagerHandoff.commit()` and daemon boot Manager divide at `8a867e7b...` to freeze the exact `transition_id` plumbing and ensure the same `HandoffFenceV1` can begin before every Manager side effect in both origins.
2. Inspect all current production `write_continuous_config` / `disable_continuous_config` / CAS callers and classify their active-fence behavior as `PRESERVE`, `CANCEL`, `FINALIZE`, or `REFUSE`; update the earlier matrix against the new public main.
3. Convert the generic event identity proposal into literal Python/TypeScript regression tests and decide whether `event_id` should be generated by `new_event()` only when explicitly supplied or remain caller-supplied for deterministic retries.
4. Keep global/external protected `PIPELINE_STATE` writer fencing separate from this handoff-local candidate.
