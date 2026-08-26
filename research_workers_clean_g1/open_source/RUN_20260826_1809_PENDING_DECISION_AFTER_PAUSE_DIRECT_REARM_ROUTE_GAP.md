# Open Source Systems Scan — pending operator decision can directly re-arm a paused objective after route change

Role: `open_source` clean exploration.
Frozen semantic control tuple: note main `b0cc6f3ae62b88d7423e3fc1545d1b598c85381d`, control revision 10, role config revision 5, role config blob `118f440957ba4654e804af902aa09a9224acca43`.
Public source: `lbx154/Argus@16bb128992ea9d0c11b5bbca7a4f1d549dea84dd` (freshly verified before semantic work).

## Result

A second **live**, no-fresh-boot promotion path has the same missing Manager-route reconciliation as standing STEER: resolving a previously pending operator decision can directly re-enable the preserved continuous objective with `write_continuous_config()` after a PAUSE-era route change. This path is source-level reachable without requiring the pending decision itself to have disabled the campaign. No live exploit or unauthorized mutation was performed.

## Deterministic reachable sequence

1. Standing campaign A is active and one backlog item is already `paused_operator` with a durable `operator_decision` / `pending_question` card. Creating such a card does not need to end the campaign.
2. Operator issues PAUSE. `_handle_pause_control()` disables continuous with `done_reason="operator pause"`, requests abort only for a currently **running** item, and explicitly preserves the objective and backlog. The already-`paused_operator` decision card therefore remains available for later resolution.
3. While continuous is disabled, a fresh bounded handoff B is allowed to revise the persisted Manager route contract. It can keep the same or different vertical while changing workflow mode, research bar, target venue, stage-relevant state, etc.
4. The operator later resolves the old decision card through `manager_resolve_operator_decision()` / `manager_answer_pending_question()`. The answer is durably applied and a continuation item is created.
5. After a resolved non-stop decision, `_reconcile_campaign_after_decision()` reads `continuous.json`; if an objective exists and `enabled` is false, it directly calls `write_continuous_config(... enabled=True, objective=before.objective)`.
6. That helper does **not** call `manager_continuous_handoff`, `Manager.divide`, `commit_vertical_decision`, `_resume_matches_manager_handoff`, or any protected route-revision comparison. A resident daemon can therefore hot-reload objective A under B's newer route state, the same semantic mismatch class as the standing-STEER path.

## Decision identity is intentionally not tied to current campaign generation

The public regression `test_campaign_generation_change_does_not_block_pending_decision` sets a decision card's recorded `campaign_generation`, then writes a newer standing objective (advancing continuous generation), and explicitly asserts that resolving the old decision is still accepted. That is reasonable for preserving operator intent, but it confirms that the decision card itself is not a semantic credential for the current protected route. A route-revision check must therefore happen at **resume/re-arm projection**, not by simply declaring old decisions stale.

Idempotent replay also calls `_reconcile_campaign_after_decision()` for an already-applied non-stop decision, so replay is allowed to repair the continuous projection. The same route reconciliation rule must cover replay as well as first application.

## Refined invariant

Operator decisions should remain durable and resolvable across benign campaign/process generations. But any resolution that transitions continuous execution from disabled to enabled must:

- compare the preserved objective's last Manager handoff/protected route revision with current protected route revision;
- if equal, permit the cheap direct re-arm;
- if different, preserve the accepted operator decision but require a Manager route reconciliation before enabling execution;
- never infer route authority from decision-card idempotency, continuous generation, or backlog continuation identity alone.

This keeps durable human decisions independent from ephemeral routing while closing stale-authority reactivation.

## Regression

Create standing A and a pending operator decision D; PAUSE A; commit bounded B that changes protected route state; resolve D with a non-stop option. Current code can write `continuous.enabled=true` directly. Fixed code should record D as resolved and enqueue/retain its continuation, but leave execution disabled until Manager reconciles A against current protected route revision. Positive controls: same-route PAUSE + resolve D can resume directly; stop option stays disabled; replay under unchanged revision is idempotent; a generation-only process restart with unchanged route does not invalidate D.

## Scope limits

This is source-level reachability at the verified public commit. No live daemon, external service, capability, or production state was modified. The finding concerns the campaign projection/re-arm step, not the validity of the operator's selected decision itself.

## Exact continuation

Inventory every direct `enabled false -> true` continuous-state promotion and classify whether it performs Manager reconciliation: standing STEER, operator-decision projection/replay, Web/API explicit resume, CLI resume, upgrade/replacement, boot process-stop rearm, and any other live config writer. Then define one reusable `reconcile_or_rearm_continuous(expected_route_revision, objective)` boundary. In parallel finish the producer/consumer map for the protected route revision across Manager route writers, manager-handoff identity/event fallback, CampaignControl wait/authorization/capability, backlog manager_decision, Planner context and stage/route mutators; keep raw external/admin PIPELINE_STATE writers in a separate CAS/fencing matrix.