# Open Source Systems Scan — reconcile receipt must prove postconditions, not only route identity

Invocation started: 2026-08-27T10:59:07+09:00
Checkpointed: 2026-08-27T11:03:54+09:00

Frozen semantic tuple: `note@828d11d61f7417ef51fdaf6248c3f3a671f92313 / control 11 / open_source config 5` (`DESIRED_STATE` blob `bf7b8c7f6971c0ec2f3fa7a8d53dca1f88ac50a3`, role-config blob `118f440957ba4654e804af902aa09a9224acca43`). The note head advanced after the semantic-freeze barrier; no later control/config was adopted. Only own clean state and public sources were used. Public `lbx154/Argus` main was reverified at `33da786bbc6787a2eeb63a5f492498eae87c78c7`.

## 1. New strongest finding: target route identity is not proof that Manager commit finished

Previous continuation proposed using source/target route fingerprints to decide whether recovery may skip Manager reconciliation. Current public Argus source shows this is too weak.

`persist_vertical()` is deliberately seed-only: it writes the new vertical/domain/workflow/research fields, but if `current_stage` already exists it does **not** reset it. `reset_stage_for_new_intent()` is called only *after* `persist_vertical()`, and its own contract is explicitly fail-open: errors or rejected rollback/reset return `False` rather than failing the Manager division. In `_vertical_ops.py`, the return value is not used as a commit-admission result.

Therefore, even without a process crash, a replacement handoff can expose the full target route fingerprint while retaining a stale source-stage value. A crash between the two writes makes the same shape more obvious. A recovery rule of `current route == target_route_v4 -> exact insert/finalize` can therefore skip a Manager reconciliation whose stage-reset postcondition never completed.

This is stronger than the earlier crash-only concern and narrows the fix: route-v4 remains useful for coarse source/target classification, but it cannot itself be a commit receipt.

Public evidence:
- `argus_skill/skills/vertical_select.py`: `persist_vertical()` seeds stage only when absent and never resets an existing stage.
- same file: `reset_stage_for_new_intent()` says it must run after `persist_vertical()`, is fail-open, and returns false on reset rejection/error.
- `argus_skill/manager/_vertical_ops.py`: commit paths call `persist_vertical(...)` then `reset_stage_for_new_intent(...)` without turning the reset result into a durable success criterion.

## 2. Custom/adapted data domains add another state dimension absent from route-v4

For a new Manager-authored domain, `_vertical_ops.py` uses `_restore_files_on_error` across the pipeline state files plus the domain JSON, then performs:
1. `write_data_domain(...)`;
2. `persist_vertical(...)`;
3. `reset_stage_for_new_intent(...)`.

For adapted existing data domains, it can also rewrite the domain definition and `research/DOMAINS/INDEX.json` before persisting the route. `_restore_files_on_error` snapshots and restores only when a Python `Exception` unwinds the context manager; it is not a process-crash transaction.

The domain writer is individually atomic (`tmp -> os.replace`), but `INDEX.json` is best-effort and the domain definition is a separate file from protected pipeline state. Thus the route tuple can be unchanged while the active data-domain stage definition changed, or target route can be visible while stage-reset state is stale. Route-v4 does not capture this.

Recovery must therefore prove the post-commit protected state, including the active project-local domain definition when applicable, rather than reconstructing completion from six route fields.

Public evidence:
- `argus_skill/manager/_session_ops.py::_restore_files_on_error` restores snapshots only on caught `Exception`.
- `argus_skill/verticals/_data_domain.py::_atomic_write_json` uses one-file atomic rename; `_update_index` is explicitly best-effort.
- `argus_skill/manager/_vertical_ops.py` new/adapted domain commit order described above.

## 3. Minimal typed recovery receipt refined

The fence should carry an optional **host-minted reconciliation receipt**, not a mutable phase string and not a replayable serialized `PreparedManagerHandoff`.

Proposed `ManagerReconcileReceiptV1` minimum fields:
- `fence_id` and `intent_id`;
- `execution_task_sha256`;
- `target_item_id`;
- `target_route_v4` for human-readable/coarse classification;
- `pipeline_state_sha256` computed from the exact protected pipeline object *after* `Prepared.commit()` returns and deterministic postconditions pass;
- `data_domain_sha256` when the selected vertical is a project-local/adapted data domain, otherwise null;
- `replacement_reset_required` plus `expected_target_stage` when replacement semantics require reset;
- `observed_target_stage` at receipt mint time;
- observed goal-contract revision/status as **advisory provenance only under current semantics**, because current goal-contract recording is deliberately additive/fail-soft and does not gate completion.

Receipt minting requirements:
1. Manager semantic commit runs under the existing pipeline lock.
2. Host re-reads protected pipeline state and, for project-local data domains, the exact active domain definition.
3. If replacement reset was required, persisted/current stage must satisfy the intended reset postcondition; a fail-open reset result is not enough.
4. Only then may the host exact-CAS the disabled fence to include `ManagerReconcileReceiptV1`.

Recovery becomes mechanical:
- fence has **no receipt** -> Manager re-reconcile, regardless of whether route fields happen to equal target;
- receipt exists but current protected pipeline/domain digest differs -> Manager re-reconcile;
- receipt exists and exact protected state still matches -> skip Manager, perform exact idempotent Backlog insert if needed, then final CAS enable;
- exact target Backlog row already exists -> return it and finalize without duplicate observability.

This keeps route fingerprints as classification evidence while the receipt proves the stronger postcondition actually needed for safe replay avoidance.

## 4. GoalContract is a separate authority side effect and should not be silently conflated with route success

`PreparedManagerHandoff.commit()` calls `_record_goal_contract(...)` after `commit_vertical_decision(...)`. `_record_goal_contract` explicitly catches every exception, emits `life.manager.goal_contract.failed`, and still lets the handoff succeed. `project_contract.py` likewise documents contracts as additive today and not completion-gating for existing projects.

So the proposed reconciliation receipt must **not** claim that route success implies contract success. Under current public semantics, record observed contract revision/status in the receipt for audit/repair but do not retroactively make it a hard handoff gate. If GoalContract later becomes completion-authoritative, its revision/digest must move into the deterministic postcondition gate rather than remain best-effort.

This is important because the front-door source itself says an invisible contract-write failure leaves downstream roles reading stale authority.

## 5. Source-exact regression harness refinement

Existing `tests/manager/test_pipeline_yield.py::test_continuous_handoff_requests_boundary_yield` already provides real `Backlog`, real continuous state, pipeline-yield assertion, and fake `Prepared`. Existing `tests/daemon/test_state_portable.py` provides the fault seams for callback-committed/final-replace-failed and post-replace durability failure.

Add three focused regressions:

### A. Target route visible but reset postcondition missing
- seed A with a same-vertical non-initial `current_stage`;
- replacement fake/fixture persists target route fields but simulates `reset_stage_for_new_intent` returning false or leaves stale stage;
- assert no `ManagerReconcileReceiptV1` may be minted;
- recovery must re-enter Manager even though `target_route_v4` matches.

### B. Callback route commit + exact mission insert land, final continuous replace fails
- first exact CAS writes disabled fence;
- Manager commit mints receipt only after postcondition readback;
- real Backlog exact-inserts target ID;
- monkeypatch `daemon_state.os.replace` to fail only the **final** `continuous.json` replace after the earlier fence write has succeeded;
- on recovery, re-read actual state; matching receipt permits skipping Manager and exact insert returns `(existing, inserted=False)`;
- final enable succeeds once; physical Backlog contains exactly one target ID and no duplicate queued/task-added observable.

### C. Custom/adapted domain receipt mismatch
- commit a target project-local domain and mint receipt including domain digest;
- alter/recover into a state where route tuple still matches but domain JSON or protected pipeline digest does not;
- assert recovery re-enters Manager instead of finalizing from route-v4 alone.

The existing post-replace durability test remains a positive control that an exception does not tell recovery whether bytes landed; every recovery branch must re-read current state/generation.

## Candidate refinement

`clean-os-g1-005` is now better described as:

**disabled handoff fence + Manager postcondition receipt + exact durable Backlog insertion + current-state reconcile/rearm + derivative route-v4 identity**.

The key change in this run is that route-v4 is no longer treated as sufficient evidence that semantic route commit completed. The postcondition receipt must bind the exact protected pipeline state and active data-domain definition after any required stage reset.

No public Argus mutation, live daemon fault injection, or unauthorized state change was performed.

## Exact continuation

1. Inspect the exact `write_pipeline_state` object and stage-reset primitives to choose a canonical postcondition digest that is stable across irrelevant serialization differences but includes every protected field relevant before mission execution.
2. Determine whether `ManagerReconcileReceiptV1` is best stored inside the CAS-protected continuous fence or as a separate durable sidecar; prefer the design that cannot leave `receipt present / fence absent` or `fence finalized / receipt stale` under crash.
3. Expand the source-exact pytest pseudocode into concrete monkeypatch ordering for the *second* `continuous.json` replace (fence succeeds, final enable fails) and a same-route stale-stage case.
4. Keep external/admin `PIPELINE_STATE` writer fencing as a separate candidate branch; do not broaden this handoff-recovery result into a claim about all Argus state writers.
