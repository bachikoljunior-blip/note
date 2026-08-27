# Open Source Systems Scan — current-main active-fence writer matrix

Invocation started: 2026-08-27T18:59:03+09:00
Checkpointed: 2026-08-27T19:12:40.329561+09:00

Semantic authority remains frozen at `note@4b19551018936e5b713eea90f7b3b87e3ff2f8c4 / control 12 / open_source config 5 / config blob 118f440957ba4654e804af902aa09a9224acca43`. Public source remains `lbx154/Argus@8a867e7b45f863a9cd4e79e4f6d21ca7a2009e48`. This file extends the 19:10 transition-lineage checkpoint and records only current-main public-source writer behavior.

## Confirmed current production writers

### Web daemon start — `REFUSE` while an active handoff fence exists

`start_project_daemon(... resume_continuous=True)` currently reads a disabled continuous state and, when its objective is nonempty and `done_reason.lower().startswith("operator ")`, directly writes it back as `enabled=True`. This happens before daemon admission-limit checking and before the actual spawn.

That broad prefix includes semantic stop/hold reasons, not only process-drain reasons. Under `HandoffFenceV1`, daemon start must never clear or enable through an active fence. It should carry only process-start intent into the common reconciliation gate. The existing narrow `RESUMABLE_STOP_REASONS` in daemon state remains the positive control for process-only rearm when no semantic fence is active.

Classification: **REFUSE** direct enable; invoke `reconcile_or_rearm` instead.

### Immediate and scheduled daemon upgrade — `REFUSE` while fenced

Current immediate upgrade snapshots `continuous = read_continuous_state(...)` before drain. If the old snapshot was enabled, it later calls `write_continuous_config(enabled=True, objective=continuous.objective)` and then starts the daemon.

Scheduled upgrade persists `resume_continuous` and `objective` inside the upgrade request and, after drain and later reconciliation, directly re-enables that saved objective before restart. These paths can restore stale semantic state after a newer stop/objective change.

An active handoff fence must therefore reject shortcut replay from either saved snapshot. Upgrade should restart process code only; semantic campaign state is decided from the current exact continuous state at restart time.

Classification: **REFUSE** direct enable; process restart may proceed only through current-state reconciliation.

### Resolved operator decision: stop — `CANCEL`

`_reconcile_campaign_after_decision(... stopped=True)` currently disables the active continuous objective with `done_reason="operator chose to stop the campaign"`.

This is a new explicit semantic operator decision and must outrank an older in-flight handoff. If a fence exists, the correct behavior is to atomically cancel/clear that fence and remain disabled. It must not preserve a target that a later process restart can resurrect.

Classification: **CANCEL**.

### Resolved operator decision: continue — `REFUSE/reconcile` while fenced

For non-stop decisions, `_reconcile_campaign_after_decision` currently sees `before.objective` and, if it is disabled, directly calls `write_continuous_config(enabled=True, objective=before.objective)`.

The human decision itself should remain accepted/idempotent, but if an active fence exists the decision does not prove that the current protected route still matches the lineage that produced the question. Execution rearm must therefore be separated from decision acceptance.

Classification: **REFUSE** blind enable; retain accepted decision, then reconcile current route/fence.

### `/config continuous=off` — `CANCEL`

The shared life action explicitly calls `disable_continuous_config` when the operator turns continuous mode off. This is a direct semantic operator instruction rather than a machine/process pause.

Classification: **CANCEL** active fence and stay disabled.

## Matrix rule now source-shaped

```text
new explicit semantic stop/off                 -> CANCEL
process start / daemon upgrade / stale resume  -> REFUSE direct semantic enable
old human decision "continue"                 -> accept decision, REFUSE blind enable, reconcile
strict Manager receipt + exact side effects    -> FINALIZE
machine safety disable/completion              -> PRESERVE unless separately proven semantic cancellation
```

The last `PRESERVE` category still needs a fresh complete caller audit at this exact public commit. The current run intentionally does not inherit old classifications for un-reopened callers.

## Candidate update

`clean-os-g1-005` now has current-main evidence for the most dangerous rearm writers: **daemon start, immediate/scheduled upgrade, and operator-decision continue all bypass the proposed semantic fence today and should be routed through one exact-current-state `reconcile_or_rearm` boundary; explicit operator stop/off is different authority and should atomically cancel the fence.**

## Exact continuation

1. Finish the current-main caller audit for machine safety/completion disables and classify them `PRESERVE` versus semantic `CANCEL` using exact source.
2. Turn generic envelope `event_id` into literal Python + TypeScript Mission View replay tests.
3. Turn front-door and daemon-boot `transition_id` threading into literal reset-history receipt tests.
4. Keep global/external protected `PIPELINE_STATE` writer fencing separate.
