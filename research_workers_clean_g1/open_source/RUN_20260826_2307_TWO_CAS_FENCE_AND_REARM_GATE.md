# Open Source Systems Scan — two-CAS handoff fence + semantic rearm gate

Invocation started: 2026-08-26T22:57:11+09:00
Checkpointed: 2026-08-26T23:07:39.691762+09:00

Frozen semantic tuple for this invocation:
- note main SHA: `21c88a7daf463faf6f892c916aeb66945fa36003`
- sanitized control revision: `10`
- open_source config revision: `5`
- open_source config blob: `118f440957ba4654e804af902aa09a9224acca43`
- public Argus main: `8c5a0e356c470ad4cbdc904a7fbe4de14af366cf`

Independence: own clean state + public sources only. No O/O-derived state, other-worker state, downstream semantics, legacy research, shared aggregate ledger, or other-role receipt/config was used. The note head advanced after the first semantic read; this checkpoint remains bound to the frozen tuple above and does not adopt later control during this invocation.

## 1. `PreparedManagerHandoff.failed()` is observability, not recovery authority

`PreparedManagerHandoff.completed()` emits a rich `life.manager.intent.completed` event, while `failed()` emits `life.manager.intent.failed` containing the raw operator objective and error. Both go through `_emit_manager_event()`, whose event append is wrapped in a broad exception handler. Therefore the event tape is useful audit context but cannot be the sole crash-recovery carrier for a partially committed handoff.

This narrows the handoff-fence payload question: the disabled fence itself must preserve enough durable semantic input for replay. A minimal safe payload can use the same Manager-clean `prepared.execution_task` that successful continuous handoff already persists, rather than relying on a fail-soft event to recover the raw operator body.

## 2. Existing continuous-state machinery is already strong enough for a two-CAS protocol

Argus continuous state already has:
- a cross-process lock,
- full-state compare-and-swap including generation,
- atomic temp-file replacement,
- file `fsync`, parent-directory `fsync`,
- a disabled state that may retain a nonempty objective,
- exact process-stop allowlisting through `RESUMABLE_STOP_REASONS`.

The existing storage regression `test_replace_failure_after_callback_surfaces_instead_of_false` proves the critical low-level failure shape: a `before_write` side effect may commit, the later `continuous.json` replace may fail, the CAS raises, and the original continuous state remains unchanged.

The best protocol is therefore not a new transaction system, but **two exact CAS operations under the existing outer Manager pipeline lock**:

1. CAS old enabled state A -> disabled **handoff fence** containing B's Manager-clean execution task, the resolved open-ended bit, and a dedicated non-resumable reason such as `manager handoff reconciliation required`.
2. Read the exact resulting fence state (its generated `done_at` is part of state equality).
3. CAS exact fence -> enabled B, with the protected route commit performed as this second CAS's `before_write` callback.

This ordering closes two failure classes simultaneously:
- If another continuous command changes state between steps 1 and 3, step 3 fails its expected-fence comparison before the route callback runs, so route B is not committed.
- If route B commits but final `continuous.json` replacement fails, the existing post-callback failure path leaves the durable fence disabled. The system may have route B + fence B, but it cannot have old objective A enabled under route B.

A replace that actually lands B but fails only subsequent durability reporting can still raise, but semantic route/objective coherence is preserved because B and route B agree.

A successful handoff now advances generation twice (`g -> g+1 fence -> g+2 enabled`), so completed events and manager-handoff identity must record the final generation rather than assuming `g+1`.

## 3. Fence recovery should be a semantic boot path, never a process-resume reason

The fence reason must not begin with `operator ` and must never enter `RESUMABLE_STOP_REASONS`. Drain and graceful SIGTERM/SIGINT are process-lifecycle stops and may be re-armed cheaply; a handoff fence means a semantic route/objective transaction was incomplete and requires Manager reconciliation.

A boot-time fence handler can recognize exactly:
- `resume_continuous=true`,
- continuous disabled,
- exact fence reason,
- nonempty preserved Manager-clean objective.

It should then set boot intent for a fresh Manager division without first enabling continuous state. Existing `_rf_manager_divide_on_boot` can classify/commit and only enable after a successful handoff CAS. This preserves fail-closed behavior after a crash between the two CAS operations.

## 4. Process helpers currently mutate semantic state too early

`start_project_daemon(..., resume_continuous=True)` currently pre-enables a disabled campaign when `done_reason` merely starts with `operator `, and does so before daemon admission/spawn. Besides previously observed semantic-stop resurrection, this means a process-start helper is acting as a semantic mutation authority.

For the new fence, the current helper would have the opposite problem: a correctly non-`operator` fence would remain disabled, and the helper would not even pass `config.resume_continuous=True`, so daemon boot would never get a chance to reconcile it.

The cleaner boundary is:
- process helper passes **resume intent only**;
- it never rewrites continuous semantic state before admission/spawn;
- daemon boot reads the current durable state and applies one exact gate:
  - drain/SIGTERM -> process rearm;
  - handoff fence -> Manager semantic reconciliation;
  - operator stop/hold/completion -> remain disabled.

This also removes the existing possibility that an admission-refused or failed daemon start changes campaign semantics before any executor actually starts.

## 5. Scheduled upgrade should consume current state, not restore its old snapshot

A scheduled daemon-upgrade request currently stores `resume_continuous` plus an objective snapshot. At completion, if the saved boolean was true, it writes that saved objective back as enabled before restart. Therefore an upgrade request created before a later semantic stop, route handoff, or fence can overwrite newer durable state.

The same fix generalizes: upgrade completion should pass only process resume intent and let daemon boot inspect the **current** continuous record. A current handoff fence is reconciled; a current stop/hold remains stopped; a drain/SIGTERM state is process-rearmed. The upgrade request no longer has authority to resurrect a stale objective snapshot.

## 6. Operator decision acceptance and execution rearm must remain separate

The pending-question bridge currently re-enables any disabled continuous state with a nonempty objective after a continue decision. Existing behavior intentionally permits a human decision itself to remain valid even when continuous generation changed while the card was pending.

That is compatible with the new design only if two facts are separated:
- the human decision is accepted and durably recorded;
- execution rearm is allowed only after current route/fence reconciliation.

A continue decision observed while the handoff fence is current must not simply flip `enabled=true`; it should enter the same semantic reconcile-or-rearm gate.

## 7. Manager-handoff identity v4 can be narrow and backward-compatible

All functional identity matching is concentrated in `daemon/_life_worker_identity.py`. Version 3 binds objective hash, vertical, domain, continuous generation and intent id, and accepts `identity_generation <= current_generation`.

The minimum v4 route fingerprint should cover Manager-owned route fields whose changes alter execution semantics but which may change without changing vertical/domain:
- `vertical`
- `domain`
- `workflow_mode`
- `research_target_level`
- `research_direction_mode`
- `target_venue`

Do **not** include `current_stage`, stage history, stage status, or evidence: legitimate progress would invalidate fast restart continuously. `research_target_set_at` is also unnecessary for the minimum identity because a real target-level change changes the normalized target itself.

A stronger later extension may include a canonical stage-order/schema digest for adapted data domains, but that is separate from the minimum route fingerprint.

Backward-compatible fail-closed migration:
- readers may still parse v1-v3 for audit/migration;
- v1-v3 do not authorize v4 fingerprint-aware fast resume;
- one fresh Manager redivision upgrades the sidecar to v4;
- v4 may retain generation `<=` matching when objective and route fingerprint match exactly, preserving cheap drain/SIGTERM restarts despite lifecycle-only generation increments.

Old completed events cannot safely synthesize a v4 fingerprint from the **current** route because that would bless exactly the drift being detected. New completed events should persist the route fingerprint directly. Old events without it should force redivision.

## 8. Regression matrix

Minimum regressions for the refined protocol:

1. Old A enabled + route A; first fence CAS succeeds; second CAS commits route B then `continuous.json` replace raises EIO -> route may be B, but continuous is disabled fence B, never A enabled + B.
2. Another continuous writer changes state after fence and before second CAS -> second CAS mismatch; route callback is never invoked.
3. Success path increments generation by two and completed identity/event records final generation.
4. Web/process start passes resume intent without mutating a fence before admission; boot reconciles the fence through Manager.
5. Fence reason is rejected by process-only resumable-stop allowlist.
6. Scheduled upgrade created before a later fence cannot restore its old objective over the fence.
7. Continue decision can be accepted while fence is current but cannot directly enable execution before reconciliation.
8. v4 identity fails fast-match when only `workflow_mode` differs under the same vertical/domain.
9. v1-v3 identity under v4 code triggers one Manager redivision, then v4 fast resume becomes available.
10. Ordinary stage progress with unchanged route fingerprint retains fast resume.
11. Pipeline-yield cleanup remains guaranteed on every failure path.

## Scope

This is source-level reachability and failure-order analysis against public Argus `8c5a0e356c470ad4cbdc904a7fbe4de14af366cf`. No live exploit, state corruption, or private system was exercised. The two-CAS protocol is an adaptation proposal; its benefits are inferred from existing tested storage semantics and must be validated by the integration regressions above.

## Exact continuation

1. Trace all call sites that currently invoke `start_project_daemon(..., resume_continuous=True)` and classify whether they express process restart intent or semantic campaign resume; define a single boot `reconcile-or-rearm` contract that preserves explicit operator stop/hold.
2. Specify the exact `HANDOFF_FENCE_REASON` and fence replay semantics, including whether any source-objective provenance must be retained outside the execution task for UX/audit only.
3. Design v4 canonical route-fingerprint normalization and migration tests, especially same-vertical `staged -> direct`, target-level, direction-mode and venue changes; separately test stage progress does not invalidate it.
4. Add a fault matrix for the two-CAS sequence: first-CAS failure, route callback failure, second-CAS mismatch, replace-before-land failure, replace-after-land/durability failure, and process crash at every boundary.
5. Keep the external/admin `PIPELINE_STATE` writer-fencing branch separate; do not conflate it with the front-door cross-file transaction defect.
