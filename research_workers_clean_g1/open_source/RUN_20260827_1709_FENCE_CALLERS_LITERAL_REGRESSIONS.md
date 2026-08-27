# Open Source Systems Scan — current Argus call-site fence semantics and literal regressions

Invocation started: 2026-08-27T17:01:42+09:00
Checkpointed: 2026-08-27T17:09:24+09:00

Frozen semantic tuple: `note@577514d101c916b2ec14795371d7f15d609b2f0a / control 11 / open_source config 5` (`DESIRED_STATE` blob `bf7b8c7f6971c0ec2f3fa7a8d53dca1f88ac50a3`, role-config blob `118f440957ba4654e804af902aa09a9224acca43`). The tuple was frozen only after the required SHA-only ref recheck and before the first role-local semantic read. Later note-main movement is not adopted in this invocation.

Public source frozen for substantive inspection: `lbx154/Argus@7cb5546d364c7d11dcc3bff4151993b7aa72a414`, verified as public `main` through a SHA-only Git-ref lookup. The prior clean checkpoint had inspected `33da786bbc6787a2eeb63a5f492498eae87c78c7`; current source inspection shows the continuous-state/handoff/rearm paths discussed below still have the relevant behavior. No O, other-worker, downstream, or legacy semantic state was read.

## 1. Literal strict-receipt test shape

The predecessor established that a Manager reconciliation receipt must never rely on prompt/liveness helpers that can fall back to `research`. The public test surface now makes the proposed helper and five negative/positive regressions concrete.

Proposed authority helper:

```python
def mint_manager_reconcile_receipt(
    project_root: Path,
    *,
    expected_intent_id: str,
    expected_route: ProtectedRouteFingerprintV4,
    require_replacement_reset: bool,
) -> ManagerReconcileReceiptV1:
    ...
```

The helper should direct-read `.argus/PIPELINE_STATE.json`, parse it once, require a nonempty persisted `vertical`, run `require_vertical(persisted_vertical, project_root)` and then strict `load_vertical(persisted_vertical, project_root=project_root)`, and inspect `current_stage`, `stages`, `stage_history`, and `rollback_history` from that parsed object. It must not call `current_stage()`, `_active_vertical_checklist_defs()`, or another research-fallback resolver while minting authority.

Canonical digest inputs should be semantic JSON objects, not raw file bytes:

```python
def canonical_json_sha256(value: object) -> str:
    payload = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()
```

`ManagerReconcileReceiptV1` should bind at least `version`, `intent_id`, semantic route fingerprint, canonical full protected-pipeline digest, strict vertical identity, strict first-stage identity, observed current stage, and a digest/identity for the fresh reset-history evidence when replacement reset is required. For a project-local data domain it should additionally bind the canonical parsed domain-definition digest. A receipt timestamp may be recorded for audit but must not participate in authority equality.

### Pytest-shaped case 1 — built-in research replacement

Start from the existing `test_force_replacement_resets_inprogress_pipeline_immediately` shape: research vertical, `current_stage="review"`, stale `research=done`, `plan=done`, `review=in_progress`; call `persist_vertical(..., "research")`, then `reset_stage_for_new_intent(..., old_vertical="research", new_vertical="research", force_replacement=True)`. Mint only if direct-read state shows exact research first stage, target status `in_progress`, no downstream status in `{done, ready, in_progress, skipped}`, and newest reset history is Manager-owned and points to research. Mutating any one of those postconditions before mint must make mint fail closed.

### Pytest-shaped case 2 — same-first-stage replacement still needs a real reset

Begin already at `current_stage="research"` but set `research.status="done"` and downstream progress. Force replacement. Receipt minting must require a *new* `direction="reset"` history entry and `research.status="in_progress"`; simply observing that the stage name already equals the target first stage is insufficient. Remove the fresh reset history or leave target `done` and assert no receipt.

### Pytest-shaped case 3 — valid custom domain

Use the existing `write_data_domain(...)` helper with a small stage order such as `scope -> execute -> review`, persist that custom vertical, force replacement, and mint only after strict load succeeds. The receipt must bind both the canonical pipeline object digest and the canonical parsed custom-domain JSON digest.

### Pytest-shaped case 4 — missing custom-domain definition

After establishing route/reset state, remove the custom domain definition. Strict receipt mint must fail before authority is issued. No fallback to research is allowed.

### Pytest-shaped case 5 — corrupt-but-present custom-domain definition

Keep the custom-domain path present but overwrite it with malformed JSON. This is the important distinction: existence-oriented `require_vertical` can recognize a named project-local domain path, but strict `load_vertical` must fail. Assert the path still exists, assert no receipt, and assert there is no research fallback.

These tests should reuse the existing public `test_verticals.py` reset scaffolding rather than inventing a parallel stage model.

## 2. Current production continuous-state writer map

A current code search at public Argus `7cb5546...` returns the following production files using the three state-mutation surfaces:

- `write_continuous_config`: `webapi/daemon_upgrade.py`, `daemon/state.py`, `apps/_life_actions.py`, `webapi/daemon_lifecycle.py`, `daemon/_life_worker_boot.py`, `webapi/manager_pending_question.py`, `daemon/_life_worker_identity.py`;
- `compare_and_swap_continuous_config`: `daemon/state.py`, `daemon/_life_worker_run.py`, `manager/front_door.py`, `webapi/manager_dispatch.py`, `daemon/_life_worker_boot.py`, `life/supervisor/_planning_cycle_verdict.py`;
- `disable_continuous_config`: `daemon/state.py`, `webapi/manager_dispatch.py`, `apps/_life_actions.py`, `life/chat/router.py`.

`state.py` is the storage primitive/definition rather than a semantic caller. The remaining production uses map to first-class fence actions as follows.

| Current path / semantic operation | Current observed behavior | Required active-fence action |
|---|---|---|
| `manager/front_door.py` continuous Manager handoff | Manager route commit, replacement supersede/session rename, optional mission persist occur in CAS `before_write`; final continuous replace happens after those side effects | **FINALIZE-capable only after hardening**: begin disabled fence first; strict receipt + exact durable mission required before clearing fence/enabling target. Current single-CAS callback is not sufficient. |
| daemon boot Manager reconciliation (`_life_worker_boot.py` CAS with `_commit_decision`) | real Manager decision can be committed in CAS callback before continuous replace | **FINALIZE-capable only after hardening** with the same strict receipt/fence contract; current callback must not bypass fence. |
| `manager_dispatch.py` standing STEER promotion | CAS directly enables `standing_objective` after directive | **REFUSE/reconcile** while a fence is active; a stored directive is not itself permission to clear/finalize an in-flight handoff. |
| `daemon_lifecycle.py` Web daemon start | when `resume_continuous=True`, disabled state with any `done_reason` beginning `operator ` is reenabled *before daemon-limit admission* | **REFUSE** active fence. More broadly, process start must not mutate semantic campaign state before admission; process rearm should use current exact state and the narrow stop-reason allowlist. |
| `daemon_upgrade.py` immediate upgrade | reads a pre-stop continuous snapshot and later rewrites its objective/enabled state | **REFUSE** active fence; never restore a copied objective snapshot. |
| `daemon_upgrade.py` scheduled upgrade | persists `resume_continuous` + objective snapshot and later re-enables that saved objective | **REFUSE** active fence; restart must reconcile current durable state, not stale request payload. |
| `_life_worker_identity.py` `_rearm_operator_drain_for_resume` | has the good exact `RESUMABLE_STOP_REASONS` allowlist but performs a non-CAS read→`write_continuous_config(enabled=True)` | **REFUSE** if fence exists; otherwise convert process-only rearm to exact-state CAS of the current disabled record. |
| `manager_pending_question.py` decision continue | if an objective exists and is disabled, directly rewrites it enabled | **REFUSE/reconcile** while fenced. The human decision can remain accepted; execution rearm is a separate authority decision. |
| `manager_pending_question.py` explicit decision stop | disables with `operator chose to stop the campaign` | **CANCEL**. A newer explicit semantic stop should cancel a fence while remaining disabled. |
| `manager_dispatch.py` Web continuous stop | `disable_continuous_config` | **CANCEL**: explicit semantic operator stop. |
| `life/chat/router.py` `/continuous stop|off|pause` | `disable_continuous_config` | **CANCEL**: explicit semantic operator pause/stop. |
| `apps/_life_actions.py` `/config continuous=false` | syncs `disable_continuous_config`; enabling through this config parser is explicitly redirected to Manager `/continuous start` | **CANCEL** for the observed off path. Any legacy/direct enable must **REFUSE** fence authority. |
| `_life_worker_run.py` planner-declared `project_done` | exact adopted-generation CAS disables active campaign | **PRESERVE** a fence / never clear it. This terminalization applies to an enabled adopted campaign, not handoff authority. |
| `_planning_cycle_verdict.py` content-filter disarm | CAS disables active campaign and requests operator reformulation | **PRESERVE** a fence / never clear it; machine safety disarm is not newer semantic authority. |
| `_life_worker_boot.py` backend incompatibility disarm | writes disabled when enabled objective is incompatible with backend | **PRESERVE** a fence / never clear it. |

The storage helper itself should not infer semantic authority from `enabled=False` or a string reason. Callers need typed `PRESERVE`, `CANCEL`, `FINALIZE`, or `REFUSE` semantics. The safety invariant remains `handoff_fence is not None => enabled is False`.

## 3. Two current-source details strengthen the fence design

### 3.1 Web daemon start still conflates process start and semantic resume

Current `start_project_daemon()` re-enables a disabled continuous objective if `done_reason.lower().startswith("operator ")`, then only afterward calculates daemon admission. This is both broader than Argus's own `RESUMABLE_STOP_REASONS` and ordered before the decision whether a process can actually start. A request can therefore change durable campaign semantics even when the daemon is not admitted. A first-class fence must be a hard refusal boundary for this path.

### 3.2 Upgrade requests still carry stale semantic snapshots

Both immediate and scheduled upgrade paths copy `continuous.enabled/objective` and later use ordinary whole-state writes to restore them. A semantic stop or replacement occurring after that snapshot can therefore be overwritten by the upgrade completion. The fix should not add another snapshot/version field to the upgrade request; it should make upgrade carry only process restart intent and let one current-state `reconcile_or_rearm` boundary decide semantic rearm.

## 4. Real-Backlog ambiguity regression is now directly composable from existing tests

The existing Manager pipeline-yield regression already gives the right harness:

- real `Backlog` on `backlog.jsonl`;
- existing old work and legacy/bootstrap work;
- fake `Prepared` whose `commit(acquire_lock=False, force_stage_reset=True)` is invoked under the Manager pipeline lock and boundary-yield marker;
- a `persist()` callback that observes old work already superseded.

The existing continuous-storage fault test independently supplies the exact failure injection: make `os.replace(...continuous.json)` fail *after* the callback committed, and assert `ContinuousConfigCommitError` while the callback side effect remains and the old continuous state remains. These should be combined instead of inventing a new storage simulator.

Target regression specification after the proposed fence/exact-insert primitive exists:

```python
def test_handoff_replace_failure_recovers_exactly_once_with_real_backlog(...):
    # A enabled; old backlog present; target_id pre-reserved.
    # Begin exact-CAS disabled handoff fence for B before any route/backlog side effect.
    # First reconcile commits Manager postconditions and persists target_id through
    # ensure_operator_priority_item_exact(...). Emit task-added only if inserted=True.
    # Inject final continuous.json replace ambiguity/failure after those side effects.
    # Reread current continuous bytes/generation; do not infer commit from exception type.
    # Run recovery twice.
    # Assert exactly one physical target_id row, exactly one task-added event,
    # no duplicate semantic mission, and one successful final target enable.
```

The exact-insert contract remains:

- no matching ID: compute operator priority, first timestamp, and immutable creation stamp under the same Backlog lock; insert once;
- one matching ID + same immutable creation stamp: return the current row with `inserted=False`;
- duplicate matching IDs, missing legacy stamp at this reserved ID, or same ID + different stamp: fail closed;
- retries reuse the persisted original row, including original timestamp/priority, and do not emit a second task-added event.

Current `Backlog.add()` simply appends under lock and current `Backlog.update()` selects the first matching ID, so duplicate-ID prevention is not cosmetic: duplicate IDs create ambiguous later state transitions. Current shared `_atomic_rewrite_jsonl` is temp+`os.replace` without explicit file/directory fsync, so if the handoff guarantee includes power-loss durability, strengthening the shared Backlog rewrite primitive remains a separate required durability step rather than claiming `os.replace` alone is durable.

## 5. Current manager-handoff identity remains too weak for semantic restart reuse

At current public head, `manager-handoff.json` is still version 3 and binds objective hash, vertical, domain, continuous generation, and intent id. Match accepts recorded generation `<=` current generation. It does not bind workflow mode, research target/direction, target venue, or a canonical protected-route/state fingerprint. Therefore the prior proposed v4 semantic route fingerprint remains applicable; old v1-v3 identities should force one Manager reconciliation before a new v4 identity is issued rather than being silently upgraded.

## 6. Candidate refinement

`clean-os-g1-005` is now:

**first-class disabled continuous handoff fence with typed PRESERVE/CANCEL/FINALIZE/REFUSE semantics; strict direct-read Manager reconciliation receipt bound to canonical protected state/custom-domain definition; disabled fence installed before *all* route/backlog/session/persist side effects; pre-reserved target ID plus immutable creation identity and atomic exactly-once operator-priority Backlog insert; recovery that always rereads current continuous bytes/generation after ambiguous write failure; current-state-only process rearm using exact stop-reason allowlist and CAS; and a v4 semantic protected-route identity for restart reuse.**

This run did not mutate Argus, reproduce a live daemon race, exploit an unauthorized state transition, or benchmark the proposed changes. Findings are source-level behavior/design and executable regression specifications at the pinned public commit.

## Exact continuation

1. Inspect the boot Manager CAS path's success/failure/suppression handling in full and decide whether the first-class fence should be initiated there or whether boot should always reconcile an existing fence created by the front door.
2. Specify the exact `HandoffFenceV1` and `ManagerReconcileReceiptV1` dataclass/JSON schemas, including source/target route fingerprints, pre-reserved target item identity, and canonical digest fields, while keeping audit timestamps out of authority equality.
3. Map the current Manager event sink to the physical `task-added` event emitted for a continuous mission, so the real-Backlog failure regression asserts exactly one durable event as well as one backlog row.
4. Keep external/admin whole-object `PIPELINE_STATE` writer fencing and global JSON-state CAS as a separate candidate branch; do not broaden this result into a claim about all Argus state writers.
