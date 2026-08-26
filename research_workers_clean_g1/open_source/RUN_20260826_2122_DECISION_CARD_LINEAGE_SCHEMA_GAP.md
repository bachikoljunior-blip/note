# Open Source Systems Scan — decision-card lineage schema gap

Role `open_source`; frozen note control tuple remains `31face47d7ee4b9b686ee3ae55fb9dbdeb877284` / control 10 / config 5 / role blob `118f440957ba4654e804af902aa09a9224acca43`. Public source remains `lbx154/Argus@8c5a0e356c470ad4cbdc904a7fbe4de14af366cf`.

## Result

The existing operator-decision schema has no generic execution-lineage binding. `core/operator_decision.py::build_operator_decision()` persists item id, card revision/status, question, evidence, options, and optional project id, but not continuous generation/objective identity, protected route revision, wait-contract id, or disable reason.

The backlog *does* already have `authorization_id` / `authorization_action` and continuation creation preserves those fields. However current Planner validation only accepts these for the specific `validator_repair` action backed by `CampaignControlStore`; they are not a generic operator-decision/wait capability. So reusing them blindly would conflate a restricted repair capability with broader semantic-resume authority.

This makes the minimal safe change clearer: add a small decision-projection lineage object (or equivalent fields) at the decision/backlog layer rather than overloading validator-repair authorization. At minimum bind the card/blocked item to the continuous generation/objective and protected route revision that created the question. Preserve card acceptance across later generations, but require current Manager reconciliation before the answer can release a different generation/route.

## Disable-reason classification

Public current-main paths show a clean separation that can be made explicit:

- process-resumable reasons: only the exact existing `RESUMABLE_STOP_REASONS` used by boot re-arm (operator drain-stop and graceful process stop); these are maintenance/process semantics;
- explicit semantic stop/pause/hold: empty done reason from ordinary `/continuous stop`, `operator pause`, `operator chose to stop the campaign`, `operator authority hold: ...`; these must not be released by raw process start or an old unrelated decision;
- terminal/system semantic stops: `planner declared project done`, content-filter reformulation-required; these also must not auto-resume.

The current raw Web start's `done_reason.startswith("operator ")` collapses process and semantic reasons, while the canonical boot helper already has the correct exact allowlist.

## Existing internal positive controls

- Manager continuous handoff uses full-state CAS and surfaces a distinct `ManagerHandoffSupersededError` when a newer generation wins.
- Planner terminal/content-filter paths and daemon project-done use CAS.
- exact operator-decision replay already reruns projection without duplicating the durable decision/continuation.

These pieces support a narrow implementation: card acceptance stays idempotent; projection returns an explicit superseded/reconcile-required state instead of rearming newer disabled semantics.

## Exact continuation

1. Inspect `Backlog.continue_with_operator_reply`/decision resolution storage to identify the smallest backward-compatible location for projection lineage fields and migration defaults.
2. Trace emergency PAUSE, ordinary `/continuous stop`, authority-hold, project-done and content-filter disable writers to define an exact semantic-resume policy table.
3. Inspect raw start/upgrade tests and add negative cases for every semantic disable class while retaining exact process-stop resume tests.
4. Map all Manager route mutations for protected route revision/digest; keep it independent of continuous generation.
5. Preserve the separate `PIPELINE_STATE` external/admin writer fencing branch.
