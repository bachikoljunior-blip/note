# Primary verification — Argus continuous-state writer authority

Verified: 2026-08-27T17:00:15+09:00

## Frozen verification scope

- Clean candidate family: `open_source/clean-os-g1-005`
- Public source: `lbx154/Argus@33da786bbc6787a2eeb63a5f492498eae87c78c7`
- Verifier semantic control tuple remains frozen at note `305fdde1549531bd213975ae076df9ee4c6247a1`, DESIRED_STATE control revision 11, DOWNSTREAM_STATE revision 19, `primary_source_verifier` config revision 5.
- Read-only audit. No Argus mutation, exploration-worker mutation, or worker-feedback write.

## Verdict

The pinned Argus source has a strong CAS path for the primary Manager continuous handoff, and several planner/daemon terminal-disarm paths also use exact-state CAS. But the same `continuous.json` semantic authority is also mutated by several production **non-CAS rearm/write paths**. The clearest current gaps are:

1. Web `start_project_daemon(..., resume_continuous=True)` can re-enable any disabled state whose `done_reason` merely starts with `"operator "`, before daemon-capacity admission. This is broader than the daemon boot helper, which only rearms the exact two `RESUMABLE_STOP_REASONS`. Therefore an operator hold/other operator-semantic stop can be re-enabled by this Web path, and the campaign can remain durably enabled even if the subsequent daemon start is rejected by the active-daemon limit.
2. Immediate and scheduled daemon upgrades snapshot `continuous.enabled/objective`, then later use `write_continuous_config(... enabled=True, objective=<snapshotted objective>)` rather than expected-state CAS. A semantic continuous-state change after the snapshot but before restart is therefore not fenced by generation/objective/done_reason equality.
3. Pending-question replay/resolution uses `_reconcile_campaign_after_decision()`: if the current continuous state has any nonempty objective and is disabled, a non-stop decision writes it enabled with no check that the decision card/revision is bound to the current continuous generation or done reason. Crucially, the **already-applied replay path calls this reconciliation again**. A stale replay of an old non-stop decision can therefore re-enable the *current* disabled objective, including a newer objective/stop state, as long as it is nonempty. This is source-reachable and more specific than the generic claim that all non-CAS writes are unsafe.
4. Daemon boot `_rearm_operator_drain_for_resume()` is narrower: it rearms only exact process-stop reasons (`operator drain-stop` or graceful SIGTERM/SIGINT). It still performs a read-then-non-CAS write, so a concurrent semantic change between the passed-in state snapshot and the write is not checked, but it should not be conflated with Web start's broad `startswith("operator ")` behavior.

By contrast, explicit operator `/continuous stop` and Web `disable_manager_continuous()` call `disable_continuous_config()`, which deliberately acquires the continuous lock, reads the **latest** state, preserves its current objective, increments generation, and disables it. These are current operator-authority surfaces, not stale-background rearm evidence by themselves. They still would need explicit first-class fence semantics if `handoff_fence` is added, because the current state type cannot preserve such a field, but the present source does not justify labeling every explicit stop as a bug.

## Current write primitives

### `write_continuous_config`

- acquires `.continuous.lock`;
- reads the current state under that lock;
- writes caller-supplied enabled/objective/done reason at `current.generation + 1`;
- has **no expected-state comparison**.

The lock serializes physical writes, but does not make a stale semantic snapshot safe: a caller may have captured an objective/reason before taking this lock and then overwrite a newer state with a fresh generation.

### `compare_and_swap_continuous_config`

- acquires the same lock;
- reads the current state;
- checks `_same_continuous_state(current, expected)` across enabled/objective/open-ended/done reason/done timestamp/generation;
- writes only on exact match.

This is the current exact semantic-freshness primitive for the six first-class fields.

### `disable_continuous_config`

- acquires the lock;
- reads latest state inside it;
- writes `enabled=False` while preserving the latest objective/open-ended and incrementing generation.

It is a latest-state operator/control primitive, not an expected-state transaction.

## Production caller classification

### A. Exact-state CAS / comparatively strong current semantics

**Primary Manager continuous handoff** — `manager.front_door.manager_continuous_handoff()` freezes `expected_state`, and its final replacement uses `compare_and_swap_continuous_config(expected=expected_state, before_write=_commit)`. The callback durably commits Manager route/backlog work before the final continuous replace, with explicit ambiguity errors if the replace/durability outcome is uncertain. This remains the strongest current semantic handoff path.

**Planner project-done disarm** — daemon main loop reads current state and only disables when its adopted generation equals the live generation; then it uses CAS against that exact current state. This prevents a planner terminal verdict from disarming a later rewritten campaign.

**Content-filter permanent block disarm** — planner verdict path reads current state and uses exact-state CAS to disable with a specific done reason. This does not blindly disable a newer rewrite.

Other CAS call sites exist and should retain exact-state treatment; this audit focused on the contrast with non-CAS rearms below.

### B. Non-CAS rearm: Web daemon start

`webapi/daemon_lifecycle.start_project_daemon()` does, before daemon-capacity admission:

- read `continuous`;
- if `resume_continuous=True`, state disabled, objective nonempty, and `done_reason.lower().startswith("operator ")`, call `write_continuous_config(enabled=True, objective=continuous.objective)`;
- only afterwards compute daemon limit / active daemon count and possibly return admission-required.

Two exact implications follow:

1. **Reason overbreadth**: daemon-state source defines only `operator drain-stop` and `operator stop (graceful SIGTERM/SIGINT — clock out)` as resumable. `startswith("operator ")` additionally admits work-semantic reasons such as an operator hold/stop phrase.
2. **enable-before-admission**: if capacity is full, the function can return without a daemon while the continuous file has already been rewritten enabled.

This is source-level behavior at the pinned commit. No production incident frequency was measured here.

### C. Non-CAS rearm: immediate/scheduled daemon upgrade

`webapi/daemon_upgrade.upgrade_project_daemon()` snapshots `continuous = read_continuous_state(life_dir)` before stopping the daemon. If the original daemon exits immediately and `continuous.enabled` was true, it calls `write_continuous_config(enabled=True, objective=continuous.objective)` before starting the replacement daemon.

When draining is scheduled, the durable upgrade request stores `resume_continuous` and `objective` from the earlier snapshot. `_complete_scheduled_daemon_upgrade()` later reads that request and, if `resume_continuous`, writes the stored objective enabled with `write_continuous_config()` before starting the daemon. The request verifies daemon/source identity, but it does not bind the stored continuous objective to an expected `continuous.json` generation/done reason at final rearm.

So process identity is fenced better than semantic campaign freshness. This does **not** prove an upgrade normally corrupts campaigns; it proves a concurrent semantic rewrite is not rejected by expected-state equality.

### D. Non-CAS rearm: pending-question decision/replay

`webapi/manager_pending_question._reconcile_campaign_after_decision()` reads `before = read_continuous_state(mem.project_root)`. For a non-stop decision, if `before.objective.strip()` and `not before.enabled`, it calls `write_continuous_config(enabled=True, objective=before.objective)`.

`manager_resolve_operator_decision()` invokes this not only for a newly accepted decision, but also when `_resolved_decision_replay()` reports `application_status == "already_applied"`.

The reconciliation condition does **not** require:

- matching a continuous generation captured when the decision was resolved;
- matching a done reason that says the decision is allowed to resume it;
- matching the decision's continuation mission/objective identity to the current continuous objective.

Therefore an old, exactly replayed non-stop decision can cause a fresh enable of whatever nonempty objective is currently in `continuous.json` if that current state is disabled. The card-level replay remains idempotent with respect to the backlog decision, but its continuous-state projection is not idempotent with respect to newer continuous semantic authority.

This is a concrete source-reachable authority mismatch. It is not evidence that such a race/replay has occurred in production.

### E. Narrow non-CAS rearm: daemon boot after process stop

`daemon._life_worker_identity._rearm_operator_drain_for_resume()` requires:

- launch is `resume_continuous` rather than a fresh explicit `continuous` launch;
- state is disabled;
- `done_reason` is exactly in `RESUMABLE_STOP_REASONS`;
- objective is nonempty.

It then writes enabled with `write_continuous_config()` and rereads the result. The semantic predicate is substantially safer than Web start's prefix test. But because the function receives a previously-read `ContinuousConfigState` and the write has no expected-state CAS, a concurrent rewrite in the interval is not rejected.

## Scope corrections to the clean candidate

1. The proposed `PRESERVE/CANCEL/FINALIZE/REFUSE` fence policy is **not implemented** today. Do not describe current callers using those labels as if they enforce them.
2. Current source already distinguishes stronger and weaker writer classes. Manager handoff and planner terminal disarms use CAS; Web/upgrade/pending-question/boot rearm surfaces use non-CAS writes. The design problem is therefore targeted, not “all continuous writes are unfenced.”
3. Explicit operator stop surfaces are semantic authority, not evidence of stale background overwrite merely because they use `disable_continuous_config()` rather than CAS.
4. The strongest presently verified rearm defect is the pending-question **already-applied replay** projection: its backlog decision may be old while its continuous projection acts on the current disabled objective with no generation/done-reason binding.
5. Web start's broad `startswith("operator ")` behavior is independently overbroad relative to the exact resumable-stop set defined in daemon state, and occurs before capacity admission.
6. Upgrade requests fence process/source identity but not the snapshotted continuous semantic identity.
7. `handoff_fence` remains a proposed first-class field. Because current `ContinuousConfigState` drops unknown fields and `_same_continuous_state` compares only the six known fields, adding a JSON-only fence would not solve these paths.

## Evidence class

- Writer primitive behavior and listed caller control flow: **source-verified at pinned commit**.
- Pending-decision replay rearm, Web resume-before-admission, and stale upgrade-snapshot overwrite: **source-reachable control-flow implications**.
- Production frequency or user-impact incidence: **unknown; not measured**.
- Proposed first-class fence policy effectiveness: **untested design hypothesis** until implemented and exercised by fault/replay regressions.

## Exact next verification

Rotate to the current clean worker's proposed durability/replay half rather than continuing static caller enumeration. At the same pinned Argus commit, inspect the real `Backlog` insertion/update/event semantics around `manager_continuous_handoff` and determine whether an ambiguous/failing final continuous replace after the durable Manager callback can be retried/recovered without duplicate physical mission rows or duplicate task-added events. Distinguish current idempotency guarantees from the worker's proposed pre-reserved mission ID / immutable creation identity / exact recovery protocol. If current code already provides identity-stable retry, narrow the proposal; if not, construct a source-exact replay counterexample without mutating the public repository.