# Open Source Systems Scan — canonical postcondition receipt and in-fence crash binding

Invocation started: 2026-08-27T11:58:18+09:00
Checkpointed: 2026-08-27T12:01:21+09:00

Frozen semantic tuple: `note@0b3c1889e88e9dd43cd90c2f7f824aa1407db7cd / control 11 / open_source config 5` (`DESIRED_STATE` blob `bf7b8c7f6971c0ec2f3fa7a8d53dca1f88ac50a3`, role-config blob `118f440957ba4654e804af902aa09a9224acca43`). The note head advanced after the semantic-freeze barrier; no newer control/config was adopted. Only own clean state and public sources were used. Public `lbx154/Argus` main was reverified at `33da786bbc6787a2eeb63a5f492498eae87c78c7`.

## 1. Canonical receipt should hash the parsed protected PIPELINE_STATE object, not selected route fields or file bytes

The exact generic state writer at `argus_skill/core/pipeline_state.py` writes one JSON object with `indent=2, sort_keys=True` through sibling-temp + `os.replace`, but there is no state revision/CAS and no fsync. The important point for a reconciliation receipt is that the file is a heterogeneous Manager-control object, not only a route tuple.

Current public writers place semantically relevant state in the same object:

- `vertical`, optional `domain`, `workflow_mode`, `research_target_level`, `research_target_set_at`, `research_direction_mode`, `target_venue`, and seed-only `current_stage` from `skills/vertical_select.py::persist_vertical`;
- `current_stage`, per-stage `stages`, `stage_history`, and `rollback_history` from `skills/stage_machine.py::_set_stage`;
- `verification_profile` and `exploration_posture` from `core/verification_policy.py`;
- `manager_classification_contract_failures` diagnostics from `manager/classification_contract.py`.

A curated six-field route digest can therefore match while protected behavior has changed. A raw file-byte digest is also unnecessarily sensitive to indentation/key-order differences. The narrowest safe primitive is instead:

```text
pipeline_state_sha256 = SHA256(
  UTF8(JSON(parsed_pipeline_object,
            ensure_ascii=false,
            sort_keys=true,
            separators=(",", ":"),
            allow_nan=false))
)
```

This is stable across whitespace and key-order differences but conservative across any actual parsed-object difference. Conservatism is desirable here: while a disabled handoff fence is active, an independent mutation of policy, classification diagnostics, stage history, or route state means the old reconciliation receipt no longer proves the current protected state and Manager reconciliation should run again.

Do **not** normalize semantic values again while hashing. The object must first be written/read through Argus's existing validators/normalizers; the receipt hashes the exact postcondition that Argus itself persisted. Re-normalizing at digest time would risk treating a corrupted or unvalidated representation as equivalent to the checked state.

## 2. Replacement reset needs a deterministic mint gate before the digest is accepted

`persist_vertical()` is seed-only: when `current_stage` already exists it never resets it. `reset_stage_for_new_intent()` is a second step and is deliberately fail-open. Under forced replacement it calls `reset_stage_for_replacement_intent()` but returns `False` if the stage primitive rejects with `ValueError`; callers do not currently make that boolean a hard commit condition.

The underlying `_set_stage(... direction="reset")` has stronger postconditions than simply `current_stage == first_stage`:

- `current_stage` becomes the target first stage;
- every downstream stage whose status is `done`, `ready`, `in_progress`, or `skipped` is downgraded to `pending`;
- the target stage is made `in_progress` even when reset lands on the same current stage;
- one `stage_history` entry with `direction="reset"` is appended;
- one legacy `rollback_history` entry is appended.

Therefore a host must not mint `ManagerReconcileReceiptV1` for a replacement solely because the route tuple matches. Before hashing the protected object it should fail closed unless all reset-required postconditions are observed. Minimal source-exact checks are:

1. selected vertical/domain resolves and its first stage is known;
2. persisted `current_stage` equals that first stage;
3. `stages[first_stage].status == "in_progress"`;
4. no downstream stage has a status outside the permitted reset postcondition set (normally absent/empty or `pending` after this primitive); in particular no downstream `done|ready|in_progress|skipped` survives;
5. the newest relevant `stage_history` record proves a Manager reset to that first stage, with a matching rollback-history record when replacement used the reset primitive.

The exact full-object digest is minted only after these postconditions pass. This separates two questions cleanly: a deterministic validator proves that the Manager transition finished; the digest then proves that the exact protected object has not changed since that proof.

## 3. `ManagerReconcileReceiptV1` belongs inside the CAS-protected continuous fence, not in an independent sidecar

A separate receipt sidecar creates a third durable object in addition to protected `PIPELINE_STATE.json` and `continuous.json`. Even with atomic writes, crashes can produce `receipt present / fence absent`, `fence present / receipt missing`, or stale receipt/fence association unless an additional transaction/revision protocol is added.

The existing continuous state already has the stronger primitive needed for the fence: cross-process locking, exact generation-aware CAS, file fsync, atomic replace, and parent-directory fsync. The receipt should therefore be an optional structured field of the disabled handoff-fence generation itself. One exact CAS then binds:

- the target objective/mission identity;
- source and target route-v4 fingerprints for coarse classification;
- frozen target backlog item ID / creation stamp identity;
- optional `ManagerReconcileReceiptV1` containing the canonical protected-state digest and, for project-local/adapted domains, the active domain-definition digest.

Crash behavior then remains fail-closed:

- route committed but receipt-CAS not written -> fence has no receipt -> re-enter Manager;
- receipt-CAS written but power loss loses the weaker non-fsynced pipeline write -> on restart current pipeline digest differs -> re-enter Manager;
- receipt-CAS and protected state both survive -> digest match permits skipping Manager and continuing exact backlog insertion/final enable;
- any later protected-state mutation -> digest mismatch -> re-enter Manager.

### Critical source constraint: current `ContinuousConfigState` silently drops unknown fields

This in-fence design is **not** implementable by merely injecting `handoff_fence` into the current JSON. `daemon/state.py::_read_continuous_state_unlocked()` constructs a fixed `ContinuousConfigState` containing only `enabled`, `objective`, `open_ended`, `done_reason`, `done_at`, and `generation`. `_write_continuous_config_unlocked()` serializes only that fixed set, and `_same_continuous_state()` compares only it.

Therefore any ad-hoc unknown `handoff_fence`/receipt field would be discarded by the next ordinary read-modify-write. A correct implementation must extend `ContinuousConfigState`, the reader, reserve serialization, writer, and `_same_continuous_state`/CAS equality so the fence payload itself is generation-bound first-class state. This is a stronger implementation requirement than the previous abstract “store it in continuous.json” proposal.

## 4. GoalContract should stay advisory in the receipt under current semantics

`PreparedManagerHandoff.commit()` first calls `manager.commit_vertical_decision(...)`, then `_record_goal_contract(...)`. `_record_goal_contract` catches all errors and emits a failure event without failing the handoff. Consequently, current Argus semantics do not make GoalContract persistence a route-commit admission condition.

The receipt may record observed contract revision/status as advisory provenance, but `pipeline_state_sha256` must not imply GoalContract success. If GoalContract later becomes completion-authoritative, its durable revision/digest should be promoted into the deterministic mint gate explicitly rather than being smuggled into “route success.”

## 5. Concrete second-replace failure regression

The existing `tests/manager/test_pipeline_yield.py::test_continuous_handoff_requests_boundary_yield` already provides the useful front-door shape, and `tests/daemon/test_state_portable.py` already contains continuous atomic-write failure seams. A source-exact regression can combine them without inventing a new harness.

Sketch:

1. seed continuous A at generation g, enabled;
2. start replacement B with a pre-reserved root task ID;
3. first exact CAS writes a **disabled structured handoff fence** at g+1; assert no target mission yet runs;
4. under existing Manager pipeline lock, `prepared.commit(force_stage_reset=True)` runs;
5. host re-reads protected pipeline state, validates reset postconditions, computes canonical `pipeline_state_sha256`, and exact-CASes the same disabled fence to attach `ManagerReconcileReceiptV1` at g+2;
6. exact durable Backlog insert writes target ID once;
7. monkeypatch `daemon_state.os.replace` so the **final** continuous enable replace fails after the earlier fence writes have succeeded;
8. recovery must re-read current `continuous.json` instead of inferring commit state from the exception;
9. matching in-fence receipt + protected digest allows skipping Manager; exact backlog insert returns the existing row (`inserted=False`); final CAS enables B once;
10. assert one physical target Backlog ID, no duplicate queued/task-added observable, B enabled, fence cleared/finalized, and no execution of A under B's route.

A companion stale-stage test seeds same-route replacement where route-v4 already equals target but the reset history/postconditions are missing. Receipt mint must fail and recovery must re-enter Manager.

## 6. Candidate refinement

`clean-os-g1-005` is now:

**disabled structured handoff fence + first-class CAS-bound Manager postcondition receipt + canonical whole protected-state digest + deterministic replacement-reset mint gate + exact durable Backlog insertion + current-state reconcile/rearm + derivative route-v4 classification.**

This remains a source-derived adaptation candidate. No Argus mutation, live daemon fault injection, unauthorized state change, or production benchmark was performed.

## Exact continuation

1. Inspect the current `ContinuousConfigState` tests and all direct constructors/callers to enumerate the minimal backward-compatible schema extension for `handoff_fence` and ensure old v1 JSON reads as `fence=None` without dropping a newly written fence on any read-modify-write path.
2. Inspect the exact active-stage-order helpers and replacement tests to turn the reset mint gate above into concrete assertion code, including same-stage reset and project-local data-domain stage orders.
3. Inspect real Backlog serialization/update code and existing events to specify `creation_stamp` storage plus `(existing, inserted=False)` retry behavior without letting generic `Backlog.update()` mutate immutable creation identity.
4. Keep external/admin `PIPELINE_STATE` writer fencing and global JSON-state CAS as a separate candidate branch; do not broaden this handoff-recovery result into a claim about all Argus writers.
