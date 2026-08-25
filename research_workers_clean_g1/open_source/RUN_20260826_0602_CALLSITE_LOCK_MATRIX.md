# Open Source clean_g1 — RUN_20260826_0602_CALLSITE_LOCK_MATRIX

Control snapshot frozen for semantic execution at note main `f49c6f2062d12c0a67bf314b763c5c7a3152ca2f`: control revision 8, `open_source` config revision 5. Before substantive work the note head was rechecked using the SHA-only Git-ref transport required by the sanitized control manifest. Later note-main movement was treated as unrelated concurrent state and not used semantically. Clean-exploration boundary was preserved: only this worker's own clean state, its own feedback path (absent), sanitized root/role control files, and public sources were read. No O/O-derived state, other-worker state/output/config, downstream comparator/integrator/index/feed/audit state, aggregate execution ledger, other-role receipts, or legacy/pre-independence semantic state was read.

## Scope

Continue the highest-priority frontier from `RUN_20260826_0502_CAPABILITY_SECRECY.md` by auditing the freshest public Argus upstream for actual production call sites of the durable pipeline mutators and classifying where the existing outer Manager pipeline lock does and does not protect them. The purpose is to distinguish a real normal-path concurrency defect from a low-level authority/embedding-path defense-in-depth gap.

No live unauthorized state mutation, lock bypass, secret read, or exploit was executed. This is source/call-path analysis only.

## Source freshness

The public upstream remains:

- `lbx154/Argus@962cb06554daaede17b786c495e13ee3b6530e6e` — exact current `main` observed by SHA-only Git-ref lookup during this run.

No newer public upstream commit was visible, so this run deepens the audit against the same freshest source revision rather than mixing source versions.

## Finding A — the normal live-daemon stage-mutation path is covered by one outer Manager pipeline lock

The strongest update from this call-site sweep is direct source confirmation of the lock coverage previously inferred.

`argus_skill/daemon/_life_worker_run.py::_rf_main_loop`:

1. checks `manager_pipeline_yield_requested`;
2. obtains `rf_state.runner.manager`;
3. obtains `manager.pipeline_lock()` when available;
4. enters `with pipeline_lock:`;
5. executes `supervisor.run()` (or all supervisor runs in a thread pool) while that lock remains held;
6. keeps planner terminal-state settlement and the in-lock self-maintenance reconciliation inside the same critical section.

The stage-mutating production paths enumerated below execute under `supervisor.run()` in the ordinary resident-daemon architecture. Therefore this run found **no supported normal-path route/stage interleaving race** among those paths.

This materially narrows `clean-os-g1-005`: the case for primitive-bound authority is not “the current daemon routinely races itself.” The case is that low-level durable mutators should remain safe even when reached through a wrong/stale/embedded path that does not carry the host's intended lock/identity contract.

## Finding B — production call-site matrix

### 1. Manager semantic stage decision → `advance_stage` / `rollback_stage` / `complete_final_stage`

Path:

`apps/_runtime_stage_transition.py` → `Manager.decide_stage_transition()` → `manager/_stage_ops.py::_apply_stage_decision_to_disk()` → stage-machine mutator.

Normal daemon lock coverage:

- **Yes.** The daemon wraps `supervisor.run()` in `manager.pipeline_lock()`, and mission execution reaches this stage-decision path before `supervisor.run()` returns.

Mutation checks:

- `advance_stage`: target-order legality + deterministic active-vertical completion validator before mutation.
- `complete_final_stage`: final-stage/explicit early-completion shape check + deterministic completion validator + versioned completion-contract fingerprint.
- `rollback_stage`: target must be earlier; it has no positive-evidence completion gate because rollback intentionally represents detected upstream deficiency.

Authority/revision checks at the primitive:

- no authenticated caller capability;
- actor fields are strings;
- no exact pre-mutation state revision/CAS requirement;
- no primitive assertion that the Manager pipeline lock is currently held.

The source itself explicitly documents that `advance_stage` is intended Manager-only but caller identity is unauthenticated, and that `complete_final_stage`'s current early-completion boolean is “a lock, not a signature.”

### 2. Planner-requested stage change → direct advance/rollback

Path:

`life/supervisor/_planning_cycle_enqueue.py::_apply_planner_stage_request()` imports the stage-machine functions directly. It attempts `advance_stage`; on a `ValueError` it attempts `rollback_stage`.

The same module also has deterministic automatic research closure: when `_research_stage_ready_for_close()` finds the research artifacts/vertical completion issues clean, it directly calls `advance_stage(... target_stage="plan", advanced_by="manager:auto_completion")`.

Normal daemon lock coverage:

- **Yes.** Planning runs inside the same `supervisor.run()` critical section held by the daemon's outer Manager pipeline lock.

Primitive authority/revision checks:

- identical to the stage-machine primitive: no caller capability and no exact revision/CAS.

Important scope detail:

- automatic research close still uses `advance_stage`, so it retains the deterministic completion validator; this is not an unvalidated forward write.

### 3. Dynamic-plan safety rollback → direct rollback

Path:

`life/supervisor/_mission_execution_settlement.py::_apply_dynamic_plan_stage_guard()` detects a premature Manager advance while sibling/dependent nodes from the same bounded plan are unfinished, then directly calls `rollback_stage(... rolled_back_by="supervisor_dynamic_plan_guard")` to restore the stage.

Normal daemon lock coverage:

- **Yes.** This settlement is part of the same supervisor run protected by the outer pipeline lock.

Primitive authority/revision checks:

- no capability / lock-ownership assertion / revision-CAS at `rollback_stage`.

This path is a useful design constraint for any future capability scheme: authority cannot be hard-coded to a single textual actor “manager.” A legitimate host guard also needs narrowly scoped rollback authority.

### 4. Manager route/vertical commit → `persist_vertical` + replacement reset/rollback

Path:

`manager/_vertical_ops.py::commit_vertical_decision()` obtains `self.pipeline_lock()` unless an already-held lock is explicitly declared, then `_commit_vertical_decision_locked()` calls:

- `persist_vertical(...)`;
- `vertical_select.reset_stage_for_new_intent(...)`.

`reset_stage_for_new_intent()` in turn uses:

- `reset_stage_for_replacement_intent()` for a Manager-confirmed forced replacement; or
- `rollback_stage()` when a genuinely new bounded intent follows a completed prior vertical.

`commit_domain()` follows the same `self.pipeline_lock()` wrapper pattern.

Normal Manager route-commit lock coverage:

- **Yes.** The high-level Manager commit methods acquire the pipeline lock themselves.

Low-level primitive properties:

- `persist_vertical()` itself does not acquire/verify that lock. It atomically writes route/workflow/domain/target fields and only seeds `current_stage` if no stage exists; it intentionally never resets an existing stage.
- `reset_stage_for_new_intent()` itself does not authenticate its caller; it relies on the locked Manager caller and invokes low-level reset/rollback primitives.

Again the normal host path is serialized, while the leaf functions remain context-dependent rather than self-defending.

### 5. Embedded `_SkillLoopRunner.execute()` / `StageTransitionMixin`

The runtime executor itself performs mission work and can call `_maybe_decide_stage_transition`, and `StageTransitionMixin` calls the Manager stage writer. These modules do **not** intrinsically acquire the Manager pipeline lock around themselves.

For the resident daemon this is safe because their caller is inside `_rf_main_loop`'s outer lock.

This run did not establish a current public production embedding that calls the same runtime stage-writing path outside that lock. Therefore:

- supported: the leaf runtime does not self-enforce lock ownership;
- not yet supported: a current non-daemon production path actively bypasses the lock.

The historical direct-import completion incident remains evidence that wrong-path access to the primitive has happened before, but current bypass reachability should be proven per embedding rather than assumed.

## Finding C — post-mutation CampaignControlStore revision is observability/reconciliation, not pre-mutation authorization

`apps/_runtime_stage_transition.py` records a `CampaignControlStore` projection **after** `Manager.decide_stage_transition()` has already written the pipeline stage. The projection includes a SHA-256 of the resulting pipeline state and then advances/returns a campaign-control `state_revision`.

That is useful durable reconciliation evidence, but it cannot by itself provide the missing low-level CAS property because the state revision is not required/consumed as a precondition by `advance_stage`, `rollback_stage`, `reset_stage_for_replacement_intent`, or `complete_final_stage`.

A stale/wrong-path caller therefore cannot currently be rejected by saying “this authorization covered pipeline/control revision N, but the live state is N+1” at the stage primitive itself.

## Finding D — the candidate should protect semantic authority, not duplicate the existing outer lock

The smallest justified architecture is now more precise:

1. retain the existing Manager pipeline lock for normal orchestration serialization;
2. keep the deterministic completion/evidence gates already present;
3. add a host-issued transition authorization that identifies the exact semantic operation and exact state snapshot it covers;
4. make the low-level durable mutator reject calls that do not carry/consume that current authorization;
5. bind mutation to an exact durable revision/digest so a capability authorized against stale state cannot overwrite a newer route/stage state;
6. keep read-side completion/authority revalidation for pre-existing or externally corrupted durable state.

The capability and revision check cover distinct properties:

- capability: *this host path is authorized to perform this transition kind/from/target*;
- revision/CAS: *the durable state is still exactly the state that authorization evaluated*.

The existing lock remains useful and should not be replaced. The new primitive contract is defense-in-depth against stale/direct/embedded callers and makes security/safety invariant independent of one particular call graph.

## Secret-readability matrix — current run refinement

The previous run's scope correction remains supported, and the freshest public sandbox chokepoint makes the default/workspace-write distinction explicit:

| Layout | Relevant public behavior | Manager-state plaintext nonce should be treated as unreadable? |
|---|---|---|
| default safe-mode OFF | `_apply_sandbox_policy()` forces `sandbox_mode=None`, `isolate_workdir=False`, `dangerous_yolo=True` | **No.** No filesystem read isolation is established. |
| Codex safe-mode `workspace-write` | command builder pins writable workspace/allowlist and explicitly describes this as write confinement; it does not establish a read deny for Manager state | **No, not from this control alone.** It protects writes, not universal reads. |
| `isolate_workdir=True` path | separate backend isolation path exists and may hide broader host roots depending on backend/OS/layout | **Potentially, but not universally established.** Exact Manager-state mount/read reachability remains a per-layout test target. |

No exploitability claim follows from readability alone. In particular, the existing validator-repair host claims the authorization and begins its one acceptance retry before invoking the Engineer, so later discovery of the plaintext nonce does not automatically recreate an unused authorization.

## Tested scope / uncertainty

- Public-source/call-path audit only; no unauthorized state mutation or secret exfiltration was performed.
- `lbx154/Argus@962cb065...` is the exact public source revision audited.
- Normal resident-daemon stage mutation and Manager route commit paths inspected here are serialized by the existing Manager pipeline lock. This run does **not** claim a normal-path concurrency bug.
- The low-level stage/route mutators remain without authenticated caller capability or exact state-revision CAS. This is an authority/defense-in-depth property, not a measured benchmark-performance claim.
- A concrete current production embedding outside the outer lock was not yet proven.
- Isolated-workdir Manager-state readability is not generalized across OS/backend/custom home layouts.

## Nonempty frontier

1. Trace every non-daemon/public embedding of `_SkillLoopRunner.execute()` and `Manager.decide_stage_transition()` and determine whether any production path can reach a stage mutator outside `manager_pipeline_lock`; if none is found, explicitly downgrade current bypass risk to historical/defense-in-depth rather than present production reachability.
2. Finish the Manager-state readability matrix with exact path/environment flow for default, Codex `workspace-write`, POSIX isolated-workdir, and any materially different non-POSIX path. Keep “file readable” separate from “authorization still usable.”
3. Inspect the direct CLI `persist_vertical` use and determine whether it can mutate a live session's route state without the Manager pipeline lock, or whether it is initialization/admin-only.
4. Search a separate public agent/runtime for a tested combination of opaque host-held authority **and** exact durable-state revision rejection at the actual state/tool mutation boundary, stronger than human confirmation alone.
5. Monitor fresh Argus upstream history/issues/PRs for stage-capability or lock/revision migration and compare rather than duplicate it if it appears.
6. Preserve the unresolved Memento Table-4 control-operator provenance question as a secondary branch; resume it only on new paper-era artifact evidence.

## Exact continuation

Start with non-daemon embedding reachability: enumerate public callers of `_SkillLoopRunner.execute()` and `decide_stage_transition()`, classify whether each obtains `manager_pipeline_lock`, and isolate any real production bypass. Then inspect the exact sandbox/mount/env construction for `isolate_workdir` to finish the Manager-state readability table. Finally inspect the CLI `persist_vertical` call under the same lock/active-session lens and search one independent runtime for an opaque host capability bound to exact state revision. Keep the candidate focused on primitive-bound semantic authority + stale-state rejection, not on a normal daemon race that the current outer lock already prevents.
