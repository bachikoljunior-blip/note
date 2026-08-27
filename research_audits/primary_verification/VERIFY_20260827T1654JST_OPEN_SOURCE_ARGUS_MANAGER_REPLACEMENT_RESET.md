# Primary verification — Argus Manager replacement/reset semantics

Verified: 2026-08-27T16:54:04+09:00

## Frozen verification scope

- Clean candidate: `open_source/clean-os-g1-005`
- Public source: `lbx154/Argus@33da786bbc6787a2eeb63a5f492498eae87c78c7`
- Verifier semantic control tuple: note `305fdde1549531bd213975ae076df9ee4c6247a1`, DESIRED_STATE control revision 11, DOWNSTREAM_STATE revision 19, `primary_source_verifier` config revision 5.
- This audit is read-only against Argus and does not modify exploration-worker state or feedback.

## Verdict

The current formal Manager replacement path does **not** ordinarily substitute `research` when a project-local/custom provider is already missing or corrupt: for an existing custom vertical, `Manager._commit_vertical_decision_locked()` computes `stages = self.plan_stages(vertical)` before `persist_vertical(...)`, and `plan_stages()` calls `load_vertical_contract(..., project_root=self.project_root)`. `load_vertical()` raises `LookupError` when the project-local provider cannot be strictly loaded. Therefore a missing or malformed custom provider causes the formal commit to fail before the route write rather than silently becoming a built-in research replacement.

However, the replacement transaction still lacks a strict postcondition/receipt binding the final persisted route and reset to the exact intended provider. `reset_stage_for_new_intent(..., force_replacement=True)` returns a boolean, but both existing-vertical and newly-authored-domain commit branches ignore that return value. The helper itself deliberately catches provider/reset errors and returns `False`; the Manager can therefore finish the route commit without proving that the replacement reset actually happened. `PreparedManagerHandoff.commit()` then returns the `Division`, and the continuous handoff proceeds to its final continuous-state CAS without a direct read-back of exact vertical/domain/provider digest/current-stage/reset-history postconditions.

There is also a narrower fallback race inside the reset primitive: `reset_stage_for_new_intent()` first strictly loads the target provider to derive `new_order`, but `stage_machine._set_stage()` independently re-resolves the active stage contract through `_active_vertical_checklist_defs()`, which falls back to the research contract on any provider-resolution error. If a valid custom provider disappears or becomes corrupt **between those two resolutions**, and its intended first-stage name is also valid in the research stage order, `_set_stage(direction="reset")` can proceed against the research order instead of the custom order. If the first-stage name is not in the research order, `_set_stage` raises `ValueError`, which the reset helper converts to `False`. This is a source-reachable TOCTOU/fallback edge under an external/non-cooperating state mutation, not an observed production incident and not shown by the normal serialized Manager path alone.

## Source evidence

### 1. Formal replacement ordering is fail-hard before persistence for missing/corrupt existing custom providers

At the pinned commit, `_commit_vertical_decision_locked()` does the following on `decision.choice == "existing"`:

1. materializes a learned data domain if available;
2. computes `stages = self.plan_stages(vertical)`;
3. calls `persist_vertical(...)`;
4. calls `reset_stage_for_new_intent(...)`;
5. adopts the operator objective;
6. returns a `Division` built from the decision.

`plan_stages()` explicitly uses `load_vertical_contract(vertical, project_root=self.project_root)` and documents that a missing/broken provider fails visibly rather than substituting another vertical. In `_base.py`, `load_vertical()` checks built-ins/plugins and then `load_data_domain(cleaned, project_root)`; if none resolves, it raises `LookupError("unknown vertical: ...")`.

This means a custom domain that is already missing or malformed at commit-time does not reach the route persistence/reset step through the formal Manager existing-vertical path.

### 2. `require_vertical()` alone is insufficient for corrupt-but-present custom domains

`vertical_select._known_vertical()` accepts a project-local slug when `data_domain_exists()` is true. `data_domain_exists()` checks only whether `<project>/research/DOMAINS/<name>.json` is a file. By contrast, `load_data_domain()` returns `None` for malformed JSON, malformed/non-dict payload, or a domain with no stages.

So a corrupt-but-present custom file can pass name validation while failing strict provider loading. The formal Manager path is protected by the earlier `plan_stages()` strict load; any future reconciliation receipt must likewise perform strict `load_vertical()`/contract resolution, not only `require_vertical()`.

Pinned tests explicitly cover `load_data_domain()` returning `None` for missing and corrupt files.

### 3. Built-in research forced replacement has direct regression coverage

Pinned test `test_force_replacement_resets_inprogress_pipeline_immediately` starts an in-progress research pipeline at a later stage, calls `persist_vertical(root, "research")`, then `reset_stage_for_new_intent(... force_replacement=True)`. It asserts:

- reset returned `True`;
- `current_stage == "research"` (the first research stage);
- target research stage becomes `in_progress`;
- downstream `plan` and `review` states become `pending`;
- newest `stage_history.direction == "reset"`.

This is repository regression coverage at the pinned source, not an independently re-run verifier experiment in this environment.

### 4. Same-first-stage replacement is semantically a real reset

`_set_stage(direction="reset")` intentionally has no strict earlier/later index condition. It may land on the same first stage to clear stale completion state. On `direction == "reset"`, it forces the target-stage record to `status="in_progress"`, downgrades downstream records whose status is in `{done, ready, in_progress, skipped}` to `pending`, appends `stage_history`, and (for the replacement wrapper) legacy `rollback_history`.

Therefore a strict postcondition cannot conclude success merely because `current_stage` already equals the first-stage string. A fresh reset history entry and actionable target/downstream cleanup are load-bearing evidence.

### 5. Valid custom domains can reset using their own order, but no strict final binding exists

Pinned tests cover a completed custom domain `same_math_family` with order `scope -> solve -> review`: after re-persisting the same custom vertical, `reset_stage_for_new_intent()` resets `review -> scope`, and the custom domain no longer appears terminal. Another regression covers a finished custom vertical switching to built-in research and resetting a stale shared stage name instead of inheriting false progress.

Those tests establish custom-domain stage-order support. They do **not** establish a current `ManagerReconcileReceipt`, domain-definition digest binding, or a post-mutation readback that proves the domain file and pipeline state still name the exact same provider after a standing replacement.

## Scope corrections to the clean candidate

1. **Do not claim** that the normal formal Manager replacement silently falls back to research merely because a custom domain is already missing/corrupt. Existing custom-provider commit is fail-hard at `plan_stages()` before persistence.
2. **Do retain** the need for a strict direct-read reconciliation receipt. Current Manager code ignores reset success/failure and has no exact postcondition binding route/provider/domain/current-stage/reset history after mutation.
3. **Do retain** the custom-domain distinction: file existence/name validation is weaker than strict provider loading.
4. **Do retain, but narrowly scope**, the research-fallback hazard: availability-oriented stage helpers can fall back to research, creating a source-reachable TOCTOU edge if the provider changes between strict target-order resolution and `_set_stage()` re-resolution. This is not a demonstrated normal-path or production failure.
5. `handoff_fence`, `creation_stamp`, strict `ManagerReconcileReceipt`, and provider/domain digests remain proposed design elements, not current Argus guarantees.

## Evidence class

- Current formal-path ordering and missing/corrupt custom-provider behavior: **source-verified at pinned commit**.
- Built-in research forced reset and completed custom-domain reset: **covered by pinned repository unit tests inspected here; not independently executed by this verifier**.
- Provider-disappears-between-two-reset-resolutions race: **source-reachable by control/data-flow inspection only**.
- Production incidence/frequency: **unknown; not observed or measured**.

## Exact next verification

Rotate away from the already-audited reset shape and inspect the same pinned Argus commit for the proposed strict-receipt boundary's remaining authority gap: enumerate production callers that can mutate continuous state (`write_continuous_config`, `compare_and_swap_continuous_config`, `disable_continuous_config`) and determine which current callers can enable/rearm/disable after a semantic handoff without any first-class fence. Separate current caller behavior from the clean worker's proposed `PRESERVE/CANCEL/FINALIZE/REFUSE` policy; prioritize source-reachable paths where a process/admin operation can clear or overwrite semantic authority without exact expected-state binding.