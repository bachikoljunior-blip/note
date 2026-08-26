# Open Source Systems Scan — standing-objective replacement invalidates old CampaignControl authorization identity

Role: `open_source` clean exploration.
Same frozen semantic control tuple for this physical invocation: note main `456111f88cd26b8ad796866aaf64a6c44a176908`, control revision 10, role config revision 5, role config blob `118f440957ba4654e804af902aa09a9224acca43`.
Public source remains freshly verified `lbx154/Argus@16bb128992ea9d0c11b5bbca7a4f1d549dea84dd`.

## Front-door standing replacement is stronger than a bare route reset

The prior continuation asked whether `reset_stage_for_replacement_intent` can leave a live old CampaignControl wait authorizable. The normal continuous front door does not invoke that primitive in isolation.

`manager_continuous_handoff(...)`:

1. reads the exact current continuous config as `expected`;
2. computes `replacement_intent` only when there is a standing objective and the new operator request is genuinely non-additive/non-equivalent (it checks both raw body and Manager-clean execution task);
3. acquires the Manager pipeline lock;
4. calls `compare_and_swap_continuous_config(...)` with the new `prepared.execution_task` and `before_write=_commit`;
5. inside that callback, commits the new vertical/route with `force_stage_reset=replacement_intent`, supersedes pending backlog for a true replacement, and persists the task if configured;
6. only then does the continuous-config atomic writer replace `continuous.json` with the new objective and `generation = current.generation + 1`.

Thus the route reset and objective replacement are one higher-level CAS handoff, not unrelated writes.

## Old CampaignControl identity becomes unusable after a genuine replacement

`CampaignControlStore.campaign_identity(...)` hashes the current continuous objective into `objective_sha256` and combines it with a campaign epoch.

The Web/API authorization handler does not blindly trust the old HEAD. It constructs a current identity from the current continuous state (while preserving the HEAD epoch for comparison) and rejects if either current `campaign_id` or `objective_sha256` differs from the stored HEAD.

For `replacement_intent=True`, the new Manager-clean execution task cannot be equal to, or a monotonic extension of, the old objective under `objective_update_requires_stage_reset(...)`; otherwise replacement would have been false. After the successful continuous CAS, `continuous.json.objective` therefore changes. Any old CampaignControl HEAD/wait from the replaced objective now has a different objective hash/campaign id and authorization issuance rejects it as `active campaign identity changed`.

The continuous CAS also advances its own generation, but the current authorization comparison explicitly supplies the HEAD epoch when rebuilding identity, so the decisive observed fence here is the changed objective hash, not an inferred epoch check.

## Supplemental bounded work does not create the opposite problem

`manager_bounded_handoff(...)` has an explicit special case for a bounded operator task submitted while a continuous campaign is active. `_bounded_handoff_division(...)` returns a non-mutating Division using the already persisted vertical/workflow mode; its contract says supplemental work must not replace the standing campaign's vertical, stage, target level, or workflow mode.

Therefore the common front-door cases split cleanly:

- **standing objective replacement**: protected route/stage may reset, but the continuous objective changes and old CampaignControl identity is rejected;
- **bounded supplemental task inside an active campaign**: CampaignControl identity remains current, but the task does not mutate the standing route/stage.

This further weakens the hypothesis that the normal operator front door can leave an old live wait authorizable after a semantic route replacement.

## Remaining suspect surface

Do not generalize this to every writer. The still-open risk surface is now narrower:

1. external/admin/direct protected pipeline writers that bypass `manager_continuous_handoff`;
2. a new bounded handoff when no continuous campaign is active, if an old CampaignControl wait can survive in the same life-dir and remain identity-compatible;
3. low-level rollback/reset calls reachable outside the normal front-door contracts;
4. non-stage protected fields that an allowed repair action semantically relies on but does not revalidate.

## Candidate refinement

For `clean-os-g1-005`, front-door route replacement itself is not current evidence for migrating stage authority into CampaignControl. Keep:

- CampaignControl `stage_projection` derivative;
- front-door continuous objective CAS/identity fencing as a positive control;
- one authoritative protected `pipeline_revision`/digest for low-level stale-writer and lost-update defense;
- direct binding of any *actually stage-sensitive* future authorization to that protected revision, only if a live-wait path is demonstrated;
- host-ephemeral bearer redesign as a separate concern.

## Exact continuation

Audit the remaining non-front-door paths under a live `active_wait`: bounded handoff when continuous mode is disabled, direct/admin `persist_vertical`, standalone objective/route writers, low-level rollback/reset, and completion. For each, establish whether old CampaignControl identity becomes invalid, the wait is cleared, the protected field is revalidated at authorization/claim, or a real stale-wait window remains. Prefer proving the first concrete surviving sequence over broad architectural migration.