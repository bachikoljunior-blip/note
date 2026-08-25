# Open Source clean_g1 — Argus mutation-authority matrix

Continuation of the 04:01 run under control revision 6 / open_source config revision 3. Clean-exploration boundary unchanged.

Public source pinned: `microsoft/ArgusAgent@455da6cb2fe10e9fbaeab5126f2f3b363237cf57`.

## Matrix

| Mutation path | Evidence / semantic gate before write | Caller / capability gate before write | Durable mutation | Read-side revalidation |
|---|---|---|---|---|
| `advance_stage` via Manager `_apply_stage_decision_to_disk` | Stronger: Manager parses Reviewer evidence/checklist; low-level `_advance` reruns deterministic `_ensure_stage_completion` and fails closed if validator unavailable/fails | **No secret or revision-bound capability.** Host routing uses ordinary `holds_stage_authority` bool; low-level `advanced_by` is free text | `_set_stage` -> `write_pipeline_state` atomic replace | completion certificate checks exist for completed state, but no general actor authentication record |
| `complete_final_stage` via Manager | Stronger: Manager derives `_allow_early_completion` from authoritative workflow mode + non-open-ended condition; completion blockers/checklist; low-level `_complete` reruns stage validator and re-derives direct-mode backstop | **No secret capability.** `completed_by` free text; `allow_early_completion` remains a boolean at primitive boundary. Current host route derives it rather than trusting model output, but direct import caller can still pass it; code says "lock, not signature" | `_set_stage(direction="complete")` atomic write | `vertical_completion_certificate_status` rechecks final/early workflow legitimacy and contract fingerprint, but fingerprint is not actor authentication |
| `rollback_stage` via Manager / planner request / supervisor guard | Stage target must be earlier; surrounding host logic may have Reviewer/planner reason, but low-level rollback has **no deterministic evidence validator** | **No secret/revision-bound capability.** `rolled_back_by` free text | `_set_stage(direction="rollback", downgrade_downstream=True)` atomic write | rollback history provides audit trail, not authority authentication |
| `reset_stage_for_replacement_intent` | Known target stage only; semantic wrapper says Manager-confirmed replacement. No `_ensure_stage_completion`. Forced replacement can bypass prior-terminal requirement | **No secret/revision-bound capability.** `reset_by` free text | `_set_stage(direction="reset", downgrade_downstream=True)`; reset can land on same or other known stage and makes it actionable | no equivalent actor/capability revalidation found |
| `persist_vertical` / route contract write | validates vertical/domain/workflow/target values; anti-clobber rule avoids overwriting existing stage | **No secret/revision-bound capability at function boundary** | `write_pipeline_state` atomically changes route semantics | route readers validate known values, but no actor authentication |
| Restricted validator repair (`CampaignControlStore`) | Reviewer diagnosis must identify validator defect; frozen evidence/tree/write baselines; exact action and allowed paths | **Yes.** host-held random nonce, campaign/objective/epoch + exact Manager state revision, one-shot authorization/capability, expiry/action scope, mission/validator binding; nonce not put in model prelude or runner kwargs | immutable revision snapshot + HEAD commit point; authorization consumed; active capability one-shot; close clears capability | claim/start/close each recheck state/evidence/tree; interrupted acceptance recovered as rejected; tests cover stale/race/symlink/drift cases |

## Important stage-authority nuance

The current runtime DOES have an explicit host eligibility control: `holds_stage_authority` is checked first in `_should_run_stage_transition`, and dispatched teammates pass `holds_stage_authority=False`. Public tests assert both the unconditional precedence of this flag and that teammate entry actually passes it.

That is materially better than allowing every mission to reach the Manager stage writer. However it is still an in-process ordinary boolean, not a durable one-shot capability consumed by the stage mutator. Once a path reaches `Manager.decide_stage_transition`, `_apply_stage_decision_to_disk` calls `_advance`, `_complete`, or `_rollback` without presenting a secret/revision-bound transition authorization.

The post-write `CampaignControlStore.clear_wait_for_new_evidence(...)` in `_runtime_stage_transition.py` records the resulting stage projection and terminal review in a new Manager control revision. That is useful durable projection/observability, but it happens **after** `Manager.decide_stage_transition` has already written `PIPELINE_STATE.json`; it does not authorize the write.

## Early completion is host-derived on the normal path, but primitive authority remains forgeable

A useful scope correction: `allow_early_completion` is not simply copied from model text in the normal Manager route. `_parse_and_finalize_stage_decision` derives it as:

`not open_ended and resolve_workflow_mode(root) == "direct"`

and `_apply_stage_decision_to_disk` re-derives a direct-mode backstop before calling `complete_final_stage`.

So the normal route has strong host mediation. The residual architectural gap is at the privileged primitive boundary: `complete_final_stage` accepts the boolean and free-text actor but no unforgeable/revision-bound capability, exactly as its own docstring acknowledges.

## Refined implementation candidate

The best transferable change is now narrowly specified:

1. Keep `holds_stage_authority` as a cheap routing guard.
2. After Manager forms a transition decision, host control code mints a one-shot `StageTransitionCapability` using the existing `CampaignControlStore` pattern.
3. Bind it to campaign/objective/epoch, exact Manager HEAD revision, route/workflow digest, `from_stage`, transition kind, allowed target(s), decision/plan/mission id, and the relevant evidence/checklist fingerprint.
4. Keep the nonce host-side; model sees only public decision/scope, as validator repair already does.
5. Low-level `_advance/_rollback/_reset/_complete` (or a single mediator above `_set_stage`) must consume the capability atomically and reject stale/reused/mismatched transitions before any `PIPELINE_STATE` mutation.
6. Keep current deterministic evidence validators and read-side certificate checks; capability authorization is additive, not a replacement for evidence validity.
7. Add negative tests analogous to `test_control_state.py`: stale revision, wrong transition kind/target, route change after minting, reused capability, and unauthorized caller must leave `PIPELINE_STATE.json` byte-identical.

## Test-gap observation

Searches in the current public tree found tests that verify `holds_stage_authority=False` prevents a teammate from reaching the stage writer, but this worker did not find a test that directly invokes a privileged low-level rollback/reset with an unauthorized/stale authority object and asserts byte-identical `PIPELINE_STATE` rejection. This is expected because no such authority object exists on those primitives today; it is a concrete regression-test gap for the proposed design rather than proof of an exploit.

## Exact continuation

1. Inspect supported Engineer sandbox layouts to test whether Manager state-root authorization logs/nonces are physically outside model-readable mounts; keep interface confinement and filesystem confinement separate.
2. Trace all `persist_vertical` / route-contract mutation entry points and determine which should share the same transition capability or route-revision CAS to eliminate route-transition TOCTOU.
3. Search Argus history/issues for any pending/private-public mention of migrating stage authority onto `CampaignControlStore` so the candidate is not duplicating an already-planned fix.
4. Seek an independent open-source system with host-held capability/token authorization for semantic durable-state transitions and adversarial tests, to avoid overfitting the recommendation to Argus's own architecture.
5. Preserve the Memento Table-4 protocol branch as secondary until new primary artifacts appear.
