# Open Source Systems Scan — strict Manager receipt gate and first-class fence schema

Invocation started: 2026-08-27T16:00:38+09:00
Checkpointed: 2026-08-27T16:06:01+09:00

Frozen semantic tuple: `note@0bd5939eb9d153e20819a666a4276b8e61e796a0 / control 11 / open_source config 5` (`DESIRED_STATE` blob `bf7b8c7f6971c0ec2f3fa7a8d53dca1f88ac50a3`, role-config blob `118f440957ba4654e804af902aa09a9224acca43`). The second SHA-only note-main check matched before the first substantive semantic read. Note main later advanced; no newer control/config was adopted or used to reinterpret this invocation.

Public source frozen for this run: `lbx154/Argus@33da786bbc6787a2eeb63a5f492498eae87c78c7`, verified current `main` by SHA-only Git-ref lookup. Only own clean state and public source were used.

## 1. Strict Manager receipt minting must bypass all research fallbacks

The predecessor identified a strict no-fallback receipt as the authority proof required before a disabled handoff fence can be finalized. Source inspection now makes the rule exact.

The normal stage helpers are intentionally availability-oriented:

- `stage_machine._active_vertical_checklist_defs()` falls back to research on any vertical-resolution/provider error;
- `stage_machine.current_stage()` also derives its fallback stage from that helper;
- `vertical_select.resolve_vertical()` retains a low-level research fallback when no Manager decision exists.

These are valid prompt/liveness behaviors but cannot mint authority.

A receipt mint helper must instead:

1. read the protected `PIPELINE_STATE.json` object directly;
2. require a nonempty persisted `vertical` field;
3. call `require_vertical(persisted_vertical, project_root)`;
4. call `load_vertical(persisted_vertical, project_root=project_root)` and derive the exact contract/stage order from that returned provider;
5. inspect the persisted `current_stage`, `stages`, `stage_history`, and `rollback_history` directly, without `current_stage()` or `_active_vertical_checklist_defs()`;
6. only after all strict checks pass, canonicalize the full protected pipeline JSON object and mint its digest into the Manager reconciliation receipt.

### New custom-domain distinction: `require_vertical` is necessary but not sufficient

For a project-local data domain, `require_vertical()` ultimately uses `data_domain_exists()`, which checks only whether `<project>/research/DOMAINS/<name>.json` exists as a file. `load_data_domain()` is stricter: malformed JSON, malformed payload, or no stages returns `None`; then `load_vertical()` raises `LookupError` instead of silently returning research.

Therefore the receipt gate must perform both checks. The exact negative regressions are now:

- **missing domain file**: `require_vertical()` fails; no receipt;
- **corrupt domain file that still exists**: `require_vertical()` can still accept the name because the file exists, but `load_vertical()` must fail; no receipt and no research fallback;
- **valid domain**: strict load succeeds and its exact stage order is used.

This is stronger than a generic “custom domain must exist” check and directly prevents a corrupt-but-present domain from becoming authority.

## 2. Source-shaped reset receipt postconditions

`reset_stage_for_replacement_intent()` delegates to `_set_stage(direction="reset", downgrade_downstream=True, legacy_rollback_history=True)`.

A successful strict replacement receipt should verify the source-exact postconditions rather than infer success from route fields alone:

- persisted `current_stage` equals the exact first stage from the strictly loaded target provider;
- target stage record exists and `status == "in_progress"`;
- no downstream stage retains a status in `{done, ready, in_progress, skipped}`;
- the newest `stage_history` entry has `direction == "reset"`, `to_stage == first_stage`, and Manager ownership;
- the newest legacy `rollback_history` entry names the same target/reset authority;
- route/provider identity still resolves strictly after reset.

Important nuance: `_set_stage` creates missing downstream stage records but does **not** force every fresh empty record to `pending`; it only rewrites an existing status in `{done, ready, in_progress, skipped}` to `pending`. A receipt that requires every downstream status to equal `pending` would falsely reject legitimate fresh state. The correct invariant is that no downstream stage remains in an actionable/terminal-progress status from the superseded objective.

### Executable cases now map directly onto existing tests

1. **Built-in research replacement** — extend the existing forced replacement pattern: begin at a later research stage with stale done/in-progress records, force replacement, then mint only if the strict direct-read postconditions above hold.
2. **Same-first-stage replacement** — begin with `current_stage="research"` but stale `research.status="done"` plus downstream progress. Forced replacement is still a real reset: target must become `in_progress`, downstream terminal/actionable statuses must be cleared, and a new `direction="reset"` history entry must exist. Receipt minting cannot treat “already at first stage” as a no-op.
3. **Project-local/custom-domain replacement** — use the existing `write_data_domain(...)` test helper, persist the custom vertical, force replacement, and bind the receipt to both the canonical pipeline-state digest and the exact domain definition digest. Then delete or corrupt the domain and assert no receipt can be minted. In the corrupt-file case, explicitly assert that the path still exists so the test covers the `require_vertical passes / load_vertical fails` distinction.

## 3. First-class `handoff_fence` touches every continuous-state serialization/equality seam

`ContinuousConfigState` currently contains only `enabled`, `objective`, `open_ended`, `done_reason`, `done_at`, and `generation`. The reader reconstructs only those fields; every whole-state write serializes only those fields. Unknown JSON keys are therefore dropped on the next read/write cycle.

A `handoff_fence` cannot be added as an ad-hoc JSON key. It must be first-class in all of:

- `ContinuousConfigState`;
- `_read_continuous_state_unlocked()`;
- `_continuous_state_reserve_text()`;
- `_write_continuous_config_unlocked()`;
- `write_continuous_config()`;
- `compare_and_swap_continuous_config()`;
- `disable_continuous_config()`;
- `_same_continuous_state()`;
- all state-portability/fault tests and any direct test constructors.

Two seams are especially safety-critical:

### 3.1 CAS equality must include the fence

`generation` is marked `compare=False` on the dataclass, but `_same_continuous_state()` manually compares every authoritative field including generation. If `handoff_fence` were omitted from this manual comparator, a writer holding an expected state from before a fence change could still pass CAS as long as the legacy fields matched. Therefore the fence identity/content must be part of `_same_continuous_state()`.

### 3.2 Reserve sizing must include the fence

The quota-recovery reserve size is derived from `_continuous_state_reserve_text(state)`. If the real continuous JSON gains a potentially nontrivial fence payload but reserve rendering omits it, the preallocated reserve can be too small precisely when a handoff write hits ENOSPC/EDQUOT. So first-class fence support must also serialize the fence into the reserve text used for sizing.

## 4. Generic writers need explicit fence action, not a boolean/default side effect

Current APIs can rewrite the entire continuous state without expected-state CAS (`write_continuous_config`, `disable_continuous_config`) or with CAS (`compare_and_swap_continuous_config`). Once a fence is first-class, an omitted argument cannot safely mean “clear it” or “copy whatever happened to be read earlier.”

The narrow contract remains the predecessor’s four actions:

- `PRESERVE`: keep the exact current fence;
- `CANCEL`: explicit newer semantic authority cancels it while staying disabled;
- `FINALIZE`: only strict Manager receipt + exact durable mission may clear it and enable target authority;
- `REFUSE`: process/admin shortcut is not allowed to mutate semantic fence authority.

Implementation-wise this needs a tri-state/sentinel-style field update or dedicated typed helpers, because `None` is already the natural representation of “no active fence.” A useful invariant for every writer is:

`handoff_fence != None  =>  enabled == False`

Any attempt to enable while preserving an active fence must fail closed rather than silently clear or bypass it.

## 5. Regression matrix added by this run

Strict receipt:

1. built-in research forced replacement mints receipt only after exact direct-read reset postconditions;
2. same-first-stage replacement still requires a fresh reset history entry and actionable target;
3. valid custom domain mints with pipeline + domain digests;
4. missing custom-domain file fails before mint;
5. corrupt-but-present custom-domain file proves `require_vertical` alone is insufficient and fails at strict `load_vertical` without research fallback.

Continuous fence serialization:

6. legacy continuous JSON without a fence reads `handoff_fence=None`;
7. round-trip preserves fence exactly;
8. reserve serialization/size includes the fence;
9. CAS expected-state comparison fails when only fence identity/content differs;
10. a whole-state disable with `PRESERVE` keeps fence exactly;
11. any `enabled=True` write while an active fence is preserved is rejected;
12. only typed `CANCEL`/`FINALIZE` paths may clear it, with `FINALIZE` requiring the strict receipt and exact durable mission.

## 6. Candidate refinement

`clean-os-g1-005` is now:

**first-class disabled handoff fence with explicit PRESERVE/CANCEL/FINALIZE/REFUSE semantics + strict direct-read Manager reconciliation receipt that never uses research-fallback helpers + exact custom-domain load/digest binding + source-exact reset postconditions + pre-reserved target mission ID + immutable backlog creation identity + atomic operator-priority exact insert + durable recovery + current-state-only process rearm.**

No Argus mutation, live daemon fault injection, unauthorized state change, or production benchmark was performed. Findings remain source-level behavior/design at the pinned public commit.

## Exact continuation

1. Turn the five strict-receipt cases above into literal pytest-shaped scaffolding using the existing `test_force_replacement_resets_inprogress_pipeline_immediately`, `write_data_domain`, and data-domain corruption helpers; specify exact helper signature for `mint_manager_reconcile_receipt(...)` and canonical digest inputs.
2. Enumerate every production caller of `write_continuous_config`, `compare_and_swap_continuous_config`, and `disable_continuous_config` and assign one of `PRESERVE/CANCEL/FINALIZE/REFUSE`, with special attention to daemon start, boot rearm, immediate/scheduled upgrade, operator decision, standing STEER, planner safety disarm, and semantic stop.
3. Build the real-Backlog final-continuous-replace ambiguity regression on the existing Manager handoff harness: exact mission insert succeeds, final continuous replace is ambiguous/fails, recovery executes twice, and only one physical mission plus one task-added event exists before one successful final enable.
4. Keep external/admin `PIPELINE_STATE` whole-object writer fencing and global JSON-state CAS as a separate candidate branch; do not broaden this result into a claim about all Argus state writers.
